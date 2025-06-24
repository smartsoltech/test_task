from django.shortcuts import render, get_object_or_404
from database.models import Product, Category

from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.core.management import call_command

from django.db.models import QuerySet

from django.db.models import Min, Max
from django.http import JsonResponse


def index(request):
    top_categories = Category.objects.filter(parent__isnull=True).order_by("name")
    return render(request, "frontend/index.html", {"top_categories": top_categories})


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

    html = render_to_string("frontend/products_table.html", {"products": qs})

    # Динамическая гистограмма по цене
    agg = qs.aggregate(min_price=Min("discounted_price"), max_price=Max("discounted_price"))
    min_val = agg["min_price"] or 0
    max_val = agg["max_price"] or 0

    histogram = []
    if max_val > min_val:
        margin = int((max_val - min_val) * 0.1)
        start = max(min_val - margin, 0)
        end = max_val + margin
        steps = 6
        step_size = max((end - start) // steps, 1)

        for i in range(steps):
            lower = start + i * step_size
            upper = lower + step_size
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


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    history = product.history.order_by("date")

    history_serialized = [
        {
            "date": entry.date.strftime("%Y-%m-%d"),
            "price": entry.price,
            "discounted_price": entry.discounted_price,
            "discount": entry.price - entry.discounted_price
        }
        for entry in history
    ]

    return render(request, "frontend/product_detail.html", {
        "product": product,
        "history": history,
        "history_serialized": history_serialized
    })
    
    
def load_data_view(request):
    from database.models import Category
    top_categories = Category.objects.filter(parent__isnull=True).order_by("name")
    return render(request, "frontend/load_data.html", {"top_categories": top_categories})