"""
IoT Sensor Simulator — demonstrates IoT concepts without physical hardware.
Every reading is explicitly marked data_type = "SIMULATED".
"""
import random
import time
from datetime import datetime, timezone

from config import CITIES, POLLUTANTS, IOT_SIMULATOR_BASELINES, IOT_INTERVAL
from aqi_calculator import calculate_aqi, get_aqi_category


class SimulatedSensor:
    """A virtual IoT pollution sensor assigned to one city."""

    def __init__(self, sensor_id, city_id, station_name=None):
        self.sensor_id = sensor_id
        self.city_id = city_id
        city = CITIES.get(city_id, {})
        self.city_name = city.get('name', city_id)
        self.station_name = station_name or f"Virtual Sensor — {self.city_name} [SIMULATED]"
        self.lat = city.get('lat', 0) + random.uniform(-0.01, 0.01)
        self.lon = city.get('lon', 0) + random.uniform(-0.01, 0.01)
        self.status = 'online'
        self.last_reading = None
        self.last_seen = datetime.now(timezone.utc).isoformat()
        self._baselines = IOT_SIMULATOR_BASELINES.get(city_id, IOT_SIMULATOR_BASELINES.get('delhi'))

    def generate_reading(self):
        """Generate one realistic simulated reading. All values stay within plausible ranges."""
        now = datetime.now(timezone.utc)

        # Time-of-day variation: pollution tends to be higher in morning and evening
        hour = (now.hour + 5) % 24  # IST approximation
        if 7 <= hour <= 10 or 17 <= hour <= 21:
            multiplier = random.uniform(1.1, 1.4)  # Rush hours
        elif 1 <= hour <= 5:
            multiplier = random.uniform(0.6, 0.8)  # Night
        else:
            multiplier = random.uniform(0.85, 1.15)

        pollutant_values = {}
        pollutants_dict = {}

        for key in ['pm25', 'pm10', 'no2', 'so2', 'co', 'o3']:
            lo, hi = self._baselines.get(key, (10, 100))
            base = random.uniform(lo, hi)
            value = round(base * multiplier, 1)
            # Clamp to physically plausible ranges
            value = max(0, value)
            pollutant_values[key] = value
            pollutants_dict[key] = {
                'value': value,
                'unit': POLLUTANTS[key]['unit'],
            }

        # Randomly set 1-2 pollutants to null to simulate sensor gaps
        if random.random() < 0.3:
            null_key = random.choice(['so2', 'o3', 'co'])
            pollutant_values[null_key] = None
            pollutants_dict[null_key] = {'value': None, 'unit': POLLUTANTS[null_key]['unit']}

        aqi, aqi_cat, dominant = calculate_aqi(pollutant_values)

        self.last_seen = now.isoformat()
        self.last_reading = {
            'city': self.city_name,
            'city_id': self.city_id,
            'station_id': self.sensor_id,
            'station_name': self.station_name,
            'lat': self.lat,
            'lon': self.lon,
            'reading_timestamp': now.isoformat(),
            'aqi': aqi,
            'aqi_category': aqi_cat,
            'dominant_pollutant': dominant,
            'data_type': 'SIMULATED',
            'source': 'IoT Simulator',
            'provider': 'Simulated',
            'pollutants': pollutants_dict,
        }
        return self.last_reading

    def get_info(self):
        """Return sensor metadata."""
        return {
            'sensor_id': self.sensor_id,
            'city': self.city_name,
            'city_id': self.city_id,
            'station_name': self.station_name,
            'lat': self.lat,
            'lon': self.lon,
            'status': self.status,
            'last_seen': self.last_seen,
            'data_type': 'SIMULATED',
            'interval_seconds': IOT_INTERVAL,
        }

    def set_status(self, status):
        self.status = status
        self.last_seen = datetime.now(timezone.utc).isoformat()


class IoTSimulatorManager:
    """Manages a fleet of simulated sensors across cities."""

    def __init__(self):
        self.sensors = {}
        self._init_sensors()

    def _init_sensors(self):
        """Create one simulated sensor per city."""
        for i, city_id in enumerate(CITIES.keys(), start=1):
            sensor_id = f"SIM-SENSOR-{i:02d}"
            self.sensors[sensor_id] = SimulatedSensor(
                sensor_id=sensor_id,
                city_id=city_id,
            )

    def get_all_sensors(self):
        """Return info for all sensors."""
        return [s.get_info() for s in self.sensors.values()]

    def get_sensor(self, sensor_id):
        """Return info for one sensor."""
        s = self.sensors.get(sensor_id)
        return s.get_info() if s else None

    def get_sensors_for_city(self, city_id):
        """Return sensors assigned to a city."""
        return [s.get_info() for s in self.sensors.values() if s.city_id == city_id]

    def generate_reading(self, sensor_id=None, city_id=None):
        """
        Generate a reading. Specify sensor_id or city_id.
        Returns the reading dict or None.
        """
        if sensor_id:
            s = self.sensors.get(sensor_id)
            if s:
                return s.generate_reading()
        elif city_id:
            for s in self.sensors.values():
                if s.city_id == city_id:
                    return s.generate_reading()
        return None

    def generate_all_readings(self):
        """Generate fresh readings for all sensors."""
        return [s.generate_reading() for s in self.sensors.values()]

    def get_latest_reading(self, sensor_id=None, city_id=None):
        """Get the most recent reading (generates one if none exists)."""
        if sensor_id:
            s = self.sensors.get(sensor_id)
            if s:
                if not s.last_reading:
                    s.generate_reading()
                return s.last_reading
        elif city_id:
            for s in self.sensors.values():
                if s.city_id == city_id:
                    if not s.last_reading:
                        s.generate_reading()
                    return s.last_reading
        return None


# Global singleton
iot_manager = IoTSimulatorManager()
