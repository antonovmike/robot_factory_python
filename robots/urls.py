from django.contrib import admin
from django.urls import path
# from robots.views import RobotView
from . import views


urlpatterns = [
    path('/', views.download_summary(), name='robot'),
]
