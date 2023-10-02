from django.test import TestCase

# Create your tests here.
from django.test import Client
from django.urls import reverse
from django.utils.crypto import get_random_string

from .models import Robot

import json

class RobotTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.url = reverse('create_robot')

    def test_create_robot(self):
        url = reverse('create_robot')
        data = {
            "model": "R2",
            "version": "D2",
            "created": "2022-12-31 23:59:59"
        }
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Robot.objects.count(), 1)
        self.assertEqual(Robot.objects.get().model, 'R2')

    def test_robot_status_code(self):
        data = {
            "model": get_random_string(length=2, allowed_chars='ABCDEFGHIJKLMNOT123456789'),
            "version": get_random_string(length=2, allowed_chars='ABCDEFGHIJKLMNOT123456789'),
            "created": "2022-12-31 23:59:59"
        }
        response = self.client.post(self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
