from django.db import models
from django.core.validators import MinValueValidator
from players.models import Player
from decimal import Decimal


# Create your models here.
class Wallet(models.Model):
    player = models.OneToOneField(
        Player,
        on_delete=models.CASCADE,
        related_name="wallet",
    )
    balance = models.PositiveBigIntegerField(default=0)

    def __str__(self):
        return f"Wallet - {self.player.user_name}"


class Transaction(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"

    class TransactionTypes(models.TextChoices):
        CREDIT = "CREDIT", "Credit"
        DEBIT = "PURCHASE", "Purchase"
        REWARD = "REWARD", "Reward"

    wallet = models.ForeignKey(
        Wallet, on_delete=models.CASCADE, related_name="transactions"
    )
    amount = models.PositiveBigIntegerField()
    transaction_type = models.CharField(
        max_length=10,
        choices=TransactionTypes.choices,
        default=TransactionTypes.CREDIT,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10, choices=StatusChoices.choices, default=StatusChoices.PENDING
    )
    idempotency_record = models.OneToOneField(
        "IdempotencyKey",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transaction",
    )

    reason = models.CharField(max_length=255)

    class Meta:
        indexes = [
            models.Index(fields=["wallet"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        if self.transaction_type == self.TransactionTypes.CREDIT:
            return f"Credit of {self.amount} to {self.wallet}"
        elif self.transaction_type == self.TransactionTypes.DEBIT:
            return f"Debit of {self.amount} from {self.wallet}"
        elif self.transaction_type == self.TransactionTypes.REWARD:
            return f"Reward Added"
        else:
            return f"Transaction of {self.amount} for {self.wallet}"


class IdempotencyKey(models.Model):

    key = models.CharField(max_length=255, unique=True)

    request_hash = models.CharField(max_length=255)

    response_status = models.PositiveSmallIntegerField()

    response_body = models.JSONField()

    created_at = models.DateTimeField(auto_now_add=True)

    expires_at = models.DateTimeField(null=True, blank=True)
