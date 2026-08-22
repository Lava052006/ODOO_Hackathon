from django.contrib import admin
from .models import SalaryStructure, PayrollRun

@admin.register(SalaryStructure)
class SalaryStructureAdmin(admin.ModelAdmin):
    list_display = ('employee', 'basic', 'hra', 'special', 'other', 'deductions', 'gross_salary')
    search_fields = ('employee__first_name', 'employee__last_name', 'employee__employee_id')

    def gross_salary(self, obj):
        return obj.basic + obj.hra + obj.special + obj.other
    gross_salary.short_description = 'Gross Earnings'

@admin.register(PayrollRun)
class PayrollRunAdmin(admin.ModelAdmin):
    list_display = ('month', 'year', 'gross_amount_lakhs', 'is_closed', 'pay_date')
    list_filter = ('is_closed', 'year', 'month')
    list_editable = ('is_closed',)
