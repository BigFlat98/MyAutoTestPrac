import requests
import random

def get_fear_and_greed_index():
    # CNN Private API Endpoint
    url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "https://edition.cnn.com/"
    }
    
    try:
        # 1. API Request with Timeout
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        
        # 2. Parse JSON
        data = response.json()
        
        # 3. Extract Score and Rating
        # Data structure: {'fear_and_greed': {'score': 65, 'rating': 'greed', ...}}
        fng_data = data.get('fear_and_greed', {})
        score = int(fng_data.get('score', 0))
        rating = fng_data.get('rating', 'Unknown')
        
        return {
            "score": score, 
            "status": "success",
            "rating": rating,
            "timestamp": fng_data.get('timestamp')
        }
            
    except requests.exceptions.RequestException as e:
        print(f"Network error crawling Fear & Greed: {e}")
    except (KeyError, ValueError, TypeError) as e:
        print(f"Data parsing error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    # Fallback: Return Mock Data on any error
    print("Returning fallback mock data.")
    mock_score = random.randint(30, 70)
    return {
        "score": mock_score, 
        "status": "error", 
        "rating": "Fear" if mock_score < 50 else "Greed",
        "timestamp": None
    }