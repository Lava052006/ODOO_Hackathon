from django.urls import path
from .views import notifications_view, mark_all_notifications_read, save_preferences_view, command_centre_summary

urlpatterns = [
    path('notifications/', notifications_view, name='notifications'),
    path('notifications/mark-read/', mark_all_notifications_read, name='notifications_mark_read'),
    path('notifications/preferences/', save_preferences_view, name='notifications_preferences'),
    path('dashboard/command-centre/', command_centre_summary, name='command_centre_summary'),
]
