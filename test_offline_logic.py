#!/usr/bin/env python3
"""
Test script to demonstrate automatic offline logic for employees
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'employeemanagement.settings')
django.setup()

from employees.models import Employee, EmployeeLocation, Attendance
from employees.views import check_employee_online_status
from django.utils import timezone

def test_offline_logic():
    """Test the automatic offline logic"""
    print("🧪 Testing Employee Offline Logic")
    print("=" * 50)
    
    employees = Employee.objects.all()
    
    if not employees.exists():
        print("❌ No employees found in database")
        return
    
    print(f"📊 Found {employees.count()} employees")
    print()
    
    for employee in employees:
        print(f"👤 Employee: {employee.name} ({employee.employee_id})")
        
        # Get latest attendance
        latest_attendance = Attendance.objects.filter(
            employee=employee
        ).order_by('-timestamp').first()
        
        # Get latest location
        latest_location = EmployeeLocation.objects.filter(
            employee=employee
        ).order_by('-timestamp').first()
        
        # Check online status
        is_online = check_employee_online_status(employee)
        
        print(f"   📅 Last attendance: {latest_attendance.timestamp if latest_attendance else 'Never'}")
        print(f"   📍 Last location: {latest_location.timestamp if latest_location else 'Never'}")
        
        if latest_attendance:
            time_since_login = timezone.now() - latest_attendance.timestamp
            print(f"   ⏰ Time since login: {time_since_login.total_seconds()/3600:.1f} hours")
        
        if latest_location:
            time_since_location = timezone.now() - latest_location.timestamp
            print(f"   📍 Time since location: {time_since_location.total_seconds()/60:.1f} minutes")
        
        print(f"   🟢 Status: {'ONLINE' if is_online else 'OFFLINE'}")
        print()
    
    print("📋 Offline Rules:")
    print("   • No login for > 1 hour → OFFLINE")
    print("   • No location for > 30 minutes → OFFLINE")
    print("   • Both conditions must be met to stay ONLINE")

def create_test_data():
    """Create test data to demonstrate offline logic"""
    print("🔧 Creating test data...")
    
    # Get first employee
    try:
        employee = Employee.objects.first()
        if not employee:
            print("❌ No employees found. Please create an employee first.")
            return
    except Employee.DoesNotExist:
        print("❌ No employees found. Please create an employee first.")
        return
    
    print(f"👤 Using employee: {employee.name}")
    
    # Create old attendance (more than 1 hour ago)
    old_attendance = Attendance.objects.create(
        employee=employee,
        image=employee.face_image,  # Reuse existing image
        latitude=employee.office.latitude,
        longitude=employee.office.longitude,
        action='login',
        timestamp=timezone.now() - timedelta(hours=2)  # 2 hours ago
    )
    print(f"✅ Created old attendance: {old_attendance.timestamp}")
    
    # Create old location (more than 30 minutes ago)
    old_location = EmployeeLocation.objects.create(
        employee=employee,
        latitude=employee.office.latitude,
        longitude=employee.office.longitude,
        is_in_office_radius=True,
        distance_from_office=0,
        is_active=True,
        timestamp=timezone.now() - timedelta(minutes=45)  # 45 minutes ago
    )
    print(f"✅ Created old location: {old_location.timestamp}")
    
    print("\n🧪 Now test the offline logic:")
    print("python manage.py shell -c 'from test_offline_logic import test_offline_logic; test_offline_logic()'")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "create":
        create_test_data()
    else:
        test_offline_logic() 