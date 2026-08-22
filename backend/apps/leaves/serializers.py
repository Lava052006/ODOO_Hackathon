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
        from datetime import datetime, date
        f_date = obj.from_date
        t_date = obj.to_date
        if isinstance(f_date, str):
            try:
                f_date = datetime.strptime(f_date, "%Y-%m-%d").date()
            except ValueError:
                pass
        if isinstance(t_date, str):
            try:
                t_date = datetime.strptime(t_date, "%Y-%m-%d").date()
            except ValueError:
                pass

        f_str = f_date.strftime('%d %b') if hasattr(f_date, 'strftime') else str(f_date)
        t_str = t_date.strftime('%d %b %Y') if hasattr(t_date, 'strftime') else str(t_date)
        return f"{f_str} – {t_str}" if f_date != t_date else t_str

    def get_applied(self, obj):
        if hasattr(obj.applied_at, 'strftime'):
            return obj.applied_at.strftime('%d %b')
        return 'today'
