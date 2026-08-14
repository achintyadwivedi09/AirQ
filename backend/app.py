"""
Smart Air Pollution Monitoring Portal — Flask Backend
Main application entry point with all REST API routes.
"""
import os
import sys
from datetime import datetime, timezone
from flask import Flask, jsonify, request, send_from_directory

from config import FLASK_HOST, FLASK_PORT, FLASK_DEBUG, CITIES, POLLUTANTS, ALERT_THRESHOLDS
from openaq_client import (
    discover_stations_for_city,
    get_latest_reading,
    get_historical_readings,
    get_summary_stats,
)
from iot_simulator import iot_manager
from fallback_loader import get_fallback_reading, get_fallback_history, has_fallback_data
from alerts import check_alerts, get_alerts_for_city
from aqi_calculator import get_aqi_category
from cache import clear_cache
from intelligence import generate_intelligence_summary, get_trend_direction

# Add parent directory to path for ml import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    from ml.forecaster import generate_forecast
except ImportError:
    generate_forecast = None

app = Flask(__name__, static_folder=None)

# CORS for local development (frontend served from file:// or different port)
@app.after_request
def add_cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response


def _now():
    return datetime.now(timezone.utc).isoformat()


def _success(data, data_type='REAL', cached=False, **extra):
    resp = {
        'status': 'ok',
        'data_type': data_type,
        'cached': cached,
        'timestamp': _now(),
    }
    resp.update(data)
    resp.update(extra)
    return jsonify(resp)


def _error(message, status_code=400):
    return jsonify({
        'status': 'error',
        'error': message,
        'timestamp': _now(),
    }), status_code


# ──────────────────────────────────────────────
# Serve frontend (static files)
# ──────────────────────────────────────────────
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))

@app.route('/')
def serve_index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:filepath>')
def serve_static(filepath):
    # Don't serve API routes as files
    if filepath.startswith('api/'):
        return _error('Not found', 404)
    full = os.path.join(FRONTEND_DIR, filepath)
    if os.path.isfile(full):
        return send_from_directory(FRONTEND_DIR, filepath)
    # SPA fallback: serve index.html for client-side routes
    return send_from_directory(FRONTEND_DIR, 'index.html')


# ══════════════════════════════════════════════
# API ROUTES
# ══════════════════════════════════════════════

# ── Cities ────────────────────────────────────

@app.route('/api/cities')
def api_cities():
    """List all supported cities."""
    cities = []
    for cid, c in CITIES.items():
        cities.append({
            'id': c['id'],
            'name': c['name'],
            'state': c['state'],
            'lat': c['lat'],
            'lon': c['lon'],
            'note': c.get('note'),
        })
    return _success({'cities': cities})


# ── Stations ──────────────────────────────────

@app.route('/api/stations')
def api_stations():
    """List monitoring stations for a city."""
    city_id = request.args.get('city', '').strip().lower()
    if not city_id:
        return _error('Missing required parameter: city')
    if city_id not in CITIES:
        return _error(f'Unknown city: {city_id}', 404)

    stations = discover_stations_for_city(city_id,
                                          force_refresh=request.args.get('refresh') == 'true')

    data_type = 'REAL' if stations else 'FALLBACK'
    msg = None if stations else 'No live stations found via OpenAQ. Data may be limited.'

    resp = {'city': city_id, 'stations': stations}
    if msg:
        resp['message'] = msg
    return _success(resp, data_type=data_type)


# ── Latest Readings ──────────────────────────

@app.route('/api/readings/latest')
def api_readings_latest():
    """Get latest pollution reading for a city/station."""
    city_id = request.args.get('city', '').strip().lower()
    station_id = request.args.get('station', '').strip() or None
    refresh = request.args.get('refresh') == 'true'

    if not city_id:
        return _error('Missing required parameter: city')
    if city_id not in CITIES:
        return _error(f'Unknown city: {city_id}', 404)

    reading = get_latest_reading(city_id, station_id=station_id, force_refresh=refresh)

    if not reading:
        # Try fallback
        reading = get_fallback_reading(city_id)
        if reading:
            return _success({'reading': reading}, data_type='FALLBACK')
        # Try simulated
        sim = iot_manager.generate_reading(city_id=city_id)
        if sim:
            return _success({'reading': sim}, data_type='SIMULATED')
        return _success({
            'reading': None,
            'message': f'No data currently available for {CITIES[city_id]["name"]}.',
        }, data_type='FALLBACK')

    return _success({'reading': reading}, data_type=reading.get('data_type', 'REAL'))


# ── All Readings (multi-city latest) ────────

@app.route('/api/readings')
def api_readings():
    """Get latest readings for all cities or filtered set."""
    city_filter = request.args.get('city', '').strip().lower()
    cities_to_fetch = [city_filter] if city_filter and city_filter in CITIES else list(CITIES.keys())

    readings = []
    for cid in cities_to_fetch:
        reading = get_latest_reading(cid)
        if not reading:
            reading = get_fallback_reading(cid)
        if not reading:
            reading = iot_manager.generate_reading(city_id=cid)
        if reading:
            readings.append(reading)

    return _success({'readings': readings, 'count': len(readings)})


# ── Historical Readings ─────────────────────

@app.route('/api/history')
def api_history():
    """Get historical readings for charting."""
    city_id = request.args.get('city', '').strip().lower()
    station_id = request.args.get('station', '').strip() or None
    pollutant = request.args.get('pollutant', 'pm25').strip().lower()
    days = request.args.get('days', '7').strip()

    if not city_id:
        return _error('Missing required parameter: city')
    if city_id not in CITIES:
        return _error(f'Unknown city: {city_id}', 404)
    if pollutant not in POLLUTANTS:
        return _error(f'Unknown pollutant: {pollutant}. Valid: {", ".join(POLLUTANTS.keys())}')

    try:
        days = int(days)
        days = min(max(days, 1), 30)  # Clamp 1-30
    except ValueError:
        return _error('Parameter "days" must be an integer')

    readings = get_historical_readings(city_id, station_id=station_id,
                                        days=days, pollutant=pollutant)

    data_type = 'REAL'
    if not readings:
        readings = get_fallback_history(city_id, pollutant=pollutant, days=days)
        data_type = 'FALLBACK' if readings else 'REAL'

    return _success({
        'city': city_id,
        'city_name': CITIES[city_id]['name'],
        'pollutant': pollutant,
        'pollutant_name': POLLUTANTS[pollutant]['name'],
        'unit': POLLUTANTS[pollutant]['unit'],
        'days': days,
        'readings': readings,
        'count': len(readings),
    }, data_type=data_type)


# ── Summary Stats ────────────────────────────

@app.route('/api/summary')
def api_summary():
    """Get summary statistics, trend, and intelligence for a city."""
    city_id = request.args.get('city', '').strip().lower()
    days = request.args.get('days', '7').strip()

    if not city_id:
        return _error('Missing required parameter: city')
    if city_id not in CITIES:
        return _error(f'Unknown city: {city_id}', 404)

    try:
        days = int(days)
        days = min(max(days, 1), 30)
    except ValueError:
        return _error('Parameter "days" must be an integer')

    summary = get_summary_stats(city_id, days=days)
    reading = get_latest_reading(city_id) or get_fallback_reading(city_id) or iot_manager.generate_reading(city_id=city_id)
    history = get_historical_readings(city_id, days=1, pollutant='pm25') # for trend
    
    # Active alerts
    alerts = check_alerts(reading) if reading else []

    intel = generate_intelligence_summary(reading, history, alerts)
    trend = get_trend_direction(history)

    return _success({
        'city': city_id,
        'city_name': CITIES[city_id]['name'],
        'period_days': days,
        'summary': summary,
        'intelligence': intel,
        'trend': trend
    })


# ── IoT Sensors ──────────────────────────────

@app.route('/api/sensors')
def api_sensors():
    """List all IoT simulated sensors."""
    city_id = request.args.get('city', '').strip().lower() or None
    if city_id:
        if city_id not in CITIES:
            return _error(f'Unknown city: {city_id}', 404)
        sensors = iot_manager.get_sensors_for_city(city_id)
    else:
        sensors = iot_manager.get_all_sensors()

    return _success({'sensors': sensors, 'count': len(sensors)}, data_type='SIMULATED')


@app.route('/api/sensors/<sensor_id>')
def api_sensor_detail(sensor_id):
    """Get info for a specific sensor."""
    info = iot_manager.get_sensor(sensor_id)
    if not info:
        return _error(f'Sensor not found: {sensor_id}', 404)
    return _success({'sensor': info}, data_type='SIMULATED')


@app.route('/api/sensors/<sensor_id>/reading')
def api_sensor_reading(sensor_id):
    """Generate and return a fresh reading from a simulated sensor."""
    reading = iot_manager.generate_reading(sensor_id=sensor_id)
    if not reading:
        return _error(f'Sensor not found: {sensor_id}', 404)
    return _success({'reading': reading}, data_type='SIMULATED')


@app.route('/api/iot/latest')
def api_iot_latest():
    """Get latest IoT reading for a city."""
    city_id = request.args.get('city', '').strip().lower()
    if not city_id:
        # Generate for all
        readings = iot_manager.generate_all_readings()
        return _success({'readings': readings, 'count': len(readings)}, data_type='SIMULATED')

    if city_id not in CITIES:
        return _error(f'Unknown city: {city_id}', 404)

    reading = iot_manager.generate_reading(city_id=city_id)
    if not reading:
        return _error(f'No simulator for city: {city_id}', 404)
    return _success({'reading': reading}, data_type='SIMULATED')


# ── Alerts ───────────────────────────────────

@app.route('/api/alerts')
def api_alerts():
    """Get active alerts for a city or all cities."""
    city_id = request.args.get('city', '').strip().lower() or None
    cities_to_check = [city_id] if city_id and city_id in CITIES else list(CITIES.keys())

    all_alerts = []
    for cid in cities_to_check:
        # Check real data
        reading = get_latest_reading(cid)
        if reading:
            all_alerts.extend(check_alerts(reading))

        # Check simulated data
        sim = iot_manager.get_latest_reading(city_id=cid)
        if sim:
            all_alerts.extend(check_alerts(sim))

    # Deduplicate alerts based on ID (which does not include timestamp)
    unique_alerts = {}
    for a in all_alerts:
        unique_alerts[a['id']] = a
    all_alerts = list(unique_alerts.values())

    # Sort by severity
    severity_order = {'SEVERE': 0, 'DANGER': 1, 'WARNING': 2}
    all_alerts.sort(key=lambda a: severity_order.get(a.get('severity', ''), 99))

    return _success({
        'alerts': all_alerts,
        'count': len(all_alerts),
        'thresholds': ALERT_THRESHOLDS,
    })


# ── Forecast (placeholder) ──────────────────

@app.route('/api/forecast')
def api_forecast():
    """Forecast endpoint — ML implementation."""
    city_id = request.args.get('city', '').strip().lower()
    pollutant = request.args.get('pollutant', 'pm25').strip().lower()
    horizon = int(request.args.get('horizon', 24))

    if not city_id:
        return _error('Missing required parameter: city')
    if city_id not in CITIES:
        return _error(f'Unknown city: {city_id}', 404)
    if pollutant not in POLLUTANTS:
        return _error(f'Unknown pollutant: {pollutant}')

    if generate_forecast is None:
        return _error('Forecasting module is not available.', 500)

    # Fetch last 14 days of data to have enough for lags and rolling windows
    historical = get_historical_readings(city_id, days=14, pollutant=pollutant)
    
    # Try fallback if no live data
    data_type = 'PREDICTED'
    if not historical:
        historical = get_fallback_history(city_id, pollutant=pollutant, days=14)
        data_type = 'FALLBACK_PREDICTED'

    result = generate_forecast(historical, horizon_hours=horizon)
    
    if result.get('status') == 'error':
        return _error(result.get('message', 'Forecasting failed.'))

    return _success({
        'city': city_id,
        'city_name': CITIES[city_id]['name'],
        'pollutant': pollutant,
        'pollutant_name': POLLUTANTS[pollutant]['name'],
        'unit': POLLUTANTS[pollutant]['unit'],
        'horizon_hours': horizon,
        'message': result.get('message'),
        'forecast': result.get('forecast'),
        'metrics': result.get('metrics'),
        'model': result.get('model'),
        'confidence_interval': result.get('confidence_interval')
    }, data_type=data_type)


# ── Utility ──────────────────────────────────

@app.route('/api/health')
def api_health():
    return _success({'message': 'Backend is running'})


@app.route('/api/cache/clear')
def api_clear_cache():
    """Dev utility: clear the cache."""
    clear_cache()
    return _success({'message': 'Cache cleared'})


# ══════════════════════════════════════════════
# Entry point
# ══════════════════════════════════════════════

if __name__ == '__main__':
    print("=" * 60)
    print("  Smart Air Pollution Monitoring Portal — Backend")
    print(f"  Running on http://{FLASK_HOST}:{FLASK_PORT}")
    print("=" * 60)
    # Generate initial IoT readings
    iot_manager.generate_all_readings()
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
