from django.contrib import admin
from .models import Notification, NotificationPreference, ActivityEvent

# Customizing the Django Admin branding
admin.site.site_header = "ARIA HRMS Command Centre"
admin.site.site_title = "ARIA HR Admin"
admin.site.index_title = "Platform Administration"

@admin.register(ActivityEvent)
class ActivityEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'detail', 'time_text', 'tone')
    search_fields = ('title', 'detail')
    list_filter = ('tone',)
    
    # Make read-only for audit purposes
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'detail', 'time_text', 'is_read')
    search_fields = ('title', 'detail')
    list_filter = ('is_read', 'tone')

@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'push')
    search_fields = ('user__username', 'user__employee_id')
