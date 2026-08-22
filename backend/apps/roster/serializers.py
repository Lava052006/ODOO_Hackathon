from rest_framework import serializers
from .models import ShiftAssignment, RosterState

class ShiftAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShiftAssignment
        fields = ['id', 'date', 'code', 'label', 'shift_type']
