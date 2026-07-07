from datetime import timedelta

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from inventory.models import InventoryItem
from shop.models import ShopItems
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

    @staticmethod
    @transaction.atomic
    def purchase_item(
        player_id,
        item_id,
        price,
        idempotency_key,
    ):
        """
        Purchase an item exactly once.
        """

        wallet = get_object_or_404(
            Wallet.objects.select_for_update().select_related("player"),
            player__player_id=player_id,
        )

        current_request_hash = create_request_hash(
            {
                "item_id": item_id,
                "price": str(price),
                "player_id": player_id,
            }
        )

        existing = get_existing_request(idempotency_key)

        if existing:

            if existing.request_hash != current_request_hash:
                raise ValidationError(
                    {
                        "error": "IDEMPOTENCY_KEY_CONFLICT",
                        "message": "This idempotency key has already been used with a different request.",
                    }
                )

            return existing.response_body

        shop_item = get_object_or_404(
            ShopItems,
            item_id=item_id,
        )

        if shop_item.price != price:
            raise ValidationError(
                {
                    "error": "PRICE_MISMATCH",
                    "message": "The item price does not match the current server price.",
                }
            )
        if wallet.balance < shop_item.price:
            raise ValidationError(
                {
                    "error": "INSUFFICIENT_FUNDS",
                    "message": "Not enough balance to purchase this item.",
                }
            )
        wallet.balance -= shop_item.price
        wallet.save(update_fields=["balance"])
        inventory_item, created = InventoryItem.objects.get_or_create(
            wallet=wallet,
            shop_item=shop_item,
            defaults={"quantity": 1},
        )

        if not created:
            inventory_item.quantity += 1
            inventory_item.save(update_fields=["quantity"])
        transaction_record = wallet.transactions.create(
            amount=shop_item.price,
            reason=f"Purchased: {shop_item.name}",
            transaction_type=Transaction.TransactionTypes.DEBIT,
            status=Transaction.StatusChoices.SUCCESS,
        )
        response_data = {
            "status": "SUCCESS",
            "message": "Purchase completed successfully.",
            "balance": wallet.balance,
            "item": shop_item.name,
            "quantity": inventory_item.quantity,
        }
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
