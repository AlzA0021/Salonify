// static/js/pages/select_datetime.js
// page: select_datetime
export function init() {
  console.debug('[select_datetime] init');

  // ----------------- Helpers -----------------
  function loadScript(url, cb) {
    const s = document.createElement('script');
    s.type = 'text/javascript';
    s.src = url;
    s.onload = cb;
    s.onerror = () => alert('خطا در بارگذاری اسکریپت');
    document.head.appendChild(s);
  }

  // ----------------- One-off styles -----------------
  (function injectOnce(id, css) {
    if (!document.getElementById(id)) {
      const style = document.createElement('style');
      style.id = id;
      style.textContent = css;
      document.head.appendChild(style);
    }
  })('select-datetime-inline-styles', `
    .stylist-option.needs-selection { background-color:#ffe6e6; border-right:3px solid #ff5252; }
    .dropdown-header i.rotate { transform: rotate(180deg); }
    .dropdown-content.show { display:block !important; z-index:1000 !important; }
    .stylist-dropdown { position:relative; }
    .calendar-modal.show { display:block !important; }
  `);

  // ----------------- Calendar modal -----------------
  function setupCalendarIcon() {
    const calendarIcon = document.getElementById('calendarIcon');
    const calendarModal = document.getElementById('calendarModal');
    const modalCloseBtn = document.getElementById('modalCloseBtn');

    if (!calendarIcon || !calendarModal || !modalCloseBtn) {
      console.warn('calendar elements not found');
      return;
    }

    calendarIcon.onclick = (e) => {
      e.preventDefault(); e.stopPropagation();
      calendarModal.classList.add('show');
      calendarModal.style.display = 'block';
      initDatePicker();
    };
    modalCloseBtn.onclick = (e) => {
      e.preventDefault(); e.stopPropagation();
      calendarModal.classList.remove('show');
      calendarModal.style.display = 'none';
    };
    window.addEventListener('click', (e) => {
      if (e.target === calendarModal) {
        calendarModal.classList.remove('show');
        calendarModal.style.display = 'none';
      }
    });
  }

  // ----------------- Dropdown (stylists) -----------------
  function setupStylistDropdown() {
    const stylistOptions = document.querySelectorAll('.stylist-option');
    const dropdown = document.getElementById('stylistDropdownHeader');
    const dropdownContent = document.getElementById('stylistDropdownContent');

    if (!dropdown || !dropdownContent || !stylistOptions.length) return;

    // toggle
    dropdown.onclick = (e) => {
      e.preventDefault(); e.stopPropagation();
      dropdownContent.classList.toggle('show');
      dropdown.querySelector('i')?.classList.toggle('rotate');
    };

    stylistOptions.forEach((option) => {
      option.onclick = (e) => {
        e.preventDefault(); e.stopPropagation();

        try { saveCurrentTabSelections(); } catch {}
        const stylistId = option.getAttribute('data-stylist-id');
        if (!stylistId) return;

        // header update
        try {
          dropdown.innerHTML = '';
          const img = option.querySelector('img');
          if (img) dropdown.appendChild(img.cloneNode(true));
          const nameSpan = document.createElement('span');
          nameSpan.textContent = option.querySelector('span:first-of-type')?.textContent ?? 'آرایشگر';
          dropdown.appendChild(nameSpan);
          const icon = document.createElement('i'); icon.className = 'fa-solid fa-chevron-down';
          dropdown.appendChild(icon);
        } catch {}

        dropdownContent.classList.remove('show');
        dropdown.querySelector('i')?.classList.remove('rotate');

        switchToStylistTab(stylistId);
      };
    });

    // initial show first stylist tab
    const firstId = stylistOptions[0]?.getAttribute('data-stylist-id');
    if (firstId) switchToStylistTab(firstId);

    // click outside to close
    document.addEventListener('click', (e) => {
      if (dropdownContent.classList.contains('show') &&
          !dropdown.contains(e.target) &&
          !dropdownContent.contains(e.target)) {
        dropdownContent.classList.remove('show');
        dropdown.querySelector('i')?.classList.remove('rotate');
      }
    });
  }

  // ----------------- Date picker (Babakhani) -----------------
  function ensurePersianDatepicker(cb) {
    if (typeof jQuery === 'undefined') {
      loadScript('https://code.jquery.com/jquery-3.6.0.min.js', () => ensurePersianDatepicker(cb));
      return;
    }
    if (typeof persianDate === 'undefined') {
      loadScript('https://unpkg.com/persian-date@1.1.0/dist/persian-date.min.js', () => ensurePersianDatepicker(cb));
      return;
    }
    if (!jQuery.fn.persianDatepicker) {
      loadScript('https://unpkg.com/persian-datepicker@1.2.0/dist/js/persian-datepicker.min.js', () => ensurePersianDatepicker(cb));
      return;
    }
    cb && cb();
  }

  function initDatePicker() {
    ensurePersianDatepicker(() => {
      try {
        const $ = window.jQuery;
        try { $('#modalDatePicker').persianDatepicker('destroy'); $('#inlineCalendarContainer').empty(); } catch {}
        $('#inlineCalendarContainer').persianDatepicker({
          inline: true,
          initialValue: false,
          persianDigit: true,
          altField: '#modalDatePicker',
          observer: true,
          autoClose: true,
          onSelect: function (unix) {
            handleDateSelection(unix);
            const calendarModal = document.getElementById('calendarModal');
            if (calendarModal) {
              calendarModal.classList.remove('show');
              calendarModal.style.display = 'none';
            }
          },
        });
      } catch {
        alert('خطا در راه‌اندازی تقویم');
      }
    });
  }

  // ----------------- Days & slots -----------------
  function initializeDayEvents(tabContent) {
    const dayCircles = tabContent.querySelectorAll('.day-circle, .day');
    dayCircles.forEach((day) => {
      day.removeEventListener('click', dayClickHandler);
      day.addEventListener('click', dayClickHandler);
    });

    const selectedDay = tabContent.querySelector('.day-circle[data-selected="true"], .day[data-selected="true"]');
    if (selectedDay) selectedDay.click();
    else dayCircles[0]?.click();
  }

  function dayClickHandler() {
    const parentTab = this.closest('.tab-content');
    if (!parentTab) return;

    parentTab.querySelectorAll('.day-circle, .day').forEach((dc) => {
      dc.classList.remove('active', 'selected');
    });
    this.classList.add('active', 'selected');
    this.setAttribute('data-selected', 'true');

    const stylistId = parentTab.getAttribute('data-stylist-id');
    const selectedDate = this.dataset.date || this.getAttribute('data-date');
    const dayContent = parentTab.querySelector('.day-content') || document.getElementById(`dayContent-${stylistId}`);
    if (!dayContent) return;

    dayContent.innerHTML = '';
    const scheduleScript = document.getElementById(`schedule-${stylistId}`);
    if (!scheduleScript) return;

    let scheduleData;
    const raw = scheduleScript.textContent.trim();
    if (!raw || raw === '{}' || raw === '[]') {
      dayContent.innerHTML = '<div class="fully-booked-msg"><i class="fa-solid fa-circle-xmark"></i>هیچ سانسی برای این تاریخ موجود نیست</div>';
      updateFinalizeButtonState();
      return;
    }
    try { scheduleData = JSON.parse(raw); } catch {
      dayContent.innerHTML = '<div class="error-message">خطا در تجزیه داده‌های زمان‌بندی</div>';
      updateFinalizeButtonState();
      return;
    }

    if (Array.isArray(scheduleData)) {
      const slots = scheduleData.filter((it) => it.date === selectedDate || (it.datetime && it.datetime.startsWith(selectedDate)));
      if (slots.length) displayTimeSlots(dayContent, slots);
      else dayContent.innerHTML = '<div class="fully-booked-msg"><i class="fa-solid fa-circle-xmark"></i>هیچ سانسی برای این تاریخ موجود نیست</div>';
    } else if (typeof scheduleData === 'object') {
      const slots = scheduleData[selectedDate] || [];
      if (slots.length) displayTimeSlots(dayContent, slots);
      else dayContent.innerHTML = '<div class="fully-booked-msg"><i class="fa-solid fa-circle-xmark"></i>هیچ سانسی برای این تاریخ موجود نیست</div>';
    } else {
      dayContent.innerHTML = '<div class="error-message">فرمت داده‌های زمان‌بندی نامعتبر است</div>';
    }

    updateFinalizeButtonState();
  }

  function displayTimeSlots(container, scheduleItems) {
    if (!Array.isArray(scheduleItems) || !scheduleItems.length) {
      container.innerHTML = '<div class="fully-booked-msg"><i class="fa-solid fa-circle-xmark"></i>هیچ سانسی برای این تاریخ موجود نیست</div>';
      return;
    }

    const wrap = document.createElement('div');
    wrap.className = 'time-slots';

    const first = scheduleItems[0];
    if (first.start_time && first.end_time) {
      // Generate slots by 60 minutes (can be customized)
      const duration = 60;
      const [sh, sm] = first.start_time.split(':').map(Number);
      let [eh, em] = first.end_time.split(':').map(Number);
      if (eh === 0 && em === 0) eh = 24;

      const startTotal = sh * 60 + sm;
      const endTotal = eh * 60 + em;

      const gens = [];
      for (let m = startTotal; m <= endTotal - duration; m += duration) {
        const sH = String(Math.floor(m / 60)).padStart(2, '0');
        const sM = String(m % 60).padStart(2, '0');
        const eM = m + duration;
        const eH = String(Math.floor(eM / 60)).padStart(2, '0');
        const eMM = String(eM % 60).padStart(2, '0');
        gens.push({ start_time: `${sH}:${sM}`, end_time: `${eH}:${eMM}`, date: first.date });
      }

      gens.forEach((slot) => {
        const el = document.createElement('div');
        el.className = 'time-slot';
        el.textContent = `${slot.start_time} - ${slot.end_time}`;
        el.dataset.time = `${slot.date || first.date}T${slot.start_time}`;
        el.addEventListener('click', function () {
          wrap.querySelectorAll('.time-slot').forEach((s) => s.classList.remove('selected', 'active'));
          this.classList.add('selected'); this.dataset.selected = 'true';

          const tabContent = container.closest('.tab-content');
          const d = slot.date || first.date;
          tabContent?.querySelectorAll('.day-circle, .day').forEach((day) => {
            if (day.getAttribute('data-date') === d) {
              day.classList.add('selected'); day.dataset.selected = 'true';
            }
          });

          updateFinalizeButtonState();
          autoSwitchToNextStylist(tabContent);
        });
        wrap.appendChild(el);
      });
    } else {
      // use datetime/time as-is
      scheduleItems.forEach((item) => {
        const el = document.createElement('div');
        el.className = 'time-slot';
        let text = '', dt = '';
        if (item.datetime) {
          text = item.datetime.split('T')[1];
          dt = item.datetime;
        } else if (item.time) {
          text = item.time;
          dt = `${item.date}T${item.time}`;
        } else {
          text = 'Unknown';
        }
        el.textContent = text;
        el.dataset.time = dt;
        el.addEventListener('click', function () {
          wrap.querySelectorAll('.time-slot').forEach((s) => s.classList.remove('selected', 'active'));
          this.classList.add('selected'); this.dataset.selected = 'true';

          const tabContent = container.closest('.tab-content');
          const dp = this.dataset.time?.split('T')[0];
          if (dp) {
            tabContent?.querySelectorAll('.day-circle, .day').forEach((day) => {
              if (day.getAttribute('data-date') === dp) {
                day.classList.add('selected'); day.dataset.selected = 'true';
              }
            });
          }

          updateFinalizeButtonState();
          autoSwitchToNextStylist(tabContent);
        });
        wrap.appendChild(el);
      });
    }

    container.appendChild(wrap);
  }

  function autoSwitchToNextStylist(currentTab) {
    if (!currentTab) return;
    const currentId = currentTab.getAttribute('data-stylist-id');
    const allTabs = document.querySelectorAll('.tab-content');
    let found = false, nextId = null;
    allTabs.forEach((tab) => {
      const id = tab.getAttribute('data-stylist-id');
      if (found && !nextId) nextId = id;
      if (id === currentId) found = true;
    });
    if (nextId) setTimeout(() => switchToStylistTab(nextId), 300);
  }

  // ----------------- Date selection from modal -----------------
  function handleDateSelection(selectedDate) {
    let formatted = '';
    try {
      if (typeof selectedDate === 'number') {
        const p = new persianDate(selectedDate);
        formatted = `${p.year()}-${String(p.month()).padStart(2,'0')}-${String(p.date()).padStart(2,'0')}`;
      } else if (typeof selectedDate === 'object' && selectedDate?.getTime) {
        const p = new persianDate(selectedDate);
        formatted = `${p.year()}-${String(p.month()).padStart(2,'0')}-${String(p.date()).padStart(2,'0')}`;
      } else if (typeof selectedDate === 'string') {
        formatted = selectedDate;
      } else {
        alert('فرمت تاریخ نامعتبر است.'); return;
      }
    } catch { alert('خطا در پردازش تاریخ.'); return; }

    const active = document.querySelector('.tab-content.active');
    if (!active) return;

    const targetDay = active.querySelector(`.day-circle[data-date="${formatted}"]`);
    const calendarModal = document.getElementById('calendarModal');

    if (targetDay) {
      targetDay.scrollIntoView({ behavior: 'smooth', inline:'center' });
      targetDay.click();
      calendarModal?.classList.remove('show');
      if (calendarModal) calendarModal.style.display = 'none';
      return;
    }

    // fallback: match by day & month if same month grid
    const [yy, mm, dd] = formatted.split('-').map(Number);
    let found = null;
    active.querySelectorAll('.day-circle').forEach((d) => {
      const [y2, m2, d2] = (d.getAttribute('data-date') || '').split('-').map(Number);
      if (!found && d2 === dd && m2 === mm) found = d;
    });

    if (found) {
      found.scrollIntoView({ behavior:'smooth', inline:'center' });
      found.click();
      calendarModal?.classList.remove('show');
      if (calendarModal) calendarModal.style.display = 'none';
    } else {
      alert('این تاریخ در لیست روزهای موجود نیست!');
    }
  }

  // ----------------- Tab switch & persist -----------------
  function setupTabSelectionPersistence() {
    const stylistOptions = document.querySelectorAll('.stylist-option');
    stylistOptions.forEach((option) => {
      option.addEventListener('click', () => {
        saveCurrentTabSelections();
        const id = option.getAttribute('data-stylist-id');
        switchToStylistTab(id);
      });
    });
  }

  function saveCurrentTabSelections() {
    const active = document.querySelector('.tab-content.active');
    if (!active) return;
    active.querySelector('.day-circle.selected, .day-circle.active, .day.selected, .day.active')
      ?.setAttribute('data-selected', 'true');
    active.querySelector('.time-slot.selected, .time-slot.active')
      ?.setAttribute('data-selected', 'true');
  }

  function switchToStylistTab(stylistId) {
    const allTabs = document.querySelectorAll('.tab-content');
    allTabs.forEach((t) => { t.classList.remove('active'); t.style.display = 'none'; });

    const target = document.getElementById(`tab-${stylistId}`);
    if (!target) {
      // fallback show first
      const first = allTabs[0];
      first?.classList.add('active'); if (first) first.style.display = 'block';
      return;
    }

    target.classList.add('active'); target.style.display = 'block';

    // ensure first day loaded if nothing selected
    const hasSelected = target.querySelector('.day-circle.selected, .day-circle.active, .day.selected, .day.active');
    if (!hasSelected) {
      const firstDay = target.querySelector('.day-circle');
      firstDay?.click();
    }

    // update header (optional)
    try {
      const option = document.querySelector(`.stylist-option[data-stylist-id="${stylistId}"]`);
      const header = document.getElementById('stylistDropdownHeader');
      if (option && header) {
        const img = option.querySelector('img');
        const name = option.querySelector('span:first-of-type')?.textContent || 'آرایشگر';
        header.innerHTML = '';
        if (img) header.appendChild(img.cloneNode(true));
        const span = document.createElement('span'); span.textContent = name; header.appendChild(span);
        const icon = document.createElement('i'); icon.className = 'fa-solid fa-chevron-down'; header.appendChild(icon);
      }
    } catch {}
  }

  function highlightStylistInDropdown(stylistId, highlight = true) {
    const el = document.querySelector(`.stylist-option[data-stylist-id="${stylistId}"]`);
    if (!el) return;
    el.classList.toggle('needs-selection', !!highlight);
  }

  // ----------------- Finalize button -----------------
  function updateFinalizeButtonState() {
    const finalizeButton = document.querySelector('.finalize-button');
    if (!finalizeButton) return;

    const allTabs = document.querySelectorAll('.tab-content');
    let allSelected = true;
    let selectedCount = 0;

    allTabs.forEach((tab) => {
      if (!tab.getAttribute('data-stylist-id')) return;
      const has = tab.querySelector('.time-slot.selected, .time-slot.active');
      if (has) selectedCount++; else allSelected = false;
    });

    if (allSelected && selectedCount > 0) {
      finalizeButton.classList.add('ready');
      if (!finalizeButton.hasAttribute('data-original-text')) {
        finalizeButton.setAttribute('data-original-text', finalizeButton.textContent);
      }
      finalizeButton.textContent = selectedCount > 1
        ? `نهایی کردن انتخاب (${selectedCount} آرایشگر)`
        : 'نهایی کردن انتخاب';
    } else {
      finalizeButton.classList.remove('ready');
      if (finalizeButton.hasAttribute('data-original-text')) {
        finalizeButton.textContent = finalizeButton.getAttribute('data-original-text');
      } else {
        finalizeButton.textContent = 'نهایی کردن انتخاب';
    }
    }
  }

  function finalizeSelection() {
    try {
      const allTabs = document.querySelectorAll('.tab-content');
      const unselected = [];

      // clear highlights
      allTabs.forEach((tab) => {
        tab.classList.remove('needs-selection');
        const id = tab.getAttribute('data-stylist-id');
        if (id) highlightStylistInDropdown(id, false);
      });

      // validate
      allTabs.forEach((tab) => {
        const id = tab.getAttribute('data-stylist-id');
        if (!id) return;
        const hasSelected = tab.querySelector('.time-slot.selected, .time-slot.active');
        if (!hasSelected) {
          let name = 'آرایشگر';
          const opt = document.querySelector(`.stylist-option[data-stylist-id="${id}"]`);
          const nameEl = opt?.querySelector('span:first-of-type');
          if (nameEl) name = nameEl.textContent.trim();
          unselected.push({ id, name });
          tab.classList.add('needs-selection');
          highlightStylistInDropdown(id, true);
        }
      });

      if (unselected.length) {
        const msg = 'لطفاً برای آرایشگرهای زیر زمان را انتخاب کنید:\n\n' +
          unselected.map((s, i) => `${i + 1}. ${s.name}`).join('\n');
        alert(msg);
        switchToStylistTab(unselected[0].id);
        return false;
      }

      // collect data
      const stylistsData = [];
      allTabs.forEach((tab) => {
        const id = tab.getAttribute('data-stylist-id');
        if (!id) return;
        const day = tab.querySelector('.day-circle.selected, .day-circle.active, .day.selected, .day.active');
        const time = tab.querySelector('.time-slot.selected, .time-slot.active');
        if (day && time) {
          const dateStr = day.getAttribute('data-date');
          let timeVal = time.getAttribute('data-time') || '';
          if (timeVal && !timeVal.includes('T')) {
            timeVal = `${dateStr}T${timeVal}`;
          }
          let name = 'آرایشگر';
          const opt = document.querySelector(`.stylist-option[data-stylist-id="${id}"]`);
          const n = opt?.querySelector('span:first-of-type');
          if (n) name = n.textContent.trim();

          stylistsData.push({
            stylist_id: id,
            selected_date: dateStr,
            selected_time: (timeVal.includes('T') ? timeVal.split('T')[1] : timeVal),
            stylist_name: name,
          });
        }
      });

      // salon id
      let salonId = '';
      try {
        const urlParams = new URLSearchParams(window.location.search);
        salonId = urlParams.get('salon_id') || document.getElementById('current_salon_id')?.value || '';
      } catch {}

      // service selections (from url param)
      let servicesData = '{}';
      try {
        const urlParams = new URLSearchParams(window.location.search);
        servicesData = urlParams.get('selections') || '{}';
      } catch {}

      // build & submit form
      let form = document.getElementById('bookingForm');
      if (!form) {
        form = document.createElement('form');
        form.id = 'bookingForm';
        form.method = 'POST';
        form.action = '/orders/reservation_preview/';
        document.body.appendChild(form);
      } else {
        form.innerHTML = '';
      }

      function addField(name, value) {
        const input = document.createElement('input');
        input.type = 'hidden'; input.name = name; input.value = value; form.appendChild(input);
      }

      // CSRF
      const csrf = window.CSRF_TOKEN || document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
      if (csrf) addField('csrfmiddlewaretoken', csrf);
      if (salonId) addField('salon_id', salonId);
      addField('stylists_data', JSON.stringify(stylistsData));
      addField('service_selections', servicesData);

      const count = stylistsData.length;
      alert(`زمان‌های انتخابی برای ${count > 1 ? `${count} آرایشگر` : 'آرایشگر'} ثبت شد. در حال انتقال...`);
      setTimeout(() => {
        try { form.submit(); } catch { alert('خطا در ارسال فرم.'); }
      }, 100);

      return true;
    } catch (e) {
      console.error('finalizeSelection error:', e);
      alert('خطا در پردازش انتخاب‌ها.');
      return false;
    }
  }

  // expose finalizeSelection for button onclick (template)
  window.finalizeSelection = finalizeSelection;

  // ----------------- Bootstrapping -----------------
  setupStylistDropdown();
  setupCalendarIcon();
  setupTabSelectionPersistence();

  // attach day events for all tabs
  document.querySelectorAll('.tab-content').forEach((tab) => {
    initializeDayEvents(tab);
  });

  // mark tabs needing selection
  document.querySelectorAll('.tab-content').forEach((tab) => {
    const has = tab.querySelector('.time-slot.selected, .time-slot.active');
    if (!has) {
      tab.classList.add('needs-selection');
      const id = tab.getAttribute('data-stylist-id');
      if (id) highlightStylistInDropdown(id, true);
    }
  });

  updateFinalizeButtonState();
}
