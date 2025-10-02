from django.contrib import admin

from .models import StylistSchedule, StylistTimeOff


# --------------------------------------------------------------------------
@admin.register(StylistSchedule)
class StylistWeeklyScheduleAdmin(admin.ModelAdmin):
    list_display = ["stylist", "salon", "service"]


# --------------------------------------------------------------------------
@admin.register(StylistTimeOff)
class StylistTimeOffAdmin(admin.ModelAdmin):
    list_display = ["stylist", "date", "reason"]
