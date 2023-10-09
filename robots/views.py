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
        # Удалить дефолтную страницу
        wb.remove(wb.active)
        # Получить данные за последнюю неделю
        week_ago = timezone.now() - timezone.timedelta(weeks=1)
        robots = Robot.objects.filter(created__gte=week_ago)
        # Группировать данные по модели и версии
        data = robots.values('model', 'version').annotate(total=Count('model')).order_by('model', 'version')
        current_model = ''
        for row_data in data:
            if row_data['model'] != current_model:
                current_model = row_data['model']
                ws = wb.create_sheet(title=current_model)
                headers = ["Модель", "Версия", "Количество за неделю"]
                for col_num, column_title in enumerate(headers, 1):
                    col_letter = ws.cell(row=1, column=col_num).column_letter
                    ws['{}1'.format(col_letter)] = column_title
                    ws.column_dimensions[col_letter].width = 15
            row_num = ws.max_row + 1
            ws.cell(row=row_num, column=1, value=row_data['model'])
            ws.cell(row=row_num, column=2, value=row_data['version'])
            ws.cell(row=row_num, column=3, value=row_data['total'])
        # Сохранить workbook в файл
        wb.save('robots_report.xlsx')
        # Создать HTTP ответ с файлом
        response = FileResponse(open('robots_report.xlsx', 'rb'), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=robots_report.xlsx'
        return response

