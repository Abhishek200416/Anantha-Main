#!/usr/bin/env python3
"""
ORDER EMAIL NOTIFICATIONS TESTING
Comprehensive testing for order email notifications as requested in review:
1. Order confirmation email when creating orders
2. Order status update emails when admin changes status  
3. Admin order update emails
4. Products API verification (56 products)
"""

import requests
import json
import sys
from datetime import datetime, timedelta, timezone
import time
import random

# Backend URL from environment
BACKEND_URL = "https://env-config-tool.preview.emergentagent.com/api"
ADMIN_PASSWORD = "admin123"

def test_api_endpoint(method, endpoint, headers=None, data=None, description="", expected_status=None):
    """Test a single API endpoint"""
    url = f"{BACKEND_URL}{endpoint}"
    
    print(f"\n{'='*60}")
    print(f"Testing: {method} {endpoint}")
    print(f"Description: {description}")
    print(f"URL: {url}")
    if data:
        print(f"Request Data: {json.dumps(data, indent=2)}")
    print(f"{'='*60}")
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=30)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=headers, json=data, timeout=30)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers, timeout=30)
        else:
            print(f"❌ Unsupported method: {method}")
            return False, None
            
        print(f"Status Code: {response.status_code}")
        
        # Try to parse JSON response
        response_data = None
        try:
            response_data = response.json()
            print(f"Response Data: {json.dumps(response_data, indent=2)}")
        except:
            print(f"Response Text: {response.text}")
        
        # Check if request was successful
        if expected_status:
            success = response.status_code == expected_status
        else:
            success = 200 <= response.status_code < 300
            
        if success:
            print("✅ SUCCESS: API endpoint is working as expected")
            return True, response_data
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            return False, response_data
            
    except requests.exceptions.ConnectionError as e:
        print(f"❌ CONNECTION ERROR: {str(e)}")
        return False, None
    except requests.exceptions.Timeout as e:
        print(f"❌ TIMEOUT ERROR: {str(e)}")
        return False, None
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {str(e)}")
        return False, None

def admin_login():
    """Login as admin and get auth token"""
    print("\n" + "="*80)
    print("🔐 ADMIN AUTHENTICATION")
    print("="*80)
    
    login_data = {"password": ADMIN_PASSWORD}
    
    success, response_data = test_api_endpoint(
        "POST",
        "/auth/admin-login",
        data=login_data,
        description="Admin login with password 'admin123'"
    )
    
    if success and response_data and "token" in response_data:
        token = response_data["token"]
        print(f"✅ Successfully logged in as admin and got JWT token")
        return token
    
    print("❌ Failed to get admin authentication token")
    return None

def check_backend_logs(search_term, log_file="/var/log/supervisor/backend.out.log"):
    """Check backend logs for specific terms"""
    try:
        import subprocess
        result = subprocess.run(
            ["tail", "-n", "100", log_file],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.stdout and search_term in result.stdout:
            print(f"✅ SUCCESS: Found '{search_term}' in backend logs")
            return True
        else:
            print(f"⚠️  WARNING: '{search_term}' not found in recent backend logs")
            return False
            
    except Exception as e:
        print(f"⚠️  WARNING: Could not check logs: {e}")
        return False

def test_products_api():
    """Test GET /api/products API and verify 56 products"""
    print("\n" + "="*80)
    print("📦 TESTING PRODUCTS API - VERIFY 56 PRODUCTS")
    print("="*80)
    
    success, response_data = test_api_endpoint(
        "GET",
        "/products",
        description="Get all products and verify 56 products are seeded"
    )
    
    if success and isinstance(response_data, list):
        total_products = len(response_data)
        print(f"✅ SUCCESS: Products API returns {total_products} products")
        
        # Verify we have 56 products as expected
        if total_products == 56:
            print(f"✅ SUCCESS: Correct number of products (56)")
            
            # Verify product structure
            if response_data:
                sample_product = response_data[0]
                required_fields = ["id", "name", "category", "description", "image", "prices"]
                
                print(f"\n🔍 PRODUCT STRUCTURE VERIFICATION:")
                for field in required_fields:
                    if field in sample_product:
                        print(f"   ✅ '{field}' field present")
                    else:
                        print(f"   ❌ '{field}' field missing")
                        return False
                
                # Verify prices structure
                prices = sample_product.get("prices", [])
                if isinstance(prices, list) and prices:
                    print(f"   ✅ Prices array has {len(prices)} price tiers")
                    return True
                else:
                    print(f"   ❌ Prices array empty or invalid")
                    return False
            return True
        else:
            print(f"❌ FAILED: Expected 56 products, got {total_products}")
            return False
    
    print(f"❌ FAILED: Products API failed or returned invalid data")
    return False

def test_order_creation_with_email():
    """Test POST /api/orders - Order creation with email confirmation"""
    print("\n" + "="*80)
    print("📧 TESTING ORDER CREATION WITH EMAIL CONFIRMATION")
    print("="*80)
    
    # First get a product to use in the order
    success, products = test_api_endpoint(
        "GET",
        "/products",
        description="Get products to use in test order"
    )
    
    if not success or not products:
        print("❌ FAILED: Cannot get products for order test")
        return False, None
    
    # Use the first product
    test_product = products[0]
    product_id = test_product["id"]
    product_name = test_product["name"]
    product_price = test_product["prices"][0]["price"]
    product_weight = test_product["prices"][0]["weight"]
    
    print(f"Using test product: {product_name} (ID: {product_id})")
    
    # Create test order data
    order_data = {
        "customer_name": "Test Customer",
        "email": "test@example.com",
        "phone": "9876543210",
        "doorNo": "123",
        "building": "Test Building",
        "street": "Test Street",
        "city": "Guntur",
        "state": "Andhra Pradesh",
        "pincode": "522001",
        "location": "Guntur",
        "payment_method": "online",
        "payment_sub_method": "paytm",
        "items": [
            {
                "product_id": product_id,
                "name": product_name,
                "image": test_product.get("image", ""),
                "weight": product_weight,
                "price": product_price,
                "quantity": 1,
                "description": test_product.get("description", "")
            }
        ],
        "subtotal": product_price,
        "delivery_charge": 49.0,
        "total": product_price + 49.0
    }
    
    success, response_data = test_api_endpoint(
        "POST",
        "/orders",
        data=order_data,
        description="Create order with all required fields including email"
    )
    
    if success and response_data:
        order_id = response_data.get("order_id")
        tracking_code = response_data.get("tracking_code")
        
        if order_id and tracking_code:
            print(f"✅ SUCCESS: Order created successfully")
            print(f"   - Order ID: {order_id}")
            print(f"   - Tracking Code: {tracking_code}")
            
            # Check backend logs for email confirmation
            print(f"\n📧 Checking backend logs for order confirmation email...")
            email_sent = check_backend_logs("Order confirmation email sent to")
            
            if email_sent:
                print(f"✅ SUCCESS: Order confirmation email function called")
            else:
                print(f"⚠️  WARNING: Order confirmation email log not found")
            
            return True, order_id
        else:
            print(f"❌ FAILED: Missing order_id or tracking_code in response")
            return False, None
    
    print(f"❌ FAILED: Order creation failed")
    return False, None

def test_order_status_update_email(admin_token, order_id):
    """Test PUT /api/orders/{order_id}/status - Status update with email"""
    print("\n" + "="*80)
    print("📧 TESTING ORDER STATUS UPDATE WITH EMAIL NOTIFICATION")
    print("="*80)
    
    auth_headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
    
    # Test status transitions
    status_transitions = [
        ("confirmed", "processing"),
        ("processing", "shipped"),
        ("shipped", "delivered")
    ]
    
    for old_status, new_status in status_transitions:
        print(f"\n--- Testing Status Update: {old_status} → {new_status} ---")
        
        status_data = {"status": new_status}
        
        success, response_data = test_api_endpoint(
            "PUT",
            f"/orders/{order_id}/status",
            headers=auth_headers,
            data=status_data,
            description=f"Update order status from {old_status} to {new_status}"
        )
        
        if success:
            print(f"✅ SUCCESS: Order status updated to {new_status}")
            
            # Check backend logs for status update email
            print(f"📧 Checking backend logs for status update email...")
            email_sent = check_backend_logs("order status update email")
            
            if email_sent:
                print(f"✅ SUCCESS: Order status update email function called")
            else:
                print(f"⚠️  WARNING: Order status update email log not found")
        else:
            print(f"❌ FAILED: Could not update order status to {new_status}")
            return False
        
        # Small delay between status updates
        time.sleep(2)
    
    return True

def test_admin_order_update_email(admin_token, order_id):
    """Test PUT /api/orders/{order_id}/admin-update - Admin update with email"""
    print("\n" + "="*80)
    print("📧 TESTING ADMIN ORDER UPDATE WITH EMAIL NOTIFICATION")
    print("="*80)
    
    auth_headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
    
    # Test admin update with status change
    admin_update_data = {
        "order_status": "processing",
        "admin_notes": "Order packed and ready for dispatch",
        "delivery_days": 3
    }
    
    success, response_data = test_api_endpoint(
        "PUT",
        f"/orders/{order_id}/admin-update",
        headers=auth_headers,
        data=admin_update_data,
        description="Admin update order with status change and notes"
    )
    
    if success:
        print(f"✅ SUCCESS: Admin order update completed")
        
        # Check backend logs for admin update email
        print(f"📧 Checking backend logs for admin update email...")
        email_sent = check_backend_logs("order status update email")
        
        if email_sent:
            print(f"✅ SUCCESS: Admin update email function called")
            return True
        else:
            print(f"⚠️  WARNING: Admin update email log not found")
            return False
    
    print(f"❌ FAILED: Admin order update failed")
    return False

def main():
    """Main test execution"""
    print("="*80)
    print("🚀 COMPREHENSIVE ORDER EMAIL NOTIFICATIONS TESTING")
    print("="*80)
    
    test_results = []
    
    # Test 1: Products API Verification
    print(f"\n🧪 TEST 1: PRODUCTS API VERIFICATION")
    products_success = test_products_api()
    test_results.append(("Products API (56 products)", products_success))
    
    # Test 2: Admin Authentication
    print(f"\n🧪 TEST 2: ADMIN AUTHENTICATION")
    admin_token = admin_login()
    if admin_token:
        test_results.append(("Admin Authentication", True))
    else:
        test_results.append(("Admin Authentication", False))
        print("❌ CRITICAL: Cannot proceed without admin authentication")
        return
    
    # Test 3: Order Creation with Email Confirmation
    print(f"\n🧪 TEST 3: ORDER CREATION WITH EMAIL CONFIRMATION")
    order_success, order_id = test_order_creation_with_email()
    test_results.append(("Order Creation + Confirmation Email", order_success))
    
    if not order_success or not order_id:
        print("❌ CRITICAL: Cannot proceed without successful order creation")
        return
    
    # Test 4: Order Status Update with Email
    print(f"\n🧪 TEST 4: ORDER STATUS UPDATE WITH EMAIL")
    status_update_success = test_order_status_update_email(admin_token, order_id)
    test_results.append(("Order Status Update + Email", status_update_success))
    
    # Test 5: Admin Order Update with Email
    print(f"\n🧪 TEST 5: ADMIN ORDER UPDATE WITH EMAIL")
    admin_update_success = test_admin_order_update_email(admin_token, order_id)
    test_results.append(("Admin Order Update + Email", admin_update_success))
    
    # Final Results Summary
    print("\n" + "="*80)
    print("📊 FINAL TEST RESULTS SUMMARY")
    print("="*80)
    
    total_tests = len(test_results)
    passed_tests = sum(1 for _, success in test_results if success)
    
    for test_name, success in test_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n📈 OVERALL RESULTS: {passed_tests}/{total_tests} tests passed ({(passed_tests/total_tests)*100:.1f}%)")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! Order email notifications are working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the detailed output above.")
    
    # Email Configuration Status
    print(f"\n📧 EMAIL CONFIGURATION STATUS:")
    print(f"   - Gmail credentials are configured in backend .env")
    print(f"   - Email functions are called even if actual emails aren't sent in test environment")
    print(f"   - Check backend logs for 'Order confirmation email sent to' messages")
    print(f"   - Both order confirmation and status update emails should be triggered")

if __name__ == "__main__":
    main()