from django.urls import path
from .views import (
    RegisterEmployeeView,
    AttendanceView,
    OfficeLocationView,
    GetEmployeeByID,
    AdminAttendanceLogsView,
    analyze_face
)

from .views import EmployeeListView  # ⬅️ Import the new view

urlpatterns = [
    path('register-employee/', RegisterEmployeeView.as_view(), name='register-employee'),
    path('attendance/', AttendanceView.as_view()),
    path('set-office-location/', OfficeLocationView.as_view()),
    path('office-locations/', OfficeLocationView.as_view()),
    path('employees/<str:employee_id>/', GetEmployeeByID.as_view()),
    path('admin-attendance-logs/', AdminAttendanceLogsView.as_view(), name='admin-logs'),

    # ✅ NEW ROUTE to list all employees
    path('employees/', EmployeeListView.as_view(), name='employee-list'),
     path('analyze-face/', analyze_face, name='analyze_face'),  # ✅ register here
]
