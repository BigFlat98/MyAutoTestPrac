"""
[대시보드 마켓 데이터 스케줄러]

외부 API를 주기적으로 호출해 데이터를 DB에 저장합니다.
기존 서비스 모듈을 그대로 재사용하며, 저장 로직만 추가합니다.

수집 주기:
  - 공포탐욕지수: 1시간
  - 주식 (KOSPI/NASDAQ): 10분
  - 환율: 1시간
  - 기준금리: 24시간
  - 암호화폐: 5분
  - 금: 1시간
"""
import asyncio
from datetime import datetime, date
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from database import db
from controller.service.fng_crawler import fetch_fear_and_greed_from_api
from controller.service.stock_service import get_stock_data
from controller.service.exchange_service import ExchangeRateService
from controller.service.interest_service import InterestRateService
from controller.service import crypto_service, gold_service

# ──────────────────────────────────────────────────────────────────────────────
# [트러블슈팅] 스케줄러 잡 미실행 문제
#
# 발생 문제:
#   EC2 배포 후 앱 시작 시 crypto를 제외한 나머지 잡(fear_greed, stocks,
#   exchange_rate, interest_rate, gold)이 실행되지 않아 DB에 데이터가
#   저장되지 않음 → 해당 엔드포인트 전부 503 응답.
#
# 발생 원인:
#   setup_scheduler()에서 모든 잡을 next_run_time=now로 등록하지만,
#   APScheduler가 실제로 잡을 실행하기까지 EC2 환경에서 약 3초가 소요됨.
#   APScheduler의 기본 misfire_grace_time은 1초이므로,
#   3초 > 1초 → 1초를 초과한 잡은 "missed"로 처리되어 스킵됨.
#   (crypto만 타이밍 차이로 1초 이내에 처리되어 정상 실행)
#
#   로그 예시:
#     Run time of job "fetch_and_save_exchange_rate..." was missed by 0:00:02.966367
#
# 해결 방안:
#   misfire_grace_time=None 설정 → 지연 시간에 상관없이 missed 잡을 반드시 실행.
# ──────────────────────────────────────────────────────────────────────────────
scheduler = AsyncIOScheduler(job_defaults={"misfire_grace_time": None})


# ──────────────────────────────────────────
# 공포탐욕지수
# ──────────────────────────────────────────
async def fetch_and_save_fear_greed():
    print("[Scheduler] Fetching Fear & Greed Index...")
    try:
        data = fetch_fear_and_greed_from_api()
        async with db.pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO market_fear_greed (score, rating) VALUES ($1, $2)",
                data["score"], data["rating"]
            )
        print(f"[Scheduler] Fear & Greed saved: score={data['score']}, rating={data['rating']}")
    except Exception as e:
        print(f"[Scheduler][ERROR] Fear & Greed: {e}")


# ──────────────────────────────────────────
# 주식 (KOSPI / NASDAQ)
# ──────────────────────────────────────────
async def fetch_and_save_stocks():
    print("[Scheduler] Fetching Stocks...")
    batch_time = datetime.now()
    try:
        for market in ["kospi", "nasdaq"]:
            data = await asyncio.get_event_loop().run_in_executor(
                None, get_stock_data, market
            )
            if not data or data.get("status") != "success":
                print(f"[Scheduler][WARN] Stocks {market}: no data or error status")
                continue

            async with db.pool.acquire() as conn:
                for stock in data["stocks"]:
                    await conn.execute(
                        """INSERT INTO market_stocks
                           (market, rank, name, symbol, price, change_rate, fetched_at)
                           VALUES ($1, $2, $3, $4, $5, $6, $7)""",
                        market.upper(),
                        stock["rank"],
                        stock["name"],
                        stock["symbol"],
                        float(stock["price"]),
                        float(stock["change"]),
                        batch_time
                    )
            print(f"[Scheduler] Stocks {market.upper()} saved: {len(data['stocks'])} items")
    except Exception as e:
        print(f"[Scheduler][ERROR] Stocks: {e}")


# ──────────────────────────────────────────
# 환율 (USD/KRW 일별 시계열)
# ──────────────────────────────────────────
async def fetch_and_save_exchange_rate():
    print("[Scheduler] Fetching Exchange Rate...")
    try:
        service = ExchangeRateService()
        data = await asyncio.get_event_loop().run_in_executor(
            None, service.get_usd_krw_rate
        )
        if not data or not data["dates"]:
            print("[Scheduler][WARN] Exchange Rate: no data")
            return

        async with db.pool.acquire() as conn:
            for date_str, rate in zip(data["dates"], data["rates"]):
                await conn.execute(
                    """INSERT INTO market_exchange_rate (trade_date, rate)
                       VALUES ($1, $2)
                       ON CONFLICT (trade_date) DO UPDATE
                       SET rate = EXCLUDED.rate,
                           updated_at = CURRENT_TIMESTAMP""",
                    datetime.strptime(date_str, "%Y-%m-%d").date(),
                    float(rate)
                )
        print(f"[Scheduler] Exchange Rate saved: {len(data['dates'])} rows")
    except Exception as e:
        print(f"[Scheduler][ERROR] Exchange Rate: {e}")


# ──────────────────────────────────────────
# 기준금리 (한국 / 미국)
# ──────────────────────────────────────────
async def fetch_and_save_interest_rate():
    print("[Scheduler] Fetching Interest Rates...")
    try:
        service = InterestRateService()
        data = await asyncio.get_event_loop().run_in_executor(
            None, service.get_comparison_data
        )
        if not data or not data["dates"]:
            print("[Scheduler][WARN] Interest Rate: no data")
            return

        async with db.pool.acquire() as conn:
            for date_str, kr, us in zip(data["dates"], data["kr"], data["us"]):
                await conn.execute(
                    """INSERT INTO market_interest_rate (trade_date, kr_rate, us_rate)
                       VALUES ($1, $2, $3)
                       ON CONFLICT (trade_date) DO UPDATE
                       SET kr_rate = EXCLUDED.kr_rate,
                           us_rate = EXCLUDED.us_rate,
                           updated_at = CURRENT_TIMESTAMP""",
                    datetime.strptime(date_str, "%Y-%m-%d").date(),
                    float(kr),
                    float(us)
                )
        print(f"[Scheduler] Interest Rate saved: {len(data['dates'])} rows")
    except Exception as e:
        print(f"[Scheduler][ERROR] Interest Rate: {e}")


# ──────────────────────────────────────────
# 암호화폐 (BTC / ETH / XRP)
# ──────────────────────────────────────────
async def fetch_and_save_crypto():
    """
    현재가: 기존 get_crypto_data() 재사용 (upbit ccxt None 폴백 포함)
    히스토리: fetch_ohlcv 직접 호출 (raw timestamp → TIMESTAMP 저장)
    """
    print("[Scheduler] Fetching Crypto...")
    try:
        exchange_rate = crypto_service.get_exchange_rate()

        for coin in ["BTC", "ETH", "XRP"]:
            try:
                # 현재가 — 기존 서비스 함수 재사용 (upbit None 폴백 로직 포함)
                data = await crypto_service.get_crypto_data(coin)
                if not data:
                    print(f"[Scheduler][WARN] Crypto {coin}: no data returned")
                    continue

                async with db.pool.acquire() as conn:
                    await conn.execute(
                        """INSERT INTO market_crypto_price
                           (coin, krw_price, usd_price, change_rate, kimchi_premium, exchange_rate)
                           VALUES ($1, $2, $3, $4, $5, $6)""",
                        coin,
                        float(data["krwPrice"]),
                        float(data["usdPrice"]),
                        float(data["changeRate"]),
                        float(data["kimchiPremium"]),
                        float(data["exchangeRate"]),
                    )

                # 히스토리 — OHLCV raw timestamp 사용 (fetch_ohlcv는 upbit 정상 동작)
                symbols = crypto_service.SYMBOL_MAP[coin]
                ohlcv_upbit   = crypto_service.upbit.fetch_ohlcv(symbols["upbit"], "1d", limit=90)
                ohlcv_binance = crypto_service.binance.fetch_ohlcv(symbols["binance"], "1d", limit=90)

                length = min(len(ohlcv_upbit), len(ohlcv_binance))
                async with db.pool.acquire() as conn:
                    for i in range(length):
                        trade_dt      = datetime.fromtimestamp(ohlcv_upbit[i][0] / 1000)
                        upbit_close   = float(ohlcv_upbit[i][4])
                        binance_close_krw = float(ohlcv_binance[i][4]) * float(exchange_rate)

                        await conn.execute(
                            """INSERT INTO market_crypto_history
                               (coin, trade_datetime, upbit_price, binance_price)
                               VALUES ($1, $2, $3, $4)
                               ON CONFLICT (coin, trade_datetime) DO UPDATE
                               SET upbit_price    = EXCLUDED.upbit_price,
                                   binance_price  = EXCLUDED.binance_price,
                                   updated_at     = CURRENT_TIMESTAMP""",
                            coin, trade_dt, upbit_close, binance_close_krw
                        )

                print(f"[Scheduler] Crypto {coin} saved: price + {length} history rows")

            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"[Scheduler][ERROR] Crypto {coin}: {e}")

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[Scheduler][ERROR] Crypto (outer): {e}")


# ──────────────────────────────────────────
# 금 (국내 / 국제)
# ──────────────────────────────────────────
async def fetch_and_save_gold():
    print("[Scheduler] Fetching Gold...")
    try:
        domestic_items = await asyncio.get_event_loop().run_in_executor(
            None, gold_service.get_domestic_gold_price
        )
        international_df = await asyncio.get_event_loop().run_in_executor(
            None, gold_service.get_international_gold_data
        )

        if not domestic_items:
            print("[Scheduler][WARN] Gold: no domestic data")
            return

        latest = domestic_items[-1]
        current_price = float(int(latest.get("clpr", 0)))
        change_rate = float(latest.get("fltRt", 0))

        # 현재가 스냅샷 저장
        async with db.pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO market_gold_price (domestic_price, change_rate) VALUES ($1, $2)",
                current_price, change_rate
            )

        # 국제 금 가격 날짜별 맵 구성
        intl_map = {}
        if international_df is not None and not international_df.empty:
            for dt, row in international_df.iterrows():
                intl_map[dt.strftime("%Y-%m-%d")] = round(float(row["Close"]), 4)

        # 히스토리 저장
        async with db.pool.acquire() as conn:
            for item in domestic_items:
                dt_str = item.get("basDt", "")
                if len(dt_str) == 8:
                    trade_date = date(int(dt_str[:4]), int(dt_str[4:6]), int(dt_str[6:8]))
                    domestic_price = float(int(item.get("clpr", 0)))
                    intl_price = intl_map.get(trade_date.strftime("%Y-%m-%d"))

                    await conn.execute(
                        """INSERT INTO market_gold_history
                           (trade_date, domestic_price, international_price)
                           VALUES ($1, $2, $3)
                           ON CONFLICT (trade_date) DO UPDATE
                           SET domestic_price = EXCLUDED.domestic_price,
                               international_price = EXCLUDED.international_price,
                               updated_at = CURRENT_TIMESTAMP""",
                        trade_date, domestic_price, intl_price
                    )

        print(f"[Scheduler] Gold saved: price + {len(domestic_items)} history rows")

    except Exception as e:
        print(f"[Scheduler][ERROR] Gold: {e}")


# ──────────────────────────────────────────
# 스케줄러 등록
# ──────────────────────────────────────────
def setup_scheduler():
    """
    각 잡을 등록하고 스케줄러 인스턴스를 반환합니다.
    next_run_time=datetime.now() 으로 앱 시작 시 즉시 1회 실행됩니다.
    """
    now = datetime.now()

    # replace_existing=True: 재시작 시 동일 id 잡이 이미 등록된 경우 덮어씀 (ConflictingIdError 방지)
    scheduler.add_job(fetch_and_save_fear_greed,  "interval", hours=1,    id="fear_greed",    next_run_time=now, replace_existing=True)
    scheduler.add_job(fetch_and_save_stocks,       "interval", minutes=10, id="stocks",        next_run_time=now, replace_existing=True)
    scheduler.add_job(fetch_and_save_exchange_rate,"interval", hours=1,    id="exchange_rate", next_run_time=now, replace_existing=True)
    scheduler.add_job(fetch_and_save_interest_rate,"interval", hours=24,   id="interest_rate", next_run_time=now, replace_existing=True)
    scheduler.add_job(fetch_and_save_crypto,       "interval", minutes=5,  id="crypto",        next_run_time=now, replace_existing=True)
    scheduler.add_job(fetch_and_save_gold,         "interval", hours=1,    id="gold",          next_run_time=now, replace_existing=True)

    return scheduler
