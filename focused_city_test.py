#!/usr/bin/env python3
"""
Focused City Approval and Notification Testing
Tests the specific issues found in the comprehensive test
"""

import requests
import json
import time
from datetime import datetime

BACKEND_URL = "https://recipe-store-1.preview.emergentagent.com/api"

def admin_login():
    """Login as admin and get auth token"""
    response = requests.post(f"{BACKEND_URL}/auth/admin-login", json={"password": "admin123"})
    if response.status_code == 200:
        return response.json()["token"]
    return None

def test_direct_approve_city_endpoint():
    """Test the direct approve-city endpoint after fix"""
    print("\n🔧 TESTING FIXED APPROVE-CITY ENDPOINT")
    print("="*60)
    
    admin_token = admin_login()
    if not admin_token:
        print("❌ Failed to get admin token")
        return False
    
    headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
    
    # Test direct approve-city endpoint
    approve_data = {
        "city_name": "Tirupati",
        "state_name": "Andhra Pradesh", 
        "delivery_charge": 75,
        "free_delivery_threshold": 900
    }
    
    response = requests.post(f"{BACKEND_URL}/admin/approve-city", headers=headers, json=approve_data)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ SUCCESS: {data.get('message')}")
        print(f"City Data: {json.dumps(data.get('city_data'), indent=2)}")
        return True
    else:
        print(f"❌ FAILED: {response.text}")
        return False

def test_city_suggestion_workflow():
    """Test complete city suggestion workflow"""
    print("\n🏙️ TESTING COMPLETE CITY SUGGESTION WORKFLOW")
    print("="*60)
    
    admin_token = admin_login()
    if not admin_token:
        print("❌ Failed to get admin token")
        return False
    
    headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
    
    # Step 1: Create city suggestion
    suggestion_data = {
        "state": "Kerala",
        "city": "Kochi",
        "customer_name": "Test User Kerala",
        "phone": "9876543213",
        "email": "kerala@example.com"
    }
    
    response = requests.post(f"{BACKEND_URL}/suggest-city", json=suggestion_data)
    if response.status_code != 200:
        print(f"❌ Failed to create suggestion: {response.text}")
        return False
    
    suggestion_id = response.json()["suggestion_id"]
    print(f"✅ Created suggestion with ID: {suggestion_id}")
    
    # Step 2: Check it appears in admin list
    response = requests.get(f"{BACKEND_URL}/admin/city-suggestions", headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to get suggestions: {response.text}")
        return False
    
    suggestions = response.json()
    found = any(s.get("id") == suggestion_id for s in suggestions)
    if found:
        print(f"✅ Suggestion found in admin list")
    else:
        print(f"❌ Suggestion not found in admin list")
        return False
    
    # Step 3: Approve the suggestion
    approval_data = {
        "status": "approved",
        "delivery_charge": 85,
        "free_delivery_threshold": 950
    }
    
    response = requests.put(f"{BACKEND_URL}/admin/city-suggestions/{suggestion_id}/status", 
                           headers=headers, json=approval_data)
    if response.status_code != 200:
        print(f"❌ Failed to approve suggestion: {response.text}")
        return False
    
    print(f"✅ Suggestion approved successfully")
    
    # Step 4: Verify city appears in locations
    response = requests.get(f"{BACKEND_URL}/locations")
    if response.status_code != 200:
        print(f"❌ Failed to get locations: {response.text}")
        return False
    
    locations = response.json()
    kochi_location = next((loc for loc in locations if loc.get("name") == "Kochi"), None)
    
    if kochi_location:
        print(f"✅ Kochi found in locations: {json.dumps(kochi_location, indent=2)}")
        
        # Verify correct settings
        if (kochi_location.get("charge") == 85 and 
            kochi_location.get("free_delivery_threshold") == 950):
            print(f"✅ Delivery settings are correct")
        else:
            print(f"❌ Delivery settings incorrect")
            return False
    else:
        print(f"❌ Kochi not found in locations")
        return False
    
    # Step 5: Verify suggestion no longer in pending list (correct behavior)
    response = requests.get(f"{BACKEND_URL}/admin/city-suggestions", headers=headers)
    if response.status_code == 200:
        suggestions = response.json()
        found = any(s.get("id") == suggestion_id for s in suggestions)
        if not found:
            print(f"✅ Approved suggestion correctly removed from pending list")
        else:
            print(f"⚠️  Approved suggestion still in pending list")
    
    return True

def test_notification_dismissal():
    """Test notification dismissal system"""
    print("\n🔔 TESTING NOTIFICATION DISMISSAL SYSTEM")
    print("="*60)
    
    admin_token = admin_login()
    if not admin_token:
        print("❌ Failed to get admin token")
        return False
    
    headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
    
    # Step 1: Create a city suggestion to have notifications
    suggestion_data = {
        "state": "Maharashtra",
        "city": "Mumbai",
        "customer_name": "Mumbai Test User",
        "phone": "9876543214",
        "email": "mumbai@example.com"
    }
    
    response = requests.post(f"{BACKEND_URL}/suggest-city", json=suggestion_data)
    if response.status_code != 200:
        print(f"❌ Failed to create suggestion for notification test")
        return False
    
    print(f"✅ Created suggestion for notification test")
    
    # Step 2: Get initial notification count
    response = requests.get(f"{BACKEND_URL}/admin/notifications/count", headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to get notification count: {response.text}")
        return False
    
    initial_counts = response.json()
    print(f"Initial counts: {json.dumps(initial_counts, indent=2)}")
    initial_city_suggestions = initial_counts.get("city_suggestions", 0)
    
    # Step 3: Dismiss city suggestions
    dismiss_data = {"type": "city_suggestions"}
    response = requests.post(f"{BACKEND_URL}/admin/notifications/dismiss-all", 
                           headers=headers, json=dismiss_data)
    if response.status_code != 200:
        print(f"❌ Failed to dismiss notifications: {response.text}")
        return False
    
    print(f"✅ Dismissed city suggestion notifications")
    
    # Step 4: Check count after dismissal
    response = requests.get(f"{BACKEND_URL}/admin/notifications/count", headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to get notification count after dismissal")
        return False
    
    after_counts = response.json()
    print(f"After dismissal counts: {json.dumps(after_counts, indent=2)}")
    
    if after_counts.get("city_suggestions", -1) == 0:
        print(f"✅ City suggestions count correctly reduced to 0")
        return True
    else:
        print(f"❌ City suggestions count not reduced: {after_counts.get('city_suggestions')}")
        return False

def main():
    """Run focused tests"""
    print("🎯 FOCUSED CITY APPROVAL AND NOTIFICATION TESTING")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now()}")
    print("="*80)
    
    results = []
    
    # Test 1: Direct approve-city endpoint (after fix)
    results.append(("Direct Approve-City Endpoint", test_direct_approve_city_endpoint()))
    
    # Test 2: Complete city suggestion workflow
    results.append(("City Suggestion Workflow", test_city_suggestion_workflow()))
    
    # Test 3: Notification dismissal
    results.append(("Notification Dismissal", test_notification_dismissal()))
    
    # Summary
    print("\n" + "="*80)
    print("📊 FOCUSED TEST RESULTS")
    print("="*80)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {test_name}")
        if success:
            passed += 1
    
    print(f"\n🎯 RESULT: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL FOCUSED TESTS PASSED!")
        return 0
    else:
        print("⚠️  SOME TESTS STILL FAILING")
        return 1

if __name__ == "__main__":
    exit(main())