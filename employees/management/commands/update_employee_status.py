from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from employees.models import Employee, EmployeeLocation, Attendance
from employees.views import check_employee_online_status

class Command(BaseCommand):
    help = 'Update employee online/offline status based on login and location activity'

    def handle(self, *args, **options):
        self.stdout.write("🔄 Starting employee status update...")
        
        employees = Employee.objects.all()
        updated_count = 0
        
        for employee in employees:
            # Check if employee should be marked as offline
            is_online = check_employee_online_status(employee)
            
            # Get the latest location record
            latest_location = EmployeeLocation.objects.filter(
                employee=employee
            ).order_by('-timestamp').first()
            
            if latest_location:
                # Update the is_active status based on online check
                if latest_location.is_active != is_online:
                    latest_location.is_active = is_online
                    latest_location.save()
                    updated_count += 1
                    
                    status = "online" if is_online else "offline"
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✅ Updated {employee.name} ({employee.employee_id}) to {status}"
                        )
                    )
                else:
                    status = "online" if is_online else "offline"
                    self.stdout.write(
                        f"ℹ️  {employee.name} ({employee.employee_id}) already {status}"
                    )
            else:
                # No location record exists, create one with offline status
                EmployeeLocation.objects.create(
                    employee=employee,
                    latitude=employee.office.latitude if employee.office else 0,
                    longitude=employee.office.longitude if employee.office else 0,
                    is_in_office_radius=False,
                    distance_from_office=0,
                    is_active=False,
                    timestamp=timezone.now()
                )
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(
                        f"⚠️  Created offline record for {employee.name} ({employee.employee_id}) - no previous location"
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Employee status update completed. Updated {updated_count} employees."
            )
        ) 