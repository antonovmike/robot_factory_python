from django.test import TestCase

# Create your tests here.
from rest_framework.test import APIClient, APITestCase
from django.urls import reverse
from .models import Robot
from .serializers import RobotSerializer


class RobotAPITestCase(APITestCase):
    def setup(self):
        self.client = APIClient()
        self.robot_data = {"model": "R2", "version": "D2", "created": "2022-12-31 23:59:59"}
        self.response = self.client.post(
            reverse('robot-list'),
            self.robot_data,
            format="json"
        )

    def test_api_can_create_a_robot(self):
        self.assertEqual(self.response.status_code, 201)

    def test_api_can_get_a_robot(self):
        robot = Robot.objects.get()
        response = self.client.get(
            reverse('robot-detail',
                    kwargs={'pk': robot.id}), format="json")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, robot)

    def test_api_can_update_robot(self):
        robot = Robot.objects.get()
        change_robot = {'model': 'R1', 'version': 'D1', 'created': '2022-12-31 23:59:59'}
        res = self.client.put(
            reverse('robot-detail', kwargs={'pk': robot.id}),
            change_robot, format='json'
        )
        self.assertEqual(res.status_code, 200)

    def test_api_can_delete_robot(self):
        robot = Robot.objects.get()
        response = self.client.delete(
            reverse('robot-detail', kwargs={'pk': robot.id}),
            format='json',
            follow=True)

        self.assertEquals(response.status_code, 204)
