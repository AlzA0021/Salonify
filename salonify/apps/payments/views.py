import logging
import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import View, ListView
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import JsonResponse
from .models import Wallet, WalletTransaction, Payment

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------------------------------------------------
class WalletDetailView(LoginRequiredMixin, View):
    """نمایش جزئیات کیف پول کاربر و تاریخچه تراکنش‌ها"""

    def get(self, request):
        try:
            # دریافت یا ایجاد کیف پول برای کاربر
            wallet, created = Wallet.objects.get_or_create(user=request.user)

            # دریافت تاریخچه تراکنش‌ها (10 تراکنش آخر)
            transactions = WalletTransaction.objects.filter(wallet=wallet).order_by("-created_at")[
                :10
            ]

            context = {"wallet": wallet, "transactions": transactions, "created": created}

            return render(request, "payments/wallet_detail.html", context)

        except Exception as e:
            logger.error(f"Error in WalletDetailView: {e}")
            messages.error(request, "خطا در بارگذاری اطلاعات کیف پول")
            return redirect("accounts:customer_panel")


# ----------------------------------------------------------------------------------------------------------------------
class WalletChargeView(LoginRequiredMixin, View):
    """شارژ کیف پول کاربر"""

    def get(self, request):
        """نمایش فرم شارژ کیف پول"""
        try:
            wallet, created = Wallet.objects.get_or_create(user=request.user)
            context = {"wallet": wallet}
            return render(request, "payments/wallet_charge.html", context)

        except Exception as e:
            logger.error(f"Error in WalletChargeView GET: {e}")
            messages.error(request, "خطا در بارگذاری صفحه شارژ")
            return redirect("payments:detail")

    def post(self, request):
        """پردازش درخواست شارژ کیف پول"""
        try:
            # دریافت amount و حذف کاماها
            amount_str = request.POST.get("amount", "")
            amount_cleaned = amount_str.replace(",", "") if amount_str else ""

            # لاگ کردن مقادیر برای دیباگ
            logger.info(f"Original amount: {amount_str}")
            logger.info(f"Cleaned amount: {amount_cleaned}")

            # اعتبارسنجی مبلغ
            if not amount_cleaned:
                messages.error(request, "لطفاً مبلغ مورد نظر را وارد کنید")
                return redirect("payments:charge")

            try:
                amount = int(amount_cleaned)
                logger.info(f"Parsed amount: {amount}")

                if amount < 10000:  # حداقل 10 هزار تومان
                    messages.error(request, "حداقل مبلغ شارژ 10,000 تومان است")
                    return redirect("payments:charge")

                if amount > 50000000:  # حداکثر 50 میلیون تومان
                    messages.error(request, "حداکثر مبلغ شارژ 50,000,000 تومان است")
                    return redirect("payments:charge")

            except (ValueError, TypeError) as e:
                logger.error(f"Error parsing amount: {e}")
                messages.error(request, "مبلغ وارد شده معتبر نیست")
                return redirect("payments:charge")

            # دریافت یا ایجاد کیف پول
            wallet, created = Wallet.objects.get_or_create(user=request.user)
            logger.info(f"Wallet: {wallet}, Created: {created}")

            # ایجاد پرداخت برای شارژ کیف پول
            payment = Payment.objects.create(
                customer=request.user.customer_profile,
                amount=amount,
                description=f"شارژ کیف پول کاربر {request.user.name}",
                is_finally=False,
            )
            logger.info(f"Payment created: {payment.pk}")

            # ارسال به درگاه زرین‌پال
            return self._redirect_to_zarinpal(request, payment, amount)

        except Exception as e:
            logger.error(f"Error in WalletChargeView POST: {str(e)}", exc_info=True)
            messages.error(request, f"خطا در پردازش درخواست شارژ: {str(e)}")
            return redirect("payments:charge")

    def _redirect_to_zarinpal(self, request, payment, amount):

        try:
            # تعیین آدرس بر اساس محیط (سندباکس یا واقعی)
            if settings.SANDBOX:
                base_url = "https://sandbox.zarinpal.com"
            else:
                base_url = "https://api.zarinpal.com"

            # آدرس جدید برای درخواست پرداخت
            request_url = f"{base_url}/pg/v4/payment/request.json"

            data = {
                "merchant_id": settings.MERCHANT,
                "amount": amount * 10,  # تبدیل تومان به ریال
                "description": f"شارژ کیف پول - کد پرداخت: {payment.id}",
                "callback_url": request.build_absolute_uri("/payments/charge/verify/"),
                "metadata": {
                    "mobile": request.user.mobile_number,
                    "email": request.user.email
                }
            }

            headers = {"Content-Type": "application/json", "Accept": "application/json"}

            logger.info(f"Request to Zarinpal: {request_url}")
            logger.info(f"Request data: {data}")

            response = requests.post(
                request_url,
                json=data,
                headers=headers,
                timeout=10,
            )

            logger.info(f"Zarinpal Response Status: {response.status_code}")
            logger.info(f"Zarinpal Response Content: {response.text}")

            if "application/json" in response.headers.get("Content-Type", ""):
                try:
                    response_data = response.json()

                    # ساختار پاسخ در نسخه جدید API زرین‌پال
                    if response.status_code == 200 and response_data.get("data", {}).get("code") == 100:
                        authority = response_data["data"]["authority"]
                        payment.ref_id = authority
                        payment.save()

                        # آدرس جدید برای انتقال به درگاه پرداخت
                        payment_url = f"{base_url}/pg/StartPay/{authority}"
                        logger.info(f"Redirecting to: {payment_url}")
                        return redirect(payment_url)

                    error_message = response_data.get("errors", {}).get("message", "خطای ناشناخته")
                    logger.error(f"Zarinpal Payment Request Failed: {response_data}")
                    messages.error(request, f"خطا در درگاه پرداخت: {error_message}")

                except (ValueError, KeyError) as json_error:
                    logger.error(f"JSON Decode Error: {json_error}")
                    messages.error(request, "خطا در پردازش پاسخ درگاه پرداخت")

            messages.error(request, "خطا در اتصال به درگاه پرداخت")
            return redirect("payments:charge")

        except Exception as e:
            logger.error(f"Error in Zarinpal redirect: {str(e)}", exc_info=True)
            messages.error(request, "خطا در پردازش پرداخت")
            return redirect("payments:charge")


# ----------------------------------------------------------------------------------------------------------------------
class WalletChargeVerifyView(LoginRequiredMixin, View):
    """تایید پرداخت شارژ کیف پول از زرین‌پال"""

    def get(self, request):
        """بررسی نتیجه پرداخت از زرین‌پال"""
        try:
            authority = request.GET.get("Authority")
            status = request.GET.get("Status")

            logger.info(f"Verification request - Authority: {authority}, Status: {status}")
            logger.info(f"Request GET params: {dict(request.GET)}")

            if not authority:
                messages.error(request, "کد تراکنش معتبر نیست")
                return redirect("payments:detail")

            # یافتن پرداخت بر اساس authority
            try:
                payment = Payment.objects.get(ref_id=authority, customer__user=request.user)
                logger.info(f"Found payment: {payment.id}, Amount: {payment.amount}")
            except Payment.DoesNotExist:
                logger.error(f"Payment not found for authority: {authority}")
                messages.error(request, "تراکنش مورد نظر یافت نشد")
                return redirect("payments:detail")

            if status == "OK":
                return self._verify_payment(request, payment, authority)
            else:
                payment.status_code = -1
                payment.save()
                logger.warning(f"Payment canceled by user - Authority: {authority}")
                messages.error(request, "پرداخت لغو شد")
                return redirect("payments:charge")

        except Exception as e:
            logger.error(f"Error in WalletChargeVerifyView: {str(e)}", exc_info=True)
            messages.error(request, "خطا در تایید پرداخت")
            return redirect("payments:detail")

    def _verify_payment(self, request, payment, authority):
        """تایید پرداخت با زرین‌پال و شارژ کیف پول"""
        try:
            # تعیین آدرس بر اساس محیط (سندباکس یا واقعی)
            if settings.SANDBOX:
                base_url = "https://sandbox.zarinpal.com"
            else:
                base_url = "https://api.zarinpal.com"

            # آدرس جدید برای تایید پرداخت
            verify_url = f"{base_url}/pg/v4/payment/verify.json"

            data = {
                "merchant_id": settings.MERCHANT,
                "amount": int(payment.amount * 10),  # تبدیل تومان به ریال
                "authority": authority,
            }

            headers = {"Content-Type": "application/json", "Accept": "application/json"}

            logger.info(f"Verifying payment - URL: {verify_url}")
            logger.info(f"Verification data: {data}")

            response = requests.post(
                verify_url,
                json=data,
                headers=headers,
                timeout=10,
            )

            logger.info(f"Verification response status: {response.status_code}")
            logger.info(f"Verification response content: {response.text}")

            if "application/json" in response.headers.get("Content-Type", ""):
                try:
                    response_data = response.json()
                    logger.info(f"Verification response JSON: {response_data}")

                    # ساختار پاسخ در نسخه جدید API زرین‌پال
                    if (
                        response.status_code == 200
                        and response_data.get("data", {}).get("code") == 100
                    ):
                        # پرداخت موفق - شارژ کیف پول
                        with transaction.atomic():
                            payment.is_finally = True
                            payment.status_code = 100
                            payment.ref_id = response_data.get("data", {}).get("ref_id", authority)
                            payment.save()

                            # شارژ کیف پول
                            wallet, created = Wallet.objects.get_or_create(user=request.user)
                            wallet.deposit(
                                amount=int(payment.amount),
                                description=f"شارژ از درگاه پرداخت - کد تراکنش: {authority}",
                            )

                        messages.success(
                            request, f"کیف پول شما با مبلغ {payment.amount:,} تومان شارژ شد"
                        )
                        logger.info(
                            f"Payment successful - Authority: {authority}, Amount: {payment.amount}"
                        )
                        return redirect("payments:detail")
                    else:
                        error_code = response_data.get("data", {}).get("code", -2)
                        error_message = response_data.get("errors", {}).get(
                            "message", "خطای ناشناخته"
                        )

                        payment.status_code = error_code
                        payment.save()

                        logger.error(
                            f"Payment verification failed - Code: {error_code}, Message: {error_message}"
                        )
                        messages.error(
                            request,
                            f"تایید پرداخت ناموفق بود: {error_message} (کد خطا: {error_code})",
                        )

                except (ValueError, KeyError) as json_error:
                    logger.error(f"JSON Decode Error in verification: {json_error}")
                    messages.error(request, "خطا در پردازش پاسخ درگاه پرداخت")
            else:
                logger.error(
                    f"Invalid response content type: {response.headers.get('Content-Type')}"
                )
                messages.error(request, "خطا در اتصال به درگاه پرداخت")

            return redirect("payments:charge")

        except requests.exceptions.Timeout:
            logger.error("Zarinpal verification request timed out")
            messages.error(request, "اتصال به درگاه پرداخت timed out شد")
            return redirect("payments:detail")
        except requests.exceptions.ConnectionError:
            logger.error("Zarinpal verification connection error")
            messages.error(request, "خطا در اتصال به درگاه پرداخت")
            return redirect("payments:detail")
        except Exception as e:
            logger.error(f"Error in payment verification: {str(e)}", exc_info=True)
            messages.error(request, "خطا در تایید پرداخت")
            return redirect("payments:detail")


# ----------------------------------------------------------------------------------------------------------------------
class WalletTransactionsView(LoginRequiredMixin, ListView):
    """نمایش تاریخچه کامل تراکنش‌های کیف پول"""

    model = WalletTransaction
    template_name = "payments/wallet_transactions.html"
    context_object_name = "transactions"
    paginate_by = 20

    def get_queryset(self):
        """فیلتر تراکنش‌ها بر اساس کاربر فعلی"""
        try:
            wallet = Wallet.objects.get(user=self.request.user)
            return WalletTransaction.objects.filter(wallet=wallet).order_by("-created_at")
        except Wallet.DoesNotExist:
            return WalletTransaction.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            wallet, created = Wallet.objects.get_or_create(user=self.request.user)
            context["wallet"] = wallet
        except Exception as e:
            logger.error(f"Error getting wallet in transactions view: {e}")
        return context
