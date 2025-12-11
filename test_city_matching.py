#!/usr/bin/env python3
"""Test script to debug city matching issue"""
import requests
import json

BASE_URL = "http://localhost:8001/api"

def test_order_creation(city, state):
    """Test order creation with given city and state"""
    print(f"\n{'='*80}")
    print(f"Testing order creation for: {city}, {state}")
    print('='*80)
    
    order_data = {
        "customer_name": "Test Customer",
        "email": "test@example.com",
        "phone": "9876543210",
        "doorNo": "123",
        "building": "Test Building",
        "street": "Test Street",
        "city": city,
        "state": state,
        "pincode": "522001",
        "items": [
            {
                "product_id": "product_1762952759",
                "name": "Immunity Dry Fruits Laddu",
                "price": 550,
                "quantity": 1,
                "weight": "1 kg",
                "image": "https://images.pexels.com/photos/8887055/pexels-photo-8887055.jpeg"
            }
        ],
        "subtotal": 550,
        "delivery_charge": 49,
        "total": 599,
        "payment_method": "razorpay",
        "payment_sub_method": "upi"
    }
    
    print(f"\n📤 Sending order with city='{city}', state='{state}'")
    
    response = requests.post(f"{BASE_URL}/orders", json=order_data)
    
    print(f"\n📥 Response Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Order created successfully!")
        print(f"   Order ID: {data.get('order_id')}")
        print(f"   Tracking Code: {data.get('tracking_code')}")
        
        # Check if it was treated as custom city request
        if 'message' in data:
            print(f"   Message: {data['message']}")
    else:
        print(f"❌ Order creation failed!")
        print(f"   Response: {response.text}")
    
    return response

def main():
    """Run tests for different city variations"""
    
    # Test 1: Guntur with exact case
    print("\n\n🧪 TEST 1: Guntur (exact case)")
    test_order_creation("Guntur", "Andhra Pradesh")
    
    # Test 2: Guntur with lowercase
    print("\n\n🧪 TEST 2: guntur (lowercase)")
    test_order_creation("guntur", "Andhra Pradesh")
    
    # Test 3: Guntur with uppercase
    print("\n\n🧪 TEST 3: GUNTUR (uppercase)")
    test_order_creation("GUNTUR", "Andhra Pradesh")
    
    # Test 4: Hyderabad with exact case
    print("\n\n🧪 TEST 4: Hyderabad (exact case)")
    test_order_creation("Hyderabad", "Telangana")
    
    # Test 5: Hyderabad with lowercase
    print("\n\n🧪 TEST 5: hyderabad (lowercase)")
    test_order_creation("hyderabad", "Telangana")
    
    print("\n\n" + "="*80)
    print("✅ All tests completed!")
    print("="*80)

if __name__ == "__main__":
    main()
