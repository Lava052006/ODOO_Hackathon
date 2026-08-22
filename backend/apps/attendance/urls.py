from django.urls import path
from .views import attendance_summary_view, toggle_checkin_view, employee_attendance_week, export_attendance_csv

urlpatterns = [
    path('summary/', attendance_summary_view, name='attendance_summary'),
    path('toggle-checkin/', toggle_checkin_view, name='attendance_toggle_checkin'),
    path('my-week/', employee_attendance_week, name='attendance_my_week'),
    path('export/', export_attendance_csv, name='attendance_export'),
]
