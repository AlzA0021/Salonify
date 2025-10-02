// static/js/pages/checkout.js
// page: checkout

export function init() {
  console.debug('[checkout] init');

  const root = document.querySelector('.checkout-page');
  if (!root) return;

  const payForm = root.querySelector('#checkoutPayForm');
  const payButton = root.querySelector('#paySubmitBtn');
  const radios = root.querySelectorAll('input[name="payment_type"]');
  const couponForm = root.querySelector('#couponForm');
  const couponInput = root.querySelector('#couponCodeInput');
  const couponMsg = root.querySelector('#couponMessage');
  const totalsBox = root.querySelector('[data-totals]');

  // --- کمک‌تابع‌ها
  const fa = new Intl.NumberFormat('fa-IR');
  const enablePay = (flag) => {
    if (!payButton) return;
    payButton.disabled = !flag;
    payButton.classList.toggle('is-disabled', !flag);
    payButton.setAttribute('aria-disabled', String(!flag));
  };

  // --- فعال‌سازی دکمه پرداخت زمانی که یک گزینه انتخاب شود
  if (radios.length) {
    const hasChecked = Array.from(radios).some(r => r.checked);
    enablePay(hasChecked);
    radios.forEach(r => {
      r.addEventListener('change', () => enablePay(true));
    });
  } else {
    // اگر رادیویی نبود، بگذار دکمه فعال باشد
    enablePay(true);
  }

  // --- اسکرول به پیام‌ها/خطاها (در صورت وجود)
  const firstAlert = root.querySelector('.alert, .form-error, .errorlist');
  if (firstAlert) {
    firstAlert.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  // --- فرمت اعداد داخل باکس مجموع‌ها (احتیاطی)
  if (totalsBox) {
    totalsBox.querySelectorAll('[data-intcomma]').forEach(el => {
      const raw = el.getAttribute('data-intcomma');
      if (!raw) return;
      const n = Number(String(raw).replace(/[^\d.-]/g, ''));
      if (!Number.isNaN(n)) el.textContent = fa.format(n);
    });
  }

  // --- ارسال AJAX برای کوپن (اختیاری؛ اگر بخواهی پست عادی باشد، این بلاک را حذف کن)
  if (couponForm && couponInput) {
    couponForm.addEventListener('submit', async (e) => {
      // اگر فرم اکشن سمت سرور دارد و نمی‌خواهی AJAX باشد، این return را بگذار:
      // return;

      e.preventDefault();
      const action = couponForm.getAttribute('action');
      const csrf = couponForm.querySelector('input[name="csrfmiddlewaretoken"]')?.value || '';
      const code = couponInput.value.trim();

      if (!code) {
        showCouponMessage('لطفاً کد تخفیف را وارد کنید.', false);
        couponInput.focus();
        return;
      }

      try {
        setCouponLoading(true);
        const res = await fetch(action, {
          method: 'POST',
          headers: { 'X-CSRFToken': csrf, 'Accept': 'application/json' },
          body: new FormData(couponForm),
        });

        // API شما ممکن است HTML برگرداند؛ اگر JSON نیست، fallback به reload:
        const contentType = res.headers.get('Content-Type') || '';
        if (!contentType.includes('application/json')) {
          window.location.reload();
          return;
        }

        const data = await res.json();
        if (data.success) {
          showCouponMessage(data.message || 'کد تخفیف با موفقیت اعمال شد.', true);
          // در صورت برگشت مقادیر جدید مجموع‌ها:
          if (data.totals && totalsBox) {
            updateTotalsUI(totalsBox, data.totals);
          }
        } else {
          showCouponMessage(data.message || 'کد تخفیف معتبر نیست.', false);
        }
      } catch (err) {
        showCouponMessage('خطای شبکه در اعمال کد تخفیف.', false);
      } finally {
        setCouponLoading(false);
      }
    });
  }

  function setCouponLoading(loading) {
    couponForm?.classList.toggle('is-loading', loading);
  }

  function showCouponMessage(msg, ok) {
    if (!couponMsg) return alert(msg);
    couponMsg.textContent = msg;
    couponMsg.classList.remove('ok', 'err');
    couponMsg.classList.add(ok ? 'ok' : 'err');
    couponMsg.style.display = 'block';
    couponMsg.focus({ preventScroll: false });
  }

  function updateTotalsUI(box, totals) {
    // انتظار: totals = { total_price, tax, final_price } (ارقام عددی)
    const sel = (s) => box.querySelector(s);
    const setNum = (el, val) => { if (el) el.textContent = fa.format(Number(val || 0)) + ' تومان'; };

    setNum(sel('[data-total-price]'), totals.total_price);
    setNum(sel('[data-tax]'), totals.tax);
    setNum(sel('[data-final-price]'), totals.final_price);
  }
}
