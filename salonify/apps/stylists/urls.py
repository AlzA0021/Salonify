from django.urls import path

from .views import stylist_services_api

# -----------------------------------------------------------------------------
app_name = "stylists"
urlpatterns = [
    path("api/stylist/<int:stylist_id>/", stylist_services_api, name="stylist_services_api"),
]
