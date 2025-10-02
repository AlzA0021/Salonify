// static/js/pages/dashboard_membership.js
// page: dashboard_membership

export function init() {
  console.debug('[dashboard_membership] init');

  const root = document.querySelector('.membership-page');
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

  // Buttons: learn more / get started
  const learnBtn = root.querySelector('[data-action="learn"]');
  const startBtn = root.querySelector('[data-action="start"]');

  if (learnBtn) {
    learnBtn.addEventListener('click', (e) => {
      e.preventDefault();
      // اینجا می‌تونید به یک صفحه راهنما لینک بدید
      alert('آموزش بیشتر به‌زودی!');
    });
  }

  if (startBtn) {
    startBtn.addEventListener('click', (e) => {
      e.preventDefault();
      // اینجا می‌تونید به فرم ساخت عضویت هدایت کنید
      alert('بخش ساخت عضویت به‌زودی راه‌اندازی می‌شود!');
    });
  }

  // Membership options (اگر بعداً بخش عضویت‌ها را از کامنت خارج کردید)
  const options = root.querySelectorAll('.membership-option');
  if (options.length) {
    options.forEach((opt) => {
      opt.addEventListener('click', () => {
        options.forEach((o) => (o.style.border = 'none'));
        opt.style.border = '2px solid #9C88FF';
        const name = opt.querySelector('.membership-name')?.textContent?.trim() || '—';
        alert(`عضویت انتخاب شد: ${name}`);
      });
    });
  }
}
