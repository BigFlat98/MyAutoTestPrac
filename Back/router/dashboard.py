from fastapi import APIRouter
from controller.service.fng_crawler import get_fear_and_greed_index
from controller.service.stock_service import get_stock_data_from_db
from controller.service.interest_service import get_comparison_data_from_db
from controller.service.exchange_service import get_usd_krw_rate_from_db
from controller.service.crypto_service import get_crypto_data_from_db
from controller.service.gold_service import get_gold_data_from_db
from fastapi import HTTPException

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

# ... existing endpoints ...

@router.get("/interest-rates")
async def get_interest_rates():
    data = await get_comparison_data_from_db()
    if not data:
        raise HTTPException(status_code=503, detail="데이터를 수집 중입니다. 잠시 후 다시 시도해 주세요.")
    return data

@router.get("/exchange-rate")
async def get_exchange_rate():
    data = await get_usd_krw_rate_from_db()
    if not data:
        raise HTTPException(status_code=503, detail="데이터를 수집 중입니다. 잠시 후 다시 시도해 주세요.")
    return data

@router.get("/fear-greed")
async def get_fear_greed():
    data = await get_fear_and_greed_index()
    if not data:
        raise HTTPException(status_code=503, detail="데이터를 수집 중입니다. 잠시 후 다시 시도해 주세요.")
    return data

@router.get("/stocks/{market}")
async def get_dashboard_stocks(market: str):
    data = await get_stock_data_from_db(market.lower())
    if not data:
        raise HTTPException(status_code=503, detail="데이터를 수집 중입니다. 잠시 후 다시 시도해 주세요.")
    return data

@router.get("/crypto/{coin}")
async def get_crypto(coin: str):
    data = await get_crypto_data_from_db(coin.upper())
    if not data:
        raise HTTPException(status_code=503, detail="데이터를 수집 중입니다. 잠시 후 다시 시도해 주세요.")
    return data

@router.get("/gold")
async def get_gold():
    data = await get_gold_data_from_db()
    if not data:
        raise HTTPException(status_code=503, detail="데이터를 수집 중입니다. 잠시 후 다시 시도해 주세요.")
    return data
