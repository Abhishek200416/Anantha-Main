#!/usr/bin/env python3
"""
Backend API Testing Script for Cities and States Management
Tests the new APIs added for location and state management
"""

import requests
import json
import sys
from datetime import datetime
import time

# Backend URL from environment
BACKEND_URL = "https://env-config-tool.preview.emergentagent.com/api"

def test_api_endpoint(method, endpoint, headers=None, data=None, description="", expected_status=None):
    """Test a single API endpoint"""
    url = f"{BACKEND_URL}{endpoint}"
    
    print(f"\n{'='*70}")
    print(f"Testing: {method} {endpoint}")
    print(f"Description: {description}")
    print(f"{'='*70}")
    
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
            print(f"Response: {json.dumps(response_data, indent=2)}")
        except:
            print(f"Response Text: {response.text}")
        
        # Check if request was successful
        if expected_status:
            success = response.status_code == expected_status
        else:
            success = 200 <= response.status_code < 300
            
        if success:
            print("✅ SUCCESS")
            return True, response_data
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            return False, response_data
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
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
        print(f"✅ Successfully logged in as admin")
        return token
    
    print("❌ Failed to get admin authentication token")
    return None

def main():
    """Main testing function"""
    print("🚀 Testing Cities and States Management APIs")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now()}")
    
    test_results = {}
    
    # Step 1: Admin login
    auth_token = admin_login()
    if not auth_token:
        print("\n❌ CRITICAL: Cannot proceed without admin authentication token")
        return 1
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # ============= TEST 1: DELETE CITY API =============
    print("\n" + "="*80)
    print("🏙️  TEST 1: DELETE CITY API")
    print("="*80)
    
    # Test 1.1: Get current cities
    print("\n--- Step 1.1: Get current cities ---")
    success, current_locations = test_api_endpoint(
        "GET",
        "/locations",
        description="Get current cities/locations"
    )
    
    test_results['get_locations'] = success
    
    if success and current_locations and len(current_locations) > 0:
        print(f"\n📊 Found {len(current_locations)} cities")
        print(f"Sample cities: {[loc.get('name') for loc in current_locations[:5]]}")
        
        # Pick a city to delete (avoid major cities)
        test_city = None
        for location in current_locations:
            city_name = location.get('name', '')
            if city_name not in ['Hyderabad', 'Vijayawada', 'Visakhapatnam', 'Guntur', 'Warangal']:
                test_city = city_name
                break
        
        if test_city:
            print(f"\n🎯 Selected city for deletion test: {test_city}")
            
            # Test 1.2: Delete the city
            print("\n--- Step 1.2: Delete the city ---")
            success, response = test_api_endpoint(
                "DELETE",
                f"/admin/locations/{test_city}",
                headers=headers,
                description=f"Delete city: {test_city}"
            )
            test_results['delete_city'] = success
            
            time.sleep(0.5)
            
            # Test 1.3: Verify city is deleted
            print("\n--- Step 1.3: Verify city was deleted ---")
            success, updated_locations = test_api_endpoint(
                "GET",
                "/locations",
                description="Verify city was deleted"
            )
            
            if success and updated_locations:
                city_still_exists = any(loc.get('name') == test_city for loc in updated_locations)
                
                if not city_still_exists:
                    print(f"✅ City '{test_city}' successfully deleted")
                    test_results['verify_city_deleted'] = True
                else:
                    print(f"❌ City '{test_city}' still exists after deletion")
                    test_results['verify_city_deleted'] = False
            else:
                test_results['verify_city_deleted'] = False
        else:
            print(f"⚠️  No suitable city found for deletion test")
            test_results['delete_city'] = None
            test_results['verify_city_deleted'] = None
    else:
        print(f"⚠️  No locations found or API failed")
        test_results['get_locations'] = False
    
    # ============= TEST 2: STATES MANAGEMENT APIs =============
    print("\n" + "="*80)
    print("🗺️  TEST 2: STATES MANAGEMENT APIs")
    print("="*80)
    
    # Test 2.1: GET /api/states (public - enabled states only)
    print("\n--- Step 2.1: Get enabled states (public API) ---")
    success, public_states = test_api_endpoint(
        "GET",
        "/states",
        description="Get all enabled states (public API)"
    )
    test_results['get_public_states'] = success
    
    if success and public_states:
        print(f"\n📊 Public States: {len(public_states)} states")
        for state in public_states[:5]:
            print(f"  • {state.get('name')} (enabled: {state.get('enabled', False)})")
    
    time.sleep(0.5)
    
    # Test 2.2: GET /api/admin/states (admin - all states)
    print("\n--- Step 2.2: Get all states (admin API) ---")
    success, admin_states = test_api_endpoint(
        "GET",
        "/admin/states",
        headers=headers,
        description="Get all states for admin management"
    )
    test_results['get_admin_states'] = success
    
    if success and admin_states:
        enabled_count = sum(1 for s in admin_states if s.get('enabled', False))
        disabled_count = len(admin_states) - enabled_count
        print(f"\n📊 Admin States: {len(admin_states)} total")
        print(f"  - Enabled: {enabled_count}")
        print(f"  - Disabled: {disabled_count}")
        
        for state in admin_states[:5]:
            print(f"  • {state.get('name')} (enabled: {state.get('enabled', False)})")
    
    time.sleep(0.5)
    
    # Test 2.3: POST /api/admin/states - Add a new state
    print("\n--- Step 2.3: Add new state (Kerala) ---")
    new_state_name = "Kerala"
    new_state_data = {
        "name": new_state_name,
        "enabled": True
    }
    
    success, response = test_api_endpoint(
        "POST",
        "/admin/states",
        headers=headers,
        data=new_state_data,
        description=f"Add new state: {new_state_name}"
    )
    test_results['add_new_state'] = success
    
    time.sleep(0.5)
    
    # Test 2.4: Verify new state was added
    print("\n--- Step 2.4: Verify new state was added ---")
    success, states_after_add = test_api_endpoint(
        "GET",
        "/admin/states",
        headers=headers,
        description="Verify new state was added"
    )
    
    if success and states_after_add:
        new_state_exists = any(s.get('name') == new_state_name for s in states_after_add)
        
        if new_state_exists:
            print(f"✅ State '{new_state_name}' successfully added")
            test_results['verify_state_added'] = True
        else:
            print(f"❌ State '{new_state_name}' not found after addition")
            test_results['verify_state_added'] = False
    else:
        test_results['verify_state_added'] = False
    
    time.sleep(0.5)
    
    # Test 2.5: PUT /api/admin/states/{state_name} - Update state status
    print("\n--- Step 2.5: Update state status (disable Kerala) ---")
    update_state_data = {
        "name": new_state_name,
        "enabled": False
    }
    
    success, response = test_api_endpoint(
        "PUT",
        f"/admin/states/{new_state_name}",
        headers=headers,
        data=update_state_data,
        description=f"Update state '{new_state_name}' to disabled"
    )
    test_results['update_state_status'] = success
    
    time.sleep(0.5)
    
    # Test 2.6: Verify state status was updated
    print("\n--- Step 2.6: Verify state status was updated ---")
    success, states_after_update = test_api_endpoint(
        "GET",
        "/admin/states",
        headers=headers,
        description="Verify state status was updated"
    )
    
    if success and states_after_update:
        updated_state = next((s for s in states_after_update if s.get('name') == new_state_name), None)
        
        if updated_state:
            is_enabled = updated_state.get('enabled', True)
            
            if not is_enabled:
                print(f"✅ State '{new_state_name}' successfully updated to disabled")
                test_results['verify_state_updated'] = True
            else:
                print(f"❌ State status not updated correctly")
                test_results['verify_state_updated'] = False
        else:
            print(f"❌ State not found after update")
            test_results['verify_state_updated'] = False
    else:
        test_results['verify_state_updated'] = False
    
    time.sleep(0.5)
    
    # Test 2.7: DELETE /api/admin/states/{state_name} - Delete the test state
    print("\n--- Step 2.7: Delete state (Kerala) ---")
    success, response = test_api_endpoint(
        "DELETE",
        f"/admin/states/{new_state_name}",
        headers=headers,
        description=f"Delete state: {new_state_name}"
    )
    test_results['delete_state'] = success
    
    time.sleep(0.5)
    
    # Test 2.8: Verify state was deleted
    print("\n--- Step 2.8: Verify state was deleted ---")
    success, states_after_delete = test_api_endpoint(
        "GET",
        "/admin/states",
        headers=headers,
        description="Verify state was deleted"
    )
    
    if success and states_after_delete:
        deleted_state_exists = any(s.get('name') == new_state_name for s in states_after_delete)
        
        if not deleted_state_exists:
            print(f"✅ State '{new_state_name}' successfully deleted")
            test_results['verify_state_deleted'] = True
        else:
            print(f"❌ State still exists after deletion")
            test_results['verify_state_deleted'] = False
    else:
        test_results['verify_state_deleted'] = False
    
    time.sleep(0.5)
    
    # Test 2.9: Test error handling - Delete non-existent state
    print("\n--- Step 2.9: Error handling - Delete non-existent state ---")
    success, response = test_api_endpoint(
        "DELETE",
        "/admin/states/NonExistentState123",
        headers=headers,
        description="Test error handling: Delete non-existent state",
        expected_status=404
    )
    test_results['delete_nonexistent_state_error'] = success
    
    if success:
        print(f"✅ Correctly returns 404 for non-existent state")
    
    time.sleep(0.5)
    
    # Test 2.10: Test error handling - Add duplicate state
    print("\n--- Step 2.10: Error handling - Add duplicate state ---")
    # First, ensure a state exists
    test_state_data = {"name": "TestState", "enabled": True}
    test_api_endpoint(
        "POST",
        "/admin/states",
        headers=headers,
        data=test_state_data,
        description="Add TestState (for duplicate test)"
    )
    
    time.sleep(0.5)
    
    # Try to add it again
    success, response = test_api_endpoint(
        "POST",
        "/admin/states",
        headers=headers,
        data=test_state_data,
        description="Test error handling: Add duplicate state",
        expected_status=400
    )
    test_results['add_duplicate_state_error'] = success
    
    if success:
        print(f"✅ Correctly returns 400 for duplicate state")
    
    # Clean up - delete TestState
    test_api_endpoint(
        "DELETE",
        "/admin/states/TestState",
        headers=headers,
        description="Clean up: Delete TestState"
    )
    
    # ============= FINAL SUMMARY =============
    print(f"\n{'='*80}")
    print("🎯 TEST SUMMARY - CITIES AND STATES MANAGEMENT")
    print(f"{'='*80}")
    
    # Filter out None values
    valid_results = {k: v for k, v in test_results.items() if v is not None}
    
    total_tests = len(valid_results)
    passed_tests = sum(1 for result in valid_results.values() if result)
    failed_tests = total_tests - passed_tests
    
    print("\n📋 Detailed Results:")
    
    print("\n  🏙️  Cities Management:")
    city_tests = {k: v for k, v in test_results.items() if 'city' in k or 'location' in k}
    for test_name, result in city_tests.items():
        if result is not None:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"    {test_name}: {status}")
    
    print("\n  🗺️  States Management:")
    state_tests = {k: v for k, v in test_results.items() if 'state' in k}
    for test_name, result in state_tests.items():
        if result is not None:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"    {test_name}: {status}")
    
    print(f"\n📊 Overall Statistics:")
    print(f"  Total Tests: {total_tests}")
    print(f"  Passed: {passed_tests}")
    print(f"  Failed: {failed_tests}")
    print(f"  Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests > 0:
        print(f"\n⚠️  {failed_tests} test(s) failed. Check the detailed output above.")
        return 1
    else:
        print(f"\n🎉 All tests passed! Cities and States Management APIs are working correctly.")
        return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
