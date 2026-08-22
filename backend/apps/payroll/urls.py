from django.urls import path
from .views import payroll_summary_view, update_salary_view, run_payroll_check_view, export_payroll_report

urlpatterns = [
    path('summary/', payroll_summary_view, name='payroll_summary'),
    path('employees/<str:employee_id>/', update_salary_view, name='update_salary'),
    path('run-check/', run_payroll_check_view, name='run_payroll_check'),
    path('export-report/', export_payroll_report, name='export_payroll_report'),
]
