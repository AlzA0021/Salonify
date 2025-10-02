from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from apps.accounts.models import Stylist
from apps.services.models import Services


# ---------------------------------------------------------------------------------
def stylist_services_api(request, stylist_id):
    stylist = get_object_or_404(Stylist, user_id=stylist_id)
    services = Services.objects.filter(stylists=stylist, is_active=True)
    data = [{"id": service.id, "name": service.service_name} for service in services]
    return JsonResponse(data, safe=False)
