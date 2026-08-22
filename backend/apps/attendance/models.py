from django.db import models
from django.conf import settings
from django.utils import timezone

class AttendanceRecord(models.Model):
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Half-day', 'Half-day'),
        ('On leave', 'On leave'),
        ('Late', 'Late'),
        ('Off', 'Off'),
        ('Absent', 'Absent'),
        ('Remote', 'Remote'),
    ]

    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Present')
    check_in = models.CharField(max_length=30, blank=True, default='—')
    check_out = models.CharField(max_length=30, blank=True, default='—')
    work_hours = models.CharField(max_length=30, blank=True, default='—')
    location = models.CharField(max_length=100, default='New Delhi')
    tone = models.CharField(max_length=30, default='protected')
    issue = models.CharField(max_length=255, blank=True, default='')
    is_exception = models.BooleanField(default=False)
    exception_time = models.CharField(max_length=50, blank=True, default='')

    class Meta:
        ordering = ['-date', 'employee__first_name']
        unique_together = ('employee', 'date')

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.date} ({self.status})"
