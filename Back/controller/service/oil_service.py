import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

FMP_API_KEY = os.getenv("FMP_API_KEY")
FMP_BASE_URL = "https://financialmodelingprep.com/stable"

# FMP commodity symbols (EOD full chart)
GRADE_CONFIG = {
    "WTI": {"symbol": "CLUSD"},
    "BRENT": {"symbol": "BZUSD"},
}


def fetch_oil_prices(grade: str, length: int = 90, include_missing: bool = False):
    """
    FMP API에서 원유 일별(EOD) 가격(USD)을 최대 length일치 가져옵니다.
    반환값: 날짜 오름차순 정렬된 dict 리스트 [{"period": "2024-01-15", "value": "72.50"}, ...]
    """
    if not FMP_API_KEY:
        print("[oil_service] FMP_API_KEY not found in env")
        return None

    symbol = GRADE_CONFIG.get(grade.upper(), {}).get("symbol")
    if not symbol:
        print(f"[oil_service] Unknown grade: {grade}")
        return None

    # EOD 데이터는 주말/휴일이 비므로, 충분히 넓게 요청 후 length개만 슬라이스
    today = datetime.now().date()
    from_date = today - timedelta(days=max(180, (length or 90) * 2))
    params = {"symbol": symbol, "from": from_date.strftime("%Y-%m-%d"), "to": today.strftime("%Y-%m-%d"), "apikey": FMP_API_KEY}

    try:
        response = requests.get(f"{FMP_BASE_URL}/historical-price-eod/full", params=params, timeout=20)
        if response.status_code != 200:
            print(f"[oil_service] FMP API Error: {response.status_code} - {response.text[:200]}")
            return None

        payload = response.json()

        # FMP full chart: {"symbol":"CLUSD","historical":[{"date":"2026-04-15","close":...}, ...]}
        historical = payload.get("historical") if isinstance(payload, dict) else None
        if not isinstance(historical, list) or len(historical) == 0:
            # 일부 엔드포인트/플랜에서는 리스트를 직접 반환하기도 해서 보조 처리
            if isinstance(payload, list) and payload:
                historical = payload
            else:
                print(f"[oil_service] FMP: empty/unrecognized data for {grade} ({symbol})")
                return None

        rows = []
        for item in historical:
            if not isinstance(item, dict):
                continue
            period = item.get("date")
            # EOD 기준으로 close를 사용
            value = item.get("close") if item.get("close") is not None else item.get("price")
            if period is None or value is None:
                continue
            rows.append({"period": str(period), "value": str(value)})

        # 날짜 오름차순 정렬 후 최근 length개만 사용
        rows.sort(key=lambda x: x.get("period", ""))
        if length and len(rows) > length:
            rows = rows[-length:]

        return rows if include_missing else rows

    except Exception as e:
        print(f"[oil_service] Error fetching FMP data for {grade}: {e}")
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
