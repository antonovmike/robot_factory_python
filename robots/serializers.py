import re

from django.utils import timezone
from rest_framework import serializers

from .models import Robot


class RobotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Robot
        fields = '__all__'
        read_only_fields = ('serial',)

    def validate(self, data):
        # Check that the first character of model and version is a letter and the second is a number
        pattern = r'^[A-Za-z][0-9]$'
        if not re.match(pattern, data['model']):
            raise serializers.ValidationError("Invalid model. First character must be a letter, second character must be a number.")
        if not re.match(pattern, data['version']):
            raise serializers.ValidationError("Invalid version. First character must be a letter, second character must be a number.")
        # Check that the creation date does not exceed the current date, if present
        if 'created' in data and data['created'] > timezone.now():
            raise serializers.ValidationError("Creation date should not be in future.")
        return data
