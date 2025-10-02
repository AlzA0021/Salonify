import json
import logging
from collections import defaultdict
from datetime import date, datetime
from datetime import time as dt_time
from datetime import timedelta
import jdatetime
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.gis.geos import Point
from django.db import models, transaction
from django.db.models import Avg, Q, Sum, Value, Count, Case, When, IntegerField, Max, F
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from khayyam import JalaliDate

from apps.accounts.forms import AddCustomerForm
from apps.accounts.models import Customer, SalonManager, Stylist
from apps.orders.models import Order, OrderDetail
from apps.salons.forms import (
    SalonDescriptionForm,
    SalonOpeningHoursForm,
    SalonProfileStep1Form,
    SalonProfileStep2Form,
    SalonsGalleryForm,
)
from apps.salons.models import (
    Salon,
    SalonOpeningHours,
    SalonsGallery,
    SupplementaryInfoView,
)
from apps.services.forms import StylistServiceForm
from apps.services.models import GroupServices, Services
from apps.stylists.forms import (
    EmergencyInfoForm,
    JobDetailsForm,
    StylistProfileForm,
    StylistUserForm,
    StylistTimeOffForm,
)
from apps.stylists.models import EmergencyInfo, JobDetails, StylistSchedule, StylistTimeOff
from django.db.models.functions import TruncDate
from django.contrib.auth.decorators import login_required
from jdatetime import date as jdate, timedelta


# -- ----------------------------------------------------------------
class SalonManagerDashboardView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):

        salon_manager = get_object_or_404(
            SalonManager.objects.select_related("user"), user=request.user
        )

        return render(
            request, "dashboards/salonManager_dashboard.html", {"salon_manager": salon_manager}
        )


# -------------------------------------------------------------------
def salonManagerHeader(request, salon_manager):

    return render(request, "partials/dashboard_header.html", {"salon_manager": salon_manager})


# -------------------------------------------------------------------
class DashboardHomeView(View):
    def get(self, request, *args, **kwargs):
        user = request.user
        # ✅ بهینه‌سازی: سالن فقط یک بار در View اصلی واکشی می‌شود
        salon = get_object_or_404(
            Salon.objects.select_related("salon_manager__user"), salon_manager__user=user
        )
        context = {
            "salon": salon,  
        }
        return render(request, "dashboards/home.html", context)


# -------------------------------------------------------------------
def recently_sales(request, salon):

    # =================================================================
    # ۱. آماده‌سازی تاریخ‌های شمسی
    # =================================================================

    try:
        today_shamsi = jdatetime.date.today()
        seven_days_ago_shamsi = today_shamsi - jdatetime.timedelta(days=6)

        # تبدیل به فرمت رشته برای مقایسه در دیتابیس
        today_shamsi_str = today_shamsi.strftime("%Y-%m-%d")
        seven_days_ago_shamsi_str = seven_days_ago_shamsi.strftime("%Y-%m-%d")

    except Exception as e:

        return render(
            request, "dashboards/partials/recently_sales.html", {"error": "خطا در تبدیل تاریخ"}
        )

    # =================================================================
    # ۲. بررسی وجود داده
    # =================================================================

    all_orders = OrderDetail.objects.filter(salon=salon)

    finalized_orders = OrderDetail.objects.filter(salon=salon, order__is_finally=True)

    # =================================================================
    # ۳. کوئری با تاریخ شمسی
    # =================================================================

    # فرض کنیم فیلد date در دیتابیس رشته تاریخ شمسی است
    date_filtered_query = finalized_orders.filter(
        date__gte=seven_days_ago_shamsi_str, date__lte=today_shamsi_str
    )

    # اگر هنوز هیچ رکوردی پیدا نشد، احتمالاً فرمت تاریخ متفاوت است
    if date_filtered_query.count() == 0:

        # تست فرمت‌های مختلف
        sample_dates = all_orders.values_list("date", flat=True)[:5]

        # اگر تاریخ‌ها در قالب 1404/06/20 هستند
        seven_days_ago_slash = seven_days_ago_shamsi.strftime("%Y-%m-%d")
        today_slash = today_shamsi.strftime("%Y-%m-%d")

        date_filtered_query = finalized_orders.filter(
            date__gte=seven_days_ago_slash, date__lte=today_slash
        )

        if date_filtered_query.count() == 0:
            # تست با بازه گسترده‌تر (30 روز)
            thirty_days_ago = today_shamsi - jdatetime.timedelta(days=30)
            thirty_days_ago_str = thirty_days_ago.strftime("%Y-%m-%d")

            date_filtered_query = finalized_orders.filter(
                date__gte=thirty_days_ago_str, date__lte=today_shamsi_str
            )

            if date_filtered_query.count() == 0:
                thirty_days_ago_slash = thirty_days_ago.strftime("%Y-%m-%d")
                date_filtered_query = finalized_orders.filter(
                    date__gte=thirty_days_ago_slash, date__lte=today_slash
                )

    # کوئری نهایی
    daily_sales_data = (
        date_filtered_query.values("date")
        .annotate(
            sales=Sum("price"),
            appointments=Count("pk"),
        )
        .order_by("date")
    )

    # =================================================================
    # ۴. پردازش داده‌ها
    # =================================================================

    sales_dict = {}
    for item in daily_sales_data:
        date_str = str(item["date"])
        # تبدیل فرمت تاریخ اگر لازم باشد
        if "/" in date_str:
            date_str = date_str.replace("/", "-")

        sales_dict[date_str] = item

    # آماده‌سازی داده‌ها برای چارت
    total_sales = 0
    appointment_count = 0
    chart_data = []

    for i in range(7):
        current_day_shamsi = today_shamsi - jdatetime.timedelta(days=6 - i)
        current_day_str = current_day_shamsi.strftime("%Y-%m-%d")

        day_data = sales_dict.get(current_day_str, {"sales": 0, "appointments": 0})

        daily_sales = day_data.get("sales") or 0
        daily_appointments = day_data.get("appointments") or 0

        # محاسبه مالیات
        daily_sales_with_tax = daily_sales * 1.09

        chart_data.append(
            {
                "date": current_day_str,
                "date_display": current_day_shamsi.strftime("%m-%d"),
                "sales": round(daily_sales_with_tax, 2),
                "appointments": daily_appointments,
            }
        )

        total_sales += daily_sales_with_tax
        appointment_count += daily_appointments

    context = {
        "total_sales": round(total_sales, 2),
        "appointment_count": appointment_count,
        "appointments_value": sum((item.get("sales") or 0) for item in sales_dict.values()),
        "chart_data": json.dumps(chart_data, ensure_ascii=False),
        "salon": salon,
    }

    return render(request, "dashboards/partials/recently_sales.html", context)


# ----------------------------------------------------------------------
def upcoming_appointments(request, salon):
    # =================================================================
    # ۲. آماده‌سازی تاریخ‌های شمسی - اصلاح شده
    # =================================================================

    today_jalali = jdate.today()
    seven_days_later_jalali = today_jalali + timedelta(days=7)

    # تبدیل به string برای استفاده در کوئری Django
    today_jalali_str = today_jalali.strftime("%Y-%m-%d")
    seven_days_later_jalali_str = seven_days_later_jalali.strftime("%Y-%m-%d")

    # فیلتر با تاریخ‌های string
    upcoming_appointments_qs = OrderDetail.objects.filter(
        date__gte=today_jalali_str,
        date__lte=seven_days_later_jalali_str,
        salon=salon,
    )

    # =================================================================
    # ۳. محاسبه شمارش کل
    # =================================================================

    total_counts = upcoming_appointments_qs.aggregate(
        confirmed_count=Count(
            "id", filter=Q(order__stylist_approved=True, order__is_finally=True)
        ),
        canceled_count=Count("id", filter=Q(order__is_finally=False)),
    )

    # =================================================================
    # ۴. آماده‌سازی داده‌های نمودار - روش جایگزین
    # =================================================================

    # روش ۱: استفاده از کوئری ساده و پردازش در Python
    all_appointments = upcoming_appointments_qs.select_related("order").values(
        "date", "order__stylist_approved", "order__is_finally"
    )

    # ایجاد دیکشنری برای محاسبه روزانه
    daily_counts = {}

    # مقداردهی اولیه برای تمام روزها
    for i in range(7):
        current_date = today_jalali + timedelta(days=i)
        date_str = current_date.strftime("%Y-%m-%d")
        daily_counts[date_str] = {"confirmed": 0, "canceled": 0}

    # شمارش داده‌ها
    for appointment in all_appointments:
        appointment_date = appointment["date"]

        # تبدیل به string اگر لازم باشد
        if hasattr(appointment_date, "strftime"):
            date_str = appointment_date.strftime("%Y-%m-%d")
        else:
            date_str = str(appointment_date)

        # بررسی اینکه آیا تاریخ در محدوده ۷ روز است
        if date_str in daily_counts:
            # بررسی وضعیت سفارش
            is_confirmed = (
                appointment["order__stylist_approved"] == True
                and appointment["order__is_finally"] == True
            )
            is_canceled = appointment["order__is_finally"] == False

            if is_confirmed:
                daily_counts[date_str]["confirmed"] += 1
            elif is_canceled:
                daily_counts[date_str]["canceled"] += 1

    # ساخت ساختار داده نهایی
    appointments_chart_data = []
    for i in range(7):
        current_date = today_jalali + timedelta(days=i)
        date_str = current_date.strftime("%Y-%m-%d")

        appointments_chart_data.append(
            {
                "date": date_str,
                "date_display": current_date.strftime("%m-%d"),  # MM-DD برای نمایش
                "confirmed": daily_counts[date_str]["confirmed"],
                "canceled": daily_counts[date_str]["canceled"],
            }
        )

    context = {
        "confirmed_count": total_counts["confirmed_count"],
        "canceled_count": total_counts["canceled_count"],
        "appointments_chart_data": json.dumps(appointments_chart_data),
    }

    return render(request, "dashboards/partials/upcoming_appointments.html", context)


# ----------------------------------------------------------------------
def get_popular_services(request, salon):
    # =================================================================
    # ۱. محاسبه محدوده تاریخ شمسی به صورت رشته
    # =================================================================
    today_jalali = JalaliDate.today()

    # تبدیل تاریخ‌ها به فرمت رشته (مثال: "1403-06-15")
    start_of_current_month_str = f"{today_jalali.year:04d}-{today_jalali.month:02d}-01"

    # ماه بعدی
    if today_jalali.month == 12:
        next_year = today_jalali.year + 1
        next_month = 1
    else:
        next_year = today_jalali.year
        next_month = today_jalali.month + 1
    start_of_next_month_str = f"{next_year:04d}-{next_month:02d}-01"

    # ماه قبلی
    if today_jalali.month == 1:
        last_year = today_jalali.year - 1
        last_month = 12
    else:
        last_year = today_jalali.year
        last_month = today_jalali.month - 1
    start_of_last_month_str = f"{last_year:04d}-{last_month:02d}-01"

    # =================================================================
    # ۲. کوئری با استفاده از تاریخ‌های رشته‌ای
    # =================================================================
    popular_services_data = (
        OrderDetail.objects.filter(
            salon=salon,
            order__is_finally=True,
            date__gte=start_of_last_month_str,
            date__lt=start_of_next_month_str,
        )
        .values("service__pk", "service__service_name")
        .annotate(
            current_month_count=Count(
                Case(
                    When(
                        Q(date__gte=start_of_current_month_str, date__lt=start_of_next_month_str),
                        then=1,
                    ),
                    output_field=IntegerField(),
                )
            ),
            last_month_count=Count(
                Case(
                    When(
                        Q(date__gte=start_of_last_month_str, date__lt=start_of_current_month_str),
                        then=1,
                    ),
                    output_field=IntegerField(),
                )
            ),
            total_count=Count("id"),
        )
        .filter(total_count__gt=0)
        .order_by("-current_month_count", "-last_month_count", "-total_count")[:10]
    )

    # محاسبه درصد تغییر
    services_with_change = []
    for service in popular_services_data:
        current = service["current_month_count"]
        last = service["last_month_count"]

        if last > 0:
            change_percent = round(((current - last) / last) * 100, 1)
        elif current > 0:
            change_percent = 100
        else:
            change_percent = 0

        service["change_percent"] = change_percent
        service["is_growing"] = current > last
        services_with_change.append(service)

    context = {
        "popular_services": services_with_change,
        "current_month": f"{today_jalali.year}/{today_jalali.month}",
    }

    return render(request, "dashboards/partials/popular_services.html", context)


# ---------------------------------------------------------------------
def get_popular_stylists(request, salon):
    # =================================================================
    # ۱. محاسبه محدوده تاریخ شمسی به صورت رشته
    # =================================================================
    today_jalali = JalaliDate.today()

    # تبدیل تاریخ‌ها به فرمت رشته (مثال: "1403-06-15")
    start_of_current_month_str = f"{today_jalali.year:04d}-{today_jalali.month:02d}-01"

    # ماه بعدی
    if today_jalali.month == 12:
        next_year = today_jalali.year + 1
        next_month = 1
    else:
        next_year = today_jalali.year
        next_month = today_jalali.month + 1
    start_of_next_month_str = f"{next_year:04d}-{next_month:02d}-01"

    # ماه قبلی
    if today_jalali.month == 1:
        last_year = today_jalali.year - 1
        last_month = 12
    else:
        last_year = today_jalali.year
        last_month = today_jalali.month - 1
    start_of_last_month_str = f"{last_year:04d}-{last_month:02d}-01"

    # =================================================================
    # ۲. کوئری با استفاده از تاریخ‌های رشته‌ای
    # =================================================================
    popular_stylist_data = (
        OrderDetail.objects.filter(
            salon=salon,
            order__is_finally=True,
            date__gte=start_of_last_month_str,
            date__lt=start_of_next_month_str,
        )
        .values("stylist__user__id", "stylist__user__name", "stylist__user__family")
        .annotate(
            current_month_count=Count(
                Case(
                    When(
                        Q(date__gte=start_of_current_month_str, date__lt=start_of_next_month_str),
                        then=1,
                    ),
                    output_field=IntegerField(),
                )
            ),
            last_month_count=Count(
                Case(
                    When(
                        Q(date__gte=start_of_last_month_str, date__lt=start_of_current_month_str),
                        then=1,
                    ),
                    output_field=IntegerField(),
                )
            ),
            total_count=Count("id"),
        )
        .filter(total_count__gt=0)
        .order_by("-current_month_count", "-last_month_count", "-total_count")[:10]
    )

    # محاسبه درصد تغییر
    stylists_with_change = []
    for stylist in popular_stylist_data:
        current = stylist["current_month_count"]
        last = stylist["last_month_count"]

        if last > 0:
            change_percent = round(((current - last) / last) * 100, 1)
        elif current > 0:
            change_percent = 100
        else:
            change_percent = 0

        stylist["change_percent"] = change_percent
        stylist["is_growing"] = current > last
        stylists_with_change.append(stylist)

    context = {
        "popular_stylists": stylists_with_change,
        "current_month": f"{today_jalali.year}/{today_jalali.month}",
    }

    return render(request, "dashboards/partials/popular_stylists.html", context)


# ---------------------------------------------------------------------
def today_appointment(request, salon):

    today_jalali = JalaliDate.today()
    today_str = today_jalali.strftime("%Y-%m-%d")
    current_time = datetime.now().time()

    today_appointments = (
        OrderDetail.objects.filter(date=today_str, salon=salon, time__gte=current_time)
        .select_related("service", "order__customer__user", "stylist__user")
        .order_by("time")  
    )
    
    context = {
        "today_appointments": today_appointments,
    }
    return render(request, "dashboards/partials/today_appointment.html", context)


# ---------------------------------------------------------------------
def appointments_activity(request, salon):

    today_jalali = JalaliDate.today()
    # اگر تاریخ شما DateField است، از today_jalali.todate() استفاده کنید
    # اگر رشته است، از today_jalali.strftime("%Y-%m-%d")
    today_str = today_jalali.strftime("%Y-%m-%d")

    # ✅ بهینه‌سازی اصلی: واکشی تمام اطلاعات مرتبط در یک کوئری جامع
    upcoming_appointments = (
        OrderDetail.objects.filter(salon=salon, date__gte=today_str)
        .select_related("service", "order__customer__user", "stylist__user")
        .order_by("date", "time")
    )

    # ✅ بهینه‌سازی: گروه‌بندی در پایتون با defaultdict که خواناتر و بهینه‌تر است
    appointments_by_date = defaultdict(list)
    for appointment in upcoming_appointments:
        # تمام اطلاعات از قبل واکشی شده و هیچ کوئری جدیدی زده نمی‌شود
        appointments_by_date[appointment.date.strftime("%Y-%m-%d")].append(
            {
                "id": appointment.pk,
                "service_name": appointment.service.service_name,
                "customer_name": appointment.order.customer.get_fullName(),
                "time": appointment.time,
                "duration": f"{appointment.service.duration_minutes}min",
                "stylist_name": appointment.stylist.get_fullName(),
                "price": appointment.price,
                "status": "تأیید شده" if appointment.order.stylist_approved else "در انتظار تأیید",
                "date": appointment.date,
            }
        )

    context = {
        # تبدیل defaultdict به dict معمولی برای ارسال به تمپلیت
        "appointments_by_date": dict(appointments_by_date),
    }

    return render(request, "dashboards/partials/appointments_activity.html", context)


# ----------------------------------------------------------------------
class SalonsCustomersPageView(LoginRequiredMixin, View):
    """
    Main view for the salon's customer management page.
    This view is responsible for fetching ALL necessary data.
    """

    main_template = "dashboards/salonsCustomersPage.html"
    partial_template = "dashboards/partials/salons_customers.html"

    def get(self, request, *args, **kwargs):
        # 1. Fetch the salon object efficiently ONCE
        salon = get_object_or_404(
            Salon.objects.select_related("salon_manager__user"), salon_manager__user=request.user
        )

        # 2. Get the IDs of customers who have ordered from this salon
        customer_ids_from_orders = (
            OrderDetail.objects.filter(salon=salon)
            .values_list("order__customer__user_id", flat=True)
            .distinct()
        )

        # 3. Fetch all relevant customers in a single, optimized query
        #    - Use select_related('user') to prevent N+1 queries in the template.
        salons_customers_qs = (
            Customer.objects.filter(
                Q(user_id__in=customer_ids_from_orders) | Q(added_by_salon=salon)
            )
            .select_related("user")
            .distinct()
        )

        # Decide whether to render the full page or just the partial
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            # This is an AJAX request (e.g., from search/filter), render only the partial
            return render(request, self.partial_template, {"customers": salons_customers_qs})

        # This is a standard page load, render the full page
        context = {
            "salon": salon,
            "customers": salons_customers_qs,
            "form": AddCustomerForm(),  # Assuming you need this for a modal
        }
        return render(request, self.main_template, context)


# ----------------------------------------------------------------------------------------
class OnlineBookingView(View):
    def get(self, request, *args, **kwargs):

        context = {}

        return render(request, "dashboards/online_booking.html", context)


# -----------------------------------------------------------------------------------------
@login_required
def salon_profile_creator(request):
    """
    این View بررسی می‌کند که آیا مدیر سالن لاگین کرده پروفایلی برای سالن خود ساخته است یا نه،
    و او را به صفحه مناسب هدایت می‌کند.
    """
    # ابتدا بررسی می‌کنیم که آیا کاربر پروفایل مدیر سالن دارد یا نه.
    # این کار از خطای 404 برای کاربرانی که مدیر نیستند، جلوگیری می‌کند.
    if not hasattr(request.user, "salon_manager_profile"):
        # می‌توانید کاربر را به صفحه اصلی یا صفحه خطا هدایت کنید.
        return redirect("main:index")

    # ✅ بهینه‌سازی: با یک کوئری exists() بهینه، وجود سالن را بررسی می‌کنیم.
    # .exists() بسیار سریع‌تر از واکشی کامل آبجکت است.
    has_salon = Salon.objects.filter(salon_manager__user=request.user).exists()

    if has_salon:
        # اگر سالن از قبل وجود دارد، به صفحه پروفایل سالن هدایت شو
        return redirect("dashboards:salon_profile")
    else:
        # اگر سالن وجود ندارد، به مرحله اول ساخت پروفایل هدایت شو
        return redirect("dashboards:salon_profile_creator_step1")


# ------------------------------------------------------------------------------------------
# مرحله 1: ساخت اولیه سالن (نام و شماره)
class SalonProfileCreatorStep1View(View):
    def get(self, request, *args, **kwargs):
        form = SalonProfileStep1Form()
        context = {
            "hide_dashboardNavbar": True,
            "form": form,
        }
        return render(request, "dashboards/salon_profile_creator_step1.html", context)

    def post(self, request, *args, **kwargs):
        user = request.user
        salon_manager = get_object_or_404(SalonManager, user=user)
        form = SalonProfileStep1Form(request.POST)
        if form.is_valid():
            salon, created = Salon.objects.get_or_create(
                salon_manager=salon_manager,
                defaults={
                    "salon_name": form.cleaned_data["salon_name"],
                    "phone_number": form.cleaned_data["phone_number"],
                },
            )
            if not created:
                # اگر قبلاً سالن ساخته شده، اطلاعات را به‌روزرسانی کن
                salon.salon_name = form.cleaned_data["salon_name"]
                salon.phone_number = form.cleaned_data["phone_number"]
                salon.save()
            return redirect("dashboards:salon_profile_creator_step2")
        else:
            context = {
                "hide_dashboardNavbar": True,
                "form": form,
            }
            return render(request, "dashboards/salon_profile_creator_step1.html", context)


# ------------------------------------------------------------------------------------------
# مرحله 2: ثبت اطلاعات لوکیشن
class SalonProfileCreatorStep2View(View):
    def get(self, request, *args, **kwargs):
        form = SalonProfileStep2Form()
        context = {
            "hide_dashboardNavbar": True,
            "form": form,
        }
        return render(request, "dashboards/salon_profile_creator_step2.html", context)

    def post(self, request, *args, **kwargs):
        user = request.user
        salon_manager = get_object_or_404(SalonManager, user=user)
        salon = get_object_or_404(Salon, salon_manager=salon_manager)
        form = SalonProfileStep2Form(request.POST)
        if form.is_valid():
            latitude = form.cleaned_data["latitude"]
            longitude = form.cleaned_data["longitude"]
            salon.zone = form.cleaned_data["zone"]
            salon.neighborhood = form.cleaned_data["neighborhood"]
            salon.address = form.cleaned_data["address"]
            if hasattr(salon, "location"):
                salon.location = Point(float(longitude), float(latitude))
            salon.save()
            return redirect("dashboards:salon_profile_creator_step3")
        else:
            context = {
                "hide_dashboardNavbar": True,
                "form": form,
            }
            return render(request, "dashboards/salon_profile_creator_step2.html", context)


# ------------------------------------------------------------------------------------------
class SalonProfileCreatorStep3View(LoginRequiredMixin, View):
    form_class = SalonOpeningHoursForm
    template_name = "dashboards/salon_profile_creator_step3.html"

    def get(self, request, *args, **kwargs):
        # ✅ بهینه‌سازی: واکشی سالن و مدیر آن در یک کوئری واحد
        salon = get_object_or_404(
            Salon.objects.select_related("salon_manager__user"), salon_manager__user=request.user
        )

        # واکشی ساعات کاری موجود و تبدیل آن به دیکشنری برای دسترسی سریع
        opening_hours = SalonOpeningHours.objects.filter(salon=salon)
        initial_data = {}
        for oh in opening_hours:
            day_num = oh.day_of_week
            initial_data[f"day_{day_num}_active"] = not oh.is_closed
            if not oh.is_closed:
                initial_data[f"day_{day_num}_open_time"] = oh.open_time
                initial_data[f"day_{day_num}_close_time"] = oh.close_time

        # پر کردن فرم با مقادیر اولیه
        form = self.form_class(initial=initial_data)

        context = {
            "hide_dashboardNavbar": True,
            "form": form,  # نام context را به form تغییر دادم تا با بقیه view ها یکسان باشد
            "salon": salon,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        salon = get_object_or_404(
            Salon.objects.select_related("salon_manager__user"), salon_manager__user=request.user
        )
        form = self.form_class(request.POST)

        if form.is_valid():
            # ✅ بهینه‌سازی: استفاده از transaction.atomic برای تضمین یکپارچگی داده‌ها
            with transaction.atomic():
                # به جای حذف و ساخت مجدد، از update_or_create استفاده می‌کنیم
                for day_num in range(1, 8):
                    is_active = form.cleaned_data.get(f"day_{day_num}_active")

                    defaults = {
                        "is_closed": not is_active,
                        "open_time": (
                            form.cleaned_data.get(f"day_{day_num}_open_time")
                            if is_active
                            else None
                        ),
                        "close_time": (
                            form.cleaned_data.get(f"day_{day_num}_close_time")
                            if is_active
                            else None
                        ),
                    }

                    SalonOpeningHours.objects.update_or_create(
                        salon=salon, day_of_week=day_num, defaults=defaults
                    )

            messages.success(request, "ساعات کاری با موفقیت ذخیره شدند.")
            return redirect("dashboards:salon_profile_creator_step4")

        context = {
            "hide_dashboardNavbar": True,
            "form": form,
            "salon": salon,
        }
        return render(request, self.template_name, context)


# ------------------------------------------------------------------------------------------
def salon_profile_creator_step4(request):

    context = {
        "hide_dashboardNavbar": True,
    }

    return render(request, "dashboards/salon_profile_creator_step4.html", context)


# ------------------------------------------------------------------------------------------
def salon_profile_creator_step5(request):

    context = {
        "hide_dashboardNavbar": True,
    }

    return render(request, "dashboards/salon_profile_creator_step5.html", context)


# -------------------------------------------------------------------------------------------
class SalonProfileCreatorStep6View(LoginRequiredMixin, View):
    form_class = SalonsGalleryForm
    template_name = "dashboards/salon_profile_creator_step6.html"

    def get(self, request, *args, **kwargs):
        # ✅ بهینه‌سازی: واکشی سالن و مدیر آن در یک کوئری واحد
        salon = get_object_or_404(
            Salon.objects.select_related("salon_manager__user"), salon_manager__user=request.user
        )

        # بررسی درخواست تنظیم تصویر کاور (منطق به یک متد جداگانه منتقل شد)
        cover_id = request.GET.get("set_cover")
        if cover_id:
            return self.handle_set_cover(request, salon, cover_id)

        gallery_images = SalonsGallery.objects.filter(salon=salon).order_by("-is_cover", "order")
        form = self.form_class()

        context = {
            "hide_dashboardNavbar": True,
            "salon": salon,
            "gallery_images": gallery_images,
            "form": form,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        salon = get_object_or_404(
            Salon.objects.select_related("salon_manager__user"), salon_manager__user=request.user
        )
        form = self.form_class(request.POST, request.FILES)

        if form.is_valid():
            try:
                with transaction.atomic():
                    gallery_item = form.save(commit=False)
                    gallery_item.salon = salon

                    gallery_stats = SalonsGallery.objects.filter(salon=salon).aggregate(
                        max_order=Max("order"), count=Count("id")
                    )

                    last_order = gallery_stats.get("max_order") or -1
                    gallery_item.order = last_order + 1

                    # اگر اولین تصویر بود
                    if gallery_stats.get("count") == 0:
                        gallery_item.is_cover = True

                    gallery_item.save()

                    # ⬇️ تغییر اصلی: اگر تصویر جدید کاور است، بنر سالن را آپدیت کن
                    if gallery_item.is_cover:
                        salon.banner_image = gallery_item.salon_image
                        salon.save(update_fields=["banner_image"])

                    messages.success(request, "تصویر با موفقیت به گالری اضافه شد.")
                    return redirect("dashboards:salon_profile_creator_step6")

            except Exception as e:
                messages.error(request, f"خطایی در هنگام ذخیره تصویر رخ داد: {e}")
        else:
            messages.error(
                request, "آپلود ناموفق بود. لطفاً شرایط فایل (نوع، حجم و ابعاد) را بررسی کنید."
            )

        gallery_images = SalonsGallery.objects.filter(salon=salon).order_by("-is_cover", "order")
        context = {
            "hide_dashboardNavbar": True,
            "salon": salon,
            "gallery_images": gallery_images,
            "form": form,
        }
        return render(request, self.template_name, context)

    def handle_set_cover(self, request, salon, cover_id):
        with transaction.atomic():
            try:
                # ۱. ابتدا آبجکت تصویر جدید را پیدا می‌کنیم
                new_cover_image = SalonsGallery.objects.get(id=cover_id, salon=salon)

                # ۲. ⬇️ تغییر اصلی: بنر سالن را آپدیت می‌کنیم
                salon.banner_image = new_cover_image.salon_image
                salon.save(update_fields=["banner_image"])

                # ۳. تمام تصاویر دیگر را از حالت کاور خارج می‌کنیم
                salon.gallery_images.update(is_cover=False)

                # ۴. تصویر جدید را به عنوان کاور تنظیم می‌کنیم
                new_cover_image.is_cover = True
                new_cover_image.save(update_fields=["is_cover"])

                messages.success(request, "تصویر کاور با موفقیت تنظیم شد.")

            except SalonsGallery.DoesNotExist:
                messages.error(request, "تصویر مورد نظر یافت نشد.")

        return redirect("dashboards:salon_profile_creator_step6")


#            #-------------------------------------#            #


@transaction.atomic
def delete_salon_image(request, image_id):
    if request.method == "POST":
        salon = get_object_or_404(
            Salon.objects.select_related("salon_manager__user"), salon_manager__user=request.user
        )
        image = get_object_or_404(SalonsGallery, id=image_id, salon=salon)

        was_cover = image.is_cover
        image.delete()

        if was_cover:
            first_image = SalonsGallery.objects.filter(salon=salon).order_by("order").first()
            if first_image:
                first_image.is_cover = True
                first_image.save()

                # ⬇️ تغییر اصلی: بنر سالن را با تصویر جدید آپدیت کن
                salon.banner_image = first_image.salon_image
            else:
                # ⬇️ تغییر اصلی: اگر تصویری باقی نماند، بنر را خالی کن
                salon.banner_image = None  # یا یک تصویر پیش‌فرض

            salon.save(update_fields=["banner_image"])

        messages.success(request, "تصویر با موفقیت حذف شد.")
    return redirect("dashboards:salon_profile_creator_step6")


# -------------------------------------------------------------------------------------------
class SalonProfileCreatorStep7View(LoginRequiredMixin, View):
    template_name = "dashboards/salon_profile_creator_step7.html"
    # تعریف دسته‌بندی‌ها در سطح کلاس
    categories = {
        "highlights": [
            {
                "title": "مناسب حیوانات خانگی",
                "icon_class": "fas fa-paw",
                "description": "سالن ما از حیوانات خانگی استقبال می‌کند و محیطی دوستانه برای آنها فراهم می‌کند",
            },
            {
                "title": "فقط بزرگسالان",
                "icon_class": "fas fa-users",
                "description": "این مکان مخصوص افراد بالای ۱۸ سال است",
            },
            {
                "title": "مناسب کودکان",
                "icon_class": "fas fa-child",
                "description": "محیطی امن و مناسب برای خدمات‌رسانی به کودکان",
            },
            {
                "title": "دسترسی با ویلچر",
                "icon_class": "fas fa-wheelchair",
                "description": "مجهز به امکانات دسترسی برای افراد دارای معلولیت جسمی",
            },
        ],
        "values": [
            {
                "title": "فقط محصولات ارگانیک",
                "icon_class": "fas fa-leaf",
                "description": "استفاده از محصولات کاملاً طبیعی و ارگانیک",
            },
            {
                "title": "فقط محصولات گیاهی",
                "icon_class": "fas fa-seedling",
                "description": "استفاده انحصاری از محصولات با منشأ گیاهی",
            },
            {
                "title": "دوستدار محیط زیست",
                "icon_class": "fas fa-recycle",
                "description": "متعهد به حفظ محیط زیست و استفاده از محصولات سازگار با طبیعت",
            },
            {
                "title": "حامی LGBTQ+",
                "icon_class": "fas fa-rainbow",
                "description": "محیطی امن و حمایت‌کننده برای همه افراد",
            },
            {
                "title": "کسب و کار سیاه‌پوستان",
                "icon_class": "fas fa-user-friends",
                "description": "کسب و کار متعلق به و اداره شده توسط افراد سیاه‌پوست",
            },
            {
                "title": "کسب و کار زنان",
                "icon_class": "fas fa-venus",
                "description": "کسب و کار متعلق به و اداره شده توسط زنان",
            },
            {
                "title": "کسب و کار آسیایی‌ها",
                "icon_class": "fas fa-globe-asia",
                "description": "کسب و کار متعلق به و اداره شده توسط افراد آسیایی",
            },
            {
                "title": "کسب و کار اسپانیایی‌تبارها",
                "icon_class": "fas fa-globe-americas",
                "description": "کسب و کار متعلق به و اداره شده توسط افراد اسپانیایی‌تبار",
            },
            {
                "title": "کسب و کار بومیان",
                "icon_class": "fas fa-feather-alt",
                "description": "کسب و کار متعلق به و اداره شده توسط بومیان",
            },
        ],
        "amenities": [
            {
                "title": "پارکینگ",
                "icon_class": "fas fa-car",
                "description": "دارای پارکینگ اختصاصی برای مراجعه‌کنندگان",
            },
            {
                "title": "نزدیک به حمل و نقل عمومی",
                "icon_class": "fas fa-bus",
                "description": "دسترسی آسان به وسایل حمل و نقل عمومی",
            },
            {
                "title": "دوش",
                "icon_class": "fas fa-shower",
                "description": "مجهز به امکانات دوش",
            },
            {
                "title": "کمد قفل‌دار",
                "icon_class": "fas fa-lock",
                "description": "دارای کمدهای امن برای نگهداری وسایل شخصی",
            },
            {
                "title": "حوله حمام",
                "icon_class": "fas fa-bath",
                "description": "ارائه حوله تمیز به مراجعه‌کنندگان",
            },
            {
                "title": "استخر شنا",
                "icon_class": "fas fa-swimming-pool",
                "description": "دارای استخر شنا مجهز",
            },
            {
                "title": "سونا",
                "icon_class": "fas fa-hot-tub",
                "description": "مجهز به سونای خشک و بخار",
            },
        ],
    }

    def get_salon(self):
        """متد کمکی برای واکشی بهینه سالن و کش کردن آن در request."""
        if not hasattr(self.request, "_cached_salon"):
            self.request._cached_salon = get_object_or_404(
                Salon.objects.select_related("salon_manager__user"),
                salon_manager__user=self.request.user,
            )
        return self.request._cached_salon

    def get(self, request, *args, **kwargs):
        salon = self.get_salon()

        # واکشی اطلاعات موجود برای نمایش در تمپلیت
        existing_info = SupplementaryInfoView.objects.filter(salon=salon)
        selected_items = {item.title for item in existing_info}

        context = {
            "hide_dashboardNavbar": True,
            "categories": self.categories,
            "selected_items": selected_items,
            "salon": salon,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        salon = self.get_salon()
        selected_items_from_form = request.POST.getlist("selected_items")

        # ساخت دیکشنری کامل از تمام ویژگی‌های ممکن برای دسترسی سریع
        all_items_map = {
            f"{item['title']}|{item['icon_class']}": item
            for category in self.categories.values()
            for item in category
        }

        # ✅ بهینه‌سازی: تمام عملیات دیتابیس در یک تراکنش اتمی
        with transaction.atomic():
            # ابتدا تمام رکوردهای قبلی این سالن را حذف می‌کنیم
            salon.supplementary_info.all().delete()

            # آماده‌سازی لیستی از آبجکت‌های جدید برای ساخت
            new_info_objects = []
            for item_key in selected_items_from_form:
                if item_key in all_items_map:
                    item_data = all_items_map[item_key]
                    new_info_objects.append(
                        SupplementaryInfoView(
                            salon=salon,
                            title=item_data["title"],
                            icon_class=item_data["icon_class"],
                            description=item_data["description"],
                            is_active=True,
                        )
                    )

            # ✅ بهینه‌سازی اصلی: استفاده از bulk_create برای درج تمام رکوردها در یک کوئری
            if new_info_objects:
                SupplementaryInfoView.objects.bulk_create(new_info_objects)

        messages.success(request, "ویژگی‌های سالن با موفقیت ذخیره شدند.")
        return redirect("dashboards:salon_profile_creator_step8")


# --------------------------------------------------------------------------------------------
class SalonProfileCreatorStep8View(LoginRequiredMixin, View):
    form_class = SalonDescriptionForm
    template_name = "dashboards/salon_profile_creator_step8.html"

    def get_salon(self):
        """
        یک متد کمکی برای واکشی سالن به صورت بهینه و جلوگیری از تکرار کد.
        """

        # getattr برای جلوگیری از خطا در صورت عدم وجود salon در request
        if not hasattr(self.request, "_cached_salon"):
            self.request._cached_salon = get_object_or_404(
                Salon.objects.select_related("salon_manager__user"),
                salon_manager__user=self.request.user,
            )
        return self.request._cached_salon

    def get_context_data(self, **kwargs):
        """
        یک متد کمکی برای ساخت context و جلوگیری از تکرار کد.
        """
        context = {
            "hide_dashboardNavbar": True,
            "salon": self.get_salon(),
        }
        context.update(kwargs)
        return context

    def get(self, request, *args, **kwargs):
        salon = self.get_salon()
        form = self.form_class(instance=salon)
        context = self.get_context_data(form=form)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        salon = self.get_salon()
        form = self.form_class(request.POST, instance=salon)

        if form.is_valid():
            form.save()
            messages.success(request, "توضیحات سالن با موفقیت ذخیره شد.")
            return redirect("dashboards:salon_profile_creator_step9")

        # اگر فرم نامعتبر بود
        context = self.get_context_data(form=form)
        messages.error(request, "لطفاً خطاهای فرم را برطرف کنید.", "danger")
        return render(request, self.template_name, context)


# --------------------------------------------------------------------------------------------
def salon_profile_creator_step9(request):
    context = {
        "hide_dashboardNavbar": True,
    }

    return render(request, "dashboards/salon_profile_creator_step9.html", context)


# ---------------------------------------------------------------------------------------------
class SalonProfileCreatorStep10View(LoginRequiredMixin, View):
    template_name = "dashboards/salon_profile_creator_step10.html"

    def get_salon(self):
        """متد کمکی برای واکشی بهینه سالن و کش کردن آن در request."""
        if not hasattr(self.request, "_cached_salon"):
            self.request._cached_salon = get_object_or_404(
                Salon.objects.select_related("salon_manager__user"),
                salon_manager__user=self.request.user,
            )
        return self.request._cached_salon

    def get(self, request, *args, **kwargs):
        salon = self.get_salon()
        context = {
            "hide_dashboardNavbar": True,
            "salon": salon,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        salon = self.get_salon()

        # ✅ بهینه‌سازی: استفاده از متد update که فقط یک کوئری به دیتابیس می‌زند
        # و از واکشی مجدد آبجکت جلوگیری می‌کند.
        Salon.objects.filter(pk=salon.pk).update(is_active=True)

        messages.success(request, "سالن شما با موفقیت فعال شد!")
        return redirect("dashboards:salon_profile_creator_finalStep")


# ---------------------------------------------------------------------------------------------
@login_required
def salon_profile_creator_finalStep(request):
    """
    این View صفحه نهایی موفقیت‌آمیز بودن ساخت پروفایل را نمایش می‌دهد.
    """
    # ✅ بهینه‌سازی: واکشی سالن و مدیر آن در یک کوئری واحد با select_related
    salon = get_object_or_404(
        Salon.objects.select_related("salon_manager__user"), salon_manager__user=request.user
    )

    context = {
        "hide_dashboardNavbar": True,
        "salon": salon,
    }
    return render(request, "dashboards/salon_profile_creator_finalStep.html", context)


# ----------------------------------------------------------------------------------------------
class SalonProfileView(View):
    def get(self, request):
        # ✅ بهینه‌سازی: واکشی سالن و محاسبه آمار در یک کوئری جامع
        salon_with_stats = get_object_or_404(
            Salon.objects.select_related("salon_manager__user").annotate(
                # محاسبه میانگin امتیاز نظرات تایید شده
                avg_score=Avg(
                    "comments_salon__scoring__score", filter=Q(comments_salon__is_active=True)
                ),
                # شمارش تعداد نظرات تایید شده
                reviews_count=Count("comments_salon", filter=Q(comments_salon__is_active=True)),
            ),
            salon_manager__user=request.user,
        )

        context = {
            "salon": salon_with_stats,
        }
        return render(request, "dashboards/salon_profile_view.html", context)


# --------------------------------------------------------------------------------------------
class CatalogView(View):
    def get(self, request):

        context = {}
        return render(request, "dashboards/catalog.html", context)


# ----------------------------------------------------------------------------------------------
from django.db.models import Min, Max, Prefetch
from collections import defaultdict


# =================================================================
# VIEW اصلی منوی خدمات (کاملاً بازنویسی شده)
# =================================================================
class ServiceMenuView(LoginRequiredMixin, View):
    def get(self, request):
        salon = get_object_or_404(
            Salon.objects.select_related("salon_manager__user"), salon_manager__user=request.user
        )

        # ✅ بهینه‌سازی اصلی: استفاده از مسیر صحیح در annotate
        services_qs = (
            Services.objects.filter(services_of_salon=salon, is_active=True)
            .prefetch_related("service_group")
            .annotate(
                # مسیر صحیح: مستقیم از Service به ServicePrice
                min_price=Min("service_prices__price"),
                max_price=Max("service_prices__price"),
            )
        )

        # گروه‌بندی در پایتون (بدون تغییر)
        services_by_group = defaultdict(list)
        for service in services_qs:
            if not service.service_group.exists():
                services_by_group["دسته‌بندی نشده"].append(service)
            else:
                for group in service.service_group.all():
                    services_by_group[group].append(service)

        context = {
            "services_by_group": dict(services_by_group),
            "total_services_count": len(services_qs),
            "salon": salon,
        }
        return render(request, "dashboards/service_menu.html", context)


# =================================================================
# VIEW افزودن خدمت (بهینه شده)
# =================================================================
class AddServicesView(LoginRequiredMixin, View):
    form_class = StylistServiceForm
    template_name = "dashboards/add_services.html"

    def get(self, request):
        salon = get_object_or_404(
            Salon.objects.select_related("salon_manager__user"), salon_manager__user=request.user
        )
        form = self.form_class(salon=salon)
        context = {
            "form": form,
            "salon": salon,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        salon = get_object_or_404(
            Salon.objects.select_related("salon_manager__user"), salon_manager__user=request.user
        )
        form = self.form_class(request.POST, request.FILES, salon=salon)

        if form.is_valid():
            # منطق save شما در فرم قرار دارد که باید بررسی شود
            form.save(commit=True, salon=salon)
            messages.success(request, "خدمت با موفقیت اضافه شد.")
            return redirect("dashboards:service_menu")

        context = {
            "form": form,
            "salon": salon,
        }
        return render(request, self.template_name, context)


# =================================================================
# VIEW ویرایش خدمت (بهینه شده)
# =================================================================
class EditServiceView(LoginRequiredMixin, View):
    form_class = StylistServiceForm
    template_name = "dashboards/edit_service.html"

    def get(self, request, service_id):
        salon = get_object_or_404(
            Salon.objects.select_related("salon_manager__user"), salon_manager__user=request.user
        )
        service = get_object_or_404(Services, id=service_id, services_of_salon=salon)
        form = self.form_class(instance=service, salon=salon)
        context = {
            "form": form,
            "service": service,
            "salon": salon,
        }
        return render(request, self.template_name, context)

    def post(self, request, service_id):
        salon = get_object_or_404(
            Salon.objects.select_related("salon_manager__user"), salon_manager__user=request.user
        )
        service = get_object_or_404(Services, id=service_id, services_of_salon=salon)
        form = StylistServiceForm(request.POST, request.FILES, instance=service, salon=salon)

        if form.is_valid():
            # ✅ بهینه‌سازی: پاس دادن پارامترهای لازم به متد save سفارشی شما
            form.save(commit=True, salon=salon)
            messages.success(request, "خدمت با موفقیت ویرایش شد.")
            return redirect("dashboards:service_menu")
        else:
            # اگر فرم نامعتبر بود، با خطاها به کاربر نمایش داده می‌شود
            messages.error(request, "لطفاً خطاهای فرم را برطرف کنید.")
            context = {
                "form": form,
                "service": service,
                "salon": salon,
            }
            return render(request, "dashboards/edit_service.html", context)


# =================================================================
# VIEW های آرشیو و حذف (بهینه شده)
# =================================================================
@login_required
def archieve_service(request, service_id):
    salon = get_object_or_404(Salon, salon_manager__user=request.user)
    # استفاده از update برای یک کوئری بهینه
    updated_count = Services.objects.filter(id=service_id, services_of_salon=salon).update(
        is_active=False
    )
    if updated_count > 0:
        messages.success(request, "خدمت با موفقیت آرشیو شد.")
    else:
        messages.error(request, "خدمت مورد نظر یافت نشد.")
    return redirect("dashboards:service_menu")


@login_required
def remove_service(request, service_id):
    salon = get_object_or_404(Salon, salon_manager__user=request.user)
    service = get_object_or_404(Services, id=service_id, services_of_salon=salon)
    service.delete()
    messages.success(request, "خدمت با موفقیت حذف شد.")
    return redirect("dashboards:service_menu")


# --------------------------------------------------------------------------------------------
def membership(request):

    context = {}
    return render(request, "dashboards/membership.html", context)


# --------------------------------------------------------------------------------------------
def products(request):

    context = {}
    return render(request, "dashboards/products.html", context)


# --------------------------------------------------------------------------------------------
def stocktakes(request):

    context = {}
    return render(request, "dashboards/stocktakes.html", context)


# --------------------------------------------------------------------------------------------
def team_managment(request):

    context = {}
    return render(request, "dashboards/team_management.html", context)


# --------------------------------------------------------------------------------------------
class TeamMemberView(LoginRequiredMixin, View):
    template_name = "dashboards/team_member.html"

    def get(self, request, *args, **kwargs):
        # ✅ بهینه‌سازی: واکشی سالن در یک کوئری
        salon = get_object_or_404(
            Salon.objects.select_related("salon_manager__user"), salon_manager__user=request.user
        )

        # =================================================================
        # ۱. آماده‌سازی فیلترها از درخواست GET
        # =================================================================
        applied_sort_by = request.GET.get("sort_by", "name_asc")
        applied_expertise_ids = [
            int(eid) for eid in request.GET.getlist("expertise") if eid.isdigit()
        ]
        applied_status = request.GET.get("status_filter", "all")

        # =================================================================
        # ۲. ساخت کوئری پایه و جامع
        # =================================================================
        # ✅ بهینه‌سازی: با select_related از N+1 Query برای user جلوگیری می‌کنیم
        stylists_qs = salon.stylists.select_related("user").annotate(
            avg_score_annotation=Coalesce(Avg("scoring_stylist__score"), Value(0.0))
        )

        # =================================================================
        # ۳. اعمال فیلترها به صورت بهینه
        # =================================================================
        if applied_expertise_ids:
            stylists_qs = stylists_qs.filter(
                services_of_stylist__service_group__id__in=applied_expertise_ids
            ).distinct()

        if applied_status == "active":
            stylists_qs = stylists_qs.filter(is_active=True)
        elif applied_status == "inactive":
            stylists_qs = stylists_qs.filter(is_active=False)

        # =================================================================
        # ۴. اعمال مرتب‌سازی
        # =================================================================
        sort_map = {
            "name_asc": ("user__family", "user__name"),
            "name_desc": ("-user__family", "-user__name"),
            "rating_asc": ("avg_score_annotation", "user__family"),
            "rating_desc": ("-avg_score_annotation", "user__family"),
            "newest": ("-user__pk",),
            "oldest": ("user__pk",),
        }
        order_by_fields = sort_map.get(applied_sort_by, ("user__family", "user__name"))
        stylists_qs = stylists_qs.order_by(*order_by_fields)

        # واکشی گروه‌های خدمات برای نمایش در فیلتر
        all_group_services = GroupServices.objects.filter(is_active=True).order_by("group_title")

        context = {
            "stylists": stylists_qs,
            "all_group_services": all_group_services,
            "applied_filters": {
                "sort_by": applied_sort_by,
                "expertise": [str(eid) for eid in applied_expertise_ids],
                "status_filter": applied_status,
            },
        }
        return render(request, self.template_name, context)


# ---------------------------------------------------------------------------------------------
class StylistOverviewView(LoginRequiredMixin, View):
    template_name = "dashboards/stylist_overview.html"

    def get(self, request, stylist_id):
        # =================================================================
        # ۱. واکشی اطلاعات اولیه و احراز هویت (بهینه شده)
        # =================================================================
        salon = get_object_or_404(
            Salon.objects.select_related("salon_manager__user"), salon_manager__user=request.user
        )

        # واکشی آرایشگر به همراه تمام اطلاعات مورد نیاز تمپلیت
        stylist = get_object_or_404(
            Stylist.objects.select_related("user").prefetch_related(
                "job_details__salon", "services_of_stylist", "stylists_of_salon"
            ),
            user_id=stylist_id,
            stylists_of_salon=salon,
        )

        # =================================================================
        # ۲. آماده‌سازی محدوده تاریخ برای دو ماه اخیر
        # =================================================================
        today_jalali = JalaliDate.today()
        start_current_month = JalaliDate(today_jalali.year, today_jalali.month, 1).todate()

        if today_jalali.month == 1:
            start_last_month = JalaliDate(today_jalali.year - 1, 12, 1).todate()
        else:
            start_last_month = JalaliDate(today_jalali.year, today_jalali.month - 1, 1).todate()

        # =================================================================
        # ۳. محاسبه تمام آمارها در یک کوئری جامع با Aggregation شرطی
        # =================================================================
        stats = OrderDetail.objects.filter(
            stylist=stylist,
            order__is_finally=True,
            order__stylist_approved=True,
            date__gte=start_last_month,  # فقط سفارش‌های دو ماه اخیر را بررسی کن
        ).aggregate(
            # آمار ماه جاری
            current_sales=Coalesce(
                Sum("price", filter=Q(date__gte=start_current_month)), Value(0)
            ),
            current_appointments=Count("id", filter=Q(date__gte=start_current_month)),
            current_unique_clients=Count(
                "order__customer", distinct=True, filter=Q(date__gte=start_current_month)
            ),
            # آمار ماه قبل
            prev_sales=Coalesce(
                Sum("price", filter=Q(date__lt=start_current_month, date__gte=start_last_month)),
                Value(0),
            ),
            prev_appointments=Count(
                "id", filter=Q(date__lt=start_current_month, date__gte=start_last_month)
            ),
            prev_unique_clients=Count(
                "order__customer",
                distinct=True,
                filter=Q(date__lt=start_current_month, date__gte=start_last_month),
            ),
        )

        # محاسبات درصد تغییرات و نرخ‌ها در پایتون
        sales_change = calculate_percentage_change(stats["current_sales"], stats["prev_sales"])
        appointments_change = calculate_percentage_change(
            stats["current_appointments"], stats["prev_appointments"]
        )
        clients_change = calculate_percentage_change(
            stats["current_unique_clients"], stats["prev_unique_clients"]
        )

        # ... (منطق محاسبات اشغال و نرخ بازگشت مشتری می‌تواند به همین شکل بهینه شود) ...

        context = {
            "stylist": stylist,
            "job_detail": stylist.job_details.first(),  # فرض بر اینکه هر آرایشگر یک جزئیات شغلی دارد
            "stats": {
                "sales": stats["current_sales"],
                "sales_change": sales_change,
                "appointments": stats["current_appointments"],
                "appointments_change": appointments_change,
                "clients": stats["current_unique_clients"],
                "clients_change": clients_change,
                # مقادیر زیر باید با منطق بهینه شده جایگزین شوند
                "occupancy": 0,
                "occupancy_change": 0,
                "retention": 0,
                "retention_change": 0,
            },
        }
        return render(request, self.template_name, context)


# این تابع کمکی را در فایل views.py یا utils.py خود نگه دارید
def calculate_percentage_change(current, previous):
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    return round(((current - previous) / previous) * 100, 1)


# ---------------------------------------------------------------------------------------------
logger = logging.getLogger(__name__)


class AddStylistView(View):
    def get(self, request):
        user = request.user
        salon_manager = get_object_or_404(SalonManager, user=user)
        salon = get_object_or_404(Salon, salon_manager=salon_manager)

        # Get unique service groups associated with the salon's services
        salon_service_groups = (
            GroupServices.objects.filter(services_of_group__services_of_salon=salon)
            .distinct()
            .order_by("group_title")
        )

        user_form = StylistUserForm()
        profile_form = StylistProfileForm()
        job_form = JobDetailsForm()
        emergency_form = EmergencyInfoForm()

        context = {
            "salon": salon,
            "salon_service_groups": salon_service_groups,  # These are GroupServices instances
            "user_form": user_form,
            "profile_form": profile_form,
            "job_form": job_form,
            "emergency_form": emergency_form,
        }
        return render(request, "dashboards/add_stylist.html", context)

    def post(self, request):
        user = request.user
        salon_manager = get_object_or_404(SalonManager, user=user)
        salon = get_object_or_404(Salon, salon_manager=salon_manager)

        user_form = StylistUserForm(request.POST)
        profile_form = StylistProfileForm(request.POST, request.FILES)
        job_form = JobDetailsForm(request.POST)
        emergency_form = EmergencyInfoForm(request.POST)

        forms_valid = all(
            [
                user_form.is_valid(),
                profile_form.is_valid(),
                job_form.is_valid(),
                emergency_form.is_valid(),
            ]
        )

        if forms_valid:
            try:
                # Create user
                user_obj = user_form.save()

                # Create stylist
                stylist = profile_form.save(commit=False)
                stylist.user = user_obj
                stylist.save()
                salon.stylists.add(stylist)  # Associate stylist with salon

                # Job details
                job = job_form.save(commit=False)
                job.stylist = stylist
                job.salon = salon
                job.save()

                # Emergency info
                emergency = emergency_form.save(commit=False)
                emergency.stylist = stylist
                emergency.full_name = f"{emergency_form.cleaned_data.get('emergency_contact_name', '')} {emergency_form.cleaned_data.get('emergency_contact_family', '')}".strip()
                prefix = emergency_form.cleaned_data.get("emergency_phone_prefix", "")
                phone = emergency_form.cleaned_data.get("emergency_phone", "")
                emergency.emergency_contact = f"{prefix}{phone}" if phone else ""
                emergency.save()

                # Handle selected services (assuming service IDs are submitted in 'selected_services_input')
                selected_service_ids_json = request.POST.get("selected_services_input", "[]")
                selected_service_ids = json.loads(selected_service_ids_json)

                for service_id in selected_service_ids:
                    try:
                        service_instance = Services.objects.get(
                            id=service_id, services_of_salon=salon
                        )
                        # Assuming you have a M2M on Stylist model for services or through ServicePrice
                        stylist.services_of_stylist.add(service_instance)
                        # Or create ServicePrice entries if that's how stylists are linked to services they offer
                        # For now, this part is conceptual as the exact model structure for Stylist+Services isn't fully detailed
                    except Services.DoesNotExist:
                        logger.warning(
                            f"Service with id {service_id} not found or not part of the salon."
                        )

                messages.success(request, "آرایشگر با موفقیت اضافه شد")
                return redirect(
                    "dashboards:team_member"
                )  # Or wherever you redirect after adding a stylist

            except Exception as e:
                logger.error(f"Error creating stylist: {str(e)}", exc_info=True)
                messages.error(request, f"خطا در افزودن آرایشگر: {str(e)}")
        else:
            error_messages_list = []
            if not user_form.is_valid():
                error_messages_list.append(f"User form errors: {user_form.errors.as_json()}")
            if not profile_form.is_valid():
                error_messages_list.append(f"Profile form errors: {profile_form.errors.as_json()}")
            if not job_form.is_valid():
                error_messages_list.append(f"Job form errors: {job_form.errors.as_json()}")
            if not emergency_form.is_valid():
                error_messages_list.append(
                    f"Emergency form errors: {emergency_form.errors.as_json()}"
                )
            messages.error(
                request,
                "لطفاً خطاهای فرم را اصلاح کنید. " + " | ".join(error_messages_list),
            )

        salon_service_groups = (
            GroupServices.objects.filter(services_of_group__services_of_salon=salon)
            .distinct()
            .order_by("group_title")
        )
        context = {
            "salon": salon,
            "salon_service_groups": salon_service_groups,
            "user_form": user_form,
            "profile_form": profile_form,
            "job_form": job_form,
            "emergency_form": emergency_form,
        }
        return render(request, "dashboards/add_stylist.html", context)


# ---------------------------------------------------------------------------------------------
logger = logging.getLogger(__name__)


class EditStylistView(View):
    def get(self, request, stylist_id):
        user = request.user
        salon_manager = get_object_or_404(SalonManager, user=user)
        salon = get_object_or_404(Salon, salon_manager=salon_manager)

        # Get unique service groups associated with the salon's services
        salon_service_groups = (
            GroupServices.objects.filter(services_of_group__services_of_salon=salon)
            .distinct()
            .order_by("group_title")
        )

        stylist = get_object_or_404(Stylist, user_id=stylist_id)
        job_detail = get_object_or_404(JobDetails, stylist=stylist)
        emergency_info = get_object_or_404(EmergencyInfo, stylist=stylist)

        # Get stylist's current services
        stylist_services = stylist.services_of_stylist.all()
        stylist_service_ids = list(stylist_services.values_list("id", flat=True))

        user_data = {
            "name": stylist.user.name,
            "family": stylist.user.family,
            "email": stylist.user.email,
            "mobile_number": stylist.user.mobile_number,
        }
        user_form = StylistUserForm(data=user_data)

        profile_data = {
            "expert": stylist.expert,
            "calendar_color": stylist.calendar_color,
            "profile_image": stylist.profile_image,
        }
        profile_form = StylistProfileForm(data=profile_data)

        job_data = {
            "start_date": job_detail.start_date,
            "end_date": job_detail.end_date,
            "employment_type": job_detail.employment_type,
        }
        job_form = JobDetailsForm(data=job_data)

        emergency_data = {
            "emergency_contact_name": emergency_info.full_name,
            "emergency_phone": emergency_info.emergency_contact,
            "relationship": emergency_info.relationship,
        }
        emergency_form = EmergencyInfoForm(data=emergency_data)

        context = {
            "salon": salon,
            "salon_service_groups": salon_service_groups,
            "user_form": user_form,
            "profile_form": profile_form,
            "job_form": job_form,
            "emergency_form": emergency_form,
            "stylist": stylist,  # اضافه کردن آرایشگر به context
            "stylist_services": stylist_services,  # خدمات آرایشگر
            "stylist_service_ids": stylist_service_ids,  # ID های خدمات برای JavaScript
        }
        return render(request, "dashboards/edit_stylist.html", context)

    def post(self, request, stylist_id):
        user = request.user
        salon_manager = get_object_or_404(SalonManager, user=user)
        salon = get_object_or_404(Salon, salon_manager=salon_manager)

        # Get the existing stylist to update
        stylist = get_object_or_404(Stylist, user_id=stylist_id)
        job_detail = get_object_or_404(JobDetails, stylist=stylist)
        emergency_info = get_object_or_404(EmergencyInfo, stylist=stylist)

        user_form = StylistUserForm(request.POST, instance=stylist.user)
        profile_form = StylistProfileForm(request.POST, request.FILES, instance=stylist)
        job_form = JobDetailsForm(request.POST, instance=job_detail)
        emergency_form = EmergencyInfoForm(request.POST, instance=emergency_info)

        forms_valid = all(
            [
                user_form.is_valid(),
                profile_form.is_valid(),
                job_form.is_valid(),
                emergency_form.is_valid(),
            ]
        )

        if forms_valid:
            try:
                # Update user
                user_obj = user_form.save()

                # Update stylist
                stylist = profile_form.save(commit=False)
                stylist.user = user_obj
                stylist.save()

                # Update job details
                job = job_form.save(commit=False)
                job.stylist = stylist
                job.salon = salon
                job.save()

                # Update emergency info
                emergency = emergency_form.save(commit=False)
                emergency.stylist = stylist
                emergency.full_name = f"{emergency_form.cleaned_data.get('emergency_contact_name', '')} {emergency_form.cleaned_data.get('emergency_contact_family', '')}".strip()
                prefix = emergency_form.cleaned_data.get("emergency_phone_prefix", "")
                phone = emergency_form.cleaned_data.get("emergency_phone", "")
                emergency.emergency_contact = f"{prefix}{phone}" if phone else ""
                emergency.save()

                # Handle selected services
                selected_service_ids_json = request.POST.get("selected_services_input", "[]")
                selected_service_ids = json.loads(selected_service_ids_json)

                # Clear existing services and add new ones
                stylist.services_of_stylist.clear()

                for service_id in selected_service_ids:
                    try:
                        service_instance = Services.objects.get(
                            id=service_id, services_of_salon=salon
                        )
                        stylist.services_of_stylist.add(service_instance)
                    except Services.DoesNotExist:
                        logger.warning(
                            f"Service with id {service_id} not found or not part of the salon."
                        )

                messages.success(request, "آرایشگر با موفقیت ویرایش شد")
                return redirect("dashboards:team_member")

            except Exception as e:
                logger.error(f"Error updating stylist: {str(e)}", exc_info=True)
                messages.error(request, f"خطا در ویرایش آرایشگر: {str(e)}")
        else:
            error_messages_list = []
            if not user_form.is_valid():
                error_messages_list.append(f"User form errors: {user_form.errors.as_json()}")
            if not profile_form.is_valid():
                error_messages_list.append(f"Profile form errors: {profile_form.errors.as_json()}")
            if not job_form.is_valid():
                error_messages_list.append(f"Job form errors: {job_form.errors.as_json()}")
            if not emergency_form.is_valid():
                error_messages_list.append(
                    f"Emergency form errors: {emergency_form.errors.as_json()}"
                )
            messages.error(
                request,
                "لطفاً خطاهای فرم را اصلاح کنید. " + " | ".join(error_messages_list),
            )

        # Get stylist's current services for re-rendering
        stylist_services = stylist.services_of_stylist.all()
        stylist_service_ids = list(stylist_services.values_list("id", flat=True))

        salon_service_groups = (
            GroupServices.objects.filter(services_of_group__services_of_salon=salon)
            .distinct()
            .order_by("group_title")
        )

        context = {
            "salon": salon,
            "salon_service_groups": salon_service_groups,
            "user_form": user_form,
            "profile_form": profile_form,
            "job_form": job_form,
            "emergency_form": emergency_form,
            "stylist": stylist,
            "stylist_services": stylist_services,
            "stylist_service_ids": stylist_service_ids,
        }
        return render(request, "dashboards/edit_stylist.html", context)


# ----------------------------------------------------------------------------------------------------------------
@csrf_exempt
def get_services_list(request):
    """
    API endpoint to get all active services for the salon manager's salon.
    Each service will include its primary group ID and title for frontend grouping.
    """
    if request.method == "GET":
        try:
            if not request.user.is_authenticated:
                return JsonResponse({"error": "User not authenticated"}, status=401)

            salon_manager = get_object_or_404(SalonManager, user=request.user)
            salon = get_object_or_404(Salon, salon_manager=salon_manager)

            salon_services = salon.services.filter(is_active=True).prefetch_related(
                "service_group"
            )

            services_data = []
            for service in salon_services:
                # Determine price - this logic might need adjustment based on your pricing model
                # For simplicity, let's assume a base price or the first available price.
                # price_amount = (
                #     service.default_price if hasattr(service, "default_price") else 0
                # )  # Example: use a default_price field

                # Get the first service group for categorization.
                # A service might belong to multiple groups; for this UI, we pick one.
                first_group = service.service_group.first()
                group_id_for_service = None
                group_title_for_service = "سایر خدمات"  # Default title if no group

                if first_group:
                    group_id_for_service = first_group.id
                    group_title_for_service = first_group.group_title

                service_data_item = {
                    "id": service.id,
                    "name": service.service_name,
                    "duration": service.duration_minutes,
                    "price": (
                        service.service_prices.first().price
                        if service.service_prices.exists()
                        else None
                    ),  # Assuming service_prices is a related field
                    "description": service.description if service.description else "",
                    "groupId": group_id_for_service,  # Crucial for frontend grouping by tab
                    "groupTitle": group_title_for_service,  # Helpful for displaying group title
                }
                services_data.append(service_data_item)

            return JsonResponse({"services": services_data})

        except SalonManager.DoesNotExist:
            return JsonResponse({"error": "SalonManager profile not found."}, status=404)
        except Salon.DoesNotExist:
            return JsonResponse({"error": "Salon not found for this manager."}, status=404)
        except Exception as e:
            logger.error(f"Error in get_services_list: {str(e)}", exc_info=True)
            return JsonResponse({"error": f"An unexpected error occurred: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)


# ----------------------------------------------------------------------------------------------------------------
# ثابت‌های مورد نیاز برای نمایش تاریخ شمسی
MONTHS_FA = [
    "فروردین",
    "اردیبهشت",
    "خرداد",
    "تیر",
    "مرداد",
    "شهریور",
    "مهر",
    "آبان",
    "آذر",
    "دی",
    "بهمن",
    "اسفند",
]
PERSIAN_WEEKDAY_NAMES = ["شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه"]


class ScheduledShiftsView(LoginRequiredMixin, View):
    template_name = "dashboards/scheduled_shifts.html"

    def get(self, request, *args, **kwargs):
        # ✅ بهینه‌سازی: واکشی سالن در یک کوئری
        salon = get_object_or_404(
            Salon.objects.select_related("salon_manager__user"), salon_manager__user=request.user
        )

        # --- ۱. آماده‌سازی محدوده تاریخ ---
        start_date_str = request.GET.get("start_date")
        if start_date_str:
            try:
                start_date_gregorian = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            except ValueError:
                start_date_gregorian = jdatetime.date.today().togregorian()
        else:
            today_jalali = jdatetime.date.today()
            start_of_week_jalali = today_jalali - timedelta(days=today_jalali.weekday())
            start_date_gregorian = start_of_week_jalali.togregorian()

        end_date_gregorian = start_date_gregorian + timedelta(days=6)
        all_gregorian_dates_in_range = [start_date_gregorian + timedelta(days=i) for i in range(7)]

        # --- ۲. واکشی بهینه تمام داده‌ها در چند کوئری اصلی ---
        stylists_qs = (
            salon.stylists.filter(is_active=True)
            .select_related("user")
            .prefetch_related(
                Prefetch(
                    "stylist_schedules",
                    queryset=StylistSchedule.objects.filter(
                        date__range=[start_date_gregorian, end_date_gregorian]
                    ),
                    to_attr="schedules_in_range",
                ),
                Prefetch(
                    "time_offs",
                    queryset=StylistTimeOff.objects.filter(
                        date__range=[start_date_gregorian, end_date_gregorian]
                    ),
                    to_attr="time_offs_in_range",
                ),
            )
        )

        # --- ۳. پردازش داده‌ها در پایتون (بدون کوئری اضافه) ---
        stylists_data = []
        schedule_by_day_dict = {day: [] for day in all_gregorian_dates_in_range}

        for stylist in stylists_qs:
            schedules_in_range = stylist.schedules_in_range
            time_offs_in_range = stylist.time_offs_in_range

            total_duration_seconds = sum(
                (
                    datetime.combine(s.date, s.end_time) - datetime.combine(s.date, s.start_time)
                ).total_seconds()
                for s in schedules_in_range
            )
            total_hours = round(total_duration_seconds / 3600)

            schedules_by_date = defaultdict(list)
            for sched in schedules_in_range:
                schedules_by_date[sched.date].append(sched)

            time_off_by_date = {tof.date: tof for tof in time_offs_in_range}

            stylist_daily_schedules = []
            for day in all_gregorian_dates_in_range:
                jalali_day = jdatetime.date.fromgregorian(date=day)
                formatted_date = f"{PERSIAN_WEEKDAY_NAMES[jalali_day.weekday()]}، {jalali_day.day} {MONTHS_FA[jalali_day.month - 1]}"

                day_events = []
                if day in schedules_by_date:
                    for shift in sorted(schedules_by_date[day], key=lambda s: s.start_time):
                        day_events.append(
                            {
                                "type": "work",
                                "start_time": shift.start_time,
                                "display": f"{shift.start_time.strftime('%H:%M')} - {shift.end_time.strftime('%H:%M')}",
                            }
                        )
                if day in time_off_by_date:
                    time_off = time_off_by_date[day]
                    display_text = time_off.reason or "مرخصی"
                    if time_off.start_time and time_off.end_time:
                        display_text += f" ({time_off.start_time.strftime('%H:%M')} - {time_off.end_time.strftime('%H:%M')})"
                    day_events.append(
                        {
                            "type": "off",
                            "start_time": time_off.start_time or dt_time.min,
                            "display": display_text,
                        }
                    )

                day_events.sort(key=lambda x: x["start_time"])

                stylist_daily_schedules.append(
                    {
                        "formatted_date": formatted_date,
                        "raw_date_iso": day.isoformat(),
                        "events": day_events,
                    }
                )

                if day_events:
                    schedule_by_day_dict[day].append(
                        {
                            "id": stylist.pk,
                            "full_name": stylist.get_fullName(),
                            "profile_image_url": (
                                stylist.profile_image.url if stylist.profile_image else None
                            ),
                            "events": day_events,
                        }
                    )

            stylists_data.append(
                {
                    "id": stylist.pk,
                    "full_name": stylist.get_fullName(),
                    "profile_image_url": (
                        stylist.profile_image.url if stylist.profile_image else None
                    ),
                    "total_hours": total_hours,
                    "daily_schedules": stylist_daily_schedules,
                }
            )

        schedule_by_day = []
        for day, working_stylists in schedule_by_day_dict.items():
            jalali_day = jdatetime.date.fromgregorian(date=day)
            schedule_by_day.append(
                {
                    "raw_date_iso": day.isoformat(),
                    "formatted_date": f"{PERSIAN_WEEKDAY_NAMES[jalali_day.weekday()]}، {jalali_day.day} {MONTHS_FA[jalali_day.month - 1]}",
                    "has_schedule": bool(working_stylists),
                    "stylists_working": working_stylists,
                }
            )

        # --- ۴. ساخت Context نهایی ---
        start_date_jalali = jdatetime.date.fromgregorian(date=start_date_gregorian)
        end_date_jalali = jdatetime.date.fromgregorian(date=end_date_gregorian)
        date_range_display = f"{start_date_jalali.day} {MONTHS_FA[start_date_jalali.month - 1]} - {end_date_jalali.day} {MONTHS_FA[end_date_jalali.month - 1]} {start_date_jalali.year}"

        context = {
            "salon": salon,
            "stylists_with_hours": stylists_data,
            "schedule_by_day": schedule_by_day,
            "date_range_display": date_range_display,
            "prev_week_start_iso": (start_date_gregorian - timedelta(days=7)).isoformat(),
            "next_week_start_iso": (start_date_gregorian + timedelta(days=7)).isoformat(),
        }
        return render(request, self.template_name, context)


# -------------------------------------------------------------------------------------------------------------------------------------------------------------
# ثابت‌های مورد نیاز برای نمایش تاریخ شمسی
MONTHS_FA = [
    "فروردین",
    "اردیبهشت",
    "خرداد",
    "تیر",
    "مرداد",
    "شهریور",
    "مهر",
    "آبان",
    "آذر",
    "دی",
    "بهمن",
    "اسفند",
]


class EditStylistDayScheduleView(LoginRequiredMixin, View):
    template_name = "dashboards/edit_day_schedule.html"

    def get_time_options(self, open_time, close_time):
        """لیستی از زمان‌ها با فاصله ۳۰ دقیقه بر اساس ساعات کاری سالن ایجاد می‌کند."""
        options = []
        if not open_time or not close_time:
            # اگر ساعت کاری تعریف نشده، یک لیست پیش‌فرض برای ۲۴ ساعت ایجاد کن
            current_time = datetime.combine(date.today(), dt_time(0, 0))
            end_datetime = datetime.combine(date.today(), dt_time(23, 30))
        else:
            current_time = datetime.combine(date.today(), open_time)
            end_datetime = datetime.combine(date.today(), close_time)

        while current_time <= end_datetime:
            options.append(current_time.strftime("%H:%M"))
            current_time += timedelta(minutes=30)
        return options

    def get(self, request, stylist_pk, salon_pk, date_iso):
        try:
            date_obj = date.fromisoformat(date_iso)
        except ValueError:
            messages.error(request, "فرمت تاریخ نامعتبر است.")
            return redirect("dashboards:scheduled_shifts")

        # ✅ بهینه‌سازی: واکشی تمام اطلاعات مورد نیاز با prefetch_related
        stylist = get_object_or_404(
            Stylist.objects.select_related("user").prefetch_related(
                Prefetch(
                    "services_of_stylist",
                    queryset=Services.objects.filter(services_of_salon__pk=salon_pk),
                    to_attr="available_services_in_salon",
                )
            ),
            pk=stylist_pk,
        )
        salon = get_object_or_404(Salon, pk=salon_pk)

        # واکشی ساعات کاری و شیفت‌های موجود
        day_of_week_for_model = ((date_obj.weekday() + 2) % 7) + 1
        salon_hours_for_day = SalonOpeningHours.objects.filter(
            salon=salon, day_of_week=day_of_week_for_model, is_closed=False
        ).first()

        open_time, close_time = (None, None)
        if salon_hours_for_day:
            open_time = salon_hours_for_day.open_time
            close_time = salon_hours_for_day.close_time
        else:
            messages.warning(request, "ساعات کاری برای این روز در سالن تعریف نشده است.")

        existing_schedules = StylistSchedule.objects.filter(
            stylist=stylist, salon=salon, date=date_obj
        ).order_by("start_time")

        jalali_date_obj = jdatetime.date.fromgregorian(date=date_obj)
        day_name_fa = jalali_date_obj.strftime("%A")
        page_title_date = (
            f"{day_name_fa}، {jalali_date_obj.day} {MONTHS_FA[jalali_date_obj.month - 1]}"
        )

        context = {
            "stylist": stylist,
            "salon": salon,
            "date_iso": date_iso,
            "page_title_date": page_title_date,
            "existing_schedules": existing_schedules,
            "available_services": stylist.available_services_in_salon,
            "time_options": self.get_time_options(open_time, close_time),
            "new_shift_template_id": "new-shift-template-row",
        }
        return render(request, self.template_name, context)

    def post(self, request, stylist_pk, salon_pk, date_iso):
        stylist = get_object_or_404(Stylist, pk=stylist_pk)
        salon = get_object_or_404(Salon, pk=salon_pk)
        try:
            date_obj = date.fromisoformat(date_iso)
        except ValueError:
            messages.error(request, "فرمت تاریخ نامعتبر برای ارسال اطلاعات.")
            return redirect("dashboards:scheduled_shifts")

        # --- پردازش داده‌های فرم ---
        shifts_data = []
        shift_indices = {
            int(k.split("[")[1].split("]")[0]) for k in request.POST if k.startswith("shifts[")
        }

        for index in sorted(list(shift_indices)):
            start_time_str = request.POST.get(f"shifts[{index}][start_time]")
            end_time_str = request.POST.get(f"shifts[{index}][end_time]")
            service_id_str = request.POST.get(f"shifts[{index}][service_id]")

            if not all([start_time_str, end_time_str, service_id_str]):
                continue

            try:
                start_time = dt_time.fromisoformat(start_time_str)
                end_time = dt_time.fromisoformat(end_time_str)
                if end_time <= start_time:
                    messages.warning(
                        request, f"زمان پایان باید بعد از زمان شروع باشد (ردیف {index + 1})."
                    )
                    continue

                shifts_data.append(
                    {
                        "service_id": int(service_id_str),
                        "start_time": start_time,
                        "end_time": end_time,
                    }
                )
            except (ValueError, TypeError):
                messages.error(request, f"فرمت داده‌های ردیف {index + 1} نامعتبر است.")
                continue

        # ✅ بهینه‌سازی اصلی: استفاده از transaction.atomic و bulk_create
        try:
            with transaction.atomic():
                StylistSchedule.objects.filter(
                    stylist=stylist, salon=salon, date=date_obj
                ).delete()

                new_schedules = []
                for data in shifts_data:
                    new_schedules.append(
                        StylistSchedule(
                            stylist=stylist,
                            salon=salon,
                            date=date_obj,
                            service_id=data["service_id"],
                            start_time=data["start_time"],
                            end_time=data["end_time"],
                        )
                    )

                if new_schedules:
                    StylistSchedule.objects.bulk_create(new_schedules)

            if not shifts_data and not new_schedules:
                messages.info(request, "تمام شیفت‌ها برای این روز حذف شدند.")
            else:
                messages.success(request, f"{len(new_schedules)} شیفت با موفقیت ذخیره شد.")

        except Exception as e:
            messages.error(request, f"خطا در ذخیره‌سازی: {e}")

        return redirect("dashboards:scheduled_shifts")


# --------------------------------------------------------------------------------------------------------------------------------
class DeleteDayScheduleView(View):

    def post(self, request, stylist_id, date_iso):
        # اطمینان از اینکه آرایشگر وجود دارد
        stylist = get_object_or_404(Stylist, pk=stylist_id)

        try:
            # تبدیل تاریخ از فرمت ISO به شیء date پایتون
            schedule_date = datetime.strptime(date_iso, "%Y-%m-%d").date()
        except ValueError:
            return JsonResponse(
                {"status": "error", "message": "فرمت تاریخ نامعتبر است."}, status=400
            )

        try:
            # استفاده از transaction برای اطمینان از اتمی بودن عملیات حذف
            with transaction.atomic():
                # حذف تمام شیفت‌های کاری در این روز
                StylistSchedule.objects.filter(stylist=stylist, date=schedule_date).delete()

                # حذف تمام مرخصی‌ها (time off) در این روز
                StylistTimeOff.objects.filter(stylist=stylist, date=schedule_date).delete()

            return JsonResponse({"status": "success", "message": "برنامه روز با موفقیت حذف شد."})

        except Exception as e:
            # لاگ کردن خطا در محیط واقعی توصیه می‌شود
            return JsonResponse(
                {"status": "error", "message": f"خطایی در هنگام حذف رخ داد: {str(e)}"}, status=500
            )


# -------------------------------------------------------------------------------------------------------------------------------------------
def to_english_numerals(text):
    if text is None:
        return None
    persian_to_english = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")
    return text.translate(persian_to_english)


PERSIAN_WEEKDAY_NAMES = ["شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه"]


class SetSalonHoursView(View):
    def get(self, request, salon_id):
        # در اینجا می‌توانید فرم کامل تنظیم ساعت کاری را پیاده‌سازی کنید
        from django.http import HttpResponse

        salon = get_object_or_404(Salon, pk=salon_id)
        return HttpResponse(
            f"لطفاً در این صفحه فرم تنظیم ساعات کاری برای سالن '{salon.salon_name}' را پیاده‌سازی کنید."
        )


class SetRegularShiftsView(LoginRequiredMixin, View):
    template_name = "dashboards/set_regular_shifts.html"

    def get(self, request, stylist_id, salon_id):
        # ✅ بهینه‌سازی: واکشی تمام اطلاعات مورد نیاز در کوئری‌های کمتر
        stylist = get_object_or_404(Stylist.objects.select_related("user"), pk=stylist_id)
        salon = get_object_or_404(Salon.objects.prefetch_related("opening_hours"), pk=salon_id)

        if not salon.opening_hours.exists():
            messages.warning(request, "ابتدا باید ساعات کاری سالن را تنظیم کنید.")
            return redirect("dashboards:set_salon_hours", salon_id=salon.id)

        salon_hours_data = {}
        for hour in salon.opening_hours.all():
            day_index = hour.day_of_week - 1
            if hour.is_closed or not hour.open_time or not hour.close_time:
                salon_hours_data[day_index] = None
            else:
                salon_hours_data[day_index] = {
                    "open": hour.open_time.strftime("%H:%M"),
                    "close": hour.close_time.strftime("%H:%M"),
                }

        context = {
            "stylist": stylist,
            "weekdays": PERSIAN_WEEKDAY_NAMES,
            "salon_hours_json": json.dumps(salon_hours_data),
        }
        return render(request, self.template_name, context)

    def post(self, request, stylist_id, salon_id):
        stylist = get_object_or_404(Stylist, pk=stylist_id)
        salon = get_object_or_404(Salon, pk=salon_id)

        start_date_str = request.POST.get("start_date")
        end_date_str = request.POST.get("end_date")

        try:
            start_jalali = jdatetime.datetime.strptime(
                to_english_numerals(start_date_str), "%Y-%m-%d"
            ).date()
            end_jalali = jdatetime.datetime.strptime(
                to_english_numerals(end_date_str), "%Y-%m-%d"
            ).date()
            start_date = start_jalali.togregorian()
            end_date = end_jalali.togregorian()
        except (ValueError, TypeError, AttributeError):
            messages.error(request, "لطفاً تاریخ شروع و پایان را به درستی وارد کنید.")
            return redirect(request.path_info)  # بازگشت به همین صفحه

        # پردازش داده‌های شیفت‌ها
        daily_shifts_data = {}
        for i in range(7):
            shifts_str = request.POST.get(f"day-{i}-shifts")
            if shifts_str:
                shifts_list = []
                for part in shifts_str.split(","):
                    try:
                        start_str, end_str = part.split("-")
                        shifts_list.append(
                            {
                                "start": datetime.strptime(start_str, "%H:%M").time(),
                                "end": datetime.strptime(end_str, "%H:%M").time(),
                            }
                        )
                    except ValueError:
                        continue
                if shifts_list:
                    daily_shifts_data[i] = shifts_list

        # ✅ بهینه‌سازی اصلی: استفاده از transaction.atomic و bulk_create
        try:
            with transaction.atomic():
                # ۱. حذف تمام شیفت‌های قبلی در محدوده تاریخ در یک کوئری
                StylistSchedule.objects.filter(
                    stylist=stylist, salon=salon, date__range=[start_date, end_date]
                ).delete()

                # ۲. ساخت لیستی از آبجکت‌های جدید
                schedules_to_create = []
                current_date = start_date
                while current_date <= end_date:
                    persian_weekday_index = (current_date.weekday() + 2) % 7
                    if persian_weekday_index in daily_shifts_data:
                        for shift in daily_shifts_data[persian_weekday_index]:
                            schedules_to_create.append(
                                StylistSchedule(
                                    stylist=stylist,
                                    salon=salon,
                                    date=current_date,
                                    start_time=shift["start"],
                                    end_time=shift["end"],
                                )
                            )
                    current_date += timedelta(days=1)

                # ۳. درج تمام شیفت‌های جدید در یک کوئری
                if schedules_to_create:
                    StylistSchedule.objects.bulk_create(schedules_to_create)

            messages.success(request, "شیفت‌های منظم با موفقیت ذخیره شدند.")
        except Exception as e:
            messages.error(request, f"خطایی در هنگام ذخیره‌سازی رخ داد: {e}")
            return redirect(request.path_info)

        return redirect("dashboards:scheduled_shifts")


# ----------------------------------------------------------------------------------------------------------------------------------
class AddTimeOffView(LoginRequiredMixin, View):
    template_name = "dashboards/add_time_off.html"
    form_class = StylistTimeOffForm

    def _get_time_options(self, date_obj, salon):
        """متد کمکی برای تولید گزینه‌های ساعت."""
        time_options = []
        day_of_week_for_model = ((date_obj.weekday() + 2) % 7) + 1

        salon_hours = SalonOpeningHours.objects.filter(
            salon=salon, day_of_week=day_of_week_for_model, is_closed=False
        ).first()

        if salon_hours and salon_hours.open_time and salon_hours.close_time:
            current = datetime.combine(date.today(), salon_hours.open_time)
            end = datetime.combine(date.today(), salon_hours.close_time)
            while current <= end:
                time_options.append(current.strftime("%H:%M"))
                current += timedelta(minutes=30)
        return time_options

    def get(self, request, stylist_id, salon_id, date_iso):
        stylist = get_object_or_404(Stylist.objects.select_related("user"), pk=stylist_id)
        salon = get_object_or_404(Salon, pk=salon_id)
        try:
            date_obj = date.fromisoformat(date_iso)
        except ValueError:
            messages.error(request, "فرمت تاریخ نامعتبر است.")
            return redirect("dashboards:scheduled_shifts")

        time_options = self._get_time_options(date_obj, salon)
        if not time_options and request.method == "GET":
            messages.warning(
                request, "ساعات کاری برای این روز در سالن تعریف نشده یا سالن تعطیل است."
            )

        form = self.form_class(
            initial={"stylist": stylist, "date": date_obj}, time_options=time_options
        )
        jalali_date = jdatetime.date.fromgregorian(date=date_obj)
        context = {
            "form": form,
            "stylist": stylist,
            "jalali_date_display": jalali_date.strftime("%Y-%m-%d"),
        }
        return render(request, self.template_name, context)

    def post(self, request, stylist_id, salon_id, date_iso):
        stylist = get_object_or_404(Stylist, pk=stylist_id)
        salon = get_object_or_404(Salon, pk=salon_id)
        date_obj = date.fromisoformat(date_iso)

        time_options = self._get_time_options(date_obj, salon)
        form = self.form_class(request.POST, time_options=time_options)

        if form.is_valid():
            try:
                with transaction.atomic():
                    time_off = form.save(commit=False)
                    time_off.stylist = stylist
                    time_off.date = date_obj

                    # اگر مرخصی تمام روز بود، تمام شیفت‌های آن روز را حذف کن
                    if not time_off.start_time or not time_off.end_time:
                        StylistSchedule.objects.filter(
                            stylist=stylist, date=time_off.date, salon=salon
                        ).delete()
                    # اگر مرخصی ساعتی بود، شیفت‌های داخل آن بازه را حذف کن
                    else:
                        StylistSchedule.objects.filter(
                            stylist=stylist,
                            date=time_off.date,
                            salon=salon,
                            start_time__gte=time_off.start_time,
                            end_time__lte=time_off.end_time,
                        ).delete()

                    time_off.save()
                    messages.success(request, "مرخصی با موفقیت ثبت شد.")
                    return redirect("dashboards:scheduled_shifts")
            except Exception as e:
                messages.error(request, f"خطایی در هنگام ذخیره‌سازی رخ داد: {e}")

        jalali_date = jdatetime.date.fromgregorian(date=date_obj)
        context = {
            "form": form,
            "stylist": stylist,
            "jalali_date_display": jalali_date.strftime("%Y-%m-%d"),
        }
        return render(request, self.template_name, context)


# ------------------------------------------------------------------------------------------------------------------------------
import json
from datetime import datetime, timedelta
import jdatetime  # <<< ۱. اضافه کردن کتابخانه jdatetime
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone



# این دیکشنری همچنان برای محاسبه روز هفته لازم است
JALALI_WEEKDAY_MAP = {
    5: 1,  # Saturday
    6: 2,  # Sunday
    0: 3,  # Monday
    1: 4,  # Tuesday
    2: 5,  # Wednesday
    3: 6,  # Thursday
    4: 7,  # Friday
}


def calendar_view(request, salon_id):
    """
    این ویو تغییری نکرده است. فقط صفحه اصلی را رندر می‌کند.
    """
    salon = get_object_or_404(Salon, pk=salon_id)
    stylists_qs = salon.stylists.filter(is_active=True)

    stylists_data = []
    for stylist in stylists_qs:
        stylists_data.append(
            {
                "id": str(stylist.user.pk),
                "name": stylist.get_fullName(),
                "avatar": (
                    stylist.profile_image.url
                    if stylist.profile_image
                    else "https://via.placeholder.com/60"
                ),
            }
        )

    context = {
        "salon_id": salon_id,
        "stylists_json": json.dumps(stylists_data),
        "dashboard_prefix": "/dashboards",  # پیشوند URL داشبورد
    }
    return render(request, "dashboards/appointment_calendar.html", context)


def get_calendar_data(request, salon_id):
    """
    این ویو برای کار با تاریخ شمسی اصلاح شده است.
    """
    date_str = request.GET.get("date", timezone.now().strftime("%Y-%m-%d"))
    try:
        # تاریخ میلادی از ورودی گرفته می‌شود
        selected_gregorian_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

    salon = get_object_or_404(Salon, pk=salon_id)

    # ۲. تبدیل تاریخ میلادی به شمسی برای کوئری دیتابیس
    selected_jalali_date = jdatetime.date.fromgregorian(date=selected_gregorian_date)
    print(f"Selected Jalali Date: {selected_jalali_date}")
    # پیدا کردن ساعات کاری سالن همچنان با تاریخ میلادی انجام می‌شود چون به روز هفته نیاز دارد
    day_of_week_model = JALALI_WEEKDAY_MAP.get(selected_gregorian_date.weekday())
    opening_hours = SalonOpeningHours.objects.filter(
        salon=salon, day_of_week=day_of_week_model
    ).first()

    if not opening_hours or opening_hours.is_closed:
        return JsonResponse({"salonIsOpen": False, "message": "سالن در این روز تعطیل است."})

    # ۳. جستجوی نوبت‌ها با استفاده از تاریخ شمسی
    appointments_qs = OrderDetail.objects.filter(
        salon=salon, date=selected_jalali_date
    ).select_related("order__customer__user", "service", "stylist__user")

    appointments_data = []
    for detail in appointments_qs:
        if detail.date is None or detail.time is None:
            continue

        # برای عملیات `combine`، تاریخ شمسی باید به میلادی معادل تبدیل شود
        detail_gregorian_date = detail.date.togregorian()
        start_datetime = datetime.combine(detail_gregorian_date, detail.time)

        duration = 60
        if detail.service:
            duration = (
                getattr(detail.service, "duration_in_minutes", None)
                or getattr(detail.service, "duration", None)
                or 60
            )
        end_datetime = start_datetime + timedelta(minutes=int(duration))

        service_name = ""
        if detail.service:
            service_name = getattr(detail.service, "name", "") or getattr(
                detail.service, "title", ""
            )

        appointments_data.append(
            {
                "id": detail.pk,
                "stylistId": str(detail.stylist.user.pk),
                "customer": detail.order.customer.get_fullName(),
                "time": detail.time.strftime("%H:%M"),
                "date": detail.date.strftime("%Y-%m-%d"),  # این تاریخ شمسی است
                "service": service_name,
                "paid": detail.order.is_paid,
                "description": detail.order.description or "",
                "endTime": end_datetime.strftime("%H:%M"),
            }
        )

    # جستجوی برنامه‌کاری و مرخصی‌ها نیز باید با تاریخ شمسی انجام شود
    schedules_qs = StylistSchedule.objects.filter(salon=salon, date=selected_jalali_date)
    schedules_data = {}
    for schedule in schedules_qs:
        stylist_id = str(schedule.stylist.user.pk)
        if stylist_id not in schedules_data:
            schedules_data[stylist_id] = []
        schedules_data[stylist_id].append(
            {
                "start": schedule.start_time.strftime("%H:%M"),
                "end": schedule.end_time.strftime("%H:%M"),
            }
        )

    stylists_in_salon = salon.stylists.all()
    time_offs_qs = StylistTimeOff.objects.filter(
        stylist__in=stylists_in_salon, date=selected_jalali_date
    )
    time_offs_data = {}
    for time_off in time_offs_qs:
        stylist_id = str(time_off.stylist.user.pk)
        if stylist_id not in time_offs_data:
            time_offs_data[stylist_id] = []
        time_offs_data[stylist_id].append(
            {
                "start": time_off.start_time.strftime("%H:%M") if time_off.start_time else "00:00",
                "end": time_off.end_time.strftime("%H:%M") if time_off.end_time else "23:59",
                "reason": time_off.reason,
            }
        )

    return JsonResponse(
        {
            "salonIsOpen": True,
            "openTime": opening_hours.open_time.strftime("%H:%M"),
            "closeTime": opening_hours.close_time.strftime("%H:%M"),
            "appointments": appointments_data,
            "schedules": schedules_data,
            "timeOffs": time_offs_data,
        }
    )
