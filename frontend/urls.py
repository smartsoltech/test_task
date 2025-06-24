from django.urls import path
from .views import index, filter_ajax, run_parser, product_detail, load_data_view

app_name = 'frontend'

urlpatterns = [
    path('', index, name='index'),
    path('filter/', filter_ajax, name='filter'),
    path('run-parser/', run_parser, name='run_parser'),
    path('product/<int:pk>/', product_detail, name='product_detail'),
    path('load_data', load_data_view, name='parse')
]
