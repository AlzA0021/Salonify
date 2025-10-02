from django.urls import path

from .views import (
    # IndexServiceGroupsView,
    # ServicesView,
    categories,
    service_dynamic_content,
    get_service_priceList,
    get_subgroups,
    get_service_of_subgroups,
    get_service_of_sorting,
)

# --------------------------------------------------------------------------------
app_name = "services"
urlpatterns = [
    # path(
    #     "show_services_group/",
    #     IndexServiceGroupsView.as_view(),
    #     name="show_services_group",
    # ),
    # path("all_services/", ServicesView.as_view(), name="all_services"),
    # path(
    #     "group_services/<int:group_id>/",
    #     ServicesView.as_view(),
    #     name="group_services",
    # ),
    path("categories/", categories, name="categories"),
    path("dynamic-content/", service_dynamic_content, name="service_dynamic_content"),
    path(
        "service_card_priceList/<int:service_id>/",
        get_service_priceList,
        name="service_priceList",
    ),
    path(
        "get_subgroups/<int:group_id>/",
        get_subgroups,
        name="get_subgroups",
    ),
    path(
        "get_service_of_subgroups/<int:subgroup_id>/",
        get_service_of_subgroups,
        name="get_service_of_subgroups",
    ),
    path(
        "get_service_of_sorting/<int:subgroup_id>/<int:sort_type>/",
        get_service_of_sorting,
        name="get_service_of_sorting",
    ),
]
