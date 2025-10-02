from admin_decorators import order_field, short_description
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.core import serializers
from django.db.models import Count
from django.http import HttpResponse
from apps.accounts.models import Stylist
from .models import (
    Feature,
    FeatureValue,
    GroupServices,
    ServiceFeature,
    ServiceGallery,
    ServicePrice,
    Services,
)


# -------------------------------------------------------
class GroupFilter(SimpleListFilter):
    title = "گروه های خدمات"
    parameter_name = "group"

    def lookups(self, request, model_admin):
        sub_groups = GroupServices.objects.filter(group_parent__isnull=False)
        groups = set([item.group_parent for item in sub_groups])
        return [(group.id, group.group_title) for group in groups]  # type: ignore

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(group_parent_id=self.value())
        return queryset


def de_active_service_group(modeladmin, request, queryset):
    res = queryset.update(is_active=False)
    message = f"تعداد {res} از گروه خدمات غیرفعال شدند"
    modeladmin.message_user(request, message)


def active_service_group(modeladmin, request, queryset):
    res = queryset.update(is_active=True)
    message = f"تعداد {res} از گروه خدمات فعال شدند"
    modeladmin.message_user(request, message)


def export_json(modeladmin, request, queryset):
    response = HttpResponse("application/json")
    serializers.serialize("json", queryset, stream=response)
    return response


# ----------------------------------------------------------------------------------------------------------------
class ServiceGroupInstanceInlineAdmin(admin.TabularInline):
    model = GroupServices


@admin.register(GroupServices)
class ServiceGroupAdmin(admin.ModelAdmin):
    list_display = (
        "group_title",
        "is_active",
        "group_parent",
        "registere_date",
        "updated_date",
        "count_sub_group",
        "count_service_group",
    )
    list_filter = (GroupFilter,)
    search_fields = ("group_title",)
    ordering = ("group_parent", "group_title")
    inlines = [ServiceGroupInstanceInlineAdmin]
    actions = [de_active_service_group, active_service_group, export_json]
    list_editable = ["is_active"]

    def get_queryset(self, *args, **kwargs):
        qs = super(ServiceGroupAdmin, self).get_queryset(*args, **kwargs)
        qs = qs.annotate(sub_group=Count("groups"))
        qs = qs.annotate(service_of_group=Count("services_of_group"))
        return qs

    def count_sub_group(self, obj):
        return obj.sub_group

    @short_description("تعداد خدمات")
    @order_field("count_service_group")
    def count_service_group(self, obj):
        return obj.service_of_group

    count_sub_group.short_description = "تعداد زیرگروهها"
    de_active_service_group.short_description = "غیرفعال کردن گروه های خدمات"
    active_service_group.short_description = "فعال کردن گروه های خدمات"
    export_json.short_description = "خروجی json از گروه خدمات "


# --------------------------------------------------------------------------------------------------------------
def de_active_service(modeladmin, request, queryset):
    res = queryset.update(is_active=False)
    message = f"تعداد {res} از خدمات غیرفعال شدند"
    modeladmin.message_user(request, message)


def active_service(modeladmin, request, queryset):
    res = queryset.update(is_active=True)
    message = f"تعداد {res} از خدمات فعال شدند"
    modeladmin.message_user(request, message)


class ServiceFeatureInlineAdmin(admin.TabularInline):
    model = ServiceFeature


class ServiceGalleryInlineAdmin(admin.TabularInline):
    model = ServiceGallery


@admin.register(Services)
class ServicesAdmin(admin.ModelAdmin):
    list_display = [
        "service_name",
        "is_active",
        "updated_date",
        "show_service_groups",
        "display_stylists",
    ]
    list_filter = [
        "service_name",
    ]
    search_fields = ["service_name", "service_group"]
    ordering = ["updated_date", "service_name"]
    actions = [de_active_service, active_service]
    inlines = [ServiceFeatureInlineAdmin, ServiceGalleryInlineAdmin]

    de_active_service.short_description = "غیرفعال کردن خدمات"
    active_service.short_description = "فعال کردن خدمات"

    def show_service_groups(self, obj):
        return " , ".join([group.group_title for group in obj.service_group.all()])

    show_service_groups.short_description = "گروه های خدمات "

    # def formfield_for_manytomany(self, db_field, request, **kwargs) :
    #     if db_field.name == 'service_group':
    #         kwargs['queryset'] = GroupServices.objects.filter(~Q(group_parent=None))
    #     return super().formfield_for_manytomany(db_field, request, **kwargs)

    fieldsets = (
        (
            "خدمات",
            {
                "fields": (
                    "service_name",
                    "description",
                    ("service_image", "is_active"),
                    (
                        "service_group",
                        "duration_minutes",
                    ),
                ),
            },
        ),
        (
            "تاریخ و زمان",
            {
                "fields": ("published_date",),
            },
        ),
        (
            "آرایشگران",
            {
                "fields": ("stylists",),
            },
        ),
    )

    class Media:
        css = {"all": ("css/admin_style.css",)}

    def display_stylists(self, obj):
        return ", ".join(
            [stylist.user.name + "" + stylist.user.family for stylist in obj.stylists.all()]
        )

    display_stylists.short_description = "آرایشگران "

    # filter_horizontal = ('stylists',)  # This allows for easy editing of many-to-many relationships

    admin.site.unregister(Stylist)
    admin.site.register(Stylist)


# ------------------------------------------------------------------------------------------------
class FeatureValueInlineAdmin(admin.TabularInline):
    model = FeatureValue
    extra = 3


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ["feature_name", "display_groups", "display_feature_values"]
    list_filter = ["feature_name"]
    search_fields = ["feature_name"]
    ordering = ["feature_name"]
    inlines = [
        FeatureValueInlineAdmin,
    ]

    def display_groups(self, obj):
        return " , ".join([group.group_title for group in obj.service_group.all()])

    def display_feature_values(self, obj):
        return " , ".join([value.value_title for value in obj.feature_values.all()])

    display_groups.short_description = "نمایش گروهها"
    display_feature_values.short_description = "نمایش مقدار ویژگی"


# ----------------------------------------------------------------------------------------------------
@admin.register(FeatureValue)
class FeatureValueAdmin(admin.ModelAdmin):
    list_display = [
        "value_title",
    ]
    list_filter = ["value_title"]
    search_fields = ["value_title"]
    ordering = ["value_title"]


# -----------------------------------------------------------------------------------------------------
@admin.register(ServicePrice)
class ServicePriceAdmin(admin.ModelAdmin):
    list_display = ["stylist", "service", "price"]
