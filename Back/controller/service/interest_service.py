import os
import requests
import pandas as pd
from fredapi import Fred
from datetime import datetime, timedelta

class InterestRateService:
    def __init__(self):
        self.ecos_key = os.getenv("ECOS_DATA_API_KEY")
        self.fred_key = os.getenv("FRED_DATA_API_KEY")
        
        # Debugging Logs
        print(f"DEBUG: ECOS_KEY_LOADED={bool(self.ecos_key)}")
        print(f"DEBUG: FRED_KEY_LOADED={bool(self.fred_key)}")
        
        try:
            self.fred = Fred(api_key=self.fred_key)
        except Exception as e:
            print(f"ERROR: Failed to initialize Fred API: {e}")
            self.fred = None

    def get_korea_rate(self, start_date=None, end_date=None):
        """한국은행 기준금리 (ECOS)"""
        # 통계표: 722Y001 (한국은행 기준금리 및 여수신금리)
        # 주기: D (일) / 항목: 0101000 (한국은행 기준금리)
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365*10)).strftime("%Y%m%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
            
        url = f"http://ecos.bok.or.kr/api/StatisticSearch/{self.ecos_key}/json/kr/1/5000/722Y001/D/{start_date}/{end_date}/0101000"
        
        try:
            response = requests.get(url)
            data = response.json()
            if 'StatisticSearch' in data:
                rows = data['StatisticSearch']['row']
                df = pd.DataFrame(rows)
                # 날짜/값 정리
                df['date'] = pd.to_datetime(df['TIME'])
                df['kr_rate'] = df['DATA_VALUE'].astype(float)
                return df[['date', 'kr_rate']]
            else:
                print("ECOS Error:", data)
                return pd.DataFrame()
        except Exception as e:
            print(f"Failed to fetch KR Data: {e}")
            return pd.DataFrame()

    def get_us_rate(self):
        """미국 기준금리 (FRED - FEDFUNDS)"""
        if not self.fred:
            print("ERROR: Fred instance is None")
            return pd.DataFrame()

        try:
            # FRED는 pandas Series로 반환
            # FEDFUNDS: 실효 기금 금리 (시장 거래 평균, 변동 있음)
            # DFEDTARU: 연준 목표 금리 상단 (정책 금리, 0.25 단위)
            series = self.fred.get_series('DFEDTARU', observation_start=datetime.now() - timedelta(days=365*6))
            df = pd.DataFrame({'date': series.index, 'us_rate': series.values})
            return df
        except Exception as e:
            print(f"Failed to fetch US Data: {e}")
            return pd.DataFrame()

    def get_treasury_yield(self):
        """미 국채 10년물 수익률 (FRED - DGS10)"""
        if not self.fred:
            print("ERROR: Fred instance is None")
            return pd.DataFrame()

        try:
            series = self.fred.get_series('DGS10', observation_start=datetime.now() - timedelta(days=365*6))
            df = pd.DataFrame({'date': series.index, 'yield_rate': series.values})
            return df
        except Exception as e:
            print(f"Failed to fetch Treasury Yield: {e}")
            return pd.DataFrame()

    def get_comparison_data(self):
        # 1. 데이터 가져오기
        kr_df = self.get_korea_rate()
        us_df = self.get_us_rate()
        
        if kr_df.empty and us_df.empty:
            return {"dates": [], "kr": [], "us": []}

        # 2. 병합 (Outer Join으로 날짜 맞춤)
        merged = pd.merge(kr_df, us_df, on='date', how='outer')
        merged = merged.sort_values('date').ffill() # 결측치 앞 데이터로 채움
        
        # 3. JSON 변환 (최근 데이터만, 너무 많으면 차트 무거움)
        merged = merged.dropna() # 앞부분 빈 곳 제거
        
        return {
            "dates": merged['date'].dt.strftime('%Y-%m-%d').tolist(),
            "kr": merged['kr_rate'].tolist(),
            "us": merged['us_rate'].tolist()
        }


async def get_comparison_data_from_db():
    """DB에 저장된 한/미 기준금리 시계열을 반환합니다."""
    from database import db

    async with db.pool.acquire() as conn:
        rows = await conn.fetch(
            """SELECT trade_date, kr_rate, us_rate
               FROM market_interest_rate
               WHERE kr_rate IS NOT NULL AND us_rate IS NOT NULL
               ORDER BY trade_date"""
        )
    if not rows:
        return None
    return {
        "dates": [r["trade_date"].strftime("%Y-%m-%d") for r in rows],
        "kr":    [float(r["kr_rate"]) for r in rows],
        "us":    [float(r["us_rate"]) for r in rows]
    }

async def get_treasury_yield_from_db():
    """DB에 저장된 미 국채 10년물 수익률 시계열을 반환합니다."""
    from database import db

    async with db.pool.acquire() as conn:
        rows = await conn.fetch(
            """SELECT trade_date, yield_rate
               FROM market_treasury_yield
               WHERE yield_rate IS NOT NULL
               ORDER BY trade_date"""
        )
    if not rows:
        return None
    return {
        "dates": [r["trade_date"].strftime("%Y-%m-%d") for r in rows],
        "yields": [float(r["yield_rate"]) for r in rows]
    }