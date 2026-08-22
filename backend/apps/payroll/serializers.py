from rest_framework import serializers
from .models import SalaryStructure, PayrollRun

class SalaryStructureSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    initials = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    employee_db_id = serializers.IntegerField(source='employee.id', read_only=True)
    role = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()
    gross = serializers.ReadOnlyField()
    net = serializers.ReadOnlyField()

    class Meta:
        model = SalaryStructure
        fields = [
            'id', 'employee_db_id', 'name', 'initials', 'role', 'color',
            'basic', 'hra', 'special', 'other', 'deductions',
            'gross', 'net'
        ]

    def get_id(self, obj):
        return obj.employee.employee_id

    def get_name(self, obj):
        return obj.employee.get_full_name() or obj.employee.username

    def get_initials(self, obj):
        name = self.get_name(obj)
        return "".join([part[0] for part in name.split() if part])

    def get_role(self, obj):
        return getattr(obj.employee, 'job_title', 'Software Engineer')

    def get_color(self, obj):
        return getattr(obj.employee, 'avatar_color', 'teal')


class PayrollRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollRun
        fields = '__all__'
