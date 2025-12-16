#!/usr/bin/env python3
"""
Payment and Order Status Email Testing Script
Tests the city-specific payment options and email functionality as requested in review:

TEST SCENARIOS:
1. Order Creation for Regular City (Not Guntur) - Hyderabad/Vijayawada
2. Order Creation for Custom City (Not in Database) - Bangalore
3. Complete Payment for Pending Order
4. Order Status Update Emails
5. Email Service Verification
"""

import requests
import json
import sys
from datetime import datetime, timedelta, timezone
import time
import random
import subprocess

# Backend URL from environment
BACKEND_URL = "https://easy-whatsapp-send.preview.emergentagent.com/api"
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

def check_backend_logs(search_term="", lines=50):
    """Check backend logs for specific terms"""
    try:
        result = subprocess.run(
            ["tail", "-n", str(lines), "/var/log/supervisor/backend.out.log"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.stdout:
            if search_term:
                if search_term in result.stdout:
                    print(f"✅ Found '{search_term}' in backend logs")
                    return True
                else:
                    print(f"❌ '{search_term}' not found in backend logs")
                    return False
            else:
                print("Backend Logs:")
                print(result.stdout)
                return True
        else:
            print("No backend logs found")
            return False
            
    except Exception as e:
        print(f"Could not read backend logs: {e}")
        return False

def test_scenario_1_regular_city_order():
    """Test Scenario 1: Order Creation for Regular City (Not Guntur)"""
    print("\n" + "="*100)
    print("🏙️ TEST SCENARIO 1: ORDER CREATION FOR REGULAR CITY (HYDERABAD)")
    print("="*100)
    
    # Create order for Hyderabad with complete data
    order_data = {
        "customer_name": "Rajesh Kumar",
        "email": "rajesh.kumar@example.com",
        "phone": "9876543210",
        "city": "Hyderabad",
        "state": "Telangana",
        "doorNo": "12-34",
        "building": "Sunrise Apartments",
        "street": "Banjara Hills Road",
        "pincode": "500034",
        "payment_method": "online",
        "payment_sub_method": "Paytm",
        "items": [
            {
                "product_id": "product_1762765616",  # Using existing product ID
                "name": "Immunity Dry Fruits Laddu",
                "image": "https://images.pexels.com/photos/4198019/pexels-photo-4198019.jpeg",
                "weight": "1 kg",
                "price": 550.0,
                "quantity": 1,
                "description": "Nutritious laddu packed with dry fruits and immunity-boosting ingredients"
            }
        ],
        "subtotal": 550.0,
        "delivery_charge": 149.0,  # Hyderabad charge
        "total": 699.0
    }
    
    success, response = test_api_endpoint(
        "POST",
        "/orders",
        data=order_data,
        description="Create order for Hyderabad with Paytm payment"
    )
    
    if success and response:
        order_id = response.get("order_id")
        tracking_code = response.get("tracking_code")
        
        print(f"✅ SUCCESS: Order created successfully")
        print(f"   - Order ID: {order_id}")
        print(f"   - Tracking Code: {tracking_code}")
        print(f"   - Payment Status: {response.get('payment_status', 'N/A')}")
        print(f"   - Order Status: Expected 'confirmed'")
        
        # Verify payment_status is "completed" and order_status is "confirmed"
        if response.get("payment_status") == "completed":
            print(f"✅ VERIFIED: Payment status is 'completed' for regular city")
        else:
            print(f"❌ FAILED: Payment status is '{response.get('payment_status')}', expected 'completed'")
            return False, None
        
        # Check backend logs for email confirmation
        print(f"\n📧 Checking backend logs for order confirmation email...")
        if check_backend_logs("Email sent successfully", 100):
            print(f"✅ SUCCESS: Order confirmation email sent successfully")
        else:
            print(f"❌ WARNING: Order confirmation email log not found")
        
        return True, order_id
    else:
        print(f"❌ FAILED: Could not create order for regular city")
        return False, None

def test_scenario_2_custom_city_order():
    """Test Scenario 2: Order Creation for Custom City (Not in Database)"""
    print("\n" + "="*100)
    print("🌆 TEST SCENARIO 2: ORDER CREATION FOR CUSTOM CITY (BANGALORE)")
    print("="*100)
    
    # Create order for Bangalore (not in AP/Telangana database)
    order_data = {
        "customer_name": "Priya Sharma",
        "email": "priya.sharma@example.com", 
        "phone": "9876543211",
        "city": "Bangalore",
        "state": "Karnataka",
        "doorNo": "45-67",
        "building": "Tech Park Plaza",
        "street": "Whitefield Main Road",
        "pincode": "560066",
        "payment_method": "online",
        "payment_sub_method": "PhonePe",
        "items": [
            {
                "product_id": "product_1762765616",  # Using existing product ID
                "name": "Immunity Dry Fruits Laddu",
                "image": "https://images.pexels.com/photos/4198019/pexels-photo-4198019.jpeg",
                "weight": "½ kg",
                "price": 280.0,
                "quantity": 2,
                "description": "Nutritious laddu packed with dry fruits and immunity-boosting ingredients"
            }
        ],
        "subtotal": 560.0,
        "delivery_charge": 0.0,  # Should be 0 for custom city initially
        "total": 560.0
    }
    
    success, response = test_api_endpoint(
        "POST",
        "/orders",
        data=order_data,
        description="Create order for Bangalore (custom city not in database)"
    )
    
    if success and response:
        order_id = response.get("order_id")
        tracking_code = response.get("tracking_code")
        
        print(f"✅ SUCCESS: Order created successfully")
        print(f"   - Order ID: {order_id}")
        print(f"   - Tracking Code: {tracking_code}")
        print(f"   - Payment Status: {response.get('payment_status', 'N/A')}")
        print(f"   - Order Status: Expected 'pending'")
        
        # Verify payment_status is "pending" and order_status is "pending"
        if response.get("payment_status") == "pending":
            print(f"✅ VERIFIED: Payment status is 'pending' for custom city")
        else:
            print(f"❌ FAILED: Payment status is '{response.get('payment_status')}', expected 'pending'")
            return False, None
        
        # Check if custom_city_request flag is set
        if response.get("custom_city_request") == True:
            print(f"✅ VERIFIED: Custom city request flag is set")
        else:
            print(f"❌ FAILED: Custom city request flag not set")
        
        # Check backend logs for order confirmation email (should still be sent)
        print(f"\n📧 Checking backend logs for order confirmation email...")
        if check_backend_logs("Email sent successfully", 100):
            print(f"✅ SUCCESS: Order confirmation email sent successfully")
        else:
            print(f"❌ WARNING: Order confirmation email log not found")
        
        return True, order_id
    else:
        print(f"❌ FAILED: Could not create order for custom city")
        return False, None

def test_scenario_3_complete_payment(order_id):
    """Test Scenario 3: Complete Payment for Pending Order"""
    print("\n" + "="*100)
    print("💳 TEST SCENARIO 3: COMPLETE PAYMENT FOR PENDING ORDER")
    print("="*100)
    
    if not order_id:
        print("❌ FAILED: No order ID provided for payment completion")
        return False
    
    # Complete payment for the pending order
    payment_data = {
        "payment_method": "online",
        "payment_sub_method": "PhonePe"
    }
    
    success, response = test_api_endpoint(
        "POST",
        f"/orders/{order_id}/complete-payment",
        data=payment_data,
        description=f"Complete payment for order {order_id} with PhonePe"
    )
    
    if success and response:
        print(f"✅ SUCCESS: Payment completed successfully")
        print(f"   - Order Status: {response.get('order_status', 'N/A')}")
        print(f"   - Tracking Code: {response.get('tracking_code', 'N/A')}")
        
        # Verify payment_status changes to "completed" and order_status to "confirmed"
        if response.get("order_status") == "confirmed":
            print(f"✅ VERIFIED: Order status changed to 'confirmed' after payment")
        else:
            print(f"❌ FAILED: Order status is '{response.get('order_status')}', expected 'confirmed'")
            return False
        
        # Check backend logs for payment completion email
        print(f"\n📧 Checking backend logs for payment completion email...")
        if check_backend_logs("payment completion email", 100):
            print(f"✅ SUCCESS: Payment completion email sent successfully")
        else:
            print(f"⚠️  WARNING: Payment completion email log not found")
        
        return True
    else:
        print(f"❌ FAILED: Could not complete payment for order")
        return False

def test_scenario_4_order_status_updates(admin_token, order_id):
    """Test Scenario 4: Order Status Update Emails"""
    print("\n" + "="*100)
    print("📦 TEST SCENARIO 4: ORDER STATUS UPDATE EMAILS")
    print("="*100)
    
    if not admin_token or not order_id:
        print("❌ FAILED: Missing admin token or order ID for status updates")
        return False
    
    auth_headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
    
    # Test 1: Update order status to "shipped"
    print(f"\n--- Test 4.1: Update Order Status to 'shipped' ---")
    
    update_data = {
        "order_status": "shipped",
        "admin_notes": "Order has been shipped via courier"
    }
    
    success, response = test_api_endpoint(
        "PUT",
        f"/orders/{order_id}/admin-update",
        headers=auth_headers,
        data=update_data,
        description=f"Update order {order_id} status to 'shipped'"
    )
    
    if success:
        print(f"✅ SUCCESS: Order status updated to 'shipped'")
        
        # Check backend logs for status update email
        print(f"\n📧 Checking backend logs for 'shipped' status email...")
        if check_backend_logs("Order status update email sent successfully", 100):
            print(f"✅ SUCCESS: Order status update email sent successfully for 'shipped'")
        else:
            print(f"❌ FAILED: Order status update email not found for 'shipped'")
            return False
    else:
        print(f"❌ FAILED: Could not update order status to 'shipped'")
        return False
    
    # Wait a moment before next update
    time.sleep(2)
    
    # Test 2: Update order status to "delivered"
    print(f"\n--- Test 4.2: Update Order Status to 'delivered' ---")
    
    update_data = {
        "order_status": "delivered",
        "admin_notes": "Order has been delivered successfully"
    }
    
    success, response = test_api_endpoint(
        "PUT",
        f"/orders/{order_id}/admin-update",
        headers=auth_headers,
        data=update_data,
        description=f"Update order {order_id} status to 'delivered'"
    )
    
    if success:
        print(f"✅ SUCCESS: Order status updated to 'delivered'")
        
        # Check backend logs for status update email
        print(f"\n📧 Checking backend logs for 'delivered' status email...")
        if check_backend_logs("Order status update email sent successfully", 100):
            print(f"✅ SUCCESS: Order status update email sent successfully for 'delivered'")
        else:
            print(f"❌ FAILED: Order status update email not found for 'delivered'")
            return False
    else:
        print(f"❌ FAILED: Could not update order status to 'delivered'")
        return False
    
    return True

def test_scenario_5_email_service_verification():
    """Test Scenario 5: Email Service Verification"""
    print("\n" + "="*100)
    print("📧 TEST SCENARIO 5: EMAIL SERVICE VERIFICATION")
    print("="*100)
    
    # Check backend logs for Gmail credentials loading
    print(f"\n--- Test 5.1: Gmail Credentials Verification ---")
    
    # Check for Gmail credentials in backend logs
    print(f"Checking backend logs for Gmail credentials...")
    
    try:
        result = subprocess.run(
            ["tail", "-n", "200", "/var/log/supervisor/backend.out.log"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.stdout:
            # Check for Gmail credentials loaded properly
            if "Gmail credentials not configured" in result.stdout:
                print(f"❌ FAILED: Gmail credentials not configured warning found")
                return False
            else:
                print(f"✅ SUCCESS: No 'Gmail credentials not configured' warnings found")
            
            # Check for successful email sends
            email_success_count = result.stdout.count("Email sent successfully")
            gmail_success_count = result.stdout.count("via Gmail")
            
            print(f"📊 Email Statistics from logs:")
            print(f"   - 'Email sent successfully' occurrences: {email_success_count}")
            print(f"   - 'via Gmail' occurrences: {gmail_success_count}")
            
            if email_success_count > 0:
                print(f"✅ SUCCESS: Found {email_success_count} successful email sends")
            else:
                print(f"⚠️  WARNING: No successful email sends found in recent logs")
            
            if gmail_success_count > 0:
                print(f"✅ SUCCESS: Found {gmail_success_count} Gmail SMTP sends")
            else:
                print(f"⚠️  WARNING: No Gmail SMTP sends found in recent logs")
            
            return True
        else:
            print(f"❌ FAILED: No backend logs found")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: Could not check backend logs: {e}")
        return False

def main():
    """Main test execution"""
    print("="*120)
    print("🧪 PAYMENT AND ORDER STATUS EMAIL FUNCTIONALITY TESTING")
    print("="*120)
    print("Testing city-specific payment options and email notifications")
    print("="*120)
    
    test_results = []
    
    # Get admin token first
    admin_token = admin_login()
    if not admin_token:
        print("❌ CRITICAL: Cannot proceed without admin authentication")
        return False
    
    # Test Scenario 1: Regular City Order (Hyderabad)
    print(f"\n🏙️ Starting Test Scenario 1...")
    success_1, regular_order_id = test_scenario_1_regular_city_order()
    test_results.append(("Scenario 1: Regular City Order", success_1))
    
    # Test Scenario 2: Custom City Order (Bangalore)
    print(f"\n🌆 Starting Test Scenario 2...")
    success_2, custom_order_id = test_scenario_2_custom_city_order()
    test_results.append(("Scenario 2: Custom City Order", success_2))
    
    # Test Scenario 3: Complete Payment (using custom city order)
    if success_2 and custom_order_id:
        print(f"\n💳 Starting Test Scenario 3...")
        success_3 = test_scenario_3_complete_payment(custom_order_id)
        test_results.append(("Scenario 3: Complete Payment", success_3))
    else:
        print(f"\n💳 Skipping Test Scenario 3 - No pending order available")
        test_results.append(("Scenario 3: Complete Payment", False))
        success_3 = False
    
    # Test Scenario 4: Order Status Updates (using regular city order)
    if success_1 and regular_order_id:
        print(f"\n📦 Starting Test Scenario 4...")
        success_4 = test_scenario_4_order_status_updates(admin_token, regular_order_id)
        test_results.append(("Scenario 4: Order Status Updates", success_4))
    else:
        print(f"\n📦 Skipping Test Scenario 4 - No confirmed order available")
        test_results.append(("Scenario 4: Order Status Updates", False))
        success_4 = False
    
    # Test Scenario 5: Email Service Verification
    print(f"\n📧 Starting Test Scenario 5...")
    success_5 = test_scenario_5_email_service_verification()
    test_results.append(("Scenario 5: Email Service Verification", success_5))
    
    # Print final results
    print("\n" + "="*120)
    print("📊 FINAL TEST RESULTS")
    print("="*120)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, success in test_results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {test_name}")
        if success:
            passed_tests += 1
    
    print(f"\n📈 SUMMARY: {passed_tests}/{total_tests} tests passed ({(passed_tests/total_tests)*100:.1f}%)")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! Payment and order status email functionality is working correctly.")
        return True
    else:
        print("⚠️  SOME TESTS FAILED. Please review the failed scenarios above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)