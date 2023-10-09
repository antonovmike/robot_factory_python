# from django.shortcuts import render
from rest_framework import generics
from .models import Robot
from .serializers import RobotSerializer


class RobotCreateView(generics.CreateAPIView):
    queryset = Robot.objects.all()
    serializer_class = RobotSerializer

from django.views import View
from django.http import FileResponse
from openpyxl import Workbook
from django.utils import timezone
from django.db.models import Count


class RobotReportView(View):
    def get(self, request):
        # Создать новый workbook
        wb = Workbook()
        ws = wb.active
        # Добавить заголовки в первую строку
        headers = ["Модель", "Версия", "Количество за неделю"]
        for col_num, column_title in enumerate(headers, 1):
            col_letter = ws.cell(row=1, column=col_num).column_letter
            ws['{}1'.format(col_letter)] = column_title
            ws.column_dimensions[col_letter].width = 15
        # Получить данные за последнюю неделю
        week_ago = timezone.now() - timezone.timedelta(weeks=1)
        robots = Robot.objects.filter(created__gte=week_ago)
        # Группировать данные по модели и версии
        data = robots.values('model', 'version').annotate(total=Count('model')).order_by('model', 'version')
        # Добавить данные в таблицу
        for row_num, row_data in enumerate(data, 2):
            ws.cell(row=row_num, column=1, value=row_data['model'])
            ws.cell(row=row_num, column=2, value=row_data['version'])
            ws.cell(row=row_num, column=3, value=row_data['total'])
        # Сохранить workbook в файл
        wb.save('robots_report.xlsx')
        # Создать HTTP ответ с файлом
        response = FileResponse(open('robots_report.xlsx', 'rb'), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=robots_report.xlsx'
        return response
