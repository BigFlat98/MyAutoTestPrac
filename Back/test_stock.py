from controller.service.stock_service import get_stock_data
import os
from dotenv import load_dotenv

load_dotenv()
print(f"API Key present: {bool(os.getenv('TWELVE_DATA_API_KEY'))}")

print("Testing KOSPI fetch...")
result = get_stock_data("kospi")
print(result)
