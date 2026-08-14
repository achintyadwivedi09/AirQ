import os
import csv
import json
import requests
from datetime import datetime
from config import CITIES, POLLUTANTS

# Open-Meteo variables
VAR_MAP = {
    'pm10': 'pm10',
    'pm2_5': 'pm25',
    'carbon_monoxide': 'co',
    'nitrogen_dioxide': 'no2',
    'sulphur_dioxide': 'so2',
    'ozone': 'o3'
}

FALLBACK_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'fallback'))

def fetch_and_save():
    os.makedirs(FALLBACK_DIR, exist_ok=True)
    
    for city_id, city_info in CITIES.items():
        print(f"Fetching fallback data for {city_id}...")
        lat = city_info['lat']
        lon = city_info['lon']
        
        url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&hourly=pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone&past_days=14"
        
        try:
            r = requests.get(url)
            r.raise_for_status()
            data = r.json()
            
            hourly = data.get('hourly', {})
            times = hourly.get('time', [])
            
            csv_path = os.path.join(FALLBACK_DIR, f"{city_id}.csv")
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                headers = ['timestamp', 'pm10', 'pm25', 'co', 'no2', 'so2', 'o3']
                writer.writerow(headers)
                
                for i, t in enumerate(times):
                    # convert '2024-01-01T00:00' to ISO with Z
                    dt = t + ':00Z'
                    row = [dt]
                    
                    # map values
                    for om_var, our_var in VAR_MAP.items():
                        val = hourly.get(om_var, [])[i] if hourly.get(om_var) else None
                        row.append(val if val is not None else '')
                        
                    writer.writerow(row)
            print(f"Saved {len(times)} records for {city_id}.")
        except Exception as e:
            print(f"Error for {city_id}: {e}")

if __name__ == '__main__':
    fetch_and_save()
