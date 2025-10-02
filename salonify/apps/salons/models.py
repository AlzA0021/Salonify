from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.contrib.gis.db import models as gis_models
from django.db import models
from middlewares.middlewares import RequestMiddleware
from utils import File_Uploader

from apps.accounts.models import Customer, CustomUser
from apps.locations.models import Neighborhood
from apps.services.models import Services


# --------------------------------------------------------------------
# Salon
class Salon(models.Model):
    salon_name = models.CharField(max_length=50, verbose_name="نام سالن")
    file_upload = File_Uploader("images", "salons_banner")
    banner_image = models.ImageField(
        upload_to=file_upload.upload_to,
        default="salons_banner.jpg",
        verbose_name="بنر",
        null=True,
        blank=True,
    )
    description = models.TextField(blank=True, verbose_name="توضیحات ")
    video = models.FileField(
        upload_to=file_upload.upload_to, blank=True, null=True, verbose_name="ویدیو"
    )
    zone = models.PositiveIntegerField(verbose_name="منطقه ", null=True, blank=True)
    location = gis_models.PointField(geography=True, verbose_name="موقعیت جغرافیایی", null=True)
    neighborhood = models.ForeignKey(
        Neighborhood,
        on_delete=models.CASCADE,
        verbose_name="محله",
        null=True,
        related_name="salon_neighborhood",
    )
    address = models.TextField(verbose_name="آدرس", blank=True, null=True)
    linkedin_link = models.CharField(
        max_length=200, null=True, blank=True, verbose_name="لینک لینکدین"
    )
    insta_link = models.CharField(
        max_length=200, null=True, blank=True, verbose_name="لینک اینستا"
    )
    telegram_link = models.CharField(
        max_length=200, null=True, blank=True, verbose_name="لینک تلگرام "
    )
    salon_manager = models.ForeignKey(
        "accounts.SalonManager",
        on_delete=models.CASCADE,
        verbose_name="مدیر سالن ",
        related_name="salon_manager",
    )
    services = models.ManyToManyField(
        Services, verbose_name="خدمات ", related_name="services_of_salon"
    )
    stylists = models.ManyToManyField(
        "accounts.Stylist", verbose_name="آرایشگر", related_name="stylists_of_salon"
    )
    is_active = models.BooleanField(default=False, verbose_name="وضعیت ")
    registere_date = models.DateTimeField(auto_now_add=True, verbose_name="زمان ثبت")
    phone_number = models.IntegerField(verbose_name="شماره تلفن ", null=True, blank=True)

    def __str__(self):
        return f"{self.salon_name}"

    def get_user_score(self):
        request = RequestMiddleware(get_response=None)
        request = request.thread_local.current_request
        score = 0
        user_score = self.scoring_salon.filter(scoring_user=request.user)
        if user_score.count() > 0:
            score = user_score[0].score
        return score

    def get_average_score(self):
        from apps.comments_scores_favories.models import Comments

        # دریافت نظرات تایید شده مرتبط با این سالن
        approved_comments = Comments.objects.filter(salon=self, is_active=True)
        approved_scores = []
        for comment in approved_comments:
            # چک می‌کنیم که اگر نظر دارای رابطه scoring است و امتیاز مقداردهی شده باشد
            if (
                hasattr(comment, "scoring")
                and comment.scoring
                and comment.scoring.score is not None
            ):
                approved_scores.append(comment.scoring.score)
        if approved_scores:
            return round(sum(approved_scores) / len(approved_scores), 1)
        return None

    def get_user_favorite(self):
        request = RequestMiddleware(get_response=None)
        request = request.thread_local.current_request
        flag = self.favorite_salon.filter(favorite_user__user=request.user,).exists()
        return flag

    def get_salon_age(self):
        # بررسی اینکه آیا ناحیه زمانی فعال است یا خیر
        if self.registere_date.tzinfo is not None:
            now = datetime.now(
                self.registere_date.tzinfo
            )  # اگر ناحیه زمانی دارد، همسان سازی با ناحیه زمانی
        else:
            now = datetime.now()  # در غیر این صورت استفاده از زمان فعلی بدون ناحیه زمانی
        # محاسبه اختلاف با استفاده از relativedelta
        age_difference = relativedelta(now, self.registere_date)

        # سن را به صورت سال برمی‌گردانیم
        return age_difference.years

    class Meta:
        verbose_name = "سالن"
        verbose_name_plural = "سالن ها "
        db_table = "s_salon"


# --------------------------------------------------------------------
# گالری سالن
class SalonsGallery(models.Model):
    salon = models.ForeignKey(
        Salon,
        on_delete=models.CASCADE,
        verbose_name="سالن",
        related_name="gallery_images",
    )
    file_upload = File_Uploader("images", "salon_gallery")
    salon_image = models.ImageField(upload_to=file_upload.upload_to, verbose_name="تصویر سالن")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")
    is_cover = models.BooleanField(default=False, verbose_name="تصویر کاور")

    class Meta:
        verbose_name = "تصویر سالن"
        verbose_name_plural = "تصاویر سالن ها "
        db_table = "salons_gallery"
        ordering = ["order"]  # مرتب‌سازی بر اساس فیلد order


# --------------------------------------------------------------------
class SalonOpeningHours(models.Model):
    DAY_CHOICES = [
        (1, "شنبه"),
        (2, "یکشنبه"),
        (3, "دوشنبه"),
        (4, "سه شنبه"),
        (5, "چهارشنبه"),
        (6, "پنج شنبه"),
        (7, "جمعه"),
    ]
    salon = models.ForeignKey(
        "Salon",
        on_delete=models.CASCADE,
        related_name="opening_hours",
        verbose_name="سالن مرتبط",
    )
    day_of_week = models.PositiveSmallIntegerField(choices=DAY_CHOICES, verbose_name="روز هفته")
    open_time = models.TimeField(null=True, blank=True, verbose_name="ساعت شروع")
    close_time = models.TimeField(null=True, blank=True, verbose_name="ساعت پایان")
    is_closed = models.BooleanField(default=False, verbose_name="تعطیل")

    class Meta:
        verbose_name = "ساعت کاری سالن"
        verbose_name_plural = "ساعت کاری سالن‌ها"
        db_table = "s_salon_opening_hours"

    def __str__(self):
        return f"{self.get_day_of_week_display()} - {self.salon.salon_name}"

    def get_day_of_week_display(self):
        """برگرداندن نام فارسی روز متناسب با day_of_week"""
        day_dict = {
            1: "شنبه",
            2: "یکشنبه",
            3: "دوشنبه",
            4: "سه شنبه",
            5: "چهارشنبه",
            6: "پنج شنبه",
            7: "جمعه",
        }
        return day_dict.get(self.day_of_week, "نامشخص")


# ---------------------------------------------------------------------
User = get_user_model()


class SalonVisit(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="کاربر",
        related_name="salon_visits",
    )
    salon = models.ForeignKey(
        "Salon",
        on_delete=models.CASCADE,
        verbose_name="سالن",
        related_name="salon_visits",
    )
    visit_date = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ بازدید")

    class Meta:
        verbose_name = "بازدید سالن"
        verbose_name_plural = "بازدیدهای سالن"
        db_table = "s_salon_visit"
        # اطمینان از اینکه هر کاربر فقط یک بازدید برای هر سالن دارد که آپدیت می‌شود
        unique_together = ("user", "salon")

    def __str__(self):
        return f"{self.user} - {self.salon} - {self.visit_date}"


# ----------------------------------------------------------------------
class SupplementaryInfoView(models.Model):
    salon = models.ForeignKey(
        Salon,
        on_delete=models.CASCADE,
        verbose_name="سالن",
        related_name="supplementary_info",
    )
    title = models.CharField(max_length=50, verbose_name="عنوان")
    description = models.CharField(max_length=200, verbose_name="توضیحات", null=True, blank=True)
    file_upload = File_Uploader("images", "SupplementaryInfo")
    icon_image = models.ImageField(
        upload_to=file_upload.upload_to,
        verbose_name="تصویر آیکون",
        null=True,
        blank=True,
    )
    icon_class = models.CharField(max_length=50, verbose_name="کلاس آیکون", null=True, blank=True)
    is_active = models.BooleanField(default=False, verbose_name="وضعیت")

    class Meta:
        verbose_name = "اطلاعات تکمیلی"
        verbose_name_plural = "اطلاعات تکمیلی"
        db_table = "s_salon_supplementary_info"


# -------------------------------------------------------------------------
class CustomerNote(models.Model):
    salon = models.ForeignKey(
        Salon,
        on_delete=models.CASCADE,
        verbose_name="سالن",
        related_name="customer_notes",
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        verbose_name="مشتری",
        related_name="customer_note",
        null=True,
        blank=True,
    )
    note = models.TextField(verbose_name="یادداشت")
    file_upload = File_Uploader("images", "customer_note")
    note_image = models.ImageField(
        upload_to=file_upload.upload_to,
        verbose_name="تصویر یادداشت",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name="ایجاد کننده",
        related_name="customer_note_creator",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "یادداشت مشتری"
        verbose_name_plural = "یادداشت‌های مشتری"
        db_table = "s_customer_note"
        
        # ✅ بهینه‌سازی: اضافه کردن ایندکس برای جستجوی سریع‌تر
        indexes = [
            models.Index(fields=['customer', 'salon'], name='customer_salon_note_idx'),
        ]

    def __str__(self):
        return f"{self.salon} - {self.created_at}"