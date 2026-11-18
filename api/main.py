"""PathSnap FastAPI backend (Laptop 1).

Endpoints
  GET  /health                 model + data status
  GET  /trips                  trip ids available for evaluation (ids only)
  POST /predict  {"trip_id"}   run the full pipeline on that trip and score it server-side

Run
  PATHSNAP_EVAL_DIR=data/eval_test uvicorn api.main:app --host 0.0.0.0 --port 8000

Ground truth (.route) is read only inside `evaluate_prediction`, after prediction, and
only the resulting metrics are returned. The reference route itself is never sent.
"""
from __future__ import annotations

import logging
import os
import sys
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
from pathsnap.pipeline import PathSnapModel, evaluate_prediction, predict_trip_dir  # noqa: E402

EVAL_DIR = Path(os.environ.get("PATHSNAP_EVAL_DIR", REPO / "data" / "eval_test")).resolve()
MAX_GPS_POINTS = 2500

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s  %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("pathsnap")

app = FastAPI(title="PathSnap API", version="1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
MODEL = PathSnapModel()
log.info("model loaded: %s | eval dir: %s", MODEL.config["classifier"]["type"], EVAL_DIR)


class PredictRequest(BaseModel):
    trip_id: str


def available_trips() -> list[str]:
    if not EVAL_DIR.is_dir():
        return []
    return sorted(p.name for p in EVAL_DIR.iterdir() if p.is_dir() and (p / f"{p.name}.track").exists())


@app.middleware("http")
async def log_requests(request: Request, call_next):
    t0 = time.perf_counter()
    response = await call_next(request)
    client = request.client.host if request.client else "?"
    log.info("%s %s from %s -> %d (%.0f ms)", request.method, request.url.path, client, response.status_code,
             (time.perf_counter() - t0) * 1000)
    return response


@app.get("/health")
def health():
    return {"status": "ok", "eval_dir": EVAL_DIR.name, "n_trips": len(available_trips()),
            "classifier": MODEL.config["classifier"]["type"], "decoder": MODEL.config["decoder"]}


@app.get("/trips")
def trips():
    return {"trips": available_trips()}


@app.post("/predict")
def predict(req: PredictRequest):
    if req.trip_id not in available_trips():
        raise HTTPException(404, f"unknown trip_id {req.trip_id!r}")
    log.info("predict trip %s: running pipeline", req.trip_id)
    pred, trip, net = predict_trip_dir(MODEL, req.trip_id, EVAL_DIR)
    metrics = evaluate_prediction(pred, req.trip_id, EVAL_DIR, net)  # server-side only
    log.info("predict trip %s: %d points, %d route arcs, top1=%.4f, route_f1=%.4f, %.0f ms",
             req.trip_id, pred.n_points, len(pred.route), metrics.get("top1_accuracy", float("nan")),
             metrics.get("route_f1", float("nan")), pred.timings_ms["total"])

    lon, lat = trip.nodes.lon.to_numpy(), trip.nodes.lat.to_numpy()
    segments, cur = [], []
    for a in pred.route:  # predicted route as polylines of [lat, lon]; split where not contiguous
        s, e = int(net.u[a]), int(net.v[a])
        if cur and cur[-1] != [lat[s], lon[s]]:
            segments.append(cur)
            cur = []
        if not cur:
            cur.append([lat[s], lon[s]])
        cur.append([lat[e], lon[e]])
    if cur:
        segments.append(cur)
    step = max(1, len(trip.track) // MAX_GPS_POINTS)
    gps = trip.track.iloc[::step][["lat", "lon"]].round(7).to_numpy().tolist()

    return {
        "trip_id": req.trip_id,
        "n_points": pred.n_points,
        "points_matched": int((pred.point_arc >= 0).sum()),
        "route_arcs": len(pred.route),
        "route_gaps": pred.route_gaps,
        "gps": gps,
        "route_segments": [[[round(x, 7) for x in pt] for pt in seg] for seg in segments],
        "metrics": metrics,
        "timings_ms": {k: round(v, 1) for k, v in pred.timings_ms.items()},
    }
