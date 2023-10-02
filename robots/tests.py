from django.test import TestCase

# Create your tests here.
from django.test import Client
from django.urls import reverse
from django.utils.crypto import get_random_string

from datetime import datetime, timedelta
from random import randint

from .models import Robot

import json


class BaseTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.url = reverse('create_robot')
        cls.url_create_robot = reverse('create_robot')


class RobotTest(BaseTest):
    def generate_data(self):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=10)
        random_seconds = randint(0, int((end_date - start_date).total_seconds()))
        random_date = start_date + timedelta(seconds=random_seconds)
        return {
            "model": get_random_string(length=2, allowed_chars='ABCDEFGHIJKLMNOT123456789'),
            "version": get_random_string(length=2, allowed_chars='ABCDEFGHIJKLMNOT123456789'),
            "created": random_date.strftime("%Y-%m-%d %H:%M:%S")
        }
        
    def test_create_robot_status_code(self):
        data = self.generate_data()
        response = self.client.post(self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_create_robot_object_count(self):
        initial_count = Robot.objects.count()
        data = self.generate_data()
        response = self.client.post(self.url_create_robot, json.dumps(data), content_type='application/json')
        assert response.status_code == 200
        assert Robot.objects.count() == initial_count + 1

    def test_create_robot_model(self):
        data = self.generate_data()
        model = data.get("model")
        version = data.get("version")
        response = self.client.post(self.url_create_robot, json.dumps(data), content_type='application/json')
        assert response.status_code == 200
        robot = Robot.objects.get(model=model, version=version)
        assert robot is not None


class RobotViewTest(TestCase):
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

    # def test_download_report(self):
    #     url = reverse('download_report')
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response['Content-Disposition'], 'attachment; filename=robots_report.xlsx')
    #     self.assertEqual(response['Content-Type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
