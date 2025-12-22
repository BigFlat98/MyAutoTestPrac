import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()

API_KEY = os.getenv("TWELVE_DATA_API_KEY")
BASE_URL = "https://api.twelvedata.com/quote"

# Try variations
variations = ["005930", "005930:KRX", "005930:KS"] 

for sym in variations:
    params = {
        "symbol": sym,
        "apikey": API_KEY,
        "format": "json"
    }
    print(f"-- Requesting: {sym} --")
    try:
        res = requests.get(BASE_URL, params=params, timeout=5)
        data = res.json()
        if "code" in data and data["code"] != 200:
            print(f"FAILED: {data['message']}")
        else:
            print(f"SUCCESS: Name={data.get('name')}, Price={data.get('close')}")
    except Exception as e:
        print(f"Error: {e}")
