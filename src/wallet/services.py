from datetime import timedelta, timezone

from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from wallet.idempotency import *

from .models import Transaction, Wallet
from .serializers import WalletSerializer
from django.db import transaction


class WalletService:

    @staticmethod
    def get_wallet(player_id):
        """
        Fetch the wallet for a player and return serialized data.
        """

        wallet = get_object_or_404(
            Wallet.objects.select_related("player"),
            player__player_id=player_id,
        )

        serializer = WalletSerializer(wallet)

        return serializer.data

    @staticmethod
    @transaction.atomic
    def credit_wallet(player_id, amount, reason, idempotency_key):
        """
        Credit the wallet for a player with the specified amount and reason.
        """

        wallet = get_object_or_404(
            Wallet.objects.select_for_update().select_related("player"),
            player__player_id=player_id,
        )

        current_request_hash = create_request_hash(
            {
                "amount": str(amount),
                "reason": reason,
            }
        )

        existing = get_existing_request(idempotency_key)
        if existing and existing.expires_at < timezone.now():
            existing.delete()
            existing = None
        if existing:

            if existing.request_hash != current_request_hash:
                raise ValidationError(
                    {
                        "error": "IDEMPOTENCY_KEY_CONFLICT",
                        "message": "This idempotency key has already been used for a different request payload.",
                    }
                )

            return existing.response_body

        wallet.balance += amount
        wallet.save()

        transaction_record = wallet.transactions.create(
            amount=amount,
            reason=reason,
            transaction_type=Transaction.TransactionTypes.CREDIT,
            status=Transaction.StatusChoices.SUCCESS,
        )
        serializer = WalletSerializer(wallet)
        response_data = serializer.data
        idempotency_record = create_idempotency_record(
            key=idempotency_key,
            request_hash=current_request_hash,
            response_status=200,
            response_body=response_data,
            expires_at=timezone.now() + timedelta(hours=24),
        )
        transaction_record.idempotency_record = idempotency_record
        transaction_record.save(update_fields=["idempotency_record"])
        return response_data
