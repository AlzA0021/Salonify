from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Wallet, Payment



@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_wallet(sender, instance, created, **kwargs):
    """
    سیگنالی برای ساخت خودکار کیف پول هنگام ایجاد کاربر جدید
    """
    if created:
        Wallet.objects.create(user=instance)

# -----------------------------------------------------------------------------
@receiver(post_save, sender=Payment)
def top_up_wallet_on_successful_payment(sender, instance, created, **kwargs):
    """
    اگر پرداخت موفق بود و برای اولین بار ثبت می‌شد، کیف پول را شارژ کن
    """
    # created=True: برای اینکه فقط یک بار با ساخت رکورد اجرا شود
    # instance.is_finally=True: برای اطمینان از موفقیت پرداخت
    if created and instance.is_finally:
        try:
            # کاربر از طریق مدل مشتری در دسترس است
            user_wallet = instance.customer.user.wallet
            user_wallet.deposit(
                amount=instance.amount,
                description=f"شارژ کیف پول از طریق پرداخت شماره {instance.ref_id}",
            )
        except Wallet.DoesNotExist:
            # مدیریت خطا در صورتی که کاربر کیف پول نداشته باشد
            pass
