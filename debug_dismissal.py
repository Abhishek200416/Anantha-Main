#!/usr/bin/env python3
"""
Debug notification dismissal system
"""

import requests
import json
from datetime import datetime, timezone, timedelta

BACKEND_URL = "https://recipe-store-1.preview.emergentagent.com/api"

def debug_dismissal():
    # Login
    response = requests.post(f"{BACKEND_URL}/auth/admin-login", json={"password": "admin123"})
    token = response.json()["token"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    print("🔍 DEBUGGING NOTIFICATION DISMISSAL")
    print("="*50)
    
    # Step 1: Get initial count
    response = requests.get(f"{BACKEND_URL}/admin/notifications/count", headers=headers)
    initial_count = response.json()
    print(f"1. Initial count: {json.dumps(initial_count, indent=2)}")
    
    # Step 2: Dismiss city suggestions
    print(f"\n2. Dismissing city_suggestions...")
    dismiss_data = {"type": "city_suggestions"}
    response = requests.post(f"{BACKEND_URL}/admin/notifications/dismiss-all", headers=headers, json=dismiss_data)
    print(f"   Dismiss response: {response.status_code} - {response.text}")
    
    # Step 3: Get count immediately after
    response = requests.get(f"{BACKEND_URL}/admin/notifications/count", headers=headers)
    after_count = response.json()
    print(f"3. Count after dismiss: {json.dumps(after_count, indent=2)}")
    
    # Step 4: Wait 1 second and try again
    import time
    time.sleep(1)
    response = requests.get(f"{BACKEND_URL}/admin/notifications/count", headers=headers)
    wait_count = response.json()
    print(f"4. Count after 1 second: {json.dumps(wait_count, indent=2)}")
    
    # Step 5: Check if there are any pending city suggestions at all
    response = requests.get(f"{BACKEND_URL}/admin/city-suggestions", headers=headers)
    suggestions = response.json()
    print(f"5. Actual pending suggestions: {len(suggestions)}")
    for i, suggestion in enumerate(suggestions[:3]):  # Show first 3
        print(f"   Suggestion {i+1}: {suggestion.get('city')}, {suggestion.get('state')} - {suggestion.get('status')}")
    
    # Analysis
    print(f"\n📊 ANALYSIS:")
    print(f"   - Initial city_suggestions count: {initial_count.get('city_suggestions')}")
    print(f"   - After dismissal count: {after_count.get('city_suggestions')}")
    print(f"   - Actual pending suggestions: {len(suggestions)}")
    
    if after_count.get('city_suggestions') == 0:
        print(f"   ✅ Dismissal working correctly")
    elif len(suggestions) == 0:
        print(f"   ⚠️  No pending suggestions but count not zero - possible caching issue")
    else:
        print(f"   ❌ Dismissal not working - count should be 0 but is {after_count.get('city_suggestions')}")

if __name__ == "__main__":
    debug_dismissal()