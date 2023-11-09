from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient

from robots.models import Robot
from robots.serializers import RobotSerializer


class RobotAPITestCase(TestCase):
    def setUp(self):
        # Create a client to send requests
        self.client = APIClient()
        # Create multiple robots in the database
        self.robot1 = Robot.objects.create(model="A1", version="B2", created="2023-10-06 11:09:22")
        self.robot2 = Robot.objects.create(model="C3", version="D4", created="2023-10-07 12:10:23")
        # Get the URL for the robot creation API endpoint
        self.create_url = reverse('robot-create')

    def test_create_robot_success(self):
        data = {"model":"E5", "version":"F6", "created":"2023-10-08 11:11:24"}
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        robot = Robot.objects.get(model="E5")
        expected_data = RobotSerializer(robot).data
        self.assertEqual(response.data, expected_data)


    def test_create_robot_fail(self):
        # Prepare invalid data for the request (for example, empty or incorrect)
        data = {"model":"", "version":"G7", "created":"2023-10-09 11:12:25"}
        # Send a POST request with data
        response = self.client.post(self.create_url, data, format='json')
        # Check that the response status code is 400 (Bad Request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Check that the response contains a validation error message
        self.assertTrue('model' in response.data)
        self.assertEqual(response.data['model'], ['This field may not be blank.'])

    def test_validate_correct_data(self):
        # Valid test data
        data = {
            "model": "A1",
            "version": "B2",
            "created": timezone.now()
        }
        serializer = RobotSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_validate_future_created(self):
        # Invalid test data (creation date in the future)
        data = {
            "model": "A1",
            "version": "B2",
            "created": timezone.now() + timezone.timedelta(days=1)
        }
        serializer = RobotSerializer(data=data)
        # Check that a ValidationError exception is thrown when validating data
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_validate_incorrect_model(self):
        # Invalid data for the test (incorrect model format)
        data = {
            "model": "11",
            "version": "B2",
            "created": timezone.now()
        }
        serializer = RobotSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_validate_incorrect_version(self):
        # Invalid data for the test (incorrect version format)
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

        report_url = reverse('robot-report')

        response = self.client.get(report_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that the response contains data for each page
        content = list(response.streaming_content) # Convert generator to list
        self.assertTrue(b'A' in content[0]) # Check that the first element of a list contains the letter A
        self.assertTrue(b'E' in content[1]) # Check that the first element of a list contains the letter E
