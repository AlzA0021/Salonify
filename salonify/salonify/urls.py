"""
URL configuration for salonify project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("main", include("apps.main.urls", namespace="main")),
    path("accounts/", include("apps.accounts.urls", namespace="accounts")),
    path("services/", include("apps.services.urls", namespace="services")),
    path("", include("apps.salons.urls", namespace="salons")),
    path("stylists/", include("apps.stylists.urls", namespace="stylists")),
    # path("blogs/", include("apps.blogs.urls", namespace="blogs")),
    path("orders/", include("apps.orders.urls", namespace="orders")),
    # path("discounts/", include("apps.discounts.urls", namespace="discounts")),
    path("payments/", include("apps.payments.urls", namespace="payments")),
    path("csf/", include("apps.comments_scores_favories.urls", namespace="csf")),
    path("ckeditor", include("ckeditor_uploader.urls")),
    path("search/", include("apps.search.urls", namespace="search")),
    # path("locations/", include("apps.locations.urls", namespace="locations")),
    path("dashboards/", include("apps.dashboards.urls", namespace="dashboards")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
