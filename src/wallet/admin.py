from django.contrib import admin

from wallet.models import IdempotencyKey, Transaction, Wallet

# Register your models here.
admin.site.register(Wallet)
admin.site.register(Transaction)
admin.site.register(IdempotencyKey)
