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

        idempotency_key = request.headers.get("Idempotency-Key")
        if not idempotency_key:
            return Response(
                {
                    "error": "IDEMPOTENCY_KEY_REQUIRED",
                    "message": "Idempotency-Key header is required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = WalletService.credit_wallet(
            player_id=player_id,
            amount=serializer.validated_data["amount"],
            reason=serializer.validated_data["reason"],
            idempotency_key=idempotency_key,
        )

        return Response(data, status=200)


class WalletPurchaseView(APIView):

    def post(self, request, player_id):

        serializer = PurchaseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        idempotency_key = request.headers.get("Idempotency-Key")

        if not idempotency_key:
            return Response(
                {
                    "error": "IDEMPOTENCY_KEY_REQUIRED",
                    "message": "Idempotency-Key header is required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = WalletService.purchase_item(
            player_id=player_id,
            item_id=serializer.validated_data["itemId"],
            price=serializer.validated_data["price"],
            idempotency_key=idempotency_key,
        )

        return Response(data, status=status.HTTP_200_OK)


class WalletDetailView(APIView):

    def get(self, request, player_id):
        print(f"Getting wallet details for player_id: {player_id}")

        data = WalletService.get_wallet(player_id)

        return Response(
            data,
            status=status.HTTP_200_OK,
        )
