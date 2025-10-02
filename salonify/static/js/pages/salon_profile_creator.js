/* static/js/pages/salon_profile_creator.js (ESM)
 * - Map (Leaflet + OSM) + reverse geocoding
 * - Working hours toggler
 * - Step 6: Gallery upload + "more" menu (set cover / delete)
 * - Step 7: Features selection + tooltips
 * - Step 8: Description counter
 * - Common small UX (back/close buttons, button press effects)
 */

export function init() {
  // ---------- helpers ----------
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));
  const on = (el, ev, fn, opts) => el && el.addEventListener(ev, fn, opts);

  function getCSRFToken() {
    const bodyToken = document.body?.dataset?.csrfToken;
    if (bodyToken) return bodyToken;
    const cfg = $('#js-config');
    if (cfg && cfg.dataset.csrfToken) return cfg.dataset.csrfToken;
    const match = document.cookie.match(/(^|;\s*)csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[2]) : '';
  }

  function btnPressFX() {
    $$('.btn, .continue-btn, .enable-button').forEach((btn) => {
      on(btn, 'mousedown', () => (btn.style.transform = 'scale(0.98)'));
      ['mouseup', 'mouseleave'].forEach((ev) =>
        on(btn, ev, () => (btn.style.transform = 'scale(1)')),
      );
    });
  }

  function goBackSmart(e, fallbackUrl) {
    if (e && (e.button !== undefined) && (e.button !== 0)) return;
    if (e && (e.metaKey || e.ctrlKey)) return;
    e?.preventDefault?.();
    if (history.length > 1) {
      try { history.back(); return; } catch {}
    }
    window.location.assign(fallbackUrl || '/');
  }

  // ---------- Working hours ----------
  function toggleDayInternal(dayNum) {
    const checkbox = $(`#checkbox-${dayNum}`);
    const statusText = $(`#status-${dayNum}`);
    const timeRange = $(`#time-range-${dayNum}`);
    const activeInput = $(`#day-${dayNum}-active`);
    if (!checkbox || !statusText || !timeRange || !activeInput) return;

    const timeInputs = $$('input[type="time"]', timeRange);
    const isOpen = !!checkbox.checked;

    statusText.textContent = isOpen ? 'باز' : 'تعطیل';
    statusText.classList.toggle('open-text', isOpen);
    statusText.classList.toggle('closed-text', !isOpen);
    timeRange.style.opacity = isOpen ? '1' : '0.5';
    activeInput.value = isOpen ? 'true' : 'false';
    timeInputs.forEach((input) => {
      input.disabled = !isOpen;
      input.classList.toggle('disabled', !isOpen);
    });
  }
  if (!window.toggleDay) {
    window.toggleDay = function (dayNum) { toggleDayInternal(dayNum); };
  }
  function initWorkingHoursPage() {
    $$('[id^="checkbox-"]').forEach((cb) => {
      const id = cb.id.replace('checkbox-', '');
      toggleDayInternal(id);
    });
    const fridayCheckbox = $('#checkbox-7');
    if (fridayCheckbox && !fridayCheckbox.checked) toggleDayInternal(7);
  }

  // ---------- Leaflet Map + Reverse geocoding ----------
  function initMapFromElement(mapEl) {
    if (!mapEl) return;
    if (typeof L === 'undefined') {
      console.warn('[salon_profile_creator] Leaflet not found on page.');
      return;
    }

    const latSel = mapEl.dataset.latInput || '#id_latitude, [name="latitude"], #lat-input';
    const lngSel = mapEl.dataset.lngInput || '#id_longitude, [name="longitude"], #lng-input';
    const addressSel = mapEl.dataset.addressInput || '#id_address, [name="address"], #address-input';
    const zoneSel = mapEl.dataset.zoneSelect || '#id_zone, [name="zone"], #form-zone';
    const neighSel = mapEl.dataset.neighborhoodSelect || '#id_neighborhood, [name="neighborhood"], #form-neighborhood';

    const latInput = $(latSel);
    const lngInput = $(lngSel);
    const addressInput = $(addressSel);
    const zoneSelect = $(zoneSel);
    const neighborhoodSelect = $(neighSel);

    const spinner = $('.loading-spinner');
    const label = $('.map-marker-label');

    let defaultLat = 35.6892; // Tehran
    let defaultLng = 51.389;

    if (latInput?.value && lngInput?.value) {
      const pLat = parseFloat(latInput.value);
      const pLng = parseFloat(lngInput.value);
      if (!Number.isNaN(pLat)) defaultLat = pLat;
      if (!Number.isNaN(pLng)) defaultLng = pLng;
    }

    const map = L.map(mapEl.id).setView([defaultLat, defaultLng], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    }).addTo(map);

    const marker = L.marker([defaultLat, defaultLng], { draggable: true }).addTo(map);

    if (latInput?.value && lngInput?.value && label) {
      label.classList.add('active');
      if (addressInput && !addressInput.value) reverseGeocode(defaultLat, defaultLng);
    }

    map.on('click', (e) => {
      marker.setLatLng(e.latlng);
      updateCoordinates(e.latlng.lat, e.latlng.lng);
      reverseGeocode(e.latlng.lat, e.latlng.lng);
    });

    marker.on('dragend', () => {
      const pos = marker.getLatLng();
      updateCoordinates(pos.lat, pos.lng);
      reverseGeocode(pos.lat, pos.lng);
    });

    function updateCoordinates(lat, lng) {
      if (latInput) latInput.value = lat.toFixed(6);
      if (lngInput) lngInput.value = lng.toFixed(6);
      label && label.classList.add('active');
    }

    function reverseGeocode(lat, lng) {
      spinner && spinner.classList.add('active');
      const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=18&addressdetails=1&accept-language=fa`;
      fetch(url)
        .then((r) => r.json())
        .then((data) => {
          if (data?.address) {
            const filtered = formatLocalAddress(data.address);
            if (addressInput) addressInput.value = filtered;
            populateZoneAndNeighborhood(data.address);
          }
        })
        .catch((err) => console.error('Reverse geocoding error:', err))
        .finally(() => spinner && spinner.classList.remove('active'));
    }

    function formatLocalAddress(addressData) {
      const parts = [];
      if (addressData.house_number) parts.push('پلاک ' + addressData.house_number);
      if (addressData.road) parts.push(addressData.road);
      if (addressData.pedestrian) parts.push(addressData.pedestrian);
      if (addressData.neighbourhood) parts.push(addressData.neighbourhood);
      else if (addressData.quarter) parts.push(addressData.quarter);
      if (addressData.suburb) parts.push(addressData.suburb);
      else if (addressData.district) parts.push(addressData.district);
      if (!parts.length) {
        if (addressData.amenity) parts.push('نزدیک ' + addressData.amenity);
        else if (addressData.office) parts.push('نزدیک ' + addressData.office);
        else if (addressData.shop) parts.push('نزدیک ' + addressData.shop);
        else if (addressData.leisure) parts.push('نزدیک ' + addressData.leisure);
      }
      return parts.join('، ');
    }

    function populateZoneAndNeighborhood(addressData) {
      if (!addressData) return;
      const zone = addressData.suburb || addressData.district || addressData.city_district;
      const neighborhood = addressData.neighbourhood || addressData.quarter;

      if (zone && zoneSelect) {
        for (let i = 0; i < zoneSelect.options.length; i++) {
          if (zoneSelect.options[i].text.includes(zone)) {
            zoneSelect.selectedIndex = i;
            zoneSelect.dispatchEvent(new Event('change'));
            break;
          }
        }
      }
      if (neighborhood && neighborhoodSelect) {
        setTimeout(() => {
          for (let i = 0; i < neighborhoodSelect.options.length; i++) {
            if (neighborhoodSelect.options[i].text.includes(neighborhood)) {
              neighborhoodSelect.selectedIndex = i;
              break;
            }
          }
        }, 500);
      }
    }

    zoneSelect && on(zoneSelect, 'change', () => { /* hook for neighborhoods */ });
  }

  function initMapPage() {
    const mapEl = $('#map-container');
    if (mapEl) initMapFromElement(mapEl);
  }

  // ---------- Step 6: Gallery upload ----------
  function initUploadPage() {
    const uploadForm = $('#upload-form');
    const salonImageInput = uploadForm?.querySelector('input[name="salon_image"]');
    const uploadArea = $('#upload-area');
    const addMoreBtn = $('#add-more-btn');
    const continueBtn = $('#continue-btn');
    const imagesContainer = $('.uploaded-images-container');
    const cfg = $('#js-config');
    const csrfToken = getCSRFToken();
    const nextStepUrl = cfg?.dataset?.step7Url || document.body?.dataset?.step7Url;

    if (!uploadForm) return;

    const triggerFileInput = () => salonImageInput && salonImageInput.click();

    uploadArea && on(uploadArea, 'click', triggerFileInput);
    addMoreBtn && on(addMoreBtn, 'click', triggerFileInput);

    salonImageInput &&
      on(salonImageInput, 'change', () => {
        if (salonImageInput.files.length > 0) uploadForm.submit();
      });

    continueBtn &&
      on(continueBtn, 'click', (e) => {
        e.preventDefault();
        if (nextStepUrl) window.location.href = nextStepUrl;
      });

    // ==== "⋮ بیشتر" منو (set cover / delete) ====
    let openMenuEl = null;

    function closeMenus() {
      $$('.image-options-menu').forEach((m) => m.remove());
      openMenuEl = null;
    }

    if (imagesContainer) {
      // باز کردن منو روی کلیک دکمه‌ی ⋮
      on(imagesContainer, 'click', (e) => {
        const btn = e.target.closest('.image-option-btn');
        if (!btn) return;

        e.preventDefault();
        // اگر همین دکمه منوی باز دارد، ببند
        if (openMenuEl && openMenuEl === btn) {
          closeMenus();
          return;
        }
        closeMenus();

        // URLها را از خود دکمه یا کارت والد بخوان
        const card = btn.closest('.uploaded-image, .image-card, .gallery-item');
        const setCoverUrl =
          btn.dataset.setCoverUrl ||
          card?.dataset.setCoverUrl ||
          btn.getAttribute('data-set-cover-url');
        const deleteUrl =
          btn.dataset.deleteUrl ||
          card?.dataset.deleteUrl ||
          btn.getAttribute('data-delete-url');

        // اگر هیچ عملیاتی نبود، منویی نساز
        if (!setCoverUrl && !deleteUrl) return;

        const menu = document.createElement('div');
        menu.className = 'image-options-menu';
        // حداقل استایل‌های لازم (اگر CSS جدا نداری)
        menu.style.position = 'absolute';
        menu.style.minWidth = '160px';
        menu.style.background = '#fff';
        menu.style.border = '1px solid #eee';
        menu.style.borderRadius = '10px';
        menu.style.boxShadow = '0 8px 24px rgba(0,0,0,0.12)';
        menu.style.padding = '6px 0';
        menu.style.zIndex = '9999';

        const makeItem = (text, { danger = false } = {}) => {
          const it = document.createElement('button');
          it.type = 'button';
          it.className = 'menu-item' + (danger ? ' danger' : '');
          it.style.width = '100%';
          it.style.textAlign = 'right';
          it.style.padding = '10px 14px';
          it.style.cursor = 'pointer';
          it.style.background = 'transparent';
          it.style.border = '0';
          it.style.fontSize = '14px';
          it.textContent = text;
          it.addEventListener('mouseenter', () => (it.style.background = '#f7f7f7'));
          it.addEventListener('mouseleave', () => (it.style.background = 'transparent'));
          if (danger) it.style.color = '#e53935';
          return it;
        };

        if (setCoverUrl) {
          const setCoverItem = makeItem('تنظیم به عنوان کاور');
          on(setCoverItem, 'click', () => {
            window.location.href = setCoverUrl; // طبق منطق فعلی‌ات: GET
          });
          menu.appendChild(setCoverItem);
        }
        if (deleteUrl) {
          const delItem = makeItem('حذف', { danger: true });
          on(delItem, 'click', () => {
            if (!confirm('آیا از حذف این تصویر مطمئن هستید؟')) {
              closeMenus();
              return;
            }
            fetch(deleteUrl, {
              method: 'POST',
              headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json',
              },
            })
              .then((res) => {
                if (res.ok) window.location.reload();
                else alert('خطایی در حذف تصویر رخ داد.');
              })
              .catch(() => alert('خطایی در ارتباط با سرور رخ داد.'))
              .finally(closeMenus);
          });
          menu.appendChild(delItem);
        }

        document.body.appendChild(menu);

        // پوزیشن بعد از append (offsetWidth آماده است)
        const r = btn.getBoundingClientRect();
        const mw = menu.offsetWidth || 160;
        const top = window.scrollY + r.bottom + 6; // کمی فاصله
        let left = window.scrollX + r.right - mw; // از سمت راست دکمه
        // جلوگیری از خروج از چپ/راست
        left = Math.max(8, Math.min(left, window.scrollX + window.innerWidth - mw - 8));
        menu.style.top = `${top}px`;
        menu.style.left = `${left}px`;

        openMenuEl = btn;
      });

      // بستن منو با کلیک بیرون
      on(document, 'click', (e) => {
        if (!e.target.closest('.image-options-menu') && !e.target.closest('.image-option-btn')) {
          closeMenus();
        }
      }, true);

      // بستن منو روی اسکرول/ریسایز
      ['scroll', 'resize'].forEach((ev) =>
        on(window, ev, () => { if (openMenuEl) closeMenus(); }, { passive: true })
      );
    }
  }

  // ---------- Step 7: Features + tooltips ----------
  function initFeaturesPage() {
    const items = $$('.feature-item');
    if (!items.length) return;

    const hasPopper = typeof window.Popper !== 'undefined';

    items.forEach((el) => {
      on(el, 'click', (ev) => {
        if (ev.target.closest('input[type="checkbox"]')) return;
        const cb = el.querySelector('input[type="checkbox"]');
        if (cb) cb.checked = !cb.checked;
        el.classList.toggle('selected', !!cb?.checked);
      });

      if (!hasPopper) return;
      const tipText = el.dataset.tooltip || '';
      if (!tipText) return;

      const tip = document.createElement('div');
      tip.className = 'tooltip';
      tip.textContent = tipText;
      document.body.appendChild(tip);

      const instance = Popper.createPopper(el, tip, {
        placement: el.dataset.tooltipPlacement || 'top',
        modifiers: [{ name: 'offset', options: { offset: [0, 8] } }],
      });

      on(el, 'mouseenter', () => { tip.setAttribute('data-show', ''); instance.update(); });
      on(el, 'mouseleave', () => { tip.removeAttribute('data-show'); });
    });
  }

  // ---------- Step 8: Description counter ----------
  function initDescriptionPage() {
    const input = $('#id_description');
    const counter = $('#char-count');
    const btn = $('#continue-btn');
    if (!input || !counter || !btn) return;

    const update = () => {
      const len = input.value.length;
      counter.textContent = String(len);
      btn.disabled = len < 200;
    };
    update();
    on(input, 'input', update);
  }

  // ---------- Common nav ----------
  function initCommonNav() {
    $$('.back-btn, .back-button').forEach((btn) => {
      on(btn, 'click', (e) => {
        if (e.button !== 0 || e.metaKey || e.ctrlKey) return;
        const href = btn.getAttribute('href') || btn.dataset.fallbackUrl || '';
        goBackSmart(e, href);
      });
    });
    $$('.close-btn').forEach((btn) => {
      on(btn, 'click', (e) => {
        const url = btn.dataset.closeUrl || '';
        goBackSmart(e, url);
      });
    });
  }

  // ---------- boot ----------
  initCommonNav();
  btnPressFX();

  if ($('#map-container')) initMapPage();
  if ($('.opening-hours-form') || $$('[id^="checkbox-"]').length) initWorkingHoursPage();
  if ($('#upload-form')) initUploadPage();
  if ($('.items-grid')) initFeaturesPage();
  if ($('#description-form')) initDescriptionPage();
}
