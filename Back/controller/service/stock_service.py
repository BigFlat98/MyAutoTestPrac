import os
import requests
from dotenv import load_dotenv

import datetime
import json

load_dotenv()

# Twelve Data Config
TWELVE_API_KEY = os.getenv("TWELVE_DATA_API_KEY")
TWELVE_BASE_URL = "https://api.twelvedata.com/quote"

# KIS (Korea Investment & Securities) Config
KIS_AppKey = os.getenv("KIS_APP_KEY")
KIS_AppSecret = os.getenv("KIS_APP_SECRET")
KIS_CANO = os.getenv("KIS_ACCOUNT_NO") # Account No (First 8 digits)
KIS_ACNT_PRDT_CD = "01" # Account Product Code, usually '01'
KIS_BASE_URL = "https://openapi.koreainvestment.com:9443" # Check if user wants real or vps. Defaulting to Real.

# Simple In-Memory Cache
# Structure: { "nasdaq": { "data": [...], "timestamp": datetime } }
_cache = {}
CACHE_DURATION_MINUTES = 5

# KIS Token Cache
_kis_token_cache = {
    "access_token": None,
    "token_expiry": None
}

# KIS REST API: 모의투자 기준 sleep 1.5s 간격으로 40개 조회 시 약 60초 소요
# 10분 스케줄러 내 허용 범위이며, 장외 종가 확인용 DB 저장 목적
KOSPI_SYMBOLS = [
    "005930", # 삼성전자
    "000660", # SK하이닉스
    "005380", # 현대차
    "012450", # 한화에어로스페이스
    "079550", # LIG넥스원
    "272210", # 한화시스템
    "034020", # 두산에너빌리티
    "360750", # TIGER 미국S&P500
    "261220", # KODEX WTI원유선물(H)
    "035420", # NAVER
    "035720", # 카카오
    "373220", # LG에너지솔루션
    "006400", # 삼성SDI
    "051910", # LG화학
    "068270", # 셀트리온
    "000270", # 기아
    "005490", # POSCO홀딩스
    "105560", # KB금융
    "055550", # 신한지주
    "086790", # 하나금융지주
    "017670", # SK텔레콤
    "030200", # KT
    "066570", # LG전자
    "028260", # 삼성물산
    "012330", # 현대모비스
    "096770", # SK이노베이션
    "034730", # SK
    "032830", # 삼성생명
    "323410", # 카카오뱅크
    "259960", # 크래프톤
    "247540", # 에코프로비엠
    "086520", # 에코프로
    "003670", # 포스코퓨처엠
    "329180", # HD현대중공업
    "015760", # 한국전력
    "241560", # 두산밥캣
    "009150", # 삼성전기
    "000720", # 현대건설
    "003550", # LG
    "069500", # KODEX 200
]

NASDAQ_SYMBOLS = [
    "AAPL", "NVDA", "MSFT", "AMZN", "GOOGL"
]

def get_kis_auth_token():
    """
    Get or refresh KIS Access Token.
    Returns the access token string.
    """
    global _kis_token_cache
    now = datetime.datetime.now()
    
    # Check if we have a valid token
    if _kis_token_cache["access_token"] and _kis_token_cache["token_expiry"]:
        # Buffer of 60 seconds
        if now < _kis_token_cache["token_expiry"] - datetime.timedelta(seconds=60):
            return _kis_token_cache["access_token"]

    url = f"{KIS_BASE_URL}/oauth2/tokenP"
    headers = {"content-type": "application/json"}
    body = {
        "grant_type": "client_credentials",
        "appkey": KIS_AppKey,
        "appsecret": KIS_AppSecret
    }
    
    try:
        res = requests.post(url, headers=headers, data=json.dumps(body), timeout=10)
        res.raise_for_status()
        data = res.json()
        
        access_token = data.get("access_token")
        expires_in = data.get("expires_in", 86400) # Default 1 day
        
        _kis_token_cache["access_token"] = access_token
        _kis_token_cache["token_expiry"] = now + datetime.timedelta(seconds=expires_in)
        
        return access_token
    except Exception as e:
        print(f"Error getting KIS token: {e}")
        return None

def get_kospi_data_from_kis():
    """
    Fetch KOSPI stock data from KIS API.
    """
    access_token = get_kis_auth_token()
    if not access_token:
        return {"market": "kospi", "stocks": [], "status": "error", "message": "Failed to authenticate with KIS API"}

    result = []
    
    # KIS API Current Price Endpoint
    url = f"{KIS_BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-price"
    
    headers = {
        "content-type": "application/json; charset=utf-8",
        "authorization": f"Bearer {access_token}",
        "appkey": KIS_AppKey,
        "appsecret": KIS_AppSecret,
        "tr_id": "FHKST01010100" # JooSik HyunJaeGa (Stock Current Price)
    }
    
    # Dictionary to map symbol to readable name (KIS API returns name but we can hardcode for safety/speed if needed, but API usually has it? 
    # Actually inquire-price response might NOT contain the stock name, just price details.
    # We should map manually or fetch master. For simplicity, manual mapping for these 5 top stocks.
    
    name_map = {
        "005930": "삼성전자",       "000660": "SK하이닉스",
        "005380": "현대차",         "012450": "한화에어로스페이스",
        "079550": "LIG넥스원",      "272210": "한화시스템",
        "034020": "두산에너빌리티", "360750": "TIGER 미국S&P500",
        "261220": "KODEX WTI원유선물(H)",
        "035420": "NAVER",          "035720": "카카오",
        "373220": "LG에너지솔루션", "006400": "삼성SDI",
        "051910": "LG화학",         "068270": "셀트리온",
        "000270": "기아",           "005490": "POSCO홀딩스",
        "105560": "KB금융",         "055550": "신한지주",
        "086790": "하나금융지주",   "017670": "SK텔레콤",
        "030200": "KT",             "066570": "LG전자",
        "028260": "삼성물산",       "012330": "현대모비스",
        "096770": "SK이노베이션",   "034730": "SK",
        "032830": "삼성생명",       "323410": "카카오뱅크",
        "259960": "크래프톤",       "247540": "에코프로비엠",
        "086520": "에코프로",       "003670": "포스코퓨처엠",
        "329180": "HD현대중공업",   "015760": "한국전력",
        "241560": "두산밥캣",       "009150": "삼성전기",
        "000720": "현대건설",       "003550": "LG",
        "069500": "KODEX 200",
    }

    import time

    for i, symbol in enumerate(KOSPI_SYMBOLS):
        # 모의투자 rate limit 대응: 1.5초 간격 (40종목 × 1.5s ≈ 60초)
        time.sleep(1.5)
        
        params = {
            "fid_cond_mrkt_div_code": "J",
            "fid_input_iscd": symbol
        }
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                res = requests.get(url, headers=headers, params=params, timeout=5)
                res.raise_for_status()
                data = res.json()
                
                # Response structure check
                # output: { stck_prpr (price), prdy_ctrt (change rate), ... }
                if data.get("rt_cd") == "0":
                    output = data.get("output", {})
                    price = float(output.get("stck_prpr", 0))
                    change = float(output.get("prdy_ctrt", 0))
                    
                    result.append({
                        "rank": i + 1,
                        "symbol": symbol,
                        "name": name_map.get(symbol, symbol),
                        "price": price,
                        "change": change,
                        "currency": "KRW"
                    })
                    break  # 성공 시 재시도 루프 탈출
                else:
                    # KIS API 자체 에러 메시지(예: 잘못된 키 등)인 경우 재시도 의미가 없으므로 중단
                    print(f"KIS API Error for {symbol}: {data.get('msg1')}")
                    break
            except Exception as e:
                print(f"Error fetching {symbol} from KIS (Attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2.0)  # 재시도 전 대기 시간 추가
                else:
                    print(f"Failed to fetch {symbol} after {max_retries} attempts.")
            
    return {"market": "kospi", "stocks": result, "status": "success"}


def get_stock_data(market: str):
    global _cache
    
    # Check Cache Validity
    now = datetime.datetime.now()
    if market in _cache:
        last_update = _cache[market]["timestamp"]
        # If cache is fresh (less than 5 minutes old), return it to save API credits
        if (now - last_update).total_seconds() < (CACHE_DURATION_MINUTES * 60):
            print(f"Returning cached data for {market}")
            return _cache[market]["data"]

    final_data = None

    if market == "kospi":
        # Check if KIS keys are present
        if not KIS_AppKey or not KIS_AppSecret:
             return {"market": "kospi", "stocks": [], "status": "error", "message": "KIS API Credentials missing"}
        
        final_data = get_kospi_data_from_kis()
        
    elif market == "nasdaq":
        symbols_list = NASDAQ_SYMBOLS
        symbols_str = ",".join(symbols_list)
        
        params = {
            "symbol": symbols_str,
            "apikey": TWELVE_API_KEY,
            "format": "json"
        }
        
        try:
            response = requests.get(TWELVE_BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if "code" in data and data["code"] != 200:
                print(f"Twelve Data API Error: {data['message']}")
                if market in _cache: return _cache[market]["data"]
                return {"market": market, "stocks": [], "status": "error", "message": data["message"]}
            
            result = []
            for i, symbol in enumerate(symbols_list):
                item = None
                if symbol in data: item = data[symbol]
                elif "symbol" in data and data["symbol"] == symbol: item = data
                    
                if item:
                    try: change_pct = float(item.get("percent_change", 0))
                    except: change_pct = 0.0
                        
                    result.append({
                        "rank": i + 1,
                        "symbol": symbol,
                        "name": item.get("name", symbol),
                        "price": float(item.get("close", 0)),
                        "change": change_pct,
                        "currency": item.get("currency", "USD")
                    })
            
            final_data = {"market": market, "stocks": result, "status": "success"}

        except Exception as e:
            print(f"Error fetching stocks from Twelve Data: {e}")
            if market in _cache: return _cache[market]["data"]
            return {"market": market, "stocks": [], "status": "error"}
            
    else:
        return {"market": market, "stocks": [], "status": "error", "message": "Unknown market"}

    # Update Cache if success
    if final_data and final_data.get("status") == "success":
        _cache[market] = {
            "data": final_data,
            "timestamp": now
        }
    
    return final_data


async def get_stock_data_from_db(market: str):
    """DB에 저장된 최신 주식 현재가를 반환합니다."""
    from database import db

    async with db.pool.acquire() as conn:
        latest = await conn.fetchrow(
            "SELECT MAX(fetched_at) AS latest FROM market_stocks WHERE market = $1",
            market.upper()
        )
        if not latest or not latest["latest"]:
            return None

        rows = await conn.fetch(
            """SELECT rank, name, symbol, price, change_rate
               FROM market_stocks
               WHERE market = $1 AND fetched_at = $2
               ORDER BY rank""",
            market.upper(), latest["latest"]
        )

    stocks = [
        {
            "rank":   r["rank"],
            "name":   r["name"],
            "symbol": r["symbol"],
            "price":  float(r["price"]),
            "change": float(r["change_rate"])
        }
        for r in rows
    ]
    return {"market": market.lower(), "stocks": stocks, "status": "success"}
