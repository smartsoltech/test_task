from rest_framework import viewsets, filters as rest_filters
from django_filters.rest_framework import DjangoFilterBackend
from database.models import Product
from .serializers import ProductSerializer
from .filters import ProductFilter

from django.http import JsonResponse
from database.models import Category
from django.views.decorators.csrf import csrf_exempt

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, rest_filters.OrderingFilter]
    filterset_class = ProductFilter
    ordering_fields = ['price', 'discounted_price', 'rating', 'review_count', 'name']


def get_subcategories_api(request):
    wb_id = request.GET.get("parent_id")
    if not wb_id:
        return JsonResponse([], safe=False)

    try:
        parent = Category.objects.get(wb_id=wb_id)
    except Category.DoesNotExist:
        return JsonResponse([], safe=False)

    children = Category.objects.filter(parent=parent).order_by("name")
    data = [{"id": c.wb_id, "name": c.name} for c in children]
    return JsonResponse(data, safe=False)


from django.core.management import call_command
import json

@csrf_exempt
def run_parser_ajax(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    try:
        body = json.loads(request.body)
        wb_id = body.get("wb_id")

        if not wb_id:
            return JsonResponse({"error": "wb_id required"}, status=400)

        # приведение к int
        call_command("parse_wb", int(wb_id))

        return JsonResponse({"message": f"Парсинг категории {wb_id} успешно запущен."})
    except Exception as e:
        import traceback
        print(traceback.format_exc())  # ✅ покажет полный traceback в консоли
        return JsonResponse({"error": str(e)}, status=500)

from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models import Q
from database.models import Product

def product_filter_api(request):
    category_id = request.GET.get("category")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    min_reviews = request.GET.get("min_reviews")
    min_rating = request.GET.get("min_rating")

    products = Product.objects.all()

    if category_id:
        products = products.filter(category__wb_id=category_id)
    if min_price:
        products = products.filter(discounted_price__gte=min_price)
    if max_price:
        products = products.filter(discounted_price__lte=max_price)
    if min_reviews:
        products = products.filter(review_count__gte=min_reviews)
    if min_rating:
        products = products.filter(rating__gte=min_rating)

    html = render_to_string("frontend/products_table.html", {"products": products})

    # Пример данных для графиков
    histogram_data = [
        {"range": "0-1000", "count": products.filter(discounted_price__lte=1000).count()},
        {"range": "1000-2000", "count": products.filter(discounted_price__gt=1000, discounted_price__lte=2000).count()},
        {"range": "2000+", "count": products.filter(discounted_price__gt=2000).count()},
    ]
    scatter_data = [{"rating": p.rating, "discount": p.price - p.discounted_price} for p in products if p.rating and p.price]

    return JsonResponse({
        "html": html,
        "chart_data": {
            "histogram": histogram_data,
            "linechart": scatter_data
        }
    })
