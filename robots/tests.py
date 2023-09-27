from django.test import TestCase

# Create your tests here.
# from django.urls import reverse
from .models import Robot
from django.test import Client, TestCase
from .models import Robot
import json


from django.utils.timezone import make_aware
from datetime import datetime

naive_datetime = datetime.strptime("2022-12-31 23:59:59", "%Y-%m-%d %H:%M:%S")
aware_datetime = make_aware(naive_datetime)


class RobotTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.robot_data = {"model": "R2", "version": "D2", "created": aware_datetime.isoformat()}

    def test_api_can_create_a_robot(self):
        response = self.client.post('/robots/', data=json.dumps(self.robot_data), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_api_can_get_a_robot(self):
        response = self.client.post('/robots/', data=json.dumps(self.robot_data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        robot = Robot.objects.get()
        response = self.client.get(f'/robots/{robot.id}/')
        self.assertEqual(response.status_code, 200)
