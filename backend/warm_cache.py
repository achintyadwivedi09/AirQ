import os
import sys
import time

# Add backend directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import CITIES, POLLUTANTS
from openaq_client import discover_stations_for_city, get_latest_reading, get_historical_readings, get_summary_stats

def warm_cache():
    print("======================================================")
    print(" WARMING UP CACHE FOR INSTANT LOADING")
    print("======================================================")
    
    total_cities = len(CITIES)
    for i, city_id in enumerate(CITIES.keys(), 1):
        print(f"\n[{i}/{total_cities}] Processing {city_id}...")
        
        print("  - Discovering stations...")
        discover_stations_for_city(city_id, force_refresh=True)
        
        print("  - Fetching latest reading...")
        get_latest_reading(city_id, force_refresh=True)
        
        print("  - Fetching summary stats (7 days)...")
        get_summary_stats(city_id, days=7, force_refresh=True)
        
        print("  - Fetching historical readings for all pollutants...")
        for poll_id in POLLUTANTS.keys():
            get_historical_readings(city_id, days=7, pollutant=poll_id, force_refresh=True)
            time.sleep(0.5)  # Slight delay to avoid hammering the OpenAQ API
            
        print(f"  [OK] {city_id} cached successfully!")
        
    print("\n======================================================")
    print(" CACHE WARMUP COMPLETE! App will now load instantly.")
    print("======================================================")

if __name__ == '__main__':
    warm_cache()
