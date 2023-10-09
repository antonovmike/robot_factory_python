# from django.shortcuts import render
from rest_framework import generics
from .models import Robot
from .serializers import RobotSerializer


class RobotCreateView(generics.CreateAPIView):
    queryset = Robot.objects.all()
    serializer_class = RobotSerializer
