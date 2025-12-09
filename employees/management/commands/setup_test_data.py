from django.core.management.base import BaseCommand
from employees.models import OfficeLocation

class Command(BaseCommand):
    help = 'Setup test office locations for the face attendance app'

    def handle(self, *args, **options):
        # Create test office locations
        offices = [
            {
                'name': 'Main Office',
                'latitude': 37.7749,
                'longitude': -122.4194,
                'radius_meters': 100.0
            },
            {
                'name': 'Branch Office',
                'latitude': 37.7849,
                'longitude': -122.4094,
                'radius_meters': 150.0
            },
            {
                'name': 'Remote Office',
                'latitude': 37.7649,
                'longitude': -122.4294,
                'radius_meters': 200.0
            }
        ]

        for office_data in offices:
            office, created = OfficeLocation.objects.get_or_create(
                name=office_data['name'],
                defaults=office_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Created office: {office.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️ Office already exists: {office.name}')
                )

        self.stdout.write(
            self.style.SUCCESS('🎉 Test office locations setup complete!')
        ) 