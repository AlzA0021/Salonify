from django import template
from khayyam import JalaliDate

register = template.Library()


@register.filter
def jalali_date(date, date_format="%B"):
    """
    تبدیل تاریخ میلادی به تاریخ شمسی با فرمت دلخواه.
    به طور پیش‌فرض فرمت %B به معنی نمایش نام کامل ماه (فارسی) است.
    """
    try:
        j_date = JalaliDate(date)
        return j_date.strftime(date_format)
    except Exception:
        return date


@register.filter
def intdiv(value, arg):
    """
    تقسیم صحیح (integer division): مقدار value را بر arg تقسیم کرده و بخش صحیح را برمی‌گرداند.
    """
    try:
        return int(value) // int(arg)
    except (ValueError, ZeroDivisionError, TypeError):
        return ""


@register.filter
def modulo(value, arg):
    """
    باقیمانده تقسیم (modulo): باقیمانده value بر arg را برمی‌گرداند.
    """
    try:
        return int(value) % int(arg)
    except (ValueError, ZeroDivisionError, TypeError):
        return ""


@register.filter
def startswith(text, starts):
    """
    Template filter to check if a string starts with another string.

    Usage:
    {% if field_name|startswith:'stylist_price_' %}
        <!-- Field is a stylist price field -->
    {% endif %}
    """
    if isinstance(text, str):
        return text.startswith(starts)
    return False
