
# PathSnap 🗺️
### GPS Map Matching and Route Reconstruction Using Machine Learning

PathSnap is a machine-learning-based GPS map-matching system that reconstructs accurate road routes from noisy GPS trajectories.

The system combines **XGBoost classification**, **Hidden Markov Models (HMM)**, and **Viterbi decoding** to identify the most likely road segments traveled by a vehicle.

It features a **FastAPI backend** for prediction and evaluation, alongside an interactive **Streamlit frontend** for route visualization and performance analysis.

---

## 📌 Project Overview

GPS observations are not always perfectly aligned with roads due to signal interference, measurement errors, urban infrastructure, and complex road networks.

Traditional nearest-road matching methods may produce incorrect results, especially around intersections, parallel roads, and overlapping road segments.

PathSnap addresses these challenges through a combination of machine learning and probabilistic sequence modeling.

The system processes GPS trajectories, generates nearby road candidates, extracts relevant features, predicts the most likely road segments, and reconstructs a connected route.

### Objectives

- Match noisy GPS observations to road-network segments.
- Improve map-matching accuracy using machine learning.
- Maintain route continuity through HMM/Viterbi decoding.
- Visualize reconstructed routes on interactive maps.
- Evaluate predictions using quantitative performance metrics.
- Support distributed execution through a client-server architecture.

---

## ✨ Key Features

- **GPS Map Matching:** Matches noisy GPS observations to nearby road segments.
- **Candidate Generation:** Uses spatial indexing to identify relevant road candidates.
- **Feature Engineering:** Extracts 26 features covering distance, heading, road topology, motion, and neighboring observations.
- **Machine Learning:** Uses XGBoost to score candidate road segments.
- **Route Reconstruction:** Applies HMM and Viterbi decoding to reconstruct connected routes.
- **Interactive Visualization:** Displays GPS observations and predicted routes using Folium and Streamlit.
- **REST API:** Provides prediction and evaluation services through FastAPI.
- **Performance Evaluation:** Reports Top-1 accuracy, precision, recall, route F1, continuity, and execution timings.
- **Distributed Architecture:** Supports running the backend and frontend on separate laptops.
- **Automated Pipeline:** Includes scripts for data processing, model training, evaluation, and report generation.

---

## ⚙️ How PathSnap Works

The map-matching pipeline consists of six major stages.

```text
             GPS Trajectory Data
                     |
                     v
            Data Preprocessing
                     |
                     v
             Road Candidate
                Generation
                     |
                     v
             Feature Engineering
               (26 Features)
                     |
                     v
             XGBoost Classifier
              (Candidate Scores)
                     |
                     v
             HMM + Viterbi
                 Decoding
                     |
                     v
             Route Reconstruction
                     |
                     v
             FastAPI Backend
                     |
                     v
             Streamlit Frontend
                     |
                     v
             Interactive Map
             + Evaluation Metrics
```

### 1. Data Preprocessing

GPS trajectory data and road-network information are loaded and processed.

The system uses a per-trip local metric projection to perform accurate distance calculations.

### 2. Candidate Generation

For each GPS observation, nearby road segments are identified using a spatial index.

The selected configuration uses:

- Candidate search radius: 50 metres
- Maximum candidates per observation: 12

### 3. Feature Engineering

Each candidate road segment is represented using 26 inference-safe features.

Feature categories include:

- Distance and candidate ranking
- Heading agreement
- Road topology
- Vehicle motion
- Neighboring-point consistency

### 4. Machine Learning Classification

Multiple machine-learning models were evaluated, including:

- Logistic Regression
- Gaussian Naive Bayes
- K-Nearest Neighbors
- Decision Tree
- Random Forest
- LightGBM
- XGBoost
- Multi-Layer Perceptron

XGBoost was selected for the final pipeline based on classification performance, probability quality, and inference efficiency.

### 5. HMM and Viterbi Decoding

The Hidden Markov Model incorporates candidate probabilities and road-network connectivity.

Viterbi decoding identifies the most likely sequence of road segments while reducing discontinuities and incorrect road transitions.

### 6. Route Visualization

The reconstructed route is returned through the FastAPI backend and displayed in the Streamlit interface.

The frontend visualizes:

- GPS observations
- Predicted road routes
- Start and end locations
- Evaluation metrics
- Processing times

---

## 🛠️ Technology Stack

| Component | Technologies |
|-----------|-------------|
| Programming Language | Python |
| Machine Learning | XGBoost, scikit-learn, LightGBM |
| Hyperparameter Optimization | Optuna |
| Data Processing | NumPy, Pandas |
| Backend | FastAPI, Uvicorn |
| Frontend | Streamlit |
| Mapping and Visualization | Folium, Streamlit-Folium |
| HTTP Communication | Requests |
| Data Storage | CSV, JSON, Parquet |
| Version Control | Git, GitHub |

---

## 📊 Model Performance

The final system uses an untuned XGBoost classifier combined with HMM/Viterbi decoding.

### Final Pipeline Results

The following results were recorded on the project's 10-trip `student_test` dataset.

| Metric | Result |
|--------|--------|
| Top-1 Accuracy | 95.52% |
| Route F1 Score | 99.05% |
| Route Continuity | 98.40% |
| Unbridged Route Gaps | 6 |

### Classifier vs HMM Comparison

| Metric | XGBoost Only | XGBoost + HMM |
|--------|-------------|---------------|
| Top-1 Accuracy | 89.70% | 95.52% |
| Route F1 | 88.93% | 99.05% |
| Route Continuity | 94.14% | 98.40% |

The addition of HMM/Viterbi decoding improved route reconstruction by considering road-network connectivity and sequential consistency.

**Note:** These are results from the project's documented `student_test` evaluation dataset. They do not represent guaranteed performance on arbitrary unseen datasets.

Detailed experiment results are available in:

- `TRACKER.md`
- `experiments/results/`
- `reports/`

---

## 🏗️ System Architecture

PathSnap supports a two-laptop client-server architecture.

```text
          LAPTOP 2 - FRONTEND
        +----------------------+
        |    Streamlit UI      |
        |                      |
        | Trip Selection       |
        | Route Visualization  |
        | Performance Metrics  |
        +----------+-----------+
                   |
                   | HTTP Requests
                   |
                   v
          LAPTOP 1 - BACKEND
        +----------------------+
        |      FastAPI         |
        |                      |
        | Candidate Generation |
        | XGBoost Prediction   |
        | HMM/Viterbi Decoding |
        | Server-side Scoring  |
        +----------+-----------+
                   |
                   v
        +----------------------+
        |    GPS and Road      |
        |    Network Data      |
        +----------------------+
```

### Backend Responsibilities

- Load evaluation trip data.
- Generate candidate road segments.
- Run machine-learning inference.
- Reconstruct predicted routes.
- Calculate evaluation metrics.
- Return predictions through HTTP endpoints.

### Frontend Responsibilities

- Connect to the backend API.
- Display available evaluation trips.
- Request predictions.
- Visualize predicted routes.
- Display accuracy and performance metrics.

**Important:** Ground-truth reference routes remain on the backend. The frontend receives predicted routes and evaluation metrics, but never the reference route itself.

---

## 📁 Repository Structure

```text
PathSnap/
|
|-- api/
|   |-- main.py
|
|-- ui/
|   |-- app.py
|
|-- src/
|   |-- pathsnap/
|       |-- Core map-matching library
|
|-- scripts/
|   |-- 01_eda.py
|   |-- 02_labels_candidates.py
|   |-- 03_features.py
|   |-- 04_model_experiments.py
|   |-- 04b_model_plots.py
|   |-- 05_bayesian_hpo.py
|   |-- 06_hmm_viterbi.py
|   |-- 07_export_artifacts.py
|   |-- 08_integration_test.py
|   |-- 09_build_report.py
|
|-- experiments/
|   |-- Experiment configurations and results
|
|-- artifacts/
|   |-- Exported model and pipeline configuration
|
|-- reports/
|   |-- Figures, maps and final report
|
|-- data/
|   |-- README.md
|   |-- Local dataset files (not committed)
|
|-- README.md
|-- PLAN.md
|-- TRACKER.md
|-- CONTRIBUTING.md
|-- requirements.txt
|-- pyproject.toml
|-- run_all.sh
```

---

## 🚀 Installation and Setup

### Prerequisites

- Python 3.10 or newer
- Git
- pip
- A compatible operating system (Windows, Linux, or macOS)

Python 3.11 is recommended for the documented setup.

### 1. Clone the Repository

```bash
git clone https://github.com/Gagancreates/pathsnap.git
cd pathsnap
```

### 2. Create a Virtual Environment

On Linux/macOS:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

On Windows:

```cmd
python -m venv .venv
.venv\Scripts\activate
```

Alternatively, using `uv`:

```bash
uv venv --python 3.11
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
pip install -e .
```

### 4. Configure the Dataset

Place the dataset inside the `data/` directory as described in:

`data/README.md`

Alternatively, configure a custom data directory:

```bash
export PATHSNAP_DATA=/path/to/data
```

On Windows CMD:

```cmd
set PATHSNAP_DATA=C:\path\to\data
```

---

## 📂 Dataset Format

Each trip contains four header-less, whitespace-separated files.

| File | Description |
|------|-------------|
| `.track` | GPS observations containing longitude, latitude, and timestamp |
| `.nodes` | Road-network node coordinates |
| `.arcs` | Directed road segments connecting nodes |
| `.route` | Ordered reference-route arc IDs |

### Data Fields

**Track Data**

- `lon` — Longitude
- `lat` — Latitude
- `t` — Timestamp in seconds

**Node Data**

- `lon` — Longitude
- `lat` — Latitude
- Row index represents the node ID.

**Arc Data**

- `u` — Source node
- `v` — Destination node
- Row index represents the arc ID.

**Route Data**

- Ordered sequence of arc IDs representing the reference route.

Raw datasets and evaluation data should not be committed to the repository.

---

## ▶️ Running the Pipeline

The project includes an automated execution script.

### Run the Main Pipeline

```bash
bash run_all.sh
```

This runs the main pipeline stages covering data exploration, candidate generation, feature engineering, and model experiments.

### Run Selected Models

```bash
bash run_all.sh --models xgb,lgbm
```

### Run Individual Stages

| Stage | Command |
|-------|---------|
| Data Exploration | `python scripts/01_eda.py` |
| Candidate Generation | `python scripts/02_labels_candidates.py` |
| Feature Engineering | `python scripts/03_features.py` |
| Model Comparison | `python scripts/04_model_experiments.py` |
| Model Plots | `python scripts/04b_model_plots.py` |
| Bayesian Optimization | `python scripts/05_bayesian_hpo.py --trials 40` |
| HMM/Viterbi Decoding | `python scripts/06_hmm_viterbi.py --model xgb_untuned --maps` |
| Export Artifacts | `python scripts/07_export_artifacts.py` |
| Integration Testing | `python scripts/08_integration_test.py --api http://localhost:8000` |
| Report Generation | `python scripts/09_build_report.py` |

### Pipeline Outputs

The pipeline produces:

- Experiment results and evaluation metrics
- Feature tables and cached predictions
- Trained model artifacts
- Performance comparison figures
- Interactive route maps
- Technical reports

Results are stored in the corresponding `experiments/`, `artifacts/`, `cache/`, and `reports/` directories.

---

## 🌐 Running the FastAPI Backend

The backend performs model inference and server-side evaluation.

### Start the API

On Linux/macOS:

```bash
PATHSNAP_EVAL_DIR=data/eval_test uvicorn api.main:app --host 0.0.0.0 --port 8000
```

On Windows CMD:

```cmd
set PATHSNAP_EVAL_DIR=data/eval_test
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### Available API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Returns model and dataset status |
| GET | `/trips` | Lists available evaluation trip IDs |
| POST | `/predict` | Runs map matching for a selected trip |

### Prediction Request

```json
{
  "trip_id": "00000095"
}
```

### Prediction Response

A successful response includes:

- Trip identifier
- Number of GPS observations
- Number of matched observations
- Predicted route segments
- Route arc count
- Route gap count
- Evaluation metrics
- Execution timings

The reference route is never returned to the client.

### Request Logging

The backend logs HTTP requests, response status codes, processing latency, and prediction metrics to the console.

---

## 🖥️ Running the Streamlit Frontend

The frontend provides an interactive interface for evaluating map-matching predictions.

### Start the UI

On Linux/macOS:

```bash
PATHSNAP_API=http://localhost:8000 streamlit run ui/app.py --server.address 0.0.0.0
```

On Windows CMD:

```cmd
set PATHSNAP_API=http://localhost:8000
streamlit run ui/app.py --server.address 0.0.0.0
```

For a two-laptop setup, replace `localhost` with the backend laptop's reachable IP address.

### Frontend Features

**Single Trip Evaluation**

- Select an evaluation trip.
- Run map-matching inference.
- Display the predicted route.
- View Top-1 accuracy, route F1, precision, recall, and continuity.
- Inspect processing times.

**All Trips Evaluation**

- Evaluate every available trip.
- Display per-trip results.
- Calculate pooled Top-1 accuracy.
- Display mean route F1.
- Show successful and failed predictions.

### Map Visualization

The Folium interface displays:

- Blue markers for GPS observations
- Red lines for predicted road routes
- Start and end markers
- Layer controls and map legend

---

## 🧪 Testing and Validation

PathSnap includes an HTTP integration-testing script that communicates with the running FastAPI backend.

### Run Integration Tests

```bash
python scripts/08_integration_test.py --api http://localhost:8000
```

The script:

1. Connects to the API.
2. Retrieves available evaluation trips.
3. Sends prediction requests.
4. Collects performance metrics.
5. Checks that reference routes are not exposed.
6. Checks the response status for an unknown trip.
7. Generates an integration-results CSV.

### Test Output

```text
experiments/results/phase10/integration.csv
```

The documented integration run successfully evaluated all 10 `student_test` trips, achieving a pooled Top-1 accuracy of 95.52%.

The project also completed a real two-laptop integration run using Tailscale.

---

## 💻 Two-Laptop Deployment

PathSnap supports separating model inference and visualization across two devices.

### Laptop 1 — Backend

1. Copy evaluation trip folders into `data/eval_test/`.
2. Start the FastAPI server.
3. Identify the laptop's reachable IP address.
4. Ensure the backend is accessible from Laptop 2.
5. Monitor API request logs.

### Laptop 2 — Frontend

1. Install the frontend dependencies.
2. Set `PATHSNAP_API` to Laptop 1's API address.
3. Launch the Streamlit application.
4. Verify the connection status.
5. Select trips and run predictions.

The documented project demonstration used Tailscale for connectivity between the two laptops.

### Demo Checklist

- [ ] Backend server is running.
- [ ] Evaluation trip folders are available on Laptop 1.
- [ ] Frontend can connect to the backend.
- [ ] The sidebar displays the connected model and trip count.
- [ ] Single-trip prediction works.
- [ ] Predicted routes are displayed correctly.
- [ ] All-trips evaluation completes.
- [ ] API request logs are visible.

---

## 📈 Experiments and Evaluation

The project includes several stages of experimentation.

### Model Comparison

Eight candidate-scoring models from seven model families were evaluated.

Models were compared using:

- Top-1 accuracy
- Macro-F1 score
- Log loss
- Route continuity
- Training time
- Inference time

### Hyperparameter Optimization

Optuna's Tree-structured Parzen Estimator (TPE) was used for Bayesian hyperparameter optimization.

The project evaluated 40 trials for XGBoost.

The final pipeline retained the untuned XGBoost configuration because it performed competitively after HMM decoding while offering better inference efficiency.

### Route Reconstruction Evaluation

HMM/Viterbi decoding was evaluated against classifier-only predictions.

The results demonstrated improved route accuracy and connectivity on the documented evaluation dataset.

For detailed experimental findings, refer to `TRACKER.md` and the generated reports.

---

## 👥 Project Team

| Team Member | GitHub | Contribution Area |
|-------------|--------|-------------------|
| Gagan | [@Gagancreates](https://github.com/Gagancreates) | Project setup and data pipeline |
| Dhruv Purushotham | [@dhruvpurushotham1718-ui](https://github.com/dhruvpurushotham1718-ui) | Dataset documentation |
| Dheepak Seetharam | [@ds610](https://github.com/ds610) | Pipeline automation and modeling |
| Gandhar Gokhale | [@GGO4411](https://github.com/GGO4411) | Documentation, validation, and frontend–API integration |

For the detailed project progress, responsibilities, and decisions, see [TRACKER.md](TRACKER.md).

---

## 📚 Project Documentation

Additional project documentation is available in:

- [Project Plan](PLAN.md) — Project objectives, methodology, and planned implementation.
- [Progress Tracker](TRACKER.md) — Development phases, experimental results, and decisions.
- [Contribution Guidelines](CONTRIBUTING.md) — Team workflow and contribution practices.
- [Dataset Documentation](data/README.md) — Dataset setup and file organization.

---

## 🤝 Contributing

Contributions and improvements should follow the repository's documented team workflow.

1. Create a dedicated branch for your changes.
2. Implement and test your contribution.
3. Update `TRACKER.md` with relevant progress.
4. Commit changes using your own GitHub identity.
5. Push your branch and open a pull request.
6. Request review from a teammate before merging.

For complete instructions, refer to [CONTRIBUTING.md](CONTRIBUTING.md).

---

## 🤖 AI Assistance

Parts of this repository were developed with AI assistance (Claude).

Experiments were executed by the project team, and reported numerical results were generated using the committed project code.

---

## 📄 Project Summary

PathSnap demonstrates how machine learning and probabilistic sequence modeling can be combined to reconstruct road routes from noisy GPS observations.

By integrating XGBoost classification, HMM/Viterbi decoding, FastAPI services, and interactive Streamlit visualization, the project provides an end-to-end system for GPS map matching, route reconstruction, and performance evaluation.
