from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import Driver, Trip, FuelLog, ComplianceReport
from .models import LocationUpdate


class DriverRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Driver
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name', 'license_number', 'phone']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        driver = Driver.objects.create(**validated_data)
        driver.set_password(password)
        driver.save()
        return driver


class DriverSerializer(serializers.ModelSerializer):
    total_hours_8days = serializers.ReadOnlyField()
    remaining_hours_8days = serializers.ReadOnlyField()
    compliance_status = serializers.ReadOnlyField()
    miles_since_last_fuel = serializers.ReadOnlyField()
    needs_refuel = serializers.ReadOnlyField()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Driver
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'license_number', 'phone', 'is_admin', 'total_hours_8days',
            'remaining_hours_8days', 'compliance_status', 'miles_since_last_fuel',
            'needs_refuel', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_full_name(self, obj):
        return obj.get_full_name()


class DriverUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = ['first_name', 'last_name', 'email', 'phone']


class TripSerializer(serializers.ModelSerializer):
    total_trip_hours = serializers.ReadOnlyField()
    driver_hours_after_trip = serializers.ReadOnlyField()
    driver_name = serializers.CharField(source='driver.get_full_name', read_only=True)
    compliance_errors = serializers.SerializerMethodField()

    class Meta:
        model = Trip
        fields = [
            'id', 'driver', 'driver_name', 'vehicle_id', 'origin', 'destination',
            'pickup_lat', 'pickup_lng', 'destination_lat', 'destination_lng',
            'distance', 'start_time', 'end_time', 'pickup_time', 'dropoff_time',
            'status', 'notes', 'total_trip_hours', 'driver_hours_after_trip',
            'compliance_errors', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_compliance_errors(self, obj):
        return obj.validate_compliance()

    def validate(self, attrs):
        if attrs.get('end_time') and attrs.get('start_time'):
            if attrs['end_time'] < attrs['start_time']:
                raise serializers.ValidationError({"end_time": "End time must be after start time."})

        if attrs.get('status') == 'completed':
            trip = Trip(**attrs)
            trip.driver = attrs.get('driver', self.instance.driver if self.instance else None)
            errors = trip.validate_compliance()
            if errors:
                raise serializers.ValidationError({"compliance": errors})

        return attrs


class TripCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = [
            'vehicle_id', 'origin', 'destination', 'distance',
            'start_time', 'pickup_time', 'dropoff_time', 'notes'
        ]

    def validate(self, attrs):
        driver = self.context['request'].user
        if driver.needs_refuel:
            raise serializers.ValidationError({
                "refuel": f"Refueling required before starting new trip. "
                          f"Miles since last fuel: {driver.miles_since_last_fuel}"
            })
        return attrs

    def create(self, validated_data):
        validated_data['driver'] = self.context['request'].user
        validated_data['status'] = 'in_progress'
        return super().create(validated_data)


class TripLocationSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    lat = serializers.FloatField(required=False)
    lng = serializers.FloatField(required=False)

    def validate(self, attrs):
        lat = attrs.get('lat')
        lng = attrs.get('lng')
        if (lat is None) ^ (lng is None):
            raise serializers.ValidationError({'lat_lng': 'Both lat and lng must be provided together.'})
        return attrs


class FuelLogSerializer(serializers.ModelSerializer):
    cost_per_gallon = serializers.ReadOnlyField()
    driver_name = serializers.CharField(source='driver.get_full_name', read_only=True)

    class Meta:
        model = FuelLog
        fields = [
            'id', 'driver', 'driver_name', 'trip', 'fuel_type', 'fuel_amount',
            'fuel_cost', 'cost_per_gallon', 'odometer_reading', 'location',
            'timestamp', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class FuelLogCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FuelLog
        fields = [
            'fuel_type', 'fuel_amount', 'fuel_cost', 'odometer_reading',
            'location', 'timestamp', 'notes', 'trip'
        ]

    def create(self, validated_data):
        validated_data['driver'] = self.context['request'].user
        return super().create(validated_data)


class ComplianceReportSerializer(serializers.ModelSerializer):
    driver_name = serializers.CharField(source='driver.get_full_name', read_only=True)

    class Meta:
        model = ComplianceReport
        fields = [
            'id', 'driver', 'driver_name', 'date_start', 'date_end',
            'total_hours', 'total_miles', 'trip_count', 'limit_exceeded',
            'refuel_violations', 'notes', 'generated_at'
        ]
        read_only_fields = ['id', 'generated_at']


class DashboardStatsSerializer(serializers.Serializer):
    total_drivers = serializers.IntegerField()
    active_trips = serializers.IntegerField()
    completed_trips_today = serializers.IntegerField()
    compliance_violations = serializers.IntegerField()
    drivers_needing_refuel = serializers.IntegerField()


class LocationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationUpdate
        fields = ['id', 'trip', 'driver', 'lat', 'lng', 'accuracy', 'speed', 'recorded_at', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate(self, attrs):
        if attrs.get('trip') and attrs.get('driver'):
            if attrs['trip'].driver_id != attrs['driver'].id:
                raise serializers.ValidationError({'driver': 'Driver does not match trip driver.'})
        return attrs
