from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from decimal import Decimal


class Driver(AbstractUser):
    license_number = models.CharField(max_length=50, unique=True)
    phone = models.CharField(max_length=20, blank=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Fix reverse accessor clash
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='driver_set',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='driver_set',
        blank=True
    )

    class Meta:
        db_table = 'drivers'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_full_name()} ({self.license_number})"

    @property
    def total_hours_8days(self):
        eight_days_ago = timezone.now() - timedelta(days=8)
        trips = self.trips.filter(status='completed', end_time__gte=eight_days_ago)
        total_hours = sum(trip.total_trip_hours for trip in trips)
        return round(total_hours, 2)

    @property
    def remaining_hours_8days(self):
        limit = getattr(settings, 'HOURS_LIMIT_8_DAYS', 70)
        return round(max(0, limit - self.total_hours_8days), 2)

    @property
    def compliance_status(self):
        used = self.total_hours_8days
        limit = getattr(settings, 'HOURS_LIMIT_8_DAYS', 70)
        if used >= limit:
            return 'exceeded'
        elif used >= limit * 0.9:
            return 'warning'
        return 'compliant'

    @property
    def miles_since_last_fuel(self):
        last_fuel = self.fuel_logs.order_by('-timestamp').first()
        if not last_fuel:
            total_miles = self.trips.filter(status='completed').aggregate(
                total=models.Sum('distance')
            )['total'] or Decimal('0.00')
            return round(total_miles, 2)

        trips_after_fuel = self.trips.filter(status='completed', end_time__gt=last_fuel.timestamp)
        miles = trips_after_fuel.aggregate(total=models.Sum('distance'))['total'] or Decimal('0.00')
        return round(miles, 2)

    @property
    def needs_refuel(self):
        limit = getattr(settings, 'REFUEL_MILES_LIMIT', 500)
        return self.miles_since_last_fuel >= limit


class Trip(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='trips')
    vehicle_id = models.CharField(max_length=50)
    origin = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    pickup_lat = models.FloatField(null=True, blank=True)
    pickup_lng = models.FloatField(null=True, blank=True)
    destination_lat = models.FloatField(null=True, blank=True)
    destination_lng = models.FloatField(null=True, blank=True)
    distance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    pickup_time = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal(str(getattr(settings, 'PICKUP_TIME_HOURS', 0.5)))
    )
    dropoff_time = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal(str(getattr(settings, 'DROPOFF_TIME_HOURS', 0.5)))
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'trips'
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['driver', 'status']),
            models.Index(fields=['start_time']),
        ]

    def __str__(self):
        return f"Trip {self.id}: {self.origin} to {self.destination}"

    @property
    def total_trip_hours(self):
        if not self.end_time:
            return Decimal('0.00')
        driving_time = Decimal((self.end_time - self.start_time).total_seconds() / 3600)
        return round(driving_time + self.pickup_time + self.dropoff_time, 2)

    @property
    def driver_hours_after_trip(self):
        return round(self.driver.total_hours_8days + self.total_trip_hours, 2)

    def validate_compliance(self):
        errors = []
        if self.driver.needs_refuel:
            errors.append(f"Refueling required. Miles since last fuel: {self.driver.miles_since_last_fuel}")
        if self.status == 'completed' and self.end_time:
            projected_hours = self.driver_hours_after_trip
            limit = getattr(settings, 'HOURS_LIMIT_8_DAYS', 70)
            if projected_hours > limit:
                errors.append(
                    f"Trip would exceed {limit}-hour limit. "
                    f"Current: {self.driver.total_hours_8days} hrs, "
                    f"After trip: {projected_hours} hrs"
                )
        return errors


class FuelLog(models.Model):
    FUEL_TYPE_CHOICES = [
        ('diesel', 'Diesel'),
        ('gasoline', 'Gasoline'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid'),
    ]

    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='fuel_logs')
    trip = models.ForeignKey(Trip, on_delete=models.SET_NULL, null=True, blank=True, related_name='fuel_logs')
    fuel_type = models.CharField(max_length=20, choices=FUEL_TYPE_CHOICES, default='diesel')
    fuel_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Gallons"
    )
    fuel_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    odometer_reading = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))]
    )
    location = models.CharField(max_length=255)
    timestamp = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'fuel_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['driver', 'timestamp']),
        ]

    def __str__(self):
        return f"Fuel Log {self.id}: {self.fuel_amount} gal at {self.location}"

    @property
    def cost_per_gallon(self):
        if self.fuel_amount == 0:
            return Decimal('0.00')
        return round(self.fuel_cost / self.fuel_amount, 2)


class ComplianceReport(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='compliance_reports')
    date_start = models.DateField()
    date_end = models.DateField()
    total_hours = models.DecimalField(max_digits=6, decimal_places=2)
    total_miles = models.DecimalField(max_digits=10, decimal_places=2)
    trip_count = models.IntegerField(default=0)
    limit_exceeded = models.BooleanField(default=False)
    refuel_violations = models.IntegerField(default=0)
    notes = models.TextField(blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'compliance_reports'
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['driver', 'date_start', 'date_end']),
        ]

    def __str__(self):
        return f"Compliance Report for {self.driver.get_full_name()} ({self.date_start} to {self.date_end})"


class LocationUpdate(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='locations')
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='location_updates')
    lat = models.FloatField()
    lng = models.FloatField()
    accuracy = models.FloatField(null=True, blank=True)
    speed = models.FloatField(null=True, blank=True)
    recorded_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'location_updates'
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['trip', 'recorded_at']),
            models.Index(fields=['driver', 'recorded_at']),
        ]

    def __str__(self):
        return f"LocationUpdate {self.id} for Trip {self.trip_id} at {self.recorded_at}"
