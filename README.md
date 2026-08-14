# Smart Air Pollution Monitoring Portal
# APYJSR!



> **College Assessment Project** — Concepts: IoT and Dashboards  
> Individual Vibe Coding Assessment  
> Current Phase: **DONE**

---

## Project Purpose

A web-based air pollution monitoring dashboard for major Indian cities that:

- Displays **real-time** air quality readings from official CPCB monitoring stations via the OpenAQ API.
- Demonstrates **IoT concepts** through a clearly-labelled simulated sensor that generates synthetic readings.
- Provides AQI summaries, pollutant breakdowns, and city comparisons.
- Is designed to later support ML-based short-term forecasting.

All data is clearly labelled as **REAL**, **SIMULATED**, or **FALLBACK** at every point in the system. Fake pollution measurements are never inserted.

---

## Supported Cities (Planned)

| City | State | CPCB Stations via OpenAQ |
|---|---|---|
| Delhi | Delhi | Multiple (confirmed) |
| Mumbai | Maharashtra | Multiple (confirmed) |
| Chennai | Tamil Nadu | Multiple (confirmed) |
| Bengaluru | Karnataka | Multiple (confirmed) |
| Kolkata | West Bengal | Multiple (confirmed) |
| Hyderabad | Telangana | Multiple (confirmed) |
| Pune | Maharashtra | Multiple (confirmed) |
| Ahmedabad | Gujarat | Multiple (confirmed) |
| Lucknow | Uttar Pradesh | Multiple (confirmed) |
| **Prayagraj** | Uttar Pradesh | **Conditionally available** — see `docs/data_sources.md` |

---

## Five-Folder Structure

```
AirQ/
├── frontend/       # Responsive web application (HTML + CSS + JS)
├── backend/        # REST API server, data ingestion, caching, IoT simulator stub
├── data/           # Raw downloads, cleaned CSVs, development/fallback datasets
├── ml/             # Forecasting models and preprocessing (future step)
└── docs/           # Architecture, requirements, API contract, tech-stack docs
```

### What each folder contains

| Folder | Responsibility |
|---|---|
| `frontend/` | Dashboard UI; communicates only with the backend REST API, never directly with OpenAQ |
| `backend/` | Fetches from OpenAQ, caches responses, exposes REST endpoints, runs the IoT simulator |
| `data/` | Static fallback CSVs, downloaded OpenAQ datasets for offline dev, future training data |
| `ml/` | Forecasting scripts; called by the backend, not the frontend |
| `docs/` | All documentation: requirements, architecture, API contract, tech-stack rationale |

---

## Planned Architecture (Conceptual)

```
+-----------------------------------------------------------------+
|                         DATA SOURCES                           |
|   OpenAQ API (CPCB data)   |   OGD India (historical CSVs)    |
+---------------+--------------------------+----------------------+
                |                          |
                v                          v
+-----------------------------------------------------------------+
|                          BACKEND                               |
|  - Data ingestion (OpenAQ client with caching)                 |
|  - IoT Simulator (labelled SIMULATED)                          |
|  - AQI computation                                             |
|  - REST API endpoints                                          |
|  - Fallback to local CSV if API is unavailable                 |
+---------------------------+------------------------------------+
                            |   REST API (JSON)
                            v
+-----------------------------------------------------------------+
|                         FRONTEND                               |
|  - Dashboard (city selector, AQI cards, charts)                |
|  - Clearly labels data source on every widget                  |
|  - Responsive design                                           |
+-----------------------------------------------------------------+
```

---

## Technology Stack (Summary)

| Layer | Technology | Reason |
|---|---|---|
| Backend | Python + Flask | Lightweight, easy to run on a college laptop |
| Data access | OpenAQ API v3 + requests | Official open API aggregating CPCB data |
| Caching | File-based JSON cache | No extra services; works offline |
| Frontend | HTML + CSS + Vanilla JS | No build step; instantly runnable |
| Charts | Chart.js (CDN) | Zero-install, good documentation |
| Data files | CSV + JSON | Human-readable, no DB setup |
|## Project Structure (Five-Folder Architecture)

1. **`frontend/`**: The complete frontend application (HTML, CSS, JS). Runs purely in the browser.
2. **`backend/`**: The Flask REST API that proxies data, handles caching, and provides fallback simulation.
3. **`data/`**: Storage for file-based caching and static fallback CSV data.
4. **`ml/`**: The forecasting engine utilizing a lightweight pure-Python statistical model (momentum and mean reversion) to predict future pollution levels based on historical data.
5. **`docs/`**: Comprehensive project documentation mapping features to the assessment rubric.

## Core Features
*   **Real Data Integration**: Fetches live AQI and pollutant data from OpenAQ for major Indian cities, caching to minimize API calls.
*   **IoT Simulation**: A robust virtual sensor network simulates realistic IoT behavior, sensor drift, and heartbeat statuses when real data is unavailable.
*   **Responsive Dashboard**: Multi-page SPA built without external frameworks. Features live monitoring, city comparison, historical analytics, alerts, and IoT sensor health.
*   **Pollution Intelligence**: A deterministic, rule-based engine that synthesizes current conditions, trends, and alerts into explainable, human-readable summaries without relying on heavy or expensive external LLMs.
*   **Forecasting**: A lightweight, explainable statistical forecasting engine that predicts short-term (24h) and long-term (7d) pollution levels based on historical trends.

## Setup Instructions

### 1. Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
python app.py
```
The backend will run on `http://127.0.0.1:5000`.

### 2. Frontend Setup
Because the application uses a decoupled SPA architecture, the frontend files are served directly by the backend for convenience.
Once the backend is running, simply open your browser and navigate to:
**`http://127.0.0.1:5000/`**

*Note: You can also open `frontend/index.html` directly in your browser, provided your browser allows local file CORS requests.*

## Technical Constraints & Cloud Strategy
As per the assessment constraints:
*   The application operates entirely locally for evaluation purposes.
*   The architecture is inherently cloud-ready (Dockerizable Flask backend, static frontend deployable to S3/CDN), but no cloud services are required to run it locally.
*   Forecasting uses a lightweight custom statistical model rather than heavy ML frameworks (TensorFlow/PyTorch) to ensure it runs reliably on a standard laptop without complex environment dependencies.
*   Simulated data is clearly labelled with a `[SIMULATED]` or `[FALLBACK]` badge to maintain integrity and prevent confusion with real measurements.

## Known Limitations
*   Forecasting depends heavily on the availability of historical OpenAQ data. If the OpenAQ API is down or a city lacks historical coverage, the forecast module will gracefully degrade and display an "Insufficient Data" warning.
*   Virtual sensors simulate drift but do not reflect actual physical hardware.

---

## Data Integrity Policy

> **This project never fabricates pollution measurements.**
> Every reading displayed in the dashboard is tagged with one of:
> - `REAL` -- from OpenAQ / CPCB official monitoring station
> - `SIMULATED` -- from the on-device IoT simulator (clearly marked in UI)
> - `FALLBACK` -- from a pre-downloaded static dataset used when the live API is unavailable

---

*Assessment submission for Smart Air Pollution Monitoring Portal -- IoT and Dashboards*
