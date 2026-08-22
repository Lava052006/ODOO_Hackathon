from rest_framework import serializers
from .models import User, Document, OTPVerification
from apps.attendance.models import AttendanceRecord
from datetime import date

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'name', 'meta', 'file', 'uploaded_at']

class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    employeeId = serializers.CharField(source='employee_id')
    jobTitle = serializers.CharField(source='job_title', required=False)
    avatarColor = serializers.CharField(source='avatar_color', required=False)
    birthDate = serializers.DateField(source='birth_date', required=False, allow_null=True)
    emergencyContact = serializers.CharField(source='emergency_contact', required=False, allow_blank=True)
    emergencyPhone = serializers.CharField(source='emergency_phone', required=False, allow_blank=True)
    employmentType = serializers.CharField(source='employment_type', required=False)
    joiningDate = serializers.DateField(source='joining_date', required=False, allow_null=True)
    photoUrl = serializers.CharField(source='photo_url', required=False, allow_blank=True)
    isProbation = serializers.BooleanField(source='is_probation', required=False)
    status = serializers.SerializerMethodField()
    documents = DocumentSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'name', 'first_name', 'last_name',
            'employeeId', 'role', 'phone', 'birthDate', 'address',
            'emergencyContact', 'emergencyPhone', 'department', 'jobTitle',
            'manager', 'employmentType', 'joiningDate', 'location',
            'shift', 'avatarColor', 'photoUrl', 'isProbation', 'status', 'documents'
        ]

    def get_name(self, obj):
        full_name = f"{obj.first_name} {obj.last_name}".strip()
        return full_name if full_name else obj.username

    def get_status(self, obj):
        if hasattr(obj, 'today_attendance') and obj.today_attendance:
            return obj.today_attendance[0].status
        today = date(2026, 8, 22)
        att = AttendanceRecord.objects.filter(employee=obj, date=today).first()
        return att.status if att else 'Present'

class SigninSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    remember = serializers.BooleanField(default=True)

class SignupSerializer(serializers.Serializer):
    firstName = serializers.CharField()
    lastName = serializers.CharField()
    employeeId = serializers.CharField()
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=['admin', 'employee'], default='employee')
    password = serializers.CharField()

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField()
