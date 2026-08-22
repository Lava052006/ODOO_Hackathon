from rest_framework import serializers
from .models import AttendanceRecord

class AttendanceRecordSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    initials = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()
    employeeId = serializers.CharField(source='employee.employee_id', read_only=True)
    in_time = serializers.CharField(source='check_in')
    out_time = serializers.CharField(source='check_out')
    hours = serializers.CharField(source='work_hours')

    class Meta:
        model = AttendanceRecord
        fields = [
            'id', 'name', 'initials', 'color', 'employeeId',
            'status', 'tone', 'in_time', 'out_time', 'hours',
            'location', 'issue', 'is_exception', 'exception_time', 'date'
        ]

    def get_name(self, obj):
        return obj.employee.get_full_name() or obj.employee.username

    def get_initials(self, obj):
        name = self.get_name(obj)
        return "".join([part[0] for part in name.split() if part])

    def get_color(self, obj):
        return getattr(obj.employee, 'avatar_color', 'teal')
