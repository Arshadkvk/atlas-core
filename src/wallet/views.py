from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from wallet.services import *

from .serializers import (
    CreditSerializer,
    PurchaseSerializer,
    WalletSerializer,
)


class WalletCreditView(APIView):

    def post(self, request, player_id):
        serializer = CreditSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # TODO:
        # Call wallet service

        return Response(
            {"message": "Not implemented"},
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )


class WalletPurchaseView(APIView):

    def post(self, request, player_id):
        serializer = PurchaseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # TODO:
        # Call wallet service

        return Response(
            {"message": "Not implemented"},
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )


class WalletDetailView(APIView):

    def get(self, request, player_id):
        print(f"Getting wallet details for player_id: {player_id}")

        data = WalletService.get_wallet(player_id)

        return Response(
            data,
            status=status.HTTP_200_OK,
        )
