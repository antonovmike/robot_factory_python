from django.test import TestCase

# Create your tests here.
from django.test import Client
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.core import mail

from .models import Robot
from customers.models import Customer
from orders.models import Order
from robots.views import check_robot_exists
from robots.views import notify_customer

import datetime
import json
import os


class BaseTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.url = reverse('create_robot')
        cls.url_create_robot = reverse('create_robot')
        cls.url_download_report = reverse('download_report')
        cls.customer = Customer.objects.create(email='test@example.com')
        cls.robot_model = 'R2'
        cls.robot_version = 'D2'


class RobotTest(BaseTest):
    def generate_data(self):
        return {
            "model": get_random_string(length=2, allowed_chars='ABCDEFGHIJKLMNOT123456789'),
            "version": get_random_string(length=2, allowed_chars='ABCDEFGHIJKLMNOT123456789'),
            "created": "2022-12-31 23:59:59"
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


class RobotViewTest(BaseTest):
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


class RobotAvailabilityTestCase(BaseTest):
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


class EmailTest(TestCase):
    def test_send_email(self):
        # Отправляем письмо
        mail.send_mail('Subject here', 'Here is the message.',
            'from@example.com', ['to@example.com'],
            fail_silently=False)
        # Проверяем, что одно письмо было отправлено
        self.assertEqual(len(mail.outbox), 1)
        # Проверяем, что тема первого письма правильная
        self.assertEqual(mail.outbox[0].subject, 'Subject here')
