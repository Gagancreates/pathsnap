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

## Run

| Step | Command | Output |
|------|---------|--------|
| 1. EDA | `python scripts/01_eda.py` | `experiments/results/eda_*`, `reports/figures/eda_*.png`, `reports/maps/eda_trip_*.html` |

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

Parts of this repository were written with AI assistance (Claude); such commits carry a `Co-Authored-By` trailer. All experiments are run by the team and every reported number is produced by committed code.
