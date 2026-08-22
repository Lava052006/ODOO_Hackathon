from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Document, OTPVerification

class DocumentInline(admin.TabularInline):
    model = Document
    extra = 1

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('employee_id', 'username', 'get_full_name', 'role', 'department', 'job_title', 'is_probation')
    list_filter = ('role', 'department', 'location', 'employment_type', 'is_probation', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'employee_id', 'email')
    ordering = ('employee_id',)
    inlines = [DocumentInline]

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'phone', 'birth_date', 'address', 'avatar_color', 'photo_url')}),
        ('HR & Job Details', {'fields': ('employee_id', 'role', 'department', 'job_title', 'manager', 'employment_type', 'joining_date', 'location', 'shift', 'is_probation')}),
        ('Emergency Contact', {'fields': ('emergency_contact', 'emergency_phone')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'uploaded_at', 'meta')
    search_fields = ('name', 'user__employee_id', 'user__first_name')
    list_filter = ('uploaded_at',)

@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ('email', 'code', 'created_at', 'is_verified')
    search_fields = ('email', 'code')
    list_filter = ('is_verified', 'created_at')
