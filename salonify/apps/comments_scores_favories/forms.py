from django import forms

from apps.accounts.models import Stylist
from apps.services.models import Services

from .models import Comments, Scoring


# ---------------------------------------------------------------------------------
class CommentsForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ["comment_text"]
        widgets = {
            "comment_text": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "نظر خود را بنویسید...",
                }
            ),
        }
        labels = {
            "comment_text": "نظر",
        }


# ---------------------------------------------------------------------------------
class ScoringForm(forms.ModelForm):
    class Meta:
        model = Scoring
        fields = ["score"]
        widgets = {
            "score": forms.RadioSelect(
                attrs={"class": "rating-input"},
                choices=[(1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5")],
            ),
        }
        labels = {
            "score": "امتیاز",
        }


# ---------------------------------------------------------------------------------
class CommentScoringForm(forms.Form):
    comment_text = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "دیدگاه خود را بنویسید...",
            }
        ),
        required=False,
        label="دیدگاه",
    )
    score = forms.IntegerField(
        widget=forms.RadioSelect(
            attrs={"class": "rating-input"},
            choices=[(1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5")],
        ),
        label="امتیاز",
    )
    stylist = forms.ModelChoiceField(
        queryset=Stylist.objects.none(),
        required=False,
        label="آرایشگر",
        widget=forms.Select(attrs={"class": "form-control", "id": "stylist_select"}),
    )
    service = forms.ModelChoiceField(
        queryset=Services.objects.none(),
        required=False,
        label="خدمت",
        widget=forms.Select(attrs={"class": "form-control", "id": "service_select"}),
    )

    def __init__(self, *args, **kwargs):
        salon = kwargs.pop("salon", None)
        super().__init__(*args, **kwargs)
        if salon:
            self.fields["stylist"].queryset = salon.stylists.filter(is_active=True)
            # Initialize service queryset with all active services from the salon's stylists
            self.fields["service"].queryset = Services.objects.filter(
                stylists__in=salon.stylists.filter(is_active=True), is_active=True
            ).distinct()


# ---------------------------------------------------------------------------------
