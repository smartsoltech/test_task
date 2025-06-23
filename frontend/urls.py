from django.urls import path
from .views import index, filter_ajax, run_parser

app_name = 'frontend'

urlpatterns = [
    path('', index, name='index'),
    path('filter/', filter_ajax, name='filter'),
    path('run-parser/', run_parser, name='run_parser'),
]
