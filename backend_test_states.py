#!/usr/bin/env python3
"""
Backend API Testing Script for Anantha Lakshmi Food Delivery App
FOCUSED TEST: State Management APIs
Tests: GET /api/states, GET /api/admin/states (with admin auth), Database verification
"""

import requests
import json
import sys
from datetime import datetime, timedelta, timezone
import time
import random

# Backend URL from environment
BACKEND_URL = "https://foodcode-solver.preview.emergentagent.com/api"

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

def main():
    """Main testing function - FOCUSED ON STATE MANAGEMENT APIS"""
    print("🚀 Starting FOCUSED Backend API Tests - State Management APIs")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now()}")
    
    # Test results tracking
    test_results = {}
    
    # ============= STEP 1: ADMIN LOGIN AUTHENTICATION =============
    print("\n" + "="*80)
    print("🔐 STEP 1: ADMIN LOGIN AUTHENTICATION TEST")
    print("="*80)
    
    # Test 1.1: Admin login with correct password
    auth_token = admin_login()
    if not auth_token:
        print("\n❌ CRITICAL: Admin login failed - cannot proceed with admin-only tests")
        test_results['admin_login'] = False
        return 1
    
    test_results['admin_login'] = True
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Test 1.2: Verify token contains proper admin info
    print(f"\n  📊 Admin Token Verification:")
    print(f"    - Token received: {bool(auth_token)}")
    print(f"    - Token length: {len(auth_token) if auth_token else 0}")
    print(f"    - Token starts with expected format: {auth_token.startswith('eyJ') if auth_token else False}")
    
    # ============= STEP 2: TEST PUBLIC STATES API =============
    print("\n" + "="*80)
    print("🏛️ STEP 2: TEST PUBLIC STATES API (GET /api/states)")
    print("="*80)
    
    # Test 2.1: Get states without authentication (public endpoint)
    success, states_data = test_api_endpoint(
        "GET",
        "/states",
        description="Get states (public endpoint - no authentication required)"
    )
    
    test_results['get_states_public'] = success
    
    if success and states_data is not None:
        states_count = len(states_data) if isinstance(states_data, list) else 0
        print(f"\n  📊 Public States API Verification:")
        print(f"    - Total states returned: {states_count}")
        print(f"    - Response is list: {isinstance(states_data, list)}")
        
        # Expected states: Only Andhra Pradesh and Telangana
        expected_states = ["Andhra Pradesh", "Telangana"]
        
        if isinstance(states_data, list):
            actual_state_names = [state.get('name') for state in states_data if isinstance(state, dict)]
            print(f"    - Actual state names: {actual_state_names}")
            print(f"    - Expected state names: {expected_states}")
            
            # Check if we have exactly 2 states
            if states_count == 2:
                print(f"    ✅ Correct number of states (2)")
                test_results['verify_states_count'] = True
            else:
                print(f"    ❌ Incorrect number of states. Expected: 2, Got: {states_count}")
                test_results['verify_states_count'] = False
            
            # Check if both expected states are present
            ap_found = any(state.get('name') == 'Andhra Pradesh' for state in states_data)
            telangana_found = any(state.get('name') == 'Telangana' for state in states_data)
            
            print(f"    - Andhra Pradesh found: {ap_found}")
            print(f"    - Telangana found: {telangana_found}")
            
            if ap_found and telangana_found:
                print(f"    ✅ Both expected states (AP and Telangana) are present")
                test_results['verify_expected_states'] = True
            else:
                print(f"    ❌ Missing expected states")
                test_results['verify_expected_states'] = False
            
            # Check if both states are enabled
            ap_enabled = any(state.get('name') == 'Andhra Pradesh' and state.get('enabled') == True for state in states_data)
            telangana_enabled = any(state.get('name') == 'Telangana' and state.get('enabled') == True for state in states_data)
            
            print(f"    - Andhra Pradesh enabled: {ap_enabled}")
            print(f"    - Telangana enabled: {telangana_enabled}")
            
            if ap_enabled and telangana_enabled:
                print(f"    ✅ Both states have enabled: true")
                test_results['verify_states_enabled'] = True
            else:
                print(f"    ❌ States not properly enabled")
                test_results['verify_states_enabled'] = False
            
            # Check for unwanted states
            unwanted_states = [name for name in actual_state_names if name not in expected_states]
            if unwanted_states:
                print(f"    ❌ Found unwanted states: {unwanted_states}")
                test_results['verify_no_extra_states'] = False
            else:
                print(f"    ✅ No unwanted states found")
                test_results['verify_no_extra_states'] = True
        else:
            print(f"    ❌ Invalid response format")
            test_results['verify_states_count'] = False
            test_results['verify_expected_states'] = False
            test_results['verify_states_enabled'] = False
            test_results['verify_no_extra_states'] = False
    else:
        print(f"    ❌ Failed to get states from public API")
        test_results['verify_states_count'] = False
        test_results['verify_expected_states'] = False
        test_results['verify_states_enabled'] = False
        test_results['verify_no_extra_states'] = False
    
    # ============= STEP 3: TEST ADMIN STATES API =============
    print("\n" + "="*80)
    print("🔐 STEP 3: TEST ADMIN STATES API (GET /api/admin/states)")
    print("="*80)
    
    # Test 3.1: Get admin states with authentication
    success, admin_states_data = test_api_endpoint(
        "GET",
        "/admin/states",
        headers=headers,
        description="Get states with admin authentication"
    )
    
    test_results['get_states_admin'] = success
    
    if success and admin_states_data is not None:
        admin_states_count = len(admin_states_data) if isinstance(admin_states_data, list) else 0
        print(f"\n  📊 Admin States API Verification:")
        print(f"    - Total states returned: {admin_states_count}")
        print(f"    - Response is list: {isinstance(admin_states_data, list)}")
        
        if isinstance(admin_states_data, list):
            admin_state_names = [state.get('name') for state in admin_states_data if isinstance(state, dict)]
            print(f"    - Admin state names: {admin_state_names}")
            
            # Check if admin API returns same data as public API
            if states_data and admin_states_data:
                public_names = sorted([state.get('name') for state in states_data])
                admin_names = sorted([state.get('name') for state in admin_states_data])
                
                if public_names == admin_names:
                    print(f"    ✅ Admin API returns same states as public API")
                    test_results['verify_admin_public_consistency'] = True
                else:
                    print(f"    ❌ Admin API returns different states than public API")
                    print(f"        Public: {public_names}")
                    print(f"        Admin: {admin_names}")
                    test_results['verify_admin_public_consistency'] = False
            
            # Check admin-specific requirements
            if admin_states_count == 2:
                print(f"    ✅ Admin API returns correct number of states (2)")
                test_results['verify_admin_states_count'] = True
            else:
                print(f"    ❌ Admin API returns incorrect number of states. Expected: 2, Got: {admin_states_count}")
                test_results['verify_admin_states_count'] = False
        else:
            print(f"    ❌ Invalid admin response format")
            test_results['verify_admin_public_consistency'] = False
            test_results['verify_admin_states_count'] = False
    else:
        print(f"    ❌ Failed to get states from admin API")
        test_results['verify_admin_public_consistency'] = False
        test_results['verify_admin_states_count'] = False
    
    # Test 3.2: Try to get admin states without authentication (should fail with 401)
    success, response = test_api_endpoint(
        "GET",
        "/admin/states",
        description="Try to get admin states without authentication (should return 401)",
        expected_status=401
    )
    
    test_results['get_admin_states_no_auth'] = success
    
    if success:
        print(f"    ✅ Correctly returns 401 when no authentication provided")
    else:
        print(f"    ❌ Should return 401 for unauthenticated access")
    
    # ============= STEP 4: DATABASE VERIFICATION =============
    print("\n" + "="*80)
    print("💾 STEP 4: DATABASE VERIFICATION")
    print("="*80)
    
    # Since we can't directly access MongoDB, we'll verify through API behavior
    print(f"\n  📊 Database State Verification (via API behavior):")
    
    # If both APIs return only AP and Telangana, it suggests database is clean
    if (test_results.get('verify_states_count') and 
        test_results.get('verify_expected_states') and 
        test_results.get('verify_no_extra_states') and
        test_results.get('verify_admin_states_count')):
        
        print(f"    ✅ Database appears to contain only AP and Telangana states")
        print(f"    ✅ No extra states found in database")
        test_results['verify_database_clean'] = True
    else:
        print(f"    ❌ Database may contain extra states or incorrect data")
        test_results['verify_database_clean'] = False
    
    # ============= FINAL SUMMARY =============
    print(f"\n{'='*80}")
    print("🎯 STATE MANAGEMENT APIS TEST SUMMARY")
    print(f"{'='*80}")
    
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result)
    failed_tests = total_tests - passed_tests
    
    print("\n📋 Detailed Results by Test Category:")
    
    # Group results by category
    categories = {
        "Admin Authentication": ['admin_login'],
        "Public States API": ['get_states_public', 'verify_states_count', 'verify_expected_states', 'verify_states_enabled', 'verify_no_extra_states'],
        "Admin States API": ['get_states_admin', 'verify_admin_states_count', 'verify_admin_public_consistency', 'get_admin_states_no_auth'],
        "Database Verification": ['verify_database_clean']
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
    
    # Admin Login
    if test_results.get('admin_login'):
        print(f"  ✅ Admin login with password 'admin123' works correctly")
    else:
        print(f"  ❌ Admin login failed - check password or backend service")
    
    # Public States API
    if test_results.get('get_states_public'):
        print(f"  ✅ GET /api/states endpoint is accessible (public)")
    else:
        print(f"  ❌ GET /api/states endpoint failed")
    
    if (test_results.get('verify_states_count') and 
        test_results.get('verify_expected_states') and 
        test_results.get('verify_no_extra_states')):
        print(f"  ✅ GET /api/states returns only Andhra Pradesh and Telangana")
    else:
        print(f"  ❌ GET /api/states returns incorrect states")
    
    if test_results.get('verify_states_enabled'):
        print(f"  ✅ Both states have enabled: true")
    else:
        print(f"  ❌ States are not properly enabled")
    
    # Admin States API
    if test_results.get('get_states_admin'):
        print(f"  ✅ GET /api/admin/states endpoint works with admin auth")
    else:
        print(f"  ❌ GET /api/admin/states endpoint failed with admin auth")
    
    if test_results.get('get_admin_states_no_auth'):
        print(f"  ✅ GET /api/admin/states properly requires authentication (returns 401)")
    else:
        print(f"  ❌ GET /api/admin/states should return 401 without authentication")
    
    if test_results.get('verify_admin_public_consistency'):
        print(f"  ✅ Admin and public APIs return consistent data")
    else:
        print(f"  ❌ Admin and public APIs return different data")
    
    # Database
    if test_results.get('verify_database_clean'):
        print(f"  ✅ Database contains only AP and Telangana states")
    else:
        print(f"  ❌ Database may contain extra or incorrect states")
    
    if failed_tests > 0:
        print(f"\n⚠️  {failed_tests} test(s) failed. Check the detailed output above for specific issues.")
        return 1
    else:
        print(f"\n🎉 ALL TESTS PASSED! State management APIs are working correctly.")
        print(f"✅ Only Andhra Pradesh and Telangana states are returned")
        print(f"✅ Both states have enabled: true")
        print(f"✅ Admin authentication works properly")
        print(f"✅ Database appears to be clean (no extra states)")
        return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)