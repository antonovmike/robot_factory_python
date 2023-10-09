# from django.shortcuts import render
from django.views import View
from django.http import FileResponse
from django.utils import timezone
from django.db.models import Count
from openpyxl import Workbook

from rest_framework import generics

from .models import Robot
from .serializers import RobotSerializer


class RobotCreateView(generics.CreateAPIView):
    queryset = Robot.objects.all()
    serializer_class = RobotSerializer


class RobotReportView(View):
    def get(self, request):
        wb = Workbook()
        # Удалить дефолтную страницу
        wb.remove(wb.active)
        # Получить данные за последнюю неделю
        week_ago = timezone.now() - timezone.timedelta(weeks=1)
        robots = Robot.objects.filter(created__gte=week_ago)
        # Группировать данные по первой букве модели и версии
        data = robots.values('model', 'version').annotate(total=Count('model')).order_by('model', 'version')
        current_letter = ''
        for row_data in data:
            letter = row_data['model'][0]
            if letter != current_letter:
                current_letter = letter
                ws = wb.create_sheet(title=letter)
                headers = ["Модель", "Версия", "Количество за неделю"]
                for col_num, column_title in enumerate(headers, 1):
                    col_letter = ws.cell(row=1, column=col_num).column_letter
                    ws['{}1'.format(col_letter)] = column_title
                    ws.column_dimensions[col_letter].width = 15
            row_num = ws.max_row + 1
            ws.cell(row=row_num, column=1, value=row_data['model'])
            ws.cell(row=row_num, column=2, value=row_data['version'])
            ws.cell(row=row_num, column=3, value=row_data['total'])

        wb.save('robots_report.xlsx')

        response = FileResponse(
            open('robots_report.xlsx', 'rb'), 
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=robots_report.xlsx'
        return response
