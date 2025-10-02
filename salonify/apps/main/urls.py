from django.urls import path
from .views import SupportView, success_view

# ------------------------------------------------------------------------------
app_name = "main"
urlpatterns = [
    # path("", IndexPage.as_view(), name="index"),
    path("contact/", SupportView.as_view(), name="contact"),
    path("success/", success_view, name="success"),
]
