#!/usr/bin/env python3
"""
Admin Payment Endpoints Testing Script
Testing all payment-related endpoints in the admin panel as specified in review request

**Backend URL:** https://recipe-store-1.preview.emergentagent.com/api

**Admin Credentials:**
- Email: admin@ananthalakshmi.com
- Password: admin123

**Endpoints to Test:**
1. Admin Login (POST /api/admin/login)
2. Get Payment Settings (GET /api/admin/payment-settings)
3. Update Payment Settings (PUT /api/admin/payment-settings?status=enabled)
4. Get Razorpay Settings (GET /api/admin/razorpay-settings)
5. Update Razorpay Settings (PUT /api/admin/razorpay-settings?key_id=test_key&key_secret=test_secret)
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://recipe-store-1.preview.emergentagent.com/api"

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
            response = requests.post(url, headers=headers, json=data, params=params, timeout=30)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=headers, json=data, params=params, timeout=30)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers, params=params, timeout=30)
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

def test_admin_payment_endpoints():
    """Test all payment-related endpoints in the admin panel"""
    print("🚀 STARTING ADMIN PAYMENT ENDPOINTS TESTING")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Testing Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    test_results = []
    
    # Step 1: Admin Login
    print("\n🔐 STEP 1: ADMIN LOGIN")
    login_data = {
        "email": "admin@ananthalakshmi.com",
        "password": "admin123"
    }
    
    success, response_data = test_api_endpoint(
        "POST",
        "/auth/admin-login",
        data=login_data,
        description="Admin login with correct credentials"
    )
    
    if success and response_data and "token" in response_data:
        admin_token = response_data["token"]
        print(f"✅ SUCCESS: Admin login successful")
        print(f"   - Token Length: {len(admin_token)} characters")
        print(f"   - User: {response_data.get('user', {}).get('name', 'Unknown')}")
        test_results.append(("Admin Login", True))
        
        auth_headers = {
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json"
        }
    else:
        print(f"❌ FAILED: Admin login failed")
        test_results.append(("Admin Login", False))
        return test_results
    
    # Step 2: Get Payment Settings
    print("\n💳 STEP 2: GET PAYMENT SETTINGS")
    success, response_data = test_api_endpoint(
        "GET",
        "/admin/payment-settings",
        headers=auth_headers,
        description="Get current payment settings (should return payment status)"
    )
    
    if success:
        print(f"✅ SUCCESS: Payment settings retrieved")
        if response_data:
            status = response_data.get('status', 'unknown')
            print(f"   - Current Status: {status}")
            
            # Verify expected fields
            if 'status' in response_data:
                print(f"   - Response contains 'status' field ✓")
            else:
                print(f"   - Missing 'status' field ⚠️")
        test_results.append(("Get Payment Settings", True))
    else:
        print(f"❌ FAILED: Could not get payment settings")
        test_results.append(("Get Payment Settings", False))
    
    # Step 3: Update Payment Settings - Test different status values
    print("\n⚙️ STEP 3: UPDATE PAYMENT SETTINGS")
    
    status_values = ["enabled", "disabled", "removed"]
    
    for status in status_values:
        print(f"\n  Testing status: {status}")
        success, response_data = test_api_endpoint(
            "PUT",
            "/admin/payment-settings",
            headers=auth_headers,
            params={"status": status},
            description=f"Update payment settings to {status}"
        )
        
        if success:
            print(f"   ✅ SUCCESS: Payment status updated to {status}")
            test_results.append((f"Update Payment Settings ({status})", True))
        else:
            print(f"   ❌ FAILED: Could not update payment status to {status}")
            test_results.append((f"Update Payment Settings ({status})", False))
    
    # Step 4: Get Razorpay Settings
    print("\n🔑 STEP 4: GET RAZORPAY SETTINGS")
    success, response_data = test_api_endpoint(
        "GET",
        "/admin/razorpay-settings",
        headers=auth_headers,
        description="Get current Razorpay settings (should return key_id and key_secret)"
    )
    
    if success:
        print(f"✅ SUCCESS: Razorpay settings retrieved")
        if response_data:
            key_id = response_data.get('key_id', 'not found')
            key_secret = response_data.get('key_secret', 'not found')
            print(f"   - Key ID: {key_id}")
            print(f"   - Key Secret: {'*' * len(key_secret) if key_secret != 'not found' else 'not found'}")
            
            # Verify expected fields
            expected_fields = ['key_id', 'key_secret']
            for field in expected_fields:
                if field in response_data:
                    print(f"   - Response contains '{field}' field ✓")
                else:
                    print(f"   - Missing '{field}' field ⚠️")
        test_results.append(("Get Razorpay Settings", True))
    else:
        print(f"❌ FAILED: Could not get Razorpay settings")
        test_results.append(("Get Razorpay Settings", False))
    
    # Step 5: Update Razorpay Settings
    print("\n🔧 STEP 5: UPDATE RAZORPAY SETTINGS")
    success, response_data = test_api_endpoint(
        "PUT",
        "/admin/razorpay-settings",
        headers=auth_headers,
        params={"key_id": "test_key", "key_secret": "test_secret"},
        description="Update Razorpay key_id and key_secret"
    )
    
    if success:
        print(f"✅ SUCCESS: Razorpay settings updated")
        test_results.append(("Update Razorpay Settings", True))
    else:
        print(f"❌ FAILED: Could not update Razorpay settings")
        test_results.append(("Update Razorpay Settings", False))
    
    # Step 6: Test Unauthorized Access (without token)
    print("\n🚫 STEP 6: TEST UNAUTHORIZED ACCESS")
    
    unauthorized_endpoints = [
        ("/admin/payment-settings", "GET"),
        ("/admin/razorpay-settings", "GET"),
        ("/admin/payment-settings", "PUT"),
        ("/admin/razorpay-settings", "PUT")
    ]
    
    for endpoint, method in unauthorized_endpoints:
        print(f"\n  Testing unauthorized {method} {endpoint}")
        success, response_data = test_api_endpoint(
            method,
            endpoint,
            params={"status": "enabled"} if "payment-settings" in endpoint and method == "PUT" else None,
            description=f"Test unauthorized {method} access to {endpoint} (should return 401/403)",
            expected_status=401
        )
        
        if success:
            print(f"   ✅ SUCCESS: Unauthorized access correctly blocked")
            test_results.append((f"Unauthorized Access Block ({method} {endpoint})", True))
        else:
            print(f"   ❌ FAILED: Unauthorized access not properly blocked")
            test_results.append((f"Unauthorized Access Block ({method} {endpoint})", False))
    
    # Print Summary
    print("\n" + "="*80)
    print("📊 ADMIN PAYMENT ENDPOINTS TESTING SUMMARY")
    print("="*80)
    
    passed_count = sum(1 for _, passed in test_results if passed)
    total_count = len(test_results)
    success_rate = (passed_count / total_count) * 100 if total_count > 0 else 0
    
    print(f"Overall Success Rate: {passed_count}/{total_count} ({success_rate:.1f}%)")
    print(f"Status: {'✅ ALL TESTS PASSED' if passed_count == total_count else '❌ SOME TESTS FAILED'}")
    
    print(f"\n📋 DETAILED RESULTS:")
    for test_name, passed in test_results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status} - {test_name}")
    
    # Endpoint Status Summary
    print(f"\n🎯 ENDPOINT STATUS SUMMARY:")
    
    # Group results by endpoint
    endpoint_groups = {
        "Admin Login": [r for r in test_results if "Admin Login" in r[0]],
        "Payment Settings": [r for r in test_results if "Payment Settings" in r[0] and "Unauthorized" not in r[0]],
        "Razorpay Settings": [r for r in test_results if "Razorpay Settings" in r[0] and "Unauthorized" not in r[0]],
        "Security (Unauthorized Access)": [r for r in test_results if "Unauthorized" in r[0]]
    }
    
    for group_name, group_results in endpoint_groups.items():
        if group_results:
            group_passed = sum(1 for _, passed in group_results if passed)
            group_total = len(group_results)
            group_status = "✅" if group_passed == group_total else "❌"
            print(f"   {group_status} {group_name}: {group_passed}/{group_total} tests passed")
    
    print(f"\n🏁 CONCLUSION:")
    if passed_count == total_count:
        print(f"   🎉 ALL ADMIN PAYMENT ENDPOINTS WORKING PERFECTLY!")
        print(f"   ✅ Admin authentication successful")
        print(f"   ✅ Payment settings can be retrieved and updated")
        print(f"   ✅ Razorpay settings can be retrieved and updated")
        print(f"   ✅ Unauthorized access properly blocked")
        print(f"   🔧 Admin panel payment management is fully functional")
    else:
        failed_tests = [name for name, passed in test_results if not passed]
        print(f"   ⚠️ ISSUES FOUND IN THE FOLLOWING TESTS:")
        for failed_test in failed_tests:
            print(f"     - {failed_test}")
        print(f"   🔧 Review and fix failing endpoints before production use")
    
    return passed_count == total_count

if __name__ == "__main__":
    success = test_admin_payment_endpoints()
    sys.exit(0 if success else 1)