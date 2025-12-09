"""
URL configuration for employeemanagement project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def health_check(request):
    """Health check endpoint for mobile apps and monitoring"""
    return JsonResponse({
        'status': 'healthy',
        'message': 'Employee Attendance API is running',
        'version': '1.0.0',
        'cloudinary_configured': bool(settings.CLOUDINARY_CLOUD_NAME if hasattr(settings, 'CLOUDINARY_CLOUD_NAME') else False)
    })

def api_info(request):
    """API information endpoint"""
    return JsonResponse({
        'api_name': 'Employee Attendance System',
        'endpoints': {
            'health': '/api/health/',
            'employees': '/api/employees/',
            'attendance': '/api/attendance/',
            'locations': '/api/employee-locations/',
            'alerts': '/api/location-alerts/',
        },
        'documentation': 'Check the API endpoints for usage'
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('employees.urls')),
    path('api/health/', health_check, name='health_check'),
    path('api/info/', api_info, name='api_info'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

