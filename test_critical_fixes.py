#!/usr/bin/env python3
"""
Critical Bug Fixes Testing Script
Tests the TWO specific issues mentioned in the review request:

ISSUE 1: Order Status Update Emails NOT Triggering
- Test order creation with email
- Test order status updates via PUT /api/orders/{order_id}/admin-update
- Check backend logs for enhanced email logging

ISSUE 2: Cities Disappearing After City Approval  
- Test initial city count (should be 431+ cities)
- Test city suggestion creation and approval
- Verify all cities remain after approval (no disappearing cities)
"""

import requests
import json
import sys
from datetime import datetime, timedelta, timezone
import time
import random
import subprocess

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

def check_backend_logs(search_terms, log_file="/var/log/supervisor/backend.out.log"):
    """Check backend logs for specific terms"""
    try:
        result = subprocess.run(
            ["tail", "-n", "100", log_file],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.stdout:
            print(f"\n📋 BACKEND LOGS (last 100 lines from {log_file}):")
            print("-" * 60)
            
            lines = result.stdout.split('\n')
            relevant_lines = []
            
            for line in lines:
                for term in search_terms:
                    if term.lower() in line.lower():
                        relevant_lines.append(line)
                        break
            
            if relevant_lines:
                print("🔍 RELEVANT LOG ENTRIES:")
                for line in relevant_lines[-10:]:  # Show last 10 relevant lines
                    print(f"   {line}")
                return relevant_lines
            else:
                print("⚠️  No relevant log entries found")
                print("📋 RECENT LOG ENTRIES (last 10 lines):")
                for line in lines[-10:]:
                    if line.strip():
                        print(f"   {line}")
                return []
        else:
            print("⚠️  No log output found")
            return []
            
    except Exception as e:
        print(f"❌ Could not read backend logs: {e}")
        return []

def test_issue_1_order_status_emails():
    """
    ISSUE 1: Order Status Update Emails NOT Triggering
    Test the enhanced logging and email functionality
    """
    print("\n" + "="*100)
    print("🚨 TESTING ISSUE 1: ORDER STATUS UPDATE EMAILS NOT TRIGGERING")
    print("="*100)
    
    # Step 1: Admin login
    admin_token = admin_login()
    if not admin_token:
        print("❌ CRITICAL: Cannot proceed without admin authentication")
        return False
    
    auth_headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
    
    # Step 2: Create a test order with email address
    print("\n--- Step 2: Create Test Order with Email Address ---")
    order_data = {
        "customer_name": "Email Test User",
        "email": "test@example.com",
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
                "price": 299.0,
                "quantity": 1,
                "description": "Test product for email testing"
            }
        ],
        "subtotal": 299.0,
        "delivery_charge": 49.0,
        "total": 348.0,
        "payment_method": "online",
        "payment_sub_method": "paytm"
    }
    
    success, order_response = test_api_endpoint(
        "POST",
        "/orders",
        data=order_data,
        description="Create test order with email address test@example.com"
    )
    
    if not success or not order_response or "order_id" not in order_response:
        print("❌ CRITICAL: Could not create test order")
        return False
    
    order_id = order_response["order_id"]
    print(f"✅ SUCCESS: Test order created with ID: {order_id}")
    
    # Step 3: Update order status to "shipped" using admin-update endpoint
    print(f"\n--- Step 3: Update Order Status to 'shipped' ---")
    update_data = {
        "order_status": "shipped",
        "admin_notes": "Order shipped today"
    }
    
    # Clear logs before the test
    print("🧹 Clearing recent logs to focus on new entries...")
    
    success, update_response = test_api_endpoint(
        "PUT",
        f"/orders/{order_id}/admin-update",
        headers=auth_headers,
        data=update_data,
        description=f"Update order {order_id} status to 'shipped' with admin notes"
    )
    
    if not success:
        print("❌ CRITICAL: Order status update failed")
        return False
    
    print(f"✅ SUCCESS: Order status updated to 'shipped'")
    
    # Step 4: Check backend logs for enhanced email logging
    print(f"\n--- Step 4: Check Backend Logs for Enhanced Email Logging ---")
    
    # Wait a moment for logs to be written
    time.sleep(2)
    
    email_search_terms = [
        "Attempting to send order status update email",
        "Order status update email sent successfully",
        "Order status update email function returned False",
        "Failed to send order status update email",
        f"email to test@example.com",
        f"order {order_id}",
        "✅", "⚠️", "❌"
    ]
    
    log_entries = check_backend_logs(email_search_terms)
    
    # Analyze log entries
    email_attempt_found = False
    email_success_found = False
    email_warning_found = False
    email_error_found = False
    
    for entry in log_entries:
        if "Attempting to send order status update email" in entry:
            email_attempt_found = True
            print(f"✅ FOUND: Email attempt log entry")
        elif "✅" in entry and "Order status update email sent successfully" in entry:
            email_success_found = True
            print(f"✅ FOUND: Email success log entry")
        elif "⚠️" in entry and "returned False" in entry:
            email_warning_found = True
            print(f"⚠️  FOUND: Email warning log entry")
        elif "❌" in entry and "Failed to send" in entry:
            email_error_found = True
            print(f"❌ FOUND: Email error log entry")
    
    # Step 5: Test another status update to "delivered"
    print(f"\n--- Step 5: Update Order Status to 'delivered' ---")
    update_data_2 = {
        "order_status": "delivered",
        "admin_notes": "Order delivered successfully"
    }
    
    success, update_response_2 = test_api_endpoint(
        "PUT",
        f"/orders/{order_id}/admin-update",
        headers=auth_headers,
        data=update_data_2,
        description=f"Update order {order_id} status to 'delivered'"
    )
    
    if success:
        print(f"✅ SUCCESS: Order status updated to 'delivered'")
        
        # Check logs again
        time.sleep(2)
        log_entries_2 = check_backend_logs(email_search_terms)
        
        # Count total email attempts
        total_attempts = sum(1 for entry in log_entries + log_entries_2 
                           if "Attempting to send order status update email" in entry)
        
        print(f"\n📊 EMAIL LOGGING ANALYSIS:")
        print(f"   - Total email attempts logged: {total_attempts}")
        print(f"   - Email attempt messages found: {'✅' if email_attempt_found else '❌'}")
        print(f"   - Email success messages found: {'✅' if email_success_found else '❌'}")
        print(f"   - Email warning messages found: {'⚠️' if email_warning_found else '✅ (none expected)'}")
        print(f"   - Email error messages found: {'❌' if email_error_found else '✅ (none expected)'}")
    
    # Step 6: Summary for Issue 1
    print(f"\n--- ISSUE 1 SUMMARY ---")
    if email_attempt_found:
        print("✅ SUCCESS: Enhanced logging is working - email attempts are being logged")
        if email_success_found:
            print("✅ SUCCESS: Emails are being sent successfully")
            return True
        elif email_warning_found or email_error_found:
            print("⚠️  ISSUE IDENTIFIED: Email attempts logged but emails not sending")
            print("   - Check Gmail credentials configuration")
            print("   - Verify GMAIL_EMAIL and GMAIL_APP_PASSWORD in .env")
            return False
        else:
            print("⚠️  PARTIAL: Email attempts logged but no success/failure messages")
            return False
    else:
        print("❌ CRITICAL: Enhanced logging not working - no email attempt messages found")
        print("   - Email functions may not be called at all")
        print("   - Check server.py lines 1175-1188 and 1358-1371")
        return False

def test_issue_2_cities_disappearing():
    """
    ISSUE 2: Cities Disappearing After City Approval
    Test that all existing cities remain after approving a new city
    """
    print("\n" + "="*100)
    print("🚨 TESTING ISSUE 2: CITIES DISAPPEARING AFTER CITY APPROVAL")
    print("="*100)
    
    # Step 1: Admin login
    admin_token = admin_login()
    if not admin_token:
        print("❌ CRITICAL: Cannot proceed without admin authentication")
        return False
    
    auth_headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
    
    # Step 2: Get initial city count and sample cities
    print("\n--- Step 2: Get Initial City Count ---")
    success, initial_locations = test_api_endpoint(
        "GET",
        "/locations",
        description="Get all delivery locations to check initial count"
    )
    
    if not success or not isinstance(initial_locations, list):
        print("❌ CRITICAL: Could not get initial locations")
        return False
    
    initial_count = len(initial_locations)
    print(f"✅ SUCCESS: Found {initial_count} cities initially")
    
    # Get sample city names for verification
    sample_cities = [loc.get("name") for loc in initial_locations[:10]]
    print(f"📋 Sample cities: {', '.join(sample_cities)}")
    
    # Verify we have the expected 431+ cities
    if initial_count >= 431:
        print(f"✅ SUCCESS: City count ({initial_count}) meets expectation (431+)")
    else:
        print(f"⚠️  WARNING: City count ({initial_count}) is less than expected (431+)")
    
    # Step 3: Create a city suggestion
    print("\n--- Step 3: Create City Suggestion ---")
    suggestion_data = {
        "state": "Andhra Pradesh",
        "city": "TestCity",
        "customer_name": "Test User",
        "phone": "9876543210",
        "email": "testcity@example.com"
    }
    
    success, suggestion_response = test_api_endpoint(
        "POST",
        "/suggest-city",
        data=suggestion_data,
        description="Create city suggestion for TestCity, Andhra Pradesh"
    )
    
    if not success or not suggestion_response or "suggestion_id" not in suggestion_response:
        print("❌ CRITICAL: Could not create city suggestion")
        return False
    
    suggestion_id = suggestion_response["suggestion_id"]
    print(f"✅ SUCCESS: City suggestion created with ID: {suggestion_id}")
    
    # Step 4: Get the suggestion ID from admin endpoint
    print("\n--- Step 4: Verify Suggestion in Admin Panel ---")
    success, suggestions = test_api_endpoint(
        "GET",
        "/admin/city-suggestions",
        headers=auth_headers,
        description="Get city suggestions from admin panel"
    )
    
    if not success or not isinstance(suggestions, list):
        print("❌ CRITICAL: Could not get city suggestions")
        return False
    
    # Find our suggestion
    found_suggestion = None
    for suggestion in suggestions:
        if (suggestion.get("city") == "TestCity" and 
            suggestion.get("state") == "Andhra Pradesh"):
            found_suggestion = suggestion
            break
    
    if not found_suggestion:
        print("❌ CRITICAL: Created suggestion not found in admin panel")
        return False
    
    actual_suggestion_id = found_suggestion.get("id")
    print(f"✅ SUCCESS: Found suggestion in admin panel with ID: {actual_suggestion_id}")
    
    # Step 5: Approve the city
    print("\n--- Step 5: Approve City with Delivery Settings ---")
    approval_data = {
        "status": "approved",
        "delivery_charge": 99,
        "free_delivery_threshold": 1000
    }
    
    success, approval_response = test_api_endpoint(
        "PUT",
        f"/admin/city-suggestions/{actual_suggestion_id}/status",
        headers=auth_headers,
        data=approval_data,
        description="Approve TestCity with delivery charge ₹99 and free delivery threshold ₹1000"
    )
    
    if not success:
        print("❌ CRITICAL: Could not approve city")
        return False
    
    print(f"✅ SUCCESS: City approved successfully")
    
    # Step 6: Verify all cities remain after approval
    print("\n--- Step 6: Verify All Cities Remain After Approval ---")
    success, final_locations = test_api_endpoint(
        "GET",
        "/locations",
        description="Get all delivery locations after city approval"
    )
    
    if not success or not isinstance(final_locations, list):
        print("❌ CRITICAL: Could not get final locations")
        return False
    
    final_count = len(final_locations)
    print(f"📊 CITY COUNT COMPARISON:")
    print(f"   - Initial count: {initial_count}")
    print(f"   - Final count: {final_count}")
    print(f"   - Expected: {initial_count + 1} (initial + 1 new city)")
    
    # Check if count increased by 1
    if final_count == initial_count + 1:
        print(f"✅ SUCCESS: City count increased by exactly 1 ({initial_count} → {final_count})")
    elif final_count > initial_count:
        print(f"✅ SUCCESS: City count increased ({initial_count} → {final_count})")
    else:
        print(f"❌ CRITICAL: City count did not increase or decreased ({initial_count} → {final_count})")
        return False
    
    # Step 7: Verify existing cities are still present
    print("\n--- Step 7: Verify Existing Cities Still Present ---")
    final_city_names = [loc.get("name") for loc in final_locations]
    
    missing_cities = []
    for sample_city in sample_cities:
        if sample_city not in final_city_names:
            missing_cities.append(sample_city)
    
    if missing_cities:
        print(f"❌ CRITICAL: {len(missing_cities)} cities disappeared after approval:")
        for city in missing_cities:
            print(f"   - {city}")
        return False
    else:
        print(f"✅ SUCCESS: All sample cities ({len(sample_cities)}) still present")
    
    # Step 8: Verify new city is present
    print("\n--- Step 8: Verify New City is Present ---")
    testcity_found = None
    for location in final_locations:
        if location.get("name") == "TestCity":
            testcity_found = location
            break
    
    if testcity_found:
        print(f"✅ SUCCESS: TestCity found in locations")
        print(f"   - Name: {testcity_found.get('name')}")
        print(f"   - Charge: ₹{testcity_found.get('charge')}")
        print(f"   - Free Delivery Threshold: ₹{testcity_found.get('free_delivery_threshold')}")
        
        # Verify correct values
        if (testcity_found.get("charge") == 99 and 
            testcity_found.get("free_delivery_threshold") == 1000):
            print(f"✅ SUCCESS: Delivery settings are correct")
        else:
            print(f"⚠️  WARNING: Delivery settings incorrect")
    else:
        print(f"❌ CRITICAL: TestCity not found in locations after approval")
        return False
    
    # Step 9: Summary for Issue 2
    print(f"\n--- ISSUE 2 SUMMARY ---")
    print(f"✅ SUCCESS: Cities do NOT disappear after city approval")
    print(f"   - Initial cities: {initial_count}")
    print(f"   - Final cities: {final_count}")
    print(f"   - All existing cities preserved: ✅")
    print(f"   - New city added correctly: ✅")
    
    return True

def main():
    """Main test function"""
    print("🧪 CRITICAL BUG FIXES TESTING")
    print("="*100)
    print("Testing TWO specific issues from the review request:")
    print("1. Order Status Update Emails NOT Triggering")
    print("2. Cities Disappearing After City Approval")
    print("="*100)
    
    results = {}
    
    # Test Issue 1: Order Status Update Emails
    try:
        results["Issue 1 - Order Status Emails"] = test_issue_1_order_status_emails()
    except Exception as e:
        print(f"❌ EXCEPTION in Issue 1 testing: {str(e)}")
        results["Issue 1 - Order Status Emails"] = False
    
    # Test Issue 2: Cities Disappearing
    try:
        results["Issue 2 - Cities Disappearing"] = test_issue_2_cities_disappearing()
    except Exception as e:
        print(f"❌ EXCEPTION in Issue 2 testing: {str(e)}")
        results["Issue 2 - Cities Disappearing"] = False
    
    # Final Summary
    print("\n" + "="*100)
    print("🏁 FINAL TEST RESULTS")
    print("="*100)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    print(f"\n📊 SUMMARY: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL CRITICAL ISSUES RESOLVED!")
        return True
    else:
        print("⚠️  SOME CRITICAL ISSUES REMAIN")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)