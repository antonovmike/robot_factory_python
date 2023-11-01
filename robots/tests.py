import json
from django.core import mail
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient

from robots.models import Robot
from orders.models import Order
from customers.models import Customer
from robots.serializers import RobotSerializer


class RobotAPITestCase(TestCase):
    def setUp(self):
        # Создать клиент для отправки запросов
        self.client = APIClient()
        # Создать несколько роботов в базе данных
        self.robot1 = Robot.objects.create(model="A1", version="B2", created="2023-10-06 11:09:22")
        self.robot2 = Robot.objects.create(model="C3", version="D4", created="2023-10-07 12:10:23")
        # Получить URL для API-endpoint создания робота
        self.create_url = reverse('robot-create')

    def test_create_robot_success(self):
        data = {"model":"E5", "version":"F6", "created":"2023-10-08 11:11:24"}
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        robot = Robot.objects.get(model="E5")
        expected_data = RobotSerializer(robot).data
        self.assertEqual(response.data, expected_data)


    def test_create_robot_fail(self):
        # Подготовить невалидные данные для запроса (например, пустые или некорректные)
        data = {"model":"", "version":"G7", "created":"2023-10-09 11:12:25"}
        # Отправить POST-запрос с данными
        response = self.client.post(self.create_url, data, format='json')
        # Проверить, что статус-код ответа равен 400 (Bad Request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Проверить, что в ответе есть сообщение об ошибке валидации
        self.assertTrue('model' in response.data)
        self.assertEqual(response.data['model'], ['This field may not be blank.'])

    def test_validate_correct_data(self):
        # Корректные данные для теста
        data = {
            "model": "A1",
            "version": "B2",
            "created": timezone.now()
        }
        serializer = RobotSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_validate_future_created(self):
        # Некорректные данные для теста (дата создания в будущем)
        data = {
            "model": "A1",
            "version": "B2",
            "created": timezone.now() + timezone.timedelta(days=1)
        }
        serializer = RobotSerializer(data=data)
        # Проверить, что при валидации данных вызывается исключение ValidationError
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_validate_incorrect_model(self):
        # Некорректные данные для теста (неверный формат model)
        data = {
            "model": "11",
            "version": "B2",
            "created": timezone.now()
        }
        serializer = RobotSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_validate_incorrect_version(self):
        # Некорректные данные для теста (неверный формат version)
        data = {
            "model": "A1",
            "version": "BB",
            "created": timezone.now()
        }
        serializer = RobotSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_robot_report_view(self):
        now = timezone.now()
        Robot.objects.create(model="A1", version="B2", created=now)
        Robot.objects.create(model="A2", version="F3", created=now)
        Robot.objects.create(model="E2", version="R4", created=now)
        Robot.objects.create(model="E5", version="T1", created=now)
        Robot.objects.create(model="E8", version="W2", created=now)
        # Получить URL для API-endpoint создания робота
        report_url = reverse('robot-report')
        # Отправить GET-запрос к RobotReportView
        response = self.client.get(report_url)
        # Проверить, что статус-код ответа равен 200 (OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверить, что в ответе есть данные для каждой страницы
        content = list(response.streaming_content) # Преобразовать генератор в список
        self.assertTrue(b'A' in content[0]) # Проверить, что первый элемент списка содержит букву A
        self.assertTrue(b'E' in content[1]) # Проверить, что второй элемент списка содержит букву E


class RobotCheckerTestCase(TestCase):
    def setUp(self):
        # Создать клиент для отправки запросов
        self.client = APIClient()
        # Создать заказчика в базе данных
        self.customer = Customer.objects.create(email="customer@test.org")
        # Создать несколько роботов в базе данных
        self.robot1 = Robot.objects.create(model="A1", version="B2", created="2023-10-06 11:09:22")
        self.robot2 = Robot.objects.create(model="C3", version="D4", created="2023-10-07 12:10:23")
        # Создать заказ в базе данных
        self.order = Order.objects.create(customer=self.customer, robot_serial="A1B2")
        # Получить URL для API-endpoint создания робота
        self.check_url = reverse('robot-check')

    def test_robot_checker_robot_exists(self):
        data = {"model":"A1", "version":"B2"}
        response = self.client.post(self.check_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content), {"exists": True})

    def test_robot_checker_robot_not_exists(self):
        data = {"model":"E5", "version":"F6"}
        response = self.client.post(self.check_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content), {"exists": False})


class RobotEmailTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.customer = Customer.objects.create(email="customer@test.org")

        self.robot1 = Robot.objects.create(model="A1", version="B2", created="2023-10-06 11:09:22")
        self.robot2 = Robot.objects.create(model="C3", version="D4", created="2023-10-07 12:10:23")

        self.order = Order.objects.create(customer=self.customer, robot_serial="E5F6")

        self.check_url = reverse('robot-check')

    def test_robot_checker_send_email(self):
        data = {"model":"E5", "version":"F6"}
        response = self.client.post(self.check_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content), {"exists": False})
        self.assertTrue(Order.objects.filter(customer=self.customer, robot_serial="E5F6").exists())

        robot3 = Robot.objects.create(model="E5", version="F6", created="2023-10-08 13:11:24")

        self.assertFalse(Order.objects.filter(customer=self.customer, robot_serial="E5F6").exists())
        self.assertEqual(len(mail.outbox), 1)

        email = mail.outbox[0]

        # Проверить тему и адресата
        self.assertEqual(email.subject, 'Заказанный вами робот теперь доступен')
        self.assertEqual(email.to, ['customer@test.org'])

        # Проверить, что отправитель письма соответствует ожидаемому
        self.assertEqual(email.from_email, settings.EMAIL_HOST_USER)

        # Проверить, что текст письма соответствует ожидаемому
        expected_message = f'Добрый день!\n\nНедавно вы интересовались нашим роботом модели E5, версии F6.\nЭтот робот теперь в наличии. Если вам подходит этот вариант - пожалуйста, свяжитесь с нами'
        self.assertEqual(email.body, expected_message)
