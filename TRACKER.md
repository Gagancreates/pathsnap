# PathSnap — Progress Tracker

Update this file in the same commit as the work. Status: ⬜ todo · 🟡 in progress · ✅ done · ⛔ blocked

## Team

| Member | GitHub | Focus |
|--------|--------|-------|
| Gagan | @Gagancreates | setup, data pipeline |
| TBD | | |
| TBD | | |
| TBD | | |

## Phase status

| # | Phase | Status | Owner | Notes |
|---|-------|--------|-------|-------|
| 0 | Setup | ✅ | Gagan | repo, env, plan, tracker |
| 1 | Data loading + EDA | ✅ | Gagan | `scripts/01_eda.py` → inventory, summary, 5 figures, 5 Folium maps |
| 2 | Labels + candidates | ✅ | Gagan | `scripts/02_labels_candidates.py`; R=50 m, K=12; 2 trips flagged unreliable |
| 3 | Feature engineering | ✅ | Gagan | `scripts/03_features.py`; 26 features, 1.34M train / 147k test rows |
| 4 | Model experiments (≥5) | ⬜ | | |
| 5 | Bayesian HPO | ⬜ | | |
| 6 | HMM + Viterbi | ⬜ | | |
| 7 | Artifacts | ⬜ | | |
| 8 | FastAPI backend | ⬜ | | |
| 9 | UI | ⬜ | | |
| 10 | Integration test | ⬜ | | |
| 11 | Report | ⬜ | | |

## Decisions log

| Date | Decision | Why |
|------|----------|-----|
| 2026-11-18 | Per-trip azimuthal-equidistant projection | trips span several countries; need metres, not degrees |
| 2026-11-18 | Raw data not committed; `data/` holds symlinks/local copies | size, and eval data must stay on Laptop 1 only |
| 2026-11-18 | Per-point labels = monotone DP alignment of track to route positions | `.route` has no per-point labels; monotonicity stops points snapping to a later/earlier pass of the same road; handles loops (00000056) |
| 2026-11-18 | Candidates: arcs within **R = 50 m**, nearest **K = 12** | train-reliable miss 1.57%, student_test 0.21%, ~7 candidates/point; R=75 only saves ~0.5 pp train miss for +20% candidates (`candidate_miss_rate.csv`) |
| 2026-11-18 | Trips with median point→label distance > 50 m are **unreliable** → excluded from training, kept in reporting | rule flags exactly 00000033, 00000054 (next-worst median is 11 m); their labels are 120–140 m off the GPS |
| 2026-11-18 | Folium base map = OpenStreetMap tiles | CartoDB tiles now require an API key |
| 2026-11-18 | Problem framed as **binary candidate classification** (is this candidate the reference arc?), Top-1 = argmax score per point | fixed-size label space doesn't exist (arc ids are per-trip); gives P(arc) per candidate = HMM emission |
| 2026-11-18 | Features exclude lon/lat, timestamps, trip ids | prevent memorising locations; same code runs in API at inference |
| 2026-11-18 | Missing heading (stationary, <2 m move) → `heading_cos=0`, `heading_diff=90`, `heading_valid=0`; edge neighbours clipped | neutral fill works for every model family (LogReg/KNN/MLP can't take NaN) |

## Data-quality findings

Source: `experiments/results/eda_inventory.csv`, `eda_summary.json` (train + student_test only).

| Finding | Evidence | Implication |
|---------|----------|-------------|
| Partitions | train 80 trips / 208,417 pts / 2,978 km; student_test 10 trips / 19,160 pts / 297 km | ~227k labelled observations |
| Clean values | 0 NaNs, 0 invalid coords, 0 non-monotonic timestamps, 0 invalid route arc IDs | no imputation needed |
| Sampling | 96.5% (train) / 98.6% (test) of steps exactly 1 s; some fractional dt | treat dt as a feature, not a constant |
| Gaps | 28/80 train trips have gaps > 30 s; trip 00000090 has a ~42 h gap, 00000078 ~15 h | decoder must break/relax transitions across gaps |
| Teleport jumps | 10 train trips have steps > 70 m/s (00000013: 95 such steps) | outlier-robust emissions / speed feature |
| GPS noise | GPS→reference-route distance median ≈ 5 m, test p95 ≈ 17 m, p99 ≈ 28 m | candidate radius ~30–50 m should cover most points |
| **Offset trips** | 00000054 median GPS→route **139 m** (GPS 84 m from *any* arc, ≈132 m southward shift); 00000033 median **122 m** but only 8 m from some arc (route ≈ parallel road 122 m away) | reference labels unreliable here → candidate generation will miss; flag/exclude from training, discuss in report |
| Networks | 3.5k–165k arcs per trip; median arc 25 m; one-way share 0–65%; 89/90 trips have >1 weakly connected component (largest ≈ 97% of nodes) | spatial index needed; shortest paths must allow "unreachable" |
| Route encoding | routes are ordered arc IDs, ≈ 99.9% contiguous (v of arc i = u of arc i+1); 11 trips have 1–3 breaks; 00000056 repeats 255 arcs (loops) | labels need monotone track↔route alignment that allows revisits |

Figures: `reports/figures/eda_*.png`. Maps: `reports/maps/eda_trip_{00000095,00000002,00000054,00000090,00000000}.html`.

## Results snapshot

Source of truth: `experiments/results/`.

**Phase 2 — candidate miss rate (%), reliable trips** (`candidate_miss_rate.csv`)

| Split | R (m) | K=4 | K=8 | K=12 | K=16 | all | mean cands @K=12 |
|-------|-------|-----|-----|------|------|-----|------------------|
| train | 30 | 4.58 | 2.80 | 2.57 | 2.50 | 2.41 | 5.1 |
| train | **50** | 3.75 | 1.84 | **1.57** | 1.49 | 1.39 | **7.0** |
| train | 75 | 3.33 | 1.39 | 1.10 | 1.01 | 0.87 | 8.4 |
| student_test | 30 | 3.43 | 0.98 | 0.81 | 0.79 | 0.77 | 5.5 |
| student_test | **50** | 2.87 | 0.40 | **0.21** | 0.17 | 0.14 | **7.7** |
| student_test | 75 | 2.85 | 0.37 | 0.18 | 0.14 | 0.11 | 9.0 |

**Phase 3 — feature table** (`feature_table_stats.json`, `feature_univariate.csv`, `heuristic_baselines.csv`)

- Rows: train 1,342,714 (reliable trips: 1,276,667), student_test 146,896; ~7 candidates/point; positive rate ≈ 13–14%.
- Strongest single features (train, |2·AUC−1|): `dist_minus_min` 0.82, `rank` 0.81, `dist_ratio` 0.80, `dist_win5_mean` 0.74, `dist` 0.72, `heading_cos_wide` 0.69, `at_endpoint` 0.66.
- Point-level context features (`speed`, `dt_*`, `min_dist`, `second_gap`) are ~0.5 alone — they only help through interactions.
- Rule-based Top-1 (no learning, all GPS points): nearest arc **49.5% train / 53.7% test** (two-way twins tie); nearest + heading **72.1% / 82.6%**. ML models must beat these.

K=2/4 miss a lot because every two-way street contributes two arcs (one per direction) at identical distance — direction must be decided by features (heading), not distance.

## Log

- **2026-11-18** — Repo scaffolded, plan written, environment set up.
- **2026-11-18** — Phase 1 done: loaders (`io.py`), per-trip projection (`geo.py`), network stats (`network.py`), Folium builder (`viz.py`), EDA script + outputs. Next: Phase 2 labels + candidates.
- **2026-11-18** — Phase 2 done: `labels.py` (monotone DP alignment, ~0.3 s/trip), `candidates.py` (KD-tree over ≤20 m arc pieces, verified identical to brute force), miss-rate grid + figures, label-assignment map (`reports/maps/labels_trip_00000095.html`). Next: Phase 3 features.
- **2026-11-18** — Phase 3 done: `features.py` (26 inference-safe features), feature tables cached as parquet (~15 s for all 90 trips), univariate AUC / class-distribution / correlation figures, rule-based baselines. Next: Phase 4 model experiments.
