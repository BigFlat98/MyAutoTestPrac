import ccxt
import requests
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import asyncio

# Initialize Exchanges (Public APIs, no keys needed for fetching tickers)
upbit = ccxt.upbit()
binance = ccxt.binance()

# Coin Symbol Mapper
# Upbit uses KRW-BTC, Binance uses BTC/USDT
SYMBOL_MAP = {
    "BTC": {"upbit": "KRW-BTC", "binance": "BTC/USDT"},
    "ETH": {"upbit": "KRW-ETH", "binance": "ETH/USDT"},
    "XRP": {"upbit": "KRW-XRP", "binance": "XRP/USDT"},
}

def get_exchange_rate():
    """
    Fetch current USD/KRW exchange rate using yfinance.
    Returns default 1400 if failed (fallback).
    """
    try:
        # yfinance ticker for USD/KRW is 'KRW=X'
        ticker = yf.Ticker("KRW=X")
        # Get the closing price of the last available data
        history = ticker.history(period="1d")
        if not history.empty:
            return history['Close'].iloc[-1]
        return 1400.0
    except Exception as e:
        print(f"Error fetching exchange rate: {e}")
        return 1400.0

async def get_crypto_data(coin_code: str):
    """
    Fetch crypto data for the given coin code (BTC, ETH, XRP).
    Returns a dictionary with current prices, changes, premium, and history.
    """
    if coin_code not in SYMBOL_MAP:
        return None

    symbols = SYMBOL_MAP[coin_code]
    
    # 1. Fetch Current Ticker (Upbit & Binance)
    # Using run_in_executor or direct synchronous calls (ccxt is sync by default unless using ccxt.async_support)
    # For simplicity in FastAPI, we can use sync calls directly if response time is acceptable, 
    # but strictly we should make them async. For now, we'll keep it simple.
    
    # try/except removed to allow propagation
    print(f"[DEBUG] Fetching tickers for {symbols}")
    upbit_ticker = upbit.fetch_ticker(symbols['upbit'])
    print(f"[DEBUG] Upbit Ticker: {upbit_ticker}")
    binance_ticker = binance.fetch_ticker(symbols['binance'])
    print(f"[DEBUG] Binance Ticker: {binance_ticker}")
    
    # Fallback for Upbit if ccxt fails (returns None)
    if upbit_ticker is None:
        print("[WARNING] Upbit ticker via ccxt is None. Attempting fallback via requests.")
        try:
            url = f"https://api.upbit.com/v1/ticker?markets={symbols['upbit']}"
            resp = requests.get(url)
            if resp.status_code == 200:
                data = resp.json()
                # API returns a list, e.g. [{"market": "KRW-BTC", "trade_price": 1000, ...}]
                if data and len(data) > 0:
                    # Construct a minimal ticker object compatible with our usage
                    upbit_ticker = {
                        'last': data[0]['trade_price'],
                        'percentage': data[0].get('signed_change_rate', 0) * 100 # Upbit returns e.g. 0.01 for 1%
                    }
                    print(f"[DEBUG] Upbit Fallback Ticker: {upbit_ticker}")
        except Exception as e:
            print(f"[ERROR] Upbit fallback failed: {e}")

    if upbit_ticker is None:
        print("[ERROR] Upbit ticker is None (Fallback also failed)")
        # Handle specifically or raise
        raise Exception("Upbit ticker returned None")
        
    if binance_ticker is None:
        print("[ERROR] Binance ticker is None")
        raise Exception("Binance ticker returned None")

    upbit_price = upbit_ticker['last']
    binance_price_usd = binance_ticker['last']
    
    # 2. Get Exchange Rate
    exchange_rate = get_exchange_rate()
    print(f"[DEBUG] Exchange Rate: {exchange_rate}")
    
    if exchange_rate is None:
         print("[DEBUG] Failed to get exchange rate, using fallback 1400")
         exchange_rate = 1400.0

    # 3. Calculate Binace Price in KRW
    # ... rest of logic
    binance_price_krw = binance_price_usd * exchange_rate
    
    # 4. Calculate Kimchi Premium
    kimchi_premium = ((upbit_price - binance_price_krw) / binance_price_krw) * 100
    
    # 5. Fetch History
    ohlcv_upbit = upbit.fetch_ohlcv(symbols['upbit'], '1d', limit=90)
    ohlcv_binance = binance.fetch_ohlcv(symbols['binance'], '1d', limit=90)
    
    dates = []
    upbit_history = []
    binance_history = []
    
    length = min(len(ohlcv_upbit), len(ohlcv_binance))
    
    for i in range(length):
        ts = ohlcv_upbit[i][0]
        date_str = datetime.fromtimestamp(ts/1000).strftime('%m.%d')
        
        upbit_close = ohlcv_upbit[i][4]
        binance_close_usd = ohlcv_binance[i][4]
        binance_close_krw = binance_close_usd * exchange_rate
        
        dates.append(date_str)
        upbit_history.append(upbit_close)
        binance_history.append(int(binance_close_krw))
        
    return {
        "coin": coin_code,
        "krwPrice": int(upbit_price),
        "usdPrice": binance_price_usd,
        "changeRate": round(upbit_ticker['percentage'], 2) if upbit_ticker.get('percentage') else 0,
        "kimchiPremium": round(kimchi_premium, 2),
        "exchangeRate": round(exchange_rate, 2),
        "history": {
            "labels": dates,
            "upbit": upbit_history,
            "binance": binance_history
        }
    }


async def get_crypto_data_from_db(coin_code: str):
    """DB에 저장된 암호화폐 현재가 및 히스토리를 반환합니다."""
    from database import db

    coin = coin_code.upper()
    if coin not in SYMBOL_MAP:
        return None

    async with db.pool.acquire() as conn:
        price_row = await conn.fetchrow(
            """SELECT krw_price, usd_price, change_rate, kimchi_premium, exchange_rate
               FROM market_crypto_price
               WHERE coin = $1
               ORDER BY fetched_at DESC LIMIT 1""",
            coin
        )
        history_rows = await conn.fetch(
            """SELECT trade_datetime, upbit_price, binance_price
               FROM market_crypto_history
               WHERE coin = $1
               ORDER BY trade_datetime""",
            coin
        )
    if not price_row:
        return None
    return {
        "coin":          coin,
        "krwPrice":      int(price_row["krw_price"]),
        "usdPrice":      float(price_row["usd_price"]),
        "changeRate":    float(price_row["change_rate"]),
        "kimchiPremium": float(price_row["kimchi_premium"]),
        "exchangeRate":  float(price_row["exchange_rate"]),
        "history": {
            "labels":  [r["trade_datetime"].strftime("%m.%d") for r in history_rows],
            "upbit":   [int(r["upbit_price"]) for r in history_rows],
            "binance": [int(r["binance_price"]) for r in history_rows]
        }
    }
