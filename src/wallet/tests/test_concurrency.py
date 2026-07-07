from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from django.test import TransactionTestCase
from django.db import OperationalError
from rest_framework.test import APIClient

from inventory.models import InventoryItem
from players.models import Player
from shop.models import ShopItems
from wallet.models import Wallet


class PurchaseConcurrencyTest(TransactionTestCase):

    reset_sequences = True

    def setUp(self):
        self.player = Player.objects.create(
            player_id="player-1",
            user_name="Test Player",
        )
        self.wallet = Wallet.objects.create(
            player=self.player,
            balance=100,
        )
        self.shop_item = ShopItems.objects.create(
            item_id="item-1",
            name="Health Potion",
            description="Restores health",
            price=100,
        )
        self.barrier = Barrier(2)

    def purchase(self, idempotency_key):
        client = APIClient()
        self.barrier.wait()

        for _ in range(5):
            try:
                return client.post(
                    f"/v1/wallets/{self.player.player_id}/purchase/",
                    {
                        "itemId": self.shop_item.item_id,
                        "price": self.shop_item.price,
                    },
                    format="json",
                    HTTP_IDEMPOTENCY_KEY=idempotency_key,
                )
            except OperationalError:
                continue

        return OperationalError("database table is locked")

    def test_only_one_purchase_succeeds_when_two_requests_race_same_balance(self):
        with ThreadPoolExecutor(max_workers=2) as executor:
            future1 = executor.submit(self.purchase, "purchase-1")
            future2 = executor.submit(self.purchase, "purchase-2")

            response1 = future1.result()
            response2 = future2.result()

        self.wallet.refresh_from_db()

        responses = [response1, response2]
        successful_responses = [
            response
            for response in responses
            if hasattr(response, "status_code") and response.status_code == 200
        ]

        self.assertEqual(len(successful_responses), 1)
        self.assertEqual(self.wallet.balance, 0)
        self.assertEqual(InventoryItem.objects.count(), 1)
        self.assertEqual(InventoryItem.objects.get().quantity, 1)
