from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    Permission,
    PermissionsMixin,
)
from django.db import models
from django.db.models import Avg
from django.utils import timezone
from utils import File_Uploader


# ----------------------------------------------------------------
#  Create User
class CustomUserManager(BaseUserManager):
    def create_user(
        self,
        mobile_number,
        active_code=None,
        email="",
        name="",
        family="",
        password=None,
    ):
        if not mobile_number:
            raise ValueError("شماره موبایل را وارد کنید ")
        user = self.model(
            mobile_number=mobile_number,
            active_code=active_code,
            email=self.normalize_email(email),
            name=name,
            family=family,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, mobile_number, email, name, family, active_code=None, password=None
    ):
        user = self.create_user(
            mobile_number=mobile_number,
            active_code=active_code,
            email=email,
            name=name,
            family=family,
            password=password,
        )
        user.is_active = True
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

# ----------------------------------------------------------------------------
# Custom User
class CustomUser(AbstractBaseUser, PermissionsMixin):
    mobile_number = models.CharField(max_length=11, unique=True, verbose_name="شماره موبایل")
    email = models.EmailField(max_length=100, blank=True, verbose_name="ایمیل")
    name = models.CharField(max_length=50, blank=True, verbose_name="نام")
    family = models.CharField(max_length=50, blank=True, verbose_name="نام خانوادگی")
    register_date = models.DateField(default=timezone.now, verbose_name="تاریخ ثبت")
    is_active = models.BooleanField(default=False, verbose_name="وضعیت ")
    active_code = models.CharField(
        max_length=100, null=True, blank=True, verbose_name="کد فعال سازی"
    )
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = "mobile_number"
    REQUIRED_FIELDS = ["email", "name", "family"]

    objects = CustomUserManager()

    # Specify custom related_name for groups
    groups = models.ManyToManyField(
        "auth.Group",
        verbose_name="groups",
        blank=True,
        help_text=("The groups this user belongs to."
                   "A user will get all permissions "
                   "granted to each of their groups."),
        related_name="custom_user_set",
        related_query_name="user",
    )

    # Specify custom related_name for user_permissions
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name="user permissions",
        blank=True,
        help_text="Specific permissions for this user.",
        related_name="custom_user_permissions",  # Specify a custom related_name
    )

    def __str__(self):
        return self.name + " " + self.family

    def get_fullName(self):
        fullName = self.name + " " + self.family
        return fullName

    @property
    def is_staff(self):
        return self.is_admin

    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"
        db_table = "A_CustomUser"

# ----------------------------------------------------------------------------
# Customer
class Customer(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        primary_key=True,
        verbose_name="کاربر",
        related_name="customer_profile",
    )
    address = models.TextField(null=True, blank=True, verbose_name="آدرس")
    file_upload = File_Uploader("images", "customers")
    profile_image = models.ImageField(
        upload_to=file_upload.upload_to,
        null=True,
        blank=True,
        verbose_name="تصویر مشتری",
    )
    added_by_salon = models.ForeignKey(
        "salons.Salon",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="اضافه شده توسط سالن",
        related_name="added_customers",
    )
    birth_date = models.DateField(null=True, blank=True, verbose_name="تاریخ تولد")
    is_active = models
    def __str__(self):
        return f"{self.user.name} {self.user.family}"

    def get_fullName(self):
        fullName = self.user.name + " " + self.user.family
        return fullName

    class Meta:
        verbose_name = "مشتری"
        verbose_name_plural = "مشتری ها "
        db_table = "A_Customers"

# -----------------------------------------------------------------------------------
class Stylist(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, primary_key=True, verbose_name="کاربر"
    )
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")
    linkedin_link = models.CharField(
        max_length=200, null=True, blank=True, verbose_name="لینک لینکدین"
    )
    insta_link = models.CharField(
        max_length=200, null=True, blank=True, verbose_name="لینک اینستا"
    )
    telegram_link = models.CharField(
        max_length=200, null=True, blank=True, verbose_name="لینک تلگرام "
    )
    file_upload_2 = File_Uploader("images", "stylists")
    profile_image = models.ImageField(
        upload_to=file_upload_2.upload_to,
        blank=True,
        null=True,
        verbose_name="تصویر پروفایل",
    )
    address = models.TextField(null=True, blank=True, verbose_name="آدرس")
    is_active = models.BooleanField(default=False, verbose_name="وضعیت")
    expert = models.CharField(max_length=100, verbose_name="تخصص", null=True)
    calendar_color = models.CharField(
        max_length=10, verbose_name="رنگ تقویم ", null=True, blank=True
    )

    def __str__(self):
        return f"{self.user.name} {self.user.family}"

    def get_average_score(self):
        avg_score = self.scoring_stylist.all().aggregate(Avg("score"))["score__avg"]
        if avg_score is None:
            avg_score = 0
        return avg_score

    def get_price_for_service(self, service):
        price_record = self.stylist_prices.filter(service=service).first()
        return price_record.price if price_record else None

    def get_discount_for_service(self, service):
        """
        دریافت تخفیف برای خدمت خاص از سبد تخفیف
        """
        current_time = timezone.now()
        try:
            discount_basket_detail = self.discount_basket_details3.filter(
                service=service,
                discount_basket__is_active=True,
                discount_basket__start_date__lte=current_time,
                discount_basket__end_date__gte=current_time,
            ).first()

            # اگر تخفیفی وجود داشته باشد
            if discount_basket_detail:
                return discount_basket_detail.discount_basket.discount
            else:
                return 0
        except self.discount_basket_details3.model.DoesNotExist:
            return 0

    def get_price_by_discount(self, service):
        """
        محاسبه قیمت با تخفیف برای خدمت خاص
        """
        # بررسی اینکه آیا آرایشگر قیمتی برای خدمت دارد
        service_price = self.get_price_for_service(service)
        if not service_price:
            return 0  # اگر قیمت خدمت وجود ندارد، صفر برمی‌گرداند

        # گرفتن تخفیف
        discount = self.get_discount_for_service(service)

        # محاسبه قیمت نهایی با تخفیف
        final_price = service_price - (service_price * discount / 100)
        return final_price

    def get_fullName(self):
        fullName = self.user.name + " " + self.user.family
        return fullName

    class Meta:
        verbose_name = "آرایشگر"
        verbose_name_plural = "آرایشگران"
        db_table = "a_stylists"

# ----------------------------------------------------------------------------
# Salon Manager
class SalonManager(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        primary_key=True,
        verbose_name="کاربر",
        related_name="salon_manager_profile",
    )
    address = models.TextField(null=True, blank=True, verbose_name="آدرس")
    file_upload = File_Uploader("images", "salon_manager")
    profile_image = models.ImageField(
        upload_to=file_upload.upload_to,
        blank=True,
        null=True,
        verbose_name="تصویر پروفایل",
    )
    salon_number = models.IntegerField(null=True, blank=True, verbose_name="تلفن سالن")
    is_active = models.BooleanField(default=False, verbose_name="وضعیت")
    slug = models.SlugField(null=True, blank=True, verbose_name="اسلاگ")

    def __str__(self):
        return f"{self.user.name} {self.user.family}"

    class Meta:
        verbose_name = "مدیر سالن"
        verbose_name_plural = "مدیران سالن ها"
        db_table = "A_Salon_Managers"

# ----------------------------------------------------------------------------
# work_sampels
class WorkSamples(models.Model):
    stylist = models.ForeignKey(
        Stylist,
        on_delete=models.CASCADE,
        verbose_name="آرایشگر",
        related_name="work_samples_of_stylist",
        null=True,
    )
    service = models.ForeignKey(
        "services.Services",
        on_delete=models.CASCADE,
        verbose_name="خدمت ",
        related_name="work_samples_services",
        null=True,
    )
    file_upload = File_Uploader("images", "work_samples")
    sample_image = models.ImageField(
        upload_to=file_upload.upload_to, verbose_name="تصویر نمونه کار"
    )
    description = models.TextField(verbose_name="توضیحات", null=True, blank=True)
    like_count = models.PositiveIntegerField(default=0, verbose_name="تعداد لایک")
    is_active = models.BooleanField(default=False, verbose_name="وضعیت")

    def __str__(self):
        return self.description

    class Meta:
        verbose_name = "نمونه کار"
        verbose_name_plural = "نمونه کار ها"
        db_table = "A_Work_Samples"

# -------------------------------------------------------------------------------------------
