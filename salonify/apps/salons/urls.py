from django.urls import path

from .views import (
    DetailSalonView,
    ShowSalonsView,
)

# -------------------------------------------------------------------
app_name = "salons"
urlpatterns = [
    path("", ShowSalonsView.as_view(), name="show_salons"),
    path("detail_salon/<int:salon_id>/", DetailSalonView.as_view(), name="detail_salon"),
]
