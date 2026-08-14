"""
Fallback data loader — serves pre-downloaded static data
when the live OpenAQ API is unavailable.
All fallback readings are tagged data_type = "FALLBACK".
"""
import os
import csv
import json
from datetime import datetime, timezone

from config import CITIES, POLLUTANTS
from aqi_calculator import calculate_aqi

FALLBACK_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'data', 'fallback')
)


def get_fallback_reading(city_id):
    """
    Load the latest reading from a fallback CSV file for a city.
    Returns a reading dict with data_type = "FALLBACK", or None.
    """
    city = CITIES.get(city_id)
    if not city:
        return None

    csv_path = os.path.join(FALLBACK_DIR, f"{city_id}.csv")
    if not os.path.exists(csv_path):
        return None

    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        if not rows:
            return None

        # Use last row (most recent)
        row = rows[-1]
        pollutant_values = {}
        pollutants_dict = {}

        for key in POLLUTANTS:
            raw = row.get(key)
            val = None
            if raw and raw.strip() and raw.strip().lower() not in ('na', 'null', '', '-'):
                try:
                    val = float(raw)
                except (ValueError, TypeError):
                    val = None
            pollutant_values[key] = val
            pollutants_dict[key] = {
                'value': val,
                'unit': POLLUTANTS[key]['unit'],
            }

        aqi, aqi_cat, dominant = calculate_aqi(pollutant_values)

        return {
            'city': city['name'],
            'city_id': city_id,
            'station_id': f"FALLBACK-{city_id.upper()}",
            'station_name': f"{city['name']} — Fallback Data",
            'lat': city['lat'],
            'lon': city['lon'],
            'reading_timestamp': row.get('timestamp',
                                         datetime.now(timezone.utc).isoformat()),
            'aqi': aqi,
            'aqi_category': aqi_cat,
            'dominant_pollutant': dominant,
            'data_type': 'FALLBACK',
            'source': 'Static Fallback CSV',
            'provider': 'Fallback',
            'pollutants': pollutants_dict,
        }
    except Exception as e:
        print(f"[Fallback] Error reading {csv_path}: {e}")
        return None


def get_fallback_history(city_id, pollutant='pm25', days=7):
    """
    Load historical readings from fallback CSV.
    Returns list of {timestamp, value} dicts.
    """
    csv_path = os.path.join(FALLBACK_DIR, f"{city_id}.csv")
    if not os.path.exists(csv_path):
        return []

    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        readings = []
        for row in rows[-days * 24:]:  # Assume hourly data, take last N days
            raw = row.get(pollutant)
            val = None
            if raw and raw.strip() and raw.strip().lower() not in ('na', 'null', '', '-'):
                try:
                    val = float(raw)
                except (ValueError, TypeError):
                    pass
            readings.append({
                'timestamp': row.get('timestamp', ''),
                'value': val,
            })
        return readings
    except Exception as e:
        print(f"[Fallback] Error reading history from {csv_path}: {e}")
        return []


def has_fallback_data(city_id):
    """Check if fallback CSV exists for a city."""
    return os.path.exists(os.path.join(FALLBACK_DIR, f"{city_id}.csv"))
