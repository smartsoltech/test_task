from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.PositiveIntegerField()
    discounted_price = models.PositiveIntegerField()
    rating = models.FloatField()
    review_count = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def discount(self):
        return self.price - self.discounted_price

    def __str__(self):
        return f"{self.name} — {self.discounted_price}₽"