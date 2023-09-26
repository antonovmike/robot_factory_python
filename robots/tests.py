import json

from django.test import TestCase

# Create your tests here.
from rest_framework.test import APIClient, APITestCase
# from django.urls import reverse
from .models import Robot
# from .serializers import RobotSerializer


class RobotTestCase(TestCase):
    def setup(self):
        self.client = APIClient()
        self.robot_data = {"model": "R2", "version": "D2", "created": "2022-12-31 23:59:59"}

    def test_api_can_create_a_robot(self):
        response = self.client.post('/robots/', data=json.dumps(self.robot_data), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_api_can_get_a_robot(self):
        # response = self.client.post('/robots/', data=json.dumps(self.robot_data), content_type='application/json')
        robot = Robot.objects.get()
        response = self.client.get(f'/robots/{robot.id}/')
        self.assertEqual(response.status_code, 200)
