from django.shortcuts import get_object_or_404

from .models import Wallet
from .serializers import WalletSerializer


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
