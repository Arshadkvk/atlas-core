from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serialzers import RewardClaimSerializer


class RewardClaimView(APIView):

    def post(self, request, reward_id):

        serializer = RewardClaimSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # TODO:
        # Call reward service

        return Response(
            {"message": "Not implemented"},
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )
