import os
import requests
from dotenv import load_dotenv

import datetime

load_dotenv()

API_KEY = os.getenv("TWELVE_DATA_API_KEY")
BASE_URL = "https://api.twelvedata.com/quote"

# Simple In-Memory Cache
# Structure: { "nasdaq": { "data": [...], "timestamp": datetime } }
_cache = {}
CACHE_DURATION_MINUTES = 5

# Predefined Top 5 Lists (Reduced due to API Rate Limit: 8/min)
# Note: Twelve Data uses "005930.KS" format for Korea.
KOSPI_SYMBOLS = [
    "005930.KS", # Samsung Electronics
    "000660.KS", # SK Hynix
    "373220.KS", # LG Energy Solution
    "207940.KS", # Samsung Biologics
    "005380.KS"  # Hyundai Motor
]

NASDAQ_SYMBOLS = [
    "AAPL", "NVDA", "MSFT", "AMZN", "GOOGL"
]

def get_stock_data(market: str):
    global _cache
    
    if market == "kospi":
        # Deferred as per user request (Twelve Data Pro needed for KOSPI)
        return {
            "market": "kospi", 
            "stocks": [], 
            "status": "deferred", 
            "message": "KOSPI data implementation deferred"
        }

    # Check Cache Validity
    now = datetime.datetime.now()
    if market in _cache:
        last_update = _cache[market]["timestamp"]
        # If cache is fresh (less than 5 minutes old), return it to save API credits
        if (now - last_update).total_seconds() < (CACHE_DURATION_MINUTES * 60):
            print(f"Returning cached data for {market}")
            return _cache[market]["data"]

    symbols_list = NASDAQ_SYMBOLS
    symbols_str = ",".join(symbols_list)
    
    params = {
        "symbol": symbols_str,
        "apikey": API_KEY,
        "format": "json"
    }
    
    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        # Check HTTP status
        response.raise_for_status()
        
        data = response.json()
        
        # Check API Error Code
        if "code" in data and data["code"] != 200:
            print(f"Twelve Data API Error: {data['message']}")
            # Fallback: Return cached data if available, even if stale
            if market in _cache:
                print("Returning stale cache due to API error")
                return _cache[market]["data"]
            return {"market": market, "stocks": [], "status": "error", "message": data["message"]}

        # If only 1 symbol is requested, response is a dict of that symbol's data directly
        # But here we request 5, so it should be { "SYM": {...}, ... }
        # However, be safe.
        
        result = []
        for i, symbol in enumerate(symbols_list):
            item = None
            if symbol in data:
                item = data[symbol]
            elif "symbol" in data and data["symbol"] == symbol: # Single item response case
                item = data
                
            if item:
                # Calculate change percent safely
                try:
                    change_pct = float(item.get("percent_change", 0))
                except:
                    change_pct = 0.0
                    
                result.append({
                    "rank": i + 1,
                    "symbol": symbol,
                    "name": item.get("name", symbol),
                    "price": float(item.get("close", 0)),
                    "change": change_pct,
                    "currency": item.get("currency", "USD")
                })
        
        final_data = {"market": market, "stocks": result, "status": "success"}
        
        # Update Cache
        _cache[market] = {
            "data": final_data,
            "timestamp": now
        }
        
        return final_data

    except Exception as e:
        print(f"Error fetching stocks from Twelve Data: {e}")
        # Fallback: Return cached data on exception
        if market in _cache:
            print("Returning stale cache due to Exception")
            return _cache[market]["data"]
        return {"market": market, "stocks": [], "status": "error"}
