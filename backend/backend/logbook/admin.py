from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Driver, Trip, FuelLog, ComplianceReport


@admin.register(Driver)
class DriverAdmin(UserAdmin):
    list_display = ['username', 'email', 'license_number', 'is_admin', 'total_hours_8days', 'compliance_status']
    list_filter = ['is_admin', 'is_active', 'created_at']
    search_fields = ['username', 'email', 'license_number', 'first_name', 'last_name']
    fieldsets = UserAdmin.fieldsets + (
        ('Driver Information', {'fields': ('license_number', 'phone', 'is_admin')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Driver Information', {'fields': ('license_number', 'phone', 'is_admin')}),
    )


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ['id', 'driver', 'origin', 'destination', 'distance', 'status', 'start_time', 'total_trip_hours']
    list_filter = ['status', 'start_time', 'driver']
    search_fields = ['origin', 'destination', 'vehicle_id', 'driver__username']
    date_hierarchy = 'start_time'
    readonly_fields = ['total_trip_hours', 'created_at', 'updated_at']


@admin.register(FuelLog)
class FuelLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'driver', 'fuel_type', 'fuel_amount', 'fuel_cost', 'location', 'timestamp']
    list_filter = ['fuel_type', 'timestamp', 'driver']
    search_fields = ['location', 'driver__username']
    date_hierarchy = 'timestamp'
    readonly_fields = ['cost_per_gallon', 'created_at']


@admin.register(ComplianceReport)
class ComplianceReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'driver', 'date_start', 'date_end', 'total_hours', 'limit_exceeded', 'refuel_violations']
    list_filter = ['limit_exceeded', 'date_start', 'driver']
    search_fields = ['driver__username']
    date_hierarchy = 'date_start'
    readonly_fields = ['generated_at']
