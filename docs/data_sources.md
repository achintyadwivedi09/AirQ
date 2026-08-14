# Data Sources — Smart Air Pollution Monitoring Portal

---

## 1. Primary Data Source: OpenAQ API v3

### What is OpenAQ?

OpenAQ (openaq.org) is a non-profit open platform that aggregates air quality data
from government-operated reference-grade monitoring networks worldwide.
For India, OpenAQ ingests data directly from the **Central Pollution Control Board (CPCB)**,
which is the statutory authority under India's Ministry of Environment, Forest and Climate Change.

This means data obtained from OpenAQ for Indian stations is ultimately official CPCB data,
made available through a standardised, programmatic interface.

### API Version

The project uses **OpenAQ API v3** (the current version as of 2025).
Earlier versions (v1, v2) are deprecated and must not be used.

### Authentication

- OpenAQ v3 requires an API key for all requests.
- Registration is free at: https://explore.openaq.org/register
- The key is sent in the HTTP request header: `X-API-Key: <your_key>`
- The key is stored in a `.env` file and never committed to version control.

### Relevant Endpoints (v3)

| Endpoint | Purpose |
|---|---|
| `GET /v3/locations?iso=IN` | Lists all Indian monitoring stations |
| `GET /v3/locations/{id}/latest` | Latest reading for a specific station |
| `GET /v3/measurements?location_id=<id>` | Historical readings for a station |
| `GET /v3/parameters` | Lists available pollutant parameters and their IDs |

### Parameters (Pollutant IDs)

Commonly used OpenAQ parameter IDs for this project:

| Pollutant | OpenAQ Parameter Name | Unit |
|---|---|---|
| PM2.5 | `pm25` | µg/m³ |
| PM10 | `pm10` | µg/m³ |
| NO2 | `no2` | µg/m³ |
| SO2 | `so2` | µg/m³ |
| CO | `co` | mg/m³ |
| O3 | `o3` | µg/m³ |

Note: Not all parameters are available at every station.
The data model uses `null` for missing values.

### Rate Limits

- Free tier: Sufficient for development with 30-minute caching.
- The backend caches all responses to avoid repeated calls.

### OpenAQ Limitations

| Limitation | Mitigation |
|---|---|
| Requires API key | Stored securely in `.env` |
| Some CPCB stations go offline periodically | Fallback to cached or CSV data |
| Historical data depth varies by station | Use OGD India CSVs for extended history |
| API may be slow for large date ranges | Use date-chunked requests |
| v3 requires pagination for full city lists | Backend handles pagination |

---

## 2. Secondary Source: Open Government Data (OGD) India

### What is OGD India?

The Indian government's open data portal at **data.gov.in** provides downloadable
datasets from various ministries including CPCB air quality data.

### How it will be used

- **Fallback dataset**: Pre-downloaded CSVs stored in `data/fallback/` for use
  when the OpenAQ API is unavailable.
- **Historical training data**: Extended historical records for the ML forecasting module.

### Limitations

- CSVs must be manually downloaded; no real-time API access.
- Data format varies between datasets (column names, units may differ).
- Requires preprocessing before use.

---

## 3. IoT Simulator (Internal — Not an External Source)

The IoT simulator (`backend/iot_simulator.py`) is an internal module, not an
external data source. It generates synthetic readings to demonstrate IoT concepts.

All simulator output is labelled `data_type = "SIMULATED"` at the data model level.
The frontend displays a clearly visible SIMULATED badge on all IoT readings.

The simulator uses realistic baseline ranges derived from historical data for each city,
but it never claims its output is real measurement data.

---

## 4. Prayagraj — Availability Investigation

### Research Summary

Investigation into OpenAQ/CPCB coverage for Prayagraj was conducted before
this project was built. The findings are:

| Finding | Detail |
|---|---|
| CPCB stations in Prayagraj | Yes — confirmed by CPCB's CAAQM portal |
| Known station locations | Nagar Nigam (Civil Lines), MNNIT Shivkuti, Jhunsi |
| OpenAQ expected coverage | Expected to be available; must be confirmed at runtime via API |
| Specific location_id known? | **No** — IDs must be discovered via `/v3/locations?iso=IN` |
| Risk | OpenAQ may have intermittent or delayed data for tier-2 cities |

### Conclusion and Policy

**Prayagraj station IDs are NOT hardcoded** in this project.

At startup, the backend will query `/v3/locations?iso=IN` and search for any
location where `city` contains "Prayagraj" or "Allahabad" (the city's former name,
which some records may still use).

If stations are found: live data will be served with `data_type = "REAL"`.

If no stations are found via OpenAQ: the backend will fall back to a pre-downloaded
CSV from `data/fallback/prayagraj.csv` and serve it with `data_type = "FALLBACK"`.
The frontend will display: *"Station data currently unavailable from OpenAQ.
Showing last available data."*

Under no circumstances will fabricated PM2.5, PM10, or AQI values be inserted
for Prayagraj or any other city.

### Verification Steps (To Be Done in Step 2)

1. Register for an OpenAQ API key.
2. Run: `GET https://api.openaq.org/v3/locations?iso=IN&limit=1000`
3. Filter results for `city` containing "Prayagraj" or "Allahabad".
4. Log the discovered `location_id` values in `data/verified_stations.json`.
5. Update `docs/data_sources.md` with the confirmed IDs.

---

## 5. Data Source Comparison

| Source | Real-time? | Free? | Programmatic? | Coverage |
|---|---|---|---|---|
| OpenAQ API v3 | Yes | Yes (key required) | Yes | 100+ Indian cities |
| OGD India | No (bulk download) | Yes | No | Varies |
| CPCB CAAQM portal | Yes (web UI only) | Yes | No (no API) | Full India |
| WAQI API | Yes | Yes (limited) | Yes | Selected Indian cities |
| IoT Simulator | Real-time (synthetic) | N/A | Internal | Any city |

### Why WAQI was not chosen as primary

The World Air Quality Index (WAQI) API also covers Indian cities but:
- Attribution requirements are complex.
- Data sources are less transparent.
- OpenAQ is a fully open, non-profit platform with clear CPCB attribution.
- OpenAQ v3 covers more stations with better programmatic access.

---

## 6. Data Integrity Rules (Non-negotiable)

1. If a pollutant reading is not available from the source, the field is set to `null`.
2. Null fields are never filled with estimated or fabricated values.
3. Every reading carried in the system has a `data_type` field: `REAL`, `SIMULATED`, or `FALLBACK`.
4. The IoT simulator only generates data clearly marked as `SIMULATED`.
5. Fallback CSV data is never presented as live data.

---

*Document version: 1.0 | Step 1 — Foundation*
*Prayagraj availability status: PENDING runtime verification (Step 2)*
