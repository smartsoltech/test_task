from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, get_subcategories_api,run_parser_ajax, product_filter_api

router = DefaultRouter()
router.register(r'products', ProductViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('subcategories/', get_subcategories_api, name='get_subcategories'),
    path("run_parser/", run_parser_ajax, name="run_parser_ajax"),
    path('filter/', product_filter_api, name='product_filter_api'),
]
