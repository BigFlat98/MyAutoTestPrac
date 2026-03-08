from database import db

async def get_fear_and_greed_index():
    """DB에 저장된 최신 공포탐욕지수를 반환합니다."""
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