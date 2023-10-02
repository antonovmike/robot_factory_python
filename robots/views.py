from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse, HttpResponse
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware
from django.views.decorators.csrf import csrf_exempt
from jsonschema import Draft7Validator
# from jsonschema import validate, ValidationError

from .models import Robot

import json


schema = {
    "type": "object",
    "properties": {
        "model": {"type": "string"},
        "version": {"type": "string"},
        "created": {"type": "string", "format": "date-time"},
    },
    "required": ["model", "version", "created"],
}


@csrf_exempt
def create_robot(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        valid = Draft7Validator(schema)
        errors = [error.message for error in valid.iter_errors(data)]
        if errors:
            return JsonResponse({'error': errors}, status=400)
        model = data.get('model')
        version = data.get('version')
        created_str = data.get('created')

        # конвертируем строку в datetime объект и делаем его "осведомленным"
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
