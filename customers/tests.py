from django.test import TestCase
from .models import Customer
from .serializers import CustomerSerializer

class CustomerTestCase(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            name='John Doe',
            email='john@example.com',
            login='johndoe',
            password='secret'
        )

    def test_customer_creation(self):
        self.assertEqual(self.customer.name, 'John Doe')
        self.assertEqual(self.customer.email, 'john@example.com')
        self.assertEqual(self.customer.login, 'johndoe')
        self.assertEqual(self.customer.password, 'secret')

    def test_customer_serializer(self):
        serializer = CustomerSerializer(instance=self.customer)
        expected_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'login': 'johndoe',
            'password': 'secret'
        }
        self.assertEqual(serializer.data, expected_data)
