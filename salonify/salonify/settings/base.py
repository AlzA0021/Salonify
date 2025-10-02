# salonify/settings/base.py

import os
from pathlib import Path
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# مسیر پایه پروژه را سه سطح بالاتر تنظیم می‌کنیم تا به ریشه پروژه (کنار manage.py) برسیم
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# راه‌اندازی django-environ برای خواندن متغیرهای محیطی
env = environ.Env(
    # مقدار پیش‌فرض و نوع متغیر DEBUG را مشخص می‌کنیم
    DEBUG=(bool, False)
)
# فایل .env را از ریشه پروژه می‌خوانیم
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# ==============================================================================
# CORE SETTINGS
# ==============================================================================

SECRET_KEY = env("SECRET_KEY")
DEBUG = env.bool("DEBUG")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

# ==============================================================================
# APPLICATION DEFINITION
# ==============================================================================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "apps.main.apps.MainConfig",
    "apps.accounts.apps.AccountsConfig",
    "apps.services.apps.ServicesConfig",
    "apps.stylists.apps.StylistsConfig",
    "apps.blogs.apps.BlogsConfig",
    "apps.salons.apps.SalonsConfig",
    "apps.comments_scores_favories.apps.CommentsScoresFavoriesConfig",
    "apps.orders.apps.OrdersConfig",
    "apps.discounts.apps.DiscountsConfig",
    "apps.payments.apps.PaymentsConfig",
    "apps.search.apps.SearchConfig",
    "apps.locations.apps.LocationsConfig",
    "apps.dashboards.apps.DashboardsConfig",
    # Third-party apps
    "ckeditor",
    "ckeditor_uploader",
    "django_admin_listfilter_dropdown",
    "django_render_partial",
    "django.contrib.gis",
    "leaflet",
    "debug_toolbar",
    "django_jalali",
    "zarinpal",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "middlewares.middlewares.RequestMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.locale.LocaleMiddleware",
]

ROOT_URLCONF = "salonify.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.csrf",
                "apps.main.views.madia_admin",
            ],
        },
    },
]

WSGI_APPLICATION = "salonify.wsgi.application"

# ==============================================================================
# DATABASES
# ==============================================================================

DATABASES = {"default": env.db_url("DATABASE_URL", default="postgis://user:pass@host:port/dbname")}
# موتور PostGIS را به صورت دستی تنظیم می‌کنیم چون env.db_url آن را تشخیص نمی‌دهد
DATABASES["default"]["ENGINE"] = "django.contrib.gis.db.backends.postgis"

# ==============================================================================
# AUTHENTICATION
# ==============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
AUTH_USER_MODEL = "accounts.CustomUser"

# ==============================================================================
# INTERNATIONALIZATION
# ==============================================================================

LANGUAGE_CODE = "fa"
TIME_ZONE = "Asia/Tehran"
USE_I18N = True
USE_TZ = True

# ==============================================================================
# STATIC & MEDIA FILES
# ==============================================================================

STATIC_URL = "static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
# STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles") # این خط را برای پروداکشن فعال کنید

MEDIA_URL = "media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# ==============================================================================
# THIRD-PARTY LIBRARIES CONFIGURATION
# ==============================================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Zarinpal Payment Gateway
MERCHANT = env("MERCHANT", default="3de1ce47-e5e5-4ffb-9f65-5e0866a08841")
PAYMENT_CALLBACK_URL = env(
    "PAYMENT_CALLBACK_URL", default="http://127.0.0.1:8000/payments/verify/"
)
SANDBOX = env.bool("SANDBOX", default=True)

# GIS Libraries Path
GDAL_LIBRARY_PATH = env("GDAL_LIBRARY_PATH", default=r"C:\OSGeo4W\bin\gdal311.dll")
GEOS_LIBRARY_PATH = env("GEOS_LIBRARY_PATH", default=r"C:\OSGeo4W\bin\geos_c.dll")
PROJ_LIBRARY_PATH = env("PROJ_LIBRARY_PATH", default=r"C:\OSGeo4W\bin\proj.dll")

LEAFLET_CONFIG = {
    "DEFAULT_CENTER": (35.6892, 51.3890),
    "DEFAULT_ZOOM": 11,
    "MIN_ZOOM": 3,
    "MAX_ZOOM": 18,
    "SCALE": "metric",
}

# ==============================================================================
# LOGGING
# ==============================================================================

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "accounts": {  # این را به نام یکی از اپ‌های خود تغییر دهید
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}


# ==============================================================================
# CKEDITOR
# ==============================================================================
CKEDITOR_UPLOAD_PATH = "images/ckeditor/upload_file"
CKEDITOR_STORAGE_BACKEND = "django.core.files.storage.FileSystemStorage"
CKEDITOR_CONFIGS = {
    "default": {
        "toolbar": "Custom",
        "toolbar_Custom": [
            ["Bold", "link", "unlink", "image"],
        ],
    },
    "special": {
        "toolbar": "special",
        "height": 500,
        "toolbar": "full",
        "toolbar_special": [
            ["Bold", "link", "unlink", "image"],
            ["CodeSnippet"],
        ],
        "extraPlugins": ",".join(
            [
                "codesnippet",
                "clipboard",
            ]
        ),
    },
    "special_an": {
        "toolbar": "special",
        "height": 500,
        "toolbar_special": [
            ["Bold"],
            ["CodeSnippet"],
        ],
        "extraPlugins": ",".join(
            [
                "codesnippet",
            ]
        ),
    },
}

# ==============================================================================
# CACHING CONFIGURATION
# ==============================================================================
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",  # آدرس سرور Redis شما
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}


# ==============================================================================
USE_L10N = True  # فعال بودن localization
USE_THOUSAND_SEPARATOR = True
