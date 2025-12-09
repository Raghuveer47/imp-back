#!/usr/bin/env python3
"""
Comprehensive System Test
Tests backend, Cloudinary, and all components
"""

import os
import sys
import django
import requests
import json
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'employeemanagement.settings')
django.setup()

def test_django_setup():
    """Test Django setup"""
    print("🧪 Testing Django Setup")
    print("=" * 30)
    
    try:
        from django.conf import settings
        print(f"✅ Django settings loaded")
        print(f"✅ DEBUG: {settings.DEBUG}")
        print(f"✅ ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        print(f"✅ CORS_ALLOW_ALL_ORIGINS: {settings.CORS_ALLOW_ALL_ORIGINS}")
        return True
    except Exception as e:
        print(f"❌ Django setup failed: {e}")
        return False

def test_cloudinary():
    """Test Cloudinary configuration"""
    print("\n🧪 Testing Cloudinary")
    print("=" * 30)
    
    try:
        from employees.cloudinary_utils import configure_cloudinary
        configure_cloudinary()
        print("✅ Cloudinary configured successfully")
        return True
    except Exception as e:
        print(f"❌ Cloudinary test failed: {e}")
        return False

def test_database():
    """Test database connection"""
    print("\n🧪 Testing Database")
    print("=" * 30)
    
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints"""
    print("\n🧪 Testing API Endpoints")
    print("=" * 30)
    
    base_url = "http://localhost:8000"
    endpoints = [
        "/api/health/",
        "/api/info/",
        "/api/employees/",
    ]
    
    all_working = True
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {endpoint} - OK")
            else:
                print(f"⚠️  {endpoint} - Status {response.status_code}")
                all_working = False
        except requests.exceptions.ConnectionError:
            print(f"❌ {endpoint} - Connection failed (server not running)")
            all_working = False
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")
            all_working = False
    
    return all_working

def test_models():
    """Test Django models"""
    print("\n🧪 Testing Models")
    print("=" * 30)
    
    try:
        from employees.models import Employee, Attendance, OfficeLocation
        print("✅ All models imported successfully")
        
        # Test creating objects
        office = OfficeLocation.objects.create(
            name="Test Office",
            latitude=16.516225,
            longitude=80.668270,
            radius_meters=100.0
        )
        print("✅ OfficeLocation creation successful")
        
        # Clean up
        office.delete()
        print("✅ Test cleanup successful")
        
        return True
    except Exception as e:
        print(f"❌ Models test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Employee Attendance System - Comprehensive Test")
    print("=" * 50)
    
    tests = [
        ("Django Setup", test_django_setup),
        ("Cloudinary", test_cloudinary),
        ("Database", test_database),
        ("Models", test_models),
        ("API Endpoints", test_api_endpoints),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready!")
        print("\n🚀 Next steps:")
        print("1. Start server: python manage.py runserver 0.0.0.0:8000")
        print("2. Start frontend: cd ../front-imop && npm run dev")
        print("3. Access from anywhere on your network!")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 