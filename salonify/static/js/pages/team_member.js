// static/js/pages/team_member.js
// page: team_member
// نقش: جستجو، بک، مودال اکشن اعضا، فیلترها

export function init() {
  // فقط روی صفحه صحیح اجرا شود
  if (document.body.dataset.page !== 'team_member') return;
  console.debug('[team_member] init');

  // ---------------------------
  // Search functionality
  // ---------------------------
  const searchInput = document.getElementById('searchInput');
  const teamMembersList = document.getElementById('teamMembersList');

  if (searchInput && teamMembersList) {
    searchInput.addEventListener('input', function () {
      const searchTerm = this.value.toLowerCase().trim();
      const teamMembers = teamMembersList.querySelectorAll('.team-member');
      teamMembers.forEach((member) => {
        const memberNameElement = member.querySelector('.team-member-name');
        const memberExpertElement = member.querySelector('.team-member-expert');
        const memberName = memberNameElement ? memberNameElement.textContent.toLowerCase() : '';
        const memberExpert = memberExpertElement ? memberExpertElement.textContent.toLowerCase() : '';
        member.style.display =
          memberName.includes(searchTerm) || memberExpert.includes(searchTerm) ? 'flex' : 'none';
      });
    });
  }

  // ---------------------------
  // Back button
  // ---------------------------
  const btnBack = document.querySelector('.btn-back');
  if (btnBack) {
    btnBack.addEventListener('click', () => {
      window.history.back();
    });
  }

  // ---------------------------
  // Member Actions Modal
  // ---------------------------
  const memberActionsModal = document.getElementById('memberActionsModal');
  const memberModalCloseBtn = memberActionsModal
    ? memberActionsModal.querySelector('.modal-close-btn')
    : null;
  const memberMoreButtons = document.querySelectorAll('.team-member-more');
  let currentStylistInfo = null;

  memberMoreButtons.forEach((button) => {
    button.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      const teamMemberElement = this.closest('.team-member');
      if (!teamMemberElement) return;

      const href = teamMemberElement.getAttribute('href') || '';
      const parts = href.split('/').filter(Boolean);
      // فرض: URL شبیه .../stylist_overview/<id>/
      const stylistId = parts[parts.length - 1] || parts[parts.length - 2];

      currentStylistInfo = {
        id: stylistId,
        name: (teamMemberElement.querySelector('.team-member-name') || {}).textContent || '',
      };

      if (memberActionsModal) memberActionsModal.classList.add('active');
      else console.error('عنصر مودال (memberActionsModal) پیدا نشد!');
    });
  });

  if (memberModalCloseBtn)
    memberModalCloseBtn.addEventListener('click', () => {
      if (memberActionsModal) memberActionsModal.classList.remove('active');
    });

  if (memberActionsModal)
    memberActionsModal.addEventListener('click', (e) => {
      if (e.target === memberActionsModal) memberActionsModal.classList.remove('active');
    });

  if (memberActionsModal) {
    memberActionsModal.querySelectorAll('.modal-action-link').forEach((link) => {
      link.addEventListener('click', function (e) {
        e.preventDefault();
        const action = this.dataset.action;

        if (!currentStylistInfo || !currentStylistInfo.id) {
          console.error('اطلاعات استایلیست برای انجام عملیات در دسترس نیست.');
          if (memberActionsModal) memberActionsModal.classList.remove('active');
          alert('خطا: اطلاعات آرایشگر یافت نشد.');
          return;
        }

        const stylistName = currentStylistInfo.name;
        const stylistId = currentStylistInfo.id;

        if (memberActionsModal) memberActionsModal.classList.remove('active');

        if (action === 'edit') {
          // مسیر ویرایش — در صورت تفاوت با پروژه‌ات این URL را تغییر بده
          const editUrl = `/dashboards/edit_stylist/${stylistId}/`;
          window.location.href = editUrl;
        } else if (action === 'view_calendar') {
          // نمونه: مسیر مشاهده تقویم (در صورت نیاز با مسیر پروژه ات هماهنگ کن)
          // window.location.href = `/dashboards/stylist/${stylistId}/calendar/`;
          alert(`گزینه: مشاهده تقویم\n${stylistName} (ID: ${stylistId})`);
        } else if (action === 'view_shifts') {
          // نمونه: مشاهده شیفت‌ها
          // window.location.href = `/dashboards/scheduled_shifts/?stylist=${stylistId}`;
          alert(`گزینه: مشاهده شیفت‌ها\n${stylistName} (ID: ${stylistId})`);
        } else if (action === 'add_time_off') {
          // نمونه: افزودن مرخصی
          // window.location.href = `/dashboards/schedule/add-time-off/stylist/${stylistId}/`;
          alert(`گزینه: افزودن مرخصی\n${stylistName} (ID: ${stylistId})`);
        } else {
          alert(
            `گزینه انتخاب شده: ${this.textContent}\nبرای آرایشگر: ${stylistName} (ID: ${stylistId})\nعملیات: ${action}`,
          );
        }
      });
    });
  }

  // ---------------------------
  // Filter Modal
  // ---------------------------
  const filterButton = document.querySelector('.filter-button.sort-button');
  const filterModal = document.getElementById('filterModal');
  const filterModalCloseBtn = filterModal
    ? filterModal.querySelector('.filter-modal-close-btn')
    : null;
  const clearFiltersBtn = filterModal ? filterModal.querySelector('.btn-clear-filters') : null;
  const applyFiltersBtn = filterModal ? filterModal.querySelector('.btn-apply-filters') : null;
  const filterCategoryHeaders = filterModal
    ? filterModal.querySelectorAll('.filter-category-header')
    : [];

  if (filterButton) {
    filterButton.addEventListener('click', function () {
      if (!filterModal) {
        console.error('عنصر مودال فیلتر (filterModal) پیدا نشد!');
        return;
      }
      // گسترش خودکار دسته‌هایی که گزینه انتخاب‌شده دارند
      filterCategoryHeaders.forEach((header) => {
        const contentId = header.getAttribute('aria-controls');
        const content = document.getElementById(contentId);
        const hasCheckedOption = content?.querySelector('input.filter-option:checked');
        if (hasCheckedOption && header.getAttribute('aria-expanded') === 'false') {
          content.style.display = 'block';
          header.setAttribute('aria-expanded', 'true');
          const chevronIcon = header.querySelector('.filter-category-chevron i');
          if (chevronIcon) chevronIcon.style.transform = 'rotate(180deg)';
        }
      });
      filterModal.classList.add('active');
    });
  }

  if (filterModalCloseBtn)
    filterModalCloseBtn.addEventListener('click', () => {
      if (filterModal) filterModal.classList.remove('active');
    });

  if (clearFiltersBtn) {
    clearFiltersBtn.addEventListener('click', function () {
      // پاک کردن فیلترها با حذف کوئری‌استرینگ
      window.location.href = window.location.pathname;
    });
  }

  if (applyFiltersBtn) {
    applyFiltersBtn.addEventListener('click', function () {
      const params = new URLSearchParams();

      // Sort by
      const sortByElement = filterModal.querySelector('input[name="sort_by"]:checked');
      if (sortByElement) params.append('sort_by', sortByElement.value);

      // Expertise (checkboxes)
      const expertiseElements = filterModal.querySelectorAll('input[name="expertise"]:checked');
      expertiseElements.forEach((cb) => params.append('expertise', cb.value));

      // Status
      const statusElement = filterModal.querySelector('input[name="status_filter"]:checked');
      if (statusElement) params.append('status_filter', statusElement.value);

      const queryString = params.toString();
      window.location.href = window.location.pathname + (queryString ? '?' + queryString : '');
    });
  }

  // آکاردئون دسته‌بندی‌های فیلتر
  filterCategoryHeaders.forEach((header) => {
    header.addEventListener('click', function () {
      const contentId = this.getAttribute('aria-controls');
      const content = document.getElementById(contentId);
      const isExpanded = this.getAttribute('aria-expanded') === 'true';
      if (content) {
        content.style.display = isExpanded ? 'none' : 'block';
        this.setAttribute('aria-expanded', String(!isExpanded));
        const chevronIcon = this.querySelector('.filter-category-chevron i');
        if (chevronIcon) chevronIcon.style.transform = isExpanded ? 'rotate(0deg)' : 'rotate(180deg)';
      }
    });
  });
}
