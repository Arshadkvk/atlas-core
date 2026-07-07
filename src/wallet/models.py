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
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0,
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    def __str__(self):
        return f"Wallet - {self.player.user_name}"


class Transaction(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"

    class TransactionTypes(models.TextChoices):
        CREDIT = "CREDIT", "Credit"
        DEBIT = "DEBIT", "Debit"
        REWARD = "REWARD", "Reward"

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
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
        return f"{self.transaction_type} - {self.amount}"


class IdempotencyKey(models.Model):

    key = models.CharField(max_length=255, unique=True)

    request_hash = models.CharField(max_length=255)

    response_status = models.PositiveSmallIntegerField()

    response_body = models.JSONField()

    created_at = models.DateTimeField(auto_now_add=True)

    expires_at = models.DateTimeField(null=True, blank=True)
