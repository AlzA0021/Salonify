from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg, Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.decorators.http import require_POST
from apps.accounts.models import Customer, SalonManager
from apps.salons.models import Salon
from apps.services.models import Services
from .forms import CommentScoringForm
from .models import Comments, Favorits, Scoring


# -----------------------------------------------------------------------------------------------
class SalonCommentScoreView(View):
    def get(self, request, *args, **kwargs):
        salon_id = request.GET.get("salon_id")
        salon = get_object_or_404(Salon, id=salon_id)
        if not request.user.is_authenticated:
            messages.error(request, "برای نوشتن نظر و امتیاز ابتدا وارد شوید.")
            return redirect("salons:detail_salon", salon_id=salon_id)
        try:
            customer = Customer.objects.get(user=request.user)
        except Customer.DoesNotExist:
            messages.error(request, "شما به عنوان مشتری شناسایی نشده‌اید.")
            return redirect("salons:detail_salon", salon_id=salon_id)
        form = CommentScoringForm(salon=salon)
        # در اینجا معمولاً باید قالب مربوط به فرم نمایش داده شود
        return redirect("salons:detail_salon", salon_id=salon_id)

    def post(self, request, *args, **kwargs):
        salon_id = request.GET.get("salon_id")
        salon = get_object_or_404(Salon, id=salon_id)
        if not request.user.is_authenticated:
            messages.error(request, "برای نوشتن نظر و امتیاز ابتدا وارد شوید.")
            return redirect("salons:detail_salon", salon_id=salon_id)
        try:
            customer = Customer.objects.get(user=request.user)
        except Customer.DoesNotExist:
            messages.error(request, "شما به عنوان مشتری شناسایی نشده‌اید.")
            return redirect("salons:detail_salon", salon_id=salon_id)
        form = CommentScoringForm(request.POST, salon=salon)
        if form.is_valid():
            comment_text = form.cleaned_data.get("comment_text")
            stylist = form.cleaned_data.get("stylist")
            service = form.cleaned_data.get("service")
            score = form.cleaned_data.get("score")

            if comment_text:
                # ثبت یا به‌روزرسانی نظر
                comment_obj, created = Comments.objects.update_or_create(
                    salon=salon,
                    comment_user=customer,
                    stylist=stylist,
                    service=service,
                    defaults={
                        "comment_text": comment_text,
                        "is_active": False,  # نیاز به تایید دارند
                    },
                )
                # ثبت یا به‌روزرسانی امتیاز مربوط به نظر
                Scoring.objects.update_or_create(
                    comment=comment_obj,
                    defaults={
                        "score": score,
                    },
                )
            else:
                messages.error(request, "متن نظر الزامی است.")
                return redirect("salons:detail_salon", salon_id=salon_id)

            messages.success(
                request,
                "نظر و امتیاز شما با موفقیت ثبت شد. نظر شما پس از تایید نمایش داده خواهد شد.",
            )
            return redirect("salons:detail_salon", salon_id=salon_id)
        else:
            print("Form errors:", form.errors)
            messages.error(request, "مشکلی در ثبت نظر پیش آمد. لطفاً دوباره تلاش کنید.")
            return redirect("salons:detail_salon", salon_id=salon_id)


# -----------------------------------------------------------------------------------------------
def addScore(request):
    serviceId = request.GET.get("serviceId")
    score = request.GET.get("score")

    service = Services.objects.get(id=serviceId)

    Scoring.objects.create(service=service, scoring_user=request.user, score=score)
    return HttpResponse("امتیاز شما با موفقیت ثبت شد ")


# --------------------------------------------------------------------------------
def addFavorite(request):
    if request.user.is_authenticated:
        salon_id = request.GET.get("salonId")
        salon = get_object_or_404(Salon, id=salon_id)

        # بررسی اینکه سالن در علاقه مندی های کاربر هست یا نه
        favorite = Favorits.objects.filter(
            Q(favorite_user_id=request.user.id) & Q(salon_id=salon_id)
        ).first()
        if favorite:
            favorite.delete()
            return HttpResponse("حذف شد")
        else:
            Favorits.objects.create(salon=salon, favorite_user=request.user)
            return HttpResponse("اضافه شد")
    return HttpResponse("ابتدا وارد حساب کاربری شوید", status=401)


# ----------------------------------------------------------------------------------------------------
def get_favorite_salons(request):
    if not request.user.is_authenticated:
        messages.error(request, "ابتدا وارد حساب کاربری شوید.", "danger")
        return redirect("accounts:login")

    # ✅ بهینه‌سازی: به جای واکشی Favorits، مستقیماً Salon ها را فیلتر و annotate می‌کنیم
    salons_qs = (
        Salon.objects.filter(favorite_salon__favorite_user=request.user, is_active=True)
        .annotate(
            avg_score=Avg("scoring_salon__score"),
            # می‌توانید تعداد نظرات را هم اضافه کنید
            num_scores=Count("scoring_salon") 
        )
    )

    return render(request, "csf/partials/favorite_salons.html", {"salons": salons_qs})


# -----------------------------------------------------------------------------------------------------
@login_required
@require_POST
def approve_comment(request, comment_id, customer_id):
    try:
        # دریافت اطلاعات پایه
        user = request.user
        salon_manager = get_object_or_404(SalonManager, user=user)
        salon = get_object_or_404(Salon, salon_manager=salon_manager)

        # دریافت و بروزرسانی نظر
        comment = get_object_or_404(Comments, id=comment_id, salon=salon)
        comment.is_active = True
        comment.approved_user = user
        comment.save()

        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)
