"""
OpenAQ API v3 client — isolated data-provider logic.
The rest of the backend only calls functions in this module.
If the provider changes, only this file needs editing.
"""
import requests
from datetime import datetime, timedelta, timezone

from config import (
    OPENAQ_API_KEY, OPENAQ_BASE_URL, OPENAQ_TIMEOUT,
    CITIES, POLLUTANTS, CACHE_TTL_READINGS, CACHE_TTL_STATIONS,
)
from cache import get_cached, set_cached
from aqi_calculator import calculate_aqi, get_aqi_category


def _headers():
    h = {'Accept': 'application/json'}
    if OPENAQ_API_KEY:
        h['X-API-Key'] = OPENAQ_API_KEY
    return h


def _get(endpoint, params=None):
    """Make a GET request to OpenAQ v3. Returns parsed JSON or None on error."""
    url = f"{OPENAQ_BASE_URL}{endpoint}"
    try:
        resp = requests.get(url, headers=_headers(), params=params, timeout=OPENAQ_TIMEOUT)
        if resp.status_code == 200:
            return resp.json()
        print(f"[OpenAQ] {resp.status_code} for {url} params={params}")
        return None
    except requests.RequestException as e:
        print(f"[OpenAQ] Request error: {e}")
        return None


# ──────────────────────────────────────────────
# Station discovery
# ──────────────────────────────────────────────

def discover_stations_for_city(city_id, force_refresh=False):
    """
    Find OpenAQ monitoring locations for a city.
    Uses bounding-box search around the city centre.
    Returns list of station dicts or empty list.
    """
    city = CITIES.get(city_id)
    if not city:
        return []

    cache_params = {'city': city_id, 'type': 'stations'}
    if not force_refresh:
        cached = get_cached('stations', cache_params, CACHE_TTL_STATIONS)
        if cached is not None:
            return cached

    # Bounding box: ~50km around city centre
    delta = 0.5  # roughly 55km
    bbox = f"{city['lon'] - delta},{city['lat'] - delta},{city['lon'] + delta},{city['lat'] + delta}"

    all_locations = []
    page = 1
    max_pages = 5

    while page <= max_pages:
        data = _get('/locations', params={
            'bbox': bbox,
            'limit': 100,
            'page': page,
        })
        if not data or 'results' not in data:
            break

        results = data['results']
        if not results:
            break

        for loc in results:
            # Filter: must match city search terms
            loc_name = (loc.get('name') or '').lower()
            loc_city = (loc.get('locality') or loc.get('city') or '').lower()
            search_match = any(
                term.lower() in loc_name or term.lower() in loc_city
                for term in city.get('search_terms', [city['name']])
            )
            # Also accept if within tight bbox
            coords = loc.get('coordinates') or {}
            lat = coords.get('latitude')
            lon = coords.get('longitude')
            geo_match = (lat is not None and lon is not None and
                         abs(lat - city['lat']) < 0.3 and
                         abs(lon - city['lon']) < 0.3)

            if search_match or geo_match:
                station = {
                    'station_id': str(loc.get('id', '')),
                    'name': loc.get('name', 'Unknown Station'),
                    'city': city['name'],
                    'city_id': city_id,
                    'lat': lat,
                    'lon': lon,
                    'provider': _extract_provider(loc),
                    'is_active': loc.get('isMonitor', True),
                    'parameters': [p.get('parameter', p.get('name', '')) if isinstance(p, dict) else str(p)
                                   for p in (loc.get('sensors') or loc.get('parameters') or [])],
                }
                all_locations.append(station)

        if len(results) < 100:
            break
        page += 1

    set_cached('stations', cache_params, all_locations)
    return all_locations


def _extract_provider(loc):
    """Extract provider name from OpenAQ location object."""
    # v3 may have 'provider' as dict or string
    provider = loc.get('provider')
    if isinstance(provider, dict):
        return provider.get('name', 'Unknown')
    if isinstance(provider, str):
        return provider
    # Try owner
    owner = loc.get('owner')
    if isinstance(owner, dict):
        return owner.get('name', 'Unknown')
    return 'CPCB'


# ──────────────────────────────────────────────
# Latest readings
# ──────────────────────────────────────────────

def get_latest_reading(city_id, station_id=None, force_refresh=False):
    """
    Get the latest available reading for a city or specific station.
    Returns a reading dict or None.
    """
    cache_params = {'city': city_id, 'station': station_id, 'type': 'latest'}
    if not force_refresh:
        cached = get_cached('latest', cache_params, CACHE_TTL_READINGS)
        if cached is not None:
            return cached

    if station_id:
        reading = _fetch_station_latest(city_id, station_id)
    else:
        # Get all stations, pick the first with data
        stations = discover_stations_for_city(city_id)
        reading = None
        for st in stations:
            r = _fetch_station_latest(city_id, st['station_id'])
            if r:
                reading = r
                break

    if reading:
        set_cached('latest', cache_params, reading)
    return reading


def _fetch_station_latest(city_id, station_id):
    """Fetch latest measurements from a specific OpenAQ location."""
    data = _get(f'/locations/{station_id}/latest')
    if not data or 'results' not in data:
        return None

    results = data.get('results', [])
    if not results:
        return None

    city = CITIES.get(city_id, {})
    pollutant_values = {}
    pollutants_dict = {}
    latest_ts = None

    for measurement in results:
        # v3 returns sensors with latest values
        param = _normalize_param(measurement)
        value = measurement.get('value')
        ts_str = measurement.get('datetime', {}).get('utc') or measurement.get('lastUpdated')

        if param and param in POLLUTANTS:
            pollutant_values[param] = value
            pollutants_dict[param] = {
                'value': value,
                'unit': POLLUTANTS[param]['unit'],
            }
            if ts_str and (latest_ts is None or ts_str > latest_ts):
                latest_ts = ts_str

    if not pollutants_dict:
        return None

    # Fill missing pollutants with null (never fabricated)
    for key in POLLUTANTS:
        if key not in pollutants_dict:
            pollutants_dict[key] = {'value': None, 'unit': POLLUTANTS[key]['unit']}

    # Calculate AQI
    aqi, aqi_cat, dominant = calculate_aqi(pollutant_values)

    # Get station info from cache or construct from data
    stations = discover_stations_for_city(city_id)
    station_info = next((s for s in stations if s['station_id'] == station_id), {})

    return {
        'city': city.get('name', city_id),
        'city_id': city_id,
        'station_id': station_id,
        'station_name': station_info.get('name', f'Station {station_id}'),
        'lat': station_info.get('lat'),
        'lon': station_info.get('lon'),
        'reading_timestamp': latest_ts or datetime.now(timezone.utc).isoformat(),
        'aqi': aqi,
        'aqi_category': aqi_cat,
        'dominant_pollutant': dominant,
        'data_type': 'REAL',
        'source': 'OpenAQ/CPCB',
        'provider': station_info.get('provider', 'CPCB'),
        'pollutants': pollutants_dict,
    }


def _normalize_param(measurement):
    """Extract parameter name from an OpenAQ v3 measurement object."""
    # v3 format varies: could be {parameter: {name: 'pm25'}} or {parameter: 'pm25'}
    param = measurement.get('parameter')
    if isinstance(param, dict):
        param = param.get('name', '')
    if isinstance(param, str):
        param = param.lower().replace('.', '').replace(' ', '')
        # Map common names
        mapping = {
            'pm25': 'pm25', 'pm2.5': 'pm25', 'pm2': 'pm25',
            'pm10': 'pm10',
            'no2': 'no2',
            'so2': 'so2',
            'co': 'co',
            'o3': 'o3', 'ozone': 'o3',
        }
        return mapping.get(param, param)
    return None


# ──────────────────────────────────────────────
# Historical data
# ──────────────────────────────────────────────

def get_historical_readings(city_id, station_id=None, days=7, pollutant='pm25'):
    """
    Get historical readings for charting.
    Returns list of {timestamp, value} dicts.
    """
    cache_params = {'city': city_id, 'station': station_id, 'days': days, 'pollutant': pollutant}
    cached = get_cached('history', cache_params, CACHE_TTL_READINGS)
    if cached is not None:
        return cached

    # Find a station
    if not station_id:
        stations = discover_stations_for_city(city_id)
        if stations:
            station_id = stations[0]['station_id']
        else:
            return []

    # Date range
    now = datetime.now(timezone.utc)
    date_from = (now - timedelta(days=days)).strftime('%Y-%m-%dT%H:%M:%SZ')
    date_to = now.strftime('%Y-%m-%dT%H:%M:%SZ')

    # Fetch measurements
    readings = []
    page = 1
    max_pages = 3

    while page <= max_pages:
        data = _get('/measurements', params={
            'locations_id': station_id,
            'parameter': POLLUTANTS.get(pollutant, {}).get('openaq_name', pollutant),
            'date_from': date_from,
            'date_to': date_to,
            'limit': 100,
            'page': page,
            'order_by': 'datetime',
            'sort': 'asc',
        })
        if not data or 'results' not in data:
            break

        results = data.get('results', [])
        for m in results:
            ts = m.get('date', {}).get('utc') or m.get('datetime', {}).get('utc', '')
            readings.append({
                'timestamp': ts,
                'value': m.get('value'),
            })

        if len(results) < 100:
            break
        page += 1

    set_cached('history', cache_params, readings)
    return readings


def get_summary_stats(city_id, days=7):
    """
    Compute min, max, avg for each pollutant over the given period.
    """
    cache_params = {'city': city_id, 'days': days, 'type': 'summary'}
    cached = get_cached('summary', cache_params, CACHE_TTL_READINGS)
    if cached is not None:
        return cached

    summary = {}
    for poll_key, poll_info in POLLUTANTS.items():
        readings = get_historical_readings(city_id, days=days, pollutant=poll_key)
        values = [r['value'] for r in readings if r.get('value') is not None]

        if values:
            summary[poll_key] = {
                'min': round(min(values), 1),
                'max': round(max(values), 1),
                'avg': round(sum(values) / len(values), 1),
                'count': len(values),
                'unit': poll_info['unit'],
            }
        else:
            summary[poll_key] = {
                'min': None, 'max': None, 'avg': None, 'count': 0,
                'unit': poll_info['unit'],
            }

    set_cached('summary', cache_params, summary)
    return summary
