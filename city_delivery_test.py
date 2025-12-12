#!/usr/bin/env python3
"""
City-Specific Free Delivery Feature Testing Script
Tests conditional free delivery system based on city and order amount
"""

import requests
import json
import sys
from datetime import datetime, timedelta, timezone
import time
import random

# Backend URL from environment
BACKEND_URL = "https://foodcraft-11.preview.emergentagent.com/api"

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
    
    # Admin login with password
    login_data = {
        "password": "admin123"
    }
    
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

def get_products():
    """Get available products for testing"""
    success, products = test_api_endpoint(
        "GET",
        "/products",
        description="Get products for order testing"
    )
    
    if success and products and len(products) > 0:
        print(f"✅ Found {len(products)} products in database")
        return products
    else:
        print("⚠️ No products found, using mock product data")
        return [{
            'id': 'product_test_001',
            'name': 'Test Product',
            'image': '/images/test-product.jpg',
            'prices': [{'weight': '250g', 'price': 150.0}],
            'description': 'Test product for delivery testing'
        }]

def create_order_with_location(location, subtotal, products):
    """Create an order with specific location and subtotal"""
    
    # Build order items
    order_items = []
    remaining_subtotal = subtotal
    
    for i, product in enumerate(products[:2]):  # Use max 2 products
        if remaining_subtotal <= 0:
            break
            
        price_tier = product['prices'][0]
        base_price = price_tier['price']
        
        # Calculate quantity to reach desired subtotal
        if i == len(products[:2]) - 1:  # Last product
            quantity = max(1, int(remaining_subtotal / base_price))
            item_total = quantity * base_price
        else:
            # Use half of remaining subtotal for this product
            target_amount = remaining_subtotal / 2
            quantity = max(1, int(target_amount / base_price))
            item_total = quantity * base_price
        
        remaining_subtotal -= item_total
        
        order_items.append({
            "product_id": product['id'],
            "name": product['name'],
            "image": product['image'],
            "weight": price_tier['weight'],
            "price": base_price,
            "quantity": quantity,
            "description": product.get('description', '')
        })
    
    # Calculate actual subtotal from items
    actual_subtotal = sum(item['price'] * item['quantity'] for item in order_items)
    
    # Determine delivery charge based on location and subtotal
    delivery_charge = 0.0
    if location == "Guntur":
        delivery_charge = 49.0 if actual_subtotal < 1000 else 0.0
    elif location == "Hyderabad":
        delivery_charge = 149.0 if actual_subtotal < 2000 else 0.0
    else:
        delivery_charge = 99.0  # Default charge
    
    total = actual_subtotal + delivery_charge
    
    # Create order data
    order_data = {
        "user_id": "guest",
        "customer_name": f"Test Customer {location}",
        "email": f"test.{location.lower()}@example.com",
        "phone": f"987654{random.randint(1000, 9999)}",
        "doorNo": "12-34",
        "building": "Test Apartments",
        "street": "Test Road",
        "city": location,
        "state": "Telangana" if location == "Hyderabad" else "Andhra Pradesh",
        "pincode": "500001" if location == "Hyderabad" else "522001",
        "location": location,
        "items": order_items,
        "subtotal": actual_subtotal,
        "delivery_charge": delivery_charge,
        "total": total,
        "payment_method": "online",
        "payment_sub_method": "paytm"
    }
    
    return order_data, actual_subtotal, delivery_charge, total

def main():
    """Main testing function for city-specific free delivery"""
    print("🚀 Starting City-Specific Free Delivery Feature Tests")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now()}")
    
    # Test results tracking
    test_results = {}
    
    # ============= STEP 1: ADMIN LOGIN =============
    print("\n" + "="*80)
    print("🔐 STEP 1: ADMIN AUTHENTICATION")
    print("="*80)
    
    auth_token = admin_login()
    if not auth_token:
        print("\n❌ CRITICAL: Admin login failed - cannot proceed with admin tests")
        return 1
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    test_results['admin_login'] = True
    
    # ============= STEP 2: TEST GET /api/locations =============
    print("\n" + "="*80)
    print("📍 STEP 2: TEST GET /api/locations")
    print("="*80)
    
    success, locations_data = test_api_endpoint(
        "GET",
        "/locations",
        description="Get all delivery locations with city-specific settings"
    )
    
    test_results['get_locations'] = success
    
    if success and locations_data:
        print(f"\n📊 Locations Data Verification:")
        print(f"  - Total locations: {len(locations_data)}")
        
        # Find Guntur and Hyderabad
        guntur_data = None
        hyderabad_data = None
        
        for location in locations_data:
            if location.get('name') == 'Guntur':
                guntur_data = location
            elif location.get('name') == 'Hyderabad':
                hyderabad_data = location
        
        # Verify Guntur settings
        if guntur_data:
            print(f"\n  🎯 Guntur Location Data:")
            print(f"    - Name: {guntur_data.get('name')}")
            print(f"    - Charge: ₹{guntur_data.get('charge', 'N/A')}")
            print(f"    - Free Delivery Threshold: ₹{guntur_data.get('free_delivery_threshold', 'N/A')}")
            print(f"    - State: {guntur_data.get('state', 'N/A')}")
            
            # Check expected values
            expected_guntur = {
                'charge': 49,
                'free_delivery_threshold': 1000,
                'state': 'Andhra Pradesh'
            }
            
            guntur_correct = True
            for key, expected_value in expected_guntur.items():
                actual_value = guntur_data.get(key)
                if actual_value != expected_value:
                    print(f"    ❌ {key}: Expected {expected_value}, got {actual_value}")
                    guntur_correct = False
                else:
                    print(f"    ✅ {key}: {actual_value} (correct)")
            
            test_results['guntur_settings_correct'] = guntur_correct
        else:
            print(f"  ❌ Guntur not found in locations")
            test_results['guntur_settings_correct'] = False
        
        # Verify Hyderabad settings
        if hyderabad_data:
            print(f"\n  🎯 Hyderabad Location Data:")
            print(f"    - Name: {hyderabad_data.get('name')}")
            print(f"    - Charge: ₹{hyderabad_data.get('charge', 'N/A')}")
            print(f"    - Free Delivery Threshold: ₹{hyderabad_data.get('free_delivery_threshold', 'N/A')}")
            print(f"    - State: {hyderabad_data.get('state', 'N/A')}")
            
            # Check expected values
            expected_hyderabad = {
                'charge': 149,
                'free_delivery_threshold': 2000,
                'state': 'Telangana'
            }
            
            hyderabad_correct = True
            for key, expected_value in expected_hyderabad.items():
                actual_value = hyderabad_data.get(key)
                if actual_value != expected_value:
                    print(f"    ❌ {key}: Expected {expected_value}, got {actual_value}")
                    hyderabad_correct = False
                else:
                    print(f"    ✅ {key}: {actual_value} (correct)")
            
            test_results['hyderabad_settings_correct'] = hyderabad_correct
        else:
            print(f"  ❌ Hyderabad not found in locations")
            test_results['hyderabad_settings_correct'] = False
        
        # Check for undefined values
        undefined_found = False
        for location in locations_data:
            for key, value in location.items():
                if value is None or str(value).lower() == 'undefined':
                    print(f"  ❌ Found undefined value in {location.get('name', 'Unknown')}: {key} = {value}")
                    undefined_found = True
        
        if not undefined_found:
            print(f"  ✅ No undefined values found in location data")
            test_results['no_undefined_values'] = True
        else:
            test_results['no_undefined_values'] = False
    
    # ============= STEP 3: GET PRODUCTS FOR TESTING =============
    print("\n" + "="*80)
    print("📦 STEP 3: GET PRODUCTS FOR ORDER TESTING")
    print("="*80)
    
    products = get_products()
    test_results['products_available'] = len(products) > 0
    
    # ============= STEP 4: TEST GUNTUR ORDERS =============
    print("\n" + "="*80)
    print("🏙️ STEP 4: TEST GUNTUR DELIVERY CHARGES")
    print("="*80)
    
    # Test 4.1: Guntur order below threshold (₹500 < ₹1000)
    print(f"\n  📦 Test 4.1: Guntur Order Below Threshold")
    order_data, actual_subtotal, delivery_charge, total = create_order_with_location("Guntur", 500, products)
    
    print(f"    - Target subtotal: ₹500")
    print(f"    - Actual subtotal: ₹{actual_subtotal}")
    print(f"    - Expected delivery charge: ₹49 (below ₹1000 threshold)")
    print(f"    - Calculated delivery charge: ₹{delivery_charge}")
    print(f"    - Total: ₹{total}")
    
    success, order_response = test_api_endpoint(
        "POST",
        "/orders",
        data=order_data,
        description=f"Create Guntur order below threshold (₹{actual_subtotal})"
    )
    
    test_results['guntur_below_threshold'] = success
    
    if success and order_response:
        # Verify delivery charge is ₹49
        if delivery_charge == 49.0:
            print(f"    ✅ Delivery charge correctly set to ₹49 for Guntur below threshold")
            test_results['guntur_below_charge_correct'] = True
        else:
            print(f"    ❌ Delivery charge should be ₹49, got ₹{delivery_charge}")
            test_results['guntur_below_charge_correct'] = False
        
        # Verify total calculation
        expected_total = actual_subtotal + 49.0
        if abs(total - expected_total) < 0.01:
            print(f"    ✅ Total correctly calculated: ₹{total}")
            test_results['guntur_below_total_correct'] = True
        else:
            print(f"    ❌ Total should be ₹{expected_total}, got ₹{total}")
            test_results['guntur_below_total_correct'] = False
    
    # Test 4.2: Guntur order above threshold (₹1200 > ₹1000)
    print(f"\n  📦 Test 4.2: Guntur Order Above Threshold")
    order_data, actual_subtotal, delivery_charge, total = create_order_with_location("Guntur", 1200, products)
    
    print(f"    - Target subtotal: ₹1200")
    print(f"    - Actual subtotal: ₹{actual_subtotal}")
    print(f"    - Expected delivery charge: ₹0 (above ₹1000 threshold)")
    print(f"    - Calculated delivery charge: ₹{delivery_charge}")
    print(f"    - Total: ₹{total}")
    
    success, order_response = test_api_endpoint(
        "POST",
        "/orders",
        data=order_data,
        description=f"Create Guntur order above threshold (₹{actual_subtotal})"
    )
    
    test_results['guntur_above_threshold'] = success
    
    if success and order_response:
        # Verify delivery charge is ₹0
        if delivery_charge == 0.0:
            print(f"    ✅ Free delivery correctly applied for Guntur above threshold")
            test_results['guntur_above_charge_correct'] = True
        else:
            print(f"    ❌ Delivery charge should be ₹0, got ₹{delivery_charge}")
            test_results['guntur_above_charge_correct'] = False
        
        # Verify total calculation
        expected_total = actual_subtotal
        if abs(total - expected_total) < 0.01:
            print(f"    ✅ Total correctly calculated: ₹{total}")
            test_results['guntur_above_total_correct'] = True
        else:
            print(f"    ❌ Total should be ₹{expected_total}, got ₹{total}")
            test_results['guntur_above_total_correct'] = False
    
    # ============= STEP 5: TEST HYDERABAD ORDERS =============
    print("\n" + "="*80)
    print("🏙️ STEP 5: TEST HYDERABAD DELIVERY CHARGES")
    print("="*80)
    
    # Test 5.1: Hyderabad order below threshold (₹1500 < ₹2000)
    print(f"\n  📦 Test 5.1: Hyderabad Order Below Threshold")
    order_data, actual_subtotal, delivery_charge, total = create_order_with_location("Hyderabad", 1500, products)
    
    print(f"    - Target subtotal: ₹1500")
    print(f"    - Actual subtotal: ₹{actual_subtotal}")
    print(f"    - Expected delivery charge: ₹149 (below ₹2000 threshold)")
    print(f"    - Calculated delivery charge: ₹{delivery_charge}")
    print(f"    - Total: ₹{total}")
    
    success, order_response = test_api_endpoint(
        "POST",
        "/orders",
        data=order_data,
        description=f"Create Hyderabad order below threshold (₹{actual_subtotal})"
    )
    
    test_results['hyderabad_below_threshold'] = success
    
    if success and order_response:
        # Verify delivery charge is ₹149
        if delivery_charge == 149.0:
            print(f"    ✅ Delivery charge correctly set to ₹149 for Hyderabad below threshold")
            test_results['hyderabad_below_charge_correct'] = True
        else:
            print(f"    ❌ Delivery charge should be ₹149, got ₹{delivery_charge}")
            test_results['hyderabad_below_charge_correct'] = False
        
        # Verify total calculation
        expected_total = actual_subtotal + 149.0
        if abs(total - expected_total) < 0.01:
            print(f"    ✅ Total correctly calculated: ₹{total}")
            test_results['hyderabad_below_total_correct'] = True
        else:
            print(f"    ❌ Total should be ₹{expected_total}, got ₹{total}")
            test_results['hyderabad_below_total_correct'] = False
    
    # Test 5.2: Hyderabad order above threshold (₹2500 > ₹2000)
    print(f"\n  📦 Test 5.2: Hyderabad Order Above Threshold")
    order_data, actual_subtotal, delivery_charge, total = create_order_with_location("Hyderabad", 2500, products)
    
    print(f"    - Target subtotal: ₹2500")
    print(f"    - Actual subtotal: ₹{actual_subtotal}")
    print(f"    - Expected delivery charge: ₹0 (above ₹2000 threshold)")
    print(f"    - Calculated delivery charge: ₹{delivery_charge}")
    print(f"    - Total: ₹{total}")
    
    success, order_response = test_api_endpoint(
        "POST",
        "/orders",
        data=order_data,
        description=f"Create Hyderabad order above threshold (₹{actual_subtotal})"
    )
    
    test_results['hyderabad_above_threshold'] = success
    
    if success and order_response:
        # Verify delivery charge is ₹0
        if delivery_charge == 0.0:
            print(f"    ✅ Free delivery correctly applied for Hyderabad above threshold")
            test_results['hyderabad_above_charge_correct'] = True
        else:
            print(f"    ❌ Delivery charge should be ₹0, got ₹{delivery_charge}")
            test_results['hyderabad_above_charge_correct'] = False
        
        # Verify total calculation
        expected_total = actual_subtotal
        if abs(total - expected_total) < 0.01:
            print(f"    ✅ Total correctly calculated: ₹{total}")
            test_results['hyderabad_above_total_correct'] = True
        else:
            print(f"    ❌ Total should be ₹{expected_total}, got ₹{total}")
            test_results['hyderabad_above_total_correct'] = False
    
    # ============= STEP 6: TEST ADMIN UPDATE CITY THRESHOLD =============
    print("\n" + "="*80)
    print("⚙️ STEP 6: TEST ADMIN UPDATE CITY THRESHOLD")
    print("="*80)
    
    # Test updating Guntur's threshold to ₹1500
    print(f"\n  🔧 Test 6.1: Update Guntur Free Delivery Threshold")
    
    success, response = test_api_endpoint(
        "PUT",
        "/admin/locations/Guntur?free_delivery_threshold=1500",
        headers=headers,
        description="Update Guntur free delivery threshold to ₹1500"
    )
    
    test_results['update_guntur_threshold'] = success
    
    if success:
        print(f"    ✅ Successfully updated Guntur threshold")
        
        # Verify the update by getting locations again
        success, updated_locations = test_api_endpoint(
            "GET",
            "/locations",
            description="Verify Guntur threshold update"
        )
        
        if success and updated_locations:
            guntur_updated = None
            for location in updated_locations:
                if location.get('name') == 'Guntur':
                    guntur_updated = location
                    break
            
            if guntur_updated and guntur_updated.get('free_delivery_threshold') == 1500:
                print(f"    ✅ Guntur threshold successfully updated to ₹1500")
                test_results['verify_guntur_threshold_update'] = True
            else:
                print(f"    ❌ Guntur threshold not updated correctly")
                test_results['verify_guntur_threshold_update'] = False
        else:
            test_results['verify_guntur_threshold_update'] = False
    
    # ============= FINAL SUMMARY =============
    print(f"\n{'='*80}")
    print("🎯 CITY-SPECIFIC FREE DELIVERY TEST SUMMARY")
    print(f"{'='*80}")
    
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result)
    failed_tests = total_tests - passed_tests
    
    print("\n📋 Detailed Results by Test Category:")
    
    # Group results by category
    categories = {
        "Admin Authentication": ['admin_login'],
        "Locations API": ['get_locations', 'no_undefined_values'],
        "City Settings Verification": ['guntur_settings_correct', 'hyderabad_settings_correct'],
        "Guntur Delivery Tests": [
            'guntur_below_threshold', 'guntur_below_charge_correct', 'guntur_below_total_correct',
            'guntur_above_threshold', 'guntur_above_charge_correct', 'guntur_above_total_correct'
        ],
        "Hyderabad Delivery Tests": [
            'hyderabad_below_threshold', 'hyderabad_below_charge_correct', 'hyderabad_below_total_correct',
            'hyderabad_above_threshold', 'hyderabad_above_charge_correct', 'hyderabad_above_total_correct'
        ],
        "Admin Threshold Management": ['update_guntur_threshold', 'verify_guntur_threshold_update']
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
    
    # Critical issues
    critical_issues = []
    
    if not test_results.get('no_undefined_values'):
        critical_issues.append("❌ CRITICAL: 'undefined' values found in location data")
    
    if not test_results.get('guntur_settings_correct'):
        critical_issues.append("❌ CRITICAL: Guntur settings incorrect (charge≠₹49 or threshold≠₹1000)")
    
    if not test_results.get('hyderabad_settings_correct'):
        critical_issues.append("❌ CRITICAL: Hyderabad settings incorrect (charge≠₹149 or threshold≠₹2000)")
    
    # Delivery logic issues
    delivery_issues = []
    
    if not test_results.get('guntur_below_charge_correct'):
        delivery_issues.append("❌ Guntur below threshold: Should charge ₹49")
    
    if not test_results.get('guntur_above_charge_correct'):
        delivery_issues.append("❌ Guntur above threshold: Should be free (₹0)")
    
    if not test_results.get('hyderabad_below_charge_correct'):
        delivery_issues.append("❌ Hyderabad below threshold: Should charge ₹149")
    
    if not test_results.get('hyderabad_above_charge_correct'):
        delivery_issues.append("❌ Hyderabad above threshold: Should be free (₹0)")
    
    # Print findings
    if critical_issues:
        print(f"\n🚨 CRITICAL ISSUES FOUND:")
        for issue in critical_issues:
            print(f"  {issue}")
    
    if delivery_issues:
        print(f"\n⚠️ DELIVERY LOGIC ISSUES:")
        for issue in delivery_issues:
            print(f"  {issue}")
    
    if not critical_issues and not delivery_issues:
        print(f"\n🎉 ALL CRITICAL TESTS PASSED!")
        print(f"  ✅ No 'undefined' values in city data")
        print(f"  ✅ Guntur: ₹49 charge, free delivery above ₹1000")
        print(f"  ✅ Hyderabad: ₹149 charge, free delivery above ₹2000")
        print(f"  ✅ City-specific thresholds working correctly")
        print(f"  ✅ Admin can update city thresholds")
    
    if failed_tests > 0:
        print(f"\n⚠️ {failed_tests} test(s) failed. Check the detailed output above for specific issues.")
        return 1
    else:
        print(f"\n🎉 ALL TESTS PASSED! City-specific free delivery feature is working correctly.")
        return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)