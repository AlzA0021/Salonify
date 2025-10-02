from django.urls import path
from .views import (
    # OrderCartView,
    # add_to_order_cart,
    # delete_from_order_cart,
    # show_order_cart,
    # show_update_order_cart,
    # show_update_salon_stylist_order,
    # update_salon_stylist_order,
    # show_update_callendar,
    # update_callendar,
    # status_of_order_cart,
    # CreateOrderView,
    # CheckOutOrderView,
    # ApplyCoupon,
    BookingStylistSelect,
    BookingDateTimeSelect,
    ReservationDetailView,
    AppointmentsView,
    AppointmentDetailView,
)

# ------------------------------------------------------------------------------------
app_name = "orders"
urlpatterns = [
    # path("order_cart/", OrderCartView.as_view(), name="order_cart"),
    # path("add_to_order_cart/", add_to_order_cart, name="add_to_order_cart"),
    # path("delete_from_order_cart/", delete_from_order_cart, name="delete_from_order_cart"),
    # path("show_order_cart/", show_order_cart, name="show_order_cart"),
    # path("show_update_order_cart/", show_update_order_cart, name="show_update_order_cart"),
    # path(
    #     "show_update_salon_stylist_order/",
    #     show_update_salon_stylist_order,
    #     name="show_update_salon_stylist_order",
    # ),
    # path(
    #     "update_salon_stylist_order/",
    #     update_salon_stylist_order,
    #     name="update_salon_stylist_order",
    # ),
    # path("show_update_callendar/", show_update_callendar, name="show_update_callendar"),
    # path("update_callendar/", update_callendar, name="update_callendar"),
    # path("status_of_order_cart/", status_of_order_cart, name="status_of_order_cart"),
    # path("create_order/", CreateOrderView.as_view(), name="create_order"),
    # path("check_out/<int:order_id>/", CheckOutOrderView.as_view(), name="check_out"),
    # path("apply_coupon/<int:order_id>", ApplyCoupon.as_view(), name="apply_coupon"),
    path("select_stylists/", BookingStylistSelect.as_view(), name="select_stylists"),
    path("select_dateTime/", BookingDateTimeSelect.as_view(), name="select_dateTime"),
    path(
        "reservation_detail/<int:order_id>/",
        ReservationDetailView.as_view(),
        name="reservation_detail",
    ),
    path(
        "reservation_preview/",
        ReservationDetailView.as_view(),
        name="reservation_preview",
    ),
    path(
        "appointments/",
        AppointmentsView.as_view(),
        name="appointments",
    ),
    path(
        "appointment_detail/<int:order_id>/",
        AppointmentDetailView.as_view(),
        name="appointment_detail",
    ),
    
]
