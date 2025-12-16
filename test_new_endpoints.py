#!/usr/bin/env python3
"""
Backend API Testing Script for New Endpoints
Tests: Image Upload, Inventory Management, and Order Creation Validation
"""

import requests
import json
import sys
from datetime import datetime, timedelta, timezone
import uuid
import io
from PIL import Image

# Backend URL from environment
BACKEND_URL = "https://easy-whatsapp-send.preview.emergentagent.com/api"

def test_api_endpoint(method, endpoint, headers=None, data=None, files=None, description="", expected_status=None):
    """Test a single API endpoint"""
    url = f"{BACKEND_URL}{endpoint}"
    
    print(f"\n{'='*60}")
    print(f"Testing: {method} {endpoint}")
    print(f"Description: {description}")
    print(f"URL: {url}")
    if data and not files:
        print(f"Request Data: {json.dumps(data, indent=2)}")
    print(f"{'='*60}")
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        elif method.upper() == "POST":
            if files:
                response = requests.post(url, headers=headers, files=files, timeout=30)
            else:
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
            print(f"Response Text: {response.text[:500]}")
        
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

def register_and_login():
    """Register a test user and get auth token"""
    print("\n" + "="*80)
    print("🔐 AUTHENTICATION SETUP")
    print("="*80)
    
    # Generate unique email for test user
    test_email = f"testuser_{uuid.uuid4().hex[:8]}@ananthalakshmi.com"
    test_password = "TestUser@123"
    
    # Register user
    register_data = {
        "email": test_email,
        "password": test_password,
        "name": "Test User",
        "phone": "9876543210"
    }
    
    success, response_data = test_api_endpoint(
        "POST",
        "/auth/register",
        data=register_data,
        description="Register test user"
    )
    
    if success and response_data and "token" in response_data:
        token = response_data["token"]
        user_id = response_data.get("user", {}).get("id")
        print(f"✅ Successfully registered and got auth token")
        return token, user_id
    
    print("❌ Failed to get authentication token")
    return None, None

def create_test_image():
    """Create a test image in memory"""
    # Create a simple test image (100x100 red square)
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes

def main():
    """Main testing function"""
    print("🚀 Starting Backend API Tests - Image Upload, Inventory, Order Creation")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now()}")
    
    # Test results tracking
    test_results = {}
    
    # Step 1: Get authentication token
    auth_token, user_id = register_and_login()
    if not auth_token:
        print("\n❌ CRITICAL: Cannot proceed without authentication token")
        return 1
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # ============= IMAGE UPLOAD ENDPOINT TEST =============
    print("\n" + "="*80)
    print("📸 IMAGE UPLOAD ENDPOINT TEST")
    print("="*80)
    
    # Test 1: Upload image with valid file
    print("\nCreating test image...")
    test_image = create_test_image()
    files = {'file': ('test_image.png', test_image, 'image/png')}
    
    # Test the alias endpoint /api/upload-image
    success, response = test_api_endpoint(
        "POST",
        "/upload-image",
        headers=headers,
        files=files,
        description="Upload test image via /api/upload-image endpoint"
    )
    
    if success and response:
        image_url = response.get("url")
        if image_url:
            print(f"✅ Image uploaded successfully")
            print(f"   Image URL: {image_url}")
            test_results['upload_image_alias'] = True
            
            # Verify the image path format
            if image_url.startswith("/uploads/"):
                print(f"✅ Image URL has correct format")
                test_results['image_url_format'] = True
            else:
                print(f"❌ Image URL format incorrect: {image_url}")
                test_results['image_url_format'] = False
        else:
            print(f"❌ No URL in response")
            test_results['upload_image_alias'] = False
            test_results['image_url_format'] = False
    else:
        test_results['upload_image_alias'] = False
        test_results['image_url_format'] = False
    
    # ============= INVENTORY MANAGEMENT TESTS =============
    print("\n" + "="*80)
    print("📦 INVENTORY MANAGEMENT ENDPOINT TESTS")
    print("="*80)
    
    # Note: Testing with non-existent product (expecting 404)
    test_product_id = "test-product-1"
    
    # Test 2: GET stock status for non-existent product (should return 404)
    success, response = test_api_endpoint(
        "GET",
        f"/admin/products/{test_product_id}/stock-status",
        headers=headers,
        description="Get stock status for non-existent product (expecting 404)",
        expected_status=404
    )
    test_results['get_stock_status_404'] = success
    
    # Test 3: PUT inventory for non-existent product (should return 404)
    inventory_data = {"inventory_count": 100}
    success, response = test_api_endpoint(
        "PUT",
        f"/admin/products/{test_product_id}/inventory",
        headers=headers,
        data=inventory_data,
        description="Update inventory for non-existent product (expecting 404)",
        expected_status=404
    )
    test_results['put_inventory_404'] = success
    
    # Test 4: PUT stock status for non-existent product (should return 404)
    stock_status_data = {"out_of_stock": False}
    success, response = test_api_endpoint(
        "PUT",
        f"/admin/products/{test_product_id}/stock-status",
        headers=headers,
        data=stock_status_data,
        description="Update stock status for non-existent product (expecting 404)",
        expected_status=404
    )
    test_results['put_stock_status_404'] = success
    
    # ============= ORDER CREATION VALIDATION TESTS =============
    print("\n" + "="*80)
    print("🛒 ORDER CREATION VALIDATION TESTS")
    print("="*80)
    
    # Test 5: Create order with complete valid data
    valid_order_data = {
        "user_id": user_id,
        "customer_name": "Rajesh Kumar",
        "email": "rajesh.kumar@example.com",
        "phone": "9876543210",
        "address": "123 MG Road",
        "doorNo": "123",
        "building": "Lakshmi Apartments",
        "street": "MG Road",
        "city": "Hyderabad",
        "state": "Telangana",
        "pincode": "500001",
        "location": "Hyderabad",
        "items": [
            {
                "product_id": str(uuid.uuid4()),
                "name": "Mysore Pak",
                "image": "/images/mysore-pak.jpg",
                "weight": "500g",
                "price": 280.0,
                "quantity": 2,
                "description": "Traditional South Indian sweet"
            }
        ],
        "subtotal": 560.0,
        "delivery_charge": 49.0,
        "total": 609.0,
        "payment_method": "online",
        "payment_sub_method": "PhonePe"
    }
    
    success, response = test_api_endpoint(
        "POST",
        "/orders",
        headers=headers,
        data=valid_order_data,
        description="Create order with complete valid data"
    )
    
    if success and response:
        order_id = response.get("order_id")
        tracking_code = response.get("tracking_code")
        if order_id and tracking_code:
            print(f"✅ Order created successfully")
            print(f"   Order ID: {order_id}")
            print(f"   Tracking Code: {tracking_code}")
            test_results['create_order_valid'] = True
        else:
            print(f"❌ Order created but missing order_id or tracking_code")
            test_results['create_order_valid'] = False
    else:
        test_results['create_order_valid'] = False
    
    # Test 6: Create order with missing required fields (should fail with 422)
    print("\n" + "="*60)
    print("Testing order creation with missing required fields...")
    print("="*60)
    
    # Test missing customer_name
    invalid_order_1 = {
        "user_id": user_id,
        # "customer_name": "Missing",  # Missing field
        "email": "test@example.com",
        "phone": "9876543210",
        "address": "123 Test Street",
        "location": "Hyderabad",
        "items": [
            {
                "product_id": str(uuid.uuid4()),
                "name": "Test Product",
                "image": "/images/test.jpg",
                "weight": "500g",
                "price": 100.0,
                "quantity": 1
            }
        ],
        "subtotal": 100.0,
        "delivery_charge": 49.0,
        "total": 149.0,
        "payment_method": "online"
    }
    
    success, response = test_api_endpoint(
        "POST",
        "/orders",
        headers=headers,
        data=invalid_order_1,
        description="Create order with missing customer_name (expecting 422)",
        expected_status=422
    )
    
    if success:
        print(f"✅ Validation working: Missing customer_name rejected")
        if response and "detail" in response:
            print(f"   Validation error: {json.dumps(response['detail'], indent=2)}")
        test_results['order_validation_missing_name'] = True
    else:
        print(f"❌ Validation failed: Missing customer_name not caught")
        test_results['order_validation_missing_name'] = False
    
    # Test missing email
    invalid_order_2 = {
        "user_id": user_id,
        "customer_name": "Test User",
        # "email": "test@example.com",  # Missing field
        "phone": "9876543210",
        "address": "123 Test Street",
        "location": "Hyderabad",
        "items": [
            {
                "product_id": str(uuid.uuid4()),
                "name": "Test Product",
                "image": "/images/test.jpg",
                "weight": "500g",
                "price": 100.0,
                "quantity": 1
            }
        ],
        "subtotal": 100.0,
        "delivery_charge": 49.0,
        "total": 149.0,
        "payment_method": "online"
    }
    
    success, response = test_api_endpoint(
        "POST",
        "/orders",
        headers=headers,
        data=invalid_order_2,
        description="Create order with missing email (expecting 422)",
        expected_status=422
    )
    
    if success:
        print(f"✅ Validation working: Missing email rejected")
        if response and "detail" in response:
            print(f"   Validation error: {json.dumps(response['detail'], indent=2)}")
        test_results['order_validation_missing_email'] = True
    else:
        print(f"❌ Validation failed: Missing email not caught")
        test_results['order_validation_missing_email'] = False
    
    # Test missing items
    invalid_order_3 = {
        "user_id": user_id,
        "customer_name": "Test User",
        "email": "test@example.com",
        "phone": "9876543210",
        "address": "123 Test Street",
        "location": "Hyderabad",
        # "items": [],  # Missing field
        "subtotal": 100.0,
        "delivery_charge": 49.0,
        "total": 149.0,
        "payment_method": "online"
    }
    
    success, response = test_api_endpoint(
        "POST",
        "/orders",
        headers=headers,
        data=invalid_order_3,
        description="Create order with missing items (expecting 422)",
        expected_status=422
    )
    
    if success:
        print(f"✅ Validation working: Missing items rejected")
        if response and "detail" in response:
            print(f"   Validation error: {json.dumps(response['detail'], indent=2)}")
        test_results['order_validation_missing_items'] = True
    else:
        print(f"❌ Validation failed: Missing items not caught")
        test_results['order_validation_missing_items'] = False
    
    # Summary
    print(f"\n{'='*80}")
    print("🎯 TEST SUMMARY")
    print(f"{'='*80}")
    
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result)
    failed_tests = total_tests - passed_tests
    
    print("\n📋 Detailed Results:")
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    print(f"\n📊 Statistics:")
    print(f"  Total Tests: {total_tests}")
    print(f"  Passed: {passed_tests}")
    print(f"  Failed: {failed_tests}")
    print(f"  Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests > 0:
        print(f"\n⚠️  {failed_tests} test(s) failed. Check the detailed output above.")
        return 1
    else:
        print(f"\n🎉 All tests passed successfully!")
        return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
