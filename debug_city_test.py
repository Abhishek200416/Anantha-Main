#!/usr/bin/env python3
"""
Debug City Detection Issue
"""

import requests
import json

BACKEND_URL = "https://recipe-store-1.preview.emergentagent.com/api"

def test_city_in_locations():
    """Test if Hyderabad is in locations"""
    response = requests.get(f"{BACKEND_URL}/locations")
    if response.status_code == 200:
        locations = response.json()
        hyderabad = [loc for loc in locations if loc['name'] == 'Hyderabad']
        print(f"Hyderabad in locations API: {len(hyderabad) > 0}")
        if hyderabad:
            print(f"Hyderabad data: {hyderabad[0]}")
        return len(hyderabad) > 0
    return False

def test_simple_order():
    """Test a simple order with Guntur (known working city)"""
    order_data = {
        "customer_name": "Test User",
        "email": "test@example.com",
        "phone": "9876543210",
        "city": "Guntur",
        "state": "Andhra Pradesh",
        "doorNo": "1-1",
        "building": "Test Building",
        "street": "Test Street",
        "pincode": "522001",
        "payment_method": "online",
        "payment_sub_method": "Paytm",
        "items": [
            {
                "product_id": "product_1762765616",
                "name": "Test Product",
                "image": "test.jpg",
                "weight": "1 kg",
                "price": 100.0,
                "quantity": 1,
                "description": "Test product"
            }
        ],
        "subtotal": 100.0,
        "delivery_charge": 49.0,
        "total": 149.0
    }
    
    response = requests.post(f"{BACKEND_URL}/orders", json=order_data)
    print(f"Guntur order status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Payment status: {data.get('payment_status', 'N/A')}")
        print(f"Custom city request: {data.get('custom_city_request', 'N/A')}")
        return data.get('order_id')
    else:
        print(f"Error: {response.text}")
    return None

if __name__ == "__main__":
    print("=== DEBUGGING CITY DETECTION ===")
    
    print("\n1. Testing Hyderabad in locations API:")
    test_city_in_locations()
    
    print("\n2. Testing Guntur order (should work):")
    guntur_order = test_simple_order()
    
    print(f"\nGuntur order ID: {guntur_order}")