// static/js/pages/stylists_list.js
// page: stylists_list
// نیازمندی‌ها: FullCalendar (CSS/JS) در <head> لود شود.

export function init() {
  console.debug('[stylists_list] init');

  // State برای هر آرایشگر: تاریخ/زمان انتخاب‌شده، سالن/خدمت انتخاب‌شده، و اینستنس تقویم
  /** @type {Map<string, {date?:string, time?:string, salon?:string, service?:string, calendar?:any}>} */
  const state = new Map();

  // کمکی: دسترسی به state یک آرایشگر
  const getStylistState = (stylistId) => {
    const k = String(stylistId);
    if (!state.has(k)) state.set(k, {});
    return state.get(k);
  };

  // ---------- Toggle Comments ----------
  function toggleComments(stylistPk) {
    const box = document.getElementById(`comments-${stylistPk}`);
    if (!box) return;
    const isOpen = box.style.display === 'block';
    box.style.display = isOpen ? 'none' : 'block';
  }

  // ---------- Calendar: render & events ----------
  function renderCalendar(stylistId, apiUrl) {
    const container = document.getElementById(`calendar-${stylistId}`);
    if (!container) {
      console.error(`calendar container #calendar-${stylistId} not found`);
      return;
    }

    // اگر قبلاً رندر شده بود، فقط نمایش بده
    const st = getStylistState(stylistId);
    if (st.calendar) {
      container.style.display = 'block';
      st.calendar.updateSize();
      return;
    }

    // دریافت داده‌ها و سپس رندر تقویم
    fetch(apiUrl)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => {
        container.style.display = 'block';

        // ساخت آرایه رویدادها
        const events = [
          ...(Array.isArray(data?.schedules) ? data.schedules : []).map((s) => ({
            start: `${s.date}T${s.start_time}`,
            end: `${s.date}T${s.end_time}`,
            color: 'green',
            title: 'کار',
          })),
          ...(Array.isArray(data?.time_offs) ? data.time_offs : []).map((to) => ({
            start: to.date + (to.start_time ? `T${to.start_time}` : ''),
            end: to.date + (to.end_time ? `T${to.end_time}` : ''),
            color: 'gray',
            title: 'تعطیلی',
          })),
        ];

        // رندر FullCalendar
        const calendar = new window.FullCalendar.Calendar(container, {
          initialView: 'timeGridWeek',
          headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'timeGridWeek', // امکان ارتقاء: افزودن views دیگر
          },
          events,
          dateClick: (info) => {
            // انتخاب مستقیم از گرید
            // رویداد نشانه‌گذاری انتخاب کاربر (دلخواه)
            calendar.addEvent({
              start: info.dateStr,
              end: info.dateStr,
              color: 'blue',
              title: 'انتخاب شما',
            });
            const [d, t = ''] = info.dateStr.split('T');
            const st2 = getStylistState(stylistId);
            st2.date = d;
            st2.time = t;
            alert(`تاریخ/زمان انتخاب شد: ${info.dateStr}`);
          },
          eventClick: (info) => {
            info.el.style.backgroundColor = 'blue';
            const [d, t = ''] = info.event.startStr.split('T');
            const st2 = getStylistState(stylistId);
            st2.date = d;
            st2.time = t;
            alert(`رویداد انتخاب شد: ${info.event.title}`);
          },
        });

        calendar.render();
        st.calendar = calendar;
      })
      .catch((err) => {
        console.error('fetch calendar error:', err);
        alert('خطا در دریافت یا نمایش برنامه کاری');
      });
  }

  function toggleCalendarVisibility(stylistId) {
    const container = document.getElementById(`calendar-${stylistId}`);
    if (!container) return;
    container.style.display = container.style.display === 'none' ? 'block' : 'none';
    const st = getStylistState(stylistId);
    if (st.calendar) st.calendar.updateSize();
  }

  // ---------- رزرو ----------
  async function reserve({ service, stylist, salon, date, time, reserveUrl }) {
    // اعتبارسنجی
    if (!service) {
      alert('لطفاً خدمت را انتخاب کنید.');
      return;
    }
    if (!salon) {
      alert('لطفاً سالن را انتخاب کنید.');
      return;
    }
    if (!date || !time) {
      alert('لطفاً تاریخ و زمان را انتخاب کنید.');
      return;
    }

    const url = new URL(reserveUrl || '/orders/add_to_order_cart/', window.location.origin);
    url.searchParams.set('service', service);
    url.searchParams.set('stylist', stylist);
    url.searchParams.set('salon', salon);
    url.searchParams.set('date', date);
    url.searchParams.set('time', time);

    try {
      const res = await fetch(url.toString(), { method: 'GET', credentials: 'same-origin' });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      // در صورت نیاز پاسخ را بررسی کنید
      alert('رزرو با موفقیت انجام شد!');
      if (typeof window.status_of_order_cart === 'function') {
        window.status_of_order_cart();
      }
    } catch (e) {
      console.error('reserve error:', e);
      alert('خطا در فرآیند رزرو.');
    }
  }

  // ---------- Event Delegation روی کل صفحه ----------
  document.addEventListener('click', (e) => {
    // نظرات
    const btnComments = e.target.closest('[data-action="toggle-comments"]');
    if (btnComments) {
      e.preventDefault();
      toggleComments(btnComments.dataset.stylistPk);
      return;
    }

    // لود تقویم
    const btnLoadCal = e.target.closest('[data-action="load-calendar"]');
    if (btnLoadCal) {
      e.preventDefault();
      renderCalendar(btnLoadCal.dataset.stylistId, btnLoadCal.dataset.apiUrl);
      return;
    }

    // نمایش/پنهان تقویم
    const btnToggleCal = e.target.closest('[data-action="toggle-calendar"]');
    if (btnToggleCal) {
      e.preventDefault();
      toggleCalendarVisibility(btnToggleCal.dataset.stylistId);
      return;
    }

    // رزرو
    const btnReserve = e.target.closest('[data-action="reserve"]');
    if (btnReserve) {
      e.preventDefault();
      const stylistId = btnReserve.dataset.stylistId;
      const reserveUrl = btnReserve.dataset.reserveUrl;
      // سعی می‌کنیم service/salon را از دکمه بخوانیم؛ اگر نبود از state/سلکت‌ها
      let { service, salon } = btnReserve.dataset;

      // اگر service یا salon خالی بود، از سلکت‌ها بخوان
      if (!service) {
        const sel = document.getElementById(`serviceSelect-${stylistId}`);
        if (sel) service = sel.value;
      }
      if (!salon) {
        const sel = document.getElementById(`salonSelect-${stylistId}`);
        if (sel) salon = sel.value;
      }

      // تاریخ/زمان از state
      const st = getStylistState(stylistId);
      const date = st?.date;
      const time = st?.time;

      reserve({
        service,
        stylist: stylistId,
        salon,
        date,
        time,
        reserveUrl,
      });
      return;
    }
  });

  // ---------- Select listeners (salon/service) ----------
  document.addEventListener('change', (e) => {
    const salonSel = e.target.closest('[data-role="salon-select"]');
    if (salonSel) {
      const stylistId = salonSel.dataset.stylistId;
      const st = getStylistState(stylistId);
      st.salon = salonSel.value || '';
      return;
    }
    const serviceSel = e.target.closest('[data-role="service-select"]');
    if (serviceSel) {
      const stylistId = serviceSel.dataset.stylistId;
      const st = getStylistState(stylistId);
      st.service = serviceSel.value || '';
    }
  });
}
