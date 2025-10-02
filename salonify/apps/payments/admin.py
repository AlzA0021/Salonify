from django.contrib import admin
from .models import Payment, Wallet, WalletTransaction


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ("wallet", "transaction_type", "amount", "created_at")

    # این مدل را فقط خواندنی کن
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Payment)
admin.site.register(Wallet)
