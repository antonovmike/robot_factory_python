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
        # Проверить, что первый символ model и version является буквой, а второй - цифрой
        pattern = r'^[A-Za-z][0-9]$'
        if not re.match(pattern, data['model']):
            raise serializers.ValidationError("Invalid model. First character must be a letter, second character must be a number.")
        if not re.match(pattern, data['version']):
            raise serializers.ValidationError("Invalid version. First character must be a letter, second character must be a number.")
        # Проверить что дата создания не превышает текущую дату
        if data['created'] > timezone.now():
            raise serializers.ValidationError("Creation date should not be in future.")
        return data
