from django import forms
from apps.salons.models import Salon, SalonsGallery, SupplementaryInfoView


# -----------------------------------------------------------------
class SalonProfileStep1Form(forms.ModelForm):
    class Meta:
        model = Salon
        fields = ["salon_name", "phone_number"]
        widgets = {
            "salon_name": forms.TextInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
        }


# -----------------------------------------------------------------
class SalonProfileStep2Form(forms.ModelForm):
    latitude = forms.FloatField(widget=forms.HiddenInput())
    longitude = forms.FloatField(widget=forms.HiddenInput())

    class Meta:
        model = Salon
        fields = ["zone", "neighborhood", "address", "latitude", "longitude"]
        widgets = {
            "zone": forms.NumberInput(attrs={"class": "form-control"}),
            "neighborhood": forms.Select(attrs={"class": "form-control"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }


# -----------------------------------------------------------------
class SalonOpeningHoursForm(forms.Form):
    days = [
        (1, "شنبه"),
        (2, "یکشنبه"),
        (3, "دوشنبه"),
        (4, "سه‌شنبه"),
        (5, "چهارشنبه"),
        (6, "پنج‌شنبه"),
        (7, "جمعه"),
    ]

    # برای هر روز هفته فیلدهای مجزا تعریف می‌کنیم
    day_1_active = forms.BooleanField(required=False, initial=True, label="شنبه")
    day_1_open_time = forms.TimeField(
        required=False, widget=forms.TimeInput(attrs={"type": "time"}), initial="10:00"
    )
    day_1_close_time = forms.TimeField(
        required=False, widget=forms.TimeInput(attrs={"type": "time"}), initial="19:00"
    )

    day_2_active = forms.BooleanField(required=False, initial=True, label="یکشنبه")
    day_2_open_time = forms.TimeField(
        required=False, widget=forms.TimeInput(attrs={"type": "time"}), initial="10:00"
    )
    day_2_close_time = forms.TimeField(
        required=False, widget=forms.TimeInput(attrs={"type": "time"}), initial="19:00"
    )

    day_3_active = forms.BooleanField(required=False, initial=True, label="دوشنبه")
    day_3_open_time = forms.TimeField(
        required=False, widget=forms.TimeInput(attrs={"type": "time"}), initial="10:00"
    )
    day_3_close_time = forms.TimeField(
        required=False, widget=forms.TimeInput(attrs={"type": "time"}), initial="19:00"
    )

    day_4_active = forms.BooleanField(required=False, initial=True, label="سه‌شنبه")
    day_4_open_time = forms.TimeField(
        required=False, widget=forms.TimeInput(attrs={"type": "time"}), initial="10:00"
    )
    day_4_close_time = forms.TimeField(
        required=False, widget=forms.TimeInput(attrs={"type": "time"}), initial="19:00"
    )

    day_5_active = forms.BooleanField(required=False, initial=True, label="چهارشنبه")
    day_5_open_time = forms.TimeField(
        required=False, widget=forms.TimeInput(attrs={"type": "time"}), initial="10:00"
    )
    day_5_close_time = forms.TimeField(
        required=False, widget=forms.TimeInput(attrs={"type": "time"}), initial="19:00"
    )

    day_6_active = forms.BooleanField(required=False, initial=True, label="پنج‌شنبه")
    day_6_open_time = forms.TimeField(
        required=False, widget=forms.TimeInput(attrs={"type": "time"}), initial="10:00"
    )
    day_6_close_time = forms.TimeField(
        required=False, widget=forms.TimeInput(attrs={"type": "time"}), initial="19:00"
    )

    day_7_active = forms.BooleanField(required=False, initial=False, label="جمعه")
    day_7_open_time = forms.TimeField(
        required=False, widget=forms.TimeInput(attrs={"type": "time"}), initial="10:00"
    )
    day_7_close_time = forms.TimeField(
        required=False, widget=forms.TimeInput(attrs={"type": "time"}), initial="17:00"
    )


# -----------------------------------------------------------------
class SalonsGalleryForm(forms.ModelForm):
    class Meta:
        model = SalonsGallery
        fields = ["salon_image"]
        labels = {
            "salon_image": "تصویر سالن",
        }
        widgets = {
            "salon": forms.Select(attrs={"class": "form-control"}),
            "salon_image": forms.FileInput(attrs={"class": "form-control"}),
        }

    # def __init__(self, *args, **kwargs):
    #     super(SalonsGalleryForm, self).__init__(*args, **kwargs)
    #     # اگر نیاز به سفارشی‌سازی بیشتر است، می‌توانید اینجا اضافه کنید
    #     # مثال: محدود کردن سالن‌ها بر اساس کاربر
    #     # self.fields['salon'].queryset = Salon.objects.filter(user=user)


# -----------------------------------------------------------------
class SupplementaryInfoForm(forms.ModelForm):
    class Meta:
        model = SupplementaryInfoView
        fields = ["title", "description", "icon_class", "is_active"]
        widgets = {
            "title": forms.HiddenInput(),
            "icon_class": forms.HiddenInput(),
        }


# --------------------------------------------------------------------
class SalonDescriptionForm(forms.ModelForm):
    description = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "description-input",
                "maxlength": "600",
                "placeholder": "توضیحات سالن خود را وارد کنید...",
            }
        ),
        required=True,
        min_length=200,
        max_length=600,
    )

    class Meta:
        model = Salon
        fields = ["description"]

    def clean_description(self):
        description = self.cleaned_data.get("description", "")
        if not description or len(description) < 200:
            raise forms.ValidationError("توضیحات باید حداقل ۲۰۰ کاراکتر باشد")
        return description
