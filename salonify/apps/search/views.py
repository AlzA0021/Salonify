import json
import re
from datetime import datetime
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.contrib.postgres.aggregates import StringAgg
from django.db.models import Avg, Q
from django.http import HttpResponseNotAllowed, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from apps.accounts.models import Customer, SalonManager
from apps.orders.models import OrderDetail
from apps.salons.models import Salon
from apps.stylists.models import StylistSchedule


# --------------------------------------------------------------------------------------
def salon_search(request):
    query = request.GET.get("q", "")

    salons = (
        Salon.objects.annotate(services_list=StringAgg("services__service_name", delimiter=", "))
        .filter(
            Q(salon_name__icontains=query)
            | Q(address__icontains=query)
            | Q(services_list__icontains=query)
        )
        .distinct()
    )

    serialized_salons = []
    for salon in salons:
        serialized_salons.append(
            {
                "id": salon.pk,
                "salon_name": salon.salon_name,
                "address": salon.address,
                "banner_image": salon.banner_image.url if salon.banner_image else "",
                "get_average_score": salon.get_average_score(),
                "neighborhood": salon.neighborhood.name if salon.neighborhood else None,
                "location": {
                    "type": "Point",
                    "coordinates": [salon.location.x, salon.location.y],
                },
            }
        )

    return JsonResponse({"salons": serialized_salons})


# --------------------------------------------------------------------------------------
class SearchPageView(View):
    def get(self, request, *args, **kwargs):
        salon = Salon.objects.all()

        context = {"salon": salon}

        return render(request, "search/search_page.html", context)


# --------------------------------------------------------------------------------------
def salon_list(request):
    salons = Salon.objects.all()
    data = []
    for salon in salons:
        data.append(
            {
                "salon_name": salon.salon_name,
                "location": {
                    "coordinates": [
                        salon.location.x,
                        salon.location.y,
                    ]  # تبدیل به لیست [longitude, latitude]
                },
            }
        )
    return JsonResponse(data, safe=False)


# -------------------------------------------------------------------------------------------------
class FilterSalonView(View):
    """
    ویویی که درخواست‌های AJAX مربوط به فیلتر سالن‌ها را دریافت کرده و بر اساس
    فیلترهای انتخابی، لیست سالن‌های فیلتر شده را به صورت JSON برمی‌گرداند.
    """

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "داده‌های ارسالی به صورت JSON معتبر نیست."}, status=400)

        user_lat = data.get("latitude")
        user_lng = data.get("longitude")
        sort_value = data.get("sort", "")
        # توجه: فیلد قیمت در مدل فعلی وجود ندارد.
        # price_value = data.get("price", "")
        neighborhood = data.get("type", "")

        salons = Salon.objects.all()

        # فیلتر بر اساس محله (در صورتی که گزینه انتخابی غیر از "همه" باشد)
        if neighborhood and neighborhood != "همه":
            salons = salons.filter(neighborhood__name__iexact=neighborhood)

        # اعمال مرتب‌سازی بر اساس گزینه انتخاب شده
        if sort_value:
            if sort_value == "جدیدترین":
                salons = salons.order_by("-registere_date")
            elif sort_value == "پربازدیدترین":
                salons = salons.order_by("-registere_date")
            elif sort_value == "پیشنهادی":
                salons = salons.annotate(avg_score=Avg("scoring_salon__score")).order_by(
                    "-avg_score"
                )
            elif sort_value == "نزدیکترین":
                if user_lat is None or user_lng is None:
                    return JsonResponse({"error": "موقعیت کاربر مشخص نیست."}, status=400)
                try:
                    # توجه: در GeoDjango، ترتیب مقادیر به صورت (longitude, latitude) می‌باشد.
                    user_location = Point(float(user_lng), float(user_lat), srid=4326)
                except (ValueError, TypeError):
                    return JsonResponse({"error": "موقعیت کاربر نامعتبر است."}, status=400)
                # تنها سالن‌هایی که موقعیت مشخص دارند در نظر گرفته شوند
                salons = salons.filter(location__isnull=False)
                salons = salons.annotate(distance=Distance("location", user_location)).order_by(
                    "distance"
                )

        salons_data = []
        for salon in salons:
            salon_data = {
                "id": salon.id,
                "salon_name": salon.salon_name,
                "banner_image": salon.banner_image.url if salon.banner_image else "",
                "address": salon.address,
                "get_average_score": salon.get_average_score(),
                "neighborhood": salon.neighborhood.name if salon.neighborhood else "",
                # ارائه مختصات: در GeoDjango، salon.location.x = طول (longitude) و salon.location.y = عرض (latitude)
                "location": {
                    "coordinates": (
                        [salon.location.x, salon.location.y] if salon.location else [0, 0]
                    )
                },
            }
            # افزودن فاصله (در صورتی که موجود باشد) به عنوان "zone" برای نمایش در نقشه
            if hasattr(salon, "distance") and salon.distance is not None:
                salon_data["zone"] = round(salon.distance.km, 2)
            else:
                salon_data["zone"] = ""
            salons_data.append(salon_data)

        return JsonResponse({"salons": salons_data})


# -----------------------------------------------------------------------------------------------------------------------------------------------
@csrf_exempt
def salonify_search(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    location_text = data.get("location", "")
    date_text = data.get("date", "")
    time_text = data.get("time", "")
    service_group = data.get("service_group", "")

    # بررسی اینکه آیا فیلترهای زمان/تاریخ/خدمت داده شده‌اند
    schedule_filter_needed = (
        (date_text and date_text != "هر تاریخی")
        or (time_text and time_text != "هر زمانی")
        or bool(service_group)
    )
    schedule_q = Q()

    # فیلتر تاریخ (در صورت انتخاب تاریخ)
    if date_text and date_text != "هر تاریخی":
        try:
            search_date = datetime.strptime(date_text, "%Y-%m-%d").date()
            schedule_q &= Q(date=search_date)
        except ValueError:
            pass

    # فیلتر زمان (در صورت انتخاب زمان)
    time_range = None
    if time_text and time_text != "هر زمانی":
        # اگر زمان به صورت "از HH:MM تا HH:MM" ارسال شده باشد
        match = re.search(r"از\s*(\d{2}:\d{2})\s*تا\s*(\d{2}:\d{2})", time_text)
        if match:
            time_start_str, time_end_str = match.groups()
            try:
                time_start = datetime.strptime(time_start_str, "%H:%M").time()
                time_end = datetime.strptime(time_end_str, "%H:%M").time()
                time_range = (time_start, time_end)
            except ValueError:
                pass
        else:
            # در صورت استفاده از گزینه‌های سریع (صبح، بعدازظهر، شب)
            if time_text == "صبح":
                time_range = (
                    datetime.strptime("06:00", "%H:%M").time(),
                    datetime.strptime("12:00", "%H:%M").time(),
                )
            elif time_text == "بعدازظهر":
                time_range = (
                    datetime.strptime("12:00", "%H:%M").time(),
                    datetime.strptime("17:00", "%H:%M").time(),
                )
            elif time_text == "شب":
                time_range = (
                    datetime.strptime("17:00", "%H:%M").time(),
                    datetime.strptime("23:00", "%H:%M").time(),
                )
        if time_range:
            # فیلتر برنامه‌هایی که زمانشان شامل بازه انتخاب‌شده باشد
            schedule_q &= Q(start_time__lte=time_range[0], end_time__gte=time_range[1])

    # فیلتر خدمت (در صورت ارائه)
    if service_group:
        # اگر service_group عددی باشد (به عنوان شناسه خدمت)
        if service_group.isdigit():
            schedule_q &= Q(service_id=int(service_group))
        else:
            # یا بر اساس نام (مثلاً در partial به صورت متن ارسال شود)
            schedule_q &= Q(service__name__iexact=service_group)

    salons_qs = Salon.objects.all()
    if schedule_filter_needed:
        schedules = StylistSchedule.objects.filter(schedule_q)
        salon_ids = schedules.values_list("salon_id", flat=True).distinct()
        salons_qs = salons_qs.filter(id__in=salon_ids)

    # فیلتر بر اساس موقعیت جغرافیایی (اگر اطلاعات مختصات در location_text موجود باشد)
    # فرض بر این است که فرمت داده شده به صورت "موقعیت فعلی (عرض: 35.6892, طول: 51.389)" است
    match = re.search(r"عرض:\s*([0-9.]+).*طول:\s*([0-9.]+)", location_text)
    if match:
        lat_str, lon_str = match.groups()
        try:
            lat = float(lat_str)
            lon = float(lon_str)
            user_location = Point(lon, lat, srid=4326)
            # فیلتر سالن‌ها در محدوده ۱۰ کیلومتری از موقعیت کاربر
            salons_qs = salons_qs.filter(location__distance_lte=(user_location, D(km=10)))
        except ValueError:
            pass

    salons = salons_qs.distinct()

    # آماده‌سازی خروجی به فرم JSON
    salons_data = []
    for salon in salons:
        salons_data.append(
            {
                "id": salon.pk,
                "salon_name": salon.salon_name,
                "banner_image": salon.banner_image.url if salon.banner_image else "",
                "address": salon.address,
                "get_average_score": salon.get_average_score(),
                "zone": salon.zone,
                "neighborhood": str(salon.neighborhood) if salon.neighborhood else "",
                "location": {
                    "coordinates": (
                        [salon.location.x, salon.location.y] if salon.location else [0, 0]
                    )
                },
            }
        )

    return JsonResponse({"salons": salons_data})


# ---------------------------------------------------------------------------------------
def customers_search(request):
    query = request.GET.get("q", "")
    user = request.user
    salon_manager = get_object_or_404(SalonManager, user=user)
    salon = get_object_or_404(Salon, salon_manager=salon_manager)

    # Find customers who have ordered from this salon
    customer_ids = (
        OrderDetail.objects.filter(salon=salon)
        .values_list("order__customer", flat=True)
        .distinct()
    )

    # Filter these customers based on the search query
    customers = (
        Customer.objects.filter(Q(user_id__in=customer_ids) | Q(added_by_salon=salon))
        .filter(
            Q(user__name__icontains=query)
            | Q(user__family__icontains=query)
            | Q(user__mobile_number__icontains=query)
            | Q(user__email__icontains=query)
        )
        .distinct()
    )

    serialized_customers = []
    for customer in customers:
        customer_data = {
            "id": customer.user.pk,
            "name": customer.get_fullName(),
            "phone_number": customer.user.mobile_number,
            "email": customer.user.email,
        }

        # Add profile image URL if it exists
        if customer.profile_image:
            customer_data["profile_image"] = customer.profile_image.url

        serialized_customers.append(customer_data)

    return JsonResponse({"customers": serialized_customers})


# ----------------------------------------------------------------------------------------
class FilterCustomersView(View):

    def post(self, request, *args, **kwargs):
        """Handle POST requests for filter submission"""
        # Get filter parameters from POST data
        sort_by = request.POST.get("sort_by", "newest")
        client_group = request.POST.get("client_group", "all")
        gender = request.POST.get("gender", "all")

        # Store filter preferences in session for persistence
        request.session["customer_filters"] = {
            "sort_by": sort_by,
            "client_group": client_group,
            "gender": gender,
        }

        # Apply filters
        user = request.user
        salon_manager = get_object_or_404(SalonManager, user=user)
        salon = get_object_or_404(Salon, salon_manager=salon_manager)

        # Base queryset - only customers of this salon
        customers = Customer.objects.filter(added_by_salon=salon).distinct()

        # Apply sorting
        if sort_by == "newest":
            customers = customers.order_by("-user__register_date")
        elif sort_by == "oldest":
            customers = customers.order_by("user__register_date")
        elif sort_by == "name_asc":
            customers = customers.order_by("user__name", "user__family")
        elif sort_by == "name_desc":
            customers = customers.order_by("-user__name", "-user__family")

        # For AJAX requests, return JSON data
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            customers_data = []
            for customer in customers:
                profile_image_url = customer.profile_image.url if customer.profile_image else None
                customers_data.append(
                    {
                        "id": customer.user.pk,
                        "name": customer.get_fullName(),
                        "phone_number": customer.user.mobile_number,
                        "email": customer.user.email or "بدون ایمیل",
                        "profile_image": profile_image_url,
                    }
                )

            return JsonResponse({"customers": customers_data})

        # If not AJAX, redirect back to the page
        return redirect("dashboards:salons_customers")
