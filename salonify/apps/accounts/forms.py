from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError


from .models import Customer, CustomUser


# ------------------------------------------------------------------------------------------------------------
# User Creation Form
class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="RePassword", widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ["mobile_number", "name", "family", "email"]

    def clean_password2(self):
        cd = self.cleaned_data
        if cd["password1"] and cd["password2"] and cd["password1"] != cd["password2"]:
            raise ValidationError("رمز عبور و تکرار آن مغایرت دارند ")
        return cd["password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


# -----------------------------------------------------------------------------------------------------------
# User Change Form
class CustomUserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(
        help_text="برای تغییر رمز عبور روی این <a href='../password' >لینک</a> کلیک کنید "
    )

    class Meta:
        model = CustomUser
        fields = [
            "mobile_number",
            "password",
            "name",
            "family",
            "email",
            "is_active",
            "is_admin",
        ]


# -------------------------------------------------------------------------------------------------------------
# Register Form
class RegisterUserForm(forms.ModelForm):
    password1 = forms.CharField(
        label="رمز عبور ",
        widget=forms.PasswordInput(
            attrs={"class": "register-input-group ", "placeholder": ""},
        ),
    )
    password2 = forms.CharField(
        label="تکرار رمز عبور ",
        widget=forms.PasswordInput(
            attrs={"class": "register-input-group ", "placeholder": ""},
        ),
    )
    agree_to_terms = forms.BooleanField(
        label="تمامی شرایط و قوانین سایت را می پذیرم",
        required=True,
        widget=forms.CheckboxInput(
            attrs={
                "class": "register-input-group ",
            }
        ),
    )

    class Meta:
        model = CustomUser
        fields = ["mobile_number"]
        widgets = {
            "mobile_number": forms.TextInput(
                attrs={"class": "register-input-group ", "placeholder": ""}
            ),
        }


# -------------------------------------------------------------------------------------------------------------
# Verify Registration Form
class VerifyRegisterForm(forms.Form):
    active_code = forms.CharField(
        label="کد فعالسازی ",
        error_messages={"required": "این قیلد نمیتواند حالی باشد "},
        widget=forms.TextInput(
            attrs={
                "class": "register-input-group",
                "placeholder": "کد دریافتی را وارد کنید ",
            },
        ),
    )


# ------------------------------------------------------------------------------------------------------------------
# Login Form
class LoginUserForm(forms.Form):
    mobile_number = forms.CharField(
        label="شماره موبایل",
        error_messages={"required": "این قیلد نمیتواند حالی باشد "},
        widget=forms.TextInput(
            attrs={
                "class": "register-input-group",
                "placeholder": "موبایل را وارد کنید ",
            },
        ),
    )
    password = forms.CharField(
        label="رمز عبور ",
        error_messages={"required": "این قیلد نمیتواند حالی باشد "},
        widget=forms.PasswordInput(
            attrs={
                "class": "register-input-group",
                "placeholder": "رمز عبور را وارد کنید ",
            },
        ),
    )


# -------------------------------------------------------------------------------------------------------------------
# فرم تغییر رمز عبور
class ChangePasswordForm(forms.Form):
    password1 = forms.CharField(
        label="رمز عبور ",
        error_messages={"required": "این قیلد نمیتواند حالی باشد "},
        widget=forms.PasswordInput(
            attrs={
                "class": "register-input-group",
                "placeholder": "رمز عبور را وارد کنید ",
            },
        ),
    )
    password2 = forms.CharField(
        label="تکرار رمز عبور",
        error_messages={"required": "این قیلد نمیتواند حالی باشد "},
        widget=forms.PasswordInput(
            attrs={
                "class": "register-input-group",
                "placeholder": "تکرار رمز عبور را وارد کنید ",
            },
        ),
    )

    def clean_password2(self):
        cd = self.cleaned_data
        if cd["password1"] and cd["password2"] and cd["password1"] != cd["password2"]:
            raise ValidationError("رمز عبور و تکرار آن مغایرت دارند ")
        return cd["password2"]


# ------------------------------------------------------------------------------------------------------------------------
# فرم فراموشی رمز عبور
class RememberPasswordForm(forms.Form):
    mobile_number = forms.CharField(
        label="شماره موبایل",
        error_messages={"required": "این قیلد نمیتواند حالی باشد "},
        widget=forms.TextInput(
            attrs={
                "class": "register-input-group",
                "placeholder": "موبایل را وارد کنید ",
            },
        ),
    )


# ------------------------------------------------------------------------------------------------------------------------
# فرم آپدیت پروفایل مشتری
class CustomerUpdateProfileForm(forms.ModelForm):
    address = forms.CharField(
        label="آدرس",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "آدرس خود را وارد کنید "}
        ),
    )
    image = forms.ImageField(label="تصویر پروفایل", required=False)

    class Meta:
        model = CustomUser
        fields = ["name", "family", "email", "mobile_number"]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "نام خود را بنویسید",
                }
            ),
            "family": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "نام خانوادگی خود را بنویسید",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "ایمیل خود را وارد کنید",
                }
            ),
            "mobile_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "موبایل خود را وارد کنید",
                    "readonly": "readonly",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        customer_instance = kwargs.pop("customer_instance", None)
        super().__init__(*args, **kwargs)

        if customer_instance:
            self.fields["address"].initial = customer_instance.address
            self.fields["image"].initial = customer_instance.profile_image

    def save(self, commit=True):
        user_instance = super().save(commit=False)
        customer_instance = Customer.objects.get(user=user_instance)

        # Update customer-specific fields
        customer_instance.address = self.cleaned_data["address"]
        if self.cleaned_data["image"]:
            customer_instance.profile_image = self.cleaned_data["image"]

        if commit:
            user_instance.save()
            customer_instance.save()

        return user_instance


# ----------------------------------------------------------------------------------------------
class AddCustomerForm(forms.ModelForm):

    image = forms.ImageField(label="تصویر پروفایل", required=False)

    class Meta:
        model = CustomUser
        fields = ["name", "family", "email", "mobile_number"]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "نام مشتری را بنویسید",
                }
            ),
            "family": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "نام خانوادگی مشتری را بنویسید",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "ایمیل مشتری را وارد کنید",
                }
            ),
            "mobile_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "موبایل مشتری را وارد کنید",
                }
            ),
        }
