from django.urls import path

from .views import (
    WalletCreditView,
    WalletPurchaseView,
    WalletDetailView,
)

urlpatterns = [
    path(
        "<str:player_id>/credit/",
        WalletCreditView.as_view(),
        name="wallet-credit",
    ),
    path(
        "<str:player_id>/purchase/",
        WalletPurchaseView.as_view(),
        name="wallet-purchase",
    ),
    path(
        "<str:player_id>/",
        WalletDetailView.as_view(),
        name="wallet-detail",
    ),
]
