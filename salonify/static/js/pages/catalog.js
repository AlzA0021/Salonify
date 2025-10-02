// static/js/pages/catalog.js
// page: catalog
// نقش: بهبود UX (کیبورد، افکت‌ها، prefetch، back behavior)؛ بدون وابستگی خارجی.

export function init() {
  console.debug('[catalog] init');

  const root = document.querySelector('.catalog-page');
  if (!root) return;

  // ----- Back button (history first, then href fallback)
  const backBtn = document.querySelector('[data-action="go-back"]');
  if (backBtn) {
    backBtn.addEventListener('click', (e) => {
      // اگر کاربر وسط-کلیک یا Ctrl/Cmd بود، دخالت نکن
      if (e.button !== 0 || e.metaKey || e.ctrlKey) return;
      e.preventDefault();
      if (window.history.length > 1) {
        try { window.history.back(); return; } catch {}
      }
      // fallback به href:
      const href = backBtn.getAttribute('href');
      if (href) window.location.assign(href);
    });
  }

  // ----- Keyboard accessibility for whole .menu-item (Enter/Space)
  root.addEventListener('keydown', (e) => {
    const link = e.target.closest('.menu-item');
    if (!link) return;
    const key = e.key.toLowerCase();
    if (key === 'enter' || key === ' ') {
      e.preventDefault();
      link.click();
    }
  });

  // ----- Active ripple-ish effect (CSS کلاس ساده)
  root.addEventListener('pointerdown', (e) => {
    const item = e.target.closest('.menu-item');
    if (!item) return;
    item.classList.add('is-active');
  });
  window.addEventListener('pointerup', () => {
    document.querySelectorAll('.menu-item.is-active').forEach(el => el.classList.remove('is-active'));
  });
  window.addEventListener('pointercancel', () => {
    document.querySelectorAll('.menu-item.is-active').forEach(el => el.classList.remove('is-active'));
  });

  // ----- Prefetch مقصد وقتی کاربر hover می‌کند (بهبود ادراک سرعت)
  const prefetch = (url) => {
    if (!url) return;
    // جلوگیری از ایجاد تگ‌های تکراری
    if (document.querySelector(`link[rel="prefetch"][href="${url}"]`)) return;
    const ln = document.createElement('link');
    ln.rel = 'prefetch';
    ln.href = url;
    ln.as = 'document';
    document.head.appendChild(ln);
  };

  root.querySelectorAll('.menu-item[href]').forEach((a) => {
    a.addEventListener('mouseenter', () => prefetch(a.getAttribute('href')));
    a.addEventListener('focus', () => prefetch(a.getAttribute('href')));
  });

  // ----- Focus ring مدیریت ظریف (فقط با کیبورد نشان بده)
  let hadKeyboardEvent = false;
  const setFocusVisible = (flag) => document.documentElement.classList.toggle('focus-visible', flag);
  window.addEventListener('keydown', (e) => {
    if (e.key === 'Tab' || e.key === 'ArrowDown' || e.key === 'ArrowUp' || e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
      hadKeyboardEvent = true; setFocusVisible(true);
    }
  }, true);
  ['mousedown','pointerdown','touchstart'].forEach(t =>
    window.addEventListener(t, () => { hadKeyboardEvent = false; setFocusVisible(false); }, true)
  );
}
