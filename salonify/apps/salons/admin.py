from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin

from .models import (
    CustomerNote,
    Salon,
    SalonOpeningHours,
    SalonsGallery,
    SupplementaryInfoView,
)


# ----------------------------------------------------------------------------------------------
class SalonsGalleryInline(admin.TabularInline):
    model = SalonsGallery
    extra = 1


@admin.register(Salon)
class SalonAdmin(LeafletGeoAdmin, admin.ModelAdmin):
    list_display = [
        "salon_name",
        "is_active",
        "zone",
        "salon_manager",
        "show_salon_service",
        "show_salon_stylist",
        "registere_date",
    ]
    list_filter = ["zone", "registere_date", "is_active"]
    search_fields = ["salon_name", "salon_manager", "stylists"]
    ordering = ["registere_date", "salon_name"]
    inlines = [
        SalonsGalleryInline,
    ]

    def show_salon_service(self, obj):
        return " , ".join([service.service_name for service in obj.services.all()])

    def show_salon_stylist(self, obj):
        stylist_names = ", ".join([stylist.user.name for stylist in obj.stylists.all()])
        return stylist_names

    show_salon_service.short_description = "خدمات سالن"
    show_salon_stylist.short_description = "آرایشکران سالن "


# --------------------------------------------------------------------------------------------------
@admin.register(SalonOpeningHours)
class SalonOpeningHoursAdmin(admin.ModelAdmin):
    list_display = ["salon", "day_of_week", "is_closed"]


# ---------------------------------------------------------------------------------------------------
@admin.register(SupplementaryInfoView)
class SupplementaryInfoAdmin(admin.ModelAdmin):
    list_display = ["salon", "title", "is_active"]

    def salon(self, obj):
        return obj.salon.salon_name if obj.salon else None


# --------------------------------------------------------------------------------------------------
@admin.register(CustomerNote)
class CustomerNoteAdmin(admin.ModelAdmin):
    list_display = ["customer", "note", "created_at"]

    def customer(self, obj):
        return obj.customer.name if obj.customer else None
