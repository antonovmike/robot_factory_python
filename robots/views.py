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


with open('robots.json') as f:
    data = json.load(f)
robot_statistics = data['robot_statistics']


def download_report(request):
    # Создаем новую книгу Excel
    wb = Workbook()
    wb.remove(wb.active)
    headings = ("Модель", "Версия", "Количество за неделю")

    # Получаем данные за последнюю неделю
    week_ago = timezone.now() - timedelta(days=7)
    robots = Robot.objects.filter(created__gte=week_ago)

    # # Для каждой модели создаем отдельный лист
    # for model in robots.values_list('model', flat=True).distinct():
    #     ws = wb.create_sheet(title=model)
    #     ws.append(['Модель', 'Версия', 'Количество за неделю'])

    #     # Для каждой версии этой модели добавляем строку в лист
    #     for version in robots.filter(model=model).values_list('version', flat=True).distinct():
    #         count = robots.filter(model=model, version=version).count()
    #         ws.append([model, version, count])

    # # Тест - файл сохраняется вместе с содержимым
    # wb = Workbook()
    # ws = wb.create_sheet(title="model")
    # ws.append(['Модель', 'Версия', 'Количество за неделю'])
    # for i in robot_statistics:
    #     ws.append([i["model"], i["version"], i["count"]])

    groups = {}
    for row in robot_statistics:
        model = row["model"]
        if model not in groups:
            groups[model] = []
            groups[model].append(row)
        else:
            groups[model].append(row)

    # для каждой группы создаем новый лист и записываем данные
    for model, data in groups.items():
    # создаем новый лист с названием модели
        ws = wb.create_sheet(model)
    # записываем названия столбцов в первую строку
        ws.append(headings)

        # записываем данные по модели в последующие строки
        for row in data:
            ws.append([row["model"], row["version"], row["count"]])

    # Сохраняем книгу в памяти
    filename = 'robots_report.xlsx'
    wb.save(filename)

    # Читаем файл из памяти и возвращаем его в ответе
    with open(filename, 'rb') as f:
        response = HttpResponse(f.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response['Content-Disposition'] = 'attachment; filename={}'.format(filename)

    return response
