from django.conf import settings
from django.db.models import Q
from django.shortcuts import render, redirect
from django.views import View
from .forms import SupportForm
from django.contrib import messages

# --------------------------------------------------------------------
# Media settings
def madia_admin(request):
    return {"media_url": settings.MEDIA_URL}


# --------------------------------------------------------------------
# Index Page
# class IndexPage(View):
#     def get(self, request):
#         service_groups = GroupServices.objects.filter(Q(is_active=True) & Q(group_parent=None))

#         context = {
#             "service_groups": service_groups,
#         }
#         return render(request, "main/index.html", context)


# ----------------------------------------------------------------------------
# # Slider
# def slider(request):
#     sliders = Slider.objects.filter(is_active=True)
#     context = {
#         "sliders": sliders,
#     }
#     return render(request, "partials/header.html", context)

# -----------------------------------------------------------------------------
class SupportView(View):
    template_name = "main/support/contact_form.html"

    def get(self, request, *args, **kwargs):
        form = SupportForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = SupportForm(request.POST)

        if form.is_valid():
            # پردازش اطلاعات فرم
            email = form.cleaned_data["email"]
            reason = form.cleaned_data["reason"]
            description = form.cleaned_data["description"]

            # در اینجا می‌توانید اطلاعات را ذخیره کنید یا ایمیل ارسال کنید
            # برای مثال:
            # support_ticket = SupportTicket.objects.create(
            #     email=email,
            #     reason=reason,
            #     description=description
            # )

            messages.success(
                request, "درخواست شما با موفقیت ارسال شد. به زودی با شما تماس خواهیم گرفت."
            )
            return redirect("main:success")

        messages.error(request, "لطفاً خطاهای فرم را برطرف کنید.")
        return render(request, self.template_name, {"form": form})


def success_view(request):
    return render(request, "main/support/success.html")
