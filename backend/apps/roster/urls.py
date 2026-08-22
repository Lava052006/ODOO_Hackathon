from django.urls import path
from .views import roster_dashboard_view, update_shift_view, publish_roster_view

urlpatterns = [
    path('', roster_dashboard_view, name='roster_dashboard'),
    path('update-shift/', update_shift_view, name='update_shift'),
    path('publish/', publish_roster_view, name='publish_roster'),
]
