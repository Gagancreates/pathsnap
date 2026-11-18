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
| 2 | Labels + candidates | ⬜ | | |
| 3 | Feature engineering | ⬜ | | |
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

_(filled as experiments land; source of truth is `experiments/results/`)_

## Log

- **2026-11-18** — Repo scaffolded, plan written, environment set up.
- **2026-11-18** — Phase 1 done: loaders (`io.py`), per-trip projection (`geo.py`), network stats (`network.py`), Folium builder (`viz.py`), EDA script + outputs. Next: Phase 2 labels + candidates.
