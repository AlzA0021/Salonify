// static/js/pages/scheduled_shifts.js
// page: scheduled_shifts
// نقش: تب‌بندی تیم/هفته، باز/بسته‌کردن آیتم‌ها، اکشن‌های مدال روز، حذف روز، ناوبری

export function init() {
  if (document.body.dataset.page !== 'scheduled_shifts') return;
  console.debug('[scheduled_shifts] init');

  // عناصر اصلی
  const teamTab = document.getElementById('team-tab');
  const weekTab = document.getElementById('week-tab');
  const teamViewContent = document.getElementById('team-view-content');
  const weekViewContent = document.getElementById('week-view-content');
  const mainContainer = document.querySelector('.container');
  const modalOverlay = document.getElementById('dayActionModal');
  const modalCloseButton = document.getElementById('modalCloseButton');
  const modalStylistLogo = document.getElementById('modalStylistLogo');
  const modalStylistName = document.getElementById('modalStylistName');
  const modalSelectedDate = document.getElementById('modalSelectedDate');

  // داده‌های کمکی از تمپلیت (از <meta> و dataset)
  const defaultAvatar =
    document.querySelector('meta[name="default-avatar"]')?.content || '';
  const salonIdFromContainer =
    document.querySelector('.container')?.dataset?.salonId || '';

  function getCsrfToken() {
    const el = document.querySelector('input[name="csrfmiddlewaretoken"]');
    return el ? el.value : '';
  }

  // تب‌ها: تیم / هفته
  if (teamTab && weekTab && teamViewContent && weekViewContent) {
    teamTab.addEventListener('click', function () {
      if (this.classList.contains('active')) return;
      this.classList.add('active');
      weekTab.classList.remove('active');
      teamViewContent.style.display = 'block';
      weekViewContent.style.display = 'none';
    });

    weekTab.addEventListener('click', function () {
      if (this.classList.contains('active')) return;
      this.classList.add('active');
      teamTab.classList.remove('active');
      teamViewContent.style.display = 'none';
      weekViewContent.style.display = 'block';
    });
  }

  // آکاردئون: باز/بسته‌کردن آیتم‌ها با کلیک روی summary
  if (mainContainer) {
    mainContainer.addEventListener('click', function (event) {
      const summary = event.target.closest('.list-item-summary');
      if (summary) {
        const parentItem = summary.closest('.list-item');
        if (parentItem) parentItem.classList.toggle('expanded');
      }
    });
  }

  // بازکردن مدال اکشن‌های روز (از آیتم‌های روز در هر دو نما)
  if (mainContainer && modalOverlay) {
    mainContainer.addEventListener('click', function (event) {
      const clickableItem = event.target.closest(
        '.daily-schedule-item, .week-view-stylist-item',
      );
      if (!clickableItem) return;

      const ds = clickableItem.dataset;
      const stylistId = ds.stylistId;
      const stylistName = ds.stylistName;
      const stylistLogoUrl = ds.stylistLogo;
      const dateIso = ds.dateIso;
      const dateFormatted = ds.dateFormatted;

      // وجود حداقل یک برنامه (شیفت/تعطیلی) برای نمایش گزینه حذف
      const hasSchedule =
        clickableItem.querySelector('.shift-item:not(.unscheduled)') !== null;
      const deleteActionItem = modalOverlay.querySelector('.delete-action');
      if (deleteActionItem) {
        deleteActionItem.style.display = hasSchedule ? 'list-item' : 'none';
      }

      if (!stylistId || !dateIso) return;

      modalStylistLogo.src = stylistLogoUrl || defaultAvatar || '';
      modalStylistLogo.alt = stylistName || '';
      modalStylistName.textContent = stylistName || '';
      modalSelectedDate.textContent = dateFormatted || '';

      modalOverlay.dataset.stylistId = stylistId;
      modalOverlay.dataset.dateIso = dateIso;
      // salonId را از container می‌گیریم (به‌صورت امن)
      modalOverlay.dataset.salonId = salonIdFromContainer || '1';

      modalOverlay.classList.add('active');
    });
  }

  // بستن مدال
  function closeModal() {
    modalOverlay?.classList.remove('active');
  }
  modalCloseButton?.addEventListener('click', closeModal);
  modalOverlay?.addEventListener('click', (event) => {
    if (event.target === modalOverlay) closeModal();
  });

  // اکشن‌های داخل مدال
  const modalActions = modalOverlay?.querySelector('.modal-actions');
  if (modalActions) {
    modalActions.addEventListener('click', function (event) {
      const actionLink = event.target.closest('a');
      if (!actionLink || !actionLink.dataset.action) return;

      event.preventDefault();
      const action = actionLink.dataset.action;
      const stylistId = modalOverlay.dataset.stylistId;
      const salonId = modalOverlay.dataset.salonId;
      const dateIso = modalOverlay.dataset.dateIso;

      if (!stylistId || !dateIso) return;

      if (action === 'edit_day') {
        const editUrl = `/dashboards/schedule/edit-day/stylist/${stylistId}/salon/${salonId}/date/${dateIso}/`;
        window.location.href = editUrl;
      } else if (action === 'delete_day') {
        const confirmMsg = `آیا از حذف تمام برنامه‌های کاری و مرخصی‌های ${modalStylistName.textContent} در تاریخ ${modalSelectedDate.textContent} مطمئن هستید؟`;
        if (!confirm(confirmMsg)) return;

        const deleteUrl = `/dashboards/schedule/delete-day/stylist/${stylistId}/date/${dateIso}/`;
        fetch(deleteUrl, {
          method: 'POST',
          headers: {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/json',
          },
        })
          .then((response) => response.json())
          .then((data) => {
            if (data.status === 'success') {
              alert('برنامه با موفقیت حذف شد.');
              window.location.reload();
            } else {
              alert('خطا در حذف: ' + (data.message || ''));
            }
          })
          .catch((error) => console.error('Fetch Error:', error));
      } else if (action === 'set_regular') {
        const setRegularUrl = `/dashboards/schedule/set-regular/stylist/${stylistId}/salon/${salonId}/`;
        window.location.href = setRegularUrl;
      } else if (action === 'add_time_off') {
        const addTimeOffUrl = `/dashboards/schedule/add-time-off/stylist/${stylistId}/date/${dateIso}/salon/${salonId}`;
        window.location.href = addTimeOffUrl;
      }
    });
  }

  console.info('[scheduled_shifts] initialized.');
}
