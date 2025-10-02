from django.contrib import admin

from .models import Order, OrderDetail, PaymentType


class OrderDetailInline(admin.TabularInline):
    model = OrderDetail
    extra = 2


@admin.register(Order)
class OrderDeatailAdmin(admin.ModelAdmin):
    list_display = (
        "customer",
        "register_date",
        "update_date",
        "is_finally",
        "discount",
    )
    inlines = [OrderDetailInline]


@admin.register(PaymentType)
class PaymentTypeAdmin(admin.ModelAdmin):
    list_display = ["payment_title"]
