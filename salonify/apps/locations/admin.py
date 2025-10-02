from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin

from .models import Neighborhood


@admin.register(Neighborhood)
class NeighborhoodAdmin(LeafletGeoAdmin, admin.ModelAdmin):
    list_display = ["name", "polygon"]
