from django.test import TestCase

# Create your tests here.
from django.test import Client
from django.urls import reverse
from django.utils.crypto import get_random_string

from .models import Robot
from customers.models import Customer
from orders.models import Order
from robots.views import check_robot_exists
from robots.views import notify_customer

import datetime
import json
import os


class RobotTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.url = reverse('create_robot')
        
    def create_robot_status_code(self):
        data = {
            "model": get_random_string(length=2, allowed_chars='ABCDEFGHIJKLMNOT123456789'),
            "version": get_random_string(length=2, allowed_chars='ABCDEFGHIJKLMNOT123456789'),
            "created": "2022-12-31 23:59:59"
        }
        response = self.client.post(self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def create_robot_object_count(self):
        self.client.post(self.url, json.dumps(self.data), content_type='application/json')
        self.assertEqual(Robot.objects.count(), 1)

    def create_robot_model(self):
        self.client.post(self.url, json.dumps(self.data), content_type='application/json')
        self.assertEqual(Robot.objects.get().model, 'R2')


class RobotViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url_create_robot = reverse('create_robot')
        cls.url_download_report = reverse('download_report')

    def download_report_status_code(self):
        response = self.client.get(self.url_download_report)
        self.assertEqual(response.status_code, 200)

    def download_report_content_disposition(self):
        response = self.client.get(self.url_download_report)
        self.assertEqual(response['Content-Disposition'], 'attachment; filename=robots_report.xlsx')

    def download_report_content_type(self):
        response = self.client.get(self.url_download_report)
        self.assertEqual(response['Content-Type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        

class RobotAvailabilityTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.customer = Customer.objects.create(email='test@example.com')
        cls.robot_model = 'R2'
        cls.robot_version = 'D2'

    def test_robot_not_available(self):
        message = check_robot_exists(self.customer, self.robot_model, self.robot_version)
        self.assertEqual(message, f'Robot {self.robot_model}-{self.robot_version} is not available. Your order is added to the waiting list.')
        self.assertTrue(Order.objects.filter(customer=self.customer, robot_serial=f'{self.robot_model}-{self.robot_version}').exists())

    def test_robot_available(self):
        Robot.objects.create(serial='R2-D2', model=self.robot_model, version=self.robot_version, created=datetime.datetime.now())
        message = check_robot_exists(self.customer, self.robot_model, self.robot_version)
        self.assertEqual(message, f'Robot {self.robot_model}-{self.robot_version} is available.')
        self.assertFalse(Order.objects.filter(customer=self.customer, robot_serial=f'{self.robot_model}-{self.robot_version}').exists())


class NotificationTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.customer = Customer.objects.create(email='test@example.com')
        cls.robot = Robot.objects.create(serial='R2-D2', model='R2', version='D2', created=datetime.datetime.now())
        cls.order = Order.objects.create(customer=cls.customer, robot_serial=cls.robot.serial)

    def test_notify_customer(self):
        notify_customer(self.robot)
        self.assertTrue(os.path.isfile(f'email_{self.customer}_{datetime.datetime.now().strftime("%Y-%m-%d")}.txt'))
