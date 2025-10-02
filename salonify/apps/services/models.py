from django.db import models
from django.db.models import Avg
from django.urls import reverse
from django.utils import timezone
from middlewares.middlewares import RequestMiddleware
from utils import File_Uploader


# -------------------------------------------------------------------------------------------
# گروه خدمات
class GroupServices(models.Model):
    group_title = models.CharField(max_length=50, verbose_name="عنوان گروه خدمات ")
    file_upload = File_Uploader("images", "GroupServices")
    group_image = models.ImageField(
        upload_to=file_upload.upload_to, verbose_name="تصویر گروه خدمات"
    )
    descriptions = models.TextField(blank=True, null=True, verbose_name="توضیحات گروه خدمات ")
    is_active = models.BooleanField(default=True, verbose_name="وضعیت فعال/ غیرفعال", blank=True)
    group_parent = models.ForeignKey(
        "GroupServices",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="والد گروه خدمات",
        related_name="groups",
    )
    registere_date = models.DateTimeField(auto_now_add=True, verbose_name="زمان ثبت")
    published_date = models.DateTimeField(default=timezone.now, verbose_name="زمان انتشار ")
    updated_date = models.DateTimeField(auto_now=True, verbose_name="زمان آخرین ویرایش")

    def __str__(self):
        return self.group_title

    class Meta:
        verbose_name = "گروه خدمات"
        verbose_name_plural = "گروه های خدمات "
        db_table = "s_groupservices"


# -------------------------------------------------------------------------------------------
# ویژگی ها
class Feature(models.Model):
    feature_name = models.CharField(max_length=100, verbose_name="نام ویژگی ")
    product_group = models.ManyToManyField(
        GroupServices, verbose_name="گروه خدمات", related_name="features_of_groups"
    )

    def __str__(self):
        return self.feature_name

    class Meta:
        verbose_name = "ویژگی"
        verbose_name_plural = "ویژگی ها"
        db_table = "s_feature"


# -------------------------------------------------------------------------------------------
# خدمات
class Services(models.Model):
    service_name = models.CharField(max_length=500, verbose_name="نام خدمات")
    summery_description = models.TextField(
        default="", verbose_name="توضیحات خلاصه خدمات", blank=True, null=True
    )
    description = models.TextField(blank=True, verbose_name="توضیحات کامل خدمات", null=True)
    file_upload = File_Uploader("images", "services")
    service_image = models.ImageField(
        upload_to=file_upload.upload_to, verbose_name="تصویر خدمات", null=True
    )
    is_active = models.BooleanField(
        default=True, blank=True, verbose_name="وضعیت فعال / غیرفعال", null=True
    )
    service_group = models.ManyToManyField(
        GroupServices, verbose_name="گروه خدمات", related_name="services_of_group"
    )
    stylists = models.ManyToManyField(
        "accounts.Stylist", verbose_name="آرایشگران", related_name="services_of_stylist"
    )
    view_count = models.IntegerField(default=0, verbose_name="تعداد بازدید")
    duration_minutes = models.PositiveIntegerField(
        verbose_name="مدت زمان خدمت (دقیقه)", default=30
    )
    registere_date = models.DateTimeField(auto_now_add=True, verbose_name="زمان ثبت")
    published_date = models.DateTimeField(default=timezone.now, verbose_name="زمان انتشار")
    updated_date = models.DateTimeField(auto_now=True, verbose_name="زمان آخرین ویرایش")
    features = models.ManyToManyField(Feature, through="ServiceFeature")

    def __str__(self):
        return f"{self.service_name}"

    def get_absolute_url(self):
        return reverse("services:service_detail", kwargs={"slug": self.slug})

    def get_user_score(self):
        request = RequestMiddleware(get_response=None)
        request = request.thread_local.current_request
        score = 0
        user_score = self.scoring_services.filter(scoring_user=request.user)  # type: ignore
        if user_score.count() > 0:
            score = user_score[0].score
        return score

    def get_average_score(self):
        avg_score = self.scoring_services.all().aggregate(Avg("score"))["score__avg"]  # type: ignore
        if avg_score is None:
            avg_score = 0
        return avg_score

    def get_user_favorite(self):
        request = RequestMiddleware(get_response=None)
        request = request.thread_local.current_request
        flag = self.favorite_services.filter(favorite_user=request.user).exists()  # type: ignore
        return flag

    def get_min_max_price(self):
        prices = []
        for stylist in self.stylists.all():
            price = stylist.get_price_for_service(self)
            if price is not None:
                prices.append(price)

        min_price = min(prices) if prices else None
        max_price = max(prices) if prices else None
        return min_price, max_price

    class Meta:
        verbose_name = "خدمات"
        verbose_name_plural = "خدمات"
        db_table = "s_services"


# ----------------------------------------------------------------------------------------------------------
# مقدار ویژگی
class FeatureValue(models.Model):
    value_title = models.CharField(max_length=100, verbose_name="عنوان مقدار")
    feature = models.ForeignKey(
        Feature,
        null=True,
        blank=True,
        verbose_name="ویژگی",
        on_delete=models.CASCADE,
        related_name="feature_values",
    )

    def __str__(self):
        return self.value_title

    class Meta:
        verbose_name = "مقدار ویژگی"
        verbose_name_plural = "مقادیر ویژگی ها "


# ---------------------------------------------------------------------------------------------------------
# ویژگی خدمات
class ServiceFeature(models.Model):
    service = models.ForeignKey(
        Services,
        on_delete=models.CASCADE,
        verbose_name="خدمات",
        related_name="service_features",
    )
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE, verbose_name="ویژگی")
    value = models.CharField(max_length=100, verbose_name="مقدار")
    filter_value = models.ForeignKey(
        FeatureValue,
        on_delete=models.CASCADE,
        verbose_name="مقدار فیلتر",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.feature} - {self.service} : {self.value}"

    class Meta:
        verbose_name = "ویژگی خدمات"
        verbose_name_plural = "ویژگی های خدمات"


# -------------------------------------------------------------------------------------------------------------
# گالری خدمات
class ServiceGallery(models.Model):
    service = models.ForeignKey(
        Services,
        on_delete=models.CASCADE,
        verbose_name="خدمات",
        related_name="gallery_images",
        null=True,
    )
    file_upload = File_Uploader("images", "services_gallery")
    service_image = models.ImageField(
        upload_to=file_upload.upload_to, verbose_name="تصویر خدمات", null=True
    )

    class Meta:
        verbose_name = "تصویر خدمات"
        verbose_name_plural = "تصاویر خدمات"


# -------------------------------------------------------------------------------------------------------
class ServicePrice(models.Model):
    stylist = models.ForeignKey(
        "accounts.Stylist", on_delete=models.CASCADE, related_name="stylist_prices"
    )
    service = models.ForeignKey(Services, on_delete=models.CASCADE, related_name="service_prices")
    price = models.IntegerField(default=0, verbose_name="قیمت")

    class Meta:
        verbose_name = "قیمت خدمت"
        verbose_name_plural = "قیمت های خدمت"
        unique_together = ("service", "stylist")
