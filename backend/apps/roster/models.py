from django.db import models
from django.conf import settings
from django.utils import timezone

class ShiftAssignment(models.Model):
    CODE_CHOICES = [
        ('M', 'Morning'),
        ('E', 'Evening'),
        ('N', 'Night'),
        ('L', 'Leave'),
        ('W', 'Weekly off'),
    ]

    TYPE_MAP = {
        'M': ('Morning', 'morning'),
        'E': ('Evening', 'evening'),
        'N': ('Night', 'night'),
        ('L'): ('Leave', 'leave'),
        ('W'): ('Weekly off', 'off'),
    }

    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shift_assignments')
    date = models.DateField(default=timezone.now)
    code = models.CharField(max_length=5, choices=CODE_CHOICES, default='M')
    label = models.CharField(max_length=50, default='Morning')
    shift_type = models.CharField(max_length=50, default='morning')

    class Meta:
        unique_together = ('employee', 'date')
        ordering = ['employee__first_name', 'date']

    def save(self, *args, **kwargs):
        if self.code in self.TYPE_MAP:
            self.label, self.shift_type = self.TYPE_MAP[self.code]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.date} ({self.code})"


class RosterState(models.Model):
    week_start = models.DateField(default=timezone.now)
    is_published = models.BooleanField(default=False)
    coverage_percent = models.IntegerField(default=98)

    def __str__(self):
        return f"Week of {self.week_start} - {'Published' if self.is_published else 'Draft'}"
