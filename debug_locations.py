#!/usr/bin/env python3
"""
Debug script to check location data in database
"""
import os
import django
import sys

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'employeemanagement.settings')
django.setup()

from employees.models import EmployeeLocation, Employee
from django.utils import timezone
from datetime import timedelta

def debug_locations():
    print("🔍 Debugging Location Data...")
    print("=" * 50)
    
    # Get all employee locations
    all_locations = EmployeeLocation.objects.all().order_by('-timestamp')
    print(f"📊 Total location records: {all_locations.count()}")
    
    if all_locations.count() > 0:
        print("\n📍 All Location Records:")
        for loc in all_locations:
            print(f"  - {loc.employee.name} ({loc.employee.employee_id}): {loc.latitude}, {loc.longitude}")
            print(f"    Distance: {loc.distance_from_office}m, In Radius: {loc.is_in_office_radius}")
            print(f"    Active: {loc.is_active}, Timestamp: {loc.timestamp}")
            print(f"    Age: {timezone.now() - loc.timestamp}")
            print()
    
    # Check active locations (last 5 minutes)
    five_minutes_ago = timezone.now() - timedelta(minutes=5)
    active_locations = EmployeeLocation.objects.filter(
        is_active=True,
        timestamp__gte=five_minutes_ago
    )
    print(f"📊 Active locations (last 5 minutes): {active_locations.count()}")
    
    if active_locations.count() > 0:
        print("\n📍 Active Location Records:")
        for loc in active_locations:
            print(f"  - {loc.employee.name} ({loc.employee.employee_id}): {loc.latitude}, {loc.longitude}")
            print(f"    Distance: {loc.distance_from_office}m, In Radius: {loc.is_in_office_radius}")
            print(f"    Timestamp: {loc.timestamp}")
            print()
    
    # Check all employees
    employees = Employee.objects.all()
    print(f"📊 Total employees: {employees.count()}")
    for emp in employees:
        print(f"  - {emp.name} (ID: {emp.employee_id})")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    debug_locations() 