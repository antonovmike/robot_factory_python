from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Robot
import json


# csrf_exempt отключает защиту CSRF для этого view
@method_decorator(csrf_exempt, name='dispatch')
class RobotView(View):
    def post(self, request):
        data = json.loads(request.body)
        robot = Robot(**data)
        robot.save()
        return JsonResponse(data)
