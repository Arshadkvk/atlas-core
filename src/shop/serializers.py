from rest_framework import serializers

from .models import ShopItems


class ShopItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopItems
        fields = "__all__"
