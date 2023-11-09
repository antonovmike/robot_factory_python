from django.views import View
from django.utils import timezone
from django.core.mail import send_mail
from django.http import JsonResponse
from django.db.models.signals import post_save
from django.dispatch import receiver
import json

from .models import Order
from customers.models import Customer

class OrderQueue:
   def __init__(self):
       self.queue = []

   def add_order(self, order):
       self.queue.append(order)

   def remove_order(self, order):
       self.queue.remove(order)

   def get_orders(self):
       return self.queue


class OrderHandler(View):
   order_queue = OrderQueue()

   def post(self, request):
       data = json.loads(request.body)
       model = data.get('model')
       version = data.get('version')
       robot_serial = model + version
       login = data.get('login')
       password = data.get('password')
       customer = Customer.objects.filter(login=login, password=password).first()

       if Order.objects.filter(robot_serial=robot_serial).exists():
           print("Robot " + model + " " + version + " found")
           for order in self.order_queue.get_orders():
               if order.robot_serial == robot_serial:
                  print(f"Robot {model} {version} is now available")
                  self.order_queue.remove_order(order)
                  send_mail(
                      'Заказанный вами робот теперь доступен',
                      f'Добрый день!\n\nНедавно вы интересовались нашим роботом модели {model}, версии {version}.\nЭтот робот теперь в наличии. Если вам подходит этот вариант - пожалуйста, свяжитесь с нами',
                      'from@example.com',
                      [customer.email],
                      fail_silently=False,
                  )
           return JsonResponse({"exists": True})
       else:
           print("Robot " + model + " " + version + " not found")
           # Добавить заказ в очередь
           order = Order(robot_serial=robot_serial)
           self.order_queue.add_order(order)
           return JsonResponse({"exists": False})


@receiver(post_save, sender=Order)
def order_created(sender, instance, created, **kwargs):
   if created:
       model = instance.robot.model
       version = instance.robot.version
       robot_serial = model + version

       for order in OrderHandler.order_queue.get_orders():
           if order.robot_serial == robot_serial:
               print(f"Robot {model} {version} is now available")
               OrderHandler.order_queue.remove_order(order)
