from fastapi import APIRouter
from controller.service.fng_crawler import get_fear_and_greed_index
from controller.service.stock_service import get_stock_data

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/fear-greed")
def get_fear_greed():
    data = get_fear_and_greed_index()
    return data

@router.get("/stocks/{market}")
def get_dashboard_stocks(market: str):
    # market: 'kospi' or 'nasdaq'
    return get_stock_data(market.lower())
