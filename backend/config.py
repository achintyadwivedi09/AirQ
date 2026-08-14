"""
Configuration for the Smart Air Pollution Monitoring Portal backend.
All configurable values are centralised here.
"""
import os
from dotenv import load_dotenv

# Load .env from the backend directory
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# ──────────────────────────────────────────────
# OpenAQ API v3 settings
# ──────────────────────────────────────────────
OPENAQ_API_KEY = os.getenv('OPENAQ_API_KEY', '')
OPENAQ_BASE_URL = 'https://api.openaq.org/v3'
OPENAQ_TIMEOUT = 10  # seconds

# ──────────────────────────────────────────────
# Flask server
# ──────────────────────────────────────────────
FLASK_HOST = os.getenv('FLASK_HOST', '127.0.0.1')
FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'true').lower() == 'true'

# ──────────────────────────────────────────────
# Cache
# ──────────────────────────────────────────────
CACHE_DIR = os.path.abspath(
    os.getenv('CACHE_DIR', os.path.join(os.path.dirname(__file__), '..', 'data', 'cache'))
)
CACHE_TTL_READINGS = int(os.getenv('CACHE_TTL_READINGS', 1800))     # 30 min
CACHE_TTL_STATIONS = int(os.getenv('CACHE_TTL_STATIONS', 86400))    # 24 hours

# ──────────────────────────────────────────────
# Supported Indian Cities
# ──────────────────────────────────────────────
CITIES = {
    'delhi': {
        'id': 'delhi', 'name': 'Delhi', 'state': 'Delhi',
        'lat': 28.6139, 'lon': 77.2090,
        'search_terms': ['Delhi', 'New Delhi'],
    },
    'mumbai': {
        'id': 'mumbai', 'name': 'Mumbai', 'state': 'Maharashtra',
        'lat': 19.0760, 'lon': 72.8777,
        'search_terms': ['Mumbai', 'Bombay'],
    },
    'chennai': {
        'id': 'chennai', 'name': 'Chennai', 'state': 'Tamil Nadu',
        'lat': 13.0827, 'lon': 80.2707,
        'search_terms': ['Chennai', 'Madras'],
    },
    'bengaluru': {
        'id': 'bengaluru', 'name': 'Bengaluru', 'state': 'Karnataka',
        'lat': 12.9716, 'lon': 77.5946,
        'search_terms': ['Bengaluru', 'Bangalore'],
    },
    'kolkata': {
        'id': 'kolkata', 'name': 'Kolkata', 'state': 'West Bengal',
        'lat': 22.5726, 'lon': 88.3639,
        'search_terms': ['Kolkata', 'Calcutta'],
    },
    'hyderabad': {
        'id': 'hyderabad', 'name': 'Hyderabad', 'state': 'Telangana',
        'lat': 17.3850, 'lon': 78.4867,
        'search_terms': ['Hyderabad'],
    },
    'pune': {
        'id': 'pune', 'name': 'Pune', 'state': 'Maharashtra',
        'lat': 18.5204, 'lon': 73.8567,
        'search_terms': ['Pune', 'Poona'],
    },
    'ahmedabad': {
        'id': 'ahmedabad', 'name': 'Ahmedabad', 'state': 'Gujarat',
        'lat': 23.0225, 'lon': 72.5714,
        'search_terms': ['Ahmedabad'],
    },
    'lucknow': {
        'id': 'lucknow', 'name': 'Lucknow', 'state': 'Uttar Pradesh',
        'lat': 26.8467, 'lon': 80.9462,
        'search_terms': ['Lucknow'],
    },
    'prayagraj': {
        'id': 'prayagraj', 'name': 'Prayagraj', 'state': 'Uttar Pradesh',
        'lat': 25.4358, 'lon': 81.8464,
        'search_terms': ['Prayagraj', 'Allahabad'],
        'note': 'Station availability subject to OpenAQ coverage',
    },
}

# ──────────────────────────────────────────────
# Pollutant definitions
# ──────────────────────────────────────────────
POLLUTANTS = {
    'pm25':  {'name': 'PM2.5',  'unit': 'µg/m³', 'openaq_name': 'pm25'},
    'pm10':  {'name': 'PM10',   'unit': 'µg/m³', 'openaq_name': 'pm10'},
    'no2':   {'name': 'NO₂',    'unit': 'µg/m³', 'openaq_name': 'no2'},
    'so2':   {'name': 'SO₂',    'unit': 'µg/m³', 'openaq_name': 'so2'},
    'co':    {'name': 'CO',     'unit': 'mg/m³',  'openaq_name': 'co'},
    'o3':    {'name': 'O₃',     'unit': 'µg/m³', 'openaq_name': 'o3'},
}

# ──────────────────────────────────────────────
# AQI breakpoints – India NAAQs
# ──────────────────────────────────────────────
AQI_CATEGORIES = [
    (0,   50,  'Good',                         '#009966'),
    (51,  100, 'Satisfactory',                 '#58a84b'),
    (101, 200, 'Moderate',                     '#ffde33'),
    (201, 300, 'Poor',                         '#ff9933'),
    (301, 400, 'Very Poor',                    '#cc0033'),
    (401, 500, 'Severe',                       '#7e0023'),
]

# PM2.5 24-hr breakpoints (India NAAQs) for sub-index calc
AQI_BREAKPOINTS = {
    'pm25': [
        (0, 30, 0, 50),
        (31, 60, 51, 100),
        (61, 90, 101, 200),
        (91, 120, 201, 300),
        (121, 250, 301, 400),
        (251, 500, 401, 500),
    ],
    'pm10': [
        (0, 50, 0, 50),
        (51, 100, 51, 100),
        (101, 250, 101, 200),
        (251, 350, 201, 300),
        (351, 430, 301, 400),
        (431, 600, 401, 500),
    ],
    'no2': [
        (0, 40, 0, 50),
        (41, 80, 51, 100),
        (81, 180, 101, 200),
        (181, 280, 201, 300),
        (281, 400, 301, 400),
        (401, 600, 401, 500),
    ],
    'so2': [
        (0, 40, 0, 50),
        (41, 80, 51, 100),
        (81, 380, 101, 200),
        (381, 800, 201, 300),
        (801, 1600, 301, 400),
        (1601, 2400, 401, 500),
    ],
    'co': [
        (0, 1.0, 0, 50),
        (1.1, 2.0, 51, 100),
        (2.1, 10.0, 101, 200),
        (10.1, 17.0, 201, 300),
        (17.1, 34.0, 301, 400),
        (34.1, 50.0, 401, 500),
    ],
    'o3': [
        (0, 50, 0, 50),
        (51, 100, 51, 100),
        (101, 168, 101, 200),
        (169, 208, 201, 300),
        (209, 748, 301, 400),
        (749, 1000, 401, 500),
    ],
}

# ──────────────────────────────────────────────
# Alert thresholds
# ──────────────────────────────────────────────
ALERT_THRESHOLDS = {
    'pm25':  {'warning': 60,  'danger': 120, 'severe': 250,  'unit': 'µg/m³'},
    'pm10':  {'warning': 100, 'danger': 250, 'severe': 430,  'unit': 'µg/m³'},
    'no2':   {'warning': 80,  'danger': 180, 'severe': 280,  'unit': 'µg/m³'},
    'so2':   {'warning': 80,  'danger': 380, 'severe': 800,  'unit': 'µg/m³'},
    'co':    {'warning': 2.0, 'danger': 10.0, 'severe': 17.0, 'unit': 'mg/m³'},
    'o3':    {'warning': 100, 'danger': 168, 'severe': 208,  'unit': 'µg/m³'},
    'aqi':   {'warning': 101, 'danger': 201, 'severe': 301,  'unit': ''},
}

# ──────────────────────────────────────────────
# IoT Simulator baseline ranges (realistic)
# ──────────────────────────────────────────────
IOT_SIMULATOR_BASELINES = {
    'delhi':      {'pm25': (45, 180), 'pm10': (80, 300),  'no2': (20, 80), 'so2': (5, 30), 'co': (0.5, 3.0), 'o3': (10, 60)},
    'mumbai':     {'pm25': (25, 90),  'pm10': (50, 150),  'no2': (15, 55), 'so2': (5, 20), 'co': (0.3, 2.0), 'o3': (15, 50)},
    'chennai':    {'pm25': (20, 70),  'pm10': (40, 120),  'no2': (10, 45), 'so2': (3, 15), 'co': (0.2, 1.5), 'o3': (10, 45)},
    'bengaluru':  {'pm25': (20, 65),  'pm10': (35, 110),  'no2': (10, 40), 'so2': (3, 12), 'co': (0.2, 1.2), 'o3': (12, 50)},
    'kolkata':    {'pm25': (30, 120), 'pm10': (55, 200),  'no2': (15, 60), 'so2': (5, 25), 'co': (0.3, 2.5), 'o3': (10, 45)},
    'hyderabad':  {'pm25': (22, 75),  'pm10': (40, 130),  'no2': (12, 50), 'so2': (4, 18), 'co': (0.2, 1.8), 'o3': (12, 55)},
    'pune':       {'pm25': (20, 70),  'pm10': (38, 120),  'no2': (10, 42), 'so2': (3, 14), 'co': (0.2, 1.3), 'o3': (15, 50)},
    'ahmedabad':  {'pm25': (28, 95),  'pm10': (50, 160),  'no2': (14, 55), 'so2': (5, 22), 'co': (0.3, 2.0), 'o3': (12, 48)},
    'lucknow':    {'pm25': (35, 140), 'pm10': (60, 250),  'no2': (18, 65), 'so2': (5, 28), 'co': (0.4, 2.8), 'o3': (10, 50)},
    'prayagraj':  {'pm25': (30, 130), 'pm10': (55, 220),  'no2': (15, 60), 'so2': (4, 25), 'co': (0.3, 2.5), 'o3': (10, 48)},
}

# IoT simulator interval in seconds
IOT_INTERVAL = int(os.getenv('IOT_INTERVAL', 60))
