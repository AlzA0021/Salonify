from django.urls import path

from .views import (
    RegisterUserView,
    VerifyRegisterView,
    LoginUserView,
    LogoutUserView,
    ChangePasswordView,
    RememberPasswordView,
    CustomerUpdateProfileView,
    CustomerPanelPageView,
    CustomerProfilePageView,
    customer_update_profile_image,
    add_customer,
    DetailCustomerView,
    delete_customer_note,
    CustomerSettingsView,
)

# ----------------------------------------------------------------
app_name = "accounts"
urlpatterns = [
    path("register/", RegisterUserView.as_view(), name="register"),
    path("verify/", VerifyRegisterView.as_view(), name="verify"),
    path("login/", LoginUserView.as_view(), name="login"),
    path("logout/", LogoutUserView.as_view(), name="logout"),
    path("change_password/", ChangePasswordView.as_view(), name="change_password"),
    path("remember_password/", RememberPasswordView.as_view(), name="remember_password"),
    path(
        "customerUpdateProfile",
        CustomerUpdateProfileView.as_view(),
        name="customer_update_profile",
    ),
    path("customerPanel", CustomerPanelPageView.as_view(), name="customer_panel"),
    path("customerProfile", CustomerProfilePageView.as_view(), name="customerProfile"),
    path(
        "update-profile-image/",
        customer_update_profile_image,
        name="customer_update_profile_image",
    ),
    path("add_customer/<int:salon_id>/", add_customer, name="add_customer"),
    path(
        "detail_customer/<int:customer_id>/", DetailCustomerView.as_view(), name="detail_customer"
    ),
    path(
        "customer/<int:customer_id>/note/<int:note_id>/delete/",
        delete_customer_note,
        name="delete_customer_note",
    ),
    path("customer_settings/", CustomerSettingsView.as_view(),name="customer_settings"),
]
