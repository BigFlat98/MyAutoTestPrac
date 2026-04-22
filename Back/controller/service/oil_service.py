import yfinance as yf
from datetime import datetime
import pandas as pd

# yfinance commodity symbols (Futures)
GRADE_CONFIG = {
    "WTI": {"symbol": "CL=F"},
    "BRENT": {"symbol": "BZ=F"},
}


def fetch_oil_prices(grade: str, length: int = 90, include_missing: bool = False):
    """
    yfinance를 통해 원유 선물 일별(EOD) 가격(USD)을 최대 length일치 가져옵니다.
    반환값: 날짜 오름차순 정렬된 dict 리스트 [{"period": "2024-01-15", "value": "72.50"}, ...]
    """
    symbol = GRADE_CONFIG.get(grade.upper(), {}).get("symbol")
    if not symbol:
        print(f"[oil_service] Unknown grade: {grade}")
        return None

    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="1y")

        if df is None or df.empty:
            print(f"[oil_service] yfinance: empty data for {grade} ({symbol})")
            return None

        rows = []
        for date, row in df.iterrows():
            period = date.strftime("%Y-%m-%d")
            value = row["Close"]
            if value is not None and not pd.isna(value):
                # 소수점 2자리 정도로 반올림
                rows.append({"period": period, "value": str(round(value, 2))})

        # 날짜 오름차순 정렬 후 최근 length개만 사용
        rows.sort(key=lambda x: x.get("period", ""))
        if length and len(rows) > length:
            rows = rows[-length:]

        return rows

    except Exception as e:
        print(f"[oil_service] Error fetching yfinance data for {grade}: {e}")
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

    return {
        "grade": grade,
        "price": float(price_row["price_usd"]),
        "changeRate": float(price_row["change_rate"]),
        "history": {
            "labels": labels,
            "prices": prices,
        },
    }
