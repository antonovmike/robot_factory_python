from django.test import TestCase

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from robots.models import Robot
from robots.serializers import RobotSerializer

from django.utils import timezone
from rest_framework.exceptions import ValidationError


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
