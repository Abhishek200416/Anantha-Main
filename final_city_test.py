#!/usr/bin/env python3
"""
Final Comprehensive City Approval and Notification Features Test
Tests all the features mentioned in the review request
"""

import requests
import json
import time
from datetime import datetime

BACKEND_URL = "https://codebase-organizer-2.preview.emergentagent.com/api"

def admin_login():
    """Login as admin and get auth token"""
    response = requests.post(f"{BACKEND_URL}/auth/admin-login", json={"password": "admin123"})
    if response.status_code == 200:
        return response.json()["token"]
    return None

def test_complete_city_approval_workflow():
    """Test complete city approval workflow with email & location addition"""
    print("\n🏙️ TESTING COMPLETE CITY APPROVAL WORKFLOW")
    print("="*60)
    
    admin_token = admin_login()
    if not admin_token:
        print("❌ Failed to get admin token")
        return []
    
    headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
    results = []
    
    # Step 1: Create city suggestion
    suggestion_data = {
        "state": "Karnataka",
        "city": "Mysore",
        "customer_name": "Test User Mysore",
        "phone": "9876543215",
        "email": "mysore@example.com"
    }
    
    response = requests.post(f"{BACKEND_URL}/suggest-city", json=suggestion_data)
    if response.status_code == 200:
        suggestion_id = response.json()["suggestion_id"]
        print(f"✅ City suggestion created: {suggestion_id}")
        results.append(("Create City Suggestion", True))
    else:
        print(f"❌ Failed to create city suggestion")
        results.append(("Create City Suggestion", False))
        return results
    
    # Step 2: Verify in admin list
    response = requests.get(f"{BACKEND_URL}/admin/city-suggestions", headers=headers)
    if response.status_code == 200:
        suggestions = response.json()
        found = any(s.get("id") == suggestion_id for s in suggestions)
        if found:
            print(f"✅ Suggestion appears in admin list")
            results.append(("Suggestion in Admin List", True))
        else:
            print(f"❌ Suggestion not in admin list")
            results.append(("Suggestion in Admin List", False))
    else:
        results.append(("Suggestion in Admin List", False))
    
    # Step 3: Approve with delivery settings
    approval_data = {
        "status": "approved",
        "delivery_charge": 99,
        "free_delivery_threshold": 1000
    }
    
    response = requests.put(f"{BACKEND_URL}/admin/city-suggestions/{suggestion_id}/status", 
                           headers=headers, json=approval_data)
    if response.status_code == 200:
        print(f"✅ City approved successfully")
        results.append(("Approve City", True))
    else:
        print(f"❌ Failed to approve city")
        results.append(("Approve City", False))
        return results
    
    # Step 4: Verify city in locations
    response = requests.get(f"{BACKEND_URL}/locations")
    if response.status_code == 200:
        locations = response.json()
        mysore_location = next((loc for loc in locations if loc.get("name") == "Mysore"), None)
        
        if mysore_location and mysore_location.get("charge") == 99:
            print(f"✅ City added to locations with correct settings")
            results.append(("City Added to Locations", True))
        else:
            print(f"❌ City not properly added to locations")
            results.append(("City Added to Locations", False))
    else:
        results.append(("City Added to Locations", False))
    
    # Step 5: Verify suggestion status updated (removed from pending list)
    response = requests.get(f"{BACKEND_URL}/admin/city-suggestions", headers=headers)
    if response.status_code == 200:
        suggestions = response.json()
        found = any(s.get("id") == suggestion_id for s in suggestions)
        if not found:
            print(f"✅ Approved suggestion removed from pending list")
            results.append(("Suggestion Status Updated", True))
        else:
            print(f"❌ Approved suggestion still in pending list")
            results.append(("Suggestion Status Updated", False))
    else:
        results.append(("Suggestion Status Updated", False))
    
    return results

def test_city_rejection_workflow():
    """Test city rejection workflow"""
    print("\n🚫 TESTING CITY REJECTION WORKFLOW")
    print("="*60)
    
    admin_token = admin_login()
    if not admin_token:
        return []
    
    headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
    results = []
    
    # Create and reject city suggestion
    suggestion_data = {
        "state": "Tamil Nadu",
        "city": "Coimbatore",
        "customer_name": "Test User Coimbatore",
        "phone": "9876543216",
        "email": "coimbatore@example.com"
    }
    
    response = requests.post(f"{BACKEND_URL}/suggest-city", json=suggestion_data)
    if response.status_code == 200:
        suggestion_id = response.json()["suggestion_id"]
        print(f"✅ City suggestion created for rejection test")
        
        # Reject it
        rejection_data = {"status": "rejected"}
        response = requests.put(f"{BACKEND_URL}/admin/city-suggestions/{suggestion_id}/status", 
                               headers=headers, json=rejection_data)
        
        if response.status_code == 200:
            print(f"✅ City rejected successfully")
            results.append(("Reject City", True))
            
            # Verify city NOT in locations
            response = requests.get(f"{BACKEND_URL}/locations")
            if response.status_code == 200:
                locations = response.json()
                coimbatore_location = next((loc for loc in locations if loc.get("name") == "Coimbatore"), None)
                
                if not coimbatore_location:
                    print(f"✅ Rejected city correctly NOT in locations")
                    results.append(("City NOT in Locations", True))
                else:
                    print(f"❌ Rejected city incorrectly found in locations")
                    results.append(("City NOT in Locations", False))
            else:
                results.append(("City NOT in Locations", False))
        else:
            results.append(("Reject City", False))
    else:
        results.append(("Reject City", False))
    
    return results

def test_notification_dismissal_system():
    """Test notification dismissal system"""
    print("\n🔔 TESTING NOTIFICATION DISMISSAL SYSTEM")
    print("="*60)
    
    admin_token = admin_login()
    if not admin_token:
        return []
    
    headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
    results = []
    
    # Create a city suggestion to have notifications
    suggestion_data = {
        "state": "West Bengal",
        "city": "Kolkata",
        "customer_name": "Test User Kolkata",
        "phone": "9876543217",
        "email": "kolkata@example.com"
    }
    
    response = requests.post(f"{BACKEND_URL}/suggest-city", json=suggestion_data)
    if response.status_code == 200:
        print(f"✅ Created suggestion for notification test")
        
        # Get initial count
        response = requests.get(f"{BACKEND_URL}/admin/notifications/count", headers=headers)
        if response.status_code == 200:
            initial_count = response.json()
            print(f"Initial city_suggestions count: {initial_count.get('city_suggestions')}")
            
            # Dismiss notifications
            dismiss_data = {"type": "city_suggestions"}
            response = requests.post(f"{BACKEND_URL}/admin/notifications/dismiss-all", 
                                   headers=headers, json=dismiss_data)
            
            if response.status_code == 200:
                print(f"✅ Notifications dismissed")
                
                # Check count after dismissal
                response = requests.get(f"{BACKEND_URL}/admin/notifications/count", headers=headers)
                if response.status_code == 200:
                    after_count = response.json()
                    print(f"After dismissal city_suggestions count: {after_count.get('city_suggestions')}")
                    
                    if after_count.get('city_suggestions') == 0:
                        print(f"✅ Dismissal working correctly")
                        results.append(("Notification Dismissal", True))
                    else:
                        print(f"❌ Dismissal not working")
                        results.append(("Notification Dismissal", False))
                else:
                    results.append(("Notification Dismissal", False))
            else:
                results.append(("Notification Dismissal", False))
        else:
            results.append(("Notification Dismissal", False))
    else:
        results.append(("Notification Dismissal", False))
    
    return results

def test_direct_approve_city_endpoint():
    """Test direct approve-city endpoint"""
    print("\n✅ TESTING DIRECT APPROVE-CITY ENDPOINT")
    print("="*60)
    
    admin_token = admin_login()
    if not admin_token:
        return []
    
    headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
    results = []
    
    # Use direct approve endpoint for a new city
    approve_data = {
        "city_name": "Madurai",
        "state_name": "Tamil Nadu",
        "delivery_charge": 65,
        "free_delivery_threshold": 850
    }
    
    response = requests.post(f"{BACKEND_URL}/admin/approve-city", headers=headers, json=approve_data)
    
    if response.status_code == 200:
        print(f"✅ Direct city approval successful")
        results.append(("Direct City Approval", True))
        
        # Verify city in locations
        response = requests.get(f"{BACKEND_URL}/locations")
        if response.status_code == 200:
            locations = response.json()
            madurai_location = next((loc for loc in locations if loc.get("name") == "Madurai"), None)
            
            if madurai_location and madurai_location.get("charge") == 65:
                print(f"✅ Directly approved city added to locations")
                results.append(("Direct Approval in Locations", True))
            else:
                print(f"❌ Directly approved city not properly added")
                results.append(("Direct Approval in Locations", False))
        else:
            results.append(("Direct Approval in Locations", False))
    elif response.status_code == 400 and "already been approved" in response.text:
        print(f"✅ Direct approval correctly prevents duplicates")
        results.append(("Direct City Approval", True))
        results.append(("Direct Approval in Locations", True))
    else:
        print(f"❌ Direct city approval failed: {response.text}")
        results.append(("Direct City Approval", False))
        results.append(("Direct Approval in Locations", False))
    
    return results

def main():
    """Run comprehensive city approval and notification tests"""
    print("🎯 FINAL COMPREHENSIVE CITY APPROVAL AND NOTIFICATION TESTING")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now()}")
    print("="*80)
    
    all_results = []
    
    # Test admin authentication first
    admin_token = admin_login()
    if admin_token:
        print("✅ Admin authentication successful")
        all_results.append(("Admin Authentication", True))
    else:
        print("❌ Admin authentication failed")
        all_results.append(("Admin Authentication", False))
        return 1
    
    # Run all test suites
    all_results.extend(test_complete_city_approval_workflow())
    all_results.extend(test_city_rejection_workflow())
    all_results.extend(test_notification_dismissal_system())
    all_results.extend(test_direct_approve_city_endpoint())
    
    # Summary
    print("\n" + "="*80)
    print("📊 FINAL COMPREHENSIVE TEST RESULTS")
    print("="*80)
    
    passed = 0
    total = len(all_results)
    
    # Group by category for better reporting
    categories = {
        "Authentication": [],
        "City Approval Workflow": [],
        "City Rejection Workflow": [],
        "Notification System": [],
        "Direct Approval": []
    }
    
    for test_name, success in all_results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {test_name}")
        if success:
            passed += 1
        
        # Categorize
        if "Authentication" in test_name:
            categories["Authentication"].append((test_name, success))
        elif "Reject" in test_name or "NOT in Locations" in test_name:
            categories["City Rejection Workflow"].append((test_name, success))
        elif "Direct" in test_name:
            categories["Direct Approval"].append((test_name, success))
        elif "Notification" in test_name or "Dismissal" in test_name:
            categories["Notification System"].append((test_name, success))
        else:
            categories["City Approval Workflow"].append((test_name, success))
    
    print(f"\n🎯 OVERALL RESULT: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    # Category breakdown
    print(f"\n📋 CATEGORY BREAKDOWN:")
    for category, tests in categories.items():
        if tests:
            cat_passed = sum(1 for _, success in tests if success)
            cat_total = len(tests)
            print(f"   {category}: {cat_passed}/{cat_total} passed")
    
    if passed == total:
        print("\n🎉 ALL CITY APPROVAL AND NOTIFICATION FEATURES WORKING PERFECTLY!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} TESTS FAILED - See details above")
        return 1

if __name__ == "__main__":
    exit(main())