#!/usr/bin/env python3
"""
Test script to verify location sharing functionality
"""

import requests
import json
import time
from datetime import datetime

# API base URL
API_BASE_URL = "http://localhost:8000/api"

def test_location_sharing():
    """Test location sharing for employee ID 2"""
    
    print("🧪 Testing Location Sharing Functionality")
    print("=" * 50)
    
    # Test 1: Check current employee locations
    print("\n1. 📍 Checking current employee locations...")
    try:
        response = requests.get(f"{API_BASE_URL}/live-employee-locations/")
        if response.status_code == 200:
            locations = response.json()
            print(f"✅ Found {len(locations)} employees")
            for emp in locations:
                status_icon = "🟢" if emp['status'] == 'online' else "🔴"
                print(f"   {status_icon} {emp['employee_name']} ({emp['employee_id']}): {emp['status']} - {emp['last_updated']}")
        else:
            print(f"❌ Failed to get locations: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting locations: {e}")
    
    # Test 2: Send location update for employee 2
    print("\n2. 📡 Sending location update for employee 'raghu'...")
    location_data = {
        "employee_id": "2",
        "latitude": 16.51622548720288,
        "longitude": 80.66827006623176,
        "is_in_office_radius": True,
        "distance_from_office": 5.0,
        "is_sharing": True,
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/location-update/",
            headers={"Content-Type": "application/json"},
            data=json.dumps(location_data)
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Location update successful: {result}")
        else:
            print(f"❌ Location update failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error sending location update: {e}")
    
    # Test 3: Check updated locations
    print("\n3. 📍 Checking updated employee locations...")
    try:
        response = requests.get(f"{API_BASE_URL}/live-employee-locations/")
        if response.status_code == 200:
            locations = response.json()
            raghu = next((emp for emp in locations if emp['employee_id'] == '2'), None)
            if raghu:
                status_icon = "🟢" if raghu['status'] == 'online' else "🔴"
                print(f"✅ {raghu['employee_name']} status: {status_icon} {raghu['status']}")
                print(f"   📍 Location: {raghu['latitude']}, {raghu['longitude']}")
                print(f"   🏢 In office radius: {raghu['is_in_office_radius']}")
                print(f"   📏 Distance: {raghu['distance_from_office']} meters")
                print(f"   🕐 Last updated: {raghu['last_updated']}")
                print(f"   📡 Sharing: {raghu['is_sharing']}")
            else:
                print("❌ Employee 'raghu' not found in locations")
        else:
            print(f"❌ Failed to get updated locations: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting updated locations: {e}")
    
    # Test 4: Test offline status
    print("\n4. 🔴 Testing offline status...")
    offline_data = {
        "employee_id": "2",
        "latitude": 16.51622548720288,
        "longitude": 80.66827006623176,
        "is_in_office_radius": True,
        "distance_from_office": 5.0,
        "is_sharing": False,  # Stop sharing
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/location-update/",
            headers={"Content-Type": "application/json"},
            data=json.dumps(offline_data)
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Offline status set: {result}")
        else:
            print(f"❌ Offline status failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error setting offline status: {e}")
    
    # Test 5: Final check
    print("\n5. 📍 Final location check...")
    try:
        response = requests.get(f"{API_BASE_URL}/live-employee-locations/")
        if response.status_code == 200:
            locations = response.json()
            raghu = next((emp for emp in locations if emp['employee_id'] == '2'), None)
            if raghu:
                status_icon = "🟢" if raghu['status'] == 'online' else "🔴"
                print(f"✅ {raghu['employee_name']} final status: {status_icon} {raghu['status']}")
                print(f"   📡 Sharing: {raghu['is_sharing']}")
            else:
                print("❌ Employee 'raghu' not found in final check")
        else:
            print(f"❌ Failed to get final locations: {response.status_code}")
    except Exception as e:
        print(f"❌ Error in final check: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Location sharing test completed!")

if __name__ == "__main__":
    test_location_sharing() 