from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.http import FileResponse, JsonResponse
from django.core.mail import send_mail
from django.db.models import Count
from django.db.models.signals import post_save
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.dispatch import receiver
from openpyxl import Workbook

from rest_framework import generics
from rest_framework.response import Response

from orders.models import Order

from .models import Robot
from .serializers import RobotSerializer
from customers.views import Customer

import json


class RobotOrderQueue:
    def __init__(self):
        self.queue = []

    def add_order(self, order):
        self.queue.append(order)

    def remove_order(self, order):
        self.queue.remove(order)

    def get_orders(self):
        return self.queue


class RobotCreateView(generics.CreateAPIView):
    queryset = Robot.objects.all()
    serializer_class = RobotSerializer


class ReportGenerator:
    def __init__(self):
        self.week_ago = timezone.now() - timezone.timedelta(weeks=1)
        self.robots = Robot.objects.filter(created__gte=self.week_ago)
        self.data = self.robots.values('model', 'version').annotate(total=Count('model')).order_by('model', 'version')

    def generate_report(self):
        return self.data


class WorkbookCreator:
    def __init__(self, data):
        self.data = data
        self.wb = Workbook()
        self.wb.remove(self.wb.active)

    def create_workbook(self):
        if not self.data:
            ws = self.wb.create_sheet(title="No data")
            ws['A1'] = "No data for the last week"
        else:
            current_letter = ''
            for row_data in self.data:
                letter = row_data['model'][0]
                if letter != current_letter:
                    current_letter = letter
                    ws = self.wb.create_sheet(title=letter)
                    headers = ["Модель", "Версия", "Количество за неделю"]
                    for col_num, column_title in enumerate(headers, 1):
                        col_letter = ws.cell(row=1, column=col_num).column_letter
                        ws['{}1'.format(col_letter)] = column_title
                        ws.column_dimensions[col_letter].width = 15
                row_num = ws.max_row + 1
                ws.cell(row=row_num, column=1, value=row_data['model'])
                ws.cell(row=row_num, column=2, value=row_data['version'])
                ws.cell(row=row_num, column=3, value=row_data['total'])
        return self.wb


class FileHandler:
    def __init__(self, wb):
        self.wb = wb

    def save_workbook_to_file(self):
        self.wb.save('robots_report.xlsx')
        return 'robots_report.xlsx'

    def create_file_response(self, filepath):
        response = FileResponse(
            open(filepath, 'rb'), 
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=robots_report.xlsx'
        return response


class RobotReportView(View):
    def get(self, request):
        report_generator = ReportGenerator()
        data = report_generator.generate_report()

        workbook_creator = WorkbookCreator(data)
        wb = workbook_creator.create_workbook()

        file_handler = FileHandler(wb)
        filepath = file_handler.save_workbook_to_file()
        response = file_handler.create_file_response(filepath)

        return response


class RobotDeleteView(generics.DestroyAPIView):
    queryset = Robot.objects.all()
    serializer_class = RobotSerializer
    lookup_field = 'serial'

    def delete(self, request, *args, **kwargs):
        # Получить робота по serial
        robot = self.get_object()
        # Сохранить информацию о роботе для вывода
        model = robot.model
        version = robot.version
        serial = robot.serial

        robot.delete()

        return Response({"message": f"Робот {model} {version} с серийным номером {serial} удален."})


class RobotOrderHandler(View):
    order_queue = RobotOrderQueue()

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        data = json.loads(request.body)
        model = data.get('model')
        version = data.get('version')
        robot_serial = model + version
        login = data.get('login')
        password = data.get('password')
        customer = Customer.objects.filter(login=login, password=password).first()

        if Robot.objects.filter(model=model, version=version).exists():
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


@receiver(post_save, sender=Robot)
def robot_created(sender, instance, created, **kwargs):
    if created:
        model = instance.model
        version = instance.version
        robot_serial = model + version

        for order in RobotOrderHandler.order_queue.get_orders():
            if order.robot_serial == robot_serial:
                print(f"Robot {model} {version} is now available")
                RobotOrderHandler.order_queue.remove_order(order)
