from ckeditor_uploader.fields import RichTextUploadingFormField
from django import forms
from django.core.exceptions import ValidationError

from apps.accounts.models import Stylist

from .models import (
    GroupServices,
    ServicePrice,
    Services,
)
from django.db import transaction

# ---------------------------------------------------------------------------
class StylistServiceForm(forms.ModelForm):
    description = RichTextUploadingFormField(
        config_name="special",
        label="توضیحات",
        required=False
    )
    
    stylists = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple,
        label="آرایشگرهایی که این خدمت را ارائه می‌دهند",
        required=True,
        error_messages={'required': 'لطفاً حداقل یک آرایشگر را برای این خدمت انتخاب کنید.'}
    )

    base_price = forms.IntegerField(
        label="قیمت پایه خدمت (تومان)",
        min_value=0,
        required=True,
        error_messages={'required': 'لطفاً قیمت پایه را وارد کنید.'}
    )

    class Meta:
        model = Services
        fields = [
            "service_name", "summery_description", "description", "service_image",
            "service_group", "duration_minutes", 'stylists', 'base_price'
        ]
        widgets = {
            "service_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "نام خدمت را وارد کنید"}),
            "summery_description": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "توضیحات مختصری از خدمت بنویسید"}),
            "duration_minutes": forms.NumberInput(attrs={"class": "form-control", "placeholder": "مدت زمان به دقیقه"}),
        }

    def __init__(self, *args, **kwargs):
        salon = kwargs.pop("salon", None)
        super().__init__(*args, **kwargs)

        if not salon:
            return

        self.fields['stylists'].queryset = salon.stylists.all().select_related('user')

        for stylist in self.fields['stylists'].queryset:
            field_name = f'price_for_stylist_{stylist.pk}'
            self.fields[field_name] = forms.IntegerField(
                required=False,
                label=f"قیمت برای {stylist.get_fullName()}",
                min_value=0,
                widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'استفاده از قیمت پایه'})
            )

        if self.instance and self.instance.pk:
            # پر کردن فیلد قیمت پایه
            first_price = self.instance.service_prices.first()
            if first_price:
                self.fields['base_price'].initial = first_price.price

            # پر کردن قیمت‌های خاص هر آرایشگر
            for price_obj in self.instance.service_prices.all():
                field_name = f'price_for_stylist_{price_obj.stylist.pk}'
                if field_name in self.fields:
                    self.fields[field_name].initial = price_obj.price

    def clean(self):
        cleaned_data = super().clean()
        
        duplicate_check_qs = Services.objects.filter(
            service_name=cleaned_data.get("service_name"),
            duration_minutes=cleaned_data.get("duration_minutes"),
            services_of_salon__in=[self.initial['salon']] if 'salon' in self.initial else []
        )
        if self.instance and self.instance.pk:
            duplicate_check_qs = duplicate_check_qs.exclude(pk=self.instance.pk)
        if duplicate_check_qs.exists():
            raise ValidationError("خدمت دیگری با این نام و مدت زمان در این سالن از قبل وجود دارد.")
            
        return cleaned_data

    @transaction.atomic
    def save(self, commit=True, salon=None):
        instance = super().save(commit=True)
        
        if salon:
            instance.services_of_salon.add(salon)

        instance.service_prices.all().delete()

        selected_stylists = self.cleaned_data.get("stylists")
        base_price = self.cleaned_data.get("base_price")
        
        prices_to_create = []
        if selected_stylists:
            for stylist in selected_stylists:
                price_field_name = f'price_for_stylist_{stylist.pk}'
                specific_price = self.cleaned_data.get(price_field_name)
                final_price = specific_price if specific_price is not None and specific_price != '' else base_price
                
                prices_to_create.append(
                    ServicePrice(service=instance, stylist=stylist, price=final_price)
                )
        
        if prices_to_create:
            ServicePrice.objects.bulk_create(prices_to_create)
            
        return instance


# ---------------------------------------------------------------------------
