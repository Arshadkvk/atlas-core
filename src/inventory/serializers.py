from rest_framework import serializers

from .models import InventoryItem


class InventoryItemSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source="shop_item.name", read_only=True)

    class Meta:
        model = InventoryItem
        fields = [
            "id",
            "item_name",
            "quantity",
            "created_at",
        ]
