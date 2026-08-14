# Requirements — Smart Air Pollution Monitoring Portal

---

## 1. Functional Requirements

### FR-01: City Support
- The system shall support at least 10 major Indian cities:
  Delhi, Mumbai, Chennai, Bengaluru, Kolkata, Hyderabad, Pune, Ahmedabad, Lucknow, Prayagraj.
- Each city shall display its available monitoring stations.
- If no station data is available for a city, the system shall display a clear message rather than fabricated data.

### FR-02: Real-time Pollution Readings
- The backend shall fetch the latest available readings from the OpenAQ v3 API.
- Readings shall include any available subset of: PM2.5, PM10, NO2, SO2, CO, O3.
- The system shall not display a measurement for a pollutant if the value is null or missing in the source data.

### FR-03: AQI Display
- The system shall display an AQI value for each city/station.
- If the OpenAQ API provides AQI directly, that value shall be used.
- If AQI is not provided, the backend shall calculate it using India's NAAQs standard from available pollutant values.
- If AQI cannot be computed (insufficient data), the AQI card shall be hidden.

### FR-04: IoT Simulation
- The backend shall include an IoT simulator module that generates synthetic pollution readings.
- All simulated readings shall be clearly tagged with `data_type = "SIMULATED"`.
- The simulated sensor shall be labelled "SIMULATED SENSOR" throughout the UI.
- Simulated values shall use realistic baseline ranges derived from historical city data.
- The simulator shall not generate physically implausible values.

### FR-05: Data Source Labelling
- Every data point displayed in the frontend shall carry a visible label:
  - Green badge: **REAL** (from OpenAQ/CPCB)
  - Orange badge: **SIMULATED** (from IoT simulator)
  - Yellow badge: **FALLBACK** (from pre-downloaded static dataset)
- The data source label shall never be absent for any displayed reading.

### FR-06: Historical Data View (Future)
- The dashboard shall eventually show a time-series chart of readings for the past 7 days.
- Historical data will be retrieved from OpenAQ's measurements endpoint or from local CSVs.

### FR-07: Multi-city Comparison (Future)
- The dashboard shall allow selecting multiple cities for side-by-side AQI comparison.

### FR-08: Forecasting Display (Future)
- The dashboard shall display a 24-hour forecast produced by the ML module.
- Forecast values shall be clearly labelled as **PREDICTED**.

### FR-09: Alert System (Future)
- The system shall raise an alert when AQI exceeds a configurable threshold.
- Alerts shall be displayed as banners in the frontend.

### FR-10: Graceful Degradation
- When the OpenAQ API is unavailable, the backend shall automatically switch to FALLBACK data.
- The frontend shall display a warning when FALLBACK data is being served.

---

## 2. Non-Functional Requirements

### NFR-01: Performance
- Dashboard initial load time shall be under 3 seconds on a standard college laptop.
- Backend API response time shall be under 500 ms for cached responses.
- Backend API response time shall be under 5 seconds for uncached live-API responses.
- API responses shall be compact (no redundant fields).

### NFR-02: Responsive Design
- The frontend shall be functional and readable on:
  - Desktop (1280px+)
  - Tablet (768px–1279px)
  - Mobile (320px–767px)
- No horizontal scrolling shall appear on any screen width.

### NFR-03: Reliability
- The system shall fall back to static data if the live API is unavailable or times out.
- API timeouts shall be set to 10 seconds maximum.
- The backend shall not crash on missing or null pollutant values.

### NFR-04: Data Integrity
- The system shall never insert fabricated measurement values.
- All null/missing pollutant fields shall remain null in the data model.
- The data source type (REAL / SIMULATED / FALLBACK) shall be preserved end-to-end from ingestion to UI.

### NFR-05: Maintainability
- Code shall be organised by function (ingestion, computation, API, UI).
- Each module shall have a clear, single responsibility.
- All configuration (API keys, TTLs, city list) shall live in one config file.
- API keys shall never be committed to version control.

### NFR-06: Simplicity (College Project Context)
- The project shall run entirely on a college laptop without cloud services.
- No external database shall be required at this stage.
- Installation shall require only `pip install -r requirements.txt` for the backend.
- The frontend shall require no build step (open `index.html` directly).

---

## 3. Data Source Requirements

### DSR-01: Primary Data Source
- The primary source for live pollution data shall be the **OpenAQ API v3**.
- OpenAQ aggregates data from CPCB (India's Central Pollution Control Board).
- The backend shall use the API key mechanism (X-API-Key header) as required by OpenAQ v3.
- API key shall be stored in `.env` and loaded via `python-dotenv`.

### DSR-02: Secondary / Fallback Source
- Pre-downloaded CSVs from OpenAQ or India's **Open Government Data (OGD)** platform
  shall be stored in `data/fallback/` as a backup.
- Fallback data shall be used only when the live API is unavailable.
- Fallback readings shall be labelled `data_type = "FALLBACK"`.

### DSR-03: Prayagraj-specific Policy
- Prayagraj monitoring stations (Nagar Nigam, MNNIT Shivkuti) are present in CPCB's
  network and are expected to be accessible via OpenAQ.
- A runtime station-discovery step shall be used to confirm their `location_id`
  rather than hardcoding IDs.
- If no Prayagraj station is found via the API, the system shall serve FALLBACK data
  and display a "Station data currently unavailable" message.
- Under no circumstances shall the system display fabricated readings for Prayagraj.

### DSR-04: Data Update Frequency
- Live readings shall be cached for 30 minutes to avoid excessive API calls.
- During development and demos, cached data shall be preferred.
- Manual cache-busting shall be possible via a query parameter (`?refresh=true`).

---

## 4. Forecasting Requirements (Future Steps)

### PR-01: Forecast Scope
- The ML module shall produce a 24-hour ahead forecast for PM2.5 and AQI.
- Forecasting shall be station-level (not city-average).

### PR-02: Input Data
- The model shall use historical time-series readings from `data/cleaned/`.
- A minimum of 30 days of hourly readings is required to train a baseline model.

### PR-03: Model Transparency
- The model type (e.g., ARIMA, Random Forest) shall be documented.
- Confidence intervals or uncertainty ranges shall be displayed if possible.
- Forecast values shall be labelled **PREDICTED** in the UI.

---

## 5. IoT Simulation Requirements (Future Steps)

### IR-01: Simulator Design
- The IoT simulator shall generate readings for a virtual sensor assigned to one city.
- It shall produce values every 60 seconds (configurable).
- Values shall be generated using a statistical model seeded from real historical ranges.

### IR-02: Labelling
- All simulator output shall carry `data_type = "SIMULATED"` at the data-model level.
- The frontend shall display an animated icon or badge to distinguish simulated readings.

### IR-03: No Physical Hardware Required
- The simulator shall run entirely in software, demonstrating IoT concepts without
  needing a physical sensor device.

---

*Document version: 1.0 | Step 1 — Foundation*
