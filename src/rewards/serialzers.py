from rest_framework import serializers

from .models import Reward, RewardClaim


class RewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reward
        fields = "__all__"


class RewardClaimSerializer(serializers.Serializer):
    playerId = serializers.CharField(max_length=255, required=True)
