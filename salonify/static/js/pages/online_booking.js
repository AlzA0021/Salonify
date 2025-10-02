// static/js/pages/dashboard_online_booking.js
// page: dashboard_online_booking

export function init() {
  console.debug('[dashboard_online_booking] init');

  const root = document.querySelector('.online-booking-page');
  if (!root) return;

  // Back button
  const backBtn = root.querySelector('[data-action="go-back"]');
  if (backBtn) {
    backBtn.addEventListener('click', (e) => {
      e.preventDefault();
      const fallback = backBtn.getAttribute('data-fallback-url') || '/';
      if (history.length > 1) history.back();
      else window.location.assign(fallback);
    });
  }

  // Enhance option cards (optional visual/behavior hooks)
  root.querySelectorAll('.option').forEach((opt) => {
    const disabled = opt.dataset.disabled === 'true';
    if (disabled) {
      opt.classList.add('is-disabled');
      opt.setAttribute('aria-disabled', 'true');
      opt.addEventListener('click', (e) => e.preventDefault());
    }
  });
}
