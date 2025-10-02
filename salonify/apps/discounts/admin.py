from django.contrib import admin

from .models import Coupon, DiscountBasket, DiscountBasketDetails


# -----------------------------------------------------------------------------------
@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("coupon_code", "start_date", "end_date", "discount", "is_active")
    list_filter = ("is_active",)


# -----------------------------------------------------------------------------------
class DiscountBasketDetailsInline(admin.TabularInline):
    model = DiscountBasketDetails
    extra = 3


@admin.register(DiscountBasket)
class DiscountBasketAdmin(admin.ModelAdmin):
    list_display = ("discount_title", "start_date", "end_date", "discount", "is_active")
    list_filter = ("is_active",)
    inlines = [
        DiscountBasketDetailsInline,
    ]
