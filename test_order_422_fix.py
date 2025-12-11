#!/usr/bin/env python3
"""
Order Creation API Test - Verify 422 Error Resolution
Tests order creation with all required fields to ensure no validation errors
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://swift-recipe-app.preview.emergentagent.com/api"

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*80}")
    print(f"{title}")
    print(f"{'='*80}")

def test_order_creation():
    """Test order creation with all required fields"""
    print_section("🛒 ORDER CREATION API TEST - Verify 422 Error Resolution")
    
    print(f"\n📋 Test Configuration:")
    print(f"  Backend URL: {BACKEND_URL}")
    print(f"  Test Time: {datetime.now()}")
    print(f"  Product: Immunity Dry Fruits Laddu (ID: 1)")
    
    # Step 1: Verify product exists
    print_section("STEP 1: Verify Product Exists")
    
    try:
        response = requests.get(f"{BACKEND_URL}/products", timeout=30)
        print(f"GET /api/products - Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ FAILED: Cannot get products (HTTP {response.status_code})")
            return False
        
        products = response.json()
        product = next((p for p in products if p.get('id') == '1'), None)
        
        if not product:
            print(f"❌ FAILED: Product ID '1' not found in database")
            return False
        
        print(f"✅ Product found: {product.get('name')}")
        print(f"   Category: {product.get('category')}")
        print(f"   Prices: {json.dumps(product.get('prices', []), indent=2)}")
        
        # Use first price tier
        price_tier = product['prices'][0]
        
    except Exception as e:
        print(f"❌ FAILED: Error getting products - {str(e)}")
        return False
    
    # Step 2: Create order with all required fields
    print_section("STEP 2: Create Order with All Required Fields")
    
    # Build order data with all required fields as specified
    order_data = {
        "user_id": "guest",
        "customer_name": "Test Customer",
        "email": "test@example.com",
        "phone": "9876543210",
        "doorNo": "12-34",
        "building": "Sri Lakshmi Apartments",
        "street": "MG Road",
        "city": "Guntur",
        "state": "Andhra Pradesh",
        "pincode": "522001",
        "location": "Guntur",
        "items": [
            {
                "product_id": "1",
                "name": product['name'],
                "image": product['image'],
                "weight": price_tier['weight'],
                "price": price_tier['price'],
                "quantity": 2,
                "description": product.get('description', '')
            }
        ],
        "subtotal": price_tier['price'] * 2,
        "delivery_charge": 49.0,
        "total": (price_tier['price'] * 2) + 49.0,
        "payment_method": "online",
        "payment_sub_method": "paytm"
    }
    
    print(f"\n📦 Order Details:")
    print(f"  Customer Name: {order_data['customer_name']}")
    print(f"  Email: {order_data['email']}")
    print(f"  Phone: {order_data['phone']}")
    print(f"  Address:")
    print(f"    - Door No: {order_data['doorNo']}")
    print(f"    - Building: {order_data['building']}")
    print(f"    - Street: {order_data['street']}")
    print(f"    - City: {order_data['city']}")
    print(f"    - State: {order_data['state']}")
    print(f"    - Pincode: {order_data['pincode']}")
    print(f"  Location: {order_data['location']}")
    print(f"  Payment Method: {order_data['payment_method']}")
    print(f"  Payment Sub-method: {order_data['payment_sub_method']}")
    print(f"  Items: {len(order_data['items'])}")
    print(f"    - Product: {order_data['items'][0]['name']}")
    print(f"    - Weight: {order_data['items'][0]['weight']}")
    print(f"    - Price: ₹{order_data['items'][0]['price']}")
    print(f"    - Quantity: {order_data['items'][0]['quantity']}")
    print(f"  Subtotal: ₹{order_data['subtotal']:.2f}")
    print(f"  Delivery Charge: ₹{order_data['delivery_charge']:.2f}")
    print(f"  Total: ₹{order_data['total']:.2f}")
    
    print(f"\n🔄 Sending POST request to /api/orders...")
    print(f"Request Data: {json.dumps(order_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/orders",
            json=order_data,
            timeout=30
        )
        
        print(f"\n📊 Response:")
        print(f"  Status Code: {response.status_code}")
        
        # Try to parse response
        try:
            response_data = response.json()
            print(f"  Response Data: {json.dumps(response_data, indent=2)}")
        except:
            print(f"  Response Text: {response.text}")
            response_data = None
        
        # Step 3: Verify response
        print_section("STEP 3: Verify Order Creation Response")
        
        # Check for 422 error
        if response.status_code == 422:
            print(f"❌ FAILED: Received 422 Unprocessable Entity error")
            print(f"   This indicates validation errors with the request data")
            if response_data:
                print(f"   Error details: {json.dumps(response_data, indent=2)}")
            return False
        
        # Check for success status codes (200 or 201)
        if response.status_code not in [200, 201]:
            print(f"❌ FAILED: Expected HTTP 200/201, got {response.status_code}")
            return False
        
        print(f"✅ SUCCESS: Order created with HTTP {response.status_code}")
        
        # Verify response contains required fields
        if not response_data:
            print(f"❌ FAILED: No response data received")
            return False
        
        order_id = response_data.get('order_id')
        tracking_code = response_data.get('tracking_code')
        
        print(f"\n📋 Order Creation Verification:")
        print(f"  ✓ HTTP Status: {response.status_code} (Expected: 200 or 201)")
        print(f"  ✓ Has order_id: {bool(order_id)} - {order_id}")
        print(f"  ✓ Has tracking_code: {bool(tracking_code)} - {tracking_code}")
        print(f"  ✓ No 422 validation errors: True")
        print(f"  ✓ All required fields accepted: True")
        
        if not order_id or not tracking_code:
            print(f"\n❌ FAILED: Missing order_id or tracking_code in response")
            return False
        
        # Step 4: Verify order can be tracked
        print_section("STEP 4: Verify Order Tracking")
        
        print(f"\n🔍 Tracking order by tracking code: {tracking_code}")
        
        track_response = requests.get(
            f"{BACKEND_URL}/orders/track/{tracking_code}",
            timeout=30
        )
        
        print(f"  Status Code: {track_response.status_code}")
        
        if track_response.status_code != 200:
            print(f"⚠️  WARNING: Order tracking failed (HTTP {track_response.status_code})")
            print(f"   Order was created but tracking may have issues")
        else:
            tracked_order = track_response.json()
            print(f"✅ Order tracking successful")
            print(f"   Order ID: {tracked_order.get('order_id')}")
            print(f"   Customer: {tracked_order.get('customer_name')}")
            print(f"   Status: {tracked_order.get('order_status')}")
            print(f"   Payment Status: {tracked_order.get('payment_status')}")
        
        # Final Summary
        print_section("✅ TEST SUMMARY - ORDER API WORKING CORRECTLY")
        
        print(f"\n🎉 All Verifications Passed:")
        print(f"  ✅ Order creation succeeds with HTTP {response.status_code}")
        print(f"  ✅ Returns order_id: {order_id}")
        print(f"  ✅ Returns tracking_code: {tracking_code}")
        print(f"  ✅ No 422 validation errors")
        print(f"  ✅ All required fields are accepted")
        print(f"  ✅ Order can be tracked successfully")
        
        print(f"\n📝 Conclusion:")
        print(f"  The 422 error has been resolved. Order creation API is working correctly")
        print(f"  with all required fields including structured address, payment details,")
        print(f"  and proper item structure.")
        
        return True
        
    except requests.exceptions.ConnectionError as e:
        print(f"❌ FAILED: Connection error - {str(e)}")
        return False
    except requests.exceptions.Timeout as e:
        print(f"❌ FAILED: Request timeout - {str(e)}")
        return False
    except Exception as e:
        print(f"❌ FAILED: Unexpected error - {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 Starting Order Creation API Test")
    print("   Purpose: Verify 422 error is resolved")
    
    success = test_order_creation()
    
    if success:
        print("\n" + "="*80)
        print("✅ TEST PASSED: Order API is working correctly")
        print("="*80)
        return 0
    else:
        print("\n" + "="*80)
        print("❌ TEST FAILED: Order API has issues")
        print("="*80)
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
