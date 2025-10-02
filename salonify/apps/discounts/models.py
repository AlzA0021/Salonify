from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.accounts.models import Stylist
from apps.services.models import Services


# --------------------------------------------------------------------------------------------
class Coupon(models.Model):
    coupon_code = models.CharField(max_length=100, verbose_name="کد تخفیف ")
    start_date = models.DateTimeField(verbose_name="تاریخ شروع")
    end_date = models.DateTimeField(verbose_name="تاریخ پایان")
    discount = models.IntegerField(
        verbose_name="درصد تخفیف",
        validators=(MinValueValidator(0), MaxValueValidator(100)),
    )
    is_active = models.BooleanField(default=False, verbose_name="وضعیت")

    def __str__(self):
        return self.coupon_code

    class Meta:
        verbose_name = "کد تخفیف"
        verbose_name_plural = "کد های تخفیف"


# --------------------------------------------------------------------------------------------
class DiscountBasket(models.Model):
    discount_title = models.CharField(max_length=100, verbose_name="عنوان تخفیف")
    start_date = models.DateTimeField(verbose_name="تاریخ شروع")
    end_date = models.DateTimeField(verbose_name="تاریخ پایان")
    discount = models.IntegerField(
        verbose_name="درصد تخفیف",
        validators=(MinValueValidator(0), MaxValueValidator(100)),
    )
    is_active = models.BooleanField(default=False, verbose_name="وضعیت")

    def __str__(self):
        return self.discount_title

    class Meta:
        verbose_name = "سبد تخفیف "
        verbose_name_plural = "سبدهای تخفیف "


# --------------------------------------------------------------------------------------------
class DiscountBasketDetails(models.Model):
    discount_basket = models.ForeignKey(
        DiscountBasket,
        on_delete=models.CASCADE,
        related_name="discount_basket_details1",
        verbose_name="سبد تخفیف",
    )
    service = models.ForeignKey(
        Services,
        on_delete=models.CASCADE,
        related_name="discount_basket_details2",
        verbose_name="خدمت",
    )
    stylist = models.ForeignKey(
        Stylist,
        on_delete=models.CASCADE,
        related_name="discount_basket_details3",
        verbose_name="آرایشگر",
        null=True,
    )

    class Meta:
        verbose_name = "جزییات سبد تخفیف "
