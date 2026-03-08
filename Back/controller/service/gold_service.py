import requests
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

# Public Data Portal API Configuration
DATA_GO_KR_API_KEY = os.getenv("DATA_GO_KR_API_KEY")
# KRX Gold Market Info Service URL
# Service: GetGeneralProductInfoService / Operation: getGoldPriceInfo
BASE_URL = "http://apis.data.go.kr/1160100/service/GetGeneralProductInfoService/getGoldPriceInfo"

def get_domestic_gold_price():
    """
    Fetch current domestic gold price (KRW/g) from Public Data Portal.
    """
    if not DATA_GO_KR_API_KEY:
        print("DATA_GO_KR_API_KEY not found in env")
        return None

    try:
        # Request parameters
        # params = {
        #     "serviceKey": DATA_GO_KR_API_KEY, 
        #     "numOfRows": 90,
        #     "pageNo": 1,
        #     "resultType": "json"
        # }
        
        # Manually construct URL to avoid double encoding of serviceKey if it's already encoded
        url = f"{BASE_URL}?serviceKey={DATA_GO_KR_API_KEY}&numOfRows=90&pageNo=1&resultType=json"
        
        response = requests.get(url)
        
        if response.status_code != 200:
            print(f"Public Data Portal Error: {response.status_code} - {response.text}")
            return None

        data = response.json()
        
        # Check structure
        items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
        
        if not items:
            return None
            
        # Items are usually list of daily records.
        # We need to sort them by date (basDt).
        # item structure example: { "basDt": "20240131", "clpr": "86000", ... }
        
        # If it's a single dict (xml-to-json quirk sometimes), wrap in list
        if isinstance(items, dict):
            items = [items]
            
        # Sort by date ascending
        sorted_items = sorted(items, key=lambda x: x.get("basDt", ""))
        
        return sorted_items

    except Exception as e:
        print(f"Error fetching domestic gold data: {e}")
        return None

def get_international_gold_data():
    """
    Fetch International Gold Futures (GC=F) from yfinance.
    Returns 90 days history.
    """
    try:
        ticker = yf.Ticker("GC=F")
        # Fetch 3 months of data
        history = ticker.history(period="3mo") 
        
        if history.empty:
            return None
            
        return history
    except Exception as e:
        print(f"Error fetching international gold data: {e}")
        return None

async def get_gold_data():
    """
    Orchestrate fetching gold data and formatting for frontend.
    """
    # 1. Fetch Domestic Data (Public API) including history
    domestic_items = get_domestic_gold_price()
    
    # 2. Fetch International Data (yfinance) including history
    international_df = get_international_gold_data()
    
    # Prepare Result Structures
    dates = []
    domestic_prices = []
    international_prices = []
    
    current_domestic_price = 0
    change_rate = 0
    
    # Process Domestic Data
    if domestic_items:
        # Take the latest one for current info
        latest = domestic_items[-1]
        current_domestic_price = int(latest.get("clpr", 0)) # Closing Price
        
        # Calculate daily change
        # vsd = limit change? fltRt = fluctuation rate?
        # usually 'fltRt' is rate, 'vs' is value change.
        change_rate = float(latest.get("fltRt", 0))
        
        # History
        # We need to align X-axis. 
        # Ideally, we iterate 90 days.
        # For simplicity, let's just use what we have in "items" (which is business days).
        
        for item in domestic_items:
            # Date format: YYYYMMDD -> MM.DD
            dt_str = item.get("basDt", "")
            if len(dt_str) == 8:
                # Store full date object for filling logic
                dt_obj = datetime.strptime(dt_str, "%Y%m%d")
                fmt_date = dt_obj.strftime("%m.%d")
                
                prices_map = item.get("clpr", 0)
                
                dates.append(fmt_date)
                domestic_prices.append(int(prices_map))
        
        # Fill missing dates up to today (Forward Fill)
        if dates and domestic_items:
            last_date_str = domestic_items[-1].get("basDt", "")
            if len(last_date_str) == 8:
                last_date = datetime.strptime(last_date_str, "%Y%m%d")
                today = datetime.now()
                
                # If last data is older than today, fill the gap
                current_date = last_date + timedelta(days=1)
                last_price = domestic_prices[-1]
                
                while current_date <= today:
                    dates.append(current_date.strftime("%m.%d"))
                    domestic_prices.append(last_price)
                    current_date += timedelta(days=1)
                    print(f"[DEBUG] Filled gold data for {current_date}")

    # Process International Data (Align with domestic dates if possible, or just push array)
    # Since charts handle labels, we might just pass two arrays and let chart.js handle mapping 
    # if we provide timestamps. But our Chart.vue uses simple index-based labels.
    # We should align international data to the same dates if possible.
    
    # Simple alignment: just take last N values corresponding to domestic length?
    # Or just fetch last 90 values from yfinance and send them.
    if international_df is not None and not international_df.empty:
        # Get 'Close' prices
        # We should map these to the 'dates' derived above?
        # It's tricky because holidays differ.
        # For a simple dashboard, we can just send the arrays. 
        # But if lengths differ significantly, the chart looks weird.
        # Let's resample or just pick the last N values matching domestic count.
        
        count = len(domestic_prices)
        if count > 0:
            # Get last 'count' rows
            aligned_intl = international_df.tail(count)
            international_prices = [round(x, 2) for x in aligned_intl['Close'].tolist()]
            
            # If still shorter (e.g. yfinance has less data), pad?
            # Or if longer, trim.
            # handled by tail. 
            
            # If domestic data is missing (e.g. key error), but yfinance is alive?
            # We used domestic dates as master.
    
    if not dates and international_df is not None:
         # Fallback to yfinance dates if domestic failed
         intl_dates = international_df.index.strftime('%m.%d').tolist()
         dates = intl_dates
         international_prices = [round(x, 2) for x in international_df['Close'].tolist()]

    return {
        "currentPrice": current_domestic_price, # KRW
        "changeRate": change_rate, 
        "history": {
            "labels": dates,
            "domestic": domestic_prices,
            "international": international_prices
        }
    }


async def get_gold_data_from_db():
    """DB에 저장된 금 현재가 및 히스토리를 반환합니다."""
    from database import db

    async with db.pool.acquire() as conn:
        price_row = await conn.fetchrow(
            "SELECT domestic_price, change_rate FROM market_gold_price ORDER BY fetched_at DESC LIMIT 1"
        )
        history_rows = await conn.fetch(
            "SELECT trade_date, domestic_price, international_price FROM market_gold_history ORDER BY trade_date"
        )
    if not price_row:
        return None
    return {
        "currentPrice": int(price_row["domestic_price"]),
        "changeRate":   float(price_row["change_rate"]),
        "history": {
            "labels":        [r["trade_date"].strftime("%m.%d") for r in history_rows],
            "domestic":      [int(r["domestic_price"]) for r in history_rows],
            "international": [float(r["international_price"]) if r["international_price"] else None for r in history_rows]
        }
    }
