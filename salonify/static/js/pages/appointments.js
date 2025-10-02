// page: appointment_detail  (در صورت نیاز: appointments)
// نکته: این فایل بدون DOMContentLoaded کار می‌کند؛ init() را app.js بعد از لود DOM صدا می‌زند.
export function init(){
  console.debug('[appointment_detail] init');

  /* ----------------------------
   * Utils
   * -------------------------- */
  const createNavigationLink = (lat, lng, salonName) => {
    const encodedSalonName = encodeURIComponent(salonName || '');
    const navLinks = {
      android: `geo:${lat},${lng}?q=${lat},${lng}(${encodedSalonName})`,
      ios:     `maps://maps.google.com/maps?daddr=${lat},${lng}&q=${encodedSalonName}`,
      web:     `https://www.google.com/maps/search/?api=1&query=${lat},${lng}`,
    };
    const ua = navigator.userAgent || '';
    if (/Android/i.test(ua)) return navLinks.android;
    if (/iPhone|iPad|iPod/i.test(ua)) return navLinks.ios;
    return navLinks.web;
  };

  const formatDateForGoogleCalendar = (date) => {
    try {
      // 2025-08-25T21:00:00.000Z -> 20250825T210000Z
      return date.toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z';
    } catch (e) {
      console.error('ISO format error:', e);
      return '';
    }
  };

  const extractTextFromElement = (element, prefix = '') => {
    if (!element) return '';
    const text = element.textContent.trim();
    return text.replace(prefix, '').trim();
  };

  /* ----------------------------
   * Handlers (event delegation)
   * -------------------------- */

  function onNavigateClick(target){
    const appointmentCard = target.closest('.appointment-card');
    if (!appointmentCard) return;

    const lat = appointmentCard.getAttribute('data-salon-lat');
    const lng = appointmentCard.getAttribute('data-salon-lng');
    const salonName = appointmentCard.getAttribute('data-salon-name') || '';

    if (!lat || !lng) {
      alert('موقعیت مکانی سالن در دسترس نیست.');
      return;
    }
    try {
      const navigationLink = createNavigationLink(lat, lng, salonName);
      window.open(navigationLink, '_blank');
    } catch (error) {
      console.error('Navigation error:', error);
      alert('مشکل در باز کردن نقشه. لطفاً مجدداً تلاش کنید.');
    }
  }

  function onCalendarClick(target){
    const appointmentCard = target.closest('.appointment-card');
    if (!appointmentCard) return;

    const appointmentDate = appointmentCard.getAttribute('data-appointment-date'); // YYYY-MM-DD
    const appointmentTime = appointmentCard.getAttribute('data-appointment-time'); // HH:MM

    if (!appointmentDate || !appointmentTime) {
      alert('تاریخ و زمان این نوبت در دسترس نیست.');
      return;
    }

    // ساخت زمان شروع/پایان (فرض: 60 دقیقه)
    const startDate = new Date(`${appointmentDate}T${appointmentTime}:00`);
    const endDate   = new Date(startDate.getTime() + 60 * 60 * 1000);

    const serviceName = extractTextFromElement(
      appointmentCard.querySelector('.service-name'),
      'خدمت:'
    );
    const salonName = extractTextFromElement(
      appointmentCard.querySelector('.salon-name')
    );

    const eventTitle   = `رزرو: ${serviceName}`;
    const eventDetails = `سالن: ${salonName}\nخدمت: ${serviceName}\nتاریخ: ${appointmentDate} - ${appointmentTime}`;
    const start = formatDateForGoogleCalendar(startDate);
    const end   = formatDateForGoogleCalendar(endDate);

    const googleCalendarUrl =
      `https://www.google.com/calendar/render?action=TEMPLATE` +
      `&text=${encodeURIComponent(eventTitle)}` +
      `&dates=${start}/${end}` +
      `&details=${encodeURIComponent(eventDetails)}` +
      `&location=${encodeURIComponent(salonName)}`;

    window.open(googleCalendarUrl, '_blank');
  }

  // Event delegation: اگر کارت‌ها بعداً به DOM اضافه شوند هم کار می‌کند
  document.addEventListener('click', (e) => {
    const navBtn = e.target.closest('.btn-directions[data-navigate="true"]');
    if (navBtn) {
      e.preventDefault();
      onNavigateClick(navBtn);
      return;
    }

    const calBtn = e.target.closest('.btn-calendar');
    if (calBtn) {
      e.preventDefault();
      onCalendarClick(calBtn);
    }
  });

  /* ----------------------------
   * سازگاری با HTML قدیمی (onclick)
   * اگر جایی onclick="addToCalendar(...)" یا onclick="openDirections(...)" داشتی،
   * این‌ها را نگاه می‌دارد:
   * -------------------------- */
  window.__appointmentOpenDirections = (lat, lng, salonName='') => {
    try {
      const link = createNavigationLink(lat, lng, salonName);
      window.open(link, '_blank');
    } catch (err) {
      console.error('Navigation error:', err);
    }
  };

  window.__appointmentAddToCalendar = ({date, time, salonName='', serviceName='', duration=60}) => {
    const startDate = new Date(`${date}T${time}:00`);
    const endDate   = new Date(startDate.getTime() + (Number(duration)||60) * 60 * 1000);
    const eventTitle   = `رزرو: ${serviceName}`;
    const eventDetails = `سالن: ${salonName}\nخدمت: ${serviceName}\nتاریخ: ${date} - ${time}`;
    const start = formatDateForGoogleCalendar(startDate);
    const end   = formatDateForGoogleCalendar(endDate);
    const url =
      `https://www.google.com/calendar/render?action=TEMPLATE` +
      `&text=${encodeURIComponent(eventTitle)}` +
      `&dates=${start}/${end}` +
      `&details=${encodeURIComponent(eventDetails)}` +
      `&location=${encodeURIComponent(salonName)}`;
    window.open(url, '_blank');
  };
}

