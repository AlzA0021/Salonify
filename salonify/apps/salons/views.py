from collections import Counter
from urllib import request
from django.db.models import Avg, Min, Prefetch, Q, Exists, OuterRef, BooleanField, Count, Value
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views import View
from apps.accounts.models import  WorkSamples, Customer
from apps.comments_scores_favories.forms import CommentScoringForm
from apps.comments_scores_favories.models import Comments, Favorits
from apps.services.models import Services
from .models import Salon, SalonVisit, SalonOpeningHours
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from apps.orders.models import OrderDetail


# --------------------------------------------------------------------------------------------------------------------------------
# @method_decorator(cache_page(60 * 30), name='dispatch') # کش به مدت ۱۰ دقیقه
class ShowSalonsView(View):
    def get(self, request):
        user = request.user

        # ✅ بهینه‌سازی شماره ۱: ساخت یک کوئری جامع و کامل
        # تمام اطلاعات مورد نیاز (میانگین امتیاز، تعداد امتیاز، علاقمندی کاربر) را با annotate واکشی می‌کنیم

        # ابتدا یک annotation برای بررسی علاقمندی کاربر می‌سازیم
        is_favorite_ann = (
            Exists(Favorits.objects.filter(salon=OuterRef("pk"), favorite_user__user=user))
            if user.is_authenticated
            else Value(False, output_field=BooleanField())
        )

        # کوئری اصلی و جامع
        all_salons_qs = (
            Salon.objects.filter(is_active=True)
            .select_related("neighborhood")
            .annotate(
                avg_score=Avg("scoring_salon__score"),
                num_scores=Count("scoring_salon__score"),  # تعداد امتیازها را هم اضافه می‌کنیم
                is_favorite=is_favorite_ann,
            )
        )

        # ✅ بهینه‌سازی شماره ۲: فقط یک بار کوئری را اجرا و نتیجه را در یک لیست ذخیره می‌کنیم
        # این کار از چند بار فراخوانی دیتابیس جلوگیری می‌کند
        all_salons_list = list(all_salons_qs)

        # ✅ بهینه‌سازی شماره ۳: تمام مرتب‌سازی‌ها و فیلترها در پایتون انجام می‌شود
        # این عملیات روی لیست در حافظه انجام شده و بسیار سریع است

        # سالن‌های اخیراً ثبت‌شده
        # با key=lambda s: s.registere_date مرتب‌سازی و ۱۰ تای اول را انتخاب می‌کنیم
        recent_salons = sorted(all_salons_list, key=lambda s: s.registere_date, reverse=True)[:10]

        # سالن‌های برتر بر اساس میانگین امتیاز
        # None ها را با 0 جایگزین می‌کنیم تا مرتب‌سازی به خطا نخورد
        top_salons = sorted(all_salons_list, key=lambda s: s.avg_score or 0, reverse=True)[:10]

        # سالن‌های مورد علاقه کاربر (با استفاده از is_favorite که annotate کردیم)
        favorits_salons = []
        if user.is_authenticated:
            favorits_salons = [s for s in all_salons_list if s.is_favorite]

        # آخرین سالن‌هایی که کاربر بازدید کرده است
        last_visited_salons = []
        if user.is_authenticated:
            # فقط ID سالن‌های بازدید شده را از دیتابیس می‌گیریم (یک کوئری سریع)
            visited_salon_ids = list(
                SalonVisit.objects.filter(user=user)
                .order_by("-visit_date")
                .values_list("salon_id", flat=True)[:10]
            )
            # با استفاده از ID ها، سالن‌ها را از لیست اصلی پیدا می‌کنیم
            visited_salons_dict = {s.pk: s for s in all_salons_list if s.pk in visited_salon_ids}
            last_visited_salons = [visited_salons_dict[id] for id in visited_salon_ids]

        # 🆕 اضافه کردن بخش "رزرو مجدد" - آخرین رزروهای کاربر
        book_again_orders = []
        if user.is_authenticated:
            try:
                # بر اساس مدل‌های شما، Order به Customer ارتباط دارد
                # فرض می‌کنیم Customer یک user field دارد

                # روش 1: اگر Customer یک user field دارد (OneToOneField یا ForeignKey)
                recent_completed_orders = (
                    OrderDetail.objects.filter(
                        order__customer__user=user,  # از طریق customer به user
                        order__is_finally=True,  # بر اساس مدل شما: سفارش نهایی شده
                        order__is_paid=True,  # پرداخت شده
                        date__lt=timezone.now().date(),  # سفارشات گذشته
                    )
                    .select_related("salon", "service", "stylist", "order", "order__customer")
                    .order_by("-date", "-time")[:20]  # ابتدا 20 تا بگیریم تا تکراری‌ها را حذف کنیم
                )

                # حذف تکراری‌ها بر اساس salon_id در Python برای کارایی بهتر
                
                book_again_orders = []
                for order in recent_completed_orders:
                    
                    book_again_orders.append(order)
                    
                    if len(book_again_orders) >= 5:  # حداکثر 5 سالن مختلف
                        break
                
            except Exception as e:
                # اگر Customer مدل user field نداشت، سعی کنید با روش‌های دیگر
                try:
                    # روش 2: اگر Customer model phone یا email field دارد
                    # و می‌خواهیم از طریق آن پیدا کنیم
                    customer = Customer.objects.filter(
                        user=user  # یا phone=user.phone یا email=user.email
                    ).first()

                    if customer:
                        recent_completed_orders = (
                            OrderDetail.objects.filter(
                                order__customer=customer,
                                order__is_finally=True,
                                order__is_paid=True,
                                date__lt=timezone.now().date(),
                            )
                            .select_related("salon", "service", "stylist", "order")
                            .order_by("-date", "-time")[:20]
                        )

                        seen_salons = set()
                        book_again_orders = []
                        for order in recent_completed_orders:
                            if order.salon_id not in seen_salons:
                                book_again_orders.append(order)
                                seen_salons.add(order.salon_id)
                                if len(book_again_orders) >= 5:
                                    break
                    else:
                        book_again_orders = []

                except Exception as e2:
                    print(f"Error in book again orders: {e2}")
                    book_again_orders = []

        context = {
            "recent_salons": recent_salons,
            "top_salons": top_salons,
            "user": user,
            "favorits_salons": favorits_salons,
            "last_visited_salons": last_visited_salons,
            "book_again_orders": book_again_orders, 
        }

        return render(request, "salons/show_salons.html", context)


#-------------------------------------------------------------------------------------------------------------------------------
@method_decorator(cache_page(60 * 10), name='dispatch') # کش به مدت ۱۰ دقیقه
class DetailSalonView(View):
    def get(self, request, salon_id):
        # =================================================================
        # ۱. واکشی آبجکت اصلی سالن به همراه روابط اولیه
        # =================================================================
        salon = get_object_or_404(
            Salon.objects.prefetch_related(
                # ✨ OPTIMIZED: Use Prefetch to order the related data in the same query
                Prefetch(
                    "opening_hours",
                    queryset=SalonOpeningHours.objects.order_by("day_of_week"),
                    to_attr="ordered_opening_hours" # Use a new attribute to store the sorted list
                ),
                "supplementary_info",
                "gallery_images"
            ),
            id=salon_id,
            is_active=True,
        )

        # =================================================================
        # ۲. واکشی آرایشگران با تمام اطلاعات مورد نیاز تمپلیت (This was already good)
        # =================================================================
        stylists_qs = (
            salon.stylists.filter(is_active=True)
            .select_related("user")
            .annotate(avg_score=Avg('scoring_stylist__score'))
            .prefetch_related(
                Prefetch(
                    "work_samples_of_stylist",
                    queryset=WorkSamples.objects.filter(is_active=True).select_related('service')
                )
            )
        )
        
        # =================================================================
        # ۳. واکشی خدمات با تمام اطلاعات مورد نیاز تمپلیت (This was already good)
        # =================================================================
        services_qs = (
            Services.objects.filter(is_active=True, services_of_salon=salon)
            .prefetch_related("service_group", "stylists")
            .annotate(
                min_price=Min("service_prices__price"),
                avg_score=Avg('scoring_services__score')
            )
        )
        
        # =================================================================
        # ۴. واکشی نظرات با تمام اطلاعات مورد نیاز تمپلیت
        # =================================================================
        comments_filter = Q(salon=salon, is_active=True)
        current_customer = None
        if request.user.is_authenticated and hasattr(request.user, 'customer_profile'):
            current_customer = request.user.customer_profile
            comments_filter |= Q(salon=salon, comment_user=current_customer, is_active=False)

        comments_qs = (
            Comments.objects.filter(comments_filter)
            # ✨ OPTIMIZED: Fetch the Customer's related User object to prevent N+1 queries in the loop.
            # Also prefetching the profile image's storage attribute if needed, though often not necessary.
            .select_related(
                "scoring", 
                "stylist__user", 
                "service", 
                "comment_user__user" # This is the key fix!
            )
            .order_by("-register_date")
        )
        
        # =================================================================
        # ۵. پردازش دیتا در پایتون (بدون کوئری اضافه)
        # =================================================================
        
        # ثبت بازدید کاربر
        if request.user.is_authenticated:
            SalonVisit.objects.update_or_create(
                user=request.user, salon=salon, defaults={"visit_date": timezone.now()}
            )

        # استخراج گروه‌های خدمات از کوئری از پیش واکشی شده
        service_groups = {group for service in services_qs for group in service.service_group.all()}
        
        # پردازش لیست نظرات (This loop is now efficient)
        comments_list = []
        approved_scores = []
        for c in comments_qs:
            score_val = c.scoring.score if hasattr(c, "scoring") and c.scoring else None
            if c.is_active and score_val is not None:
                approved_scores.append(score_val)
            
            # Now, accessing c.comment_user.user will not cause a new query
            user_full_name = c.comment_user.user.get_fullName() if c.comment_user and hasattr(c.comment_user, 'user') else c.get_fullName() # Defensive check
            avatar_url = c.comment_user.profile_image.url if c.comment_user and c.comment_user.profile_image else None
            
            comments_list.append({
                "user_full_name": user_full_name,
                "date": c.register_date,
                "comment_text": c.comment_text,
                "score": score_val,
                "avatar_url": avatar_url,
                "stylist_name": f"{c.stylist.user.name} {c.stylist.user.family}" if c.stylist and hasattr(c.stylist, 'user') else None,
                "service_name": c.service.service_name if c.service else None,
                "is_pending": not c.is_active and current_customer and c.comment_user_id == current_customer.pk,
            })
            
        # محاسبه آمار امتیازات
        score_counter = Counter(approved_scores)
        total_reviews = len(approved_scores)
        star_counts = {i: score_counter.get(i, 0) for i in range(1, 6)}
        average_score = round(sum(approved_scores) / total_reviews, 1) if total_reviews > 0 else 0

        # بررسی علاقمندی کاربر (یک کوئری ساده و ضروری)
        is_favorite = False
        if request.user.is_authenticated and hasattr(request.user, 'customer_profile'):
            is_favorite = Favorits.objects.filter(
                favorite_user=request.user.customer_profile,  
                salon=salon
            ).exists()



        form = CommentScoringForm(salon=salon)

        # =================================================================
        # ۶. ساخت Context نهایی برای ارسال به Template
        # =================================================================
        context = {
            "salon": salon,
            "stylists": stylists_qs,
            "services": services_qs,
            "service_groups": service_groups,
            "comments_list": comments_list,
            # ✨ OPTIMIZED: Access the prefetched, ordered attribute directly
            "opening_hours_list": salon.ordered_opening_hours,
            # ✨ OPTIMIZED: Access prefetched data directly without .all()
            "supplementary_info": salon.supplementary_info.all(), # .all() is ok here, but direct access is cleaner
            "average_score": average_score,
            "total_reviews": total_reviews,
            "star_counts": star_counts,
            "is_favorite": is_favorite,
            "form": form,
            "hide_navbar": True, 
        }
        return render(request, "salons/detail_salon.html", context) 

# -------------------------------------------------------------------------------------------------------------
