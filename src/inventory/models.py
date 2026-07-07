from django.db import models

from shop.models import ShopItems
from wallet.models import Wallet


# Create your models here.
class InventoryItem(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    shop_item = models.ForeignKey(
        ShopItems,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inventory_items",
    )
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["wallet", "shop_item"], name="unique_inventory_item"
            )
        ]

    def __str__(self):
        item_name = self.shop_item.name if self.shop_item else "Deleted Item"
        return f"{self.wallet} - {item_name}"
