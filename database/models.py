from django.db import models

class Category(models.Model):
    wb_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name="children")
    shard = models.CharField(max_length=100, blank=True)
    query = models.CharField(max_length=255, blank=True)
    url = models.CharField(max_length=255, blank=True)
    level = models.IntegerField(default=0)

    def __str__(self):
        return self.name
    
class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.PositiveIntegerField()
    discounted_price = models.PositiveIntegerField()
    rating = models.FloatField()
    review_count = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    def discount(self):
        return self.price - self.discounted_price

    def __str__(self):
        return f"{self.name} — {self.discounted_price}₽"
    

class ProductHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='history')
    date = models.DateTimeField(auto_now_add=True)
    price = models.IntegerField()
    discounted_price = models.IntegerField()
    rating = models.FloatField()
    review_count = models.IntegerField()

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.product.name} @ {self.date.strftime('%Y-%m-%d %H:%M')}"


