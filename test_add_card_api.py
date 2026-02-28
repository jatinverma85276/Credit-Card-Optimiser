"""
Test script for the /add_card API endpoint

This demonstrates how to use the new endpoint to add credit cards
by providing just the bank name and card name.
"""

import requests
import json

# API base URL (adjust if your server runs on a different port)
BASE_URL = "http://localhost:8000"

def test_add_card():
    """Test adding a credit card using bank name and card name"""
    
    # Example 1: HDFC Regalia Gold
    payload = {
        "bank_name": "HDFC",
        "card_name": "Regalia Gold",
        "user_id": "test_user_123"
    }
    
    print(f"🔍 Testing /add_card endpoint...")
    print(f"Request: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/add_card",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\n📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result['message']}")
            print(f"\n📋 Card Details:")
            print(json.dumps(result['card_details'], indent=2))
        else:
            print(f"❌ Error: {response.json()}")
    
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the server is running on port 8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_multiple_cards():
    """Test adding multiple cards"""
    
    test_cards = [
        {"bank_name": "ICICI", "card_name": "Amazon Pay", "user_id": "test_user_123"},
        {"bank_name": "SBI", "card_name": "Cashback", "user_id": "test_user_123"},
        {"bank_name": "American Express", "card_name": "Platinum Travel", "user_id": "test_user_123"},
    ]
    
    print("\n" + "="*60)
    print("Testing Multiple Cards")
    print("="*60)
    
    for card in test_cards:
        print(f"\n🔍 Adding: {card['bank_name']} {card['card_name']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/add_card",
                json=card,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {result['message']}")
            else:
                print(f"❌ Failed: {response.json().get('detail', 'Unknown error')}")
        
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    print("="*60)
    print("Credit Card Add API Test")
    print("="*60)
    
    # Test single card
    test_add_card()
    
    # Uncomment to test multiple cards
    # test_multiple_cards()
