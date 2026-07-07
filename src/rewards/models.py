from django.db import models

from shop.models import ShopItems
from wallet.models import Wallet


# Create your models here.
class Reward(models.Model):
    class RewardType(models.TextChoices):
        CURRENCY = "CURRENCY"
        ITEM = "ITEM"

    name = models.CharField(max_length=100)
    reward_type = models.CharField(max_length=50, choices=RewardType.choices)
    currency_amount = models.PositiveBigIntegerField(null=True, blank=True)
    shop_item = models.ForeignKey(
        ShopItems, on_delete=models.CASCADE, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class RewardClaim(models.Model):
    reward = models.ForeignKey(
        Reward,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reward_claims",
    )
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    claimed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["wallet", "reward"], name="unique_wallet_reward_claim"
            )
        ]

    def __str__(self):
        return f"{self.wallet} claimed {self.reward}"
