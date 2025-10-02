from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.views import View

from .models import GroupServices, Services


# ------------------------------------------------------------------------------------------
# class IndexServiceGroupsView(View):
#     def get(self, request):
#         # ✅ بهینه‌سازی: واکشی زیرگروه‌ها و شمارش خدمات در یک کوئری
#         service_groups = GroupServices.objects.filter(
#             is_active=True, 
#             group_parent=None
#         ).prefetch_related(
#             # واکشی تمام زیرگروه‌های فعال هر گروه اصلی
#             Prefetch(
#                 'groups', 
#                 queryset=GroupServices.objects.filter(is_active=True), 
#                 to_attr='active_subgroups'
#             ),
#             # واکشی تمام خدمات فعال هر گروه اصلی
#             Prefetch(
#                 'services_of_group',
#                 queryset=Services.objects.filter(is_active=True),
#                 to_attr='active_services'
#             )
#         )

#         context = {"service_groups": service_groups}
#         print(service_groups)
#         return render(request, "services/partials/service_group_index.html", context)


# #------------------------------------------------------------------------------------------
# # زیرگروه ها
# class SubGroupView(View):
#     def get(self, request, *args, **kwargs):
#         current_group = get_object_or_404(GroupServices, slug=kwargs["slug"])
#         sub_group = GroupServices.objects.filter(Q(is_active=True) & Q(group_parent=current_group))
#         print(sub_group)

#         context = {
#             "current_group": current_group,
#             "sub_group": sub_group,
#         }
#         return render(request, "services/sub_group.html", context)


# ---------------------------------------------------------------------------------------------
# # تمام محصولات گروه
# class ServicesView(View):
#     def get(self, request, group_id=None):
#         # گروه‌های والد که فعال هستند و والد ندارند (یعنی ریشه‌ای هستند)
#         parent_groups = GroupServices.objects.filter(is_active=True, group_parent=None)
#         selected_group = None
#         services = None
#         subgroups = None

#         if group_id:
#             # دریافت گروه انتخاب‌شده بر اساس id و فعال بودن
#             selected_group = get_object_or_404(GroupServices, id=group_id, is_active=True)
#             # دریافت خدمات مرتبط با گروه‌های زیرمجموعه‌ی این گروه انتخاب‌شده
#             services = Services.objects.filter(
#                 service_group__group_parent=selected_group
#             ).order_by("-view_count")

#             subgroups = GroupServices.objects.filter(group_parent=selected_group)

#         else:

#             services = Services.objects.filter(is_active=True).order_by("-view_count")

#             subgroups = GroupServices.objects.filter(
#                 is_active=True, group_parent__isnull=False
#             ).order_by("group_title")

#         context = {
#             "groups": parent_groups,
#             "services": services,
#             "selected_group": selected_group,
#             "subgroups": subgroups,
#         }

#         return render(request, "services/all_services.html", context)


# -------------------------------------------------------------------------------------------
def get_subgroups(request, group_id):

    try:
        group = GroupServices.objects.get(id=group_id)
        subgroups = GroupServices.objects.filter(group_parent=group).distinct()
        subgroup_list = [
            {"title": subgroup.group_title, "id": subgroup.id} for subgroup in subgroups
        ]

        response_data = {"group_title": group.group_title, "subgroups": subgroup_list}
        return JsonResponse(response_data)
    except GroupServices.DoesNotExist:
        return JsonResponse({"error": "Group not found"}, status=404)

# -------------------------------------------------------------------------------------------
def get_service_of_subgroups(request, subgroup_id):

    group_parent = get_object_or_404(GroupServices, id=subgroup_id)
    services = Services.objects.filter(service_group=group_parent)
    return render(request, "services/partials/filtered_services.html", {"services": services})

# -------------------------------------------------------------------------------------------
def get_service_of_sorting(request, subgroup_id, sort_type):

    group_parent = get_object_or_404(GroupServices, id=subgroup_id)
    services = None
    if sort_type == 0:
        services = Services.objects.filter(service_group=group_parent).order_by("-view_count")
    elif sort_type == 1:
        services = Services.objects.filter(service_group=group_parent).order_by("-registere_date")
    elif sort_type == 2:
        services = Services.objects.filter(service_group=group_parent).order_by("service_name")
    return render(request, "services/partials/filtered_services.html", {"services": services})


# ---------------------------------------------------------------------------------------------------
def categories(request):
    service_groups = GroupServices.objects.filter(Q(is_active=True) & Q(group_parent=None))

    context = {"service_groups": service_groups}
    return render(request, "services/partials/categories.html", context)


# ---------------------------------------------------------------------------------------------------
def service_dynamic_content(request):
    if request.is_ajax():
        service_id = request.GET.get("service_id")
        content_type = request.GET.get("content_type")
        service = get_object_or_404(Services, id=service_id)

        if content_type == "info":
            html = render_to_string("services/partials/service_info.html", {"service": service})
        elif content_type == "comments":
            comments = service.comment_services.filter(is_active=True)
            html = render_to_string(
                "services/partials/service_comments.html", {"comments": comments}
            )
        elif content_type == "stylists":
            html = render_to_string(
                "services/partials/service_stylists.html", {"service": service}
            )
        else:
            return JsonResponse({"status": "error", "message": "Invalid content type"})

        return JsonResponse({"status": "success", "html": html})
    else:
        return JsonResponse({"status": "error", "message": "Invalid request"})


# --------------------------------------------------------------------------------------------------------------------------------
def get_service_priceList(request, service_id):
    service = get_object_or_404(Services, id=service_id)
    stylists = service.stylists.all()

    # آماده کردن لیست خدمات به همراه قیمت
    service_price_list = []
    for stylist in stylists:
        # گرفتن قیمت خدمت برای این آرایشگر
        price = stylist.get_price_for_service(service)
        average_score = round(service.get_average_score())
        # اضافه کردن اطلاعات خدمت به لیست
        service_price_list.append(
            {
                "stylist_fullName": f"{stylist.user.name}\t\t{stylist.user.family}",
                "stylist_image": stylist.profile_image,
                "duration_minutes": service.duration_minutes,
                "score": average_score,
                "price": price,
                "star_range": range(1, 6),
            }
        )

    context = {
        "service": service,
        "service_price_list": service_price_list,
    }
    return render(request, "services/partials/priceList.html", context)
