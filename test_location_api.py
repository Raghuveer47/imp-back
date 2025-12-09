#!/usr/bin/env python3
"""
Test script for location API endpoints
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

def test_location_update():
    """Test the location update endpoint"""
    print("🧪 Testing location update endpoint...")
    
    data = {
        "employee_id": "1",  # Use an existing employee ID
        "latitude": 16.516225,
        "longitude": 80.668270,
        "is_in_office_radius": True,
        "distance_from_office": 50.0,
        "timestamp": "2024-01-01T12:00:00Z"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/location-update/", json=data)
        print(f"📍 Location update response: {response.status_code}")
        if response.ok:
            print(f"✅ Success: {response.json()}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Request failed: {e}")

def test_live_locations():
    """Test the live employee locations endpoint"""
    print("\n🧪 Testing live employee locations endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/live-employee-locations/")
        print(f"📡 Live locations response: {response.status_code}")
        if response.ok:
            locations = response.json()
            print(f"✅ Found {len(locations)} employee locations:")
            for loc in locations:
                print(f"   - {loc['employee_name']}: {loc['distance_from_office']:.0f}m from office")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Request failed: {e}")

def test_employee_list():
    """Test the employee list endpoint"""
    print("\n🧪 Testing employee list endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/employees/")
        print(f"👥 Employee list response: {response.status_code}")
        if response.ok:
            employees = response.json()
            print(f"✅ Found {len(employees)} employees:")
            for emp in employees:
                print(f"   - {emp['name']} (ID: {emp['employee_id']})")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting API tests...")
    test_employee_list()
    test_location_update()
    time.sleep(2)  # Wait a bit for the location to be saved
    test_live_locations()
    print("\n✅ API tests completed!") 