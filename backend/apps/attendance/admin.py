from django.contrib import admin
from .models import AttendanceRecord

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'status', 'check_in', 'check_out', 'is_exception', 'issue')
    list_filter = ('date', 'status', 'is_exception', 'tone')
    list_editable = ('status', 'is_exception')
    search_fields = ('employee__first_name', 'employee__last_name', 'employee__employee_id', 'issue')
    date_hierarchy = 'date'
