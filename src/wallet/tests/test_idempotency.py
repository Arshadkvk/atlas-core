from django.test import TestCase
from rest_framework.test import APIClient

from players.models import Player
from wallet.models import Wallet, IdempotencyKey


class WalletCreditIdempotencyTest(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.player = Player.objects.create(
            player_id="player-1",
            user_name="Test Player",
        )

        self.wallet = Wallet.objects.create(
            player=self.player,
            balance=0,
        )

    def test_duplicate_credit_request_is_processed_once(self):

        url = f"/v1/wallets/{self.player.player_id}/credit/"

        payload = {
            "amount": 100,
            "reason": "Battle Reward",
        }

        headers = {
            "HTTP_IDEMPOTENCY_KEY": "credit-001",
        }

        first_response = self.client.post(
            url,
            payload,
            format="json",
            **headers,
        )

        second_response = self.client.post(
            url,
            payload,
            format="json",
            **headers,
        )

        self.wallet.refresh_from_db()

        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(second_response.status_code, 200)

        self.assertEqual(
            first_response.json(),
            second_response.json(),
        )

        self.assertEqual(self.wallet.balance, 100)

        self.assertEqual(
            self.wallet.transactions.count(),
            1,
        )

        self.assertEqual(
            IdempotencyKey.objects.count(),
            1,
        )
