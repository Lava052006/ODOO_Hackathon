from django.contrib import admin
from .models import LeaveRequest

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('employee', 'leave_type', 'from_date', 'to_date', 'status', 'team_coverage')
    list_filter = ('status', 'leave_type', 'from_date')
    search_fields = ('employee__first_name', 'employee__last_name', 'employee__employee_id', 'reason')
    actions = ['approve_leaves', 'reject_leaves']

    @admin.action(description='Approve selected leaves')
    def approve_leaves(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f'{updated} leave requests were successfully approved.')

    @admin.action(description='Reject selected leaves')
    def reject_leaves(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} leave requests were successfully rejected.')
