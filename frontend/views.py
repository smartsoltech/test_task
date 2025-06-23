from django.shortcuts import render
from database.models import Product

from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.core.management import call_command

def index(request):
    products = Product.objects.all().order_by('-rating')
    return render(request, 'frontend/index.html', {
        'products': products
    })


def filter_ajax(request):
    qs = Product.objects.all()

    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    min_rating = request.GET.get("min_rating")
    min_reviews = request.GET.get("min_reviews")

    if min_price:
        qs = qs.filter(discounted_price__gte=min_price)
    if max_price:
        qs = qs.filter(discounted_price__lte=max_price)
    if min_rating:
        qs = qs.filter(rating__gte=min_rating)
    if min_reviews:
        qs = qs.filter(review_count__gte=min_reviews)

    # HTML таблица
    html = render_to_string("frontend/products_table.html", {"products": qs})

    #  Гистограмма по диапазонам цен
    price_buckets = [0, 5000, 10000, 20000, 50000, 100000]
    histogram = []
    for i in range(len(price_buckets) - 1):
        lower = price_buckets[i]
        upper = price_buckets[i + 1]
        count = qs.filter(discounted_price__gte=lower, discounted_price__lt=upper).count()
        histogram.append({
            "range": f"{lower}-{upper}",
            "count": count
        })

    linechart = []
    for p in qs:
        if p.price > p.discounted_price:
            linechart.append({
                "rating": round(p.rating, 2),
                "discount": p.price - p.discounted_price
            })

    return JsonResponse({
        "html": html,
        "chart_data": {
            "histogram": histogram,
            "linechart": linechart
        }
    })
    
    
@csrf_exempt
def run_parser(request):
    if request.method == "POST":
        query = request.POST.get("query")
        if query:
            call_command("parse_wb", query)
            return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "error"}, status=400)