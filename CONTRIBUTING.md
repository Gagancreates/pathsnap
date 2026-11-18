# Team workflow

- **Branch per task:** `phase<N>-<short-name>` (e.g. `phase4-lightgbm`). Open a PR into `main`; one teammate reviews.
- **Commit your own work from your own account.** Evaluators look at repository history and may ask any member about any part.
- **Update `TRACKER.md`** (status, owner, notes, results) in the same PR as the work.
- **Results:** every experiment writes its config, seed, metrics and timings to `experiments/results/`. Never paste numbers into the report that a script did not produce.
- **Never commit** raw data, evaluator data, secrets, or files > 50 MB.
- **Eval data** (`data/eval_test/`) is used only by the API on Laptop 1 for final scoring — never for training, tuning or feature choices.
