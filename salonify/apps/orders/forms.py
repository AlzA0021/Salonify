from django import forms

from .models import PaymentType


class OrderForm(forms.Form):
    payment_type = forms.ChoiceField(
        label="",
        choices=[],
        widget=forms.RadioSelect(),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["payment_type"].choices = [
            (item.pk, item.payment_title) for item in PaymentType.objects.all()
        ]
