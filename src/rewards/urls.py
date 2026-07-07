from django.urls import path

from .views import RewardClaimView

urlpatterns = [
    path(
        "<str:reward_id>/claim/",
        RewardClaimView.as_view(),
        name="reward-claim",
    ),
]
