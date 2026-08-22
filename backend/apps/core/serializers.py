from rest_framework import serializers
from .models import Notification, NotificationPreference, ActivityEvent

class NotificationSerializer(serializers.ModelSerializer):
    time = serializers.CharField(source='time_text')
    read = serializers.BooleanField(source='is_read')

    class Meta:
        model = Notification
        fields = ['id', 'title', 'detail', 'time', 'icon', 'tone', 'read']

class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = ['id', 'key', 'label', 'detail', 'email', 'push']

class ActivityEventSerializer(serializers.ModelSerializer):
    time = serializers.CharField(source='time_text')

    class Meta:
        model = ActivityEvent
        fields = ['id', 'title', 'detail', 'time', 'icon', 'tone']
