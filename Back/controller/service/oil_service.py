import requests
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

EIA_API_KEY = os.getenv("EIA_API_KEY")
EIA_BASE_URL = "https://api.eia.gov/v2/petroleum/pri/spt/data/"

# EIA v2 product facet codes for crude oil spot prices
GRADE_CONFIG = {
    "WTI":   {"product": "EPCWTI"},
    "BRENT": {"product": "EPCBRENT"},
}


def fetch_oil_prices(grade: str, length: int = 90):
    """
    EIA v2 API에서 원유 일별 현물가 (USD/bbl)를 최대 length일치 가져옵니다.
    반환값: 날짜 오름차순 정렬된 dict 리스트 [{"period": "2024-01-15", "value": "72.50"}, ...]
    """
    if not EIA_API_KEY:
        print("[oil_service] EIA_API_KEY not found in env")
        return None

    product_code = GRADE_CONFIG.get(grade.upper(), {}).get("product")
    if not product_code:
        print(f"[oil_service] Unknown grade: {grade}")
        return None

    params = {
        "api_key": EIA_API_KEY,
        "frequency": "daily",
        "data[]": "value",
        "facets[product][]": product_code,
        "sort[0][column]": "period",
        "sort[0][direction]": "desc",
        "length": length,
    }

    try:
        response = requests.get(EIA_BASE_URL, params=params, timeout=15)
        if response.status_code != 200:
            print(f"[oil_service] EIA API Error: {response.status_code} - {response.text[:200]}")
            return None

        rows = response.json().get("response", {}).get("data", [])
        if not rows:
            print(f"[oil_service] EIA: empty data for {grade}")
            return None

        # 유효한 값만 추려 날짜 오름차순 정렬
        valid = [r for r in rows if r.get("value") not in (None, ".")]
        valid.sort(key=lambda x: x.get("period", ""))
        return valid

    except Exception as e:
        print(f"[oil_service] Error fetching EIA data for {grade}: {e}")
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

    return {
        "grade": grade,
        "price": float(price_row["price_usd"]),
        "changeRate": float(price_row["change_rate"]),
        "history": {
            "labels": [r["trade_date"].strftime("%m/%d") for r in history_rows],
            "prices": [float(r["price_usd"]) for r in history_rows],
        },
    }
