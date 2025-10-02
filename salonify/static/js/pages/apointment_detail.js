// page: appointment_detail
// این فایل بدون DOMContentLoaded کار می‌کند؛ app.js بعد از لود DOM، init() را صدا می‌زند.
export function init() {
  console.debug('[appointment_detail] init');

  // ---------- Helpers ----------
  const $ = (sel, root = document) => root.querySelector(sel);

  const toIsoBasic = (date) => {
    // 2025-08-25T21:00:00.000Z -> 20250825T210000Z
    try { return date.toISOString().replace(/[-:]/g, '').replace(/\.\d{3}Z$/, 'Z'); }
    catch { return ''; }
  };

  const buildGoogleCalendarUrl = ({ title, details, location, start, end }) => {
    const params = new URLSearchParams({
      action: 'TEMPLATE',
      text: title || '',
      dates: `${toIsoBasic(start)}/${toIsoBasic(end)}`,
      details: details || '',
      location: location || '',
    });
    return `https://www.google.com/calendar/render?${params.toString()}`;
  };

  // ---------- Read meta ----------
  const meta = $('#appointment-meta');
  if (!meta) {
    console.warn('appointment-meta not found');
    return;
  }

  const dateStr = meta.dataset.date;     // YYYY-MM-DD
  const timeStr = meta.dataset.time;     // HH:MM
  const lat     = meta.dataset.lat;
  const lng     = meta.dataset.lng;

  let salon = {};
  let service = {};

  try { salon = JSON.parse(meta.dataset.salon || '{}'); } catch { salon = {}; }
  try { service = JSON.parse(meta.dataset.service || '{}'); } catch { service = {}; }

  if (!dateStr || !timeStr) {
    console.warn('Missing date/time on appointment-meta');
  }

  const duration = Number(service?.duration) || 60;
  const start = new Date(`${dateStr}T${timeStr}:00`);
  const end   = new Date(start.getTime() + duration * 60 * 1000);

  // ---------- Actions ----------
  // 1) Back
  const backBtn = $('[data-action="go-back"]');
  if (backBtn) backBtn.addEventListener('click', () => history.back());

  // 2) Add to Google Calendar
  const addToGoogleBtn = $('[data-action="add-to-google"]');
  if (addToGoogleBtn) {
    addToGoogleBtn.addEventListener('click', () => {
      const title   = `نوبت در ${salon?.name ?? 'سالن'}`;
      const details = `خدمت: ${service?.name ?? '-'} — مدت: ${duration} دقیقه`;
      const location = salon?.address ?? '';
      const url = buildGoogleCalendarUrl({ title, details, location, start, end });
      window.open(url, '_blank');
    });
  }

  // 3) Optional: اگر خواستی دکمه مسیریابی داینامیک باشد (به‌جای <a>)
  // می‌توانی در HTML یک دکمه با data-action="navigate" بگذاری.
  const navBtn = $('[data-action="navigate"]');
  if (navBtn && lat && lng) {
    navBtn.addEventListener('click', () => {
      const q = `${lat},${lng}`;
      window.open(`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(q)}`, '_blank');
    });
  }

  // 4) Optional: دانلود فایل ICS (اگر دکمه گذاشتی)
  const icsBtn = $('[data-action="download-ics"]');
  if (icsBtn) {
    icsBtn.addEventListener('click', () => {
      const title   = `نوبت در ${salon?.name ?? 'سالن'}`;
      const details = `خدمت: ${service?.name ?? '-'} — مدت: ${duration} دقیقه`;
      const location = salon?.address ?? '';

      const lines = [
        'BEGIN:VCALENDAR',
        'VERSION:2.0',
        'PRODID:-//Salonify//Appointment//FA',
        'CALSCALE:GREGORIAN',
        'METHOD:PUBLISH',
        'BEGIN:VEVENT',
        `UID:${Date.now()}@salonify`,
        `DTSTAMP:${toIsoBasic(new Date())}`,
        `DTSTART:${toIsoBasic(start)}`,
        `DTEND:${toIsoBasic(end)}`,
        `SUMMARY:${title}`,
        `DESCRIPTION:${details}`,
        `LOCATION:${location}`,
        'END:VEVENT',
        'END:VCALENDAR'
      ].join('\r\n');

      const blob = new Blob([lines], { type: 'text/calendar;charset=utf-8' });
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = 'appointment.ics';
      document.body.appendChild(a);
      a.click();
      a.remove();
      setTimeout(() => URL.revokeObjectURL(a.href), 1000);
    });
  }

  // 5) Safety: اگر lat/lng نیست، هیچ خطایی نده
  if (!lat || !lng) {
    console.info('No geo coords for appointment (navigation link is disabled in template when missing).');
  }
}
