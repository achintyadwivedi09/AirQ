# Architecture — Smart Air Pollution Monitoring Portal

## 1. System Overview

The system is split into three clearly separated layers:

```
+---------------------+      +---------------------+      +---------------------+
|   DATA SOURCES      |      |      BACKEND         |      |     FRONTEND        |
|                     |      |                      |      |                     |
| OpenAQ API (CPCB)   +----->| Ingestion + Cache    +----->| Dashboard (HTML/JS) |
| OGD India (CSV)     +----->| AQI Computation      |      | City Selector       |
|                     |      | REST API Layer       |      | AQI Cards           |
| IoT Simulator       +----->| Fallback Handler     |      | Pollutant Charts    |
| (SIMULATED label)   |      |                      |      | Data-source labels  |
+---------------------+      +---------------------+      +---------------------+
```

**Key design decision**: The frontend never speaks directly to OpenAQ or any external API.
The backend is the sole abstraction layer. This means the external data provider
can be swapped (e.g., from OpenAQ to another API) without changing any frontend code.

---

## 2. Component Breakdown

### 2.1 Backend (`/backend`)

| Component | Responsibility |
|---|---|
| `openaq_client.py` | Wraps OpenAQ v3 REST calls; handles auth header, timeouts, pagination |
| `cache.py` | Writes API responses to `.json` files in `data/cache/`; respects TTL |
| `aqi_calculator.py` | Computes India NAAQs-based AQI from raw pollutant concentrations |
| `iot_simulator.py` | Generates synthetic readings clearly tagged `data_type: SIMULATED` |
| `fallback_loader.py` | Reads pre-downloaded CSVs from `data/fallback/` if live API fails |
| `app.py` | Flask server; registers all REST endpoints |
| `routes/` | Individual route files (`cities.py`, `stations.py`, `readings.py`, etc.) |
| `models/reading.py` | Python dataclass for a single pollution reading (matches data model) |

### 2.2 Frontend (`/frontend`)

| Component | Responsibility |
|---|---|
| `index.html` | Single-page layout |
| `css/style.css` | Responsive styling |
| `js/api.js` | Thin wrapper around `fetch()` calls to the backend |
| `js/dashboard.js` | Renders AQI cards, charts, city selector |
| `js/labels.js` | Helper that attaches REAL / SIMULATED / FALLBACK badges |

### 2.3 Data (`/data`)

```
data/
├── raw/           # Untouched downloads from OpenAQ or OGD India
├── cleaned/       # Processed/normalised CSV files
├── fallback/      # Static CSVs served by backend when OpenAQ is unavailable
└── cache/         # Auto-generated; backend's file-based API response cache
```

### 2.4 ML (`/ml`)  — Future Step

```
ml/
├── notebooks/     # Exploratory data analysis
├── models/        # Saved model files (.pkl or .joblib)
└── src/           # Training and inference scripts
```

### 2.5 Docs (`/docs`)

```
docs/
├── architecture.md      # This file
├── requirements.md      # Functional + non-functional requirements
├── api_contract.md      # REST API endpoint specifications
├── tech_stack.md        # Technology choices and rationale
└── data_sources.md      # Data sources, limitations, Prayagraj status
```

---

## 3. Data Flow Diagrams

### 3.1 Real Data Flow (Live API)

```
+-------------------+
| OpenAQ API (CPCB) |
+--------+----------+
         |  HTTPS GET  /v3/locations?iso=IN
         |  Header: X-API-Key
         v
+--------+----------+
|  openaq_client.py |  <--- checks cache first; writes response to cache
+--------+----------+
         |
         v
+--------+----------+
|  aqi_calculator   |  <--- computes AQI from PM2.5/PM10/NO2 if not provided
+--------+----------+
         |  data_type = "REAL"
         v
+--------+----------+
|  Flask REST API   |  <--- /api/v1/readings/latest?city=Delhi
+--------+----------+
         |  JSON response
         v
+--------+----------+
|  Frontend JS      |  <--- renders card, attaches "REAL" badge
+-------------------+
```

### 3.2 IoT Simulation Flow

```
+-------------------+
|  iot_simulator.py |  <--- runs on a background thread / Flask endpoint
|  Generates values |       using real city baseline + random variation
|  data_type =      |       NEVER exceeds physically plausible ranges
|  "SIMULATED"      |
+--------+----------+
         |
         v
+--------+----------+
|  Flask REST API   |  <--- /api/v1/iot/stream
+--------+----------+
         |  JSON, data_type = "SIMULATED"
         v
+--------+----------+
|  Frontend JS      |  <--- renders with orange "SIMULATED" badge
+-------------------+
```

### 3.3 Fallback Flow (API Unavailable)

```
+-------------------+
|  fallback_loader  |  <--- reads data/fallback/<city>.csv
|  data_type =      |
|  "FALLBACK"       |
+--------+----------+
         |
         v
+--------+----------+
|  Flask REST API   |  <--- same endpoints, extra field: data_type = "FALLBACK"
+--------+----------+
         |
         v
+--------+----------+
|  Frontend JS      |  <--- renders with yellow "FALLBACK" badge
+-------------------+
```

---

## 4. Error Handling Strategy

| Failure Scenario | Backend Response | Frontend Display |
|---|---|---|
| OpenAQ API timeout | Return FALLBACK data | Show "FALLBACK" badge + warning banner |
| OpenAQ returns 401 | Log error, use FALLBACK | Show "FALLBACK" badge |
| City has no stations | Return empty list | Show "No data available" message |
| Pollutant value missing | Set field to `null` | Hide that pollutant card |
| Prayagraj not found in API | Use fallback CSV | Show "FALLBACK" badge |

---

## 5. Caching Strategy

- Cache TTL for live readings: **30 minutes** (configurable via `config.py`)
- Cache TTL for station metadata: **24 hours**
- Cache is stored as plain JSON files in `data/cache/`
- If the cache file is fresh, the backend serves it without contacting OpenAQ
- This prevents repeated API calls during development and demos

---

## 6. Security Considerations (College-level)

- OpenAQ API key stored in `.env` file, never committed to version control.
- `.env` added to `.gitignore`.
- No user authentication required (read-only dashboard).
- CORS enabled on backend for local development only.

---

*Document version: 1.0 | Step 1 — Foundation*
