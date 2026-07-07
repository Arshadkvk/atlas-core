from datetime import timedelta

from rest_framework.exceptions import APIException, ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone

from inventory.models import InventoryItem
from rewards.models import Reward, RewardClaim
from wallet.idempotency import (
    create_idempotency_record,
    create_request_hash,
    get_existing_request,
)
from wallet.models import Transaction, Wallet


class RewardService:

    @staticmethod
    @transaction.atomic
    def claim_reward(
        reward_id,
        player_id,
        idempotency_key,
    ):
        """
        Claim a reward for a player exactly once.
        """

        wallet = get_object_or_404(
            Wallet.objects.select_for_update().select_related("player"),
            player__player_id=player_id,
        )

        current_request_hash = create_request_hash(
            {
                "reward_id": reward_id,
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
        print(reward_id, player_id, idempotency_key)
        reward = get_object_or_404(Reward, reward_id=reward_id)

        if RewardClaim.objects.filter(
            wallet=wallet,
            reward=reward,
        ).exists():
            print("Wallet:", wallet.id)
            print("Reward:", reward.id)
            print(
                "Existing claims:",
                RewardClaim.objects.filter(wallet=wallet, reward=reward).count(),
            )
            raise ValidationError(
                {
                    "error": "REWARD_ALREADY_CLAIMED",
                    "message": "This reward has already been claimed.",
                }
            )

        if reward.reward_type == Reward.RewardType.CURRENCY:

            if reward.currency_amount is None:
                raise APIException(
                    "Reward configuration error: Currency amount is missing."
                )

            wallet.balance += reward.currency_amount
            wallet.save(update_fields=["balance"])

            response_data = {
                "status": "SUCCESS",
                "message": "Currency reward claimed successfully.",
                "reward_type": reward.reward_type,
                "amount_added": reward.currency_amount,
                "balance": wallet.balance,
            }

            transaction_amount = reward.currency_amount

        elif reward.reward_type == Reward.RewardType.ITEM:

            if reward.shop_item is None:
                raise APIException("Reward configuration error: Shop item is missing.")

            inventory_item, created = InventoryItem.objects.get_or_create(
                wallet=wallet,
                shop_item=reward.shop_item,
                defaults={"quantity": 1},
            )

            if not created:
                inventory_item.quantity += 1
                inventory_item.save(update_fields=["quantity"])

            response_data = {
                "status": "SUCCESS",
                "message": "Item reward claimed successfully.",
                "reward_type": reward.reward_type,
                "item_id": reward.shop_item.item_id,
                "item_name": reward.shop_item.name,
            }

            transaction_amount = 0

        else:
            raise ValidationError(
                {
                    "error": "INVALID_REWARD_TYPE",
                    "message": "Unknown reward type.",
                }
            )

        RewardClaim.objects.create(
            wallet=wallet,
            reward=reward,
        )

        transaction_record = wallet.transactions.create(
            amount=transaction_amount,
            reason=f"Reward: {reward.name}",
            transaction_type=Transaction.TransactionTypes.REWARD,
            status=Transaction.StatusChoices.SUCCESS,
        )

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
