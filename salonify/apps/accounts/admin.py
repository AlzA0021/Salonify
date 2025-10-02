from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import Customer, CustomUser, SalonManager, Stylist, WorkSamples


# -------------------------------------------------------------------------
# Custom User Admin
class CustomUserAdmin(UserAdmin):
    forms = CustomUserChangeForm
    add_forms = CustomUserCreationForm

    list_display = ["mobile_number", "email", "name", "family"]
    list_filter = ("is_active", "is_admin")
    search_fields = ("name", "family", "mobile_number", "email")
    ordering = ("name", "family")
    filter_horizontal = ("user_permissions", "groups")

    fieldsets = (
        (None, {"fields": ("mobile_number", "password")}),
        ("Personal Info", {"fields": ("name", "family", "email")}),
        (
            "Permissions",
            {"fields": ("is_active", "is_admin", "groups", "user_permissions")},
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "fields": (
                    "mobile_number",
                    "email",
                    "name",
                    "family",
                    "is_active",
                    "is_admin",
                    "password1",
                    "password2",
                )
            },
        ),
    )


admin.site.register(CustomUser, CustomUserAdmin)


# ------------------------------------------------------------------------------------------------------------------------------
# Customer Admin
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("user", "address", "profile_image")


# --------------------------------------------------------------------------------------------------------------------------------
# Stylist Admin
@admin.register(Stylist)
class StylistAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "show_expert",
        "address",
        "profile_image",
    ]
    list_filter = ["is_active", "address"]
    search_fields = ["user", "address"]

    def show_expert(self, obj):
        return " , ".join([service.service_name for service in obj.services_of_stylist.all()])

    show_expert.short_description = "تخصص ها "


# --------------------------------------------------------------------------------------------------------------------------------
# Salon Manager Admin
@admin.register(SalonManager)
class SalonManagerAdmin(admin.ModelAdmin):
    list_display = ["user", "address", "profile_image", "salon_number", "is_active"]
    list_filter = ["is_active", "address"]
    search_fields = ["user", "address"]


# --------------------------------------------------------------------------------------------------------------------------------
# Work Samples
@admin.register(WorkSamples)
class WorkSamplesAdmin(admin.ModelAdmin):
    list_display = ["stylist", "service", "is_active"]
