from django.urls import path
from . import views

urlpatterns = [
    path('register-employee/', views.RegisterEmployeeView.as_view(), name='register-employee'),
    path('employees/', views.EmployeeListView.as_view(), name='employee-list'),
    path('employees/<str:employee_id>/', views.GetEmployeeByID.as_view(), name='employee-detail'),
    path('attendance/', views.AttendanceView.as_view(), name='attendance'),
    path('office-locations/', views.OfficeLocationView.as_view(), name='office-locations'),
    path('admin-attendance-logs/', views.AdminAttendanceLogsView.as_view(), name='admin-attendance-logs'),
    path('employee-attendance-logs/<str:employee_id>/', views.EmployeeAttendanceLogsView.as_view(), name='employee-attendance-logs'),
    path('location-alerts/', views.location_alerts, name='location_alerts'),
    path('employee-locations/', views.employee_locations, name='employee_locations'),
    path('location-update/', views.location_update, name='location_update'),
    path('live-employee-locations/', views.live_employee_locations, name='live_employee_locations'),
    path('update-employee-status/', views.update_employee_status, name='update_employee_status'),
]
