from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import signin_view, signup_view, verify_otp_view, me_view, logout_view, EmployeeViewSet

router = DefaultRouter()
router.register(r'employees', EmployeeViewSet, basename='employee')

urlpatterns = [
    path('auth/signin/', signin_view, name='signin'),
    path('auth/signup/', signup_view, name='signup'),
    path('auth/verify/', verify_otp_view, name='verify_otp'),
    path('auth/me/', me_view, name='me'),
    path('auth/logout/', logout_view, name='logout'),
    path('', include(router.urls)),
]
