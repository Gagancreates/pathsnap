"""Phase 10 — integration test: call the running API over HTTP for every trip it serves.

Usage (API already running on Laptop 1):
  python scripts/08_integration_test.py --api http://<laptop-1-ip>:8000

Writes experiments/results/phase10/integration.csv and fails if any trip errors.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import pandas as pd
import requests

OUT = Path(__file__).resolve().parents[1] / "experiments" / "results" / "phase10"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--api", default="http://localhost:8000")
    args = ap.parse_args()
    base = args.api.rstrip("/")
    health = requests.get(f"{base}/health", timeout=10).json()
    trips = requests.get(f"{base}/trips", timeout=10).json()["trips"]
    print(f"API ok: {health['classifier']} + HMM, eval dir {health['eval_dir']}, {len(trips)} trips")

    rows = []
    for tid in trips:
        t0 = time.perf_counter()
        r = requests.post(f"{base}/predict", json={"trip_id": tid}, timeout=120)
        rtt = (time.perf_counter() - t0) * 1000
        if r.status_code != 200:
            rows.append({"trip_id": tid, "status": r.status_code})
            print(f"{tid}: HTTP {r.status_code}")
            continue
        d = r.json()
        assert "route" not in d and "reference" not in str(d.keys()), "ground truth must not be returned"
        rows.append({"trip_id": tid, "status": 200, "n_points": d["n_points"], "points_matched": d["points_matched"],
                     **{k: v for k, v in d["metrics"].items() if k != "available"}, "route_arcs": d["route_arcs"],
                     "route_gaps": d["route_gaps"], "server_ms": d["timings_ms"]["total"], "round_trip_ms": round(rtt, 1)})
        print(f"{tid}: top1 {d['metrics']['top1_accuracy']:.4f}  route F1 {d['metrics']['route_f1']:.4f}  "
              f"{rtt:.0f} ms round trip")
    unknown = requests.post(f"{base}/predict", json={"trip_id": "does-not-exist"}, timeout=10).status_code
    print(f"unknown trip -> HTTP {unknown}")

    df = pd.DataFrame(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT / "integration.csv", index=False)
    ok = df[df.status == 200]
    pooled = (ok.top1_accuracy * ok.n_points).sum() / ok.n_points.sum()
    print(f"{len(ok)}/{len(df)} trips succeeded; pooled Top-1 {pooled:.4f}; mean route F1 {ok.route_f1.mean():.4f}")
    sys.exit(0 if len(ok) == len(df) and unknown == 404 else 1)


if __name__ == "__main__":
    main()
