import urllib.request
import json
import urllib.error

data = json.dumps({
    "Driver": "VER",
    "LapNumber": 20,
    "TyreLife": 15
}).encode('utf-8')

req = urllib.request.Request(
    'http://localhost:8000/LapTimeSeconds/predict',
    data=data,
    headers={'Content-Type': 'application/json'}
)

try:
    with urllib.request.urlopen(req) as response:
        print(response.read().decode())
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code)
    print(e.read().decode())
except Exception as e:
    print("Error:", e)
