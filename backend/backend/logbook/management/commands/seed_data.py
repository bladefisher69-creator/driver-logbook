from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from logbook.models import Driver, Trip, FuelLog
import random
from decimal import Decimal, ROUND_HALF_UP


class Command(BaseCommand):
    help = 'Seeds the database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database...')

        admin, created = Driver.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@driverlogbook.com',
                'password': 'admin123',
                'first_name': 'Admin',
                'last_name': 'User',
                'license_number': 'ADM001',
                'is_admin': True
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
        self.stdout.write(self.style.SUCCESS(f'Created admin: {admin.username}'))

        drivers_data = [
            {'username': 'john_doe', 'first_name': 'John', 'last_name': 'Doe', 'license': 'DL123456'},
            {'username': 'jane_smith', 'first_name': 'Jane', 'last_name': 'Smith', 'license': 'DL789012'},
            {'username': 'mike_wilson', 'first_name': 'Mike', 'last_name': 'Wilson', 'license': 'DL345678'},
        ]

        drivers = []
        for driver_data in drivers_data:
            driver, created = Driver.objects.get_or_create(
                username=driver_data['username'],
                defaults={
                    'email': f"{driver_data['username']}@driverlogbook.com",
                    'first_name': driver_data['first_name'],
                    'last_name': driver_data['last_name'],
                    'license_number': driver_data['license'],
                    'phone': f'555-{random.randint(1000, 9999)}'
                }
            )
            if created:
                driver.set_password('driver123')
                driver.save()
            drivers.append(driver)
            self.stdout.write(self.style.SUCCESS(f'Created driver: {driver.username}'))

        cities = [
            ('New York, NY', 'Boston, MA', 215),
            ('Los Angeles, CA', 'San Francisco, CA', 382),
            ('Chicago, IL', 'Detroit, MI', 283),
            ('Houston, TX', 'Dallas, TX', 239),
            ('Miami, FL', 'Orlando, FL', 235),
        ]

        trip_count = 0
        for driver in drivers:
            for i in range(5):
                origin, destination, distance = random.choice(cities)
                start_time = timezone.now() - timedelta(days=random.randint(0, 7), hours=random.randint(0, 23))
                trip_duration = distance / 60  # approx hours
                end_time = start_time + timedelta(hours=trip_duration)

                trip = Trip.objects.create(
                    driver=driver,
                    vehicle_id=f'TRK{random.randint(100, 999)}',
                    origin=origin,
                    destination=destination,
                    distance=Decimal(distance).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                    start_time=start_time,
                    end_time=end_time,
                    status='completed'
                )
                trip_count += 1

                if i % 3 == 0:
                    fuel_amount = Decimal(str(random.uniform(50, 100))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    fuel_cost = Decimal(str(random.uniform(150, 300))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    odometer = Decimal(str(random.uniform(50000, 100000))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

                    FuelLog.objects.create(
                        driver=driver,
                        trip=trip,
                        fuel_type='diesel',
                        fuel_amount=fuel_amount,
                        fuel_cost=fuel_cost,
                        odometer_reading=odometer,
                        location=origin,
                        timestamp=start_time
                    )

        self.stdout.write(self.style.SUCCESS(f'Created {trip_count} trips'))
        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))
        self.stdout.write(self.style.WARNING('\nLogin credentials:'))
        self.stdout.write(self.style.WARNING('Admin - username: admin, password: admin123'))
        self.stdout.write(self.style.WARNING('Driver - username: john_doe, password: driver123'))
