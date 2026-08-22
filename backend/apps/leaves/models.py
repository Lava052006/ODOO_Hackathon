from django.db import models
from django.conf import settings
from django.utils import timezone

class LeaveRequest(models.Model):
    TYPE_CHOICES = [
        ('Paid leave', 'Paid leave'),
        ('Sick leave', 'Sick leave'),
        ('Unpaid leave', 'Unpaid leave'),
        ('Work from home', 'Work from home'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='Paid leave')
    from_date = models.DateField(default=timezone.now)
    to_date = models.DateField(default=timezone.now)
    reason = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_comment = models.TextField(blank=True, default='')
    applied_at = models.DateTimeField(auto_now_add=True)
    team_coverage = models.CharField(max_length=20, default='92%')

    class Meta:
        ordering = ['-applied_at']

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.leave_type} ({self.status})"
