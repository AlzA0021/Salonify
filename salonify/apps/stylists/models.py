from django.db import models
from django.utils import timezone

from apps.salons.models import Salon
from apps.services.models import Services


# --------------------------------------------------------------------------------------------------------------------------------
class StylistSchedule(models.Model):
    stylist = models.ForeignKey(
        "accounts.Stylist",
        on_delete=models.CASCADE,
        related_name="stylist_schedules",
        verbose_name="آرایشگر",
    )
    salon = models.ForeignKey(
        Salon,
        on_delete=models.CASCADE,
        related_name="salon_schedules",
        verbose_name="سالن",
    )
    date = models.DateField(verbose_name="تاریخ ")
    service = models.ForeignKey(
        Services,
        on_delete=models.CASCADE,
        related_name="service_schedules",
        verbose_name="خدمت",
        null=True,
        blank=True,
    )
    start_time = models.TimeField(verbose_name="زمان شروع")
    end_time = models.TimeField(verbose_name="زمان پایان")

    class Meta:
        verbose_name = "برنامه آرایشگر"
        verbose_name_plural = "برنامه‌های آرایشگران"
        unique_together = ("stylist", "date", "start_time")

    def __str__(self):
        return (
            f"{self.stylist} - {self.salon} - {self.service} - {self.start_time}-{self.end_time}"
        )


# -----------------------------------------------------------------------------------------------------------------------------------
class StylistTimeOff(models.Model):
    stylist = models.ForeignKey(
        "accounts.Stylist",
        on_delete=models.CASCADE,
        related_name="time_offs",
        verbose_name="آرایشگر",
    )
    date = models.DateField(verbose_name="تاریخ تعطیلی")
    start_time = models.TimeField(null=True, blank=True, verbose_name="زمان شروع تعطیلی")
    end_time = models.TimeField(null=True, blank=True, verbose_name="زمان پایان تعطیلی")
    reason = models.CharField(max_length=255, null=True, blank=True, verbose_name="دلیل")

    class Meta:
        verbose_name = "تعطیلی آرایشگر"
        verbose_name_plural = "تعطیلی‌های آرایشگر"
        unique_together = ("stylist", "date", "start_time")

    def __str__(self):
        if self.start_time and self.end_time:
            return (
                f"{self.stylist} - تعطیلی در {self.date} از {self.start_time} تا {self.end_time}"
            )
        else:
            return f"{self.stylist} - تعطیلی در تاریخ {self.date}"


# --------------------------------------------------------------------------------------------------------------------------------
class JobDetails(models.Model):
    stylist = models.ForeignKey(
        "accounts.Stylist",
        on_delete=models.CASCADE,
        related_name="job_details",
        verbose_name="آرایشگر",
    )
    salon = models.ForeignKey(
        Salon,
        on_delete=models.CASCADE,
        related_name="salon_job_details",
        verbose_name="سالن",
    )
    start_date = models.DateField(default=timezone.now, verbose_name="تاریخ شروع")
    end_date = models.DateField(verbose_name="تاریخ پایان", null=True, blank=True)
    employment_type = models.CharField(
        max_length=255, verbose_name="نوع استخدام", null=True, blank=True
    )

    class Meta:
        verbose_name = "جزئیات شغلی"
        verbose_name_plural = "جزئیات شغلی"

    def __str__(self):
        return f"{self.stylist} - {self.salon} "


# --------------------------------------------------------------------------------------------------------------------------------
class EmergencyInfo(models.Model):
    stylist = models.ForeignKey(
        "accounts.Stylist",
        on_delete=models.CASCADE,
        related_name="emergency_info",
        verbose_name="آرایشگر",
    )
    emergency_contact = models.CharField(max_length=255, verbose_name="شماره تماس اضطراری")
    relationship = models.CharField(max_length=255, verbose_name="نسبت با آرایشگر")
    full_name = models.CharField(
        max_length=255, verbose_name="نام و نام خانوادگی  ", null=True, blank=True
    )

    class Meta:
        verbose_name = "اطلاعات اضطراری"
        verbose_name_plural = "اطلاعات اضطراری"

    def __str__(self):
        return f"{self.stylist}  - {self.emergency_contact}"


# ---------------------------------------------------------------------------------------------------------------------------------
# class RegularShift(models.Model):
#     stylist = models.ForeignKey(
#         "accounts.Stylist",
#         on_delete=models.CASCADE,
#         related_name="regular_shift",
#         verbose_name="آرایشگر",
#     )
#     salon = models.ForeignKey(
#         Salon,
#         on_delete=models.CASCADE,
#         related_name="salon_regular_shift",
#         verbose_name="سالن",
#     )
#     schedule_type = models.CharField(max_length=200,verbose_name="نوع شیفت")
#     start_date = models.DateField(verbose_name="تاریخ شروع")
#     end_date = models.DateField(verbose_name="تاریخ پایان")
