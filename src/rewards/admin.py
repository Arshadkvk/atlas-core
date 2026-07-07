from django.contrib import admin

from rewards.models import Reward, RewardClaim

# Register your models here.
admin.site.register(Reward)
admin.site.register(RewardClaim)
