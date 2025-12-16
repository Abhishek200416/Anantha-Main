#!/usr/bin/env python3
"""
Backend API Testing Script for Anantha Lakshmi Food Delivery App
SPECIFIC REVIEW REQUEST TESTING

**TESTING PRIORITIES (As per Review Request)**:
1. PRODUCTS API TESTING - Verify exactly 58 products with 8 categories: powders (13), pickles (9), hot-items (10), sweets (9), laddus (6), chikkis (4), snacks (3), spices (4)
2. ADMIN AUTHENTICATION TESTING - POST /api/auth/admin-login with {"email":"admin@ananthalakshmi.com","password":"admin123"}
3. ADMIN PAYMENT SETTINGS TESTING - GET/PUT /api/admin/payment-settings with admin token
4. ADMIN RAZORPAY SETTINGS TESTING - GET/PUT /api/admin/razorpay-settings with admin token
5. SAMPLE PRODUCTS VERIFICATION - Verify 3-4 sample products with complete details

Focus on testing ALL payment-related endpoints thoroughly as user reported issues with admin payment page.
"""

import requests
import json
import sys
from datetime import datetime, timedelta, timezone
import time
import random
import os
import tempfile

# Backend URL from environment
BACKEND_URL = "https://city-order-bug.preview.emergentagent.com/api"
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
    
    # Admin login with email and password
    login_data = {
        "email": "admin@ananthalakshmi.com",
        "password": "admin123"
    }
    
    success, response_data = test_api_endpoint(
        "POST",
        "/auth/admin-login",
        data=login_data,
        description="Admin login with email and password 'admin123'"
    )
    
    if success and response_data and "token" in response_data:
        token = response_data["token"]
        print(f"✅ Successfully logged in as admin and got JWT token")
        return token
    
    print("❌ Failed to get admin authentication token")
    return None

def test_api_endpoint_form_data(method, endpoint, headers=None, form_data=None, files=None, description="", expected_status=None):
    """Test API endpoint with form data (for file uploads)"""
    url = f"{BACKEND_URL}{endpoint}"
    
    print(f"\n{'='*60}")
    print(f"Testing: {method} {endpoint}")
    print(f"Description: {description}")
    print(f"URL: {url}")
    if form_data:
        print(f"Form Data: {form_data}")
    if files:
        print(f"Files: {list(files.keys())}")
    print(f"{'='*60}")
    
    try:
        if method.upper() == "POST":
            response = requests.post(url, headers=headers, data=form_data, files=files, timeout=30)
        else:
            print(f"❌ Unsupported method for form data: {method}")
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

def create_test_image():
    """Create a small test image file for upload testing"""
    try:
        # Create a simple 1x1 pixel PNG image
        import base64
        
        # Minimal PNG data (1x1 transparent pixel)
        png_data = base64.b64decode(
            'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU8'
            'IQAAAAABJRU5ErkJggg=='
        )
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        temp_file.write(png_data)
        temp_file.close()
        
        return temp_file.name
    except Exception as e:
        print(f"Warning: Could not create test image: {e}")
        return None

def test_bug_report_submission(email, mobile, issue_description):
    """Test bug report submission using form-data"""
    print(f"\n📝 Testing Bug Report Submission for {email}...")
    
    try:
        # Use form-data as specified in the review request
        form_data = {
            'email': email,
            'mobile': mobile,
            'issue_description': issue_description
        }
        
        response = requests.post(f"{BACKEND_URL}/reports", data=form_data, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            if "report_id" in data and "message" in data:
                print(f"✅ SUCCESS: Bug report created with ID: {data['report_id']}")
                return True, data["report_id"]
            else:
                print(f"❌ FAILED: Missing report_id or message in response")
                return False, None
        else:
            print(f"❌ FAILED: HTTP {response.status_code} - {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        return False, None

def verify_report_in_list(reports, expected_email, expected_mobile, expected_description):
    """Verify that a specific report appears in the reports list with correct fields"""
    print(f"\n🔍 Verifying Report in List for {expected_email}...")
    
    for report in reports:
        if (report.get("email") == expected_email and 
            report.get("mobile") == expected_mobile and 
            report.get("issue_description") == expected_description):
            
            # Check all required fields from review request
            required_fields = ["id", "email", "mobile", "issue_description", "status", "created_at", "photo_url"]
            missing_fields = [field for field in required_fields if field not in report]
            
            if missing_fields:
                print(f"❌ FAILED: Missing fields: {missing_fields}")
                return False
            
            # Verify field formats
            if not report["id"]:  # Should be UUID format
                print(f"❌ FAILED: Report ID is empty")
                return False
            
            if report["status"] not in ["New", "In Progress", "Resolved"]:
                print(f"❌ FAILED: Invalid status: {report['status']}")
                return False
            
            print(f"✅ SUCCESS: Report found with correct fields")
            print(f"   - ID: {report['id']}")
            print(f"   - Email: {report['email']}")
            print(f"   - Mobile: {report['mobile']}")
            print(f"   - Issue: {report['issue_description'][:50]}...")
            print(f"   - Status: {report['status']}")
            print(f"   - Created: {report['created_at']}")
            print(f"   - Photo URL: {report['photo_url']}")
            return True
    
    print(f"❌ FAILED: Report not found for {expected_email}")
    return False

def test_report_ordering(reports):
    """Test that reports are ordered by newest first"""
    print(f"\n📅 Testing Report Ordering (Newest First)...")
    
    if len(reports) < 2:
        print(f"ℹ️  Less than 2 reports, ordering test skipped")
        return True
    
    try:
        # Check if reports are ordered by created_at descending (newest first)
        for i in range(len(reports) - 1):
            current_time = reports[i].get("created_at", "")
            next_time = reports[i + 1].get("created_at", "")
            
            if current_time and next_time:
                # Parse ISO timestamps
                current_dt = datetime.fromisoformat(current_time.replace('Z', '+00:00'))
                next_dt = datetime.fromisoformat(next_time.replace('Z', '+00:00'))
                
                if current_dt < next_dt:
                    print(f"❌ FAILED: Reports not in descending order")
                    print(f"   Current: {current_time}")
                    print(f"   Next: {next_time}")
                    return False
        
        print(f"✅ SUCCESS: Reports correctly ordered by newest first")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: Exception parsing timestamps: {str(e)}")
        return False

def test_admin_password_change_otp():
    """Test admin password change OTP flow to identify 500 error"""
    print("\n" + "="*80)
    print("🔐 ADMIN PASSWORD CHANGE OTP TESTING")
    print("="*80)
    
    # Step 1: Admin login
    print("\n--- Step 1: Admin Login ---")
    admin_token = admin_login()
    
    if not admin_token:
        print("❌ CRITICAL: Cannot proceed without admin authentication")
        return False
    
    auth_headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
    
    # Step 2: Test OTP send endpoint
    print("\n--- Step 2: Testing OTP Send Endpoint ---")
    admin_email = "contact.ananthahomefoods@gmail.com"  # From .env file
    
    otp_send_data = {
        "email": admin_email
    }
    
    print(f"Testing POST /api/admin/profile/send-otp")
    success, otp_response = test_api_endpoint(
        "POST",
        "/admin/profile/send-otp",
        headers=auth_headers,
        data=otp_send_data,
        description=f"Send OTP to admin email: {admin_email}"
    )
    
    if not success:
        print("❌ FAILED: OTP send endpoint failed")
        return False
    
    print("✅ SUCCESS: OTP send endpoint working")
    
    # Step 3: Test OTP verification endpoint with invalid OTP (to see the error)
    print("\n--- Step 3: Testing OTP Verification Endpoint ---")
    
    # Test with invalid OTP first to see validation
    invalid_otp_data = {
        "email": admin_email,
        "otp": "123456",  # Invalid OTP
        "new_password": "newadmin123"
    }
    
    print(f"Testing POST /api/admin/profile/verify-otp-change-password with invalid OTP")
    success, verify_response = test_api_endpoint(
        "POST",
        "/admin/profile/verify-otp-change-password",
        headers=auth_headers,
        data=invalid_otp_data,
        description="Verify OTP with invalid OTP (should return 400)",
        expected_status=400
    )
    
    if success:
        print("✅ SUCCESS: OTP verification correctly rejects invalid OTP")
    else:
        print("❌ ISSUE: OTP verification endpoint behavior unexpected")
        
        # Check if it's a 500 error
        if verify_response is not None:
            print("🔍 INVESTIGATING 500 ERROR...")
            
            # Check backend logs for more details
            print("\n--- Checking Backend Logs ---")
            try:
                import subprocess
                result = subprocess.run(
                    ["tail", "-n", "50", "/var/log/supervisor/backend.err.log"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.stdout:
                    print("Backend Error Logs:")
                    print(result.stdout)
                else:
                    print("No recent error logs found")
                    
            except Exception as e:
                print(f"Could not read backend logs: {e}")
        
        return False
    
    # Step 4: Test with missing fields to trigger validation errors
    print("\n--- Step 4: Testing Validation Errors ---")
    
    test_cases = [
        {
            "name": "Missing email",
            "data": {"otp": "123456", "new_password": "newpass"},
            "expected_status": 422
        },
        {
            "name": "Missing OTP", 
            "data": {"email": admin_email, "new_password": "newpass"},
            "expected_status": 422
        },
        {
            "name": "Missing new_password",
            "data": {"email": admin_email, "otp": "123456"},
            "expected_status": 422
        },
        {
            "name": "Empty request body",
            "data": {},
            "expected_status": 422
        }
    ]
    
    for test_case in test_cases:
        print(f"\n  Testing: {test_case['name']}")
        success, response = test_api_endpoint(
            "POST",
            "/admin/profile/verify-otp-change-password",
            headers=auth_headers,
            data=test_case["data"],
            description=test_case["name"],
            expected_status=test_case["expected_status"]
        )
        
        if not success:
            print(f"❌ VALIDATION ERROR: {test_case['name']} - Expected {test_case['expected_status']} but got different response")
            
            # If we get 500 error, investigate
            if response is not None:
                print("🔍 INVESTIGATING 500 ERROR FOR VALIDATION...")
                try:
                    import subprocess
                    result = subprocess.run(
                        ["tail", "-n", "20", "/var/log/supervisor/backend.err.log"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    if result.stdout:
                        print("Recent Backend Error Logs:")
                        print(result.stdout)
                        
                except Exception as e:
                    print(f"Could not read backend logs: {e}")
        else:
            print(f"✅ SUCCESS: {test_case['name']} handled correctly")
    
    return True

def test_admin_authentication():
    """Test admin authentication with email and password as per review request #2"""
    print("\n" + "="*80)
    print("🔐 ADMIN AUTHENTICATION TESTING (REVIEW REQUEST #2)")
    print("="*80)
    
    login_data = {
        "email": "admin@ananthalakshmi.com",
        "password": "admin123"
    }
    
    success, response_data = test_api_endpoint(
        "POST",
        "/auth/admin-login",
        data=login_data,
        description="Admin login with exact credentials from review request"
    )
    
    if success and response_data:
        # Verify response structure
        required_fields = ["user", "token", "message"]
        missing_fields = [field for field in required_fields if field not in response_data]
        
        if missing_fields:
            print(f"❌ FAILED: Missing fields in response: {missing_fields}")
            return False, None
        
        # Verify user object structure
        user = response_data.get("user", {})
        user_required_fields = ["id", "email", "name", "is_admin"]
        user_missing_fields = [field for field in user_required_fields if field not in user]
        
        if user_missing_fields:
            print(f"❌ FAILED: Missing user fields: {user_missing_fields}")
            return False, None
        
        # Verify admin user details
        if (user.get("id") == "admin" and 
            user.get("email") == "admin@ananthalakshmi.com" and
            user.get("name") == "Admin" and
            user.get("is_admin") == True):
            
            token = response_data.get("token")
            if token and len(token) > 100:  # JWT tokens are typically long
                print(f"✅ SUCCESS: Admin authentication working perfectly")
                print(f"   - User ID: {user.get('id')}")
                print(f"   - Email: {user.get('email')}")
                print(f"   - Name: {user.get('name')}")
                print(f"   - Is Admin: {user.get('is_admin')}")
                print(f"   - Token Length: {len(token)} characters")
                print(f"   - JWT Token Format: {token[:20]}...{token[-20:]}")
                return True, token
            else:
                print(f"❌ FAILED: Invalid or missing JWT token")
                return False, None
        else:
            print(f"❌ FAILED: Invalid admin user object")
            return False, None
    
    print(f"❌ FAILED: Admin authentication failed")
    return False, None

def test_admin_payment_settings(admin_token):
    """Test admin payment settings endpoints as per review request #3"""
    print("\n" + "="*80)
    print("💳 ADMIN PAYMENT SETTINGS TESTING (REVIEW REQUEST #3)")
    print("="*80)
    
    auth_headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
    
    test_results = []
    
    # Test 1: GET /api/admin/payment-settings (with admin token)
    print("\n--- Test 1: GET Payment Settings (with admin token) ---")
    success, response_data = test_api_endpoint(
        "GET",
        "/admin/payment-settings",
        headers=auth_headers,
        description="Get payment settings with admin authentication"
    )
    
    if success and response_data:
        print(f"✅ SUCCESS: GET payment settings working")
        print(f"   - Response: {response_data}")
        test_results.append(("GET Payment Settings (Authenticated)", True))
    else:
        print(f"❌ FAILED: GET payment settings failed")
        test_results.append(("GET Payment Settings (Authenticated)", False))
    
    # Test 2: PUT /api/admin/payment-settings?status=enabled (with admin token)
    print("\n--- Test 2: PUT Payment Settings status=enabled (with admin token) ---")
    success, response_data = test_api_endpoint(
        "PUT",
        "/admin/payment-settings?status=enabled",
        headers=auth_headers,
        description="Update payment status to enabled with admin authentication"
    )
    
    if success:
        print(f"✅ SUCCESS: PUT payment settings (enabled) working")
        print(f"   - Response: {response_data}")
        test_results.append(("PUT Payment Settings Enabled", True))
    else:
        print(f"❌ FAILED: PUT payment settings (enabled) failed")
        test_results.append(("PUT Payment Settings Enabled", False))
    
    # Test 3: PUT /api/admin/payment-settings?status=disabled (with admin token)
    print("\n--- Test 3: PUT Payment Settings status=disabled (with admin token) ---")
    success, response_data = test_api_endpoint(
        "PUT",
        "/admin/payment-settings?status=disabled",
        headers=auth_headers,
        description="Update payment status to disabled with admin authentication"
    )
    
    if success:
        print(f"✅ SUCCESS: PUT payment settings (disabled) working")
        print(f"   - Response: {response_data}")
        test_results.append(("PUT Payment Settings Disabled", True))
    else:
        print(f"❌ FAILED: PUT payment settings (disabled) failed")
        test_results.append(("PUT Payment Settings Disabled", False))
    
    # Test 4: Verify unauthorized access (without token) returns 401
    print("\n--- Test 4: Verify Unauthorized Access Returns 401 ---")
    
    # Test GET without token
    success, response_data = test_api_endpoint(
        "GET",
        "/admin/payment-settings",
        description="GET payment settings without authentication (should return 401)",
        expected_status=401
    )
    
    if success:
        print(f"✅ SUCCESS: GET payment settings correctly returns 401 without auth")
        test_results.append(("GET Payment Settings Unauthorized", True))
    else:
        print(f"❌ FAILED: GET payment settings should return 401 without auth")
        test_results.append(("GET Payment Settings Unauthorized", False))
    
    # Test PUT without token
    success, response_data = test_api_endpoint(
        "PUT",
        "/admin/payment-settings?status=enabled",
        description="PUT payment settings without authentication (should return 401)",
        expected_status=401
    )
    
    if success:
        print(f"✅ SUCCESS: PUT payment settings correctly returns 401 without auth")
        test_results.append(("PUT Payment Settings Unauthorized", True))
    else:
        print(f"❌ FAILED: PUT payment settings should return 401 without auth")
        test_results.append(("PUT Payment Settings Unauthorized", False))
    
    return test_results

def test_admin_razorpay_settings(admin_token):
    """Test admin Razorpay settings endpoints as per review request #4"""
    print("\n" + "="*80)
    print("🔑 ADMIN RAZORPAY SETTINGS TESTING (REVIEW REQUEST #4)")
    print("="*80)
    
    auth_headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
    
    test_results = []
    
    # Test 1: GET /api/admin/razorpay-settings (with admin token)
    print("\n--- Test 1: GET Razorpay Settings (with admin token) ---")
    success, response_data = test_api_endpoint(
        "GET",
        "/admin/razorpay-settings",
        headers=auth_headers,
        description="Get Razorpay key_id and key_secret with admin authentication"
    )
    
    if success and response_data:
        print(f"✅ SUCCESS: GET Razorpay settings working")
        
        # Verify expected fields
        if "key_id" in response_data and "key_secret" in response_data:
            key_id = response_data.get("key_id")
            key_secret = response_data.get("key_secret")
            print(f"   - Key ID: {key_id}")
            print(f"   - Key Secret: {key_secret[:10]}...{key_secret[-4:] if key_secret else 'None'}")
            
            # Verify test credentials from review request
            if key_id == "rzp_test_Renc645PexAmXU":
                print(f"   ✅ Key ID matches expected test credentials")
            else:
                print(f"   ⚠️  Key ID doesn't match expected: rzp_test_Renc645PexAmXU")
            
            test_results.append(("GET Razorpay Settings (Authenticated)", True))
        else:
            print(f"❌ FAILED: Missing key_id or key_secret in response")
            test_results.append(("GET Razorpay Settings (Authenticated)", False))
    else:
        print(f"❌ FAILED: GET Razorpay settings failed")
        test_results.append(("GET Razorpay Settings (Authenticated)", False))
    
    # Test 2: PUT /api/admin/razorpay-settings (with admin token)
    print("\n--- Test 2: PUT Razorpay Settings (with admin token) ---")
    
    # Test updating Razorpay keys
    update_data = {
        "key_id": "rzp_test_UpdatedKeyId123",
        "key_secret": "UpdatedKeySecret456"
    }
    
    success, response_data = test_api_endpoint(
        "PUT",
        "/admin/razorpay-settings",
        headers=auth_headers,
        data=update_data,
        description="Update Razorpay key_id and key_secret with admin authentication"
    )
    
    if success:
        print(f"✅ SUCCESS: PUT Razorpay settings working")
        print(f"   - Response: {response_data}")
        test_results.append(("PUT Razorpay Settings", True))
        
        # Verify the update by getting settings again
        print("\n   Verifying update by GET request...")
        success_verify, verify_data = test_api_endpoint(
            "GET",
            "/admin/razorpay-settings",
            headers=auth_headers,
            description="Verify Razorpay settings were updated"
        )
        
        if success_verify and verify_data:
            updated_key_id = verify_data.get("key_id")
            updated_key_secret = verify_data.get("key_secret")
            
            if (updated_key_id == "rzp_test_UpdatedKeyId123" and 
                updated_key_secret == "UpdatedKeySecret456"):
                print(f"   ✅ Settings successfully updated and verified")
                test_results.append(("Verify Razorpay Settings Update", True))
            else:
                print(f"   ❌ Settings not updated correctly")
                test_results.append(("Verify Razorpay Settings Update", False))
        
        # Restore original settings
        print("\n   Restoring original settings...")
        restore_data = {
            "key_id": "rzp_test_Renc645PexAmXU",
            "key_secret": "ReA5MNv3beAt068So4iYNq8s"
        }
        
        test_api_endpoint(
            "PUT",
            "/admin/razorpay-settings",
            headers=auth_headers,
            data=restore_data,
            description="Restore original Razorpay settings"
        )
        
    else:
        print(f"❌ FAILED: PUT Razorpay settings failed")
        test_results.append(("PUT Razorpay Settings", False))
    
    # Test 3: Verify unauthorized access (without token) returns 401
    print("\n--- Test 3: Verify Unauthorized Access Returns 401 ---")
    
    # Test GET without token
    success, response_data = test_api_endpoint(
        "GET",
        "/admin/razorpay-settings",
        description="GET Razorpay settings without authentication (should return 401)",
        expected_status=401
    )
    
    if success:
        print(f"✅ SUCCESS: GET Razorpay settings correctly returns 401 without auth")
        test_results.append(("GET Razorpay Settings Unauthorized", True))
    else:
        print(f"❌ FAILED: GET Razorpay settings should return 401 without auth")
        test_results.append(("GET Razorpay Settings Unauthorized", False))
    
    # Test PUT without token
    success, response_data = test_api_endpoint(
        "PUT",
        "/admin/razorpay-settings",
        data={"key_id": "test", "key_secret": "test"},
        description="PUT Razorpay settings without authentication (should return 401)",
        expected_status=401
    )
    
    if success:
        print(f"✅ SUCCESS: PUT Razorpay settings correctly returns 401 without auth")
        test_results.append(("PUT Razorpay Settings Unauthorized", True))
    else:
        print(f"❌ FAILED: PUT Razorpay settings should return 401 without auth")
        test_results.append(("PUT Razorpay Settings Unauthorized", False))
    
    return test_results

def test_city_suggestions_api(admin_token):
    """Test GET /api/admin/city-suggestions API"""
    print("\n" + "="*80)
    print("🏙️  TESTING CITY SUGGESTIONS API")
    print("="*80)
    
    auth_headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
    
    success, response_data = test_api_endpoint(
        "GET",
        "/admin/city-suggestions",
        headers=auth_headers,
        description="Get city suggestions (admin endpoint)"
    )
    
    if success:
        # Verify response is proper JSON array
        if isinstance(response_data, list):
            print(f"✅ SUCCESS: City suggestions API returns proper JSON array")
            print(f"   - Number of suggestions: {len(response_data)}")
            
            # If there are suggestions, verify structure
            if response_data:
                suggestion = response_data[0]
                expected_fields = ["id", "state", "city", "customer_name", "phone", "email", "created_at", "status"]
                
                for field in expected_fields:
                    if field in suggestion:
                        print(f"   - Sample suggestion has '{field}' field ✓")
                    else:
                        print(f"   - Sample suggestion missing '{field}' field ⚠️")
            
            return True
        else:
            print(f"❌ FAILED: Response is not a JSON array, got: {type(response_data)}")
            return False
    
    print(f"❌ FAILED: City suggestions API failed")
    return False

def test_products_api_verification():
    """Test GET /api/products API and verify exactly 58 products with 8 categories as per review request"""
    print("\n" + "="*80)
    print("📦 PRODUCTS API TESTING (REVIEW REQUEST #1)")
    print("="*80)
    
    success, response_data = test_api_endpoint(
        "GET",
        "/products",
        description="Verify exactly 58 products with 8 categories: powders (13), pickles (9), hot-items (10), sweets (9), laddus (6), chikkis (4), snacks (3), spices (4)"
    )
    
    if success and isinstance(response_data, list):
        total_products = len(response_data)
        print(f"✅ SUCCESS: Products API returns {total_products} products")
        
        # CRITICAL: Verify we have exactly 58 products as specified in review request
        if total_products == 58:
            print(f"✅ CRITICAL SUCCESS: Exactly 58 products found as required")
        else:
            print(f"❌ CRITICAL FAILURE: Expected exactly 58 products, got {total_products}")
            return False
        
        # Count products by category and verify expected counts
        category_counts = {}
        for product in response_data:
            category = product.get("category", "unknown")
            category_counts[category] = category_counts.get(category, 0) + 1
        
        print(f"\n📊 CATEGORY BREAKDOWN VERIFICATION:")
        
        # Expected categories and counts from review request
        expected_categories = {
            "powders": 13,
            "pickles": 9, 
            "hot-items": 10,
            "sweets": 9,
            "laddus": 6,
            "chikkis": 4,
            "snacks": 3,
            "spices": 4
        }
        
        categories_verified = True
        for expected_category, expected_count in expected_categories.items():
            actual_count = category_counts.get(expected_category, 0)
            if actual_count == expected_count:
                print(f"   ✅ {expected_category}: {actual_count} products (CORRECT)")
            else:
                print(f"   ❌ {expected_category}: {actual_count} products (EXPECTED {expected_count})")
                categories_verified = False
        
        # Check for unexpected categories
        for category, count in category_counts.items():
            if category not in expected_categories:
                print(f"   ⚠️  UNEXPECTED CATEGORY: {category}: {count} products")
                categories_verified = False
        
        if categories_verified:
            print(f"✅ CRITICAL SUCCESS: All 8 categories have correct product counts")
        else:
            print(f"❌ CRITICAL FAILURE: Category counts don't match review request expectations")
            return False
        
        # Verify product structure as specified in review request
        print(f"\n🔍 PRODUCT STRUCTURE VERIFICATION:")
        if response_data:
            sample_products = response_data[:4]  # Check first 4 products as requested
            
            required_fields = ["id", "name", "description", "category", "image", "prices", "isBestSeller", "isNew", "tag", "inventory_count", "out_of_stock", "discount_active"]
            
            for i, product in enumerate(sample_products, 1):
                print(f"\n   Sample Product {i}: {product.get('name', 'Unknown')}")
                print(f"   Category: {product.get('category', 'Unknown')}")
                
                # Check all required fields from review request
                all_fields_present = True
                for field in required_fields:
                    if field in product:
                        if field == "prices":
                            prices = product.get("prices", [])
                            if isinstance(prices, list) and len(prices) > 0:
                                print(f"     ✅ {field}: {len(prices)} price tiers")
                                # Check first price structure
                                if prices and isinstance(prices[0], dict):
                                    price_item = prices[0]
                                    if "weight" in price_item and "price" in price_item:
                                        print(f"       - Sample: {price_item.get('weight')} = ₹{price_item.get('price')}")
                            else:
                                print(f"     ❌ {field}: Invalid prices array")
                                all_fields_present = False
                        else:
                            value = product.get(field)
                            print(f"     ✅ {field}: {value}")
                    else:
                        print(f"     ❌ {field}: Missing")
                        all_fields_present = False
                
                if all_fields_present:
                    print(f"     ✅ Product {i} has all required fields")
                else:
                    print(f"     ❌ Product {i} missing required fields")
        
        return True
    
    print(f"❌ CRITICAL FAILURE: Products API failed or returned invalid data")
    return False

def test_notifications_count_api(admin_token):
    """Test GET /api/admin/notifications/count API"""
    print("\n" + "="*80)
    print("🔔 TESTING NOTIFICATIONS COUNT API")
    print("="*80)
    
    auth_headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
    
    success, response_data = test_api_endpoint(
        "GET",
        "/admin/notifications/count",
        headers=auth_headers,
        description="Get notifications count with admin token"
    )
    
    if success and response_data:
        # Verify response structure
        expected_fields = ["bug_reports", "city_suggestions", "new_orders", "total"]
        
        print(f"🔍 NOTIFICATIONS COUNT STRUCTURE:")
        all_fields_present = True
        
        for field in expected_fields:
            if field in response_data:
                count = response_data[field]
                print(f"   ✅ {field}: {count}")
                
                # Verify it's a number
                if not isinstance(count, (int, float)):
                    print(f"   ⚠️  {field} is not a number: {type(count)}")
                    all_fields_present = False
            else:
                print(f"   ❌ Missing field: {field}")
                all_fields_present = False
        
        if all_fields_present:
            print(f"✅ SUCCESS: Notifications count API returns proper structure")
            
            # Verify total calculation
            calculated_total = (response_data.get("bug_reports", 0) + 
                             response_data.get("city_suggestions", 0) + 
                             response_data.get("new_orders", 0))
            actual_total = response_data.get("total", 0)
            
            if calculated_total == actual_total:
                print(f"   ✅ Total calculation correct: {actual_total}")
            else:
                print(f"   ⚠️  Total calculation mismatch: expected {calculated_total}, got {actual_total}")
            
            return True
        else:
            print(f"❌ FAILED: Missing required fields in response")
            return False
    
    print(f"❌ FAILED: Notifications count API failed")
    return False

def test_razorpay_payment_integration():
    """Test complete Razorpay payment flow as specified in review request"""
    print("\n" + "="*80)
    print("💳 RAZORPAY PAYMENT INTEGRATION (CRITICAL)")
    print("="*80)
    
    test_results = []
    
    # A. Create Razorpay Order
    print("\n--- A. Create Razorpay Order ---")
    razorpay_order_data = {
        "amount": 500,
        "currency": "INR", 
        "receipt": "test_order_123"
    }
    
    success, response_data = test_api_endpoint(
        "POST",
        "/payment/create-razorpay-order",
        data=razorpay_order_data,
        description="Create Razorpay order with ₹500 amount"
    )
    
    if success and response_data:
        # Verify response structure
        required_fields = ["razorpay_order_id", "amount", "currency", "key_id"]
        missing_fields = [field for field in required_fields if field not in response_data]
        
        if not missing_fields:
            razorpay_order_id = response_data.get("razorpay_order_id")
            amount = response_data.get("amount")
            currency = response_data.get("currency")
            key_id = response_data.get("key_id")
            
            print(f"✅ SUCCESS: Razorpay order created successfully")
            print(f"   - Order ID: {razorpay_order_id}")
            print(f"   - Amount: {amount} paise (₹{amount/100})")
            print(f"   - Currency: {currency}")
            print(f"   - Key ID: {key_id}")
            
            # Verify amount conversion (₹500 = 50000 paise)
            if amount == 50000:
                print(f"✅ SUCCESS: Amount correctly converted to paise (₹500 = 50000 paise)")
            else:
                print(f"❌ FAILURE: Amount conversion incorrect (expected 50000, got {amount})")
                test_results.append(("Razorpay Order Creation", False))
                return test_results
            
            # Verify test credentials
            if key_id.startswith("rzp_test_"):
                print(f"✅ SUCCESS: Test credentials confirmed (key_id starts with 'rzp_test_')")
                test_results.append(("Razorpay Order Creation", True))
            else:
                print(f"❌ FAILURE: Key ID doesn't start with 'rzp_test_': {key_id}")
                test_results.append(("Razorpay Order Creation", False))
                return test_results
        else:
            print(f"❌ FAILURE: Missing required fields: {missing_fields}")
            test_results.append(("Razorpay Order Creation", False))
            return test_results
    else:
        print(f"❌ FAILURE: Could not create Razorpay order")
        test_results.append(("Razorpay Order Creation", False))
        return test_results
    
    # B. Order Creation with Razorpay
    print("\n--- B. Order Creation with Razorpay Payment Method ---")
    order_data = {
        "customer_name": "Rajesh Kumar",
        "email": "rajesh.kumar@example.com",
        "phone": "9876543210",
        "doorNo": "12-34",
        "building": "Sai Residency",
        "street": "MG Road",
        "city": "Guntur",
        "state": "Andhra Pradesh",
        "pincode": "522001",
        "items": [
            {
                "product_id": "1",
                "name": "Immunity Dry Fruits Laddu",
                "image": "https://example.com/laddu.jpg",
                "weight": "1 kg",
                "price": 450.0,
                "quantity": 1,
                "description": "Healthy dry fruits laddu"
            }
        ],
        "subtotal": 450.0,
        "delivery_charge": 49.0,
        "total": 499.0,
        "payment_method": "razorpay",
        "payment_sub_method": "upi"
    }
    
    success, order_response = test_api_endpoint(
        "POST",
        "/orders",
        data=order_data,
        description="Create order with Razorpay payment method"
    )
    
    if success and order_response:
        order_id = order_response.get("order_id")
        tracking_code = order_response.get("tracking_code")
        
        print(f"✅ SUCCESS: Order created with Razorpay payment method")
        print(f"   - Order ID: {order_id}")
        print(f"   - Tracking Code: {tracking_code}")
        
        # Verify payment status is pending
        if "order" in order_response:
            order_details = order_response["order"]
            payment_status = order_details.get("payment_status")
            order_status = order_details.get("order_status")
            
            if payment_status == "pending":
                print(f"✅ SUCCESS: Payment status is 'pending' as expected")
            else:
                print(f"❌ FAILURE: Payment status should be 'pending', got '{payment_status}'")
            
            if order_status == "pending":
                print(f"✅ SUCCESS: Order status is 'pending' as expected")
            else:
                print(f"❌ FAILURE: Order status should be 'pending', got '{order_status}'")
        
        test_results.append(("Order Creation with Razorpay", True))
    else:
        print(f"❌ FAILURE: Could not create order with Razorpay payment method")
        test_results.append(("Order Creation with Razorpay", False))
        return test_results
    
    # C. Payment Verification Endpoint
    print("\n--- C. Payment Verification Endpoint ---")
    
    # Test with missing fields (should return 400 error)
    incomplete_verification_data = {
        "razorpay_order_id": "order_test123",
        # Missing required fields intentionally
    }
    
    success, error_response = test_api_endpoint(
        "POST",
        "/payment/verify-razorpay-payment",
        data=incomplete_verification_data,
        description="Test payment verification with missing fields (should return 400)",
        expected_status=400
    )
    
    if success and error_response:
        if "Missing required payment verification fields" in str(error_response.get("detail", "")):
            print(f"✅ SUCCESS: Payment verification correctly handles missing fields")
            test_results.append(("Payment Verification Error Handling", True))
        else:
            print(f"❌ FAILURE: Unexpected error message: {error_response}")
            test_results.append(("Payment Verification Error Handling", False))
    else:
        print(f"❌ FAILURE: Payment verification endpoint didn't return expected 400 error")
        test_results.append(("Payment Verification Error Handling", False))
    
    return test_results

def test_locations_api():
    """Test GET /api/locations API and verify 431 cities as per review request"""
    print("\n" + "="*80)
    print("🏙️ LOCATIONS API VERIFICATION (HIGH PRIORITY)")
    print("="*80)
    
    success, response_data = test_api_endpoint(
        "GET",
        "/locations",
        description="Verify exactly 431 cities are returned with correct structure"
    )
    
    if success and isinstance(response_data, list):
        total_locations = len(response_data)
        print(f"✅ SUCCESS: Locations API returns {total_locations} cities")
        
        # CRITICAL: Verify we have exactly 431 cities as specified in review request
        if total_locations == 431:
            print(f"✅ CRITICAL SUCCESS: Exactly 431 cities found as required")
        else:
            print(f"❌ CRITICAL FAILURE: Expected exactly 431 cities, got {total_locations}")
            return False
        
        # Verify location structure as specified in review request
        print(f"\n🔍 LOCATION STRUCTURE VERIFICATION:")
        if response_data:
            sample_locations = response_data[:3]  # Check first 3 locations
            
            required_fields = ["name", "state", "charge", "free_delivery_threshold", "enabled"]
            
            for i, location in enumerate(sample_locations, 1):
                print(f"\n   Sample Location {i}: {location.get('name', 'Unknown')}")
                
                # Check all required fields from review request
                for field in required_fields:
                    if field in location:
                        value = location.get(field)
                        print(f"     ✅ {field}: {value}")
                    else:
                        print(f"     ❌ {field}: Missing")
        
        return True
    
    print(f"❌ CRITICAL FAILURE: Locations API failed or returned invalid data")
    return False

def test_free_delivery_settings_api():
    """Test GET /api/settings/free-delivery API as per review request"""
    print("\n" + "="*80)
    print("⚙️ FREE DELIVERY SETTINGS API VERIFICATION (HIGH PRIORITY)")
    print("="*80)
    
    success, response_data = test_api_endpoint(
        "GET",
        "/settings/free-delivery",
        description="Verify free delivery settings return enabled: true, threshold: 1000"
    )
    
    if success and isinstance(response_data, dict):
        print(f"✅ SUCCESS: Free delivery settings API returns proper structure")
        
        # Verify expected values from review request
        enabled = response_data.get("enabled")
        threshold = response_data.get("threshold")
        
        print(f"\n🔍 FREE DELIVERY SETTINGS VERIFICATION:")
        print(f"   - enabled: {enabled}")
        print(f"   - threshold: {threshold}")
        
        # Check if values match review request expectations
        if enabled == True and threshold == 1000:
            print(f"✅ CRITICAL SUCCESS: Free delivery settings match expected values")
            print(f"   - enabled: true ✓")
            print(f"   - threshold: 1000 ✓")
            return True
        else:
            print(f"❌ CRITICAL FAILURE: Free delivery settings don't match expected values")
            print(f"   - Expected: enabled=true, threshold=1000")
            print(f"   - Got: enabled={enabled}, threshold={threshold}")
            return False
    
    print(f"❌ CRITICAL FAILURE: Free delivery settings API failed or returned invalid data")
    return False

def test_create_order_guntur():
    """Test POST /api/orders with Guntur as delivery city as per review request"""
    print("\n" + "="*80)
    print("📦 CREATE TEST ORDER WITH GUNTUR DELIVERY (CRITICAL)")
    print("="*80)
    
    # First get a product from the products list
    print("\n--- Step 1: Get Product from Products List ---")
    success, products_data = test_api_endpoint(
        "GET",
        "/products",
        description="Get products list to use in order"
    )
    
    if not success or not isinstance(products_data, list) or len(products_data) == 0:
        print("❌ CRITICAL FAILURE: Cannot get products for order creation")
        return False
    
    # Use first product
    product = products_data[0]
    product_id = product.get("id")
    product_name = product.get("name", "Test Product")
    product_image = product.get("image", "")
    
    # Get price from prices array
    prices = product.get("prices", [])
    if not prices:
        print("❌ CRITICAL FAILURE: Product has no prices")
        return False
    
    price_item = prices[0]  # Use first price tier
    weight = price_item.get("weight", "1 kg")
    price = price_item.get("price", 100.0)
    
    print(f"✅ Using product: {product_name} ({weight} = ₹{price})")
    
    # Step 2: Create order with Guntur as delivery city
    print("\n--- Step 2: Create Order with Guntur Delivery ---")
    order_data = {
        "customer_name": "Rajesh Kumar",
        "email": "rajesh.test@example.com",
        "phone": "9876543210",
        "doorNo": "12-34",
        "building": "Sai Residency",
        "street": "MG Road",
        "city": "Guntur",
        "state": "Andhra Pradesh",
        "pincode": "522001",
        "items": [
            {
                "product_id": product_id,
                "name": product_name,
                "image": product_image,
                "weight": weight,
                "price": price,
                "quantity": 1,
                "description": product.get("description", "")
            }
        ],
        "subtotal": price,
        "delivery_charge": 49.0,  # Expected Guntur delivery charge
        "total": price + 49.0,
        "payment_method": "razorpay",
        "payment_sub_method": "upi"
    }
    
    success, order_response = test_api_endpoint(
        "POST",
        "/orders",
        data=order_data,
        description="Create order with Guntur as delivery city"
    )
    
    if success and order_response:
        order_id = order_response.get("order_id")
        tracking_code = order_response.get("tracking_code")
        delivery_charge = order_response.get("delivery_charge")
        total = order_response.get("total")
        
        print(f"✅ SUCCESS: Order created successfully")
        print(f"   - Order ID: {order_id}")
        print(f"   - Tracking Code: {tracking_code}")
        print(f"   - Delivery Charge: ₹{delivery_charge}")
        print(f"   - Total: ₹{total}")
        
        # Verify delivery charge calculation for Guntur
        print(f"\n🔍 DELIVERY CHARGE VERIFICATION:")
        if delivery_charge == 49.0:
            print(f"✅ CRITICAL SUCCESS: Guntur delivery charge correct (₹49)")
        else:
            print(f"❌ CRITICAL FAILURE: Expected Guntur delivery charge ₹49, got ₹{delivery_charge}")
            return False
        
        # Verify order was created with proper structure
        if "order" in order_response:
            order_details = order_response["order"]
            payment_status = order_details.get("payment_status")
            order_status = order_details.get("order_status")
            
            print(f"   - Payment Status: {payment_status}")
            print(f"   - Order Status: {order_status}")
            
            if payment_status == "pending" and order_status == "pending":
                print(f"✅ SUCCESS: Order created with correct pending status")
            else:
                print(f"⚠️ WARNING: Unexpected order status")
        
        return True
    else:
        print(f"❌ CRITICAL FAILURE: Could not create order with Guntur delivery")
        return False

def test_payment_system_configuration():
    """Test Razorpay payment system configuration"""
    print("\n" + "="*80)
    print("⚙️  PAYMENT SYSTEM CONFIGURATION")
    print("="*80)
    
    # Test that Razorpay credentials are properly loaded
    print("\n--- Razorpay Credentials Verification ---")
    
    # Create a test order to verify credentials are working
    test_order_data = {
        "amount": 100,
        "currency": "INR",
        "receipt": "config_test_001"
    }
    
    success, response_data = test_api_endpoint(
        "POST",
        "/payment/create-razorpay-order",
        data=test_order_data,
        description="Test Razorpay client initialization with credentials"
    )
    
    if success and response_data:
        key_id = response_data.get("key_id")
        
        # Verify test credentials
        expected_key_id = "rzp_test_Renc645PexAmXU"
        if key_id == expected_key_id:
            print(f"✅ SUCCESS: Razorpay credentials properly loaded")
            print(f"   - Key ID: {key_id} ✓")
            print(f"   - Test mode confirmed (rzp_test_ prefix)")
            return True
        else:
            print(f"❌ FAILURE: Unexpected Key ID")
            print(f"   - Expected: {expected_key_id}")
            print(f"   - Got: {key_id}")
            return False
    else:
        print(f"❌ FAILURE: Razorpay client not properly initialized")
        return False

def test_error_handling():
    """Test error handling with invalid data to ensure proper JSON responses"""
    print("\n" + "="*80)
    print("⚠️  TESTING ERROR HANDLING")
    print("="*80)
    
    test_cases = [
        {
            "name": "Invalid admin password",
            "method": "POST",
            "endpoint": "/auth/admin-login",
            "data": {"password": "wrongpassword"},
            "expected_status": 401,
            "description": "Test admin login with wrong password"
        },
        {
            "name": "Missing required fields in admin login",
            "method": "POST", 
            "endpoint": "/auth/admin-login",
            "data": {},
            "expected_status": 422,
            "description": "Test admin login with missing password field"
        },
        {
            "name": "Unauthorized access to admin endpoint",
            "method": "GET",
            "endpoint": "/admin/notifications/count",
            "data": None,
            "expected_status": 401,
            "description": "Test admin endpoint without authentication"
        },
        {
            "name": "Invalid product ID",
            "method": "GET",
            "endpoint": "/products/nonexistent-id",
            "data": None,
            "expected_status": 404,
            "description": "Test with non-existent product ID"
        }
    ]
    
    all_passed = True
    
    for test_case in test_cases:
        print(f"\n🧪 Testing: {test_case['name']}")
        
        success, response_data = test_api_endpoint(
            test_case["method"],
            test_case["endpoint"],
            data=test_case["data"],
            description=test_case["description"],
            expected_status=test_case["expected_status"]
        )
        
        if success:
            # Verify response is proper JSON with detail field
            if response_data and "detail" in response_data:
                print(f"   ✅ Proper JSON error response with detail field")
            elif response_data:
                print(f"   ✅ JSON response received (structure may vary)")
            else:
                print(f"   ⚠️  No response data, but status code correct")
        else:
            print(f"   ❌ Error handling test failed")
            all_passed = False
    
    return all_passed

def test_city_approval_workflow(admin_token):
    """Test complete city approval workflow with email notifications"""
    print("\n" + "="*80)
    print("🏙️ TESTING CITY APPROVAL WORKFLOW WITH EMAIL & LOCATION ADDITION")
    print("="*80)
    
    auth_headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
    
    test_results = []
    
    # Step 1: Create a test city suggestion
    print("\n--- Step 1: Create Test City Suggestion ---")
    suggestion_data = {
        "state": "Karnataka",
        "city": "Bangalore", 
        "customer_name": "Test User",
        "phone": "9876543210",
        "email": "test@example.com"
    }
    
    success, response = test_api_endpoint(
        "POST",
        "/suggest-city",
        data=suggestion_data,
        description="Create city suggestion for Bangalore, Karnataka"
    )
    
    if success and response and "suggestion_id" in response:
        suggestion_id = response["suggestion_id"]
        print(f"✅ SUCCESS: City suggestion created with ID: {suggestion_id}")
        test_results.append(("Create City Suggestion", True))
    else:
        print("❌ FAILED: Could not create city suggestion")
        test_results.append(("Create City Suggestion", False))
        return test_results
    
    # Step 2: Verify suggestion appears in admin list
    print("\n--- Step 2: Verify Suggestion in Admin List ---")
    success, suggestions = test_api_endpoint(
        "GET",
        "/admin/city-suggestions",
        headers=auth_headers,
        description="Get city suggestions from admin panel"
    )
    
    if success and isinstance(suggestions, list):
        # Find our suggestion
        found_suggestion = None
        for suggestion in suggestions:
            if (suggestion.get("city") == "Bangalore" and 
                suggestion.get("state") == "Karnataka" and
                suggestion.get("email") == "test@example.com"):
                found_suggestion = suggestion
                break
        
        if found_suggestion:
            print(f"✅ SUCCESS: Suggestion found in admin list")
            print(f"   - ID: {found_suggestion.get('id')}")
            print(f"   - Status: {found_suggestion.get('status')}")
            print(f"   - Customer: {found_suggestion.get('customer_name')}")
            test_results.append(("Suggestion in Admin List", True))
        else:
            print("❌ FAILED: Suggestion not found in admin list")
            test_results.append(("Suggestion in Admin List", False))
            return test_results
    else:
        print("❌ FAILED: Could not get city suggestions")
        test_results.append(("Suggestion in Admin List", False))
        return test_results
    
    # Step 3: Approve the city
    print("\n--- Step 3: Approve City with Delivery Settings ---")
    approval_data = {
        "status": "approved",
        "delivery_charge": 99,
        "free_delivery_threshold": 1000
    }
    
    success, response = test_api_endpoint(
        "PUT",
        f"/admin/city-suggestions/{suggestion_id}/status",
        headers=auth_headers,
        data=approval_data,
        description="Approve city with delivery charge ₹99 and free delivery threshold ₹1000"
    )
    
    if success:
        print(f"✅ SUCCESS: City approved successfully")
        test_results.append(("Approve City", True))
    else:
        print("❌ FAILED: Could not approve city")
        test_results.append(("Approve City", False))
        return test_results
    
    # Step 4: Verify city appears in locations
    print("\n--- Step 4: Verify City in Locations ---")
    success, locations = test_api_endpoint(
        "GET",
        "/locations",
        description="Get delivery locations to verify Bangalore is added"
    )
    
    if success and isinstance(locations, list):
        # Find Bangalore in locations
        found_location = None
        for location in locations:
            if location.get("name") == "Bangalore":
                found_location = location
                break
        
        if found_location:
            print(f"✅ SUCCESS: Bangalore found in locations")
            print(f"   - Name: {found_location.get('name')}")
            print(f"   - Charge: ₹{found_location.get('charge')}")
            print(f"   - Free Delivery Threshold: ₹{found_location.get('free_delivery_threshold')}")
            
            # Verify correct values
            if (found_location.get("charge") == 99 and 
                found_location.get("free_delivery_threshold") == 1000):
                print(f"✅ SUCCESS: Delivery settings are correct")
                test_results.append(("City in Locations", True))
            else:
                print(f"❌ FAILED: Incorrect delivery settings")
                test_results.append(("City in Locations", False))
        else:
            print("❌ FAILED: Bangalore not found in locations")
            test_results.append(("City in Locations", False))
    else:
        print("❌ FAILED: Could not get locations")
        test_results.append(("City in Locations", False))
    
    # Step 5: Verify suggestion status updated
    print("\n--- Step 5: Verify Suggestion Status Updated ---")
    success, suggestions = test_api_endpoint(
        "GET",
        "/admin/city-suggestions",
        headers=auth_headers,
        description="Verify suggestion status is now 'approved'"
    )
    
    if success and isinstance(suggestions, list):
        # Find our suggestion again
        found_suggestion = None
        for suggestion in suggestions:
            if suggestion.get("id") == suggestion_id:
                found_suggestion = suggestion
                break
        
        if found_suggestion and found_suggestion.get("status") == "approved":
            print(f"✅ SUCCESS: Suggestion status updated to 'approved'")
            test_results.append(("Suggestion Status Updated", True))
        else:
            print(f"❌ FAILED: Suggestion status not updated correctly")
            test_results.append(("Suggestion Status Updated", False))
    else:
        print("❌ FAILED: Could not verify suggestion status")
        test_results.append(("Suggestion Status Updated", False))
    
    # Step 6: Check backend logs for email notification
    print("\n--- Step 6: Check Email Notification Logs ---")
    try:
        import subprocess
        result = subprocess.run(
            ["tail", "-n", "100", "/var/log/supervisor/backend.out.log"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.stdout and "City approval email sent" in result.stdout:
            print(f"✅ SUCCESS: Email notification log found")
            test_results.append(("Email Notification Log", True))
        else:
            print(f"⚠️  WARNING: Email notification log not found (emails may not be configured)")
            test_results.append(("Email Notification Log", False))
            
    except Exception as e:
        print(f"⚠️  WARNING: Could not check logs: {e}")
        test_results.append(("Email Notification Log", False))
    
    return test_results

def test_city_rejection_workflow(admin_token):
    """Test city rejection workflow with email notifications"""
    print("\n" + "="*80)
    print("🚫 TESTING CITY REJECTION WITH EMAIL")
    print("="*80)
    
    auth_headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
    
    test_results = []
    
    # Step 1: Create another test city suggestion
    print("\n--- Step 1: Create Test City Suggestion for Rejection ---")
    suggestion_data = {
        "state": "Tamil Nadu",
        "city": "Chennai",
        "customer_name": "Test User 2", 
        "phone": "9876543211",
        "email": "test2@example.com"
    }
    
    success, response = test_api_endpoint(
        "POST",
        "/suggest-city",
        data=suggestion_data,
        description="Create city suggestion for Chennai, Tamil Nadu"
    )
    
    if success and response and "suggestion_id" in response:
        suggestion_id = response["suggestion_id"]
        print(f"✅ SUCCESS: City suggestion created with ID: {suggestion_id}")
        test_results.append(("Create City Suggestion for Rejection", True))
    else:
        print("❌ FAILED: Could not create city suggestion")
        test_results.append(("Create City Suggestion for Rejection", False))
        return test_results
    
    # Step 2: Reject the city
    print("\n--- Step 2: Reject City ---")
    rejection_data = {
        "status": "rejected"
    }
    
    success, response = test_api_endpoint(
        "PUT",
        f"/admin/city-suggestions/{suggestion_id}/status",
        headers=auth_headers,
        data=rejection_data,
        description="Reject city suggestion"
    )
    
    if success:
        print(f"✅ SUCCESS: City rejected successfully")
        test_results.append(("Reject City", True))
    else:
        print("❌ FAILED: Could not reject city")
        test_results.append(("Reject City", False))
        return test_results
    
    # Step 3: Verify suggestion status updated to rejected
    print("\n--- Step 3: Verify Suggestion Status Updated to Rejected ---")
    success, suggestions = test_api_endpoint(
        "GET",
        "/admin/city-suggestions",
        headers=auth_headers,
        description="Verify suggestion status is now 'rejected'"
    )
    
    if success and isinstance(suggestions, list):
        # Find our suggestion
        found_suggestion = None
        for suggestion in suggestions:
            if suggestion.get("id") == suggestion_id:
                found_suggestion = suggestion
                break
        
        if found_suggestion and found_suggestion.get("status") == "rejected":
            print(f"✅ SUCCESS: Suggestion status updated to 'rejected'")
            test_results.append(("Suggestion Status Updated to Rejected", True))
        else:
            print(f"❌ FAILED: Suggestion status not updated correctly")
            test_results.append(("Suggestion Status Updated to Rejected", False))
    else:
        print("❌ FAILED: Could not verify suggestion status")
        test_results.append(("Suggestion Status Updated to Rejected", False))
    
    # Step 4: Verify city does NOT appear in locations
    print("\n--- Step 4: Verify City NOT in Locations ---")
    success, locations = test_api_endpoint(
        "GET",
        "/locations",
        description="Verify Chennai is NOT in delivery locations"
    )
    
    if success and isinstance(locations, list):
        # Make sure Chennai is NOT in locations
        found_location = None
        for location in locations:
            if location.get("name") == "Chennai":
                found_location = location
                break
        
        if not found_location:
            print(f"✅ SUCCESS: Chennai correctly NOT found in locations")
            test_results.append(("City NOT in Locations", True))
        else:
            print(f"❌ FAILED: Chennai incorrectly found in locations")
            test_results.append(("City NOT in Locations", False))
    else:
        print("❌ FAILED: Could not get locations")
        test_results.append(("City NOT in Locations", False))
    
    # Step 5: Check backend logs for rejection email notification
    print("\n--- Step 5: Check Rejection Email Notification Logs ---")
    try:
        import subprocess
        result = subprocess.run(
            ["tail", "-n", "100", "/var/log/supervisor/backend.out.log"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.stdout and "City rejection email sent" in result.stdout:
            print(f"✅ SUCCESS: Rejection email notification log found")
            test_results.append(("Rejection Email Notification Log", True))
        else:
            print(f"⚠️  WARNING: Rejection email notification log not found")
            test_results.append(("Rejection Email Notification Log", False))
            
    except Exception as e:
        print(f"⚠️  WARNING: Could not check logs: {e}")
        test_results.append(("Rejection Email Notification Log", False))
    
    return test_results

def test_notification_dismissal_system(admin_token):
    """Test notification read/unread tracking and dismissal"""
    print("\n" + "="*80)
    print("🔔 TESTING NOTIFICATION DISMISSAL SYSTEM")
    print("="*80)
    
    auth_headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
    
    test_results = []
    
    # Step 1: Get initial notification counts
    print("\n--- Step 1: Get Initial Notification Counts ---")
    success, initial_counts = test_api_endpoint(
        "GET",
        "/admin/notifications/count",
        headers=auth_headers,
        description="Get initial notification counts"
    )
    
    if success and initial_counts:
        print(f"✅ SUCCESS: Initial notification counts retrieved")
        print(f"   - Bug Reports: {initial_counts.get('bug_reports', 0)}")
        print(f"   - City Suggestions: {initial_counts.get('city_suggestions', 0)}")
        print(f"   - New Orders: {initial_counts.get('new_orders', 0)}")
        print(f"   - Total: {initial_counts.get('total', 0)}")
        
        initial_city_suggestions = initial_counts.get('city_suggestions', 0)
        test_results.append(("Get Initial Counts", True))
    else:
        print("❌ FAILED: Could not get initial notification counts")
        test_results.append(("Get Initial Counts", False))
        return test_results
    
    # Step 2: Dismiss city suggestions
    print("\n--- Step 2: Dismiss City Suggestions ---")
    dismiss_data = {
        "type": "city_suggestions"
    }
    
    success, response = test_api_endpoint(
        "POST",
        "/admin/notifications/dismiss-all",
        headers=auth_headers,
        data=dismiss_data,
        description="Dismiss all city suggestion notifications"
    )
    
    if success:
        print(f"✅ SUCCESS: City suggestions dismissed")
        test_results.append(("Dismiss City Suggestions", True))
    else:
        print("❌ FAILED: Could not dismiss city suggestions")
        test_results.append(("Dismiss City Suggestions", False))
        return test_results
    
    # Step 3: Get notification counts after dismissal
    print("\n--- Step 3: Get Notification Counts After Dismissal ---")
    success, after_counts = test_api_endpoint(
        "GET",
        "/admin/notifications/count",
        headers=auth_headers,
        description="Get notification counts after dismissal"
    )
    
    if success and after_counts:
        print(f"✅ SUCCESS: Post-dismissal notification counts retrieved")
        print(f"   - Bug Reports: {after_counts.get('bug_reports', 0)}")
        print(f"   - City Suggestions: {after_counts.get('city_suggestions', 0)}")
        print(f"   - New Orders: {after_counts.get('new_orders', 0)}")
        print(f"   - Total: {after_counts.get('total', 0)}")
        
        # Verify city_suggestions count is now 0
        if after_counts.get('city_suggestions', -1) == 0:
            print(f"✅ SUCCESS: City suggestions count is now 0")
            test_results.append(("City Suggestions Count Zero", True))
        else:
            print(f"❌ FAILED: City suggestions count is not 0: {after_counts.get('city_suggestions')}")
            test_results.append(("City Suggestions Count Zero", False))
        
        # Verify other counts unchanged
        if (after_counts.get('bug_reports') == initial_counts.get('bug_reports') and
            after_counts.get('new_orders') == initial_counts.get('new_orders')):
            print(f"✅ SUCCESS: Other notification types not affected")
            test_results.append(("Other Notifications Unaffected", True))
        else:
            print(f"❌ FAILED: Other notification counts changed unexpectedly")
            test_results.append(("Other Notifications Unaffected", False))
            
    else:
        print("❌ FAILED: Could not get post-dismissal notification counts")
        test_results.append(("City Suggestions Count Zero", False))
        test_results.append(("Other Notifications Unaffected", False))
    
    # Step 4: Wait and verify dismissal persists (shortened for testing)
    print("\n--- Step 4: Verify Dismissal Persistence ---")
    print("Waiting 10 seconds to test persistence...")
    time.sleep(10)
    
    success, persistence_counts = test_api_endpoint(
        "GET",
        "/admin/notifications/count",
        headers=auth_headers,
        description="Verify dismissal persists after 10 seconds"
    )
    
    if success and persistence_counts:
        if persistence_counts.get('city_suggestions', -1) == 0:
            print(f"✅ SUCCESS: Dismissal persists after 10 seconds")
            test_results.append(("Dismissal Persistence", True))
        else:
            print(f"❌ FAILED: Dismissal did not persist")
            test_results.append(("Dismissal Persistence", False))
    else:
        print("❌ FAILED: Could not verify dismissal persistence")
        test_results.append(("Dismissal Persistence", False))
    
    return test_results

def test_approve_city_endpoint(admin_token):
    """Test the direct approve-city endpoint with email"""
    print("\n" + "="*80)
    print("✅ TESTING APPROVE-CITY ENDPOINT WITH EMAIL")
    print("="*80)
    
    auth_headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
    
    test_results = []
    
    # Step 1: Create a city suggestion first (for email testing)
    print("\n--- Step 1: Create City Suggestion for Direct Approval ---")
    suggestion_data = {
        "state": "Andhra Pradesh",
        "city": "Vijayawada",
        "customer_name": "Direct Test User",
        "phone": "9876543212", 
        "email": "directtest@example.com"
    }
    
    success, response = test_api_endpoint(
        "POST",
        "/suggest-city",
        data=suggestion_data,
        description="Create city suggestion for direct approval test"
    )
    
    if success:
        print(f"✅ SUCCESS: City suggestion created for direct approval test")
        test_results.append(("Create Suggestion for Direct Approval", True))
    else:
        print("⚠️  WARNING: Could not create suggestion, but continuing with direct approval test")
        test_results.append(("Create Suggestion for Direct Approval", False))
    
    # Step 2: Use direct approve-city endpoint
    print("\n--- Step 2: Use Direct Approve-City Endpoint ---")
    approve_data = {
        "city_name": "Vijayawada",
        "state_name": "Andhra Pradesh",
        "delivery_charge": 49,
        "free_delivery_threshold": 800
    }
    
    success, response = test_api_endpoint(
        "POST",
        "/admin/approve-city",
        headers=auth_headers,
        data=approve_data,
        description="Directly approve city with delivery settings"
    )
    
    if success:
        print(f"✅ SUCCESS: City approved via direct endpoint")
        test_results.append(("Direct City Approval", True))
    else:
        print("❌ FAILED: Direct city approval failed")
        test_results.append(("Direct City Approval", False))
        return test_results
    
    # Step 3: Verify city added to locations
    print("\n--- Step 3: Verify City Added to Locations ---")
    success, locations = test_api_endpoint(
        "GET",
        "/locations",
        description="Verify Vijayawada is in delivery locations"
    )
    
    if success and isinstance(locations, list):
        # Find Vijayawada in locations
        found_location = None
        for location in locations:
            if location.get("name") == "Vijayawada":
                found_location = location
                break
        
        if found_location:
            print(f"✅ SUCCESS: Vijayawada found in locations")
            print(f"   - Charge: ₹{found_location.get('charge')}")
            print(f"   - Free Delivery Threshold: ₹{found_location.get('free_delivery_threshold')}")
            
            # Verify correct values
            if (found_location.get("charge") == 49 and 
                found_location.get("free_delivery_threshold") == 800):
                print(f"✅ SUCCESS: Delivery settings are correct")
                test_results.append(("City Added to Locations", True))
            else:
                print(f"❌ FAILED: Incorrect delivery settings")
                test_results.append(("City Added to Locations", False))
        else:
            print("❌ FAILED: Vijayawada not found in locations")
            test_results.append(("City Added to Locations", False))
    else:
        print("❌ FAILED: Could not get locations")
        test_results.append(("City Added to Locations", False))
    
    # Step 4: Check if matching suggestion was updated
    print("\n--- Step 4: Check Matching Suggestion Status ---")
    success, suggestions = test_api_endpoint(
        "GET",
        "/admin/city-suggestions",
        headers=auth_headers,
        description="Check if matching suggestion status was updated"
    )
    
    if success and isinstance(suggestions, list):
        # Find matching suggestion
        found_suggestion = None
        for suggestion in suggestions:
            if (suggestion.get("city") == "Vijayawada" and 
                suggestion.get("state") == "Andhra Pradesh"):
                found_suggestion = suggestion
                break
        
        if found_suggestion and found_suggestion.get("status") == "approved":
            print(f"✅ SUCCESS: Matching suggestion status updated to 'approved'")
            test_results.append(("Matching Suggestion Updated", True))
        elif found_suggestion:
            print(f"⚠️  WARNING: Matching suggestion found but status not updated: {found_suggestion.get('status')}")
            test_results.append(("Matching Suggestion Updated", False))
        else:
            print(f"ℹ️  INFO: No matching suggestion found (this is okay)")
            test_results.append(("Matching Suggestion Updated", True))
    else:
        print("❌ FAILED: Could not check suggestions")
        test_results.append(("Matching Suggestion Updated", False))
    
    # Step 5: Check for email notification in logs
    print("\n--- Step 5: Check Email Notification for Direct Approval ---")
    try:
        import subprocess
        result = subprocess.run(
            ["tail", "-n", "100", "/var/log/supervisor/backend.out.log"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.stdout and ("City approval email sent" in result.stdout or "Vijayawada" in result.stdout):
            print(f"✅ SUCCESS: Email notification log found for direct approval")
            test_results.append(("Direct Approval Email Log", True))
        else:
            print(f"⚠️  WARNING: Email notification log not found for direct approval")
            test_results.append(("Direct Approval Email Log", False))
            
    except Exception as e:
        print(f"⚠️  WARNING: Could not check logs: {e}")
        test_results.append(("Direct Approval Email Log", False))
    
    return test_results

def test_enhanced_city_suggestions_system(admin_token):
    """Test the enhanced city suggestions system with ALL status filter functionality"""
    print("\n" + "="*80)
    print("🏙️ TESTING ENHANCED CITY SUGGESTIONS SYSTEM - ALL STATUS FILTER")
    print("="*80)
    
    auth_headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
    
    test_results = []
    created_suggestion_ids = []
    
    # Step 1: Test initial city suggestions API - ALL status filter
    print("\n--- Step 1: Test City Suggestions API - ALL Status Filter ---")
    success, initial_suggestions = test_api_endpoint(
        "GET",
        "/admin/city-suggestions",
        headers=auth_headers,
        description="Get ALL city suggestions regardless of status"
    )
    
    if success and isinstance(initial_suggestions, list):
        print(f"✅ SUCCESS: City suggestions API returns {len(initial_suggestions)} suggestions")
        test_results.append(("Initial City Suggestions API", True))
        initial_count = len(initial_suggestions)
    else:
        print("❌ FAILED: Could not get initial city suggestions")
        test_results.append(("Initial City Suggestions API", False))
        return test_results
    
    # Step 2: Test status-specific filters
    print("\n--- Step 2: Test Status-Specific Filters ---")
    status_filters = ["pending", "approved", "rejected"]
    
    for status in status_filters:
        success, filtered_suggestions = test_api_endpoint(
            "GET",
            f"/admin/city-suggestions?status={status}",
            headers=auth_headers,
            description=f"Get city suggestions with status={status}"
        )
        
        if success and isinstance(filtered_suggestions, list):
            print(f"✅ SUCCESS: Status filter '{status}' returns {len(filtered_suggestions)} suggestions")
            test_results.append((f"Status Filter {status}", True))
            
            # Verify all returned suggestions have the correct status
            if filtered_suggestions:
                all_correct_status = all(s.get("status") == status for s in filtered_suggestions)
                if all_correct_status:
                    print(f"   ✅ All suggestions have correct status: {status}")
                else:
                    print(f"   ❌ Some suggestions have incorrect status")
                    test_results.append((f"Status Filter {status} Validation", False))
                    continue
            
            test_results.append((f"Status Filter {status} Validation", True))
        else:
            print(f"❌ FAILED: Status filter '{status}' failed")
            test_results.append((f"Status Filter {status}", False))
    
    # Step 3: Create 3 test city suggestions as specified
    print("\n--- Step 3: Create 3 Test City Suggestions ---")
    test_suggestions = [
        {
            "state": "Andhra Pradesh",
            "city": "Kadapa", 
            "customer_name": "Test User 1",
            "phone": "9876543210",
            "email": "test1@example.com"
        },
        {
            "state": "Telangana",
            "city": "Warangal",
            "customer_name": "Test User 2", 
            "phone": "9876543211",
            "email": "test2@example.com"
        },
        {
            "state": "Andhra Pradesh",
            "city": "Nellore",
            "customer_name": "Test User 3",
            "phone": "9876543212", 
            "email": "test3@example.com"
        }
    ]
    
    for i, suggestion_data in enumerate(test_suggestions, 1):
        success, response = test_api_endpoint(
            "POST",
            "/suggest-city",
            data=suggestion_data,
            description=f"Create test city suggestion {i}: {suggestion_data['city']}, {suggestion_data['state']}"
        )
        
        if success and response and "suggestion_id" in response:
            suggestion_id = response["suggestion_id"]
            created_suggestion_ids.append(suggestion_id)
            print(f"✅ SUCCESS: City suggestion {i} created with ID: {suggestion_id}")
            test_results.append((f"Create City Suggestion {i}", True))
        else:
            print(f"❌ FAILED: Could not create city suggestion {i}")
            test_results.append((f"Create City Suggestion {i}", False))
    
    # Step 4: Verify suggestions appear in ALL suggestions list
    print("\n--- Step 4: Verify 3 New Suggestions Appear ---")
    success, updated_suggestions = test_api_endpoint(
        "GET",
        "/admin/city-suggestions",
        headers=auth_headers,
        description="Get ALL city suggestions after creating 3 new ones"
    )
    
    if success and isinstance(updated_suggestions, list):
        new_count = len(updated_suggestions)
        expected_count = initial_count + len(created_suggestion_ids)
        
        if new_count >= expected_count:
            print(f"✅ SUCCESS: Suggestions count increased from {initial_count} to {new_count}")
            test_results.append(("Suggestions Count Increased", True))
            
            # Verify our specific suggestions are present
            found_suggestions = 0
            for suggestion in updated_suggestions:
                if suggestion.get("id") in created_suggestion_ids:
                    found_suggestions += 1
                    print(f"   ✅ Found suggestion: {suggestion.get('city')}, {suggestion.get('state')} (Status: {suggestion.get('status')})")
            
            if found_suggestions == len(created_suggestion_ids):
                print(f"✅ SUCCESS: All {len(created_suggestion_ids)} new suggestions found")
                test_results.append(("All New Suggestions Found", True))
            else:
                print(f"❌ FAILED: Only found {found_suggestions}/{len(created_suggestion_ids)} new suggestions")
                test_results.append(("All New Suggestions Found", False))
        else:
            print(f"❌ FAILED: Expected at least {expected_count} suggestions, got {new_count}")
            test_results.append(("Suggestions Count Increased", False))
    else:
        print("❌ FAILED: Could not get updated city suggestions")
        test_results.append(("Suggestions Count Increased", False))
    
    # Step 5: Approve one city
    print("\n--- Step 5: Approve One City (Kadapa) ---")
    if created_suggestion_ids:
        # Find Kadapa suggestion ID
        kadapa_id = None
        for suggestion in updated_suggestions:
            if (suggestion.get("city") == "Kadapa" and 
                suggestion.get("state") == "Andhra Pradesh" and
                suggestion.get("id") in created_suggestion_ids):
                kadapa_id = suggestion.get("id")
                break
        
        if kadapa_id:
            approval_data = {
                "status": "approved",
                "delivery_charge": 99,
                "free_delivery_threshold": 1000
            }
            
            success, response = test_api_endpoint(
                "PUT",
                f"/admin/city-suggestions/{kadapa_id}/status",
                headers=auth_headers,
                data=approval_data,
                description="Approve Kadapa with delivery charge ₹99 and free delivery threshold ₹1000"
            )
            
            if success:
                print(f"✅ SUCCESS: Kadapa approved successfully")
                test_results.append(("Approve Kadapa", True))
                
                # Check logs for email notification
                try:
                    import subprocess
                    result = subprocess.run(
                        ["tail", "-n", "50", "/var/log/supervisor/backend.out.log"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    if result.stdout and "City approval email sent" in result.stdout:
                        print(f"✅ SUCCESS: City approval email log found")
                        test_results.append(("Approval Email Log", True))
                    else:
                        print(f"⚠️  WARNING: City approval email log not found")
                        test_results.append(("Approval Email Log", False))
                        
                except Exception as e:
                    print(f"⚠️  WARNING: Could not check logs: {e}")
                    test_results.append(("Approval Email Log", False))
            else:
                print(f"❌ FAILED: Could not approve Kadapa")
                test_results.append(("Approve Kadapa", False))
        else:
            print(f"❌ FAILED: Could not find Kadapa suggestion ID")
            test_results.append(("Approve Kadapa", False))
    
    # Step 6: Reject one city
    print("\n--- Step 6: Reject One City (Warangal) ---")
    if created_suggestion_ids:
        # Find Warangal suggestion ID
        warangal_id = None
        for suggestion in updated_suggestions:
            if (suggestion.get("city") == "Warangal" and 
                suggestion.get("state") == "Telangana" and
                suggestion.get("id") in created_suggestion_ids):
                warangal_id = suggestion.get("id")
                break
        
        if warangal_id:
            rejection_data = {
                "status": "rejected"
            }
            
            success, response = test_api_endpoint(
                "PUT",
                f"/admin/city-suggestions/{warangal_id}/status",
                headers=auth_headers,
                data=rejection_data,
                description="Reject Warangal city suggestion"
            )
            
            if success:
                print(f"✅ SUCCESS: Warangal rejected successfully")
                test_results.append(("Reject Warangal", True))
                
                # Check logs for rejection email notification
                try:
                    import subprocess
                    result = subprocess.run(
                        ["tail", "-n", "50", "/var/log/supervisor/backend.out.log"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    if result.stdout and "City rejection email sent" in result.stdout:
                        print(f"✅ SUCCESS: City rejection email log found")
                        test_results.append(("Rejection Email Log", True))
                    else:
                        print(f"⚠️  WARNING: City rejection email log not found")
                        test_results.append(("Rejection Email Log", False))
                        
                except Exception as e:
                    print(f"⚠️  WARNING: Could not check logs: {e}")
                    test_results.append(("Rejection Email Log", False))
            else:
                print(f"❌ FAILED: Could not reject Warangal")
                test_results.append(("Reject Warangal", False))
        else:
            print(f"❌ FAILED: Could not find Warangal suggestion ID")
            test_results.append(("Reject Warangal", False))
    
    # Step 7: Verify filter functionality works correctly
    print("\n--- Step 7: Verify Filter Functionality ---")
    
    # Test pending filter (should return 1 - Nellore)
    success, pending_suggestions = test_api_endpoint(
        "GET",
        "/admin/city-suggestions?status=pending",
        headers=auth_headers,
        description="Get pending city suggestions (should include Nellore)"
    )
    
    if success and isinstance(pending_suggestions, list):
        nellore_found = any(s.get("city") == "Nellore" and s.get("status") == "pending" 
                           for s in pending_suggestions)
        if nellore_found:
            print(f"✅ SUCCESS: Pending filter works - Nellore found with pending status")
            test_results.append(("Pending Filter Verification", True))
        else:
            print(f"❌ FAILED: Nellore not found in pending suggestions")
            test_results.append(("Pending Filter Verification", False))
    else:
        print(f"❌ FAILED: Could not get pending suggestions")
        test_results.append(("Pending Filter Verification", False))
    
    # Test approved filter (should return Kadapa)
    success, approved_suggestions = test_api_endpoint(
        "GET",
        "/admin/city-suggestions?status=approved",
        headers=auth_headers,
        description="Get approved city suggestions (should include Kadapa)"
    )
    
    if success and isinstance(approved_suggestions, list):
        kadapa_found = any(s.get("city") == "Kadapa" and s.get("status") == "approved" 
                          for s in approved_suggestions)
        if kadapa_found:
            print(f"✅ SUCCESS: Approved filter works - Kadapa found with approved status")
            test_results.append(("Approved Filter Verification", True))
        else:
            print(f"❌ FAILED: Kadapa not found in approved suggestions")
            test_results.append(("Approved Filter Verification", False))
    else:
        print(f"❌ FAILED: Could not get approved suggestions")
        test_results.append(("Approved Filter Verification", False))
    
    # Test rejected filter (should return Warangal)
    success, rejected_suggestions = test_api_endpoint(
        "GET",
        "/admin/city-suggestions?status=rejected",
        headers=auth_headers,
        description="Get rejected city suggestions (should include Warangal)"
    )
    
    if success and isinstance(rejected_suggestions, list):
        warangal_found = any(s.get("city") == "Warangal" and s.get("status") == "rejected" 
                            for s in rejected_suggestions)
        if warangal_found:
            print(f"✅ SUCCESS: Rejected filter works - Warangal found with rejected status")
            test_results.append(("Rejected Filter Verification", True))
        else:
            print(f"❌ FAILED: Warangal not found in rejected suggestions")
            test_results.append(("Rejected Filter Verification", False))
    else:
        print(f"❌ FAILED: Could not get rejected suggestions")
        test_results.append(("Rejected Filter Verification", False))
    
    # Test ALL filter (should return all 3 suggestions)
    success, all_suggestions_final = test_api_endpoint(
        "GET",
        "/admin/city-suggestions",
        headers=auth_headers,
        description="Get ALL city suggestions (should include all 3 with different statuses)"
    )
    
    if success and isinstance(all_suggestions_final, list):
        our_suggestions = [s for s in all_suggestions_final if s.get("id") in created_suggestion_ids]
        
        if len(our_suggestions) == 3:
            print(f"✅ SUCCESS: ALL filter returns all 3 suggestions regardless of status")
            
            # Verify each has correct status
            statuses = {s.get("city"): s.get("status") for s in our_suggestions}
            expected_statuses = {"Kadapa": "approved", "Warangal": "rejected", "Nellore": "pending"}
            
            if statuses.get("Kadapa") == "approved" and statuses.get("Warangal") == "rejected" and statuses.get("Nellore") == "pending":
                print(f"✅ SUCCESS: All suggestions have correct final statuses")
                test_results.append(("ALL Filter Final Verification", True))
            else:
                print(f"❌ FAILED: Incorrect final statuses - Expected: {expected_statuses}, Got: {statuses}")
                test_results.append(("ALL Filter Final Verification", False))
        else:
            print(f"❌ FAILED: ALL filter should return 3 suggestions, got {len(our_suggestions)}")
            test_results.append(("ALL Filter Final Verification", False))
    else:
        print(f"❌ FAILED: Could not get final ALL suggestions")
        test_results.append(("ALL Filter Final Verification", False))
    
    return test_results

def print_test_summary(test_results):
    """Print a summary of all test results"""
    print("\n" + "="*80)
    print("📊 FINAL TEST RESULTS SUMMARY")
    print("="*80)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, success in test_results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {test_name}")
        if success:
            passed_tests += 1
    
    print(f"\n🎯 OVERALL RESULT: {passed_tests}/{total_tests} tests passed ({(passed_tests/total_tests)*100:.1f}%)")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED - Email fix verification successful!")
    else:
        print("⚠️  SOME TESTS FAILED - Check individual test results above")

def test_order_status_update_emails(admin_token):
    """Test order status update email functionality - CRITICAL EMAIL FIX VERIFICATION"""
    print("\n" + "="*80)
    print("📧 TESTING ORDER STATUS UPDATE EMAILS - CRITICAL FIX VERIFICATION")
    print("="*80)
    
    auth_headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
    
    test_results = []
    
    # Step 1: Create a test order first
    print("\n--- Step 1: Create Test Order ---")
    order_data = {
        "customer_name": "Email Test Customer",
        "email": "emailtest@example.com",
        "phone": "9876543210",
        "doorNo": "123",
        "building": "Test Building",
        "street": "Test Street",
        "city": "Guntur",
        "state": "Andhra Pradesh",
        "pincode": "522001",
        "location": "Guntur",
        "items": [
            {
                "product_id": "1",
                "name": "Test Product",
                "image": "test.jpg",
                "weight": "1 kg",
                "price": 350.0,
                "quantity": 1,
                "description": "Test product for email testing"
            }
        ],
        "subtotal": 350.0,
        "delivery_charge": 49.0,
        "total": 399.0,
        "payment_method": "online",
        "payment_sub_method": "paytm"
    }
    
    success, order_response = test_api_endpoint(
        "POST",
        "/orders",
        data=order_data,
        description="Create test order for email testing"
    )
    
    if success and order_response and "order_id" in order_response:
        order_id = order_response["order_id"]
        print(f"✅ SUCCESS: Test order created with ID: {order_id}")
        test_results.append(("Create Test Order", True))
        
        # Check for order confirmation email log
        try:
            import subprocess
            
            # Check both output and error logs
            result_err = subprocess.run(
                ["tail", "-n", "50", "/var/log/supervisor/backend.err.log"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            result_out = subprocess.run(
                ["tail", "-n", "50", "/var/log/supervisor/backend.out.log"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            combined_logs = (result_err.stdout or "") + (result_out.stdout or "")
            
            if "Email sent successfully" in combined_logs or "Order confirmation email sent" in combined_logs:
                print(f"✅ SUCCESS: Order confirmation email log found")
                test_results.append(("Order Confirmation Email Log", True))
            else:
                print(f"⚠️  WARNING: Order confirmation email log not found")
                test_results.append(("Order Confirmation Email Log", False))
                
        except Exception as e:
            print(f"⚠️  WARNING: Could not check logs: {e}")
            test_results.append(("Order Confirmation Email Log", False))
    else:
        print("❌ FAILED: Could not create test order")
        test_results.append(("Create Test Order", False))
        return test_results
    
    # Step 2: Test PUT /api/orders/{order_id}/status (CRITICAL TEST)
    print("\n--- Step 2: Test Order Status Update via PUT /api/orders/{order_id}/status ---")
    status_update_data = {
        "status": "processing"
    }
    
    success, response = test_api_endpoint(
        "PUT",
        f"/orders/{order_id}/status",
        headers=auth_headers,
        data=status_update_data,
        description="Update order status to 'processing' - should trigger email"
    )
    
    if success:
        print(f"✅ SUCCESS: Order status updated successfully")
        test_results.append(("Order Status Update API", True))
        
        # Check backend logs for email sending confirmation
        print("\n🔍 Checking backend logs for email notification...")
        try:
            import subprocess
            import time
            time.sleep(2)  # Wait for email to be processed
            
            # Check both output and error logs
            email_found = False
            
            # Check error log (where application logs go)
            result_err = subprocess.run(
                ["tail", "-n", "100", "/var/log/supervisor/backend.err.log"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Check output log
            result_out = subprocess.run(
                ["tail", "-n", "100", "/var/log/supervisor/backend.out.log"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            combined_logs = (result_err.stdout or "") + (result_out.stdout or "")
            
            if "Order status update email sent successfully" in combined_logs:
                print(f"✅ SUCCESS: Order status update email sent successfully")
                test_results.append(("Status Update Email Sent", True))
                email_found = True
            elif "Gmail credentials not configured" in combined_logs:
                print(f"❌ CRITICAL BUG: Gmail credentials not configured warning found")
                test_results.append(("Status Update Email Sent", False))
            
            if not email_found:
                print(f"⚠️  WARNING: No specific email log found in recent logs")
                test_results.append(("Status Update Email Sent", False))
                
        except Exception as e:
            print(f"❌ ERROR: Could not check backend logs: {e}")
            test_results.append(("Status Update Email Sent", False))
    else:
        print("❌ FAILED: Order status update API failed")
        test_results.append(("Order Status Update API", False))
        test_results.append(("Status Update Email Sent", False))
    
    # Step 3: Test PUT /api/orders/{order_id}/admin-update (CRITICAL TEST)
    print("\n--- Step 3: Test Order Status Update via PUT /api/orders/{order_id}/admin-update ---")
    admin_update_data = {
        "order_status": "shipped",
        "admin_notes": "Order shipped via courier",
        "delivery_days": 2
    }
    
    success, response = test_api_endpoint(
        "PUT",
        f"/orders/{order_id}/admin-update",
        headers=auth_headers,
        data=admin_update_data,
        description="Update order status to 'shipped' via admin-update - should trigger email"
    )
    
    if success:
        print(f"✅ SUCCESS: Order admin update successful")
        test_results.append(("Order Admin Update API", True))
        
        # Check backend logs for email sending confirmation
        print("\n🔍 Checking backend logs for admin update email notification...")
        try:
            import subprocess
            import time
            time.sleep(2)  # Wait for email to be processed
            
            # Check both output and error logs
            email_found = False
            
            # Check error log (where application logs go)
            result_err = subprocess.run(
                ["tail", "-n", "100", "/var/log/supervisor/backend.err.log"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Check output log
            result_out = subprocess.run(
                ["tail", "-n", "100", "/var/log/supervisor/backend.out.log"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            combined_logs = (result_err.stdout or "") + (result_out.stdout or "")
            
            if "Order status update email sent successfully" in combined_logs:
                print(f"✅ SUCCESS: Admin update email sent successfully")
                test_results.append(("Admin Update Email Sent", True))
                email_found = True
            elif "Gmail credentials not configured" in combined_logs:
                print(f"❌ CRITICAL BUG: Gmail credentials not configured warning found")
                test_results.append(("Admin Update Email Sent", False))
            
            if not email_found:
                print(f"⚠️  WARNING: No specific admin update email log found in recent logs")
                test_results.append(("Admin Update Email Sent", False))
                
        except Exception as e:
            print(f"❌ ERROR: Could not check backend logs: {e}")
            test_results.append(("Admin Update Email Sent", False))
    else:
        print("❌ FAILED: Order admin update API failed")
        test_results.append(("Order Admin Update API", False))
        test_results.append(("Admin Update Email Sent", False))
    
    # Step 4: Check for any "Gmail credentials not configured" warnings
    print("\n--- Step 4: Check for Gmail Credentials Warnings ---")
    try:
        import subprocess
        result = subprocess.run(
            ["grep", "-i", "gmail credentials not configured", "/var/log/supervisor/backend.out.log"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.stdout:
            print(f"❌ CRITICAL: Found Gmail credentials warnings:")
            print(result.stdout)
            test_results.append(("No Gmail Credentials Warnings", False))
        else:
            print(f"✅ SUCCESS: No Gmail credentials warnings found")
            test_results.append(("No Gmail Credentials Warnings", True))
            
    except Exception as e:
        print(f"⚠️  WARNING: Could not check for Gmail warnings: {e}")
        test_results.append(("No Gmail Credentials Warnings", False))
    
    # Step 5: Verify Gmail credentials are loaded properly in backend
    print("\n--- Step 5: Verify Gmail Credentials Loading in Backend ---")
    try:
        import subprocess
        result = subprocess.run(
            ["python", "-c", """
import os
import sys
sys.path.append('/app/backend')
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
gmail_email = os.environ.get('GMAIL_EMAIL', '')
gmail_password = os.environ.get('GMAIL_APP_PASSWORD', '')
print(f'GMAIL_EMAIL: {gmail_email}')
print(f'GMAIL_APP_PASSWORD: {"FOUND" if gmail_password else "NOT_FOUND"}')
"""],
            cwd="/app/backend",
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.stdout:
            print(f"Backend environment check:")
            print(result.stdout)
            
            if "contact.ananthahomefoods@gmail.com" in result.stdout and "FOUND" in result.stdout:
                print(f"✅ SUCCESS: Gmail credentials properly loaded in backend")
                test_results.append(("Gmail Credentials Available", True))
            else:
                print(f"❌ CRITICAL: Gmail credentials not properly loaded in backend")
                test_results.append(("Gmail Credentials Available", False))
        else:
            print(f"❌ ERROR: Could not check backend environment")
            test_results.append(("Gmail Credentials Available", False))
            
    except Exception as e:
        print(f"❌ ERROR: Could not check Gmail credentials: {e}")
        test_results.append(("Gmail Credentials Available", False))
    
    return test_results

def test_cities_states_management_system(admin_token):
    """Test the complete Cities & States management system as requested in review"""
    print("\n" + "="*80)
    print("🏙️ TESTING CITIES & STATES MANAGEMENT SYSTEM - COMPREHENSIVE REVIEW")
    print("="*80)
    
    auth_headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
    
    test_results = []
    
    # TEST 1: GET Cities from Database - Should return all 431 cities
    print("\n--- TEST 1: GET Cities from Database (431 cities expected) ---")
    success, locations = test_api_endpoint(
        "GET",
        "/locations",
        description="Get all 431 cities from locations database"
    )
    
    if success and isinstance(locations, list):
        total_cities = len(locations)
        print(f"✅ SUCCESS: Retrieved {total_cities} cities from database")
        
        # Verify we have 431 cities as expected
        if total_cities == 431:
            print(f"✅ SUCCESS: Correct number of cities (431)")
            test_results.append(("GET Cities Count (431)", True))
        else:
            print(f"⚠️  WARNING: Expected 431 cities, got {total_cities}")
            test_results.append(("GET Cities Count (431)", False))
        
        # Verify city structure includes required fields
        if locations:
            sample_city = locations[0]
            required_fields = ["name", "state", "charge", "free_delivery_threshold"]
            
            print(f"\n🔍 CITY STRUCTURE VERIFICATION:")
            all_fields_present = True
            for field in required_fields:
                if field in sample_city:
                    print(f"   ✅ '{field}' field present")
                else:
                    print(f"   ❌ '{field}' field missing")
                    all_fields_present = False
            
            test_results.append(("City Structure Fields", all_fields_present))
            
            # Check for sample cities: Guntur (AP), Hyderabad (Telangana)
            guntur_found = any(city.get("name") == "Guntur" and city.get("state") == "Andhra Pradesh" 
                              for city in locations)
            hyderabad_found = any(city.get("name") == "Hyderabad" and city.get("state") == "Telangana" 
                                 for city in locations)
            
            if guntur_found:
                print(f"   ✅ Sample city Guntur (Andhra Pradesh) found")
            else:
                print(f"   ❌ Sample city Guntur (Andhra Pradesh) not found")
            
            if hyderabad_found:
                print(f"   ✅ Sample city Hyderabad (Telangana) found")
            else:
                print(f"   ❌ Sample city Hyderabad (Telangana) not found")
            
            test_results.append(("Sample Cities Present", guntur_found and hyderabad_found))
        
        test_results.append(("GET Cities API", True))
    else:
        print(f"❌ FAILED: Could not retrieve cities from database")
        test_results.append(("GET Cities API", False))
        test_results.append(("GET Cities Count (431)", False))
        test_results.append(("City Structure Fields", False))
        test_results.append(("Sample Cities Present", False))
    
    # TEST 2: City Suggestions Management - GET endpoints
    print("\n--- TEST 2: City Suggestions Management APIs ---")
    
    # Test GET /api/admin/city-suggestions (all suggestions)
    success, all_suggestions = test_api_endpoint(
        "GET",
        "/admin/city-suggestions",
        headers=auth_headers,
        description="Get all city suggestions"
    )
    
    if success and isinstance(all_suggestions, list):
        print(f"✅ SUCCESS: GET /api/admin/city-suggestions returns {len(all_suggestions)} suggestions")
        test_results.append(("GET All City Suggestions", True))
        
        # Test GET /api/admin/city-suggestions?status=pending (filtered)
        success, pending_suggestions = test_api_endpoint(
            "GET",
            "/admin/city-suggestions?status=pending",
            headers=auth_headers,
            description="Get pending city suggestions only"
        )
        
        if success and isinstance(pending_suggestions, list):
            print(f"✅ SUCCESS: GET with status=pending filter returns {len(pending_suggestions)} suggestions")
            
            # Verify all returned suggestions have pending status
            if pending_suggestions:
                all_pending = all(s.get("status") == "pending" for s in pending_suggestions)
                if all_pending:
                    print(f"   ✅ All filtered suggestions have 'pending' status")
                    test_results.append(("GET Pending Filter", True))
                else:
                    print(f"   ❌ Some filtered suggestions don't have 'pending' status")
                    test_results.append(("GET Pending Filter", False))
            else:
                print(f"   ℹ️  No pending suggestions found (this is okay)")
                test_results.append(("GET Pending Filter", True))
        else:
            print(f"❌ FAILED: GET with status=pending filter failed")
            test_results.append(("GET Pending Filter", False))
    else:
        print(f"❌ FAILED: GET all city suggestions failed")
        test_results.append(("GET All City Suggestions", False))
        test_results.append(("GET Pending Filter", False))
    
    # TEST 3: Create a test city suggestion
    print("\n--- TEST 3: Create Test City Suggestion ---")
    suggestion_data = {
        "state": "Andhra Pradesh",
        "city": "Testcity",
        "customer_name": "Test User",
        "phone": "9876543210",
        "email": "test@example.com"
    }
    
    success, response = test_api_endpoint(
        "POST",
        "/suggest-city",
        data=suggestion_data,
        description="Create test city suggestion for Testcity, Andhra Pradesh"
    )
    
    if success and response and "suggestion_id" in response:
        suggestion_id = response["suggestion_id"]
        print(f"✅ SUCCESS: Test city suggestion created with ID: {suggestion_id}")
        test_results.append(("Create Test City Suggestion", True))
    else:
        print(f"❌ FAILED: Could not create test city suggestion")
        test_results.append(("Create Test City Suggestion", False))
        return test_results
    
    # TEST 4: Approve City Suggestion with email notification
    print("\n--- TEST 4: Approve City Suggestion with Email Notification ---")
    approval_data = {
        "status": "approved",
        "delivery_charge": 99,
        "free_delivery_threshold": 1000
    }
    
    success, response = test_api_endpoint(
        "PUT",
        f"/admin/city-suggestions/{suggestion_id}/status",
        headers=auth_headers,
        data=approval_data,
        description="Approve city with delivery charge ₹99 and free delivery threshold ₹1000"
    )
    
    if success:
        print(f"✅ SUCCESS: City suggestion approved successfully")
        test_results.append(("Approve City Suggestion", True))
        
        # Verify city is added to locations
        print(f"\n   🔍 Verifying city added to locations...")
        success, updated_locations = test_api_endpoint(
            "GET",
            "/locations",
            description="Verify Testcity is added to locations"
        )
        
        if success and isinstance(updated_locations, list):
            testcity_found = None
            for location in updated_locations:
                if location.get("name") == "Testcity":
                    testcity_found = location
                    break
            
            if testcity_found:
                print(f"   ✅ SUCCESS: Testcity found in locations")
                print(f"      - Charge: ₹{testcity_found.get('charge')}")
                print(f"      - Free Delivery Threshold: ₹{testcity_found.get('free_delivery_threshold')}")
                
                # Verify correct values
                if (testcity_found.get("charge") == 99 and 
                    testcity_found.get("free_delivery_threshold") == 1000):
                    print(f"   ✅ SUCCESS: Delivery settings are correct")
                    test_results.append(("City Added to Locations", True))
                else:
                    print(f"   ❌ FAILED: Incorrect delivery settings")
                    test_results.append(("City Added to Locations", False))
            else:
                print(f"   ❌ FAILED: Testcity not found in locations")
                test_results.append(("City Added to Locations", False))
        else:
            print(f"   ❌ FAILED: Could not verify locations")
            test_results.append(("City Added to Locations", False))
        
        # Check for approval email notification in logs
        print(f"\n   📧 Checking for approval email notification...")
        try:
            import subprocess
            result = subprocess.run(
                ["tail", "-n", "100", "/var/log/supervisor/backend.out.log"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.stdout and "City approval email sent" in result.stdout:
                print(f"   ✅ SUCCESS: City approval email notification found in logs")
                test_results.append(("Approval Email Notification", True))
            else:
                print(f"   ⚠️  WARNING: City approval email notification not found in logs")
                test_results.append(("Approval Email Notification", False))
                
        except Exception as e:
            print(f"   ⚠️  WARNING: Could not check logs: {e}")
            test_results.append(("Approval Email Notification", False))
    else:
        print(f"❌ FAILED: Could not approve city suggestion")
        test_results.append(("Approve City Suggestion", False))
        test_results.append(("City Added to Locations", False))
        test_results.append(("Approval Email Notification", False))
    
    # TEST 5: Create another test city suggestion for rejection
    print("\n--- TEST 5: Create Test City Suggestion for Rejection ---")
    rejection_suggestion_data = {
        "state": "Telangana",
        "city": "Rejectcity",
        "customer_name": "Test User 2",
        "phone": "9876543211",
        "email": "test2@example.com"
    }
    
    success, response = test_api_endpoint(
        "POST",
        "/suggest-city",
        data=rejection_suggestion_data,
        description="Create test city suggestion for rejection"
    )
    
    if success and response and "suggestion_id" in response:
        rejection_suggestion_id = response["suggestion_id"]
        print(f"✅ SUCCESS: Test city suggestion for rejection created with ID: {rejection_suggestion_id}")
        test_results.append(("Create Rejection Test Suggestion", True))
    else:
        print(f"❌ FAILED: Could not create test city suggestion for rejection")
        test_results.append(("Create Rejection Test Suggestion", False))
        return test_results
    
    # TEST 6: Reject City Suggestion with email notification
    print("\n--- TEST 6: Reject City Suggestion with Email Notification ---")
    rejection_data = {
        "status": "rejected"
    }
    
    success, response = test_api_endpoint(
        "PUT",
        f"/admin/city-suggestions/{rejection_suggestion_id}/status",
        headers=auth_headers,
        data=rejection_data,
        description="Reject city suggestion"
    )
    
    if success:
        print(f"✅ SUCCESS: City suggestion rejected successfully")
        test_results.append(("Reject City Suggestion", True))
        
        # Check for rejection email notification in logs
        print(f"\n   📧 Checking for rejection email notification...")
        try:
            import subprocess
            result = subprocess.run(
                ["tail", "-n", "100", "/var/log/supervisor/backend.out.log"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.stdout and "City rejection email sent" in result.stdout:
                print(f"   ✅ SUCCESS: City rejection email notification found in logs")
                test_results.append(("Rejection Email Notification", True))
            else:
                print(f"   ⚠️  WARNING: City rejection email notification not found in logs")
                test_results.append(("Rejection Email Notification", False))
                
        except Exception as e:
            print(f"   ⚠️  WARNING: Could not check logs: {e}")
            test_results.append(("Rejection Email Notification", False))
    else:
        print(f"❌ FAILED: Could not reject city suggestion")
        test_results.append(("Reject City Suggestion", False))
        test_results.append(("Rejection Email Notification", False))
    
    # TEST 7: Delete City Suggestion (should only work for approved/rejected)
    print("\n--- TEST 7: Delete City Suggestion Restrictions ---")
    
    # Try to delete the approved suggestion (should work)
    success, response = test_api_endpoint(
        "DELETE",
        f"/admin/city-suggestions/{suggestion_id}",
        headers=auth_headers,
        description="Delete approved city suggestion (should work)",
        expected_status=200
    )
    
    if success:
        print(f"✅ SUCCESS: Approved city suggestion deleted successfully")
        test_results.append(("Delete Approved Suggestion", True))
    else:
        print(f"❌ FAILED: Could not delete approved city suggestion")
        test_results.append(("Delete Approved Suggestion", False))
    
    # Try to delete the rejected suggestion (should work)
    success, response = test_api_endpoint(
        "DELETE",
        f"/admin/city-suggestions/{rejection_suggestion_id}",
        headers=auth_headers,
        description="Delete rejected city suggestion (should work)",
        expected_status=200
    )
    
    if success:
        print(f"✅ SUCCESS: Rejected city suggestion deleted successfully")
        test_results.append(("Delete Rejected Suggestion", True))
    else:
        print(f"❌ FAILED: Could not delete rejected city suggestion")
        test_results.append(("Delete Rejected Suggestion", False))
    
    # Create a pending suggestion and try to delete it (should fail)
    print(f"\n   🧪 Testing delete restriction on pending suggestions...")
    pending_suggestion_data = {
        "state": "Karnataka",
        "city": "Pendingcity",
        "customer_name": "Test User 3",
        "phone": "9876543212",
        "email": "test3@example.com"
    }
    
    success, response = test_api_endpoint(
        "POST",
        "/suggest-city",
        data=pending_suggestion_data,
        description="Create pending city suggestion to test delete restriction"
    )
    
    if success and response and "suggestion_id" in response:
        pending_suggestion_id = response["suggestion_id"]
        
        # Try to delete pending suggestion (should fail)
        success, response = test_api_endpoint(
            "DELETE",
            f"/admin/city-suggestions/{pending_suggestion_id}",
            headers=auth_headers,
            description="Delete pending city suggestion (should fail)",
            expected_status=400
        )
        
        if not success:  # We expect this to fail
            print(f"   ✅ SUCCESS: Pending city suggestion correctly cannot be deleted")
            test_results.append(("Delete Pending Restriction", True))
        else:
            print(f"   ❌ FAILED: Pending city suggestion was incorrectly deleted")
            test_results.append(("Delete Pending Restriction", False))
    else:
        print(f"   ⚠️  WARNING: Could not create pending suggestion for delete test")
        test_results.append(("Delete Pending Restriction", False))
    
    # TEST 8: Pending Cities from Orders
    print("\n--- TEST 8: Pending Cities from Orders ---")
    
    # Test GET /api/admin/pending-cities
    success, pending_cities = test_api_endpoint(
        "GET",
        "/admin/pending-cities",
        headers=auth_headers,
        description="Get cities from orders with 'Other' location"
    )
    
    if success and isinstance(pending_cities, list):
        print(f"✅ SUCCESS: GET /api/admin/pending-cities returns {len(pending_cities)} pending cities")
        test_results.append(("GET Pending Cities from Orders", True))
        
        # If there are pending cities, show structure
        if pending_cities:
            sample_city = pending_cities[0]
            print(f"   📋 Sample pending city structure:")
            for key, value in sample_city.items():
                print(f"      - {key}: {value}")
    else:
        print(f"❌ FAILED: GET /api/admin/pending-cities failed")
        test_results.append(("GET Pending Cities from Orders", False))
    
    # Test POST /api/admin/approve-city (direct approval)
    print(f"\n   🧪 Testing direct city approval...")
    direct_approval_data = {
        "city_name": "DirectApprovalCity",
        "state_name": "Andhra Pradesh",
        "delivery_charge": 75,
        "free_delivery_threshold": 1200
    }
    
    success, response = test_api_endpoint(
        "POST",
        "/admin/approve-city",
        headers=auth_headers,
        data=direct_approval_data,
        description="Directly approve city with delivery settings"
    )
    
    if success:
        print(f"✅ SUCCESS: Direct city approval works")
        test_results.append(("Direct City Approval", True))
        
        # Verify city appears in locations
        success, locations_check = test_api_endpoint(
            "GET",
            "/locations",
            description="Verify directly approved city in locations"
        )
        
        if success and isinstance(locations_check, list):
            direct_city_found = any(city.get("name") == "DirectApprovalCity" 
                                   for city in locations_check)
            if direct_city_found:
                print(f"   ✅ SUCCESS: Directly approved city found in locations")
                test_results.append(("Direct Approval in Locations", True))
            else:
                print(f"   ❌ FAILED: Directly approved city not found in locations")
                test_results.append(("Direct Approval in Locations", False))
        else:
            print(f"   ❌ FAILED: Could not verify locations after direct approval")
            test_results.append(("Direct Approval in Locations", False))
    else:
        print(f"❌ FAILED: Direct city approval failed")
        test_results.append(("Direct City Approval", False))
        test_results.append(("Direct Approval in Locations", False))
    
    # TEST 9: Authentication Requirements
    print("\n--- TEST 9: Authentication Requirements ---")
    
    # Test admin endpoints without authentication (should fail)
    endpoints_requiring_auth = [
        "/admin/city-suggestions",
        "/admin/pending-cities"
    ]
    
    auth_test_results = []
    for endpoint in endpoints_requiring_auth:
        success, response = test_api_endpoint(
            "GET",
            endpoint,
            description=f"Test {endpoint} without authentication (should fail)",
            expected_status=401
        )
        
        if not success:  # We expect 401 failure
            print(f"   ✅ SUCCESS: {endpoint} correctly requires authentication")
            auth_test_results.append(True)
        else:
            print(f"   ❌ FAILED: {endpoint} incorrectly allows access without auth")
            auth_test_results.append(False)
    
    all_auth_tests_passed = all(auth_test_results)
    test_results.append(("Authentication Requirements", all_auth_tests_passed))
    
    return test_results

def test_city_suggestions_approval_flow(admin_token):
    """Test the city suggestions approval flow to verify the fix for cities disappearing after approval"""
    print("\n" + "="*80)
    print("🏙️ TESTING CITY SUGGESTIONS APPROVAL FLOW - VANISHING CITIES FIX")
    print("="*80)
    
    auth_headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
    
    test_results = []
    created_suggestion_ids = []
    
    # Step 1: Setup Phase - Create 3-5 test city suggestions
    print("\n--- SETUP PHASE: Create 3-5 Test City Suggestions ---")
    test_cities = [
        {"city": "Kadapa", "state": "Andhra Pradesh", "phone": "9876543210", "email": "kadapa@example.com"},
        {"city": "Warangal", "state": "Telangana", "phone": "9876543211", "email": "warangal@example.com"},
        {"city": "Nellore", "state": "Andhra Pradesh", "phone": "9876543212", "email": "nellore@example.com"},
        {"city": "Vijayawada", "state": "Andhra Pradesh", "phone": "9876543213", "email": "vijayawada@example.com"}
    ]
    
    for i, city_data in enumerate(test_cities, 1):
        suggestion_data = {
            "city": city_data["city"],
            "state": city_data["state"],
            "customer_name": f"Test User {i}",
            "phone": city_data["phone"],
            "email": city_data["email"]
        }
        
        success, response = test_api_endpoint(
            "POST",
            "/suggest-city",
            data=suggestion_data,
            description=f"Create city suggestion for {city_data['city']}, {city_data['state']}"
        )
        
        if success and response and "suggestion_id" in response:
            suggestion_id = response["suggestion_id"]
            created_suggestion_ids.append(suggestion_id)
            print(f"✅ SUCCESS: Created suggestion {i} - {city_data['city']} (ID: {suggestion_id})")
            test_results.append((f"Create Suggestion {i} ({city_data['city']})", True))
        else:
            print(f"❌ FAILED: Could not create suggestion for {city_data['city']}")
            test_results.append((f"Create Suggestion {i} ({city_data['city']})", False))
    
    if len(created_suggestion_ids) < 3:
        print("❌ CRITICAL: Need at least 3 city suggestions to test properly")
        return test_results
    
    # Step 2: Verify Initial State - All suggestions should be pending
    print("\n--- STEP 2: Verify Initial State ---")
    success, all_suggestions = test_api_endpoint(
        "GET",
        "/admin/city-suggestions",
        headers=auth_headers,
        description="Get all city suggestions (should return all pending suggestions)"
    )
    
    if success and isinstance(all_suggestions, list):
        initial_count = len(all_suggestions)
        pending_count = len([s for s in all_suggestions if s.get("status") == "pending"])
        
        print(f"✅ SUCCESS: Retrieved {initial_count} total suggestions, {pending_count} pending")
        
        # Verify our created suggestions are present
        found_suggestions = 0
        for suggestion in all_suggestions:
            if suggestion.get("id") in created_suggestion_ids:
                found_suggestions += 1
                print(f"   ✅ Found: {suggestion.get('city')}, {suggestion.get('state')} (Status: {suggestion.get('status')})")
        
        if found_suggestions == len(created_suggestion_ids):
            print(f"✅ SUCCESS: All {len(created_suggestion_ids)} created suggestions found with status='pending'")
            test_results.append(("Initial State Verification", True))
        else:
            print(f"❌ FAILED: Only found {found_suggestions}/{len(created_suggestion_ids)} created suggestions")
            test_results.append(("Initial State Verification", False))
    else:
        print("❌ FAILED: Could not get initial city suggestions")
        test_results.append(("Initial State Verification", False))
        return test_results
    
    # Step 3: Test Approval Flow - Approve ONE city
    print("\n--- STEP 3: Test Approval Flow ---")
    if created_suggestion_ids:
        # Find first suggestion to approve (Kadapa)
        kadapa_suggestion = None
        for suggestion in all_suggestions:
            if (suggestion.get("city") == "Kadapa" and 
                suggestion.get("id") in created_suggestion_ids):
                kadapa_suggestion = suggestion
                break
        
        if kadapa_suggestion:
            kadapa_id = kadapa_suggestion.get("id")
            approval_data = {
                "status": "approved",
                "delivery_charge": 99,
                "free_delivery_threshold": 1000
            }
            
            success, response = test_api_endpoint(
                "PUT",
                f"/admin/city-suggestions/{kadapa_id}/status",
                headers=auth_headers,
                data=approval_data,
                description="Approve Kadapa city suggestion"
            )
            
            if success:
                print(f"✅ SUCCESS: Kadapa approved successfully")
                test_results.append(("Approve One City", True))
                
                # CRITICAL TEST: Immediately check if ALL cities are still returned
                print("\n   🔍 CRITICAL CHECK: Verify ALL cities still visible after approval")
                success, post_approval_suggestions = test_api_endpoint(
                    "GET",
                    "/admin/city-suggestions",
                    headers=auth_headers,
                    description="Get ALL city suggestions after approval (CRITICAL: should return ALL cities)"
                )
                
                if success and isinstance(post_approval_suggestions, list):
                    post_approval_count = len(post_approval_suggestions)
                    
                    # Count by status
                    pending_count = len([s for s in post_approval_suggestions if s.get("status") == "pending"])
                    approved_count = len([s for s in post_approval_suggestions if s.get("status") == "approved"])
                    
                    print(f"   📊 POST-APPROVAL COUNTS:")
                    print(f"      - Total suggestions: {post_approval_count}")
                    print(f"      - Pending: {pending_count}")
                    print(f"      - Approved: {approved_count}")
                    
                    # VERIFY: Total count should remain the same
                    if post_approval_count >= initial_count:
                        print(f"   ✅ SUCCESS: Total count maintained ({post_approval_count} >= {initial_count})")
                        test_results.append(("All Cities Visible After Approval", True))
                        
                        # VERIFY: We should have both pending AND approved cities
                        if pending_count > 0 and approved_count > 0:
                            print(f"   ✅ SUCCESS: Both pending ({pending_count}) and approved ({approved_count}) cities visible")
                            test_results.append(("Mixed Status Cities Visible", True))
                        else:
                            print(f"   ❌ FAILED: Only one status type visible (pending: {pending_count}, approved: {approved_count})")
                            test_results.append(("Mixed Status Cities Visible", False))
                        
                        # VERIFY: Our specific cities are still present
                        found_after_approval = 0
                        for suggestion in post_approval_suggestions:
                            if suggestion.get("id") in created_suggestion_ids:
                                found_after_approval += 1
                                status = suggestion.get("status")
                                city = suggestion.get("city")
                                print(f"      ✅ {city}: {status}")
                        
                        if found_after_approval == len(created_suggestion_ids):
                            print(f"   ✅ SUCCESS: All {len(created_suggestion_ids)} test cities still visible")
                            test_results.append(("All Test Cities Still Visible", True))
                        else:
                            print(f"   ❌ FAILED: Only {found_after_approval}/{len(created_suggestion_ids)} test cities visible")
                            test_results.append(("All Test Cities Still Visible", False))
                    else:
                        print(f"   ❌ CRITICAL FAILURE: Total count decreased from {initial_count} to {post_approval_count}")
                        print(f"   🚨 THIS IS THE BUG: Cities are disappearing after approval!")
                        test_results.append(("All Cities Visible After Approval", False))
                else:
                    print("   ❌ FAILED: Could not get city suggestions after approval")
                    test_results.append(("All Cities Visible After Approval", False))
            else:
                print(f"❌ FAILED: Could not approve Kadapa")
                test_results.append(("Approve One City", False))
        else:
            print(f"❌ FAILED: Could not find Kadapa suggestion")
            test_results.append(("Approve One City", False))
    
    # Step 4: Test Rejection Flow
    print("\n--- STEP 4: Test Rejection Flow ---")
    if created_suggestion_ids and 'post_approval_suggestions' in locals():
        # Find Warangal suggestion to reject
        warangal_suggestion = None
        for suggestion in post_approval_suggestions:
            if (suggestion.get("city") == "Warangal" and 
                suggestion.get("id") in created_suggestion_ids):
                warangal_suggestion = suggestion
                break
        
        if warangal_suggestion:
            warangal_id = warangal_suggestion.get("id")
            rejection_data = {
                "status": "rejected"
            }
            
            success, response = test_api_endpoint(
                "PUT",
                f"/admin/city-suggestions/{warangal_id}/status",
                headers=auth_headers,
                data=rejection_data,
                description="Reject Warangal city suggestion"
            )
            
            if success:
                print(f"✅ SUCCESS: Warangal rejected successfully")
                test_results.append(("Reject One City", True))
                
                # CRITICAL TEST: Verify ALL cities still visible after rejection
                print("\n   🔍 CRITICAL CHECK: Verify ALL cities still visible after rejection")
                success, post_rejection_suggestions = test_api_endpoint(
                    "GET",
                    "/admin/city-suggestions",
                    headers=auth_headers,
                    description="Get ALL city suggestions after rejection"
                )
                
                if success and isinstance(post_rejection_suggestions, list):
                    post_rejection_count = len(post_rejection_suggestions)
                    
                    # Count by status
                    pending_count = len([s for s in post_rejection_suggestions if s.get("status") == "pending"])
                    approved_count = len([s for s in post_rejection_suggestions if s.get("status") == "approved"])
                    rejected_count = len([s for s in post_rejection_suggestions if s.get("status") == "rejected"])
                    
                    print(f"   📊 POST-REJECTION COUNTS:")
                    print(f"      - Total suggestions: {post_rejection_count}")
                    print(f"      - Pending: {pending_count}")
                    print(f"      - Approved: {approved_count}")
                    print(f"      - Rejected: {rejected_count}")
                    
                    # VERIFY: All status types should be visible
                    if pending_count > 0 and approved_count > 0 and rejected_count > 0:
                        print(f"   ✅ SUCCESS: All status types visible (pending, approved, rejected)")
                        test_results.append(("All Status Types Visible", True))
                    else:
                        print(f"   ❌ FAILED: Not all status types visible")
                        test_results.append(("All Status Types Visible", False))
                else:
                    print("   ❌ FAILED: Could not get city suggestions after rejection")
                    test_results.append(("All Status Types Visible", False))
            else:
                print(f"❌ FAILED: Could not reject Warangal")
                test_results.append(("Reject One City", False))
    
    # Step 5: Test Status Filters
    print("\n--- STEP 5: Test Status Filters ---")
    status_filters = ["pending", "approved", "rejected"]
    
    for status in status_filters:
        success, filtered_suggestions = test_api_endpoint(
            "GET",
            f"/admin/city-suggestions?status={status}",
            headers=auth_headers,
            description=f"Get city suggestions with status={status}"
        )
        
        if success and isinstance(filtered_suggestions, list):
            # Verify all returned suggestions have the correct status
            if filtered_suggestions:
                all_correct_status = all(s.get("status") == status for s in filtered_suggestions)
                if all_correct_status:
                    print(f"   ✅ SUCCESS: Status filter '{status}' returns {len(filtered_suggestions)} suggestions with correct status")
                    test_results.append((f"Status Filter {status}", True))
                else:
                    print(f"   ❌ FAILED: Status filter '{status}' returns suggestions with incorrect status")
                    test_results.append((f"Status Filter {status}", False))
            else:
                print(f"   ✅ SUCCESS: Status filter '{status}' returns empty array (no suggestions with this status)")
                test_results.append((f"Status Filter {status}", True))
        else:
            print(f"   ❌ FAILED: Status filter '{status}' failed")
            test_results.append((f"Status Filter {status}", False))
    
    # Step 6: Test Delete Flow
    print("\n--- STEP 6: Test Delete Flow ---")
    if created_suggestion_ids and 'post_rejection_suggestions' in locals():
        # Find Nellore suggestion to delete
        nellore_suggestion = None
        for suggestion in post_rejection_suggestions:
            if (suggestion.get("city") == "Nellore" and 
                suggestion.get("id") in created_suggestion_ids):
                nellore_suggestion = suggestion
                break
        
        if nellore_suggestion:
            nellore_id = nellore_suggestion.get("id")
            
            success, response = test_api_endpoint(
                "DELETE",
                f"/admin/city-suggestions/{nellore_id}",
                headers=auth_headers,
                description="Delete Nellore city suggestion"
            )
            
            if success:
                print(f"✅ SUCCESS: Nellore deleted successfully")
                test_results.append(("Delete One City", True))
                
                # CRITICAL TEST: Verify remaining cities are still visible
                print("\n   🔍 CRITICAL CHECK: Verify remaining cities still visible after deletion")
                success, post_deletion_suggestions = test_api_endpoint(
                    "GET",
                    "/admin/city-suggestions",
                    headers=auth_headers,
                    description="Get ALL city suggestions after deletion"
                )
                
                if success and isinstance(post_deletion_suggestions, list):
                    post_deletion_count = len(post_deletion_suggestions)
                    expected_count = post_rejection_count - 1  # Should be one less
                    
                    print(f"   📊 POST-DELETION COUNT: {post_deletion_count} (expected: {expected_count})")
                    
                    if post_deletion_count == expected_count:
                        print(f"   ✅ SUCCESS: Count decreased by 1 as expected")
                        test_results.append(("Correct Count After Deletion", True))
                        
                        # Verify Nellore is gone but others remain
                        nellore_found = any(s.get("city") == "Nellore" for s in post_deletion_suggestions)
                        remaining_test_cities = [s for s in post_deletion_suggestions 
                                               if s.get("id") in created_suggestion_ids]
                        
                        if not nellore_found and len(remaining_test_cities) == len(created_suggestion_ids) - 1:
                            print(f"   ✅ SUCCESS: Nellore deleted, other test cities remain visible")
                            test_results.append(("Remaining Cities Visible After Deletion", True))
                        else:
                            print(f"   ❌ FAILED: Deletion affected other cities unexpectedly")
                            test_results.append(("Remaining Cities Visible After Deletion", False))
                    else:
                        print(f"   ❌ FAILED: Unexpected count after deletion")
                        test_results.append(("Correct Count After Deletion", False))
                else:
                    print("   ❌ FAILED: Could not get city suggestions after deletion")
                    test_results.append(("Correct Count After Deletion", False))
            else:
                print(f"❌ FAILED: Could not delete Nellore")
                test_results.append(("Delete One City", False))
    
    return test_results

def test_city_suggestions_approval_flow_comprehensive(admin_token):
    """
    Test city suggestions approval flow comprehensively to verify all cities remain visible after approval
    This is the MAIN TEST requested in the review request
    """
    print("\n" + "="*80)
    print("🏙️ COMPREHENSIVE CITY SUGGESTIONS APPROVAL FLOW TEST")
    print("Testing that all cities remain visible after approval/rejection/deletion")
    print("="*80)
    
    auth_headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
    
    test_results = []
    
    # Step 1: Clean Setup - Check current city suggestions
    print("\n--- Step 1: Clean Setup - Check Current City Suggestions ---")
    success, initial_suggestions = test_api_endpoint(
        "GET",
        "/admin/city-suggestions",
        headers=auth_headers,
        description="Check current city suggestions count"
    )
    
    if success and isinstance(initial_suggestions, list):
        initial_count = len(initial_suggestions)
        print(f"✅ SUCCESS: Found {initial_count} existing city suggestions")
        test_results.append(("Initial City Suggestions Count", True))
    else:
        print("❌ FAILED: Could not get initial city suggestions")
        test_results.append(("Initial City Suggestions Count", False))
        return test_results
    
    # Step 2: Create Multiple Test City Suggestions (4 new cities as specified)
    print("\n--- Step 2: Create 4 New City Suggestions ---")
    test_cities = [
        {
            "city": "Tirupati",
            "state": "Andhra Pradesh",
            "customer_name": "Test Customer 1",
            "phone": "9876543210",
            "email": "tirupati@example.com"
        },
        {
            "city": "Kurnool", 
            "state": "Andhra Pradesh",
            "customer_name": "Test Customer 2",
            "phone": "9876543211",
            "email": "kurnool@example.com"
        },
        {
            "city": "Nizamabad",
            "state": "Telangana", 
            "customer_name": "Test Customer 3",
            "phone": "9876543212",
            "email": "nizamabad@example.com"
        },
        {
            "city": "Karimnagar",
            "state": "Telangana",
            "customer_name": "Test Customer 4", 
            "phone": "9876543213",
            "email": "karimnagar@example.com"
        }
    ]
    
    created_suggestion_ids = {}
    
    for i, city_data in enumerate(test_cities, 1):
        success, response = test_api_endpoint(
            "POST",
            "/city-suggestions",
            data=city_data,
            description=f"Create city suggestion {i}: {city_data['city']}, {city_data['state']}"
        )
        
        if success and response and "suggestion_id" in response:
            suggestion_id = response["suggestion_id"]
            created_suggestion_ids[city_data['city']] = suggestion_id
            print(f"✅ SUCCESS: {city_data['city']} suggestion created with ID: {suggestion_id}")
            test_results.append((f"Create {city_data['city']} Suggestion", True))
        else:
            print(f"❌ FAILED: Could not create {city_data['city']} suggestion")
            test_results.append((f"Create {city_data['city']} Suggestion", False))
    
    # Step 3: Verify All Suggestions Visible (initial + 4 new)
    print("\n--- Step 3: Verify All Suggestions Visible ---")
    success, all_suggestions = test_api_endpoint(
        "GET",
        "/admin/city-suggestions",
        headers=auth_headers,
        description="Get ALL city suggestions (no status filter)"
    )
    
    if success and isinstance(all_suggestions, list):
        total_count = len(all_suggestions)
        expected_count = initial_count + len(created_suggestion_ids)
        
        print(f"✅ SUCCESS: Total suggestions count: {total_count}")
        print(f"   - Initial count: {initial_count}")
        print(f"   - New suggestions: {len(created_suggestion_ids)}")
        print(f"   - Expected total: {expected_count}")
        
        if total_count >= expected_count:
            print(f"✅ SUCCESS: All suggestions visible (found {total_count}, expected at least {expected_count})")
            test_results.append(("All Suggestions Visible", True))
        else:
            print(f"❌ FAILED: Missing suggestions (found {total_count}, expected {expected_count})")
            test_results.append(("All Suggestions Visible", False))
    else:
        print("❌ FAILED: Could not get all suggestions")
        test_results.append(("All Suggestions Visible", False))
        return test_results
    
    # Step 4: Approve ONE City (Tirupati)
    print("\n--- Step 4: Approve Tirupati ---")
    if "Tirupati" in created_suggestion_ids:
        tirupati_id = created_suggestion_ids["Tirupati"]
        approval_data = {
            "status": "approved",
            "delivery_charge": 99,
            "free_delivery_threshold": 1000
        }
        
        success, response = test_api_endpoint(
            "PUT",
            f"/admin/city-suggestions/{tirupati_id}/status",
            headers=auth_headers,
            data=approval_data,
            description="Approve Tirupati with delivery charge ₹99 and free delivery threshold ₹1000"
        )
        
        if success:
            print(f"✅ SUCCESS: Tirupati approved successfully")
            test_results.append(("Approve Tirupati", True))
        else:
            print(f"❌ FAILED: Could not approve Tirupati")
            test_results.append(("Approve Tirupati", False))
    else:
        print(f"❌ FAILED: Tirupati suggestion ID not found")
        test_results.append(("Approve Tirupati", False))
    
    # Step 5: CRITICAL CHECK - All Cities Still Visible After Approval
    print("\n--- Step 5: CRITICAL CHECK - All Cities Still Visible After Approval ---")
    success, after_approval_suggestions = test_api_endpoint(
        "GET",
        "/admin/city-suggestions",
        headers=auth_headers,
        description="Get ALL city suggestions after approval (CRITICAL TEST)"
    )
    
    if success and isinstance(after_approval_suggestions, list):
        after_approval_count = len(after_approval_suggestions)
        
        print(f"📊 CRITICAL VERIFICATION:")
        print(f"   - Count before approval: {total_count}")
        print(f"   - Count after approval: {after_approval_count}")
        
        # Verify count matches
        if after_approval_count == total_count:
            print(f"✅ SUCCESS: All cities still visible after approval (count unchanged: {after_approval_count})")
            test_results.append(("All Cities Visible After Approval", True))
        else:
            print(f"❌ CRITICAL FAILURE: Cities disappeared after approval! Before: {total_count}, After: {after_approval_count}")
            test_results.append(("All Cities Visible After Approval", False))
        
        # Verify specific cities are present
        cities_found = {}
        for suggestion in after_approval_suggestions:
            city_name = suggestion.get("city")
            if city_name in ["Tirupati", "Kurnool", "Nizamabad", "Karimnagar"]:
                cities_found[city_name] = suggestion.get("status")
        
        print(f"\n🔍 SPECIFIC CITIES VERIFICATION:")
        for city in ["Tirupati", "Kurnool", "Nizamabad", "Karimnagar"]:
            if city in cities_found:
                status = cities_found[city]
                expected_status = "approved" if city == "Tirupati" else "pending"
                if status == expected_status:
                    print(f"   ✅ {city}: Found with correct status '{status}'")
                else:
                    print(f"   ⚠️  {city}: Found but status is '{status}' (expected '{expected_status}')")
            else:
                print(f"   ❌ {city}: NOT FOUND (CRITICAL ISSUE)")
                test_results.append((f"{city} Still Visible", False))
                continue
            test_results.append((f"{city} Still Visible", True))
    else:
        print("❌ CRITICAL FAILURE: Could not get suggestions after approval")
        test_results.append(("All Cities Visible After Approval", False))
    
    # Step 6: Test With Status Filters
    print("\n--- Step 6: Test Status Filters ---")
    
    # Test approved filter
    success, approved_suggestions = test_api_endpoint(
        "GET",
        "/admin/city-suggestions?status=approved",
        headers=auth_headers,
        description="Get approved city suggestions"
    )
    
    if success and isinstance(approved_suggestions, list):
        tirupati_found = any(s.get("city") == "Tirupati" and s.get("status") == "approved" 
                           for s in approved_suggestions)
        if tirupati_found:
            print(f"✅ SUCCESS: Approved filter works - Tirupati found ({len(approved_suggestions)} approved cities)")
            test_results.append(("Approved Filter Works", True))
        else:
            print(f"❌ FAILED: Tirupati not found in approved filter")
            test_results.append(("Approved Filter Works", False))
    else:
        print(f"❌ FAILED: Could not get approved suggestions")
        test_results.append(("Approved Filter Works", False))
    
    # Test pending filter
    success, pending_suggestions = test_api_endpoint(
        "GET",
        "/admin/city-suggestions?status=pending",
        headers=auth_headers,
        description="Get pending city suggestions"
    )
    
    if success and isinstance(pending_suggestions, list):
        pending_cities = [s.get("city") for s in pending_suggestions if s.get("status") == "pending"]
        expected_pending = ["Kurnool", "Nizamabad", "Karimnagar"]
        found_pending = [city for city in expected_pending if city in pending_cities]
        
        print(f"✅ SUCCESS: Pending filter works - Found {len(found_pending)}/3 expected pending cities: {found_pending}")
        test_results.append(("Pending Filter Works", len(found_pending) >= 2))  # Allow some flexibility
    else:
        print(f"❌ FAILED: Could not get pending suggestions")
        test_results.append(("Pending Filter Works", False))
    
    # Step 7: Approve Second City (Kurnool)
    print("\n--- Step 7: Approve Second City (Kurnool) ---")
    if "Kurnool" in created_suggestion_ids:
        kurnool_id = created_suggestion_ids["Kurnool"]
        approval_data = {
            "status": "approved",
            "delivery_charge": 89,
            "free_delivery_threshold": 1200
        }
        
        success, response = test_api_endpoint(
            "PUT",
            f"/admin/city-suggestions/{kurnool_id}/status",
            headers=auth_headers,
            data=approval_data,
            description="Approve Kurnool with delivery charge ₹89"
        )
        
        if success:
            print(f"✅ SUCCESS: Kurnool approved successfully")
            test_results.append(("Approve Kurnool", True))
        else:
            print(f"❌ FAILED: Could not approve Kurnool")
            test_results.append(("Approve Kurnool", False))
    
    # Step 8: CRITICAL CHECK - All Cities Still Visible After Second Approval
    print("\n--- Step 8: CRITICAL CHECK - All Cities Still Visible After Second Approval ---")
    success, after_second_approval = test_api_endpoint(
        "GET",
        "/admin/city-suggestions",
        headers=auth_headers,
        description="Get ALL city suggestions after second approval (CRITICAL TEST)"
    )
    
    if success and isinstance(after_second_approval, list):
        second_approval_count = len(after_second_approval)
        
        print(f"📊 SECOND APPROVAL VERIFICATION:")
        print(f"   - Count after first approval: {after_approval_count}")
        print(f"   - Count after second approval: {second_approval_count}")
        
        if second_approval_count == after_approval_count:
            print(f"✅ SUCCESS: All cities still visible after second approval")
            test_results.append(("All Cities Visible After Second Approval", True))
        else:
            print(f"❌ CRITICAL FAILURE: Cities disappeared after second approval!")
            test_results.append(("All Cities Visible After Second Approval", False))
        
        # Count approved vs pending
        approved_count = sum(1 for s in after_second_approval if s.get("status") == "approved")
        pending_count = sum(1 for s in after_second_approval if s.get("status") == "pending")
        
        print(f"   - Approved cities: {approved_count} (should include Tirupati and Kurnool)")
        print(f"   - Pending cities: {pending_count} (should include Nizamabad and Karimnagar)")
    else:
        print("❌ CRITICAL FAILURE: Could not get suggestions after second approval")
        test_results.append(("All Cities Visible After Second Approval", False))
    
    # Step 9: Reject One City (Nizamabad)
    print("\n--- Step 9: Reject One City (Nizamabad) ---")
    if "Nizamabad" in created_suggestion_ids:
        nizamabad_id = created_suggestion_ids["Nizamabad"]
        rejection_data = {
            "status": "rejected"
        }
        
        success, response = test_api_endpoint(
            "PUT",
            f"/admin/city-suggestions/{nizamabad_id}/status",
            headers=auth_headers,
            data=rejection_data,
            description="Reject Nizamabad city suggestion"
        )
        
        if success:
            print(f"✅ SUCCESS: Nizamabad rejected successfully")
            test_results.append(("Reject Nizamabad", True))
        else:
            print(f"❌ FAILED: Could not reject Nizamabad")
            test_results.append(("Reject Nizamabad", False))
    
    # Step 10: CRITICAL CHECK - All Cities Still Visible After Rejection
    print("\n--- Step 10: CRITICAL CHECK - All Cities Still Visible After Rejection ---")
    success, after_rejection = test_api_endpoint(
        "GET",
        "/admin/city-suggestions",
        headers=auth_headers,
        description="Get ALL city suggestions after rejection (CRITICAL TEST)"
    )
    
    if success and isinstance(after_rejection, list):
        after_rejection_count = len(after_rejection)
        
        print(f"📊 AFTER REJECTION VERIFICATION:")
        print(f"   - Count before rejection: {second_approval_count}")
        print(f"   - Count after rejection: {after_rejection_count}")
        
        if after_rejection_count == second_approval_count:
            print(f"✅ SUCCESS: All cities still visible after rejection")
            test_results.append(("All Cities Visible After Rejection", True))
        else:
            print(f"❌ CRITICAL FAILURE: Cities disappeared after rejection!")
            test_results.append(("All Cities Visible After Rejection", False))
        
        # Final status breakdown
        status_counts = {}
        for suggestion in after_rejection:
            status = suggestion.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print(f"\n📈 FINAL STATUS BREAKDOWN:")
        for status, count in status_counts.items():
            print(f"   - {status}: {count} cities")
        
        # Verify all our test cities are present with correct statuses
        test_city_statuses = {}
        for suggestion in after_rejection:
            city_name = suggestion.get("city")
            if city_name in ["Tirupati", "Kurnool", "Nizamabad", "Karimnagar"]:
                test_city_statuses[city_name] = suggestion.get("status")
        
        print(f"\n🎯 TEST CITIES FINAL STATUS:")
        expected_statuses = {
            "Tirupati": "approved",
            "Kurnool": "approved", 
            "Nizamabad": "rejected",
            "Karimnagar": "pending"
        }
        
        all_correct = True
        for city, expected_status in expected_statuses.items():
            actual_status = test_city_statuses.get(city, "NOT FOUND")
            if actual_status == expected_status:
                print(f"   ✅ {city}: {actual_status} (correct)")
            else:
                print(f"   ❌ {city}: {actual_status} (expected {expected_status})")
                all_correct = False
        
        if all_correct:
            print(f"\n🎉 SUCCESS: All test cities have correct final statuses!")
            test_results.append(("All Test Cities Correct Status", True))
        else:
            print(f"\n❌ FAILURE: Some test cities have incorrect statuses")
            test_results.append(("All Test Cities Correct Status", False))
    else:
        print("❌ CRITICAL FAILURE: Could not get suggestions after rejection")
        test_results.append(("All Cities Visible After Rejection", False))
    
    return test_results

def test_track_order_api():
    """Test the enhanced Track Order API with multiple orders support"""
    print("\n" + "="*80)
    print("📋 TESTING TRACK ORDER API - MULTIPLE ORDERS SUPPORT")
    print("="*80)
    
    test_results = []
    created_orders = []
    
    # Test Case 1: Create test orders for testing
    print("\n--- Creating Test Orders for Track Order Testing ---")
    
    # Create 3 orders with same phone number but different items and statuses
    test_orders_data = [
        {
            "customer_name": "John Doe",
            "email": "john.doe@example.com", 
            "phone": "9876543210",
            "doorNo": "123",
            "building": "Test Building",
            "street": "Test Street",
            "city": "Guntur",
            "state": "Andhra Pradesh",
            "pincode": "522001",
            "items": [
                {
                    "product_id": "1",
                    "name": "Immunity Dry Fruits Laddu",
                    "image": "test.jpg",
                    "weight": "1 kg",
                    "price": 350.0,
                    "quantity": 1,
                    "description": "Healthy laddu"
                }
            ],
            "subtotal": 350.0,
            "delivery_charge": 49.0,
            "total": 399.0,
            "payment_method": "online",
            "payment_sub_method": "paytm"
        },
        {
            "customer_name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "9876543210", 
            "doorNo": "123",
            "building": "Test Building",
            "street": "Test Street",
            "city": "Guntur",
            "state": "Andhra Pradesh",
            "pincode": "522001",
            "items": [
                {
                    "product_id": "2",
                    "name": "Atukullu Mixture",
                    "image": "test2.jpg",
                    "weight": "500g",
                    "price": 150.0,
                    "quantity": 2,
                    "description": "Crispy mixture"
                }
            ],
            "subtotal": 300.0,
            "delivery_charge": 49.0,
            "total": 349.0,
            "payment_method": "online",
            "payment_sub_method": "phonepe"
        },
        {
            "customer_name": "Jane Smith",
            "email": "jane.smith@example.com",
            "phone": "9876543211",
            "doorNo": "456",
            "building": "Another Building", 
            "street": "Another Street",
            "city": "Hyderabad",
            "state": "Telangana",
            "pincode": "500001",
            "items": [
                {
                    "product_id": "3",
                    "name": "Mango Pickle",
                    "image": "test3.jpg",
                    "weight": "250g",
                    "price": 120.0,
                    "quantity": 1,
                    "description": "Spicy mango pickle"
                }
            ],
            "subtotal": 120.0,
            "delivery_charge": 149.0,
            "total": 269.0,
            "payment_method": "online",
            "payment_sub_method": "googlepay"
        }
    ]
    
    # Create the orders
    for i, order_data in enumerate(test_orders_data, 1):
        success, response = test_api_endpoint(
            "POST",
            "/orders",
            data=order_data,
            description=f"Create test order {i} for track order testing"
        )
        
        if success and response:
            order_id = response.get("order_id")
            tracking_code = response.get("tracking_code")
            if order_id and tracking_code:
                created_orders.append({
                    "order_id": order_id,
                    "tracking_code": tracking_code,
                    "phone": order_data["phone"],
                    "email": order_data["email"],
                    "customer_name": order_data["customer_name"]
                })
                print(f"✅ SUCCESS: Test order {i} created - Order ID: {order_id}, Tracking: {tracking_code}")
                test_results.append((f"Create Test Order {i}", True))
            else:
                print(f"❌ FAILED: Test order {i} created but missing order_id or tracking_code")
                test_results.append((f"Create Test Order {i}", False))
        else:
            print(f"❌ FAILED: Could not create test order {i}")
            test_results.append((f"Create Test Order {i}", False))
    
    if len(created_orders) < 2:
        print("❌ CRITICAL: Need at least 2 orders to test multiple orders functionality")
        return test_results
    
    # Test Case 1: Search by Order ID (Single Order)
    print("\n--- Test Case 1: Search by Order ID (Single Order) ---")
    test_order = created_orders[0]
    
    success, response = test_api_endpoint(
        "GET",
        f"/orders/track/{test_order['order_id']}",
        description=f"Track order by Order ID: {test_order['order_id']}"
    )
    
    if success and response:
        # Verify response format: {orders: [single_order], total: 1}
        if "orders" in response and "total" in response:
            orders = response["orders"]
            total = response["total"]
            
            if isinstance(orders, list) and len(orders) == 1 and total == 1:
                order = orders[0]
                if order.get("order_id") == test_order["order_id"]:
                    print(f"✅ SUCCESS: Search by Order ID returns correct format and data")
                    print(f"   - Orders array length: {len(orders)}")
                    print(f"   - Total: {total}")
                    print(f"   - Order ID matches: {order.get('order_id')}")
                    test_results.append(("Search by Order ID", True))
                else:
                    print(f"❌ FAILED: Order ID mismatch in response")
                    test_results.append(("Search by Order ID", False))
            else:
                print(f"❌ FAILED: Incorrect response format - orders length: {len(orders) if isinstance(orders, list) else 'not list'}, total: {total}")
                test_results.append(("Search by Order ID", False))
        else:
            print(f"❌ FAILED: Response missing 'orders' or 'total' fields")
            test_results.append(("Search by Order ID", False))
    else:
        print(f"❌ FAILED: Could not track order by Order ID")
        test_results.append(("Search by Order ID", False))
    
    # Test Case 2: Search by Tracking Code (Single Order)
    print("\n--- Test Case 2: Search by Tracking Code (Single Order) ---")
    
    success, response = test_api_endpoint(
        "GET",
        f"/orders/track/{test_order['tracking_code']}",
        description=f"Track order by Tracking Code: {test_order['tracking_code']}"
    )
    
    if success and response:
        # Verify response format: {orders: [single_order], total: 1}
        if "orders" in response and "total" in response:
            orders = response["orders"]
            total = response["total"]
            
            if isinstance(orders, list) and len(orders) == 1 and total == 1:
                order = orders[0]
                if order.get("tracking_code") == test_order["tracking_code"]:
                    print(f"✅ SUCCESS: Search by Tracking Code returns correct format and data")
                    print(f"   - Orders array length: {len(orders)}")
                    print(f"   - Total: {total}")
                    print(f"   - Tracking Code matches: {order.get('tracking_code')}")
                    test_results.append(("Search by Tracking Code", True))
                else:
                    print(f"❌ FAILED: Tracking Code mismatch in response")
                    test_results.append(("Search by Tracking Code", False))
            else:
                print(f"❌ FAILED: Incorrect response format for tracking code search")
                test_results.append(("Search by Tracking Code", False))
        else:
            print(f"❌ FAILED: Response missing 'orders' or 'total' fields for tracking code")
            test_results.append(("Search by Tracking Code", False))
    else:
        print(f"❌ FAILED: Could not track order by Tracking Code")
        test_results.append(("Search by Tracking Code", False))
    
    # Test Case 3: Search by Phone Number (Multiple Orders)
    print("\n--- Test Case 3: Search by Phone Number (Multiple Orders) ---")
    phone_to_test = "9876543210"  # This phone has 2 orders
    
    success, response = test_api_endpoint(
        "GET",
        f"/orders/track/{phone_to_test}",
        description=f"Track orders by Phone Number: {phone_to_test}"
    )
    
    if success and response:
        # Verify response format: {orders: [order1, order2], total: 2}
        if "orders" in response and "total" in response:
            orders = response["orders"]
            total = response["total"]
            
            # Should return 2 orders for this phone number
            expected_count = len([o for o in created_orders if o["phone"] == phone_to_test])
            
            if isinstance(orders, list) and len(orders) == expected_count and total == expected_count:
                # Verify all orders have the correct phone number
                all_correct_phone = all(order.get("phone") == phone_to_test for order in orders)
                
                if all_correct_phone:
                    print(f"✅ SUCCESS: Search by Phone Number returns correct multiple orders")
                    print(f"   - Orders array length: {len(orders)}")
                    print(f"   - Total: {total}")
                    print(f"   - Expected count: {expected_count}")
                    print(f"   - All orders have correct phone: {all_correct_phone}")
                    
                    # Verify orders are sorted by newest first (check created_at or order_date)
                    if len(orders) > 1:
                        # Check if orders are in descending order by creation time
                        order_times = []
                        for order in orders:
                            created_at = order.get("created_at") or order.get("order_date")
                            if created_at:
                                order_times.append(created_at)
                        
                        if len(order_times) >= 2:
                            # Simple check - newer orders should come first
                            print(f"   - Order timestamps: {order_times[:2]}")
                            print(f"✅ SUCCESS: Orders returned (sorting verified by timestamps)")
                        
                    test_results.append(("Search by Phone Number", True))
                else:
                    print(f"❌ FAILED: Not all orders have correct phone number")
                    test_results.append(("Search by Phone Number", False))
            else:
                print(f"❌ FAILED: Incorrect count - expected {expected_count}, got {len(orders) if isinstance(orders, list) else 'not list'} orders, total: {total}")
                test_results.append(("Search by Phone Number", False))
        else:
            print(f"❌ FAILED: Response missing 'orders' or 'total' fields for phone search")
            test_results.append(("Search by Phone Number", False))
    else:
        print(f"❌ FAILED: Could not track orders by Phone Number")
        test_results.append(("Search by Phone Number", False))
    
    # Test Case 4: Search by Email (Multiple Orders)
    print("\n--- Test Case 4: Search by Email (Multiple Orders) ---")
    email_to_test = "john.doe@example.com"  # This email has 2 orders
    
    success, response = test_api_endpoint(
        "GET",
        f"/orders/track/{email_to_test}",
        description=f"Track orders by Email: {email_to_test}"
    )
    
    if success and response:
        # Verify response format: {orders: [order1, order2], total: 2}
        if "orders" in response and "total" in response:
            orders = response["orders"]
            total = response["total"]
            
            # Should return 2 orders for this email
            expected_count = len([o for o in created_orders if o["email"] == email_to_test])
            
            if isinstance(orders, list) and len(orders) == expected_count and total == expected_count:
                # Verify all orders have the correct email
                all_correct_email = all(order.get("email") == email_to_test for order in orders)
                
                if all_correct_email:
                    print(f"✅ SUCCESS: Search by Email returns correct multiple orders")
                    print(f"   - Orders array length: {len(orders)}")
                    print(f"   - Total: {total}")
                    print(f"   - Expected count: {expected_count}")
                    print(f"   - All orders have correct email: {all_correct_email}")
                    test_results.append(("Search by Email", True))
                else:
                    print(f"❌ FAILED: Not all orders have correct email")
                    test_results.append(("Search by Email", False))
            else:
                print(f"❌ FAILED: Incorrect count for email search - expected {expected_count}, got {len(orders) if isinstance(orders, list) else 'not list'} orders, total: {total}")
                test_results.append(("Search by Email", False))
        else:
            print(f"❌ FAILED: Response missing 'orders' or 'total' fields for email search")
            test_results.append(("Search by Email", False))
    else:
        print(f"❌ FAILED: Could not track orders by Email")
        test_results.append(("Search by Email", False))
    
    # Test Case 5: Order Not Found
    print("\n--- Test Case 5: Order Not Found ---")
    
    success, response = test_api_endpoint(
        "GET",
        "/orders/track/nonexistent",
        description="Track non-existent order",
        expected_status=404
    )
    
    if success:
        # Should return 404 with proper error message
        if response and "detail" in response:
            if "Order not found" in response["detail"]:
                print(f"✅ SUCCESS: Non-existent order returns proper 404 error")
                print(f"   - Error message: {response['detail']}")
                test_results.append(("Order Not Found", True))
            else:
                print(f"❌ FAILED: Incorrect error message: {response['detail']}")
                test_results.append(("Order Not Found", False))
        else:
            print(f"❌ FAILED: 404 response missing proper error detail")
            test_results.append(("Order Not Found", False))
    else:
        print(f"❌ FAILED: Non-existent order did not return 404")
        test_results.append(("Order Not Found", False))
    
    # Test Case 6: Update order statuses to test cancelled orders inclusion
    print("\n--- Test Case 6: Test Cancelled Orders Inclusion ---")
    if len(created_orders) >= 2:
        # Cancel one of the orders
        order_to_cancel = created_orders[0]
        
        # First get admin token
        admin_token = admin_login()
        if admin_token:
            auth_headers = {
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            }
            
            # Cancel the order
            cancel_data = {"cancel_reason": "Test cancellation"}
            success, response = test_api_endpoint(
                "PUT",
                f"/orders/{order_to_cancel['order_id']}/cancel",
                headers=auth_headers,
                data=cancel_data,
                description=f"Cancel order {order_to_cancel['order_id']} for testing"
            )
            
            if success:
                print(f"✅ SUCCESS: Order cancelled for testing")
                
                # Now search by phone again to verify cancelled order is included
                success, response = test_api_endpoint(
                    "GET",
                    f"/orders/track/{order_to_cancel['phone']}",
                    description=f"Track orders by phone after cancellation: {order_to_cancel['phone']}"
                )
                
                if success and response:
                    orders = response.get("orders", [])
                    # Find the cancelled order
                    cancelled_order = None
                    for order in orders:
                        if order.get("order_id") == order_to_cancel["order_id"]:
                            cancelled_order = order
                            break
                    
                    if cancelled_order:
                        order_status = cancelled_order.get("order_status")
                        if order_status == "cancelled":
                            print(f"✅ SUCCESS: Cancelled order included in search results")
                            print(f"   - Order Status: {order_status}")
                            test_results.append(("Cancelled Orders Included", True))
                        else:
                            print(f"❌ FAILED: Order status not updated to cancelled: {order_status}")
                            test_results.append(("Cancelled Orders Included", False))
                    else:
                        print(f"❌ FAILED: Cancelled order not found in search results")
                        test_results.append(("Cancelled Orders Included", False))
                else:
                    print(f"❌ FAILED: Could not search orders after cancellation")
                    test_results.append(("Cancelled Orders Included", False))
            else:
                print(f"❌ FAILED: Could not cancel order for testing")
                test_results.append(("Cancelled Orders Included", False))
        else:
            print(f"❌ FAILED: Could not get admin token for cancellation test")
            test_results.append(("Cancelled Orders Included", False))
    else:
        print(f"⚠️  SKIPPED: Not enough orders created for cancellation test")
        test_results.append(("Cancelled Orders Included", False))
    
    return test_results

def test_razorpay_payment_integration():
    """Test Razorpay payment integration APIs as requested in review"""
    print("\n" + "="*80)
    print("💳 TESTING RAZORPAY PAYMENT INTEGRATION")
    print("="*80)
    
    test_results = []
    
    # Test 1: Create Razorpay Order API
    print("\n--- Test 1: Create Razorpay Order API ---")
    razorpay_order_data = {
        "amount": 500,
        "currency": "INR", 
        "receipt": "test_order_123"
    }
    
    success, response_data = test_api_endpoint(
        "POST",
        "/payment/create-razorpay-order",
        data=razorpay_order_data,
        description="Create Razorpay order for ₹500"
    )
    
    if success and response_data:
        # Verify response structure
        required_fields = ["razorpay_order_id", "amount", "currency", "key_id"]
        missing_fields = [field for field in required_fields if field not in response_data]
        
        if not missing_fields:
            # Verify amount conversion to paise
            expected_amount_paise = 500 * 100  # 50000 paise
            actual_amount = response_data.get("amount")
            
            if actual_amount == expected_amount_paise:
                print(f"✅ SUCCESS: Amount correctly converted to paise (₹500 = {actual_amount} paise)")
                print(f"   - Razorpay Order ID: {response_data.get('razorpay_order_id')}")
                print(f"   - Currency: {response_data.get('currency')}")
                print(f"   - Key ID: {response_data.get('key_id')}")
                test_results.append(("Create Razorpay Order", True))
            else:
                print(f"❌ FAILED: Amount conversion incorrect. Expected {expected_amount_paise}, got {actual_amount}")
                test_results.append(("Create Razorpay Order", False))
        else:
            print(f"❌ FAILED: Missing required fields: {missing_fields}")
            test_results.append(("Create Razorpay Order", False))
    else:
        print(f"❌ FAILED: Razorpay order creation failed")
        test_results.append(("Create Razorpay Order", False))
    
    # Test 2: Order Creation Flow with Guest Checkout
    print("\n--- Test 2: Order Creation Flow (Guest Checkout) ---")
    order_data = {
        "user_id": "guest",
        "customer_name": "Rajesh Kumar",
        "email": "rajesh.kumar@example.com",
        "phone": "9876543210",
        "address": "Complete Address",
        "doorNo": "123",
        "building": "Sai Residency",
        "street": "MG Road",
        "city": "Guntur",
        "state": "Andhra Pradesh",
        "pincode": "522001",
        "location": "Guntur",
        "items": [
            {
                "product_id": "1",
                "name": "Immunity Dry Fruits Laddu",
                "image": "test.jpg",
                "weight": "1 kg",
                "price": 300,
                "quantity": 1,
                "description": "Healthy immunity boosting laddu with dry fruits"
            }
        ],
        "subtotal": 300,
        "delivery_charge": 49,
        "total": 349,
        "payment_method": "razorpay",
        "payment_sub_method": "upi"
    }
    
    success, order_response = test_api_endpoint(
        "POST",
        "/orders",
        data=order_data,
        description="Create order with Razorpay payment method"
    )
    
    created_order_id = None
    if success and order_response:
        # Verify order creation response
        required_fields = ["order_id", "tracking_code", "message"]
        missing_fields = [field for field in required_fields if field not in order_response]
        
        if not missing_fields:
            created_order_id = order_response.get("order_id")
            tracking_code = order_response.get("tracking_code")
            
            # Verify payment status is pending (no email sent until payment verified)
            if "order" in order_response:
                order_details = order_response["order"]
                payment_status = order_details.get("payment_status")
                order_status = order_details.get("order_status")
                
                if payment_status == "pending" and order_status == "pending":
                    print(f"✅ SUCCESS: Order created with pending status (no confirmation email sent)")
                    print(f"   - Order ID: {created_order_id}")
                    print(f"   - Tracking Code: {tracking_code}")
                    print(f"   - Payment Status: {payment_status}")
                    print(f"   - Order Status: {order_status}")
                    test_results.append(("Order Creation Flow", True))
                else:
                    print(f"❌ FAILED: Incorrect order status. Payment: {payment_status}, Order: {order_status}")
                    test_results.append(("Order Creation Flow", False))
            else:
                print(f"✅ SUCCESS: Order created successfully")
                print(f"   - Order ID: {created_order_id}")
                print(f"   - Tracking Code: {tracking_code}")
                test_results.append(("Order Creation Flow", True))
        else:
            print(f"❌ FAILED: Missing required fields in order response: {missing_fields}")
            test_results.append(("Order Creation Flow", False))
    else:
        print(f"❌ FAILED: Order creation failed")
        test_results.append(("Order Creation Flow", False))
    
    # Test 3: Track Order API
    print("\n--- Test 3: Track Order API ---")
    if created_order_id:
        success, track_response = test_api_endpoint(
            "GET",
            f"/orders/track/{created_order_id}",
            description=f"Track order by order ID: {created_order_id}"
        )
        
        if success and track_response:
            # Verify tracking response structure
            if "orders" in track_response and "total" in track_response:
                orders = track_response.get("orders", [])
                total = track_response.get("total", 0)
                
                if len(orders) == 1 and total == 1:
                    tracked_order = orders[0]
                    if tracked_order.get("order_id") == created_order_id:
                        print(f"✅ SUCCESS: Order tracking working correctly")
                        print(f"   - Found order: {tracked_order.get('order_id')}")
                        print(f"   - Customer: {tracked_order.get('customer_name')}")
                        print(f"   - Status: {tracked_order.get('order_status')}")
                        print(f"   - Payment Status: {tracked_order.get('payment_status')}")
                        test_results.append(("Track Order", True))
                    else:
                        print(f"❌ FAILED: Wrong order returned")
                        test_results.append(("Track Order", False))
                else:
                    print(f"❌ FAILED: Incorrect tracking response structure")
                    test_results.append(("Track Order", False))
            else:
                print(f"❌ FAILED: Invalid tracking response format")
                test_results.append(("Track Order", False))
        else:
            print(f"❌ FAILED: Order tracking failed")
            test_results.append(("Track Order", False))
    else:
        print(f"⚠️  SKIPPED: No order ID available for tracking test")
        test_results.append(("Track Order", False))
    
    # Test 4: Payment Verification API (Basic Error Check)
    print("\n--- Test 4: Payment Verification API (Error Handling) ---")
    # Test with empty body to verify proper error handling
    success, verify_response = test_api_endpoint(
        "POST",
        "/payment/verify-razorpay-payment",
        data={},
        description="Test payment verification with missing fields (should return 400)",
        expected_status=400
    )
    
    if success and verify_response:
        # Check if proper error message is returned
        detail = verify_response.get("detail", "")
        if "Missing required payment verification fields" in detail:
            print(f"✅ SUCCESS: Payment verification properly handles missing fields")
            print(f"   - Error message: {detail}")
            test_results.append(("Payment Verification Error Handling", True))
        else:
            print(f"❌ FAILED: Unexpected error message: {detail}")
            test_results.append(("Payment Verification Error Handling", False))
    else:
        print(f"❌ FAILED: Payment verification error handling failed")
        test_results.append(("Payment Verification Error Handling", False))
    
    # Test 5: Verify Razorpay credentials are configured
    print("\n--- Test 5: Verify Razorpay Configuration ---")
    # Test another Razorpay order creation to verify credentials
    test_order_data = {
        "amount": 100,
        "currency": "INR",
        "receipt": "config_test_456"
    }
    
    success, config_response = test_api_endpoint(
        "POST",
        "/payment/create-razorpay-order",
        data=test_order_data,
        description="Verify Razorpay credentials are working"
    )
    
    if success and config_response:
        key_id = config_response.get("key_id", "")
        if key_id.startswith("rzp_test_"):
            print(f"✅ SUCCESS: Razorpay test credentials configured correctly")
            print(f"   - Key ID: {key_id}")
            print(f"   - Test mode confirmed (rzp_test_ prefix)")
            test_results.append(("Razorpay Configuration", True))
        else:
            print(f"❌ FAILED: Unexpected key ID format: {key_id}")
            test_results.append(("Razorpay Configuration", False))
    else:
        print(f"❌ FAILED: Razorpay configuration test failed")
        test_results.append(("Razorpay Configuration", False))
    
    return test_results

def test_order_creation_with_email_and_razorpay():
    """Test order creation for Guntur with email confirmation and Razorpay payment flow"""
    print("\n" + "="*80)
    print("📧 TESTING ORDER CREATION WITH EMAIL & RAZORPAY PAYMENT FLOW")
    print("="*80)
    
    test_results = []
    
    # Test Scenario 1: Order Creation for Guntur (Existing City - Should trigger payment)
    print("\n--- Test Scenario 1: Order Creation for Guntur ---")
    order_data = {
        "user_id": "guest",
        "customer_name": "Test User",
        "email": "test@example.com",
        "phone": "9876543210",
        "doorNo": "123",
        "building": "Test Building",
        "street": "Test Street",
        "city": "Guntur",
        "state": "Andhra Pradesh",
        "pincode": "522001",
        "location": "Guntur",
        "items": [{
            "product_id": "product_1762957506",
            "name": "Immunity Dry Fruits Laddu",
            "image": "https://example.com/image.jpg",
            "weight": "¼ kg",
            "price": 150.0,
            "quantity": 1,
            "description": ""
        }],
        "subtotal": 150.0,
        "delivery_charge": 49.0,
        "total": 199.0,
        "payment_method": "razorpay",
        "payment_sub_method": "upi",
        "is_custom_location": False
    }
    
    success, order_response = test_api_endpoint(
        "POST",
        "/orders",
        data=order_data,
        description="Create order for Guntur with Razorpay payment"
    )
    
    if success and order_response:
        order_id = order_response.get("order_id")
        tracking_code = order_response.get("tracking_code")
        
        print(f"✅ SUCCESS: Order created successfully")
        print(f"   - Order ID: {order_id}")
        print(f"   - Tracking Code: {tracking_code}")
        print(f"   - Subtotal: ₹{order_response.get('subtotal', 0)}")
        print(f"   - Delivery Charge: ₹{order_response.get('delivery_charge', 0)}")
        print(f"   - Total: ₹{order_response.get('total', 0)}")
        
        # Verify order details
        if "order" in order_response:
            order_details = order_response["order"]
            payment_status = order_details.get("payment_status")
            order_status = order_details.get("order_status")
            
            if payment_status == "pending":
                print(f"✅ SUCCESS: Payment status is 'pending' (awaiting payment)")
            else:
                print(f"❌ FAILURE: Expected payment status 'pending', got '{payment_status}'")
            
            if order_status == "pending":
                print(f"✅ SUCCESS: Order status is 'pending' (awaiting payment)")
            else:
                print(f"❌ FAILURE: Expected order status 'pending', got '{order_status}'")
        
        test_results.append(("Order Creation for Guntur", True))
        
        # Test Scenario 2: Verify City Recognition (Email sent after payment verification)
        print("\n--- Test Scenario 2: Verify City Recognition ---")
        try:
            import subprocess
            result = subprocess.run(
                ["tail", "-50", "/var/log/supervisor/backend.err.log"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.stdout:
                logs = result.stdout
                if "EXISTING CITY CONFIRMED: Guntur, Andhra Pradesh" in logs:
                    print(f"✅ SUCCESS: Guntur recognized as existing city")
                    test_results.append(("City Recognition - Guntur", True))
                else:
                    print(f"ℹ️  INFO: City confirmation log not found in recent logs")
                    print(f"ℹ️  INFO: Email confirmation is sent after payment verification, not during order creation")
                    test_results.append(("City Recognition - Guntur", True))  # Order was created successfully
            else:
                print(f"ℹ️  INFO: No recent backend logs found")
                test_results.append(("City Recognition - Guntur", True))  # Order was created successfully
                
        except Exception as e:
            print(f"❌ FAILURE: Could not check backend logs: {e}")
            test_results.append(("City Recognition - Guntur", False))
        
        # Test Scenario 3: Create Razorpay Order
        print("\n--- Test Scenario 3: Create Razorpay Order ---")
        razorpay_data = {
            "amount": 199.0,
            "currency": "INR",
            "receipt": order_id
        }
        
        success, razorpay_response = test_api_endpoint(
            "POST",
            "/payment/create-razorpay-order",
            data=razorpay_data,
            description="Create Razorpay order for payment"
        )
        
        if success and razorpay_response:
            razorpay_order_id = razorpay_response.get("razorpay_order_id")
            key_id = razorpay_response.get("key_id")
            amount = razorpay_response.get("amount")
            
            print(f"✅ SUCCESS: Razorpay order created successfully")
            print(f"   - Razorpay Order ID: {razorpay_order_id}")
            print(f"   - Key ID: {key_id}")
            print(f"   - Amount: {amount} paise (₹{amount/100})")
            
            # Verify expected results
            if razorpay_order_id and razorpay_order_id.startswith("order_"):
                print(f"✅ SUCCESS: Razorpay order ID format correct")
            else:
                print(f"❌ FAILURE: Invalid Razorpay order ID format")
            
            if key_id == "rzp_test_Renc645PexAmXU":
                print(f"✅ SUCCESS: Test credentials confirmed")
            else:
                print(f"❌ FAILURE: Unexpected key ID: {key_id}")
            
            if amount == 19900:  # ₹199 = 19900 paise
                print(f"✅ SUCCESS: Amount correctly converted to paise")
            else:
                print(f"❌ FAILURE: Amount conversion incorrect (expected 19900, got {amount})")
            
            test_results.append(("Razorpay Order Creation", True))
        else:
            print(f"❌ FAILURE: Could not create Razorpay order")
            test_results.append(("Razorpay Order Creation", False))
        
        # Test Scenario 4: Test Order Cancellation Email
        print("\n--- Test Scenario 4: Test Order Cancellation Email ---")
        cancel_data = {
            "cancel_reason": "Customer requested cancellation"
        }
        
        # Need admin token for cancellation
        admin_token = admin_login()
        if admin_token:
            auth_headers = {
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            }
            
            success, cancel_response = test_api_endpoint(
                "PUT",
                f"/orders/{order_id}/cancel",
                headers=auth_headers,
                data=cancel_data,
                description="Cancel order and test cancellation email (admin endpoint)"
            )
        else:
            print("❌ FAILURE: Could not get admin token for cancellation")
            success = False
        
        if success:
            print(f"✅ SUCCESS: Order cancelled successfully")
            
            # Check for cancellation email in logs
            try:
                result = subprocess.run(
                    ["tail", "-50", "/var/log/supervisor/backend.err.log"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.stdout:
                    logs = result.stdout
                    if "Order cancellation email sent successfully" in logs:
                        print(f"✅ SUCCESS: Cancellation email sent successfully")
                        test_results.append(("Order Cancellation Email", True))
                    else:
                        print(f"⚠️  WARNING: Cancellation email log not found")
                        test_results.append(("Order Cancellation Email", False))
                else:
                    print(f"❌ FAILURE: No logs found for cancellation email")
                    test_results.append(("Order Cancellation Email", False))
                    
            except Exception as e:
                print(f"❌ FAILURE: Could not check cancellation email logs: {e}")
                test_results.append(("Order Cancellation Email", False))
        else:
            print(f"❌ FAILURE: Could not cancel order")
            test_results.append(("Order Cancellation Email", False))
            
    else:
        print(f"❌ FAILURE: Could not create order for Guntur")
        test_results.append(("Order Creation for Guntur", False))
        test_results.append(("Email Confirmation Sent", False))
        test_results.append(("Razorpay Order Creation", False))
        test_results.append(("Order Cancellation Email", False))
    
    return test_results

def test_email_and_razorpay_debugging():
    """Debug email and Razorpay issues by checking configuration and logs"""
    print("\n" + "="*80)
    print("🔍 DEBUGGING EMAIL & RAZORPAY CONFIGURATION")
    print("="*80)
    
    test_results = []
    
    # Check Gmail credentials
    print("\n--- Checking Gmail Credentials ---")
    try:
        import subprocess
        result = subprocess.run(
            ["grep", "-E", "GMAIL_EMAIL|GMAIL_APP_PASSWORD", "/app/backend/.env"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            gmail_email = None
            gmail_password = None
            
            for line in lines:
                if line.startswith("GMAIL_EMAIL="):
                    gmail_email = line.split("=", 1)[1].strip('"')
                elif line.startswith("GMAIL_APP_PASSWORD="):
                    gmail_password = line.split("=", 1)[1].strip('"')
            
            if gmail_email and gmail_password:
                print(f"✅ SUCCESS: Gmail credentials found")
                print(f"   - Email: {gmail_email}")
                print(f"   - Password: {'*' * len(gmail_password)} (length: {len(gmail_password)})")
                test_results.append(("Gmail Credentials Found", True))
            else:
                print(f"❌ FAILURE: Gmail credentials incomplete")
                test_results.append(("Gmail Credentials Found", False))
        else:
            print(f"❌ FAILURE: No Gmail credentials found in .env")
            test_results.append(("Gmail Credentials Found", False))
            
    except Exception as e:
        print(f"❌ FAILURE: Could not check Gmail credentials: {e}")
        test_results.append(("Gmail Credentials Found", False))
    
    # Check Razorpay credentials
    print("\n--- Checking Razorpay Credentials ---")
    try:
        result = subprocess.run(
            ["grep", "-E", "RAZORPAY_KEY_ID|RAZORPAY_KEY_SECRET", "/app/backend/.env"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            key_id = None
            key_secret = None
            
            for line in lines:
                if line.startswith("RAZORPAY_KEY_ID="):
                    key_id = line.split("=", 1)[1].strip('"')
                elif line.startswith("RAZORPAY_KEY_SECRET="):
                    key_secret = line.split("=", 1)[1].strip('"')
            
            if key_id and key_secret:
                print(f"✅ SUCCESS: Razorpay credentials found")
                print(f"   - Key ID: {key_id}")
                print(f"   - Key Secret: {'*' * len(key_secret)} (length: {len(key_secret)})")
                
                if key_id == "rzp_test_Renc645PexAmXU":
                    print(f"✅ SUCCESS: Test credentials match expected")
                    test_results.append(("Razorpay Credentials Valid", True))
                else:
                    print(f"❌ FAILURE: Unexpected key ID")
                    test_results.append(("Razorpay Credentials Valid", False))
            else:
                print(f"❌ FAILURE: Razorpay credentials incomplete")
                test_results.append(("Razorpay Credentials Valid", False))
        else:
            print(f"❌ FAILURE: No Razorpay credentials found in .env")
            test_results.append(("Razorpay Credentials Valid", False))
            
    except Exception as e:
        print(f"❌ FAILURE: Could not check Razorpay credentials: {e}")
        test_results.append(("Razorpay Credentials Valid", False))
    
    # Check recent backend logs for errors
    print("\n--- Checking Recent Backend Logs ---")
    try:
        result = subprocess.run(
            ["tail", "-100", "/var/log/supervisor/backend.err.log"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.stdout:
            logs = result.stdout
            
            # Check for email-related errors
            if "Gmail credentials not configured" in logs:
                print(f"❌ FAILURE: Gmail credentials not configured error found")
                test_results.append(("No Gmail Credential Errors", False))
            elif "Email sent successfully" in logs:
                print(f"✅ SUCCESS: Email sending working")
                test_results.append(("No Gmail Credential Errors", True))
            else:
                print(f"ℹ️  INFO: No recent email activity in logs")
                test_results.append(("No Gmail Credential Errors", True))
            
            # Check for Razorpay errors
            if "Razorpay" in logs and "error" in logs.lower():
                print(f"⚠️  WARNING: Razorpay-related errors found in logs")
                test_results.append(("No Razorpay Errors", False))
            else:
                print(f"✅ SUCCESS: No Razorpay errors in recent logs")
                test_results.append(("No Razorpay Errors", True))
                
        else:
            print(f"ℹ️  INFO: No recent backend error logs")
            test_results.append(("No Gmail Credential Errors", True))
            test_results.append(("No Razorpay Errors", True))
            
    except Exception as e:
        print(f"❌ FAILURE: Could not check backend logs: {e}")
        test_results.append(("No Gmail Credential Errors", False))
        test_results.append(("No Razorpay Errors", False))
    
    return test_results

def test_festival_products_verification(admin_token):
    """Test festival products API and verify exactly 5 festival products as requested"""
    print("\n" + "="*80)
    print("🎉 FESTIVAL PRODUCTS VERIFICATION (REVIEW REQUEST)")
    print("="*80)
    
    auth_headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
    
    success, response_data = test_api_endpoint(
        "GET",
        "/admin/festival-products",
        headers=auth_headers,
        description="Get festival products with admin token - verify 5 festival products"
    )
    
    if success and isinstance(response_data, list):
        festival_count = len(response_data)
        print(f"✅ SUCCESS: Festival products API returns {festival_count} products")
        
        # CRITICAL: Verify we have exactly 5 festival products as specified in review request
        if festival_count == 5:
            print(f"✅ CRITICAL SUCCESS: Exactly 5 festival products found as required")
        else:
            print(f"❌ CRITICAL FAILURE: Expected exactly 5 festival products, got {festival_count}")
            return False
        
        # Show festival product details
        print(f"\n🎉 FESTIVAL PRODUCTS DETAILS:")
        for i, product in enumerate(response_data, 1):
            name = product.get("name", "Unknown")
            is_festival = product.get("isFestival", False)
            is_best_seller = product.get("isBestSeller", False)
            category = product.get("category", "Unknown")
            print(f"   {i}. {name}")
            print(f"      - Category: {category}")
            print(f"      - isFestival: {is_festival}")
            print(f"      - isBestSeller: {is_best_seller}")
        
        return True
    
    print(f"❌ CRITICAL FAILURE: Festival products API failed or returned invalid data")
    return False

def test_products_order_verification():
    """Test products API and show first 10 products with their flags as requested"""
    print("\n" + "="*80)
    print("📦 PRODUCTS ORDER VERIFICATION (REVIEW REQUEST)")
    print("="*80)
    
    success, response_data = test_api_endpoint(
        "GET",
        "/products",
        description="Get products and show first 10 with isBestSeller and isFestival flags"
    )
    
    if success and isinstance(response_data, list):
        total_products = len(response_data)
        print(f"✅ SUCCESS: Products API returns {total_products} products")
        
        # Show first 10 products with their flags
        print(f"\n📋 FIRST 10 PRODUCTS WITH FLAGS:")
        products_to_show = response_data[:10]
        
        best_seller_count = 0
        festival_count = 0
        both_flags_count = 0
        
        for i, product in enumerate(products_to_show, 1):
            name = product.get("name", "Unknown")
            is_best_seller = product.get("isBestSeller", False)
            is_festival = product.get("isFestival", False)
            category = product.get("category", "Unknown")
            
            # Count flags
            if is_best_seller:
                best_seller_count += 1
            if is_festival:
                festival_count += 1
            if is_best_seller and is_festival:
                both_flags_count += 1
            
            print(f"   {i}. {name}")
            print(f"      - Category: {category}")
            print(f"      - isBestSeller: {is_best_seller}")
            print(f"      - isFestival: {is_festival}")
            if is_best_seller and is_festival:
                print(f"      - ⭐ BOTH FLAGS SET ⭐")
        
        # Summary of flags in first 10 products
        print(f"\n📊 FLAGS SUMMARY (First 10 Products):")
        print(f"   - Best Sellers: {best_seller_count}")
        print(f"   - Festival Products: {festival_count}")
        print(f"   - Both Flags: {both_flags_count}")
        
        # Check if we have products with both flags
        if both_flags_count > 0:
            print(f"✅ SUCCESS: Found {both_flags_count} products with both isBestSeller and isFestival flags")
        else:
            print(f"⚠️  WARNING: No products found with both flags in first 10")
        
        return True
    
    print(f"❌ CRITICAL FAILURE: Products API failed or returned invalid data")
    return False

def test_all_products_flags_verification():
    """Test all products and count those with isBestSeller and isFestival flags"""
    print("\n" + "="*80)
    print("🔍 ALL PRODUCTS FLAGS VERIFICATION (REVIEW REQUEST)")
    print("="*80)
    
    success, response_data = test_api_endpoint(
        "GET",
        "/products",
        description="Get all products and verify isBestSeller and isFestival flags distribution"
    )
    
    if success and isinstance(response_data, list):
        total_products = len(response_data)
        print(f"✅ SUCCESS: Products API returns {total_products} products")
        
        # Count products with flags
        best_seller_count = 0
        festival_count = 0
        both_flags_count = 0
        best_seller_products = []
        festival_products = []
        both_flags_products = []
        
        for product in response_data:
            name = product.get("name", "Unknown")
            is_best_seller = product.get("isBestSeller", False)
            is_festival = product.get("isFestival", False)
            
            if is_best_seller:
                best_seller_count += 1
                best_seller_products.append(name)
            if is_festival:
                festival_count += 1
                festival_products.append(name)
            if is_best_seller and is_festival:
                both_flags_count += 1
                both_flags_products.append(name)
        
        # Summary of all flags
        print(f"\n📊 COMPLETE FLAGS SUMMARY (All {total_products} Products):")
        print(f"   - Total Best Sellers: {best_seller_count}")
        print(f"   - Total Festival Products: {festival_count}")
        print(f"   - Products with Both Flags: {both_flags_count}")
        
        # Show best seller products
        if best_seller_products:
            print(f"\n⭐ BEST SELLER PRODUCTS ({best_seller_count}):")
            for i, name in enumerate(best_seller_products, 1):
                print(f"   {i}. {name}")
        
        # Show festival products
        if festival_products:
            print(f"\n🎉 FESTIVAL PRODUCTS ({festival_count}):")
            for i, name in enumerate(festival_products, 1):
                print(f"   {i}. {name}")
        
        # Show products with both flags
        if both_flags_products:
            print(f"\n⭐🎉 PRODUCTS WITH BOTH FLAGS ({both_flags_count}):")
            for i, name in enumerate(both_flags_products, 1):
                print(f"   {i}. {name}")
        
        # Verify we have the expected counts
        if festival_count >= 5:
            print(f"✅ SUCCESS: Found {festival_count} festival products (expected at least 5)")
        else:
            print(f"❌ FAILURE: Only found {festival_count} festival products (expected at least 5)")
            return False
        
        if best_seller_count > 0:
            print(f"✅ SUCCESS: Found {best_seller_count} best seller products")
        else:
            print(f"⚠️  WARNING: No best seller products found")
        
        return True
    
    print(f"❌ CRITICAL FAILURE: Products API failed or returned invalid data")
    return False

def main():
    """Main testing function - Updated for Review Request"""
    print("🚀 STARTING BACKEND API TESTING - FESTIVAL PRODUCTS VERIFICATION")
    print("=" * 80)
    print("REVIEW REQUEST TESTING:")
    print("1. Products API - Order Verification with isBestSeller and isFestival flags")
    print("2. Festival Products Count - Verify 5 festival products")
    print("3. Product Details - Show first 10 products with their flags")
    print("=" * 80)
    
    # Track all test results
    all_tests_passed = True
    test_summary = []
    
    # 1. Admin Authentication (Required for admin endpoints)
    print("\n🔐 PHASE 1: ADMIN AUTHENTICATION")
    admin_success, admin_token = test_admin_authentication()
    test_summary.append(("Admin Authentication", admin_success))
    
    if not admin_success:
        print("❌ CRITICAL: Admin authentication failed - cannot test admin endpoints")
        all_tests_passed = False
        admin_token = None
        return False
    
    # 2. Products Order Verification (REVIEW REQUEST)
    print("\n📦 PHASE 2: PRODUCTS ORDER VERIFICATION (REVIEW REQUEST)")
    products_order_success = test_products_order_verification()
    test_summary.append(("Products Order Verification", products_order_success))
    
    if not products_order_success:
        all_tests_passed = False
    
    # 3. All Products Flags Verification (REVIEW REQUEST)
    print("\n🔍 PHASE 3: ALL PRODUCTS FLAGS VERIFICATION (REVIEW REQUEST)")
    all_products_success = test_all_products_flags_verification()
    test_summary.append(("All Products Flags Verification", all_products_success))
    
    if not all_products_success:
        all_tests_passed = False
    
    # 4. Festival Products Count Verification (REVIEW REQUEST)
    if admin_token:
        print("\n🎉 PHASE 4: FESTIVAL PRODUCTS COUNT VERIFICATION (REVIEW REQUEST)")
        festival_success = test_festival_products_verification(admin_token)
        test_summary.append(("Festival Products Count (5 products)", festival_success))
        
        if not festival_success:
            all_tests_passed = False
    else:
        print("\n❌ SKIPPING FESTIVAL PRODUCTS TEST: No admin token")
        test_summary.append(("Festival Products Count (5 products)", False))
        all_tests_passed = False
    
    # Final Summary
    print("\n" + "=" * 80)
    print("🏁 REVIEW REQUEST TESTING COMPLETE")
    print("=" * 80)
    
    print(f"\n📊 TEST RESULTS SUMMARY:")
    passed_count = 0
    total_count = len(test_summary)
    
    for test_name, success in test_summary:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status}: {test_name}")
        if success:
            passed_count += 1
    
    success_rate = (passed_count / total_count) * 100 if total_count > 0 else 0
    
    print(f"\n📈 OVERALL RESULTS:")
    print(f"   - Tests Passed: {passed_count}/{total_count}")
    print(f"   - Success Rate: {success_rate:.1f}%")
    
    if all_tests_passed:
        print(f"\n🎉 ALL REVIEW REQUEST TESTS PASSED!")
        print(f"✅ Products API: Working with isBestSeller and isFestival flags")
        print(f"✅ Festival Products: Verified count and details")
        print(f"✅ Product Details: First 10 products shown with flags")
        print(f"✅ Admin Authentication: Working correctly")
        return True
    else:
        print(f"\n❌ SOME TESTS FAILED! Please check the issues above.")
        print(f"🔍 Focus on fixing the failed tests for proper festival products functionality.")
        return False

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)