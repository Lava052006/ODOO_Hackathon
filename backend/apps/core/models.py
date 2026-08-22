from django.db import models
from django.conf import settings

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    title = models.CharField(max_length=255)
    detail = models.CharField(max_length=255)
    time_text = models.CharField(max_length=50, default='Just now')
    icon = models.CharField(max_length=50, default='bell')
    tone = models.CharField(max_length=50, blank=True, default='')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({'Read' if self.is_read else 'Unread'})"


class NotificationPreference(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='notification_preferences')
    key = models.CharField(max_length=50)
    label = models.CharField(max_length=100)
    detail = models.CharField(max_length=255)
    email = models.BooleanField(default=True)
    push = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.label} (Email: {self.email}, Push: {self.push})"


class ActivityEvent(models.Model):
    title = models.CharField(max_length=255)
    detail = models.CharField(max_length=255)
    time_text = models.CharField(max_length=50, default='2m')
    icon = models.CharField(max_length=50, default='spark')
    tone = models.CharField(max_length=50, default='mint')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.time_text}"

class MediaAsset(models.Model):
    title = models.CharField(max_length=255)
    media_file = models.FileField(upload_to='minio_media/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
