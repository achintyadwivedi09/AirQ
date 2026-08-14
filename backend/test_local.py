import requests

try:
    r = requests.get('http://127.0.0.1:5000/api/history?city=prayagraj&pollutant=pm25&days=7', timeout=30)
    print("Status:", r.status_code)
    data = r.json()
    print("Data type:", data.get('data_type'))
    readings = data.get('readings', [])
    print(f"Got {len(readings)} readings")
    if readings:
        print("First reading:", readings[0])
except Exception as e:
    print("Error:", e)
