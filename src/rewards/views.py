from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rewards.services import RewardService

from .serialzers import RewardClaimSerializer


class RewardClaimView(APIView):

    def post(self, request, reward_id):

        serializer = RewardClaimSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        player_id = serializer.validated_data["playerId"]

        idempotency_key = request.headers.get("Idempotency-Key")

        if not idempotency_key:
            return Response(
                {
                    "error": "IDEMPOTENCY_KEY_REQUIRED",
                    "message": "Idempotency-Key header is required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = RewardService.claim_reward(
            player_id=player_id,
            reward_id=reward_id,
            idempotency_key=idempotency_key,
        )

        return Response(data, status=status.HTTP_200_OK)
