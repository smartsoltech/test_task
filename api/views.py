from rest_framework import viewsets, filters as rest_filters
from django_filters.rest_framework import DjangoFilterBackend
from database.models import Product
from .serializers import ProductSerializer
from .filters import ProductFilter


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, rest_filters.OrderingFilter]
    filterset_class = ProductFilter
    ordering_fields = ['price', 'discounted_price', 'rating', 'review_count', 'name']
