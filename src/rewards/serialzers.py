from rest_framework import serializers

from .models import Reward, RewardClaim


class RewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reward
        fields = "__all__"


class RewardClaimSerializer(serializers.Serializer):
    playerId = serializers.IntegerField(min_value=1)
