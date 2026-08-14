"""Test script for all API endpoints."""
import requests
import json

base = 'http://127.0.0.1:5000/api'

def test(label, url, expect_status=200):
    r = requests.get(url)
    status = 'PASS' if r.status_code == expect_status else 'FAIL'
    data = r.json()
    print(f"[{status}] {label}: HTTP {r.status_code}")
    return data

print("=" * 60)
print("  BACKEND API TESTS")
print("=" * 60)

# 1. Health
test("Health", f"{base}/health")

# 2. Cities
data = test("Cities", f"{base}/cities")
cities = data.get("cities", [])
print(f"       {len(cities)} cities returned")
for c in cities:
    name = c.get("name", "?")
    state = c.get("state", "?")
    print(f"       - {name} ({state})")

# 3. Sensors (IoT)
data = test("Sensors", f"{base}/sensors")
sensors = data.get("sensors", [])
print(f"       {len(sensors)} sensors, data_type={data.get('data_type')}")

# 4. IoT latest - Delhi
data = test("IoT Delhi", f"{base}/iot/latest?city=delhi")
rd = data.get("reading", {})
print(f"       data_type={rd.get('data_type')}, AQI={rd.get('aqi')}")

# 5. IoT latest - Prayagraj
data = test("IoT Prayagraj", f"{base}/iot/latest?city=prayagraj")
rd = data.get("reading", {})
print(f"       data_type={rd.get('data_type')}, station={rd.get('station_name')}")

# 6. Sensor detail
data = test("Sensor Detail", f"{base}/sensors/SIM-SENSOR-01")
print(f"       sensor_id={data.get('sensor', {}).get('sensor_id')}")

# 7. Sensor reading
data = test("Sensor Reading", f"{base}/sensors/SIM-SENSOR-01/reading")
rd = data.get("reading", {})
pm25 = rd.get("pollutants", {}).get("pm25", {}).get("value")
print(f"       PM2.5={pm25}, data_type={rd.get('data_type')}")

# 8. Alerts
data = test("Alerts", f"{base}/alerts")
print(f"       {len(data.get('alerts', []))} alerts")

# 9. Forecast ML
r_fc = requests.get(f"{base}/forecast?city=delhi&horizon=24")
data_fc = r_fc.json()
if r_fc.status_code == 200:
    print(f"[PASS] Forecast: HTTP 200, model={data_fc.get('model')}, forecast_points={len(data_fc.get('forecast', []))}")
elif r_fc.status_code == 400 and 'Insufficient' in data_fc.get('error', ''):
    print(f"[PASS] Forecast: HTTP 400 (Expected when no history available), error={data_fc.get('error')}")
else:
    print(f"[FAIL] Forecast: HTTP {r_fc.status_code}, error={data_fc.get('error')}")

# 10. Invalid city (expect 404)
data = test("Invalid City", f"{base}/readings/latest?city=invalidcity", expect_status=404)
print(f"       error={data.get('error')}")

# 11. Missing param (expect 400)
data = test("Missing Param", f"{base}/readings/latest", expect_status=400)
print(f"       error={data.get('error')}")

# 12. Readings for all cities
data = test("All Readings", f"{base}/readings")
readings = data.get("readings", [])
print(f"       {len(readings)} readings returned")
for r in readings:
    city = r.get("city", "?")
    aqi = r.get("aqi", "?")
    dt = r.get("data_type", "?")
    print(f"       - {city}: AQI={aqi} [{dt}]")

# 13. Summary for delhi
data = test("Summary Delhi", f"{base}/summary?city=delhi")
summary = data.get("summary", {})
print(f"       pollutants in summary: {list(summary.keys())}")
print(f"       trend: {data.get('trend')}, intelligence_len: {len(data.get('intelligence', ''))}")

print()
print("=" * 60)
print("  ALL API TESTS COMPLETE")
print("=" * 60)
