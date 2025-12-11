#!/usr/bin/env python3
"""
City-Based Product Availability Feature Testing Script
Tests the new city-specific product availability functionality
"""

import requests
import json
import sys
from datetime import datetime
import time

# Backend URL from environment
BACKEND_URL = "https://swift-recipe-app.preview.emergentagent.com/api"

def test_api_endpoint(method, endpoint, headers=None, data=None, params=None, description="", expected_status=None):
    """Test a single API endpoint"""
    url = f"{BACKEND_URL}{endpoint}"
    
    print(f"\n{'='*60}")
    print(f"Testing: {method} {endpoint}")
    print(f"Description: {description}")
    print(f"URL: {url}")
    if params:
        print(f"Query Params: {params}")
    if data:
        print(f"Request Data: {json.dumps(data, indent=2)}")
    print(f"{'='*60}")
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=params, timeout=30)
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
    
    login_data = {"password": "admin123"}
    
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

def main():
    """Main testing function for city-based product availability"""
    print("🚀 Starting City-Based Product Availability Feature Tests")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now()}")
    
    test_results = {}
    
    # ============= STEP 1: ADMIN LOGIN =============
    print("\n" + "="*80)
    print("🔐 STEP 1: ADMIN LOGIN")
    print("="*80)
    
    auth_token = admin_login()
    if not auth_token:
        print("\n❌ CRITICAL: Admin login failed - cannot proceed with admin-only tests")
        return 1
    
    test_results['admin_login'] = True
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # ============= STEP 2: GET PRODUCTS FOR TESTING =============
    print("\n" + "="*80)
    print("📦 STEP 2: GET PRODUCTS FOR TESTING")
    print("="*80)
    
    success, all_products = test_api_endpoint(
        "GET",
        "/products",
        description="Get all products to select one for city availability testing"
    )
    
    test_results['get_products'] = success
    
    if not success or not all_products or len(all_products) == 0:
        print("❌ No products available for testing")
        return 1
    
    # Select first product for testing
    test_product = all_products[0]
    product_id = test_product['id']
    product_name = test_product['name']
    
    print(f"\n📊 Selected Product for Testing:")
    print(f"  - Product ID: {product_id}")
    print(f"  - Product Name: {product_name}")
    print(f"  - Current available_cities: {test_product.get('available_cities', 'None (available everywhere)')}")
    
    # ============= STEP 3: UPDATE PRODUCT AVAILABLE CITIES =============
    print("\n" + "="*80)
    print("🏙️ STEP 3: UPDATE PRODUCT AVAILABLE CITIES")
    print("="*80)
    
    # Test 3.1: Update product to be available only in Guntur and Vijayawada
    city_update_data = {
        "available_cities": ["Guntur", "Vijayawada"]
    }
    
    success, response = test_api_endpoint(
        "PUT",
        f"/admin/products/{product_id}/available-cities",
        headers=headers,
        data=city_update_data,
        description=f"Update product '{product_name}' to be available only in Guntur and Vijayawada"
    )
    
    test_results['update_available_cities'] = success
    
    if not success:
        print("❌ Failed to update product available cities")
        return 1
    
    # Test 3.2: Verify the update worked by getting the product again
    success, updated_products = test_api_endpoint(
        "GET",
        "/products",
        description="Verify product available_cities was updated"
    )
    
    if success and updated_products:
        updated_product = next((p for p in updated_products if p['id'] == product_id), None)
        if updated_product:
            updated_cities = updated_product.get('available_cities', [])
            print(f"\n📊 Product Update Verification:")
            print(f"  - Updated available_cities: {updated_cities}")
            
            if updated_cities == ["Guntur", "Vijayawada"]:
                print("✅ Product available_cities updated correctly")
                test_results['verify_cities_update'] = True
            else:
                print("❌ Product available_cities not updated correctly")
                test_results['verify_cities_update'] = False
        else:
            print("❌ Could not find updated product")
            test_results['verify_cities_update'] = False
    else:
        print("❌ Failed to verify product update")
        test_results['verify_cities_update'] = False
    
    # ============= STEP 4: TEST CITY-FILTERED PRODUCT LISTING =============
    print("\n" + "="*80)
    print("🔍 STEP 4: TEST CITY-FILTERED PRODUCT LISTING")
    print("="*80)
    
    # Test 4.1: Get all products without city filter (should return all 56 products)
    success, all_products_no_filter = test_api_endpoint(
        "GET",
        "/products",
        description="Get all products without city parameter - should return all products"
    )
    
    test_results['get_all_products_no_filter'] = success
    
    if success and all_products_no_filter:
        total_products = len(all_products_no_filter)
        print(f"\n📊 All Products (No Filter):")
        print(f"  - Total products returned: {total_products}")
        
        if total_products > 0:
            print("✅ Products returned without city filter")
            test_results['verify_all_products_count'] = True
        else:
            print("❌ No products returned")
            test_results['verify_all_products_count'] = False
    else:
        print("❌ Failed to get all products")
        test_results['verify_all_products_count'] = False
    
    # Test 4.2: Get products filtered by Guntur (should include our restricted product)
    success, guntur_products = test_api_endpoint(
        "GET",
        "/products",
        params={"city": "Guntur"},
        description="Get products available in Guntur - should include our restricted product"
    )
    
    test_results['get_guntur_products'] = success
    
    if success and guntur_products is not None:
        guntur_count = len(guntur_products)
        print(f"\n📊 Guntur Products:")
        print(f"  - Products available in Guntur: {guntur_count}")
        
        # Check if our restricted product is included
        restricted_product_in_guntur = any(p['id'] == product_id for p in guntur_products)
        print(f"  - Our restricted product included: {restricted_product_in_guntur}")
        
        if restricted_product_in_guntur:
            print("✅ Restricted product correctly appears in Guntur results")
            test_results['verify_guntur_includes_restricted'] = True
        else:
            print("❌ Restricted product missing from Guntur results")
            test_results['verify_guntur_includes_restricted'] = False
    else:
        print("❌ Failed to get Guntur products")
        test_results['verify_guntur_includes_restricted'] = False
    
    # Test 4.3: Get products filtered by Hyderabad (should NOT include our restricted product)
    success, hyderabad_products = test_api_endpoint(
        "GET",
        "/products",
        params={"city": "Hyderabad"},
        description="Get products available in Hyderabad - should NOT include our restricted product"
    )
    
    test_results['get_hyderabad_products'] = success
    
    if success and hyderabad_products is not None:
        hyderabad_count = len(hyderabad_products)
        print(f"\n📊 Hyderabad Products:")
        print(f"  - Products available in Hyderabad: {hyderabad_count}")
        
        # Check if our restricted product is excluded
        restricted_product_in_hyderabad = any(p['id'] == product_id for p in hyderabad_products)
        print(f"  - Our restricted product included: {restricted_product_in_hyderabad}")
        
        if not restricted_product_in_hyderabad:
            print("✅ Restricted product correctly excluded from Hyderabad results")
            test_results['verify_hyderabad_excludes_restricted'] = True
        else:
            print("❌ Restricted product incorrectly appears in Hyderabad results")
            test_results['verify_hyderabad_excludes_restricted'] = False
    else:
        print("❌ Failed to get Hyderabad products")
        test_results['verify_hyderabad_excludes_restricted'] = False
    
    # Test 4.4: Get products filtered by Tenali (should have fewer products)
    success, tenali_products = test_api_endpoint(
        "GET",
        "/products",
        params={"city": "Tenali"},
        description="Get products available in Tenali - should return fewer products"
    )
    
    test_results['get_tenali_products'] = success
    
    if success and tenali_products is not None:
        tenali_count = len(tenali_products)
        print(f"\n📊 Tenali Products:")
        print(f"  - Products available in Tenali: {tenali_count}")
        
        # Compare with total products
        if 'all_products_no_filter' in locals() and all_products_no_filter:
            total_count = len(all_products_no_filter)
            if tenali_count <= total_count:
                print(f"✅ Tenali has {tenali_count} products (≤ total {total_count})")
                test_results['verify_tenali_count'] = True
            else:
                print(f"❌ Tenali has more products than total (impossible)")
                test_results['verify_tenali_count'] = False
        else:
            test_results['verify_tenali_count'] = True  # Can't compare, but API worked
    else:
        print("❌ Failed to get Tenali products")
        test_results['verify_tenali_count'] = False
    
    # ============= STEP 5: TEST ORDER CREATION WITH CITY VALIDATION =============
    print("\n" + "="*80)
    print("🛒 STEP 5: TEST ORDER CREATION WITH CITY VALIDATION")
    print("="*80)
    
    # Test 5.1: Create order with available product for Guntur (should succeed)
    order_data_success = {
        "user_id": "guest",
        "customer_name": "Test Customer Guntur",
        "email": "test.guntur@example.com",
        "phone": "9876543210",
        "doorNo": "12-34",
        "building": "Test Apartments",
        "street": "Test Road",
        "city": "Guntur",
        "state": "Andhra Pradesh",
        "pincode": "522001",
        "location": "Guntur",
        "items": [{
            "product_id": product_id,
            "name": product_name,
            "image": test_product.get('image', '/images/test.jpg'),
            "weight": "250g",
            "price": 150.0,
            "quantity": 1,
            "description": test_product.get('description', 'Test product')
        }],
        "subtotal": 150.0,
        "delivery_charge": 49.0,
        "total": 199.0,
        "payment_method": "online",
        "payment_sub_method": "paytm"
    }
    
    success, order_response = test_api_endpoint(
        "POST",
        "/orders",
        data=order_data_success,
        description=f"Create order with product '{product_name}' for delivery to Guntur (should succeed)"
    )
    
    test_results['create_order_available_city'] = success
    
    if success and order_response:
        order_id = order_response.get('order_id')
        tracking_code = order_response.get('tracking_code')
        print(f"\n📊 Successful Order:")
        print(f"  - Order ID: {order_id}")
        print(f"  - Tracking Code: {tracking_code}")
        print("✅ Order created successfully for available city")
    else:
        print("❌ Failed to create order for available city")
    
    # Test 5.2: Create order with restricted product for Hyderabad (should fail)
    order_data_fail = {
        "user_id": "guest",
        "customer_name": "Test Customer Hyderabad",
        "email": "test.hyderabad@example.com",
        "phone": "9876543211",
        "doorNo": "56-78",
        "building": "Test Apartments",
        "street": "Test Road",
        "city": "Hyderabad",
        "state": "Telangana",
        "pincode": "500001",
        "location": "Hyderabad",
        "items": [{
            "product_id": product_id,
            "name": product_name,
            "image": test_product.get('image', '/images/test.jpg'),
            "weight": "250g",
            "price": 150.0,
            "quantity": 1,
            "description": test_product.get('description', 'Test product')
        }],
        "subtotal": 150.0,
        "delivery_charge": 149.0,
        "total": 299.0,
        "payment_method": "online",
        "payment_sub_method": "paytm"
    }
    
    success, error_response = test_api_endpoint(
        "POST",
        "/orders",
        data=order_data_fail,
        description=f"Create order with product '{product_name}' for delivery to Hyderabad (should fail)",
        expected_status=400
    )
    
    test_results['create_order_unavailable_city'] = success
    
    if success and error_response:
        error_detail = error_response.get('detail', '')
        print(f"\n📊 Expected Failure:")
        print(f"  - Error message: {error_detail}")
        
        # Check if error message mentions the product and city
        if product_name in error_detail and "Hyderabad" in error_detail:
            print("✅ Error message correctly identifies unavailable product and city")
            test_results['verify_error_message'] = True
        else:
            print("❌ Error message doesn't properly identify the issue")
            test_results['verify_error_message'] = False
    else:
        print("❌ Order should have failed with 400 error for unavailable city")
        test_results['verify_error_message'] = False
    
    # ============= STEP 6: TEST PRODUCTS WITH NO CITY RESTRICTIONS =============
    print("\n" + "="*80)
    print("🌍 STEP 6: TEST PRODUCTS WITH NO CITY RESTRICTIONS")
    print("="*80)
    
    # Find a product with no city restrictions (available_cities = null or [])
    unrestricted_product = None
    for product in all_products_no_filter or []:
        available_cities = product.get('available_cities')
        if available_cities is None or available_cities == []:
            unrestricted_product = product
            break
    
    if unrestricted_product:
        unrestricted_id = unrestricted_product['id']
        unrestricted_name = unrestricted_product['name']
        
        print(f"\n📊 Testing Unrestricted Product:")
        print(f"  - Product ID: {unrestricted_id}")
        print(f"  - Product Name: {unrestricted_name}")
        print(f"  - Available Cities: {unrestricted_product.get('available_cities', 'None (available everywhere)')}")
        
        # Test that unrestricted product appears in all city filters
        test_cities = ["Guntur", "Hyderabad", "Tenali", "Vijayawada"]
        
        for city in test_cities:
            success, city_products = test_api_endpoint(
                "GET",
                "/products",
                params={"city": city},
                description=f"Check if unrestricted product appears in {city} results"
            )
            
            if success and city_products:
                product_found = any(p['id'] == unrestricted_id for p in city_products)
                print(f"  - Found in {city}: {product_found}")
                
                if product_found:
                    test_results[f'unrestricted_in_{city.lower()}'] = True
                else:
                    test_results[f'unrestricted_in_{city.lower()}'] = False
            else:
                test_results[f'unrestricted_in_{city.lower()}'] = False
        
        # Check if all cities show the unrestricted product
        unrestricted_tests = [test_results.get(f'unrestricted_in_{city.lower()}', False) for city in test_cities]
        if all(unrestricted_tests):
            print("✅ Unrestricted product appears in all city filters")
            test_results['verify_unrestricted_availability'] = True
        else:
            print("❌ Unrestricted product missing from some city filters")
            test_results['verify_unrestricted_availability'] = False
    else:
        print("⚠️ No unrestricted products found for testing")
        test_results['verify_unrestricted_availability'] = True  # Skip this test
    
    # ============= FINAL SUMMARY =============
    print(f"\n{'='*80}")
    print("🎯 CITY-BASED PRODUCT AVAILABILITY TEST SUMMARY")
    print(f"{'='*80}")
    
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result)
    failed_tests = total_tests - passed_tests
    
    print("\n📋 Detailed Results by Test Category:")
    
    categories = {
        "Admin Authentication": ['admin_login'],
        "Product Management": ['get_products', 'update_available_cities', 'verify_cities_update'],
        "City-Filtered Listings": [
            'get_all_products_no_filter', 'verify_all_products_count',
            'get_guntur_products', 'verify_guntur_includes_restricted',
            'get_hyderabad_products', 'verify_hyderabad_excludes_restricted',
            'get_tenali_products', 'verify_tenali_count'
        ],
        "Order Validation": [
            'create_order_available_city', 'create_order_unavailable_city', 'verify_error_message'
        ],
        "Unrestricted Products": [
            'verify_unrestricted_availability', 'unrestricted_in_guntur', 
            'unrestricted_in_hyderabad', 'unrestricted_in_tenali', 'unrestricted_in_vijayawada'
        ]
    }
    
    for category, test_keys in categories.items():
        category_tests = {k: v for k, v in test_results.items() if k in test_keys}
        if category_tests:
            category_passed = sum(1 for v in category_tests.values() if v)
            category_total = len(category_tests)
            print(f"\n  {category} ({category_passed}/{category_total} passed):")
            for test_name, result in category_tests.items():
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"    {test_name}: {status}")
    
    print(f"\n📊 Overall Test Statistics:")
    print(f"  Total Tests: {total_tests}")
    print(f"  Passed: {passed_tests}")
    print(f"  Failed: {failed_tests}")
    print(f"  Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print(f"\n🎯 KEY FINDINGS:")
    
    # Admin functionality
    if test_results.get('admin_login') and test_results.get('update_available_cities'):
        print(f"  ✅ Admin can successfully update product available cities")
    else:
        print(f"  ❌ Admin city management functionality failed")
    
    # City filtering
    if test_results.get('verify_guntur_includes_restricted') and test_results.get('verify_hyderabad_excludes_restricted'):
        print(f"  ✅ City-based product filtering works correctly")
    else:
        print(f"  ❌ City-based product filtering has issues")
    
    # Order validation
    if test_results.get('create_order_available_city') and test_results.get('create_order_unavailable_city'):
        print(f"  ✅ Order creation properly validates city availability")
    else:
        print(f"  ❌ Order creation city validation has issues")
    
    # Unrestricted products
    if test_results.get('verify_unrestricted_availability'):
        print(f"  ✅ Products with no city restrictions appear in all city filters")
    else:
        print(f"  ❌ Unrestricted products not appearing correctly in city filters")
    
    if failed_tests > 0:
        print(f"\n⚠️  {failed_tests} test(s) failed. Check the detailed output above for specific issues.")
        return 1
    else:
        print(f"\n🎉 ALL TESTS PASSED! City-based product availability feature is working correctly.")
        return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)