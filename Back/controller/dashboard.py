from fastapi import APIRouter
from controller.service.fng_crawler import get_fear_and_greed_index
from controller.service.stock_service import get_stock_data
from controller.service.interest_service import InterestRateService
from controller.service.exchange_service import ExchangeRateService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

# ... existing endpoints ...

@router.get("/interest-rates")
async def get_interest_rates():
    service = InterestRateService()
    data = service.get_comparison_data()
    return data

@router.get("/exchange-rate")
async def get_exchange_rate():
    service = ExchangeRateService()
    data = service.get_usd_krw_rate()
    return data

@router.get("/fear-greed")
def get_fear_greed():
    data = get_fear_and_greed_index()
    return data

@router.get("/stocks/{market}")
def get_dashboard_stocks(market: str):
    # market: 'kospi' or 'nasdaq'
    return get_stock_data(market.lower())
