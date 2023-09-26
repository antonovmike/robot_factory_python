from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import Robot
from .serializers import RobotSerializer

class RobotViewSet(viewsets.ModelViewSet):
    queryset = Robot.objects.all()
    serializer_class = RobotSerializer
