from django.db import models
from django.utils import timezone
from django.db import models, transaction
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import CheckConstraint, Q, F
from apps.accounts.models import Customer
from apps.orders.models import Order

# ------------------------------------------------------------------------------------------------------
class Payment(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="payment_order",
        verbose_name="سفارش",
        null=True,
        blank=True,
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="payment_customer",
        verbose_name="مشتری",
    )
    register_date = models.DateTimeField(default=timezone.now, verbose_name="زمان پرداخت ")
    update_date = models.DateTimeField(auto_now=True, verbose_name="زمان ویرایش پرداخت")
    amount = models.DecimalField(verbose_name="مبلغ پرداخت", max_digits=10, decimal_places=0)
    is_finally = models.BooleanField(verbose_name="وضعیت پرداخت", default=False)
    description = models.TextField(verbose_name="توضیحات پرداخت")
    status_code = models.IntegerField(verbose_name="کد وضعیت", null=True, blank=True)
    ref_id = models.CharField(
        max_length=50, verbose_name="شناسه پرداخت", null=True, blank=True, unique=True
    )

    def __str__(self):
        return f"{self.order}\t {self.customer}\t{self.ref_id}"

    class Meta:
        verbose_name = "پرداخت"
        verbose_name_plural = "پرداخت ها"

# --------------------------------------------------------------------------------------------------------
class Wallet(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wallet",
        verbose_name="کاربر",
    )

    balance = models.DecimalField(
        verbose_name="موجودی",
        max_digits=10,
        decimal_places=0,
        default=0,
    )

    class Meta:
        verbose_name = "کیف پول"
        verbose_name_plural = "کیف پول‌ها"
        constraints = [CheckConstraint(check=Q(balance__gte=0), name="balance_gte_zero")]

    def __str__(self):
        return f"کیف پول کاربر: {self.user.name} - موجودی: {self.balance}"

    def deposit(self, amount: int, description: str):

        if amount <= 0:
            raise ValidationError("مبلغ واریز باید مثبت باشد.")

        with transaction.atomic():
            # قفل کردن رکورد برای جلوگیری از race condition
            _wallet = Wallet.objects.select_for_update().get(pk=self.pk)

            # استفاده از F() expression برای آپدیت امن در دیتابیس
            _wallet.balance = F("balance") + amount
            _wallet.save()
            _wallet.refresh_from_db()

            # ثبت رکورد تراکنش
            WalletTransaction.objects.create(
                wallet=_wallet,
                transaction_type=WalletTransaction.TransactionType.DEPOSIT,
                amount=amount,
                running_balance=_wallet.balance,  # موجودی پس از آپدیت
                description=description,
            )

        # رفرش کردن آبجکت فعلی برای نمایش موجودی جدید
        self.refresh_from_db()

    def withdraw(self, amount: int, description: str):
        """
        متد امن برای برداشت وجه از کیف پول
        """
        if amount <= 0:
            raise ValidationError("مبلغ برداشت باید مثبت باشد.")

        with transaction.atomic():
            # قفل کردن رکورد برای جلوگیری از race condition
            _wallet = Wallet.objects.select_for_update().get(pk=self.pk)

            if _wallet.balance < amount:
                raise ValidationError("موجودی کافی نیست.")

            _wallet.balance = F("balance") - amount
            _wallet.save()
            _wallet.refresh_from_db()

            # ثبت رکورد تراکنش
            WalletTransaction.objects.create(
                wallet=_wallet,
                transaction_type=WalletTransaction.TransactionType.WITHDRAW,
                amount=-amount,  # ذخیره مبلغ برداشت به صورت منفی
                running_balance=_wallet.balance,
                description=description,
            )

        self.refresh_from_db()

# --------------------------------------------------------------------------------------------------------
class WalletTransaction(models.Model):

    class TransactionType(models.TextChoices):
        DEPOSIT = "DEPOSIT", "واریز"
        WITHDRAW = "WITHDRAW", "برداشت"
        PURCHASE = "PURCHASE", "خرید"
        REFUND = "REFUND", "بازگشت وجه"

    wallet = models.ForeignKey(
        Wallet, on_delete=models.CASCADE, related_name="transactions", verbose_name="کیف پول"
    )

    transaction_type = models.CharField(
        max_length=10, choices=TransactionType.choices, verbose_name="نوع تراکنش"
    )

    amount = models.DecimalField(verbose_name="مبلغ", max_digits=10, decimal_places=0)

    running_balance = models.DecimalField(
        verbose_name="موجودی پس از تراکنش",
        max_digits=10,
        decimal_places=0,
        help_text="موجودی کیف پول بعد از انجام این تراکنش",
    )

    description = models.TextField(verbose_name="توضیحات", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    class Meta:
        verbose_name = "تراکنش کیف پول"
        verbose_name_plural = "تراکنش‌های کیف پول"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_transaction_type_display()} مبلغ {self.amount} برای {self.wallet.user.username}"

# -----------------------------------------------------------------------------------------------------------------
