from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "discounted_price", "rating", "review_count")
    search_fields = ("name",)
    list_filter = ("rating", "review_count")