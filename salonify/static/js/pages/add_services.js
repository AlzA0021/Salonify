// static/js/pages/add_services.js
// page: add_services
// نقش: فرم افزودن/ویرایش خدمت در داشبورد (بدون وابستگی؛ Select2 اختیاری با jQuery)

export function init() {
  console.debug('[add_services] init');

  const $  = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  // تبدیل اعداد به فارسی
  const toFaDigits = (val) => String(val).replace(/\d/g, (d) => '۰۱۲۳۴۵۶۷۸۹'[d]);

  /* --------------------------------------
   * 1) شمارنده کاراکترها (سازگار با وجود error-message بین input و counter)
   * ------------------------------------ */
  function initCharacterCounters() {
    const candidates = $$('input[type="text"], textarea');

    candidates.forEach((input) => {
      // در همان .form-group به دنبال .character-count بگرد
      const formGroup = input.closest('.form-group') || input.parentElement;
      const counter = formGroup?.querySelector('.character-count');
      if (!counter) return;

      const getMax = () => {
        const m = input.getAttribute('maxlength');
        if (m) return parseInt(m, 10);
        // fallback معقول اگر maxlength روی فیلد ست نشده
        if (input.id === 'id_summery_description') return 200;
        return 500;
      };

      const update = () => {
        const max = getMax();
        const len = (input.value || '').length;
        counter.textContent = `${toFaDigits(len)} / ${toFaDigits(max)}`;
      };

      input.addEventListener('input', update);
      update(); // init
    });
  }

  /* --------------------------------------
   * 2) ورودی فایل + اعتبارسنجی
   * ------------------------------------ */
  function initFileInput() {
    const fileInput = $('#id_service_image');
    if (!fileInput) return;

    const wrapper = fileInput.closest('.file-input-wrapper') || fileInput.parentElement;
    const fileNameEl = wrapper?.querySelector('.file-name');
    const pickBtn = wrapper?.querySelector('.file-input-btn');

    // کلیک روی دکمه انتخاب تصویر → باز شدن فایل‌چوُزر
    if (pickBtn) {
      pickBtn.type = 'button';
      pickBtn.addEventListener('click', () => fileInput.click());
    }

    fileInput.addEventListener('change', () => {
      if (!fileNameEl) return;

      if (fileInput.files && fileInput.files.length > 0) {
        const file = fileInput.files[0];
        fileNameEl.textContent = file.name;

        const sizeMB = file.size / 1024 / 1024;
        const typeOk = ['image/jpeg', 'image/jpg', 'image/png'].includes(file.type);
        let err = '';

        if (!typeOk) err = 'فرمت فایل باید JPG یا PNG باشد.';
        if (sizeMB > 5) err = 'حجم فایل باید کمتر از ۵ مگابایت باشد.';

        if (err) {
          alert(err);
          fileInput.value = '';
          fileNameEl.textContent = '';
        }
      } else {
        fileNameEl.textContent = '';
      }
    });
  }

  /* --------------------------------------
   * 3) Select2 (اختیاری، اگر لود شده باشد)
   * ------------------------------------ */
  function initSelect2() {
    // نیازمند jQuery + Select2
    if (typeof window.$ !== 'undefined' && window.$.fn && window.$.fn.select2) {
      try {
        window.$('#id_service_group').select2({
          placeholder: 'گروه خدمت را انتخاب نمایید',
          allowClear: true,
          width: '100%',
          dir: 'rtl',
        });
      } catch (e) {
        console.warn('select2 init error:', e);
      }
    }
  }

  /* --------------------------------------
   * 4) مدیریت انتخاب آرایشگران + قیمت‌ها
   * ------------------------------------ */
  function initStylistPricing() {
    const basePriceInput    = $('#id_service_prices');
    const pricesContainer   = $('#stylist-prices-container');
    const stylistCheckboxes = $$('input[name="selected_stylists"]');
    if (!pricesContainer || !basePriceInput || !stylistCheckboxes.length) return;

    const getStylistName = (checkbox) => {
      const lbl = checkbox.closest('.checkbox-label');
      if (lbl) return lbl.textContent.trim();
      const next = checkbox.nextElementSibling;
      return (next ? next.textContent.trim() : checkbox.parentElement.textContent.trim());
    };

    const ensurePriceField = (stylistId, stylistName) => {
      let input = $(`#id_stylist_price_${stylistId}`);
      if (input) return input; // از قبل موجود است (مثلاً از سمت سرور)

      const basePrice = basePriceInput.value || 0;

      const group = document.createElement('div');
      group.className = 'form-group stylist-price';
      group.dataset.stylistId = stylistId;

      const header = document.createElement('div');
      header.className = 'stylist-price-header';
      header.textContent = `قیمت برای ${stylistName}`;

      const wrap = document.createElement('div');
      wrap.className = 'price-input-wrapper';

      input = document.createElement('input');
      input.type = 'number';
      input.name = `stylist_price_${stylistId}`;
      input.id = `id_stylist_price_${stylistId}`;
      input.className = 'form-control';
      input.min = '0';
      input.required = true;
      input.value = basePrice;

      const currency = document.createElement('span');
      currency.className = 'currency-symbol';
      currency.textContent = 'تومان';

      wrap.appendChild(input);
      wrap.appendChild(currency);
      group.appendChild(header);
      group.appendChild(wrap);
      pricesContainer.appendChild(group);

      return input;
    };

    const removePriceField = (stylistId) => {
      const input = $(`#id_stylist_price_${stylistId}`);
      if (!input) return;
      // فیلدهای دارای خطای سرور را حذف نکن
      if (input.classList.contains('is-invalid')) return;
      input.closest('.stylist-price')?.remove();
    };

    const handleSelectionChange = () => {
      stylistCheckboxes.forEach((cb) => {
        const id = cb.value;
        const name = getStylistName(cb);
        if (cb.checked) {
          ensurePriceField(id, name);
        } else {
          removePriceField(id);
        }
      });
    };

    // ست تغییر قیمت پایه → آپدیت فیلدهای ایجادشده‌ی کاربر (نه آنهایی که کاربر دستی تغییرشان داده)
    basePriceInput.addEventListener('change', () => {
      const newBase = basePriceInput.value || 0;
      $$('input[id^="id_stylist_price_"]', pricesContainer).forEach((inp) => {
        if (!inp.dataset.userModified) inp.value = newBase;
      });
    });

    // علامت‌گذاری فیلدهایی که کاربر تغییر داده
    pricesContainer.addEventListener('input', (e) => {
      if (e.target && e.target.matches('input[type="number"]')) {
        e.target.dataset.userModified = 'true';
      }
    });

    // لیسنر تغییر روی چک‌باکس‌ها
    stylistCheckboxes.forEach((cb) => cb.addEventListener('change', handleSelectionChange));

    // init
    handleSelectionChange();
  }

  /* --------------------------------------
   * 5) اعتبارسنجی فرم ارسال (تصویر فقط اگر require-image=true)
   * ------------------------------------ */
  function initFormValidation() {
    const form = $('#serviceForm');
    if (!form) return;

    const requireImage = (form.dataset.requireImage === 'true');

    form.addEventListener('submit', (e) => {
      let isValid = true;
      const errors = [];

      const mark = (el, ok) => {
        if (!el) return;
        if (ok) el.classList.remove('error');
        else el.classList.add('error');
      };

      // فیلدهای الزامی
      const fServiceName = $('#id_service_name');
      const fBasePrice   = $('#id_service_prices');
      const fDuration    = $('#id_duration_minutes');

      if (!fServiceName || !fServiceName.value.trim()) {
        isValid = false; mark(fServiceName, false);
        errors.push('لطفاً نام خدمت را وارد کنید');
      } else mark(fServiceName, true);

      if (!fBasePrice || !String(fBasePrice.value).trim()) {
        isValid = false; mark(fBasePrice, false);
        errors.push('لطفاً قیمت را وارد کنید');
      } else mark(fBasePrice, true);

      if (!fDuration || !String(fDuration.value).trim()) {
        isValid = false; mark(fDuration, false);
        errors.push('لطفاً مدت زمان را وارد کنید');
      } else mark(fDuration, true);

      // گروه خدمت
      const serviceGroup = $('#id_service_group');
      let groupOk = true;
      if (serviceGroup) {
        if (serviceGroup.multiple) {
          groupOk = serviceGroup.selectedOptions && serviceGroup.selectedOptions.length > 0;
        } else {
          groupOk = !!serviceGroup.value;
        }
      }
      if (!groupOk) {
        isValid = false; mark(serviceGroup, false);
        errors.push('لطفاً حداقل یک گروه خدمت انتخاب کنید');
      } else mark(serviceGroup, true);

      // فایل تصویر (فقط اگر ضروری باشد)
      const fileInput = $('#id_service_image');
      if (fileInput && requireImage) {
        if (!fileInput.files || fileInput.files.length === 0) {
          isValid = false;
          fileInput.parentElement?.classList.add('error');
          errors.push('لطفاً یک تصویر برای خدمت انتخاب کنید');
        } else {
          fileInput.parentElement?.classList.remove('error');
          const file = fileInput.files[0];
          const sizeMB = file.size / 1024 / 1024;
          const typeOk = ['image/jpeg', 'image/jpg', 'image/png'].includes(file.type);
          if (!typeOk) { isValid = false; errors.push('فرمت فایل باید JPG یا PNG باشد'); }
          if (sizeMB > 5) { isValid = false; errors.push('حجم فایل باید کمتر از ۵ مگابایت باشد'); }
        }
      }

      // قیمت آرایشگران انتخاب‌شده
      const selectedStylists = $$('input[name="selected_stylists"]:checked');
      selectedStylists.forEach((sty) => {
        const id = sty.value;
        const priceField = $(`#id_stylist_price_${id}`);
        const ok = priceField && String(priceField.value).trim() !== '' && parseInt(priceField.value, 10) >= 0;
        if (!ok) {
          isValid = false;
          priceField?.classList.add('error');
          const name = sty.closest('.checkbox-label')?.textContent.trim() || sty.parentElement.textContent.trim();
          errors.push(`لطفاً قیمت معتبر برای آرایشگر ${name} وارد کنید`);
        } else {
          priceField.classList.remove('error');
        }
      });

      if (!isValid) {
        e.preventDefault();
        alert(errors.join('\n'));
      }
    });
  }

  // Run all initializers
  initCharacterCounters();
  initFileInput();
  initSelect2();
  initStylistPricing();
  initFormValidation();
}
