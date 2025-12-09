#!/usr/bin/env python3
"""
Test script to simulate employee going offline
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

def test_employee_offline():
    """Test an employee going offline"""
    print("🧪 Testing employee going offline...")
    
    # First, send a location update (online)
    online_data = {
        "employee_id": "2",
        "latitude": 16.516225,
        "longitude": 80.668270,
        "is_in_office_radius": True,
        "distance_from_office": 50.0,
        "is_sharing": True,
        "timestamp": "2024-01-01T12:00:00Z"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/location-update/", json=online_data)
        print(f"📍 Online location update response: {response.status_code}")
        if response.ok:
            print(f"✅ Online status: {response.json()}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    time.sleep(2)
    
    # Now send offline status
    offline_data = {
        "employee_id": "2",
        "latitude": 16.516225,
        "longitude": 80.668270,
        "is_in_office_radius": True,
        "distance_from_office": 50.0,
        "is_sharing": False,  # This marks the employee as offline
        "timestamp": "2024-01-01T12:00:00Z"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/location-update/", json=offline_data)
        print(f"📍 Offline location update response: {response.status_code}")
        if response.ok:
            print(f"✅ Offline status: {response.json()}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    time.sleep(2)
    
    # Check live locations to see the offline status
    try:
        response = requests.get(f"{BASE_URL}/live-employee-locations/")
        print(f"📡 Live locations response: {response.status_code}")
        if response.ok:
            locations = response.json()
            print(f"✅ Found {len(locations)} employee locations:")
            for loc in locations:
                status = "🟢 ONLINE" if loc.get('status') == 'online' else "🔴 OFFLINE"
                print(f"   - {loc['employee_name']} ({loc['employee_id']}): {status}")
                if loc.get('status') == 'online':
                    print(f"     📍 {loc['distance_from_office']:.0f}m from office")
                else:
                    print(f"     📍 Last seen: {loc.get('last_updated', 'Never')}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting offline test...")
    test_employee_offline()
    print("\n✅ Offline test completed!") 