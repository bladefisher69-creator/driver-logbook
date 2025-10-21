from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Driver Logbook API",
        default_version='v1',
        description="API for Driver Logbook Management System",
        contact=openapi.Contact(email="admin@driverlogbook.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# 👇 Add a simple root route
def home(request):
    return JsonResponse({
        "message": "Driver Logbook Backend is running ✅",
        "docs": "/swagger/",
        "health": "/healthz",
        "api": "/api/"
    })

urlpatterns = [
    path('', home),  # <--- This handles the root URL
    path('admin/', admin.site.urls),
    path('api/', include('logbook.urls')),
    path('healthz', lambda request: JsonResponse({'status': 'ok'})),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
