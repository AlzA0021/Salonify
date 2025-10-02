from django import forms

class WalletChargeForm(forms.Form):
    amount = forms.DecimalField(
        label="مبلغ شارژ (تومان)",
        min_value=10000,  # حداقل مبلغ شارژ
        max_digits=10,
        decimal_places=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مبلغ را وارد کنید'})
    )