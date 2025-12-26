import requests
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_signup():
    print("Testing Signup...")
    url = f"{BASE_URL}/auth/signup"
    data = {
        "login_id": "testuser",
        "login_pw": "password123",
        "nick_name": "Tester"
    }
    try:
        response = requests.post(url, json=data)
        if response.status_code == 201:
            print("Signup Successful:", response.json())
            return True
        elif response.status_code == 400 and "already exists" in response.text:
             print("User already exists, proceeding to login...")
             return True
        else:
            print(f"Signup Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Signup Error: {e}")
        return False

def test_login():
    print("\nTesting Login...")
    url = f"{BASE_URL}/auth/login"
    data = {
        "login_id": "testuser",
        "login_pw": "password123"
    }
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print("Login Successful:", response.json())
            return True
        else:
            print(f"Login Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Login Error: {e}")
        return False

if __name__ == "__main__":
    if test_signup():
        test_login()
