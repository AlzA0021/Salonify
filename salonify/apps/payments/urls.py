from django.urls import path

from .views import WalletDetailView, WalletChargeView, WalletChargeVerifyView, WalletTransactionsView
# ---------------------------------------------------------------------------------
app_name = "payments"
urlpatterns = [
    # نمایش کیف پول
    path("", WalletDetailView.as_view(), name="detail"),
    # شارژ کیف پول
    path("charge/", WalletChargeView.as_view(), name="charge"),
    # تایید پرداخت شارژ
    path("charge/verify/", WalletChargeVerifyView.as_view(), name="charge_verify"),
    # تاریخچه کامل تراکنش‌ها
    path("transactions/", WalletTransactionsView.as_view(), name="transactions"),
]
