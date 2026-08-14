# Backend — Smart Air Pollution Monitoring Portal

This folder will contain the Flask REST API server.

## Planned Structure (Step 2)

```
backend/
├── app.py               # Flask application entry point
├── config.py            # City list, API settings, cache TTL
├── requirements.txt     # Python dependencies
├── .env.example         # Template for the API key file (never commit .env)
├── openaq_client.py     # OpenAQ API v3 wrapper
├── cache.py             # File-based JSON caching
├── aqi_calculator.py    # Compute India NAAQs AQI from pollutant values
├── iot_simulator.py     # Simulated IoT sensor (labelled SIMULATED)
├── fallback_loader.py   # Serve static CSVs when API is unavailable
└── routes/
    ├── cities.py        # GET /api/v1/cities
    ├── stations.py      # GET /api/v1/stations
    ├── readings.py      # GET /api/v1/readings/latest and /history
    ├── summary.py       # GET /api/v1/summary
    └── iot.py           # GET /api/v1/iot/latest
```

## Data Flow

External API → openaq_client.py → cache.py → routes/*.py → Frontend

## Running (Step 2 onwards)

```bash
pip install -r requirements.txt
python app.py
```

Server starts at http://localhost:5000
