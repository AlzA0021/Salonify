import json
from datetime import date
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Prefetch, Avg, Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View
from django.views.decorators.http import require_GET
from khayyam import JalaliDate
from apps.accounts.models import Customer, Stylist
from apps.salons.models import Salon
from apps.services.models import ServicePrice, Services
from apps.stylists.models import StylistSchedule
from .forms import OrderForm
from .models import Order, OrderDetail
from collections import defaultdict
from django.db import transaction

# ------------------------------------------------------------------
# class OrderCartView(View):
#     def get(self, request, *args, **kw):
#         order_cart = OrderCart(request)

#         context = {
#             "order_cart": order_cart,
#         }
#         return render(request, "orders/order_cart.html", context)


# # ---------------------------------------------------------------------
# def show_order_cart(request):
#     order_cart = OrderCart(request)
#     for item in order_cart:
#         item["discount"] = item["stylist"].get_discount_for_service(item["service"])
#     context = {"order_cart": order_cart}
#     return render(request, "orders/partials/show_order_cart.html", context)


# # ---------------------------------------------------------------------------
# import json
# from django.http import JsonResponse
# from django.shortcuts import get_object_or_404
# from django.views.decorators.http import require_POST
# from django.contrib.auth.decorators import login_required

# # مدل‌های خود را اینجا import کنید
# # from apps.salons.models import Salon
# # from apps.accounts.models import Stylist
# # from apps.services.models import Services
# # from .order_cart import OrderCart # کلاس سبد خرید شما

# @login_required  # افزودن به سبد خرید نیازمند لاگین کاربر است
# @require_POST    # این View فقط درخواست‌های POST را می‌پذیرد
# def add_to_order_cart(request):
#     """
#     یک آیتم (خدمت، آرایشگر، تاریخ و زمان) را به سبد خرید کاربر اضافه می‌کند.
#     """
#     # ۱. خواندن اطلاعات از بدنه درخواست POST (که به صورت JSON ارسال شده)
#     try:
#         data = json.loads(request.body)
#         service_id = data.get("service")
#         stylist_id = data.get("stylist")
#         salon_id = data.get("salon")
#         date = data.get("date")
#         time = data.get("time")

#         if not all([service_id, stylist_id, salon_id, date, time]):
#             return JsonResponse({"error": "اطلاعات ارسالی ناقص است."}, status=400)

#     except (json.JSONDecodeError, TypeError):
#         return JsonResponse({"error": "فرمت درخواست نامعتبر است (باید JSON باشد)."}, status=400)

#     # ۲. اعتبارسنجی و واکشی بهینه آبجکت‌ها
#     try:
#         # ✅ بهینه‌سازی اصلی: واکشی آرایشگر و بررسی همزمان روابط او با سالن و خدمت
#         # این کوئری تضمین می‌کند که آرایشگر انتخاب شده، خدمت مورد نظر را در سالن مشخص شده ارائه می‌دهد.
#         stylist = get_object_or_404(
#             Stylist.objects.select_related('user'),
#             user_id=int(stylist_id),
#             stylists_of_salon__pk=int(salon_id), # آیا این آرایشگر در این سالن کار می‌کند؟
#             services_of_stylist__pk=int(service_id)  # آیا این آرایشگر این خدمت را ارائه می‌دهد؟
#         )
        
#         # حالا که روابط تایید شده، می‌توانیم بقیه آبجکت‌ها را با خیال راحت واکشی کنیم
#         service = get_object_or_404(Services, pk=int(service_id))
#         salon = get_object_or_404(Salon, pk=int(salon_id))

#     except (ValueError, TypeError):
#          return JsonResponse({"error": "شناسه‌های ارسال شده نامعتبر هستند."}, status=400)
#     except Stylist.DoesNotExist:
#         return JsonResponse({"error": "آرایشگر انتخاب شده این خدمت را در این سالن ارائه نمی‌دهد یا معتبر نیست."}, status=404)
#     except (Services.DoesNotExist, Salon.DoesNotExist):
#         return JsonResponse({"error": "خدمت یا سالن مورد نظر یافت نشد."}, status=404)

#     # ۳. افزودن به سبد خرید
#     try:
#         order_cart = OrderCart(request)
#         order_cart.add_to_order_cart(service, stylist, salon, date, time)
#         return JsonResponse({"message": "رزرو با موفقیت به سبد شما اضافه شد."}, status=200)

#     except Exception as e:
#         # می‌توانید خطاهای خاصی که ممکن است از کلاس سبد خرید شما بیاید را اینجا مدیریت کنید
#         print(f"خطا در افزودن به سبد خرید: {e}")
#         return JsonResponse({"error": "خطایی در پردازش سبد خرید رخ داد."}, status=500)



# # --------------------------------------------------------------------------------------------------------------------
# def delete_from_order_cart(request):
#     service_id = request.GET.get("service")
#     service = get_object_or_404(Services, id=service_id)
#     order_cart = OrderCart(request)
#     order_cart.delete_from_order_cart(service)
#     return redirect("orders:show_order_cart")


# # --------------------------------------------------------------------------------------------------------------------
# def show_update_order_cart(request):
#     """
#     سبد خرید را با اطلاعات کامل و به صورت بهینه برای نمایش در تمپلیت آماده می‌کند.
#     """
#     order_cart = request.session.get("order_cart", {})
    
#     # ۱. تمام ID های خدمات را از سبد خرید جمع‌آوری می‌کنیم
#     service_ids = [item.get("service_id") for item in order_cart.values() if item.get("service_id")]

#     if not service_ids:
#         return render(request, "orders/partials/show_update_order_cart.html", {"updated_items": []})

#     # ۲. ✅ بهینه‌سازی اصلی: تمام خدمات و روابط مورد نیاز را در چند کوئری محدود واکشی می‌کنیم
#     services_qs = Services.objects.filter(id__in=service_ids).prefetch_related(
#         'stylists__user',  # واکشی آرایشگران و کاربران مرتبط با آنها
#         'services_of_salon' # واکشی سالن‌های مرتبط
#     )

#     # ۳. یک دیکشنری برای دسترسی سریع به آبجکت‌های خدمت می‌سازیم
#     services_map = {service.id: service for service in services_qs}

#     # ۴. ساختار نهایی را با استفاده از داده‌های از پیش واکشی شده، آماده می‌کنیم
#     updated_items = []
#     for item_key, item_data in order_cart.items():
#         service_id = item_data.get("service_id")
#         service = services_map.get(service_id)

#         if service:
#             updated_items.append({
#                 "key": item_key, # کلید منحصر به فرد هر آیتم در سبد خرید
#                 "service": service,
#                 "stylists": service.stylists.all(),
#                 "salons": service.services_of_salon.all(),
#                 "date": item_data.get("date"),
#                 "time": item_data.get("time"),
#                 "price": item_data.get("price"),
#                 "selected_stylist_id": item_data.get("stylist_id"),
#                 "selected_salon_id": item_data.get("salon_id"),
#             })

#     return render(
#         request,
#         "orders/partials/show_update_order_cart.html",
#         {"updated_items": updated_items},
#     )


# # ---------------------------------------------------------------------------------------------------------------------
# def show_update_salon_stylist_order(request):
#     return redirect("orders:show_update_order_cart")


# # --------------------------------------------------------------------------------------------------------------------
# def update_salon_stylist_order(request):
#     service_id_list = request.GET.getlist("service_id_list[]")
#     stylist_id_list = request.GET.getlist("stylist_id_list[]")
#     salon_id_list = request.GET.getlist("salon_id_list[]")
#     order_cart = OrderCart(request)
#     order_cart.update(service_id_list, stylist_id_list, salon_id_list, None, None)
#     return redirect("orders:show_update_callendar")


# # -----------------------------------------------------------------------------------------------------------------------
# def show_update_callendar(request):
#     order_cart = OrderCart(request)

#     return render(
#         request,
#         "orders/partials/show_update_callendar.html",
#         {"order_cart": order_cart},
#     )


# # ------------------------------------------------------------------------------------------------------------------------
# def update_callendar(request):
#     service_id_list = request.GET.getlist("service_id_list[]")
#     date_value_list = request.GET.getlist("date_value_list[]")
#     time_value_list = request.GET.getlist("time_value_list[]")
#     print(date_value_list)
#     print(100 * "-")
#     print(time_value_list)
#     order_cart = OrderCart(request)
#     order_cart.update(service_id_list, None, None, date_value_list, time_value_list)
#     return redirect("orders:show_order_cart")


# --------------------------------------------------------------------------------------------------------------------
# def status_of_order_cart(request):
#     order_cart = OrderCart(request)
#     return HttpResponse(order_cart.count)


# --------------------------------------------------------------------------------------------------------------------
# class CreateOrderView(LoginRequiredMixin, View):

#     def get(self, request):

#         user = request.user
#         customer = Customer.objects.get(user=user)
#         order = Order.objects.create(customer=customer)
#         try:
#             stylist = Stylist.objects.get(user=user)
#             # user_role = "stylist"
#         except Stylist.DoesNotExist:
#             stylist = None

#         try:
#             salon_manager = SalonManager.objects.get(user=user)
#             # user_role = "salon_manager"
#         except SalonManager.DoesNotExist:
#             salon_manager = None

#         if not stylist and not salon_manager:
#             # user_role = "customer"

#             customer = Customer.objects.get(user=user)

#             order = Order.objects.create(customer=customer)
#             order_cart = OrderCart(request)
#             for item in order_cart:
#                 service = get_object_or_404(Services, id=item["service_id"])
#                 stylist = get_object_or_404(Stylist, user_id=item["stylist_id"])
#                 salon = get_object_or_404(Salon, id=item["salon_id"])
#                 OrderDetail.objects.create(
#                     order=order,
#                     service=service,
#                     stylist=stylist,
#                     salon=salon,
#                     date=item["date"],
#                     time=item["time"],
#                     price=item["final_price"],
#                 )
#         elif stylist or salon_manager:
#             messages.warning(
#                 request, "آرایشگران و مدیران سایت قادر به رزرو وقت نیستند ", "warning"
#             )
#         return redirect("orders:check_out", order.id)  # type: ignore

# --------------------------------------------------------------------------------------------------------------------
# class CheckOutOrderView(LoginRequiredMixin, View):
#     def get(self, request, order_id):
#         order = get_object_or_404(Order, id=order_id, customer__user=request.user)
#         order_cart = OrderCart(request)
#         total_price = order_cart.calc_total_price()
#         tax = total_price * 0.09
#         order_final_price = total_price + tax

#         if order.discount:
#             order_final_price *= 1 - order.discount / 100

#         context = {
#             "order_cart": order_cart,
#             "total_price": total_price,
#             "tax": tax,
#             "order_final_price": order_final_price,
#             "form": OrderForm(),
#             "form_coupon": CouponForm(),
#             "order": order,
#         }
#         return render(request, "orders/check_out.html", context)

#     def post(self, request, order_id):
#         form = OrderForm(request.POST)
#         if not form.is_valid():
#             messages.error(request, "اطلاعات وارد شده نامعتبر است.")
#             return redirect("orders:check_out", order_id)

#         try:
#             payment_type = PaymentType.objects.get(id=form.cleaned_data["payment_type"])
#             order = get_object_or_404(Order, id=order_id, customer__user=request.user)
#             order.payment_type = payment_type
#             order.save()

#             messages.success(request, "اطلاعات شما با موفقیت به‌روزرسانی شد")
#             return redirect("payments:zarinpal", order_id)

#         except PaymentType.DoesNotExist:
#             messages.error(request, "نوع پرداخت یافت نشد.", "danger")
#             return redirect("orders:check_out", order_id)

# --------------------------------------------------------------------------------------------------------------------
# class ApplyCoupon(View):
#     def post(self, request, *args, **kwargs):
#         form = CouponForm(request.POST)
#         order_id = kwargs["order_id"]
#         if form.is_valid():
#             cd = form.cleaned_data
#             coupon_code = cd["coupon_code"]

#             coupon = Coupon.objects.filter(
#                 Q(coupon_code=coupon_code)
#                 & Q(is_active=True)
#                 & Q(start_date__lt=datetime.now())
#                 & Q(end_date__gt=datetime.now())
#             )
#             discount = 0
#             try:
#                 order = Order.objects.get(id=order_id)
#                 if coupon:
#                     discount = coupon[0].discount
#                     order.discount = discount
#                     order.save()
#                     messages.success(request, "اعمال کوپن با موفقیت انجام شد")
#                     return redirect("orders:check_out", order_id)
#                 else:
#                     order.discount = discount
#                     order.save()
#                     messages.error(request, "کد وارد شده معتبر نیست", "danger")

#             except ObjectDoesNotExist:
#                 messages.error(request, "سفارش موجود نیست")
#             return redirect("orders:check_out", order_id)

# ---------------------------------------------------------------------------------------------------------------
class BookingStylistSelect(View):
    def get(self, request):
        salon_id = request.GET.get("salon_id")
        selected_services_str = request.GET.get("selected_services", "")

        try:
            selected_service_ids = [int(s) for s in selected_services_str.split(",") if s]
        except (ValueError, TypeError):
            selected_service_ids = []

        if not salon_id or not selected_service_ids:
            # می‌توانید یک پیام خطا یا ریدایرکت مناسب اضافه کنید
            return render(request, "orders/select_stylists.html", {"error": "اطلاعات ناقص است."})

        # ✅ بهینه‌سازی: واکشی سالن
        salon = get_object_or_404(Salon, id=salon_id)

        # ✅ بهینه‌سازی اصلی: واکشی تمام خدمات و آرایشگران مرتبط در یک کوئری جامع
        selected_services_qs = Services.objects.filter(id__in=selected_service_ids).prefetch_related(
            Prefetch(
                'stylists',
                queryset=Stylist.objects.select_related('user').annotate(
                    # محاسبه میانگین امتیاز برای هر آرایشگر در همان کوئری
                    avg_score=Avg('scoring_stylist__score')
                ).filter(stylists_of_salon=salon) # فقط آرایشگران همین سالن
            )
        )

        context = {
            "salon": salon,
            "selected_services": selected_services_qs,
        }
        return render(request, "orders/select_stylists.html", context)

# ------------------------------------------------------------------------------
def is_jalali_leap(year):
    leap_remainders = [1, 5, 9, 13, 17, 22, 26, 30]
    return (year % 33) in leap_remainders

def days_in_jalali_month(year, month):
    if month <= 6:
        return 31
    elif month <= 11:
        return 30
    else:
        return 30 if is_jalali_leap(year) else 29

class BookingDateTimeSelect(View):
    def get(self, request):
        salon_id = request.GET.get("salon_id") or request.session.get("salon_id")
        selections_json = request.GET.get("selections", "[]")

        if not salon_id:
            # اگر salon_id وجود نداشت، کاربر را به صفحه قبل هدایت کن
            # (اینجا باید آدرس مناسب را قرار دهید)
            return redirect("salons:show_salons") 

        try:
            selections = json.loads(selections_json)
        except json.JSONDecodeError:
            selections = []

        stylist_ids = [int(sel["stylist_id"]) for sel in selections if sel.get("stylist_id")]

        # --- ۱. آماده‌سازی محدوده تاریخ ---
        j_today = JalaliDate.today()
        current_year_jalali = j_today.year
        current_month_jalali = j_today.month
        j_days_in_month = days_in_jalali_month(j_today.year, j_today.month)
        start_day = j_today.day
        
        days = []
        month_name = j_today.strftime("%B")
        for d in range(start_day, j_days_in_month + 1):
            day = JalaliDate(j_today.year, j_today.month, d)
            days.append({
                "date_str": day.strftime("%Y-%m-%d"), # کلید تاریخ شمسی
                "jalali_day": day.day,
                "day_name": day.strftime("%A"),
            })
        
        start_date_gregorian = JalaliDate(current_year_jalali, current_month_jalali, start_day).todate()
        end_date_gregorian = JalaliDate(current_year_jalali, current_month_jalali, j_days_in_month).todate()

        # --- ۲. واکشی بهینه تمام داده‌ها ---
        stylists_qs = Stylist.objects.filter(pk__in=stylist_ids).select_related('user').prefetch_related(
            Prefetch(
                'stylist_schedules',
                queryset=StylistSchedule.objects.filter(
                    salon_id=salon_id,
                    date__range=[start_date_gregorian, end_date_gregorian]
                ).order_by('start_time'),
                to_attr='schedules_for_month'
            )
        )

        # --- ۳. پردازش داده‌ها در پایتون ---
        stylists_data = []
        for stylist in stylists_qs:
            schedule_by_date = defaultdict(list)
            for schedule in stylist.schedules_for_month:
                # ✅ اصلاح اصلی: تبدیل تاریخ میلادی دیتابیس به رشته شمسی برای کلید دیکشنری
                jalali_schedule_date = JalaliDate(schedule.date)
                date_key = jalali_schedule_date.strftime("%Y-%m-%d")
                
                schedule_by_date[date_key].append({
                    "start_time": schedule.start_time.strftime("%H:%M"),
                    "end_time": schedule.end_time.strftime("%H:%M"),
                })

            stylists_data.append({
                "stylist": stylist,
                "schedule_json": json.dumps(schedule_by_date),
                "available_slots_count": len(stylist.schedules_for_month),
            })

        context = {
            "salon_id": salon_id,
            "stylists_data": stylists_data,
            "days": days,
            "current_year": current_year_jalali,
            "month_name": month_name,
        }
        return render(request, "orders/select_datetime.html", context)

    def post(self, request):
        if "salon_id" in request.POST:
            salon_id = request.POST.get("salon_id")
            request.session["salon_id"] = salon_id

        if (
            "stylist_id" in request.POST
            and "selected_date" in request.POST
            and "selected_time" in request.POST
        ):
            request.session["stylist_id"] = request.POST.get("stylist_id")
            request.session["selected_date"] = request.POST.get("selected_date")
            request.session["selected_time"] = request.POST.get("selected_time")
            return redirect("orders:reservation_preview")

        elif "stylists_data" in request.POST:
            request.session["stylists_data"] = request.POST.get("stylists_data")
            if "service_selections" in request.POST:
                request.session["service_selections"] = request.POST.get("service_selections")
            return redirect("orders:reservation_preview")

        return redirect("orders:select_dateTime")

# -----------------------------------------------------------------------------------------------------------------------
class ReservationDetailView(LoginRequiredMixin, View):
    template_name = "orders/reservation_preview.html"

    def get(self, request, *args, **kwargs):
        # --- ۱. خواندن و اعتبارسنجی داده‌ها از Session ---
        try:
            stylists_data = json.loads(request.session.get("stylists_data", "[]"))
            service_selections = json.loads(request.session.get("service_selections", "[]"))
            salon_id = request.session.get("salon_id")
            
            if not salon_id or not stylists_data or not service_selections:
                messages.error(request, "اطلاعات رزرو شما ناقص است. لطفاً دوباره تلاش کنید.")
                return redirect("orders:select_dateTime") # یا هر صفحه مناسب دیگر

        except (json.JSONDecodeError, TypeError):
            messages.error(request, "خطا در پردازش اطلاعات رزرو.")
            return redirect("orders:select_dateTime")

        # --- ۲. جمع‌آوری تمام ID های مورد نیاز ---
        stylist_ids = {item.get("stylist_id") for item in stylists_data if item.get("stylist_id")}
        service_ids = {item.get("service_id") for item in service_selections if item.get("service_id")}

        # --- ۳. واکشی بهینه تمام داده‌ها در چند کوئری اصلی ---
        # ✅ بهینه‌سازی: واکشی سالن به همراه آمار امتیازات در یک کوئری
        salon = get_object_or_404(
            Salon.objects.annotate(
                avg_score=Avg('scoring_salon__score', filter=Q(scoring_salon__comment__is_active=True)),
                reviews_count=Count('scoring_salon', filter=Q(scoring_salon__comment__is_active=True))
            ), 
            pk=salon_id
        )

        # ✅ بهینه‌سازی: واکشی تمام آرایشگران و سرویس‌های مورد نیاز
        stylists_map = {s.pk: s for s in Stylist.objects.filter(pk__in=stylist_ids).select_related('user')}
        services_map = {s.pk: s for s in Services.objects.filter(pk__in=service_ids)}
        
        # ✅ بهینه‌سازی: واکشی تمام قیمت‌های مورد نیاز در یک کوئری
        prices_qs = ServicePrice.objects.filter(service_id__in=service_ids, stylist_id__in=stylist_ids)
        prices_map = {(sp.service_id, sp.stylist_id): sp.price for sp in prices_qs}

        # --- ۴. پردازش داده‌ها در پایتون (بدون کوئری اضافه) ---
        stylists_info = []
        for data in stylists_data:
            stylist = stylists_map.get(int(data.get("stylist_id")))
            if stylist:
                stylists_info.append({
                    "stylist": stylist,
                    "selected_date": data.get("selected_date"),
                    "selected_time": data.get("selected_time"),
                })

        services_info = []
        total_price = 0
        for item in service_selections:
            service = services_map.get(int(item.get("service_id")))
            stylist = stylists_map.get(int(item.get("stylist_id")))
            if service and stylist:
                price = prices_map.get((service.id, stylist.user.id), 0)
                services_info.append({
                    "service": service, "stylist": stylist, "price": price
                })
                total_price += price

        tax = int(total_price * 0.09)
        final_price = total_price + tax

        context = {
            "stylists_info": stylists_info, "services_info": services_info,
            "salon": salon, "total_price": total_price,
            "tax": tax, "final_price": final_price,
        }
        return render(request, self.template_name, context)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        if "confirm_reservation" in request.POST:
            # منطق get را برای واکشی و اعتبارسنجی مجدد داده‌ها تکرار می‌کنیم
            # ... (می‌توانید منطق get را در یک متد کمکی قرار دهید تا تکراری نباشد) ...
            stylists_data = json.loads(request.session.get("stylists_data", "[]"))
            service_selections = json.loads(request.session.get("service_selections", "[]"))
            salon_id = request.session.get("salon_id")
            
            customer = get_object_or_404(Customer, user=request.user)
            salon = get_object_or_404(Salon, pk=salon_id)

            # ایجاد سفارش اصلی
            order = Order.objects.create(customer=customer, is_finally=False)

            # واکشی گروهی قیمت‌ها
            stylist_ids = {item.get("stylist_id") for item in service_selections}
            service_ids = {item.get("service_id") for item in service_selections}
            prices_qs = ServicePrice.objects.filter(service_id__in=service_ids, stylist_id__in=stylist_ids)
            prices_map = {(sp.service_id, sp.stylist_id): sp.price for sp in prices_qs}

            # آماده‌سازی جزئیات سفارش برای bulk_create
            order_details_to_create = []
            for item in service_selections:
                stylist_id = int(item.get("stylist_id"))
                service_id = int(item.get("service_id"))
                
                # پیدا کردن تاریخ و زمان مربوط به این آرایشگر
                time_data = next((s for s in stylists_data if int(s.get("stylist_id")) == stylist_id), None)
                
                if time_data:
                    order_details_to_create.append(
                        OrderDetail(
                            order=order,
                            service_id=service_id,
                            stylist_id=stylist_id,
                            salon=salon,
                            price=prices_map.get((service_id, stylist_id), 0),
                            date=time_data.get("selected_date"),
                            time=time_data.get("selected_time"),
                        )
                    )
            
            # ✅ بهینه‌سازی: درج تمام جزئیات در یک کوئری
            OrderDetail.objects.bulk_create(order_details_to_create)

            # پاکسازی session
            for key in ["stylists_data", "service_selections", "salon_id"]:
                if key in request.session:
                    del request.session[key]

            messages.success(request, "رزرو شما با موفقیت ثبت شد.")
            return redirect("orders:appointments")
        
        # اگر درخواست معتبر نبود
        return redirect("orders:select_dateTime")

# ---------------------------------------------------------------------------------------------------------
class AppointmentsView(LoginRequiredMixin, View):
    """
    لیست نوبت‌های گذشته و آینده کاربر لاگین کرده را نمایش می‌دهد.
    """
    template_name = "orders/appointments.html"

    def get(self, request, *args, **kwargs):
        # ✅ بهینه‌سازی: واکشی مشتری و کاربر مرتبط با آن در یک کوئری
        customer = get_object_or_404(Customer.objects.select_related('user'), user=request.user)

        # تاریخ امروز به شمسی
        # فرض بر اینکه تاریخ‌ها در دیتابیس به صورت رشته شمسی ذخیره شده‌اند
        today_str = JalaliDate.today().strftime("%Y-%m-%d")

        # ✅ بهینه‌سازی: ساخت یک کوئری پایه با select_related
        # این کار از N+1 Query در تمپلیت جلوگیری می‌کند
        base_qs = OrderDetail.objects.filter(
            order__customer=customer
        ).select_related(
            'order',
            'service',
            'salon',
            'stylist__user'
        )

        # فیلتر کردن نوبت‌های گذشته و آینده با استفاده از کوئری پایه
        past_appointments = base_qs.filter(date__lt=today_str).order_by("-date", "-time")
        upcoming_appointments = base_qs.filter(date__gte=today_str).order_by("date", "time")

        context = {
            "past_appointments": past_appointments,
            "upcoming_appointments": upcoming_appointments,
        }
        return render(request, self.template_name, context)

# ---------------------------------------------------------------------------------------------------------
class AppointmentDetailView(LoginRequiredMixin, View):
    def get(self, request, order_id):
        # ✅ بهینه‌سازی اصلی: واکشی تمام اطلاعات مرتبط در یک کوئری جامع
        # با select_related و استفاده از `__` تمام JOIN های لازم را در یک مرحله انجام می‌دهیم
        appointment = get_object_or_404(
            OrderDetail.objects.select_related(
                'order',
                'service',
                'salon',
                'stylist__user'
            ),
            order_id=order_id,
            # می‌توانید برای امنیت بیشتر، فیلتر کنید که نوبت متعلق به کاربر لاگین کرده باشد
            order__customer__user=request.user,
        )

        context = {
            "appointment": appointment,
            "status": appointment.order.stylist_approved
        }
        return render(request, "orders/appointment_detail.html", context)

# --------------------------------------------------------------------------------------------
