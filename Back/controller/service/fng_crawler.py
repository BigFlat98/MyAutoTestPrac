import requests
import random
from database import db


def fetch_fear_and_greed_from_api():
    """CNN API에서 공포탐욕지수를 직접 가져옵니다. (스케줄러 전용)"""
    url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "https://edition.cnn.com/"
    }
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        fng_data = data.get('fear_and_greed', {})
        score = int(fng_data.get('score', 0))
        rating = fng_data.get('rating', 'Unknown')
        return {"score": score, "rating": rating, "status": "success"}
    except Exception as e:
        print(f"[FNG] API 호출 실패: {e}")

    # 폴백: Mock 데이터 반환
    mock_score = random.randint(30, 70)
    return {
        "score": mock_score,
        "rating": "Fear" if mock_score < 50 else "Greed",
        "status": "error"
    }


async def get_fear_and_greed_index():
    """DB에 저장된 최신 공포탐욕지수를 반환합니다. (라우터 전용)"""
    async with db.pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT score, rating, fetched_at FROM market_fear_greed ORDER BY fetched_at DESC LIMIT 1"
        )
    if not row:
        return None
    return {
        "score": row["score"],
        "rating": row["rating"],
        "status": "success",
        "timestamp": row["fetched_at"]
    }
