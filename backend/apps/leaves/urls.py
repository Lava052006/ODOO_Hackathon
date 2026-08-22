from django.urls import path
from .views import leaves_dashboard_view, submit_leave_view, resolve_leave_view

urlpatterns = [
    path('', leaves_dashboard_view, name='leaves_dashboard'),
    path('submit/', submit_leave_view, name='leaves_submit'),
    path('<int:pk>/decision/', resolve_leave_view, name='leaves_decision'),
]
