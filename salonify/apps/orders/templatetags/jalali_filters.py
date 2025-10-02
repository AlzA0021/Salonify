import datetime
from django import template
from khayyam import JalaliDate

register = template.Library()


@register.filter
def remaining_days(appointment_date):

    today_jdate = JalaliDate.today()

    # محاسبه اختلاف روزها
    delta_days = appointment_date.toordinal() - today_jdate.toordinal()

    return delta_days


@register.filter
def jalali_date(value):
    # اگر value رشته باشد، سعی در تبدیل آن به تاریخ داریم.
    if isinstance(value, str):
        try:
            value = datetime.datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            return value  # در صورت عدم تطابق فرمت، مقدار اصلی برگردانده می‌شود

    # نگاشت روزهای هفته
    weekdays = {
        "Saturday": "شنبه",
        "Sunday": "یکشنبه",
        "Monday": "دوشنبه",
        "Tuesday": "سه‌شنبه",
        "Wednesday": "چهارشنبه",
        "Thursday": "پنجشنبه",
        "Friday": "جمعه",
    }

    # نگاشت ماه‌ها
    months = {
        "January": "دی",
        "February": "بهمن",
        "March": "اسفند",
        "April": "فروردین",
        "May": "اردیبهشت",
        "June": "خرداد",
        "July": "تیر",
        "August": "مرداد",
        "September": "شهریور",
        "October": "مهر",
        "November": "آبان",
        "December": "آذر",
    }

    # فرمت‌بندی تاریخ به صورت انگلیسی
    formated_date = value.strftime("%A %d %B %Y")

    # جایگزینی نام روزها
    for en, fa in weekdays.items():
        formated_date = formated_date.replace(en, fa)

    # جایگزینی نام ماه‌ها
    for en, fa in months.items():
        formated_date = formated_date.replace(en, fa)

    return formated_date
