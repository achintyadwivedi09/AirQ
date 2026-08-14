# Data Model — Smart Air Pollution Monitoring Portal

## Overview

This document defines the canonical data structure for a pollution reading.
This model is used throughout the system — from data ingestion to the REST API
response to the frontend display.

The model is designed to:
- Support multiple cities and multiple stations per city.
- Allow any pollutant field to be null (never fabricated).
- Carry a mandatory data_type tag (REAL / SIMULATED / FALLBACK).
- Support time-series analysis for future ML forecasting.
- Store coordinates for future map visualisation.

---

## PollutionReading Model

### Python Representation (Dataclass — to be used in Step 2)

```python
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

@dataclass
class PollutantValue:
    """A single pollutant measurement with its unit."""
    value: Optional[float]    # None if not reported — NEVER fabricated
    unit: str                 # e.g., "µg/m³" or "mg/m³"


@dataclass
class PollutionReading:
    """
    Canonical model for one air quality reading from any source.

    data_type values:
      "REAL"      - from OpenAQ API (CPCB official station)
      "SIMULATED" - from the IoT simulator module
      "FALLBACK"  - from a pre-downloaded static CSV/JSON file
    """

    # --- Location identification ---
    city: str                           # e.g., "Prayagraj"
    station_id: Optional[str]           # OpenAQ location_id or "SIM-SENSOR-01"
    station_name: Optional[str]         # Human-readable station name
    lat: Optional[float]                # Decimal degrees; None if unavailable
    lon: Optional[float]                # Decimal degrees; None if unavailable

    # --- Time ---
    reading_timestamp: datetime         # When the measurement was taken (UTC)

    # --- Pollutants (all optional — null means not reported) ---
    pm25: Optional[PollutantValue]      # Fine particulate matter (µg/m³)
    pm10: Optional[PollutantValue]      # Coarse particulate matter (µg/m³)
    no2:  Optional[PollutantValue]      # Nitrogen dioxide (µg/m³)
    so2:  Optional[PollutantValue]      # Sulfur dioxide (µg/m³)
    co:   Optional[PollutantValue]      # Carbon monoxide (mg/m³)
    o3:   Optional[PollutantValue]      # Ozone (µg/m³)

    # --- AQI ---
    aqi: Optional[int]                  # AQI value; None if not computable
    aqi_category: Optional[str]         # "Good", "Moderate", "Unhealthy", etc.

    # --- Data provenance (mandatory) ---
    data_type: str                      # "REAL", "SIMULATED", or "FALLBACK"
    source: str                         # e.g., "OpenAQ/CPCB", "IoT Simulator",
                                        #        "Fallback CSV"
    provider: Optional[str]             # e.g., "CPCB", "UPPCB"
```

---

## JSON Wire Format (REST API)

```json
{
  "city": "Prayagraj",
  "station_id": "openaq-12345",
  "station_name": "Nagar Nigam, Civil Lines",
  "lat": 25.4516,
  "lon": 81.8415,
  "reading_timestamp": "2025-08-14T15:45:00Z",
  "pollutants": {
    "pm25": { "value": 58.3,  "unit": "µg/m³" },
    "pm10": { "value": 112.0, "unit": "µg/m³" },
    "no2":  { "value": 34.5,  "unit": "µg/m³" },
    "so2":  { "value": null,  "unit": "µg/m³" },
    "co":   { "value": 1.2,   "unit": "mg/m³" },
    "o3":   { "value": null,  "unit": "µg/m³" }
  },
  "aqi": 142,
  "aqi_category": "Unhealthy for Sensitive Groups",
  "data_type": "REAL",
  "source": "OpenAQ/CPCB",
  "provider": "CPCB"
}
```

Note: `null` pollutant values are explicitly present in the JSON (not omitted),
so the frontend knows the field exists but has no data.

---

## City Model

```python
@dataclass
class City:
    id: str             # URL-safe identifier e.g., "prayagraj"
    name: str           # Display name e.g., "Prayagraj"
    state: str          # e.g., "Uttar Pradesh"
    lat: float          # Approximate city centre latitude
    lon: float          # Approximate city centre longitude
    note: Optional[str] # e.g., "Station availability subject to OpenAQ coverage"
```

---

## Station Model

```python
@dataclass
class Station:
    station_id: str         # OpenAQ location_id or simulator ID
    name: str               # Human-readable name
    city: str               # Parent city ID
    lat: Optional[float]
    lon: Optional[float]
    provider: str           # e.g., "CPCB", "UPPCB"
    is_active: bool         # Whether readings are currently expected
```

---

## City Configuration Table (Planned)

This table will live in `backend/config.py` and drives city support:

| City ID | Display Name | State | Centre Lat | Centre Lon |
|---|---|---|---|---|
| `delhi` | Delhi | Delhi | 28.6139 | 77.2090 |
| `mumbai` | Mumbai | Maharashtra | 19.0760 | 72.8777 |
| `chennai` | Chennai | Tamil Nadu | 13.0827 | 80.2707 |
| `bengaluru` | Bengaluru | Karnataka | 12.9716 | 77.5946 |
| `kolkata` | Kolkata | West Bengal | 22.5726 | 88.3639 |
| `hyderabad` | Hyderabad | Telangana | 17.3850 | 78.4867 |
| `pune` | Pune | Maharashtra | 18.5204 | 73.8567 |
| `ahmedabad` | Ahmedabad | Gujarat | 23.0225 | 72.5714 |
| `lucknow` | Lucknow | Uttar Pradesh | 26.8467 | 80.9462 |
| `prayagraj` | Prayagraj | Uttar Pradesh | 25.4358 | 81.8464 |

---

## AQI Categories (India NAAQs Standard)

| AQI Range | Category | Colour |
|---|---|---|
| 0 – 50 | Good | Green |
| 51 – 100 | Satisfactory | Light Green |
| 101 – 200 | Moderate | Yellow |
| 201 – 300 | Poor | Orange |
| 301 – 400 | Very Poor | Red |
| 401 – 500+ | Severe / Hazardous | Dark Red / Maroon |

---

## Time-Series Design Notes

- `reading_timestamp` is always stored in UTC.
- The frontend converts to IST (UTC+5:30) for display.
- Historical readings are a list of `PollutionReading` objects sorted ascending
  by `reading_timestamp`.
- Gaps (null values at certain timestamps) are preserved; never interpolated.

---

*Document version: 1.0 | Step 1 — Foundation*
