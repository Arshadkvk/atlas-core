from rest_framework import serializers

from inventory.serializers import InventoryItemSerializer
from rewards.models import RewardClaim

from .models import Transaction, Wallet


class CreditSerializer(serializers.Serializer):
    amount = serializers.IntegerField(min_value=1)
    reason = serializers.CharField(max_length=255)


class PurchaseSerializer(serializers.Serializer):
    itemId = serializers.CharField(max_length=255)
    price = serializers.IntegerField(min_value=1)


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"


class WalletSerializer(serializers.ModelSerializer):
    inventory = InventoryItemSerializer(
        source="inventoryitem_set",
        many=True,
        read_only=True,
    )

    claimedRewards = serializers.SerializerMethodField()

    class Meta:
        model = Wallet
        fields = [
            "balance",
            "inventory",
            "claimedRewards",
        ]

    def get_claimedRewards(self, obj):
        return list(
            RewardClaim.objects.filter(wallet=obj).values_list(
                "reward__name",
                flat=True,
            )
        )
