from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Robot
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware
from openpyxl import Workbook
from django.utils import timezone
from datetime import timedelta
import json

@csrf_exempt
def create_robot(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        model = data.get('model')
        version = data.get('version')
        created_str = data.get('created')

        # конвертируем строку в datetime объект
        naive_datetime = parse_datetime(created_str)
        created = make_aware(naive_datetime)

        # проверка на соответствие существующим в системе моделям
        if model and version and created:
            try:
                robot = Robot.objects.create(model=model, version=version, created=created)
                return JsonResponse({'message': f'Робот {robot.model}-{robot.version} успешно создан'})
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=400)
        else:
            return JsonResponse({'error': 'Неверные входные данные'}, status=400)
    else:
        return HttpResponse(status=405)

def download_report(request):
    # Создаем новую книгу Excel
    wb = Workbook()

    # Получаем данные за последнюю неделю
    week_ago = timezone.now() - timedelta(days=7)
    robots = Robot.objects.filter(created__gte=week_ago)

    # Для каждой модели создаем отдельный лист
    for model in robots.values_list('model', flat=True).distinct():
        ws = wb.create_sheet(title=model)
        ws.append(['Модель', 'Версия', 'Количество за неделю'])

        # Для каждой версии этой модели добавляем строку в лист
        for version in robots.filter(model=model).values_list('version', flat=True).distinct():
            count = robots.filter(model=model, version=version).count()
            ws.append([model, version, count])

    # Сохраняем книгу в памяти
    filename = 'robots_report.xlsx'
    wb.save(filename)

    # Читаем файл из памяти и возвращаем его в ответе
    with open(filename, 'rb') as f:
        response = HttpResponse(f.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response['Content-Disposition'] = 'attachment; filename={}'.format(filename)

    return response
