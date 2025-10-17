from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    DriverRegistrationView,
    DriverViewSet,
    TripViewSet,
    FuelLogViewSet,
    ComplianceReportViewSet,
    DashboardStatsView
)
from .views_route import RouteView
from .views_eld import ELDGenerateView
from .views import ReverseGeocodeView
from .views import AddressSearchView

router = DefaultRouter()
router.register(r'drivers', DriverViewSet, basename='driver')
router.register(r'trips', TripViewSet, basename='trip')
router.register(r'fuel-logs', FuelLogViewSet, basename='fuellog')
router.register(r'compliance-reports', ComplianceReportViewSet, basename='compliancereport')

urlpatterns = [
    path('auth/register/', DriverRegistrationView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('', include(router.urls)),
    path('route/', RouteView.as_view(), name='api-route'),
    path('eld/generate/', ELDGenerateView.as_view(), name='api-eld-generate'),
    path('search/reverse/', ReverseGeocodeView.as_view(), name='api-search-reverse'),
    path('search/address/', AddressSearchView.as_view(), name='api-search-address'),
]
