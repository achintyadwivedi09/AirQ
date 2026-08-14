"""
Alert engine — checks readings against centralized thresholds.
"""
from datetime import datetime, timezone
from config import ALERT_THRESHOLDS, POLLUTANTS


def check_alerts(reading):
    """
    Check a reading against configured thresholds.
    Returns list of alert dicts. Empty list if nothing triggered.
    """
    if not reading:
        return []

    alerts = []
    now = datetime.now(timezone.utc).isoformat()
    city = reading.get('city', 'Unknown')
    city_id = reading.get('city_id', '')
    station = reading.get('station_name', 'Unknown')
    station_id = reading.get('station_id', '')
    data_type = reading.get('data_type', 'UNKNOWN')

    # Check AQI
    aqi = reading.get('aqi')
    if aqi is not None:
        aqi_thresh = ALERT_THRESHOLDS.get('aqi', {})
        if aqi >= aqi_thresh.get('severe', 999):
            alerts.append(_make_alert(city, city_id, station, station_id, 'aqi',
                                       aqi, aqi_thresh['severe'], 'SEVERE', now, data_type))
        elif aqi >= aqi_thresh.get('danger', 999):
            alerts.append(_make_alert(city, city_id, station, station_id, 'aqi',
                                       aqi, aqi_thresh['danger'], 'DANGER', now, data_type))
        elif aqi >= aqi_thresh.get('warning', 999):
            alerts.append(_make_alert(city, city_id, station, station_id, 'aqi',
                                       aqi, aqi_thresh['warning'], 'WARNING', now, data_type))

    # Check individual pollutants
    pollutants = reading.get('pollutants', {})
    for key, poll_data in pollutants.items():
        value = poll_data.get('value') if isinstance(poll_data, dict) else None
        if value is None:
            continue

        thresh = ALERT_THRESHOLDS.get(key, {})
        unit = thresh.get('unit', POLLUTANTS.get(key, {}).get('unit', ''))

        if value >= thresh.get('severe', float('inf')):
            alerts.append(_make_alert(city, city_id, station, station_id, key,
                                       value, thresh['severe'], 'SEVERE', now, data_type, unit))
        elif value >= thresh.get('danger', float('inf')):
            alerts.append(_make_alert(city, city_id, station, station_id, key,
                                       value, thresh['danger'], 'DANGER', now, data_type, unit))
        elif value >= thresh.get('warning', float('inf')):
            alerts.append(_make_alert(city, city_id, station, station_id, key,
                                       value, thresh['warning'], 'WARNING', now, data_type, unit))

    return alerts


def _make_alert(city, city_id, station, station_id, pollutant, value, threshold,
                severity, timestamp, data_type, unit=''):
    poll_name = POLLUTANTS.get(pollutant, {}).get('name', pollutant.upper())
    messages = {
        'SEVERE': f'{poll_name} is at SEVERE levels ({value}{unit}). Avoid outdoor activity.',
        'DANGER': f'{poll_name} is at DANGEROUS levels ({value}{unit}). Limit outdoor exposure.',
        'WARNING': f'{poll_name} has crossed WARNING threshold ({value}{unit}). Stay alert.',
    }
    return {
        'id': f"{city_id}-{pollutant}-{severity}",
        'city': city,
        'city_id': city_id,
        'station': station,
        'station_id': station_id,
        'pollutant': pollutant,
        'pollutant_name': poll_name,
        'value': value,
        'threshold': threshold,
        'unit': unit,
        'severity': severity,
        'message': messages.get(severity, ''),
        'timestamp': timestamp,
        'data_type': data_type,
        'status': 'ACTIVE',
    }


def get_alerts_for_city(city_id, readings):
    """
    Check all readings for a city and aggregate alerts.
    readings: list of reading dicts (from real or simulated sources)
    """
    all_alerts = []
    for r in readings:
        all_alerts.extend(check_alerts(r))
    return all_alerts
