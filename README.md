# PathSnap

Map-matching noisy GPS trajectories to road networks: candidate road segments per GPS point → ML classifier scores → HMM/Viterbi route reconstruction, served by a FastAPI backend (Laptop 1) to an evaluator UI (Laptop 2).

- **Plan:** [PLAN.md](PLAN.md)
- **Progress, findings, decisions:** [TRACKER.md](TRACKER.md)
- **Team workflow:** [CONTRIBUTING.md](CONTRIBUTING.md)

## Setup

```bash
git clone https://github.com/Gagancreates/pathsnap.git
cd pathsnap
python3.11 -m venv .venv && source .venv/bin/activate   # or: uv venv --python 3.11
pip install -r requirements.txt && pip install -e .
```

Place the dataset under `data/` as described in [data/README.md](data/README.md) (symlinks are fine), or set `PATHSNAP_DATA=/path/to/data`.

## Dataset

Each trip contains four header-less, whitespace-separated files:

| File | Contents |
|---|---|
| `.track` | GPS observations containing longitude (`lon`), latitude (`lat`), and timestamp (`t`) in seconds. |
| `.nodes` | Road network node coordinates containing longitude (`lon`) and latitude (`lat`). Row index represents the node ID. |
| `.arcs` | Directed road segments containing source node (`u`) and destination node (`v`). Row index represents the arc ID. |
| `.route` | Ordered sequence of arc IDs representing the reference route taken by the trip. |

## Run

To run the complete pipeline end-to-end:

```bash
bash run_all.sh                             # runs all steps (Phases 1-4)
bash run_all.sh --models xgb,lgbm           # or pass flags to run a model subset
```

Or run individual steps:

| Step | Command | Output |
|------|---------|--------|
| 1. EDA | `python scripts/01_eda.py` | `experiments/results/eda_*`, `reports/figures/eda_*.png`, `reports/maps/eda_trip_*.html` |
| 2. Labels + candidates | `python scripts/02_labels_candidates.py` | `cache/labels/*.npz`, `experiments/results/{labels_trip_summary,candidate_miss_rate}.csv`, `reports/figures/{cand,labels}_*.png` |
| 3. Features | `python scripts/03_features.py` | `cache/features/*.parquet`, `experiments/results/{feature_*,heuristic_baselines}.*`, `reports/figures/feat_*.png` |
| 4. Model comparison | `python scripts/04_model_experiments.py` (`--models xgb,lgbm` for a subset), then `python scripts/04b_model_plots.py` | `experiments/results/phase4/`, `reports/figures/models_*.png`, `cache/{preds,models}/` |
| 5. Bayesian HPO | `python scripts/05_bayesian_hpo.py --trials 40` (resumable) | `experiments/results/phase5/`, `reports/figures/hpo_*.png`, `cache/{preds,models}/xgb_{tuned,untuned}*` |

_(more steps are added as phases land — see TRACKER.md)_

## Repository layout

```
src/pathsnap/      library code (io, geo, network, viz, …)
scripts/           numbered pipeline scripts (01_eda.py, …)
experiments/       configs, logs and result CSV/JSON
artifacts/         exported model + preprocessing + HMM config
api/               FastAPI backend (Laptop 1)
ui/                evaluator UI (Laptop 2)
reports/           figures, Folium maps, final report
data/              local dataset (not committed)
```

## AI assistance

Parts of this repository were written with AI assistance (Claude). All experiments are run by the team and every reported number is produced by committed code.
