"""PathSnap evaluator UI (Laptop 2).

Lists the evaluation trips served by the API on Laptop 1, sends the selected trip id to
POST /predict, and shows the predicted route on a Folium map with the server-side scores.

Run
  PATHSNAP_API=http://<laptop-1-ip>:8000 streamlit run ui/app.py --server.address 0.0.0.0

The UI never reads trip files or ground truth: everything it shows comes from the API.
"""
from __future__ import annotations

import os

import folium
import pandas as pd
import requests
import streamlit as st
from streamlit_folium import st_folium

DEFAULT_API = os.environ.get("PATHSNAP_API", "http://localhost:8000")
TIMEOUT_S = 120
GPS_COLOR, ROUTE_COLOR = "#2563eb", "#dc2626"

st.set_page_config(page_title="PathSnap", page_icon="🗺️", layout="wide")


def api_get(base: str, path: str) -> dict:
    r = requests.get(f"{base.rstrip('/')}{path}", timeout=10)
    r.raise_for_status()
    return r.json()


def api_predict(base: str, trip_id: str) -> dict:
    r = requests.post(f"{base.rstrip('/')}/predict", json={"trip_id": trip_id}, timeout=TIMEOUT_S)
    r.raise_for_status()
    return r.json()


def build_map(res: dict) -> folium.Map:
    gps, segs = res["gps"], res["route_segments"]
    pts = gps + [p for s in segs for p in s]
    m = folium.Map(tiles="OpenStreetMap", control_scale=True)
    m.fit_bounds([[min(p[0] for p in pts), min(p[1] for p in pts)],
                  [max(p[0] for p in pts), max(p[1] for p in pts)]], padding=(20, 20))

    g_gps = folium.FeatureGroup(name=f"GPS observations ({res['n_points']} pts)", show=True)
    for lat, lon in gps:
        folium.CircleMarker([lat, lon], radius=2, color=GPS_COLOR, fill=True, fill_opacity=0.7,
                            weight=0).add_to(g_gps)
    g_route = folium.FeatureGroup(name=f"Predicted route ({res['route_arcs']} arcs)", show=True)
    for seg in segs:
        folium.PolyLine(seg, color=ROUTE_COLOR, weight=5, opacity=0.8).add_to(g_route)
    if gps:
        folium.Marker(gps[0], tooltip="Start", icon=folium.Icon(color="green", icon="play")).add_to(g_route)
        folium.Marker(gps[-1], tooltip="End", icon=folium.Icon(color="black", icon="stop")).add_to(g_route)
    g_gps.add_to(m)
    g_route.add_to(m)
    folium.LayerControl(collapsed=False).add_to(m)
    legend = (f'<div style="position:fixed;top:84px;left:12px;z-index:9999;background:white;padding:8px 10px;'
              f'border:1px solid #999;border-radius:6px;font:13px sans-serif">'
              f'<span style="color:{GPS_COLOR}">●</span> GPS observation<br>'
              f'<span style="color:{ROUTE_COLOR}">━</span> Predicted route</div>')
    m.get_root().html.add_child(folium.Element(legend))
    return m


def pct(x) -> str:
    return "—" if x is None else f"{100 * x:.2f}%"


# ---------------- sidebar: connection ----------------
st.sidebar.title("PathSnap")
api = st.sidebar.text_input("API URL (Laptop 1)", DEFAULT_API)
try:
    health = api_get(api, "/health")
    trips = api_get(api, "/trips")["trips"]
    st.sidebar.success(f"Connected · {health['classifier']} + HMM · {health['n_trips']} trips")
    with st.sidebar.expander("Decoder settings"):
        st.json(health["decoder"])
except Exception as e:  # noqa: BLE001
    st.sidebar.error(f"Cannot reach API: {e}")
    st.title("PathSnap — map matching")
    st.info("Start the API on Laptop 1 and set its URL in the sidebar.")
    st.stop()

# ---------------- main ----------------
st.title("PathSnap — map matching & route reconstruction")
st.caption("Pick an evaluation trip. The API on Laptop 1 runs candidates → XGBoost → HMM/Viterbi and "
           "scores the result against its own reference data; the reference route never leaves the server.")

if not trips:
    st.warning("The API has no evaluation trips in its eval folder.")
    st.stop()

tab_one, tab_all = st.tabs(["Single trip", "All trips"])

with tab_one:
    c1, c2 = st.columns([3, 1])
    trip_id = c1.selectbox("Evaluation trip", trips, index=0)
    run = c2.button("Match trip", type="primary", use_container_width=True)
    if run:
        with st.spinner(f"Running pipeline on trip {trip_id}…"):
            try:
                st.session_state["result"] = api_predict(api, trip_id)
            except Exception as e:  # noqa: BLE001
                st.error(f"Prediction failed: {e}")

    res = st.session_state.get("result")
    if res:
        m = res["metrics"]
        st.subheader(f"Trip {res['trip_id']}")
        k = st.columns(6)
        k[0].metric("Top-1 accuracy", pct(m.get("top1_accuracy")))
        k[1].metric("Route F1", pct(m.get("route_f1")))
        k[2].metric("Route precision", pct(m.get("route_precision")))
        k[3].metric("Route recall", pct(m.get("route_recall")))
        k[4].metric("Route continuity", pct(m.get("route_continuity")))
        k[5].metric("Total time", f"{res['timings_ms']['total']:.0f} ms")
        st.caption(f"{res['points_matched']}/{res['n_points']} GPS points matched · "
                   f"{res['route_arcs']} route arcs · {res['route_gaps']} unbridged gaps · "
                   f"features {res['timings_ms']['features']:.0f} ms, classifier "
                   f"{res['timings_ms']['classifier']:.0f} ms, HMM {res['timings_ms']['hmm']:.0f} ms")
        if not m.get("available", True):
            st.info("The server has no reference route for this trip, so only the prediction is shown.")
        st_folium(build_map(res), height=600, use_container_width=True, returned_objects=[],
                  key=f"map_{res['trip_id']}")

with tab_all:
    st.write("Runs every trip through the API one by one (each call appears in the API log).")
    if st.button("Evaluate all trips"):
        rows, bar = [], st.progress(0.0)
        for i, t in enumerate(trips):
            try:
                r = api_predict(api, t)
                rows.append({"trip_id": t, "n_points": r["n_points"], **{k: r["metrics"].get(k) for k in
                             ["top1_accuracy", "route_precision", "route_recall", "route_f1", "route_continuity"]},
                             "route_gaps": r["route_gaps"], "ms": r["timings_ms"]["total"]})
            except Exception as e:  # noqa: BLE001
                rows.append({"trip_id": t, "error": str(e)})
            bar.progress((i + 1) / len(trips))
        df = pd.DataFrame(rows)
        st.session_state["all"] = df
    df = st.session_state.get("all")
    if df is not None:
        if "top1_accuracy" in df:
            ok = df.dropna(subset=["top1_accuracy"])
            pooled = (ok.top1_accuracy * ok.n_points).sum() / ok.n_points.sum()
            a, b, c = st.columns(3)
            a.metric("Pooled Top-1", pct(pooled))
            b.metric("Mean route F1", pct(ok.route_f1.mean()))
            c.metric("Trips succeeded", f"{len(ok)}/{len(df)}")
        st.dataframe(df, use_container_width=True, hide_index=True)
