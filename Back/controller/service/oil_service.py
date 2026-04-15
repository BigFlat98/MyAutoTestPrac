import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"

# Alpha Vantage commodities functions for crude oil
GRADE_CONFIG = {
    "WTI": {"function": "WTI"},
    "BRENT": {"function": "BRENT"},
}


def fetch_oil_prices(grade: str, length: int = 90, include_missing: bool = False):
    """
    Alpha Vantage API에서 원유 일별 가격 (USD/bbl)을 최대 length일치 가져옵니다.
    반환값: 날짜 오름차순 정렬된 dict 리스트 [{"period": "2024-01-15", "value": "72.50"}, ...]
    """
    if not ALPHA_VANTAGE_API_KEY:
        print("[oil_service] ALPHA_VANTAGE_API_KEY not found in env")
        return None

    fn = GRADE_CONFIG.get(grade.upper(), {}).get("function")
    if not fn:
        print(f"[oil_service] Unknown grade: {grade}")
        return None

    params = {
        "apikey": ALPHA_VANTAGE_API_KEY,
        "function": fn,
        "interval": "daily",
        "datatype": "json",
    }

    try:
        response = requests.get(ALPHA_VANTAGE_BASE_URL, params=params, timeout=20)
        if response.status_code != 200:
            print(f"[oil_service] Alpha Vantage API Error: {response.status_code} - {response.text[:200]}")
            return None

        payload = response.json()
        if isinstance(payload, dict) and (payload.get("Note") or payload.get("Information")):
            # Rate limit / informational response
            msg = payload.get("Note") or payload.get("Information")
            print(f"[oil_service] Alpha Vantage note/info for {grade}: {str(msg)[:200]}")
            return None
        if isinstance(payload, dict) and payload.get("Error Message"):
            print(f"[oil_service] Alpha Vantage error for {grade}: {str(payload.get('Error Message'))[:200]}")
            return None

        rows = []

        # Commodities endpoints commonly return: {"name": "...", "interval": "...", "unit": "...", "data": [{"date": "...", "value": "..."}]}
        if isinstance(payload, dict) and isinstance(payload.get("data"), list):
            for item in payload.get("data") or []:
                period = item.get("date")
                value = item.get("value")
                if period:
                    rows.append({"period": str(period), "value": value})

        # Fallback: in case of time-series style payloads
        if not rows and isinstance(payload, dict):
            ts = payload.get("Time Series (Daily)") or payload.get("time_series") or payload.get("timeSeries")
            if isinstance(ts, dict):
                for dt, ohlc in ts.items():
                    if isinstance(ohlc, dict):
                        close_v = ohlc.get("4. close") or ohlc.get("close") or ohlc.get("value")
                    else:
                        close_v = None
                    rows.append({"period": str(dt), "value": close_v})

        if not rows:
            print(f"[oil_service] Alpha Vantage: empty/unrecognized data for {grade}")
            return None

        # 날짜 오름차순 정렬 후 최근 length개만 사용
        rows.sort(key=lambda x: x.get("period", ""))
        if length and len(rows) > length:
            rows = rows[-length:]

        if include_missing:
            return rows

        # 유효한 값만 추려 반환
        valid = [r for r in rows if r.get("value") not in (None, ".")]
        return valid

    except Exception as e:
        print(f"[oil_service] Error fetching Alpha Vantage data for {grade}: {e}")
        return None


async def get_oil_data_from_db(grade: str = "WTI"):
    """DB에 저장된 유가 현재가 + 90일 히스토리를 반환합니다."""
    from database import db

    grade = grade.upper()
    async with db.pool.acquire() as conn:
        price_row = await conn.fetchrow(
            "SELECT price_usd, change_rate FROM market_oil_price WHERE grade = $1 ORDER BY fetched_at DESC LIMIT 1",
            grade,
        )
        history_rows = await conn.fetch(
            "SELECT trade_date, price_usd FROM market_oil_history WHERE grade = $1 ORDER BY trade_date",
            grade,
        )

    if not price_row:
        return None

    labels = [r["trade_date"].strftime("%m/%d") for r in history_rows]
    prices = [float(r["price_usd"]) for r in history_rows]

    # EIA 데이터는 1~2 영업일 지연 게시 → 마지막 값으로 오늘까지 forward-fill
    if history_rows:
        last_date = history_rows[-1]["trade_date"]
        today = datetime.now().date()
        current = last_date + timedelta(days=1)
        last_price = prices[-1]
        while current <= today:
            labels.append(current.strftime("%m/%d"))
            prices.append(last_price)
            current += timedelta(days=1)

    return {
        "grade": grade,
        "price": float(price_row["price_usd"]),
        "changeRate": float(price_row["change_rate"]),
        "history": {
            "labels": labels,
            "prices": prices,
        },
    }
