from django.test import TestCase

# Create your tests here.
from django.test import Client
from django.urls import reverse

from .models import Robot
from customers.models import Customer
from orders.models import Order
from robots.views import check_robot_exists
from robots.views import notify_customer

import datetime
import json
import os


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
        

class RobotAvailabilityTestCase(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(email='test@example.com')
        self.robot_model = 'R2'
        self.robot_version = 'D2'

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
    def setUp(self):
        self.customer = Customer.objects.create(email='test@example.com')
        self.robot = Robot.objects.create(serial='R2-D2', model='R2', version='D2', created=datetime.datetime.now())
        self.order = Order.objects.create(customer=self.customer, robot_serial=self.robot.serial)

    def test_notify_customer(self):
        notify_customer(self.robot)
        self.assertTrue(os.path.isfile(f'email_{self.customer}_{datetime.datetime.now().strftime("%Y-%m-%d")}.txt'))
