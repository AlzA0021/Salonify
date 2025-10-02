// static/js/pages/dashboard_add_stylist.js
// page: dashboard_add_stylist
export function init() {
  console.debug('[dashboard_add_stylist] init');

  // -----------------------------
  // State
  // -----------------------------
  const servicesState = {
    selectedServices: new Set(),   // مجموعه آیدی سرویس‌های انتخاب‌شده (string)
    activeCategory: 'all',         // فیلتر دسته فعلی
    searchQuery: '',               // جستجو
    allServicesData: [],           // کش داده‌ها برای جلوگیری از fetch مجدد
    servicesFetched: false,        // آیا دریافت شده‌اند؟
  };

  // -----------------------------
  // Cached DOM refs (پر می‌شوند در بوت)
  // -----------------------------
  let servicesListContainer = null;
  let servicesSearchInput = null;
  let servicesCategoryFiltersContainer = null;
  let selectedServicesCountElement = null;
  let selectedServicesHiddenInput = null;

  // ابزار
  const $  = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));
  const toFaDigits = (val) => String(val).replace(/\d/g, (d) => '۰۱۲۳۴۵۶۷۸۹'[d]);

  // =================================================================================
  // Profile Image Upload
  // =================================================================================
  function showImagePreview(input) {
    const previewImageElement = /** @type {HTMLImageElement|null} */ ($('#preview_image'));
    const avatarIconPlaceholderElement = $('#avatar_icon_placeholder');

    if (input?.files?.[0]) {
      const reader = new FileReader();
      reader.onload = (event) => {
        if (previewImageElement && event.target?.result) {
          previewImageElement.src = String(event.target.result);
          previewImageElement.style.display = 'block';
        }
        if (avatarIconPlaceholderElement) avatarIconPlaceholderElement.style.display = 'none';
      };
      reader.readAsDataURL(input.files[0]);
    } else {
      // اگر فایل انتخاب نشده (حالت اولیه/پاک کردن)
      if (window.appConfig?.hasExistingImage && window.appConfig?.existingImageUrl) {
        if (previewImageElement) {
          previewImageElement.src = window.appConfig.existingImageUrl;
          previewImageElement.style.display = 'block';
        }
        if (avatarIconPlaceholderElement) avatarIconPlaceholderElement.style.display = 'none';
      } else {
        if (previewImageElement) {
          previewImageElement.src = '#';
          previewImageElement.style.display = 'none';
        }
        if (avatarIconPlaceholderElement) avatarIconPlaceholderElement.style.display = 'flex';
      }
    }
  }

  function initializeProfileImageUpload() {
    const profileImageInputElement = /** @type {HTMLInputElement|null} */ (
      document.getElementById(window.appConfig?.profileImageInputId || 'id_profile_image')
    );
    const initialPreviewImageElement = /** @type {HTMLImageElement|null} */ ($('#preview_image'));
    const initialAvatarIconPlaceholderElement = $('#avatar_icon_placeholder');

    if (profileImageInputElement) {
      profileImageInputElement.addEventListener('change', function () {
        showImagePreview(this);
      });
    }

    const hasServerSideImage = window.appConfig?.hasExistingImage === true;
    const existingImageUrl = window.appConfig?.existingImageUrl;

    if (hasServerSideImage && existingImageUrl && initialPreviewImageElement) {
      initialPreviewImageElement.src = existingImageUrl;
      initialPreviewImageElement.style.display = 'block';
      if (initialAvatarIconPlaceholderElement) {
        initialAvatarIconPlaceholderElement.style.display = 'none';
      }
    } else if (profileImageInputElement?.files?.length) {
      showImagePreview(profileImageInputElement);
    } else {
      if (initialPreviewImageElement) {
        initialPreviewImageElement.src = '#';
        initialPreviewImageElement.style.display = 'none';
      }
      if (initialAvatarIconPlaceholderElement) {
        initialAvatarIconPlaceholderElement.style.display = 'flex';
      }
    }
  }

  // =================================================================================
  // Utils: duration & price format
  // =================================================================================
  function formatDuration(minutes) {
    if (minutes === null || minutes === undefined || minutes === 0) return '';
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    let durationStr = '';
    if (hours > 0) durationStr += `${new Intl.NumberFormat('fa-IR').format(hours)} ساعت`;
    if (remainingMinutes > 0) {
      if (hours > 0) durationStr += ' و ';
      durationStr += `${new Intl.NumberFormat('fa-IR').format(remainingMinutes)} دقیقه`;
    }
    return durationStr;
  }

  function formatPrice(price) {
    if (price === null || price === undefined || price === 0) return 'رایگان';
    return `${new Intl.NumberFormat('fa-IR').format(price)} تومان`;
  }

  // =================================================================================
  // Tabs
  // =================================================================================
  function initializeTabs() {
    const tabs = $$('.tab');
    const tabContents = $$('.tab-content');

    tabs.forEach((tab) => {
      tab.addEventListener('click', function () {
        const targetId = this.getAttribute('data-tab');

        tabs.forEach((t) => t.classList.remove('active'));
        tabContents.forEach((c) => c.classList.remove('active'));

        this.classList.add('active');
        if (targetId) {
          const targetContent = document.getElementById(targetId);
          if (targetContent) {
            targetContent.classList.add('active');
            if (targetId === 'services') checkAndLoadServices();
          }
        }
      });
    });
  }

  function activateTabFromHash() {
    const hash = window.location.hash;
    let activated = false;

    if (hash && hash.length > 1) {
      const id = hash.substring(1);
      const tab = document.querySelector(`.tab[data-tab="${id}"]`);
      if (tab) { tab.dispatchEvent(new Event('click')); activated = true; }
    }

    if (!activated) {
      const anyActive = document.querySelector('.tab.active');
      if (!anyActive) {
        const first = document.querySelector('.tab');
        first?.dispatchEvent(new Event('click'));
      }
    }
  }

  // =================================================================================
  // Flatpickr
  // =================================================================================
  function initializeDatePickers() {
    if (typeof window.flatpickr === 'undefined') {
      console.warn('Flatpickr not loaded.');
      return;
    }
    const fp = window.flatpickr;
    fp.localize(fp.l10ns.fa);

    const dateConfig = {
      dateFormat: 'Y-m-d',
      disableMobile: true,
      locale: 'fa',
      altInput: true,
      altFormat: 'j F Y',
      allowInput: false,
      onReady: (selectedDates, dateStr, instance) => {
        if (instance.altInput) {
          instance.altInput.placeholder = 'تاریخ را انتخاب کنید';
          instance.altInput.classList.add('flatpickr-alt-input');
          instance.altInput.setAttribute('readonly', 'readonly');
        }
      },
    };

    document
      .querySelectorAll('input[name="start_date"], input[name="end_date"]')
      .forEach((el) => {
        if (!(el instanceof HTMLInputElement)) return;
        const picker = fp(el, dateConfig);
        const iconId = `${el.id}_icon`;
        const dateIcon = document.getElementById(iconId);

        const openPicker = (e) => { e.stopPropagation(); picker.open(); };
        if (dateIcon) dateIcon.addEventListener('click', openPicker);
        if (picker.altInput) {
          picker.altInput.addEventListener('click', openPicker);
          el.classList.add('flatpickr-hidden-input');
        }
      });
  }

  // =================================================================================
  // Color selector
  // =================================================================================
  function initializeColorSelector() {
    const colorDots = $$('.color-dot');
    const colorInput = /** @type {HTMLInputElement|null} */ (document.querySelector('input[name="calendar_color"]'));

    if (colorDots.length && colorInput) {
      let initialColor = window.appConfig?.stylistCalendarColor || colorInput.value;
      if (!initialColor) {
        const initiallySelected = document.querySelector('.color-dot.selected') || colorDots[0];
        initialColor = initiallySelected?.getAttribute('data-color') || '';
      }
      if (initialColor) colorInput.value = initialColor;

      colorDots.forEach((dot) => {
        dot.classList.toggle('selected', dot.getAttribute('data-color') === initialColor);
        dot.addEventListener('click', () => {
          colorDots.forEach((d) => d.classList.remove('selected'));
          dot.classList.add('selected');
          colorInput.value = dot.getAttribute('data-color') || '';
        });
      });
    }
  }

  // =================================================================================
  // Services: fetch + render
  // =================================================================================
  function checkAndLoadServices() {
    if (!servicesListContainer) servicesListContainer = document.getElementById('servicesList');
    if (!servicesListContainer) { console.error("Element '#servicesList' not found."); return; }

    if (!servicesState.servicesFetched) {
      fetchServicesData();
    } else {
      populateServicesList(servicesState.allServicesData);
    }
  }

  async function fetchServicesData() {
    if (!servicesListContainer) return;
    servicesListContainer.innerHTML =
      '<div class="loading-message text-center text-gray-500 py-5">در حال بارگذاری خدمات...</div>';

    try {
      const url = window.appConfig?.servicesListUrl;
      if (!url) throw new Error('URL لیست خدمات در appConfig تعریف نشده است.');

      const res = await fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
      if (!res.ok) throw new Error(`خطای شبکه: ${res.status}`);

      const data = await res.json();
      let services = [];
      if (data && Array.isArray(data.services)) services = data.services;
      else if (Array.isArray(data)) services = data;
      else throw new Error('فرمت داده‌های دریافتی از سرور نامعتبر است.');

      servicesState.allServicesData = services;
      servicesState.servicesFetched = true;
      populateServicesList(services);
    } catch (err) {
      console.error('خطا در دریافت/پردازش خدمات:', err);
      servicesState.servicesFetched = false;
      servicesListContainer.innerHTML =
        `<div class="error-message text-center text-red-500 py-5">خطا در بارگذاری خدمات. (${err.message || 'خطای ناشناخته'})</div>`;
    }
  }

  function createServiceItemHTML(service) {
    const serviceIdStr = String(service.id);
    const isSelected = servicesState.selectedServices.has(serviceIdStr);

    const duration = service.duration_minutes ?? service.duration;
    const name = service.service_title ?? service.name;
    const price = service.price;
    const groupId = service.group_id?.toString() ?? service.groupId?.toString() ?? 'other';

    const durationText = formatDuration(duration);
    const itemSelectedClasses = isSelected ? 'selected bg-blue-50' : '';
    const checkboxCheckedClass = isSelected ? 'checked' : '';
    const checkboxTailwindClasses = isSelected ? 'border-blue-500 bg-blue-500' : 'border-gray-300';

    return `
      <div class="service-item ${itemSelectedClasses}"
           data-service-id="${serviceIdStr}"
           data-group-id="${groupId}"
           data-service-name="${(name || '').toLowerCase()}">
        <div class="service-content flex items-center justify-between p-3 hover:bg-gray-100 cursor-pointer border-b border-gray-200 last:border-b-0">
          <div class="service-checkbox-container flex items-center mr-3">
            <div class="service-checkbox w-5 h-5 border-2 rounded-sm flex items-center justify-center ${checkboxTailwindClasses} ${checkboxCheckedClass}" data-service-id="${serviceIdStr}">
              <i class="fas fa-check text-white text-xs"></i>
            </div>
          </div>
          <div class="service-info flex-grow">
            <div class="service-name font-medium text-gray-800">${name || 'سرویس بدون نام'}</div>
            ${durationText ? `<div class="service-duration text-xs text-gray-500">${durationText}</div>` : ''}
          </div>
          <div class="service-price text-sm text-gray-700 whitespace-nowrap">${formatPrice(price)}</div>
        </div>
      </div>
    `;
  }

  function populateServicesList(services) {
    if (!servicesListContainer) return;

    if (!services || !services.length) {
      servicesListContainer.innerHTML =
        '<div class="text-center text-gray-500 py-5">هیچ خدمتی برای نمایش یافت نشد.</div>';
      updateSelectedVisuals();
      return;
    }

    const grouped = services.reduce((acc, s) => {
      const gid = s.group_id?.toString() ?? s.groupId?.toString() ?? 'other';
      const title = s.group_title || 'سایر خدمات';
      if (!acc[gid]) acc[gid] = { id: gid, title, services: [] };
      acc[gid].services.push(s);
      return acc;
    }, {});

    servicesListContainer.innerHTML = Object.values(grouped)
      .map((g) => {
        if (!g.services?.length) return '';
        return `
          <div class="service-group mb-4 border rounded-lg overflow-hidden" data-category="${g.id}" data-group-id="${g.id}">
            <div class="group-header bg-gray-100 p-3 border-b flex items-center justify-between cursor-pointer">
              <div class="flex items-center">
                <div class="group-checkbox-container mr-3">
                  <div class="group-checkbox w-5 h-5 border-2 border-gray-400 rounded-sm flex items-center justify-center" data-group-id="${g.id}">
                    <i class="fas fa-check text-white text-xs"></i>
                    <i class="fas fa-minus text-white text-xs"></i>
                  </div>
                </div>
                <span class="group-title-text font-semibold text-gray-700">${g.title}</span>
              </div>
              <span class="group-count bg-gray-2 00 text-gray-600 text-xs font-medium px-2 py-0.5 rounded-full">
                ${new Intl.NumberFormat('fa-IR').format(g.services.length)}
              </span>
            </div>
            <div class="service-items-container bg-white">
              ${g.services.map(createServiceItemHTML).join('')}
            </div>
          </div>
        `;
      })
      .join('');

    attachServiceInteractionListeners();
    filterServices();
  }

  // =================================================================================
  // Filtering
  // =================================================================================
  function filterServices() {
    if (!servicesListContainer) return;

    const groups = servicesListContainer.querySelectorAll('.service-group');
    const q = servicesState.searchQuery.toLowerCase().trim();
    const activeCat = servicesState.activeCategory;
    let anyVisible = false;

    groups.forEach((groupEl) => {
      if (!(groupEl instanceof HTMLElement)) return;
      const gid = groupEl.dataset.groupId;
      const items = groupEl.querySelectorAll('.service-item');
      let visibleInGroup = 0;

      const catOk = activeCat === 'all' || gid === activeCat;

      if (catOk) {
        items.forEach((item) => {
          if (!(item instanceof HTMLElement)) return;
          const name = (item.dataset.serviceName || '').toLowerCase();
          const match = q === '' || name.includes(q);
          item.style.display = match ? 'block' : 'none';
          if (match) visibleInGroup++;
        });

        const showGroup = visibleInGroup > 0;
        groupEl.style.display = showGroup ? 'block' : 'none';
        if (showGroup) anyVisible = true;

        const countEl = groupEl.querySelector('.group-header .group-count');
        if (countEl) countEl.textContent = new Intl.NumberFormat('fa-IR').format(visibleInGroup);
      } else {
        groupEl.style.display = 'none';
      }
    });

    // پیام «یافت نشد»
    servicesListContainer.querySelector('.no-results-message')?.remove();
    if (!anyVisible && servicesState.servicesFetched && servicesState.allServicesData.length) {
      const msg = document.createElement('div');
      msg.className = 'no-results-message text-center text-gray-500 py-5';
      msg.textContent = 'هیچ خدمتی با این جستجو یا در این دسته یافت نشد.';
      servicesListContainer.appendChild(msg);
    }

    updateSelectedVisuals();
  }

  function attachCategoryFilterListeners() {
    if (!servicesCategoryFiltersContainer) return;
    const btns = servicesCategoryFiltersContainer.querySelectorAll('.services-category-btn');
    btns.forEach((b) => {
      b.removeEventListener('click', handleCategoryFilterClick);
      b.addEventListener('click', handleCategoryFilterClick);
    });

    let foundActive = false;
    btns.forEach((b) => {
      if (b.classList.contains('active')) {
        servicesState.activeCategory = b.dataset.category || 'all';
        foundActive = true;
      }
    });
    if (!foundActive) {
      const allBtn = servicesCategoryFiltersContainer.querySelector('.services-category-btn[data-category="all"]');
      if (allBtn) { allBtn.classList.add('active'); servicesState.activeCategory = 'all'; }
    }
  }

  function handleCategoryFilterClick(e) {
    const btn = /** @type {HTMLElement} */ (e.currentTarget);
    const cat = btn.dataset.category || 'all';
    servicesCategoryFiltersContainer
      ?.querySelectorAll('.services-category-btn')
      .forEach((b) => b.classList.remove('active'));
    btn.classList.add('active');
    servicesState.activeCategory = cat;
    filterServices();
  }

  // =================================================================================
  // Item interactions
  // =================================================================================
  function attachServiceInteractionListeners() {
    if (!servicesListContainer) return;

    servicesListContainer.addEventListener('click', (e) => {
      const serviceItem = e.target.closest('.service-item');
      const serviceCheckboxContainer = e.target.closest('.service-checkbox-container');
      const groupHeaderCheckboxContainer = e.target.closest('.group-header .group-checkbox-container');

      if (serviceCheckboxContainer) {
        const cb = serviceCheckboxContainer.querySelector('.service-checkbox');
        const id = cb?.dataset.serviceId;
        if (id) { e.stopPropagation(); toggleServiceSelection(id); }
      } else if (serviceItem) {
        const id = serviceItem.dataset.serviceId;
        if (id) toggleServiceSelection(id);
      } else if (groupHeaderCheckboxContainer) {
        const gcb = groupHeaderCheckboxContainer.querySelector('.group-checkbox');
        const gid = gcb?.dataset.groupId;
        if (gid) { e.stopPropagation(); toggleServiceGroupSelection(gid); }
      }
    });
  }

  function toggleServiceSelection(serviceId) {
    const id = serviceId.toString();
    const item = servicesListContainer?.querySelector(`.service-item[data-service-id="${id}"]`);
    const cbDiv = item?.querySelector('.service-checkbox');

    if (servicesState.selectedServices.has(id)) {
      servicesState.selectedServices.delete(id);
      item?.classList.remove('selected', 'bg-blue-50');
      cbDiv?.classList.remove('checked', 'border-blue-500', 'bg-blue-500');
      cbDiv?.classList.add('border-gray-300');
    } else {
      servicesState.selectedServices.add(id);
      item?.classList.add('selected', 'bg-blue-50');
      cbDiv?.classList.add('checked', 'border-blue-500', 'bg-blue-500');
      cbDiv?.classList.remove('border-gray-300');
    }
    updateSelectedVisuals();
  }

  function toggleServiceGroupSelection(groupId) {
    if (!servicesListContainer) return;
    const gid = groupId.toString();
    const items = servicesListContainer.querySelectorAll(
      `.service-item[data-group-id="${gid}"]:not([style*="display: none"])`
    );
    if (!items.length) { updateSelectedVisuals(); return; }

    const allSelected = Array.from(items).every((it) => {
      if (!(it instanceof HTMLElement) || !it.dataset.serviceId) return false;
      return servicesState.selectedServices.has(it.dataset.serviceId);
    });

    const shouldSelect = !allSelected;
    items.forEach((it) => {
      if (!(it instanceof HTMLElement) || !it.dataset.serviceId) return;
      const id = it.dataset.serviceId;
      const cbDiv = it.querySelector('.service-checkbox');

      if (shouldSelect) {
        if (!servicesState.selectedServices.has(id)) {
          servicesState.selectedServices.add(id);
          it.classList.add('selected', 'bg-blue-50');
          cbDiv?.classList.add('checked', 'border-blue-500', 'bg-blue-500');
          cbDiv?.classList.remove('border-gray-300');
        }
      } else {
        if (servicesState.selectedServices.has(id)) {
          servicesState.selectedServices.delete(id);
          it.classList.remove('selected', 'bg-blue-50');
          cbDiv?.classList.remove('checked', 'border-blue-500', 'bg-blue-500');
          cbDiv?.classList.add('border-gray-300');
        }
      }
    });

    updateSelectedVisuals();
  }

  function updateSelectedVisuals() {
    // وضعیت چک‌باکس گروه‌ها
    document.querySelectorAll('.group-checkbox').forEach((gcb) => {
      if (!(gcb instanceof HTMLElement) || !servicesListContainer) return;
      const gid = gcb.dataset.groupId;
      const visItems = servicesListContainer.querySelectorAll(
        `.service-item[data-group-id="${gid}"]:not([style*="display: none"])`
      );

      gcb.classList.remove('checked', 'partial', 'border-blue-500', 'bg-blue-500', 'border-blue-300', 'bg-blue-300');
      gcb.classList.add('border-gray-400');

      if (!visItems.length) return;

      const selectedCount = Array.from(visItems).filter((it) => {
        if (!(it instanceof HTMLElement) || !it.dataset.serviceId) return false;
        return servicesState.selectedServices.has(it.dataset.serviceId);
      }).length;

      if (selectedCount === 0) return;
      if (selectedCount === visItems.length) {
        gcb.classList.remove('border-gray-400');
        gcb.classList.add('checked', 'border-blue-500', 'bg-blue-500');
      } else {
        gcb.classList.remove('border-gray-400');
        gcb.classList.add('partial', 'border-blue-300', 'bg-blue-300');
      }
    });

    // شمارش انتخاب‌ها
    const count = servicesState.selectedServices.size;
    if (selectedServicesCountElement) {
      if (count > 0) {
        selectedServicesCountElement.textContent = `${new Intl.NumberFormat('fa-IR').format(count)} خدمت انتخاب شده`;
        selectedServicesCountElement.style.display = 'block';
      } else {
        selectedServicesCountElement.style.display = 'none';
      }
    }

    // ورودی مخفی
    if (selectedServicesHiddenInput) {
      selectedServicesHiddenInput.value = JSON.stringify(Array.from(servicesState.selectedServices));
    }
  }

  // =================================================================================
  // Bootstrap (once DOM is ready; app.js guarantees that)
  // =================================================================================
  // کش المنت‌ها
  servicesListContainer = document.getElementById('servicesList');
  servicesSearchInput = document.getElementById('servicesSearchInput');
  servicesCategoryFiltersContainer = document.getElementById('servicesCategoryFiltersContainer');
  selectedServicesCountElement = document.getElementById('selectedServicesCount');
  selectedServicesHiddenInput = document.getElementById('selectedServicesInput');

  // مقداردهی اولیه selectedServices (ویرایش/ایجاد)
  if (window.appConfig?.stylistServiceIds?.length) {
    servicesState.selectedServices = new Set((window.appConfig.stylistServiceIds || []).map(String));
  } else if (selectedServicesHiddenInput?.value) {
    try {
      const parsed = JSON.parse(selectedServicesHiddenInput.value);
      if (Array.isArray(parsed)) servicesState.selectedServices = new Set(parsed.map(String));
    } catch (e) {
      console.warn('Cannot parse selectedServices from hidden input:', e);
      servicesState.selectedServices = new Set();
    }
  } else {
    servicesState.selectedServices = new Set();
  }

  // Init UI blocks
  initializeProfileImageUpload();
  initializeTabs();
  initializeDatePickers();
  initializeColorSelector();

  // پس از آماده‌سازی تب‌ها
  activateTabFromHash();

  // Search + Filters
  if (servicesListContainer && servicesSearchInput && servicesCategoryFiltersContainer) {
    attachCategoryFilterListeners();
    servicesSearchInput.addEventListener('input', (ev) => {
      const target = /** @type {HTMLInputElement} */ (ev.target);
      servicesState.searchQuery = target.value;
      filterServices();
    });

    // اگر تب خدمات از ابتدا فعال است، بارگذاری/نمایش را تضمین کن
    const activeServicesTab = document.querySelector('.tab.active[data-tab="services"]');
    if (activeServicesTab) checkAndLoadServices();
  } else {
    console.info('Services section DOM not found (maybe hidden on this page).');
  }

  updateSelectedVisuals();

  // در ارسال فرم، ورودی مخفی را به‌روز کن
  const addStylistForm = document.getElementById('addStylistForm');
  if (addStylistForm) {
    addStylistForm.addEventListener('submit', () => {
      updateSelectedVisuals();
      // console.log('Selected services payload:', selectedServicesHiddenInput?.value);
    });
  }
}
