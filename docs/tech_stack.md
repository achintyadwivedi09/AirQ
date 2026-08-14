# Technology Stack — Smart Air Pollution Monitoring Portal

---

## Stack Summary

| Layer | Technology | Version |
|---|---|---|
| Backend runtime | Python | 3.9+ |
| Backend framework | Flask | 3.x |
| HTTP client | requests | 2.x |
| Environment config | python-dotenv | 1.x |
| Frontend structure | HTML5 | — |
| Frontend styling | Vanilla CSS3 | — |
| Frontend logic | Vanilla JavaScript (ES6+) | — |
| Charts | Chart.js (via CDN) | 4.x |
| Data files | CSV + JSON | — |
| ML (future) | scikit-learn + statsmodels | Latest |

---

## Rationale for Each Choice

### Python + Flask (Backend)

**Why Python?**
- Standard language for data science and college coursework.
- Excellent libraries for HTTP requests, data processing, and ML.
- Works on every OS without complex setup.

**Why Flask (not Django or FastAPI)?**
- Flask is the smallest possible web framework — a single file can be a working API.
- No ORM, no migrations, no admin panel overhead needed for this project.
- Easy to explain in a viva: "One function = one endpoint."
- FastAPI would also work but requires Pydantic type-model setup that adds
  unnecessary complexity for a first-step foundation.

### requests (HTTP Client)

- The standard Python library for making HTTP calls.
- `httpx` (async) would be overkill at this stage.
- Simple, well-documented, beginner-friendly.

### python-dotenv (Configuration)

- Allows storing the OpenAQ API key in a `.env` file that is never committed.
- One-liner setup: `load_dotenv()`.
- Recognised pattern that demonstrates good security habits for the assessment.

### File-based JSON Cache (No Database)

**Why no database at this stage?**
- SQLite or PostgreSQL would require additional setup, schema design, and
  migration scripts — all unnecessary for the foundation step.
- A file-based cache in `data/cache/` achieves the same rate-limiting goal
  with zero dependencies.
- Easy to inspect: open the JSON file in any text editor to see cached data.
- The cache can be replaced with a real DB in a later step without changing
  the rest of the code (abstraction via `cache.py`).

### Vanilla HTML + CSS + JavaScript (Frontend)

**Why not React / Vue / Angular?**
- No build step means the frontend runs by opening `index.html` — ideal for
  a college demo.
- No npm, no webpack, no node_modules folder taking gigabytes.
- Assessment reviewer can open the project without any installation.
- The architecture separates frontend from backend cleanly via REST APIs,
  so migrating to React later is straightforward if needed.
- Vanilla JS with `fetch()` is sufficient for this dashboard's needs.

### Chart.js (via CDN)

**Why Chart.js?**
- Loaded from a CDN — no install, no build.
- Line charts, bar charts, and doughnut charts are available out of the box.
- Good documentation with simple examples.
- Sufficient for time-series AQI charts and pollutant comparison bars.
- D3.js would offer more power but has a steep learning curve
  unnecessary for this assessment.

### CSV + JSON (Data Files)

- Human-readable; can be opened in Excel or any text editor.
- No schema setup required.
- Suitable for the fallback dataset and cache files.
- Python's built-in `csv` and `json` modules handle them with no extra install.

### OpenAQ API v3 (Primary Data Source)

- **Official**: OpenAQ aggregates data directly from CPCB (India's pollution regulator).
- **Free API key**: Free registration at explore.openaq.org.
- **Coverage**: Hundreds of CPCB stations across India including major cities.
- **v3 is current**: v1 and v2 are deprecated.
- **Rate-friendly**: With caching, only a few calls per day are needed.
- **Alternative considered**: WAQI (World Air Quality Index) also covers India but
  is less transparent about its data source and licensing.

### OGD India (Secondary / Fallback Data Source)

- India's Open Government Data platform (data.gov.in) provides historical
  CPCB datasets as CSV downloads.
- Used for building the local fallback dataset.
- No API key required for bulk downloads.

### scikit-learn + statsmodels (Future ML Layer)

- Standard libraries taught in college data science courses.
- ARIMA (statsmodels) is a well-understood time-series model suitable for
  PM2.5 forecasting as a baseline.
- scikit-learn Random Forest can serve as a comparison model.
- Both are explainable in a viva.
- Not installed at Step 1 — will be added in the ML step only.

---

## What Was Explicitly Rejected and Why

| Technology | Reason Rejected |
|---|---|
| Node.js / Express backend | Python is more appropriate for data/ML integration |
| Django | Too heavy for a simple REST API; admin panel not needed |
| FastAPI | Adds Pydantic type complexity not needed in Step 1 |
| React / Next.js | Requires build toolchain; overkill for this assessment |
| MongoDB | No database needed in foundation; adds setup complexity |
| Redis | Not needed; file cache is sufficient |
| TensorFlow / PyTorch | Too heavy for a college laptop; scikit-learn sufficient |
| Web scraping (CPCB website) | Unreliable; OpenAQ API is the correct programmatic approach |
| Any paid API | Not appropriate for a college assessment |
| Cloud services (AWS, GCP) | Out of scope per project instructions |

---

## Dependency Minimalism Principle

Every library added must answer "yes" to ALL of:
1. Is it actually used in this step?
2. Is there no standard-library alternative?
3. Does it work on a college laptop without admin privileges?

At Step 1, the backend has zero Python dependencies installed
(requirements.txt is written but `pip install` runs in Step 2).

---

## Future Additions (Planned)

| Step | New Dependency | Purpose |
|---|---|---|
| Step 2 | Flask, requests, python-dotenv | Backend server |
| Step 3 | Chart.js (CDN, no install) | Dashboard charts |
| ML step | pandas, scikit-learn, statsmodels | Forecasting |

---

*Document version: 1.0 | Step 1 — Foundation*
