import os
import requests
import pandas as pd
from datetime import datetime, timedelta

class ExchangeRateService:
    def __init__(self):
        self.ecos_key = os.getenv("ECOS_DATA_API_KEY")
        
    def get_usd_krw_rate(self, start_date=None, end_date=None):
        """원/달러 환율 (ECOS)"""
        # 통계표: 731Y001 (원/달러 환율)
        # 주기: D (일) / 항목: 0000001 (원/달러)
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365*10)).strftime("%Y%m%d") # 10년치
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
            
        url = f"http://ecos.bok.or.kr/api/StatisticSearch/{self.ecos_key}/json/kr/1/5000/731Y001/D/{start_date}/{end_date}/0000001"
        
        try:
            response = requests.get(url)
            data = response.json()
            if 'StatisticSearch' in data:
                rows = data['StatisticSearch']['row']
                df = pd.DataFrame(rows)
                # 날짜/값 정리
                df['date'] = pd.to_datetime(df['TIME'])
                df['rate'] = df['DATA_VALUE'].astype(float)
                
                # 차트용 데이터 반환
                return {
                    "dates": df['date'].dt.strftime('%Y-%m-%d').tolist(),
                    "rates": df['rate'].tolist()
                }
            else:
                print("ECOS Error (Exchange):", data)
                return {"dates": [], "rates": []}
        except Exception as e:
            print(f"Failed to fetch Exchange Data: {e}")
            return {"dates": [], "rates": []}
