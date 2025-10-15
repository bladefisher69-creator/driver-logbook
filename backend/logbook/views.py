from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.utils import timezone
from django.db.models import Sum, Count, Q
from datetime import timedelta
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Driver, Trip, FuelLog, ComplianceReport
from .serializers import (
    DriverSerializer, DriverRegistrationSerializer, DriverUpdateSerializer,
    TripSerializer, TripCreateSerializer,
    FuelLogSerializer, FuelLogCreateSerializer,
    ComplianceReportSerializer, DashboardStatsSerializer
)
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin
from .serializers import TripLocationSerializer
import requests
import os
from django.core.cache import cache
from django.conf import settings
from django.http import JsonResponse
from time import time
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from math import radians, cos, sin, asin, sqrt
import logging

# simple in-memory rate limiter (per-process). For production use Redis or a proper rate-limiter.
_search_rate = {}

class AddressSearchView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        q = request.query_params.get('q')
        if not q:
            return Response({'error': 'q is required'}, status=status.HTTP_400_BAD_REQUEST)

        # basic per-ip rate limit: 5 reqs per 10 seconds
        ip = request.META.get('REMOTE_ADDR', 'anon')
        now = time()
        window = _search_rate.get(ip, [])
        window = [t for t in window if now - t < 10]
        if len(window) >= 5:
            return Response({'error': 'rate limit exceeded'}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        window.append(now)
        _search_rate[ip] = window

        cache_key = f"places:{q}"
        cached = cache.get(cache_key)
        if cached:
            return JsonResponse(cached, safe=False)

        provider = getattr(settings, 'MAP_PROVIDER', 'mapbox')
        if provider == 'mapbox':
            token = os.getenv('MAPBOX_TOKEN', '')
            url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{q}.json?access_token={token}&autocomplete=true&limit=7"
            try:
                r = requests.get(url, timeout=5)
                r.raise_for_status()
                body = r.json()
                results = []
                for feat in body.get('features', []):
                    center = feat.get('center', [])
                    lng = center[0] if len(center) > 0 else None
                    lat = center[1] if len(center) > 1 else None
                    results.append({
                        'id': feat.get('id'),
                        'place_name': feat.get('place_name'),
                        'address': feat.get('text'),
                        'lat': lat,
                        'lng': lng,
                        'raw': feat,
                    })
                cache.set(cache_key, results, 60)
                return JsonResponse(results, safe=False)
            except requests.RequestException:
                return Response({'error': 'geocoding provider error'}, status=status.HTTP_502_BAD_GATEWAY)

        if provider == 'google':
            key = os.getenv('GOOGLE_PLACES_API_KEY', '')
            # Use Places Autocomplete to get suggestions, then fetch place details for coordinates
            try:
                ac_url = 'https://maps.googleapis.com/maps/api/place/autocomplete/json'
                ac_params = {
                    'input': q,
                    'key': key,
                    'types': 'geocode',
                    'language': 'en',
                    'components': ''
                }
                ac_resp = requests.get(ac_url, params=ac_params, timeout=5)
                ac_resp.raise_for_status()
                ac_body = ac_resp.json()
                predictions = ac_body.get('predictions', [])[:7]
                results = []
                for pred in predictions:
                    pid = pred.get('place_id')
                    description = pred.get('description') or pred.get('structured_formatting', {}).get('main_text')
                    # Fetch details to get lat/lng
                    details_url = 'https://maps.googleapis.com/maps/api/place/details/json'
                    details_params = {'place_id': pid, 'key': key, 'fields': 'geometry,formatted_address,name'}
                    det_resp = requests.get(details_url, params=details_params, timeout=5)
                    det_resp.raise_for_status()
                    det_body = det_resp.json()
                    det_result = det_body.get('result', {})
                    geom = det_result.get('geometry', {}).get('location', {})
                    lat = geom.get('lat')
                    lng = geom.get('lng')
                    place_name = det_result.get('name') or description
                    address = det_result.get('formatted_address') or description
                    results.append({
                        'id': pid,
                        'place_name': place_name,
                        'address': address,
                        'lat': lat,
                        'lng': lng,
                        'raw': {'prediction': pred, 'details': det_result},
                    })

                cache.set(cache_key, results, 60)
                return JsonResponse(results, safe=False)
            except requests.RequestException:
                return Response({'error': 'geocoding provider error'}, status=status.HTTP_502_BAD_GATEWAY)

        return Response({'error': 'no provider configured'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DriverRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = DriverRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            driver = serializer.save()
            return Response({
                'message': 'Driver registered successfully',
                'driver': DriverSerializer(driver).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['username', 'email', 'license_number', 'first_name', 'last_name']
    ordering_fields = ['created_at', 'username', 'total_hours_8days']

    def get_queryset(self):
        if self.request.user.is_admin:
            return Driver.objects.all()
        return Driver.objects.filter(id=self.request.user.id)

    @action(detail=False, methods=['get'])
    def me(self, request):
        try:
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        except Exception as e:
            # Log full traceback to the server log so we can diagnose the root cause.
            logging.exception('Unhandled exception in DriverViewSet.me')
            # Return structured JSON so the frontend can surface a readable error.
            return Response({'error': 'internal server error', 'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        serializer = DriverUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(DriverSerializer(request.user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def compliance_status(self, request, pk=None):
        driver = self.get_object()
        return Response({
            'driver': DriverSerializer(driver).data,
            'total_hours_8days': driver.total_hours_8days,
            'remaining_hours': driver.remaining_hours_8days,
            'compliance_status': driver.compliance_status,
            'miles_since_last_fuel': driver.miles_since_last_fuel,
            'needs_refuel': driver.needs_refuel
        })


class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'driver']
    search_fields = ['origin', 'destination', 'vehicle_id']
    ordering_fields = ['start_time', 'distance', 'created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return TripCreateSerializer
        return TripSerializer

    def get_queryset(self):
        if self.request.user.is_admin:
            return Trip.objects.all()
        return Trip.objects.filter(driver=self.request.user)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        trip = self.get_object()

        if trip.status == 'completed':
            return Response(
                {'error': 'Trip is already completed'},
                status=status.HTTP_400_BAD_REQUEST
            )

        end_time = request.data.get('end_time', timezone.now())
        trip.end_time = end_time
        trip.status = 'completed'

        errors = trip.validate_compliance()
        if errors:
            return Response(
                {'compliance_errors': errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        trip.save()
        serializer = self.get_serializer(trip)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        trip = self.get_object()

        if trip.status == 'completed':
            return Response(
                {'error': 'Cannot cancel a completed trip'},
                status=status.HTTP_400_BAD_REQUEST
            )

        trip.status = 'cancelled'
        trip.save()
        serializer = self.get_serializer(trip)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def pickup(self, request, pk=None):
        """Patch pickup info: name, address, lat, lng"""
        trip = self.get_object()
        serializer = TripLocationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        # Set human-readable name/address if provided
        if 'name' in data and data.get('name'):
            trip.origin = data.get('name')
        if 'address' in data and data.get('address'):
            trip.origin = data.get('address')
        # Persist coordinates in dedicated fields
        if 'lat' in data and 'lng' in data and data.get('lat') is not None and data.get('lng') is not None:
            trip.pickup_lat = data.get('lat')
            trip.pickup_lng = data.get('lng')

        trip.save()
        return Response(self.get_serializer(trip).data)

    @action(detail=True, methods=['patch'])
    def destination(self, request, pk=None):
        """Patch destination info: name, address, lat, lng"""
        trip = self.get_object()
        serializer = TripLocationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        if 'name' in data and data.get('name'):
            trip.destination = data.get('name')
        if 'address' in data and data.get('address'):
            trip.destination = data.get('address')
        if 'lat' in data and 'lng' in data and data.get('lat') is not None and data.get('lng') is not None:
            trip.destination_lat = data.get('lat')
            trip.destination_lng = data.get('lng')

        trip.save()
        return Response(self.get_serializer(trip).data)

    @action(detail=True, methods=['post'])
    def location(self, request, pk=None):
        """Accept a location update and broadcast to trip group."""
        trip = self.get_object()
        driver = request.user

        # Basic auth/ownership check
        if trip.driver_id != driver.id and not request.user.is_admin:
            return Response({'error': 'Not authorized for this trip'}, status=status.HTTP_403_FORBIDDEN)

        lat = request.data.get('lat')
        lng = request.data.get('lng')
        accuracy = request.data.get('accuracy')
        speed = request.data.get('speed')
        recorded_at = request.data.get('recorded_at')

        if lat is None or lng is None:
            return Response({'error': 'lat and lng are required'}, status=status.HTTP_400_BAD_REQUEST)

        # simple rate limiting per driver (1 req/s)
        ip = request.META.get('REMOTE_ADDR', str(driver.id))
        last_ts = cache.get(f'loc_rate:{driver.id}')
        now = time()
        if last_ts and now - last_ts < 1.0:
            return Response({'error': 'rate limit exceeded'}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        cache.set(f'loc_rate:{driver.id}', now, 2)

        # Persist location
        loc = None
        try:
            from .models import LocationUpdate
            loc = LocationUpdate.objects.create(
                trip=trip,
                driver=driver,
                lat=float(lat),
                lng=float(lng),
                accuracy=float(accuracy) if accuracy is not None else None,
                speed=float(speed) if speed is not None else None,
                recorded_at=recorded_at if recorded_at is not None else timezone.now()
            )
        except Exception as e:
            return Response({'error': 'failed to save location', 'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Simple arrival detection (15 meters)
        def haversine(lat1, lon1, lat2, lon2):
            # convert decimal degrees to radians
            lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            r = 6371000  # Radius of earth in meters
            return c * r

        arrived = False
        if trip.destination_lat and trip.destination_lng:
            dist = haversine(float(lat), float(lng), float(trip.destination_lat), float(trip.destination_lng))
            if dist <= getattr(settings, 'ARRIVAL_RADIUS_METERS', 15):
                trip.status = 'completed'
                trip.end_time = timezone.now()
                trip.save()
                arrived = True

        # Broadcast via channels
        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"trip_{trip.id}",
                {
                    'type': 'location.update',
                    'trip_id': str(trip.id),
                    'lat': loc.lat,
                    'lng': loc.lng,
                    'accuracy': loc.accuracy,
                    'speed': loc.speed,
                    'recorded_at': loc.recorded_at.isoformat(),
                    'arrived': arrived,
                }
            )
        except Exception:
            # non-fatal; continue
            pass

        from .serializers import LocationUpdateSerializer
        return Response(LocationUpdateSerializer(loc).data, status=status.HTTP_201_CREATED)


class ReverseGeocodeView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        if not lat or not lng:
            return Response({'error': 'lat and lng are required'}, status=status.HTTP_400_BAD_REQUEST)

        key = f"reverse:{lat}:{lng}"
        cached = cache.get(key)
        if cached:
            return Response(cached)

        provider = getattr(settings, 'MAP_PROVIDER', 'mapbox')
        if provider == 'mapbox':
            token = os.getenv('MAPBOX_TOKEN', '')
            url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{lng},{lat}.json?access_token={token}&limit=1"
            try:
                r = requests.get(url, timeout=5)
                r.raise_for_status()
                body = r.json()
                if body.get('features'):
                    feat = body['features'][0]
                    result = {
                        'place_name': feat.get('place_name'),
                        'address': feat.get('text'),
                        'lat': float(lat),
                        'lng': float(lng),
                    }
                    cache.set(key, result, 60)
                    return Response(result)
            except requests.RequestException:
                return Response({'error': 'reverse geocode failed'}, status=status.HTTP_502_BAD_GATEWAY)

        if provider == 'google':
            key = os.getenv('GOOGLE_PLACES_API_KEY', '')
            try:
                geocode_url = 'https://maps.googleapis.com/maps/api/geocode/json'
                params = {'latlng': f"{lat},{lng}", 'key': key}
                r = requests.get(geocode_url, params=params, timeout=5)
                r.raise_for_status()
                body = r.json()
                results_list = body.get('results', [])
                if results_list:
                    first = results_list[0]
                    result = {
                        'place_name': first.get('formatted_address'),
                        'address': first.get('formatted_address'),
                        'lat': float(lat),
                        'lng': float(lng),
                    }
                    cache.set(key, result, 60)
                    return Response(result)
            except requests.RequestException:
                return Response({'error': 'reverse geocode failed'}, status=status.HTTP_502_BAD_GATEWAY)

        return Response({'error': 'no provider configured'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class FuelLogViewSet(viewsets.ModelViewSet):
    queryset = FuelLog.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['fuel_type', 'driver']
    search_fields = ['location']
    ordering_fields = ['timestamp', 'fuel_cost', 'created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return FuelLogCreateSerializer
        return FuelLogSerializer

    def get_queryset(self):
        if self.request.user.is_admin:
            return FuelLog.objects.all()
        return FuelLog.objects.filter(driver=self.request.user)


class ComplianceReportViewSet(viewsets.ModelViewSet):
    queryset = ComplianceReport.objects.all()
    serializer_class = ComplianceReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['driver', 'limit_exceeded']
    ordering_fields = ['generated_at', 'date_start']

    def get_queryset(self):
        if self.request.user.is_admin:
            return ComplianceReport.objects.all()
        return ComplianceReport.objects.filter(driver=self.request.user)

    @action(detail=False, methods=['post'])
    def generate(self, request):
        driver_id = request.data.get('driver_id')
        date_start = request.data.get('date_start')
        date_end = request.data.get('date_end')

        if not all([driver_id, date_start, date_end]):
            return Response(
                {'error': 'driver_id, date_start, and date_end are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            driver = Driver.objects.get(id=driver_id)
        except Driver.DoesNotExist:
            return Response(
                {'error': 'Driver not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        trips = Trip.objects.filter(
            driver=driver,
            status='completed',
            start_time__date__gte=date_start,
            start_time__date__lte=date_end
        )

        total_hours = sum(trip.total_trip_hours for trip in trips)
        total_miles = trips.aggregate(total=Sum('distance'))['total'] or 0
        trip_count = trips.count()
        limit_exceeded = total_hours > 70

        fuel_logs = FuelLog.objects.filter(
            driver=driver,
            timestamp__date__gte=date_start,
            timestamp__date__lte=date_end
        ).order_by('timestamp')

        refuel_violations = 0
        if fuel_logs.exists():
            for i in range(len(fuel_logs) - 1):
                trips_between = trips.filter(
                    end_time__gte=fuel_logs[i].timestamp,
                    end_time__lt=fuel_logs[i + 1].timestamp
                )
                miles_between = trips_between.aggregate(total=Sum('distance'))['total'] or 0
                if miles_between > 1000:
                    refuel_violations += 1

        report = ComplianceReport.objects.create(
            driver=driver,
            date_start=date_start,
            date_end=date_end,
            total_hours=total_hours,
            total_miles=total_miles,
            trip_count=trip_count,
            limit_exceeded=limit_exceeded,
            refuel_violations=refuel_violations
        )

        serializer = self.get_serializer(report)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DashboardStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not request.user.is_admin:
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )

        today = timezone.now().date()
        eight_days_ago = timezone.now() - timedelta(days=8)

        stats = {
            'total_drivers': Driver.objects.filter(is_active=True).count(),
            'active_trips': Trip.objects.filter(status='in_progress').count(),
            'completed_trips_today': Trip.objects.filter(
                status='completed',
                end_time__date=today
            ).count(),
            'compliance_violations': Driver.objects.filter(
                trips__status='completed',
                trips__end_time__gte=eight_days_ago
            ).annotate(
                total_hours=Sum('trips__end_time')
            ).filter(total_hours__gt=70).count(),
            'drivers_needing_refuel': sum(1 for driver in Driver.objects.all() if driver.needs_refuel)
        }

        serializer = DashboardStatsSerializer(stats)
        return Response(serializer.data)
