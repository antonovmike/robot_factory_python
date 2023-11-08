# from django.db import models

from customers.models import Customer, models
from robots.models import Robot


# class Order(models.Model):
#     customer = models.ForeignKey(Customer,on_delete=models.CASCADE)
#     robot_serial = models.CharField(max_length=5,blank=False, null=False)

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders_orders')
    robot = models.ForeignKey(Robot, on_delete=models.CASCADE)
    order_date = models.DateTimeField(blank=False, null=False)

class Meta:
    db_table = 'orders'