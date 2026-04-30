from fastapi import APIRouter
from controller.service.stock_detail_service import fetch_stock_overview, fetch_stock_investors, fetch_stock_news

router = APIRouter(
    prefix="/api/stock",
    tags=["StockDetail"]
)

@router.get("/{symbol}/overview")
async def get_stock_overview(symbol: str):
    """
    재무 지표 및 외국인 지분율 조회 (DB 캐싱 적용)
    """
    return await fetch_stock_overview(symbol)

@router.get("/{symbol}/investors")
async def get_stock_investors(symbol: str):
    """
    개인/기관/외국인 당일 순매수 동향 (캐시 없음, 실시간 조회)
    """
    return await fetch_stock_investors(symbol)

@router.get("/{symbol_name}/news")
async def get_stock_news(symbol_name: str):
    """
    네이버 API를 이용한 뉴스 5건 검색
    """
    return await fetch_stock_news(symbol_name)
