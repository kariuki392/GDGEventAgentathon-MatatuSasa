import requests

BASE_URL = "http://127.0.0.1:8000"

def test_ussd(text=""):
    print(f"\n--- Testing USSD with text: '{text}' ---")
    data = {
        "sessionId": "test-session-123",
        "serviceCode": "*384*123#",
        "phoneNumber": "+254711123456",
        "text": text
    }
    try:
        response = requests.post(f"{BASE_URL}/ussd", data=data)
        print(f"Status Code: {response.status_code}")
        print("Response Body:")
        print(response.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Test 1: Initial dialing
    test_ussd("*8990*76#")
    
    # Test 2: User responds
    test_ussd("How do I get to Ruai from Kawangware?")
