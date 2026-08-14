"""
Offline Data Provider — serves pre-downloaded historical CSV data.
Completely bypasses OpenAQ API to guarantee 0-second load times.
"""
import os
import csv
from datetime import datetime, timezone

from config import CITIES, POLLUTANTS
from aqi_calculator import calculate_aqi

HISTORICAL_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'data', 'historical')
)


def discover_stations_for_city(city_id, force_refresh=False):
    """Return a mocked station representing the local dataset."""
    city = CITIES.get(city_id)
    if not city:
        return []
    
    if not os.path.exists(os.path.join(HISTORICAL_DIR, f"{city_id}.csv")):
        return []
        
    return [{
        'id': f"LOCAL-{city_id.upper()}",
        'name': f"{city['name']} (Historical Data)",
        'lat': city['lat'],
        'lon': city['lon'],
        'sensors': []
    }]


def get_latest_reading(city_id, station_id=None, force_refresh=False):
    """Load the latest reading from the local historical CSV file."""
    city = CITIES.get(city_id)
    if not city:
        return None

    csv_path = os.path.join(HISTORICAL_DIR, f"{city_id}.csv")
    if not os.path.exists(csv_path):
        return None

    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        if not rows:
            return None

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
            'station_id': f"LOCAL-{city_id.upper()}",
            'station_name': f"{city['name']} (Historical Data)",
            'lat': city['lat'],
            'lon': city['lon'],
            'reading_timestamp': row.get('timestamp', datetime.now(timezone.utc).isoformat()),
            'aqi': aqi,
            'aqi_category': aqi_cat,
            'dominant_pollutant': dominant,
            'data_type': 'REAL',
            'source': 'Local Historical CSV',
            'provider': 'Offline',
            'pollutants': pollutants_dict,
        }
    except Exception as e:
        print(f"[Local] Error reading {csv_path}: {e}")
        return None


def get_historical_readings(city_id, station_id=None, days=7, pollutant='pm25', force_refresh=False):
    """Load historical readings from the local CSV."""
    csv_path = os.path.join(HISTORICAL_DIR, f"{city_id}.csv")
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
        print(f"[Local] Error reading history from {csv_path}: {e}")
        return []


def get_summary_stats(city_id, days=7, force_refresh=False):
    """Compute summary stats directly from the local CSV."""
    csv_path = os.path.join(HISTORICAL_DIR, f"{city_id}.csv")
    if not os.path.exists(csv_path):
        return {}

    summary = {}
    for poll_key, poll_info in POLLUTANTS.items():
        readings = get_historical_readings(city_id, None, days, poll_key)
        valid_vals = [r['value'] for r in readings if r.get('value') is not None]
        if valid_vals:
            summary[poll_key] = {
                'name': poll_info['name'],
                'unit': poll_info['unit'],
                'min': round(min(valid_vals), 1),
                'max': round(max(valid_vals), 1),
                'avg': round(sum(valid_vals) / len(valid_vals), 1),
                'count': len(valid_vals)
            }
    return summary
