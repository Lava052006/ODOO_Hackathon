from rest_framework import serializers
from .models import LeaveRequest

class LeaveRequestSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()
    range = serializers.SerializerMethodField()
    applied = serializers.SerializerMethodField()

    class Meta:
        model = LeaveRequest
        fields = [
            'id', 'name', 'role', 'color', 'reason', 'range',
            'applied', 'status', 'leave_type', 'from_date', 'to_date',
            'admin_comment', 'team_coverage'
        ]

    def get_name(self, obj):
        return obj.employee.get_full_name() or obj.employee.username

    def get_role(self, obj):
        return getattr(obj.employee, 'job_title', 'Software Engineer')

    def get_color(self, obj):
        return getattr(obj.employee, 'avatar_color', 'teal')

    def get_range(self, obj):
        f = obj.from_date.strftime('%d %b')
        t = obj.to_date.strftime('%d %b %Y')
        return f"{f} – {t}" if obj.from_date != obj.to_date else obj.from_date.strftime('%d %b %Y')

    def get_applied(self, obj):
        return obj.applied_at.strftime('%d %b') if obj.applied_at else 'today'
