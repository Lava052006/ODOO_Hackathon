from django.contrib import admin
from .models import ShiftAssignment, RosterState

@admin.register(ShiftAssignment)
class ShiftAssignmentAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'code')
    list_filter = ('date', 'code')
    list_editable = ('code',)
    search_fields = ('employee__first_name', 'employee__last_name', 'employee__employee_id')
    date_hierarchy = 'date'

@admin.register(RosterState)
class RosterStateAdmin(admin.ModelAdmin):
    list_display = ('week_start', 'is_published', 'coverage_percent')
    list_filter = ('is_published',)
    list_editable = ('is_published',)
