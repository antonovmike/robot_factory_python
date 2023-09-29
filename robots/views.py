from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware
from django.utils import timezone

from openpyxl import Workbook

from datetime import timedelta

from .models import Robot
from robots.models import Robot
from orders.models import Order

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

        # Проверка наличия необходимых данных
        if not all([model, version, created_str]):
            return JsonResponse({'error': 'Неверные входные данные'}, status=400)

        # Конвертируем строку в datetime объект
        naive_datetime = parse_datetime(created_str)
        created = make_aware(naive_datetime)

        # Проверка на соответствие существующим моделям
        try:
            robot = Robot.objects.create(model=model, version=version, created=created)
            notify_customer(robot)
            return JsonResponse({'message': f'Робот {robot.model}-{robot.version} успешно создан'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
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


def check_robot_exists(customer, robot_model, robot_version):
    # Проверяем наличие робота в базе данных
    if Robot.objects.filter(model=robot_model, version=robot_version).exists():
        return f'Robot {robot_model}-{robot_version} is available.'
    else:
    # Если робота нет в наличии, добавляем заказ в список ожидания
        Order.objects.create(customer=customer, robot_serial=f'{robot_model}-{robot_version}')
        return f'Robot {robot_model}-{robot_version} is not available. Your order is added to the waiting list.'


def notify_customer(robot):
    # Проверяем, есть ли заказы на этот робот в списке ожидания
    orders = Order.objects.filter(robot_serial=f'{robot.model}-{robot.version}')
    for order in orders:
        # Составляем текст письма
        message = f"""Добрый день!
Недавно вы интересовались нашим роботом модели {robot.model}, версии {robot.version}.
Этот робот теперь в наличии. Если вам подходит этот вариант - пожалуйста, свяжитесь с нами"""
        # Сохраняем письмо в текстовый файл
        with open(f'email_{order.customer}_{datetime.datetime.now().strftime("%Y-%m-%d")}.txt', 'w') as f:
            f.write(message)
