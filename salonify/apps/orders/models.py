import uuid

from django.db import models
from django.utils import timezone

from apps.accounts.models import Customer, Stylist
from apps.salons.models import Salon
from apps.services.models import Services


# --------------------------------------------------------------------------------
class PaymentType(models.Model):
    payment_title = models.CharField(max_length=50, verbose_name="نوع پرداخت")

    def __str__(self):
        return self.payment_title

    class Meta:
        verbose_name = "نوع پرداخت"
        verbose_name_plural = "انواغ روش پرداخت"


# -----------------------------------------------------------------------------------
class Order(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, verbose_name="مشتری", related_name="orders"
    )
    register_date = models.DateField(default=timezone.now, verbose_name="تاریخ ثبت")
    update_date = models.DateField(auto_now=True, verbose_name="تاریخ آپدیت")
    is_finally = models.BooleanField(default=False, verbose_name="نهایی شده")
    is_paid = models.BooleanField(default=False, verbose_name="پرداخت شده")
    order_code = models.UUIDField(
        unique=True, default=uuid.uuid4, verbose_name="کد سفارش", editable=False
    )
    discount = models.IntegerField(null=True, blank=True, verbose_name="تخفیف", default=0)
    description = models.TextField(null=True, blank=True, verbose_name="توضیحات")
    payment_type = models.ForeignKey(
        PaymentType,
        on_delete=models.CASCADE,
        verbose_name="نوع پرداخت",
        related_name="payment",
        null=True,
        blank=True,
    )
    stylist_approved = models.BooleanField(default=False, verbose_name="تایید آرایشگر")

    def get_order_total_price(self):
        sum = 0
        for item in self.order_details1.all():
            sum += item.price

        tax = sum * 0.09
        return sum + tax

    def __str__(self):
        return f"{self.customer}"

    class Meta:
        verbose_name = "سفارش"
        verbose_name_plural = "سفارش ها"


# ---------------------------------------------------------------------------
class OrderDetail(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        verbose_name="سفارش",
        related_name="order_details1",
    )
    service = models.ForeignKey(
        Services,
        on_delete=models.CASCADE,
        verbose_name="خدمت",
        related_name="order_details_services",
    )
    stylist = models.ForeignKey(
        Stylist,
        on_delete=models.CASCADE,
        verbose_name="آرایشگر",
        related_name="order_details_stylist",
    )
    salon = models.ForeignKey(
        Salon,
        on_delete=models.CASCADE,
        verbose_name="سالن",
        related_name="order_details_salon",
    )
    price = models.IntegerField(verbose_name=" قیمت")
    date = models.DateField(verbose_name="تاریخ", null=True)
    time = models.TimeField(verbose_name="زمان", null=True)

    def __str__(self):
        return f"{self.order}"
