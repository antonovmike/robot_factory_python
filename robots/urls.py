from django.urls import path
from .views import create_robot
from .views import create_robot, download_report

urlpatterns = [
    path('create/', create_robot, name='create_robot'),
    path('report/', download_report, name='download_report'),
]
