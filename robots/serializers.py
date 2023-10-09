from rest_framework import serializers
from .models import Robot
from django.utils import timezone


class RobotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Robot
        fields = '__all__'
        read_only_fields = ('serial',)

    def validate(self, data):
        # Проверить что дата создания не превышает текущую дату
        if data['created'] > timezone.now():
            raise serializers.ValidationError("Creation date should not be in future.")
        return data
