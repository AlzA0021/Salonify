import utils
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.comments_scores_favories.models import Comments, Scoring
from apps.orders.models import Order, OrderDetail
from apps.salons.models import CustomerNote, Salon

from .forms import (  # StylistUpdateProfileForm,; SalonManagerUpdateProfileForm,
    AddCustomerForm,
    ChangePasswordForm,
    CustomerUpdateProfileForm,
    LoginUserForm,
    RegisterUserForm,
    RememberPasswordForm,
    VerifyRegisterForm,
)
from .models import Customer, CustomUser, SalonManager
from django.http import Http404
from django.db.models import Avg, Sum, F, Q, Value, Case, When, IntegerField


# ----------------------------------------------------------------------------------------------------
class RegisterUserView(View):

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("main:index")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = RegisterUserForm()
        return render(request, "accounts/register.html", {"form": form})

    def post(self, request, *args, **kwargs):
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            active_code = utils.create_random_code(5)
            CustomUser.objects.create_user(  # type: ignore
                mobile_number=data["mobile_number"],
                password=data["password1"],
                active_code=active_code,
            )
            utils.send_sms(
                data["mobile_number"],
                f"کد فعالسازی حساب کاربری شما {active_code} میباشد .",
            )
            request.session["user_session"] = {
                "active_code": str(active_code),
                "mobile_number": data["mobile_number"],
                "remember_password": False,
            }
            messages.success(request, "اطلاعات وارد شد . کد فعالسازی را وارد کنید  ", "success")
            return redirect("accounts:verify")
        messages.error(request, "خطا در انجام ثبت نام ", "danger")
        return render(request, "accounts/register.html", {"form": form})


# ----------------------------------------------------------------------------------------------------
class VerifyRegisterView(View):

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("main:index")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = VerifyRegisterForm()
        return render(request, "accounts/verify.html", {"form": form})

    def post(self, request, *args, **kwargs):
        form = VerifyRegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user_session = request.session["user_session"]
            if user_session["active_code"] == data["active_code"]:
                user = CustomUser.objects.get(mobile_number=user_session["mobile_number"])
                if user_session["remember_password"] is False:
                    user.is_active = True
                    user.active_code = str(utils.create_random_code(5))
                    user.save()
                    messages.success(
                        request,
                        "ثبت نام شما با موفقیت انجام شد . اکانت شما در دسترس است . ",
                        "success",
                    )
                    return redirect("main:index")
                else:
                    return redirect("accounts:change_password")
            else:
                messages.error(request, "کد وارد شده اشتباه است ", "danger")
                return render(request, "accounts/verify.html", {"form": form})
        messages.error(request, "اطلاعات وارد شده اشتباه است ", "danger")
        return render(request, "accounts/verify.html", {"form": form})


# ------------------------------------------------------------------------------------------------------
class LoginUserView(View):
    template_name = "accounts/login.html"
    form_class = LoginUserForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("main:index")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if not form.is_valid():
            messages.error(request, "لطفاً تمام فیلدها را به درستی پر کنید.", "danger")
            return render(request, self.template_name, {"form": form})

        cleaned_data = form.cleaned_data
        user = authenticate(
            username=cleaned_data["mobile_number"], password=cleaned_data["password"]
        )

        if user is None:
            messages.error(request, "شماره موبایل یا رمز عبور اشتباه است.", "danger")
            return render(request, self.template_name, {"form": form})

        if not user.is_active:
            messages.error(request, "حساب کاربری شما فعال نمی‌باشد.", "danger")
            return render(request, self.template_name, {"form": form})

        if user.is_admin:
            messages.warning(request, "لطفاً از پنل ادمین وارد شوید.", "warning")
            return render(request, self.template_name, {"form": form})

        # کاربر با موفقیت وارد می‌شود
        login(request, user)
        messages.success(request, "ورود با موفقیت انجام شد.", "success")

        # # ابتدا بررسی می‌کنیم آیا پارامتر next وجود دارد یا نه
        # next_url = request.GET.get("next")
        # if next_url:
        #     return redirect(next_url)

        # ----------------   بخش جدید: تشخیص نوع کاربر و ریدایرکت   ----------------

        # ✅ قدم ۱: بررسی می‌کنیم آیا کاربر پروفایل آرایشگر یا مدیر سالن دارد
        # related_name برای Stylist تعریف نشده، پس از نام پیش‌فرض 'stylist' استفاده می‌کنیم.
        # related_name برای SalonManager برابر 'salon_manager_profile' است.
        if hasattr(user, "stylist") or hasattr(user, "salon_manager_profile"):
            # اگر آرایشگر یا مدیر سالن بود، به داشبورد منتقل شود
            return redirect("dashboards:salon_manager_dashboard")

        # ✅ قدم ۲: بررسی می‌کنیم آیا کاربر پروفایل مشتری دارد
        # related_name برای Customer برابر 'customer_profile' است.
        elif hasattr(user, "customer_profile"):
            # اگر مشتری بود، به صفحه لیست سالن‌ها منتقل شود
            return redirect("accounts:customer_panel")

        # ✅ قدم ۳: حالت پیش‌فرض
        # اگر کاربر هیچکدام از پروفایل‌های بالا را نداشت (که بعید است)، به یک صفحه اصلی هدایت می‌شود
        return redirect("main:index")


# ----------------------------------------------------------------------------------------------------
class LogoutUserView(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("main:index")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        session_data = request.session.get("order_cart")
        logout(request)
        request.session["order_cart"] = session_data
        return redirect("salons:show_salons")


# ---------------------------------------------------------------------------------------------------
class ChangePasswordView(View):
    # def dispatch(self, request, *args, **kwargs):
    #     if request.user.is_authenticated:
    #         return redirect("main:index")
    #     return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = ChangePasswordForm()
        return render(request, "accounts/change_password.html", {"form": form})

    def post(self, request, *args, **kwargs):
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user_session = request.session["user_session"]
            user = CustomUser.objects.get(mobile_number=user_session["mobile_number"])
            user.set_password(data["password1"])
            user.active_code = str(utils.create_random_code(5))
            user.save()
            messages.success(request, "رمز عبور شما تغییر کرد . ", "success")
            return redirect("accounts:login")
        else:
            messages.error(request, "اطلاعات وارد شده نادرست است ", "danger")
            return render(request, "accounts/change_password.html", {"form": form})


# ---------------------------------------------------------------------------------------------------
class RememberPasswordView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("main:index")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = RememberPasswordForm()
        return render(request, "accounts/remember_password.html", {"form": form})

    def post(self, request, *args, **kwargs):
        form = RememberPasswordForm(request.POST)
        try:
            if form.is_valid():
                data = form.cleaned_data
                user = CustomUser.objects.get(mobile_number=data["mobile_number"])
                active_code = str(utils.create_random_code(5))
                user.active_code = active_code
                user.save()
                utils.send_sms(data["mobile_number"], f"کد تاییده شما {active_code} میباشد .")
                request.session["user_session"] = {
                    "mobile_number": data["mobile_number"],
                    "active_code": active_code,
                    "remember_password": True,
                }
                messages.success(request, "کد دریافتی را وارد کنید ", "success")
                return redirect("accounts:verify")
        except ValueError:
            messages.error(request, "شماره وارد شده موجود نمیباشد ", "danger")
            return render(request, "accounts/remember_password.html", {"form": form})


# ---------------------------------------------------------------------------------------------------
class CustomerUpdateProfileView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        customer = Customer.objects.get(user=user)
        form = CustomerUpdateProfileForm(customer_instance=customer, instance=user)
        return render(
            request,
            "accounts/partials/customer_update_profile.html",
            {"form": form, "image_url": customer.profile_image},
        )

    def post(self, request):
        user = request.user
        customer = Customer.objects.get(user=user)
        form = CustomerUpdateProfileForm(
            request.POST, request.FILES, customer_instance=customer, instance=user
        )

        if form.is_valid():
            form.save()
            messages.success(request, "ویرایش با موفقیت ثبت شد", "success")
            return redirect("accounts:customerProfile")
        else:
            messages.error(request, "اطلاعات وارد شده صحیح نمیباشد", "error")
            return render(
                request,
                "accounts/partials/customer_update_profile.html",
                {"form": form, "image_url": customer.profile_image},
            )


# ---------------------------------------------------------------------------------------------------
class CustomerPanelPageView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # به جای کوئری زدن، مستقیما از پروفایل متصل به request.user استفاده می‌کنیم
        try:
            user = get_object_or_404(
                CustomUser.objects.select_related("wallet", "customer_profile"),
                id=request.user.id,
            )
        except Customer.DoesNotExist:
            # اگر به هر دلیلی پروفایل مشتری برای کاربر وجود نداشت، خطای 404 می‌دهیم
            raise Http404("پروفایل مشتری یافت نشد")

        context = {
            "customer": user.customer_profile,
            "wallet": user.wallet,
        }
        
        return render(request, "accounts/customer_panel.html", context)


# ---------------------------------------------------------------------------------------------------
class CustomerProfilePageView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # ✅ بهینه‌سازی: به جای کوئری جدید، مستقیما از پروفایل متصل به کاربر استفاده می‌کنیم
        try:
            # `customer_profile` همان related_name است که در مدل Customer تعریف کرده‌اید
            customer = request.user.customer_profile
        except Customer.DoesNotExist:
            # اگر پروفایل مشتری برای کاربر وجود نداشت، خطای 404 نمایش می‌دهیم
            raise Http404("پروفایل مشتری یافت نشد")

        context = {
            "customer": customer,
        }
        return render(request, "accounts/customer_profile.html", context)


# ---------------------------------------------------------------------------------------------------
@login_required
@require_POST
def customer_update_profile_image(request):
    """
    ویوی تغییر تصویر پروفایل که توسط AJAX فراخوانی می‌شود.
    اگر فایل تصویر در ارسال وجود داشته باشد، تصویر پروفایل مربوط به کاربر
    بروزرسانی شده و در صورت موفقیت URL جدید تصویر برگردانده می‌شود.
    """
    try:
        customer = Customer.objects.get(user=request.user)
    except Customer.DoesNotExist:
        return JsonResponse({"status": "error", "error": "کاربر مربوطه یافت نشد."})

    if "image" not in request.FILES:
        return JsonResponse({"status": "error", "error": "تصویر ارسال نشده است."})

    image = request.FILES["image"]
    # اعتبارسنجی تصویر (اختیاری)
    customer.profile_image = image
    customer.save()

    return JsonResponse({"status": "success", "image_url": customer.profile_image.url})


# ---------------------------------------------------------------------------------------------------
@csrf_exempt
def add_customer(request, salon_id):
    if request.method == "POST":
        form = AddCustomerForm(request.POST, request.FILES)
        salon_id = int(salon_id)
        if form.is_valid():
            cd = form.cleaned_data
            user = CustomUser.objects.create(
                mobile_number=cd["mobile_number"],
                name=cd["name"],
                family=cd["family"],
                email=cd["email"],
                is_active=True,
            )
            user.save()
            customer = Customer.objects.create(
                user=user,
                profile_image=request.FILES["image"],
                added_by_salon_id=salon_id,
            )
            customer.save()
            return JsonResponse({"success": True, "message": "مشتری با موفقیت ایجاد شد!"})
        else:
            return JsonResponse({"success": False, "errors": form.errors}, status=400)
    return JsonResponse({"error": "درخواست نامعتبر"}, status=400)


# ---------------------------------------------------------------------------------------------------
class DetailCustomerView(View):
    def get(self, request, customer_id):
        # =================================================================
        # ۱. واکشی اطلاعات اولیه (بهینه شده)
        # =================================================================
        salon = get_object_or_404(
            Salon.objects.select_related("salon_manager__user"), salon_manager__user=request.user
        )
        customer = get_object_or_404(Customer.objects.select_related("user"), pk=customer_id)

        # =================================================================
        # ۲. اطلاعات سفارش‌ها و قرارها (یک کوئری جامع)
        # =================================================================
        order_details_qs = (
            OrderDetail.objects.filter(order__customer=customer)
            .select_related("order", "service", "stylist__user")
            .order_by("-date", "-time")
        )

        # =================================================================
        # ۳. محاسبه فروش کل (یک کوئری aggregate)
        # =================================================================
        total_sales_data = Order.objects.filter(customer=customer, is_finally=True).aggregate(
            total=Sum("order_details1__price")
        )
        total_sales = total_sales_data.get("total") or 0

        # =================================================================
        # ۴. نظرات و امتیازات مشتری (یک کوئری جامع)
        # =================================================================
        comments_qs = Comments.objects.filter(comment_user=customer, salon=salon).select_related(
            "stylist__user", "service", "scoring"
        )

        rating_aggregate = comments_qs.filter(scoring__score__isnull=False).aggregate(
            avg_score=Avg("scoring__score")
        )
        avg_rating = (
            round(rating_aggregate["avg_score"], 1)
            if rating_aggregate["avg_score"] is not None
            else "-"
        )

        # =================================================================
        # ۵. یادداشت‌های مشتری و نوبت‌ها (دو کوئری بهینه)
        # =================================================================
        customer_notes_qs = (
            CustomerNote.objects.filter(customer=customer, salon=salon)
            .select_related("created_by")
            .order_by("-created_at")
        )

        appointment_notes_qs = (
            Order.objects.filter(customer=customer)
            .exclude(description__exact="")
            .prefetch_related("order_details1")  # prefetch برای دسترسی به اولین جزئیات سفارش
            .order_by("-update_date")
        )

        context = {
            "hide_dashboardHeader": True,
            "customer": customer,
            "order_details": order_details_qs,
            "completed_appointments": [od for od in order_details_qs if od.order.is_finally],
            "appointments_count": order_details_qs.count(),
            "total_sales": total_sales,
            "canceled_count": 0,
            "no_show_count": 0,
            "rating": avg_rating,
            "wallet_balance": 0,
            "comments_count": comments_qs.count(),
            "customer_ratings": comments_qs,  # ارسال مستقیم queryset بهینه شده
            "customer_notes": customer_notes_qs,
            "customer_notes_count": customer_notes_qs.count(),
            "appointment_notes": appointment_notes_qs,
            "appointment_notes_count": appointment_notes_qs.count(),
        }

        return render(request, "accounts/customer_detail.html", context)

    def post(self, request, customer_id):
        # بهینه‌سازی واکشی اولیه در متد POST
        salon = get_object_or_404(
            Salon.objects.select_related("salon_manager__user"), salon_manager__user=request.user
        )
        customer = get_object_or_404(Customer, pk=customer_id)

        if "note" in request.POST:
            note_text = request.POST.get("note", "").strip()
            note_image = request.FILES.get("note_image", None)
            if note_text:
                CustomerNote.objects.create(
                    salon=salon,
                    customer=customer,
                    note=note_text,
                    note_image=note_image,
                    created_by=request.user,
                )
                messages.success(request, "یادداشت با موفقیت ثبت شد.")

        return redirect("accounts:detail_customer", customer_id=customer_id)


# ---------------------------------------------------------------------------------------------------
@require_POST
@login_required
def delete_customer_note(request, note_id, customer_id):
    user = request.user
    try:
        note = CustomerNote.objects.get(id=note_id)
        # فقط مدیر سالن مربوطه بتواند حذف کند
        if note.salon.salon_manager.user == user:
            note.delete()
            messages.success(request, "یادداشت با موفقیت حذف شد.")
        else:
            messages.error(request, "شما اجازه حذف این یادداشت را ندارید.")
    except CustomerNote.DoesNotExist:
        messages.error(request, "یادداشت مورد نظر یافت نشد.")
    return redirect("accounts:detail_customer", customer_id=customer_id)


# ----------------------------------------------------------------------------------------------------
class CustomerSettingsView(View):
    def get(self, request):
        return render(request,"accounts/customer_settings.html")
