# PathSnap — Project Plan

Map-match noisy GPS tracks to a road network: generate candidate road segments per GPS point, score them with a trained classifier, then decode a connected route with HMM + Viterbi. Serve it via FastAPI (Laptop 1) and an evaluator UI (Laptop 2).

## Data facts that shape the design

- Each trip has its **own local road network** (`.nodes`, `.arcs`); node/arc IDs are only meaningful within a trip.
- Trips are spread **worldwide** (Germany, Russia, Kazakhstan, Italy, …) → project each trip into a **local metric projection** (azimuthal equidistant centred on the trip) instead of using degrees.
- Arcs are **directed** (one-way streets have no reverse arc) → heading vs arc bearing is informative; transitions must follow arc direction.
- `.route` is an ordered list of arc IDs, **not one label per GPS point** → per-point labels must be derived (see Phase 2).
- Tracks are ~1 Hz but some trips have gaps up to minutes → decoder must handle gaps.

## Pipeline

```
.track ─► project ─► candidate arcs per point (radius / top-K) ─► features ─► classifier P(true arc)
                                                                                   │
.nodes/.arcs ─► directed graph + spatial index ────────────────────────────────────┤
                                                                                   ▼
                                                          HMM (states = candidates) + Viterbi
                                                                                   ▼
                                                              arc per GPS point + connected route
```

## Phases

| # | Phase | Output | Done when |
|---|-------|--------|-----------|
| 0 | **Setup** | repo, env, structure, plan, tracker | repo pushed, teammates invited |
| 1 | **Data loading + EDA** | `src/pathsnap/io.py`, `geo.py`, `scripts/01_eda.py`, inventory CSV, plots, Folium maps, data-quality notes | report §2 figures exist |
| 2 | **Labels + candidates** | per-point reference arc via monotone alignment of track to route; candidate generator; candidate miss-rate vs radius/K | miss rate measured on train + student_test, radius/K chosen |
| 3 | **Feature engineering** | candidate-level feature table (distance, heading diff, rank, arc length, projection fraction, speed, gap, node degree, neighbour-point distances, …) as parquet | features cached for all 90 trips |
| 4 | **Model experiments (≥5)** | LogReg, KNN, RandomForest/ExtraTrees, HistGB/LightGBM, XGBoost, MLP (+ optional SVM/NB) with GroupKFold-by-trip CV | comparison table + plots: CV macro-F1, Top-1, log loss, route continuity, timings |
| 5 | **Bayesian HPO** | Optuna (TPE) on chosen model, GroupKFold objective, trial log CSV | tuned vs untuned table on CV + student_test |
| 6 | **HMM + Viterbi** | emissions from classifier probs, transitions from directed shortest-path distance vs GPS distance, gap/break handling | classifier-only vs +HMM comparison, continuity analysis |
| 7 | **Artifacts** | saved model, scaler/feature config, HMM params in `artifacts/` | inference script reproduces student_test numbers |
| 8 | **FastAPI backend (Laptop 1)** | `/health`, `/trips`, `/predict/{trip_id}`; ground truth used only server-side for scoring; request logging to console | works for every trip in the eval folder |
| 9 | **UI (Laptop 2)** | Streamlit + Folium: list 10 eval trips, call API, show GPS / predicted route / reference route layers + metrics | end-to-end over LAN |
| 10 | **Integration test** | two-laptop dry run on student_test trips standing in for eval trips | all 10 trips succeed |
| 11 | **Report** | PDF following `Deliverables.pdf` structure, all numbers from `experiments/results/` | every figure traceable to a script |

## Evaluation protocol

- **Train (80 trips):** fitting + GroupKFold (k=5, grouped by trip) CV + Optuna.
- **Student test (10 trips):** model comparison, decoder tuning.
- **Evaluator test (10 trips, given later):** never used during development; lives only in `data/eval_test/` on Laptop 1.
- **Primary selection metric:** observation-level Top-1 accuracy after the classifier (it is what the HMM consumes), with macro-F1 and log loss as tie-breakers; route-level metrics reported after HMM.

## Metrics

Accuracy, precision, recall, F1 (macro), confusion matrix, log loss, observation Top-1, candidate miss rate, route continuity (share of consecutive predicted arcs that are equal or graph-connected), sequence-level route precision/recall, training + inference time.

## Integrity rules (from the brief)

- No eval ground truth in the prediction path or UI; no hardcoded outputs.
- Every reported number/figure produced by committed code; logs and seeds kept in `experiments/`.
- AI assistance disclosed in the report; every member must be able to explain each part.
