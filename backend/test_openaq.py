import os
from dotenv import load_dotenv
import requests
import json

load_dotenv('.env')
key = os.getenv('OPENAQ_API_KEY')
url = 'https://api.openaq.org/v3/locations'
params = {'bbox': '76.709,28.1139,77.709,29.1139', 'limit': 1}
headers = {'X-API-Key': key, 'Accept': 'application/json'}
r = requests.get(url, headers=headers, params=params)

loc = r.json()['results'][0]
print(json.dumps(loc.get('sensors', []), indent=2))
