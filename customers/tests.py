from django.test import TestCase
from .models import Customer
from .serializers import CustomerSerializer

# "sırsöz" / "сырсөз" means "password" in Kyrgyz language
class CustomerTestCase(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            name='Kurmanjan Datka',
            email='kurmanjan@example.com',
            login='kurmanjandatka',
            password='syrsoz'
        )

    def test_customer_creation(self):
        self.assertEqual(self.customer.name, 'Kurmanjan Datka')
        self.assertEqual(self.customer.email, 'kurmanjan@example.com')
        self.assertEqual(self.customer.login, 'kurmanjandatka')
        self.assertEqual(self.customer.password, 'syrsoz')

    def test_customer_serializer(self):
        serializer = CustomerSerializer(instance=self.customer)
        expected_data = {
            'name': 'Kurmanjan Datka',
            'email': 'kurmanjan@example.com',
            'login': 'kurmanjandatka',
            'password': 'syrsoz'
        }
        self.assertEqual(serializer.data, expected_data)
