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
import datetime
import json
import sqlite3

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
    conn = sqlite3.connect("db.sqlite3")
    cur = conn.cursor()
    cur.execute("SELECT * FROM robots_robot")
    robot_statistics = [
        dict(zip([column[0] for column in cur.description], row)) for row in cur.fetchall()
    ]
    # Создаем новую книгу Excel
    wb = Workbook()
    wb.remove(wb.active)
    headings = ("Модель", "Версия", "Количество за неделю")

    # Получаем данные за последнюю неделю
    week_ago = timezone.now() - timedelta(days=7)
    robots = Robot.objects.filter(created__gte=week_ago)

    # преобразуем значения в столбце date из текста в объекты datetime
    for row in robot_statistics:
        row["date"] = datetime.datetime.strptime(row["date"], "%Y-%m-%d %H:%M:%S.%f")
        # вычисляем дату неделю назад
        week_ago = datetime.datetime.now() - datetime.timedelta(days=7)
        week_ago = str(week_ago)
        # отфильтровываем данные по условию, что дата больше или равна дате неделю назад
        robot_statistics = [row for row in robot_statistics if str(row["date"]) >= week_ago]

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
