import os
import requests
import urllib.parse
from fastapi import HTTPException
from bs4 import BeautifulSoup
from database import db
from controller.service.stock_service import get_kis_auth_token, KIS_AppKey, KIS_AppSecret, KIS_BASE_URL

NAVER_CLIENT_ID = os.getenv("NAVER_STOCKNEWS_CLIENTID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_STOCKNEWS_CLIENTSECRET")

def crawl_naver_financials(symbol: str):
    """네이버 금융에서 영업이익(억)과 부채비율(%)을 크롤링합니다."""
    url = f"https://finance.naver.com/item/main.naver?code={symbol}"
    op = 0.0
    debt = 0.0
    try:
        res = requests.get(url, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")
        table = soup.select_one("table.tb_type1_ifrs")
        if table:
            for tr in table.select("tbody tr"):
                th = tr.th.text.strip() if tr.th else ""
                if th == "영업이익":
                    tds = tr.select("td")
                    for i in range(min(3, len(tds)-1), -1, -1):
                        val = tds[i].text.strip().replace(",", "")
                        if val and val != "-":
                            op = float(val)
                            break
                elif th == "부채비율":
                    tds = tr.select("td")
                    for i in range(min(3, len(tds)-1), -1, -1):
                        val = tds[i].text.strip().replace(",", "")
                        if val and val != "-":
                            debt = float(val)
                            break
    except Exception as e:
        print(f"Crawling failed for {symbol}: {e}")
    return op, debt

async def _get_fallback_overview(symbol: str):
    """KIS API 실패 시 날짜 무관하게 DB에 저장된 과거 데이터를 반환"""
    async with db.pool.acquire() as conn:
        old = await conn.fetchrow(
            "SELECT * FROM market_stock_fundamental WHERE symbol = $1",
            symbol
        )
        if old:
            return dict(old)
    return None

async def fetch_stock_overview(symbol: str):
    # 1. DB에서 캐시된 데이터 조회 (당일 갱신된 데이터가 있는지 확인)
    async with db.pool.acquire() as conn:
        cached = await conn.fetchrow(
            """SELECT * FROM market_stock_fundamental 
               WHERE symbol = $1 AND updated_at >= CURRENT_DATE""",
            symbol
        )
        if cached:
            return dict(cached)

    # 2. 캐시가 없으면 KIS API 호출
    access_token = get_kis_auth_token()
    if not access_token:
        fallback = await _get_fallback_overview(symbol)
        if fallback:
            return fallback
        raise HTTPException(status_code=503, detail="KIS API unavailable and no cached data")

    # API 1: 주식현재가 체결 (FHKST01010100)
    url_1 = f"{KIS_BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-price"
    headers_1 = {
        "content-type": "application/json; charset=utf-8",
        "authorization": f"Bearer {access_token}",
        "appkey": KIS_AppKey,
        "appsecret": KIS_AppSecret,
        "tr_id": "FHKST01010100"
    }
    params_1 = {
        "fid_cond_mrkt_div_code": "J",
        "fid_input_iscd": symbol
    }

    try:
        res_1 = requests.get(url_1, headers=headers_1, params=params_1, timeout=5)
        data_1 = res_1.json()
        
        # API Limit 등 정상 응답이 아닐 경우 에러 발생 (DB 0 덮어쓰기 방지)
        if data_1.get("rt_cd") != "0":
            fallback = await _get_fallback_overview(symbol)
            if fallback:
                return fallback
            raise HTTPException(status_code=500, detail=data_1.get("msg1", "KIS API Error"))
            
        output_1 = data_1.get("output", {})
        
        per = float(output_1.get("per", 0) or 0)
        pbr = float(output_1.get("pbr", 0) or 0)
        eps = float(output_1.get("eps", 0) or 0)
        market_cap = float(output_1.get("hts_avls", 0) or 0) # 억 단위
        w52_high = float(output_1.get("w52_hgpr", 0) or 0)
        w52_low = float(output_1.get("w52_lwpr", 0) or 0)
        frgn_ratio = float(output_1.get("hts_frgn_ehrt", 0) or 0) # 외국인 지분율 올바른 키값 매핑
        
        # 크롤링을 통해 영업이익과 부채비율 가져오기
        operating_profit, debt_ratio = crawl_naver_financials(symbol)

        # DB 저장 (UPSERT)
        async with db.pool.acquire() as conn:
            await conn.execute(
                """INSERT INTO market_stock_fundamental 
                   (symbol, per, pbr, eps, market_cap, w52_high, w52_low, frgn_ratio, operating_profit, debt_ratio, updated_at)
                   VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, CURRENT_TIMESTAMP)
                   ON CONFLICT (symbol) DO UPDATE SET
                   per = EXCLUDED.per,
                   pbr = EXCLUDED.pbr,
                   eps = EXCLUDED.eps,
                   market_cap = EXCLUDED.market_cap,
                   w52_high = EXCLUDED.w52_high,
                   w52_low = EXCLUDED.w52_low,
                   frgn_ratio = EXCLUDED.frgn_ratio,
                   operating_profit = EXCLUDED.operating_profit,
                   debt_ratio = EXCLUDED.debt_ratio,
                   updated_at = CURRENT_TIMESTAMP""",
                symbol, per, pbr, eps, market_cap, w52_high, w52_low, frgn_ratio, operating_profit, debt_ratio
            )
        
        return {
            "symbol": symbol,
            "per": per,
            "pbr": pbr,
            "eps": eps,
            "market_cap": market_cap,
            "w52_high": w52_high,
            "w52_low": w52_low,
            "frgn_ratio": frgn_ratio,
            "operating_profit": operating_profit,
            "debt_ratio": debt_ratio
        }

    except Exception as e:
        print(f"KIS API error for {symbol}: {e}")
        fallback = await _get_fallback_overview(symbol)
        if fallback:
            return fallback
        raise HTTPException(status_code=500, detail=str(e))

async def fetch_stock_investors(symbol: str):
    access_token = get_kis_auth_token()
    if not access_token:
        return {"retail": 0, "institutional": 0, "foreign": 0, "error": "KIS token unavailable"}

    url = f"{KIS_BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-investor"
    headers = {
        "content-type": "application/json; charset=utf-8",
        "authorization": f"Bearer {access_token}",
        "appkey": KIS_AppKey,
        "appsecret": KIS_AppSecret,
        "tr_id": "FHKST01010900"
    }
    params = {
        "fid_cond_mrkt_div_code": "J",
        "fid_input_iscd": symbol
    }

    try:
        res = requests.get(url, headers=headers, params=params, timeout=5)
        data = res.json()
        
        if data.get("rt_cd") != "0":
            return {"error": data.get("msg1")}
            
        output = data.get("output", [])
        if not output:
            return {"retail": 0, "institutional": 0, "foreign": 0}
            
        today_data = output[0]
        
        return {
            "retail": float(today_data.get("prsn_ntby_qty", 0)),
            "institutional": float(today_data.get("orgn_ntby_qty", 0)),
            "foreign": float(today_data.get("frgn_ntby_qty", 0))
        }

    except Exception as e:
        print(f"Error fetching investors for {symbol}: {e}")
        return {"retail": 0, "institutional": 0, "foreign": 0, "error": str(e)}

async def fetch_stock_news(symbol_name: str):
    if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
        print("Naver API credentials missing")
        return []

    query = urllib.parse.quote(f"{symbol_name} 주가")
    url = f"https://openapi.naver.com/v1/search/news.json?query={query}&display=5&sort=date"
    
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }

    try:
        res = requests.get(url, headers=headers, timeout=5)
        res.raise_for_status()
        return res.json().get("items", [])
    except Exception as e:
        print(f"Error fetching news for {symbol_name}: {e}")
        return []
