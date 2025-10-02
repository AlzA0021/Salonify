from django import forms


class SupportForm(forms.Form):
    email = forms.EmailField(
        label="ایمیل",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "اگر حساب فرشا دارید، آدرس ایمیلی که با آن وارد می‌شوید را وارد کنید",
            }
        ),
    )

    REASON_CHOICES = [
        ("", "لطفاً انتخاب کنید"),
        ("account", "مشکل در حساب کاربری"),
        ("payment", "مشکل در پرداخت"),
        ("booking", "مشکل در رزرو"),
        ("technical", "مشکل فنی"),
        ("other", "سایر"),
    ]

    reason = forms.ChoiceField(
        label="دلیل تماس با پشتیبانی",
        choices=REASON_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    description = forms.CharField(
        label="توضیح دهید به چه کمک نیاز دارید",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 5,
                "maxlength": 2000,
                "placeholder": "مشکل خود را به طور دقیق شرح دهید",
            }
        ),
    )
