from django.urls import path

from .views import (
    salon_search,
    SearchPageView,
    salon_list,
    FilterSalonView,
    salonify_search,
    customers_search,
    FilterCustomersView,
)

# ---------------------------------------------------------------------------------------
app_name = "search"
urlpatterns = [
    path("salon_search/", salon_search, name="salon_search"),
    path("search/", SearchPageView.as_view(), name="search_page"),
    path("salon_list", salon_list, name="salon_list"),
    path("filter_salon/", FilterSalonView.as_view(), name="filter_salon"),
    path("salonify_search/", salonify_search, name="salonify_search"),
    path("customers_search/", customers_search, name="customers_search"),
    path("filter_customers/", FilterCustomersView.as_view(), name="filter_customers"),
]
