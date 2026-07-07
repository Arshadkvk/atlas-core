from django.db import models


# Create your models here.
class ShopItems(models.Model):
    item_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    price = models.PositiveBigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
