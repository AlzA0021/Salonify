import datetime
from datetime import datetime
import re
from io import BytesIO
import khayyam
from django import forms
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image
from apps.accounts.models import CustomUser, Stylist, WorkSamples
from apps.salons.models import Salon
from apps.services.models import Services
from .models import EmergencyInfo, JobDetails, StylistSchedule, StylistTimeOff


# ------------------------------------------------------------------------------
class StylistScheduleForm(forms.ModelForm):
    class Meta:
        model = StylistSchedule
        fields = ["salon", "date", "service", "start_time", "end_time"]

        widgets = {
            "salon": forms.Select(attrs={"class": "form-control"}),
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "service": forms.Select(attrs={"class": "form-control"}),
            "start_time": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "end_time": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
        }

    def __init__(self, *args, **kwargs):
        stylist = kwargs.pop("stylist", None)
        super().__init__(*args, **kwargs)

        # فیلتر کردن سالن‌ها بر اساس آرایشگر
        if stylist:
            self.fields["salon"].queryset = Salon.objects.filter(stylists=stylist)
            self.fields["service"].queryset = Services.objects.filter(stylists=stylist)

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        if start_time and end_time and start_time >= end_time:
            raise ValidationError("زمان پایان باید بعد از زمان شروع باشد.")

        return cleaned_data

    def save(self, commit=True, stylist=None):
        schedule_instance = super().save(commit=False)

        # تنظیم مقدار آرایشگر
        if stylist:
            schedule_instance.stylist = stylist

        # بررسی برنامه مشابه
        if StylistSchedule.objects.filter(
            stylist=schedule_instance.stylist,
            date=schedule_instance.date,
            start_time=schedule_instance.start_time,
            service=schedule_instance.service,
        ).exists():
            raise ValidationError("برنامه مشابهی از قبل وجود دارد.")

        if commit:
            schedule_instance.save()

        return schedule_instance


# --------------------------------------------------------------------------------------
class StylistTimeOffForm(forms.ModelForm):
    TIME_OFF_TYPES = [
        ("", "انتخاب نوع"),
        (" مرخصی سالانه", "مرخصی سالانه"),
        (" مرخصی استعلاجی ", "مرخصی استعلاجی"),
        (" مرخصی بدون حقوق ", "مرخصی بدون حقوق"),
        (" سایر موارد ", "سایر موارد"),
    ]
    reason_choice = forms.ChoiceField(choices=TIME_OFF_TYPES, required=True, label="نوع")

    # ✅ 1. فیلدها را به صورت صریح به عنوان ChoiceField تعریف می‌کنیم
    start_time = forms.ChoiceField(choices=[], required=False, label="ساعت شروع")
    end_time = forms.ChoiceField(choices=[], required=False, label="ساعت پایان")

    class Meta:
        model = StylistTimeOff
        # ✅ 2. فقط فیلدهایی را نگه می‌داریم که توسط ModelForm مدیریت شوند
        fields = ["stylist", "date"]
        widgets = {
            "stylist": forms.HiddenInput(),
            "date": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        time_options = kwargs.pop("time_options", [])
        super().__init__(*args, **kwargs)

        # ✅ 3. گزینه‌ها را برای فیلدهای صریح خودمان تنظیم می‌کنیم
        choices = [("", "--")] + [(opt, opt) for opt in time_options]
        self.fields["start_time"].choices = choices
        self.fields["end_time"].choices = choices

    # ✅ 4. چون از ChoiceField استفاده کردیم، خروجی آن یک رشته است.
    # باید آن را به فرمت time برای ذخیره در دیتابیس تبدیل کنیم.
    def clean_start_time(self):
        time_str = self.cleaned_data.get("start_time")
        if time_str:
            return datetime.strptime(time_str, "%H:%M").time()
        return None

    def clean_end_time(self):
        time_str = self.cleaned_data.get("end_time")
        if time_str:
            return datetime.strptime(time_str, "%H:%M").time()
        return None

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.reason = self.cleaned_data.get("reason_choice")

        # ✅ 5. مقادیر تبدیل شده را به نمونه مدل اختصاص می‌دهیم
        instance.start_time = self.cleaned_data.get("start_time")
        instance.end_time = self.cleaned_data.get("end_time")

        if commit:
            instance.save()
        return instance


# ---------------------------------------------------------------------------------------------------------
class WorkSamplesForm(forms.ModelForm):
    class Meta:

        model = WorkSamples
        fields = ["service", "sample_image", "description"]

        Widgets = {
            "service": forms.Select(attrs={"class": "form-control"}),
            "sample_image": forms.FileInput(attrs={"class": "form-control", "type": "image"}),
            "description": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        stylist = kwargs.pop("stylist", None)
        super().__init__(*args, **kwargs)

        # فیلتر کردن خدمات مرتبط با آرایشگر
        if stylist:
            self.fields["service"].queryset = Services.objects.filter(stylists=stylist)

    def clean(self):
        cleaned_data = super().clean()
        # service = cleaned_data.get("service")
        sample_image = cleaned_data.get("sample_image")
        # description = cleaned_data.get("description")

        # Check if the sample image is provided
        if sample_image is None:
            raise ValidationError("Please upload a sample image.")

        max_size_kb = 2048
        if sample_image.size > max_size_kb * 1024:
            raise ValidationError("Image size must not exceed 2 MB.")

        valid_formats = ["jpeg", "jpg", "png"]
        if sample_image.content_type.split("/")[1] not in valid_formats:
            raise ValidationError("Image format must be JPG or PNG.")

        img = Image.open(sample_image)
        max_width = 1920
        max_height = 1080
        if img.width > max_width or img.height > max_height:
            raise ValidationError(
                f"Image dimensions must not exceed {max_width}x{max_height} pixels."
            )

        return cleaned_data

    def save(self, commit=True, stylist=None):
        sample_instance = super().save(commit=False)

        # فشرده‌سازی تصویر در صورت نیاز
        if self.cleaned_data.get("sample_image"):
            img = Image.open(self.cleaned_data["sample_image"])
            output = BytesIO()
            img = img.convert("RGB")  # تبدیل تصویر به RGB برای فرمت JPEG
            img.save(output, format="JPEG", quality=85)  # فشرده‌سازی تصویر با کیفیت 85
            output.seek(0)
            sample_instance.sample_image = InMemoryUploadedFile(
                output,
                "ImageField",
                self.cleaned_data["sample_image"].name,
                "image/jpeg",
                output.getbuffer().nbytes,
                None,
            )

        if stylist:
            sample_instance.stylist = stylist

        if commit:
            sample_instance.save()

        return sample_instance

    # -----------------------------------------------------------------------------------------------------------

    COMMISSION_TYPES = [
        ("", "انتخاب کنید"),
        ("fixed", "نرخ ثابت"),
        ("percentage", "درصدی"),
        ("none", "بدون کمیسیون"),
    ]

    service_commission_active = forms.BooleanField(required=False)
    service_commission_type = forms.ChoiceField(choices=COMMISSION_TYPES, required=False)
    service_commission_rate = forms.FloatField(required=False, min_value=0, max_value=100)

    product_commission_active = forms.BooleanField(required=False)
    membership_commission_active = forms.BooleanField(required=False)
    gift_card_commission_active = forms.BooleanField(required=False)
    cancellation_commission_active = forms.BooleanField(required=False)

    # Custom settings
    custom_settings_enabled = forms.BooleanField(required=False)
    deduct_discounts = forms.BooleanField(required=False)
    deduct_taxes = forms.BooleanField(required=False)
    deduct_service_cost = forms.BooleanField(required=False)
    earn_membership_commission = forms.BooleanField(required=False)
    earn_on_paid_invoices = forms.BooleanField(required=False)


# -------------------------------------------------------------------------------------------------------------------
class StylistUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["name", "family", "email", "mobile_number"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "نام"}),
            "family": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "نام خانوادگی"}
            ),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "ایمیل"}),
            "mobile_number": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "شماره تلفن"}
            ),
        }


# -------------------------------------------------------------------------------------------------------------------
class StylistProfileForm(forms.ModelForm):
    class Meta:
        model = Stylist
        fields = ["expert", "calendar_color", "profile_image"]
        widgets = {
            "expert": forms.TextInput(attrs={"class": "form-control", "placeholder": "تخصص"}),
            "calendar_color": forms.HiddenInput(),
            "profile_image": forms.ClearableFileInput(
                attrs={"class": "form-control", "accept": "image/*"}
            ),
        }


# -------------------------------------------------------------------------------------------------------------------
class JobDetailsForm(forms.ModelForm):
    class Meta:
        model = JobDetails
        fields = ["start_date", "end_date", "employment_type"]
        widgets = {
            "start_date": forms.TextInput(
                attrs={
                    "class": "form-control datepicker",
                    "placeholder": "روز و ماه",
                    "autocomplete": "off",
                }
            ),
            "end_date": forms.TextInput(
                attrs={
                    "class": "form-control datepicker",
                    "placeholder": "روز و ماه",
                    "autocomplete": "off",
                }
            ),
            "employment_type": forms.Select(
                attrs={"class": "form-control"},
                choices=[
                    ("", "یک گزینه را انتخاب کنید"),
                    ("full_time", "تمام وقت"),
                    ("part_time", "پاره وقت"),
                    ("contract", "قراردادی"),
                    ("project", "پروژه‌ای"),
                ],
            ),
        }

    def persian_to_english_numbers(self, text):
        """تبدیل اعداد فارسی به انگلیسی"""
        if not text:
            return text
        persian_digits = "۰۱۲۳۴۵۶۷۸۹"
        english_digits = "0123456789"

        for persian, english in zip(persian_digits, english_digits):
            text = text.replace(persian, english)
        return text

    def parse_jalali_date(self, date_str):
        """تبدیل تاریخ شمسی به میلادی با استفاده از khayyam"""
        if not date_str:
            return None

        try:
            # تبدیل اعداد فارسی به انگلیسی
            clean_date = self.persian_to_english_numbers(date_str.strip())

            # پیدا کردن الگوهای مختلف تاریخ
            patterns = [
                r"(\d{4})[/-](\d{1,2})[/-](\d{1,2})",  # YYYY/MM/DD یا YYYY-MM-DD
                r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})",  # DD/MM/YYYY یا DD-MM-YYYY
            ]

            year, month, day = None, None, None

            for pattern in patterns:
                match = re.match(pattern, clean_date)
                if match:
                    if len(match.group(1)) == 4:  # اول سال است
                        year, month, day = (
                            int(match.group(1)),
                            int(match.group(2)),
                            int(match.group(3)),
                        )
                    else:  # اول روز است
                        day, month, year = (
                            int(match.group(1)),
                            int(match.group(2)),
                            int(match.group(3)),
                        )
                    break

            if not all([year, month, day]):
                raise ValueError(f"فرمت تاریخ نامعتبر: {date_str}")

            # اعتبارسنجی مقادیر تاریخ
            if year is None or year < 1300 or year > 1500:
                raise ValueError(f"سال نامعتبر: {year}")
            if month is None or month < 1 or month > 12:
                raise ValueError(f"ماه نامعتبر: {month}")
            if day is None or day < 1 or day > 31:
                raise ValueError(f"روز نامعتبر: {day}")

            # تبدیل به تاریخ شمسی با khayyam
            if year is None or month is None or day is None:
                raise ValueError(f"فرمت تاریخ نامعتبر: {date_str}")
            jalali_date = khayyam.JalaliDate(year, month, day)

            # تبدیل به تاریخ میلادی
            gregorian_date = jalali_date.todate()

            return gregorian_date

        except ValueError as ve:
            raise ValidationError(f"خطا در تاریخ: {str(ve)}")
        except Exception as e:
            raise ValidationError(f"خطا در تبدیل تاریخ {date_str}: {str(e)}")

    def clean_start_date(self):
        start_date = self.cleaned_data.get("start_date")
        if start_date:
            # اگر قبلاً تبدیل شده باشد، همان را برگردان
            if isinstance(start_date, datetime.date):
                return start_date
            return self.parse_jalali_date(start_date)
        return start_date

    def clean_end_date(self):
        end_date = self.cleaned_data.get("end_date")
        if end_date:
            # اگر قبلاً تبدیل شده باشد، همان را برگردان
            if isinstance(end_date, datetime.date):
                return end_date
            return self.parse_jalali_date(end_date)
        return end_date

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        # بررسی منطقی بودن تاریخ‌ها
        if start_date and end_date:
            if start_date > end_date:
                raise ValidationError("تاریخ پایان کار نمی‌تواند قبل از تاریخ شروع کار باشد.")

        # بررسی اینکه تاریخ شروع در آینده نباشد (اختیاری)
        if start_date:
            today = datetime.datetime.now().date()
            if start_date > today:
                # هشدار اما مانع ذخیره نشود
                pass

        return cleaned_data


# -------------------------------------------------------------------------------------------------------------------
class EmergencyInfoForm(forms.ModelForm):
    emergency_contact_name = forms.CharField(
        label="نام",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    emergency_contact_family = forms.CharField(
        label="نام خانوادگی",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    emergency_phone_prefix = forms.ChoiceField(
        label="پیش شماره",
        required=False,
        choices=[("+98", "+98"), ("+1", "+1"), ("+44", "+44")],
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    emergency_phone = forms.CharField(
        label="شماره تلفن",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = EmergencyInfo
        fields = ["relationship"]
        widgets = {
            "relationship": forms.Select(
                attrs={"class": "form-control"},
                choices=[
                    ("", "انتخاب کنید"),
                    ("spouse", "همسر"),
                    ("parents", "والدین"),
                    ("child", "فرزند"),
                    ("friend", "دوست"),
                    ("other", "سایر"),
                ],
            ),
        }


# -------------------------------------------------------------------------------------------------------------------
