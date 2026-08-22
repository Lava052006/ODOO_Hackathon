from django.db import models
from django.conf import settings

class SalaryStructure(models.Model):
    employee = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='salary_structure')
    basic = models.IntegerField(default=60000)
    hra = models.IntegerField(default=18000)
    special = models.IntegerField(default=12000)
    other = models.IntegerField(default=5000)
    deductions = models.IntegerField(default=12680)

    @property
    def gross(self):
        return self.basic + self.hra + self.special + self.other

    @property
    def net(self):
        return self.gross - self.deductions

    def __str__(self):
        return f"{self.employee.get_full_name()} - Gross: {self.gross}"


class PayrollRun(models.Model):
    month = models.CharField(max_length=20, default='August')
    year = models.IntegerField(default=2026)
    is_closed = models.BooleanField(default=False)
    gross_amount_lakhs = models.DecimalField(max_digits=6, decimal_places=1, default=84.6)
    readiness_percent = models.IntegerField(default=90)
    exceptions_count = models.IntegerField(default=12)
    pay_date = models.CharField(max_length=30, default='31 Aug 2026')

    def __str__(self):
        return f"Payroll {self.month} {self.year} ({'Closed' if self.is_closed else 'Open'})"
