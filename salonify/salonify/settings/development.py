# salonify/settings/development.py

from .base import *

# تنظیمات امنیتی در محیط توسعه سخت‌گیرانه نیستند
DEBUG = True

# این آدرس‌ها برای دسترسی به سرور توسعه استفاده می‌شوند
CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "http://192.168.1.150:8000",
    "https://*.ngrok-free.app", # برای ngrok از wildcard استفاده کنید
    "https://*.ngrok.io",
]

# تنظیمات django-debug-toolbar
INTERNAL_IPS = [
    "127.0.0.1",
]

# در محیط توسعه، ایمیل‌ها به جای ارسال واقعی، در کنسول چاپ می‌شوند
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'