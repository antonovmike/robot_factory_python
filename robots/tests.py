from django.test import TestCase

# Create your tests here.
from django.test import Client
from django.urls import reverse
from .models import Robot
from django.core.files.uploadedfile import TemporaryUploadedFile
import json

class RobotTest(TestCase):
    def setUp(self):
        self.client = Client()

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

    def test_download_report(self):
        url = reverse('download_report')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Disposition'], 'attachment; filename=robots_report.xlsx')
        self.assertEqual(response['Content-Type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        
