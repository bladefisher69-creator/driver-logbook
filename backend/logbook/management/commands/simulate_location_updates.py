from django.core.management.base import BaseCommand
from django.utils import timezone
import time
import random

from logbook.models import Trip, LocationUpdate


class Command(BaseCommand):
    help = 'Simulate location updates for an active Trip. Usage: manage.py simulate_location_updates <trip_id> [count] [interval_seconds]'

    def add_arguments(self, parser):
        parser.add_argument('trip_id', type=int)
        parser.add_argument('--count', type=int, default=20)
        parser.add_argument('--interval', type=float, default=1.0)

    def handle(self, *args, **options):
        trip_id = options['trip_id']
        count = options['count']
        interval = options['interval']

        try:
            trip = Trip.objects.get(pk=trip_id)
        except Trip.DoesNotExist:
            self.stderr.write(self.style.ERROR(f'Trip {trip_id} does not exist'))
            return

        # If the trip has pickup/destination coords try to generate linearly spaced points between them
        if trip.pickup_lat and trip.pickup_lng and trip.destination_lat and trip.destination_lng:
            lat_start = trip.pickup_lat
            lon_start = trip.pickup_lng
            lat_end = trip.destination_lat
            lon_end = trip.destination_lng
        else:
            # Fallback: random walk near pickup coords or origin (0,0)
            lat_start = trip.pickup_lat or 0.0
            lon_start = trip.pickup_lng or 0.0
            lat_end = lat_start + 0.01 * random.random()
            lon_end = lon_start + 0.01 * random.random()

        self.stdout.write(self.style.SUCCESS(f'Simulating {count} updates for trip {trip_id} every {interval}s'))

        for i in range(count):
            t = i / max(1, count - 1)
            lat = lat_start + (lat_end - lat_start) * t + (random.random() - 0.5) * 0.0002
            lng = lon_start + (lon_end - lon_start) * t + (random.random() - 0.5) * 0.0002

            lu = LocationUpdate.objects.create(
                trip=trip,
                lat=lat,
                lng=lng,
                speed=random.uniform(0, 25),
                accuracy=random.uniform(3, 50),
                recorded_at=timezone.now(),
            )

            # Optionally echo the created update
            self.stdout.write(f'[{i+1}/{count}] {lu.lat:.6f},{lu.lng:.6f} at {lu.recorded_at.isoformat()}')

            # Broadcast via channels (if consumer listens for LocationUpdate creation) — in our code the Trip consumer listens to explicit posts
            time.sleep(interval)

        self.stdout.write(self.style.SUCCESS('Simulation complete'))
