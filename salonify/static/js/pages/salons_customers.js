// static/js/pages/salons_customers.js
// page: salons_customers
// نقش: جستجو، فیلتر، مدال «افزودن مشتری»، رندر لیست مشتریان، مدیریت تصویر پروفایل

export function init() {
  if (document.body.dataset.page !== 'salons_customers') return;
  console.debug('[salons_customers] init');

  // ========== توابع کمکی ==========
  function getCsrfToken() {
    const tokenInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
    return tokenInput ? tokenInput.value : '';
  }

  function showLoadingIndicator(container) {
    const loadingIndicator = document.createElement('div');
    loadingIndicator.className = 'loading-indicator';
    loadingIndicator.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';
    container.appendChild(loadingIndicator);
  }

  function removeLoadingIndicator() {
    const loadingElem = document.querySelector('.loading-indicator');
    if (loadingElem) loadingElem.remove();
  }

  function attachCustomerCardEventListeners() {
    document.querySelectorAll('.client-card').forEach((card) => {
      card.addEventListener('click', function () {
        const url = this.getAttribute('data-url');
        const customerId = this.getAttribute('data-customer-id'); // در صورت نیاز
        if (url) window.location.href = url;
      });
    });
  }

  function renderCustomerList(customers, container) {
    if (!customers.length) {
      container.innerHTML = '<div class="no-results">هیچ مشتری با این مشخصات یافت نشد</div>';
      return;
    }

    let html = '';
    customers.forEach((customer) => {
      const profileImageHtml = customer.profile_image
        ? `<img src="${customer.profile_image}" alt="${customer.name}" class="profile-image">`
        : `<div class="profile-placeholder">${(customer.name || '').charAt(0).toUpperCase()}</div>`;

      // استفاده از detail_url در صورت موجود بودن؛ وگرنه fallback بر اساس id
      const detailUrl = customer.detail_url || `/accounts/detail_customer/${customer.id}/`;

      html += `
        <div class="client-card" data-customer-id="${customer.id}" data-url="${detailUrl}">
          <div class="client-avatar">
            ${profileImageHtml}
          </div>
          <div class="client-info">
            <div class="client-name">${customer.name || ''}</div>
            <div class="client-details">
              <div class="client-phone">${customer.phone_number || ''}</div>
              <div class="client-email">${customer.email || 'بدون ایمیل'}</div>
            </div>
          </div>
        </div>
      `;
    });

    container.innerHTML = html;
    attachCustomerCardEventListeners();
  }

  // ========== جستجو ==========
  function searchCustomers(query) {
    const searchContainer = document.querySelector('.search-container') || document.body;
    const customerListContainer = document.querySelector('#clients-list-container');

    showLoadingIndicator(searchContainer);

    fetch(`/search/customers_search/?q=${encodeURIComponent(query)}`, {
      method: 'GET',
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
      },
      credentials: 'same-origin',
    })
      .then((response) => {
        if (!response.ok) throw new Error('Network response was not ok');
        return response.json();
      })
      .then((data) => {
        if (customerListContainer) {
          renderCustomerList(data.customers || [], customerListContainer);
        }
      })
      .catch((error) => {
        console.error('Error searching customers:', error);
        alert('خطا در جستجوی مشتریان. لطفاً مجدداً تلاش کنید.');
      })
      .finally(removeLoadingIndicator);
  }

  function initializeSearch() {
    const searchInput = document.querySelector('.search-input');
    const searchClear = document.querySelector('.search-clear');
    if (!searchInput) return;

    let debounceTimeout;

    if (searchClear) {
      searchClear.addEventListener('click', () => {
        searchInput.value = '';
        searchInput.focus();
        searchClear.style.display = 'none';
        searchCustomers('');
      });
    }

    searchInput.addEventListener('input', () => {
      const query = searchInput.value.trim();
      if (searchClear) searchClear.style.display = query.length > 0 ? 'block' : 'none';

      clearTimeout(debounceTimeout);
      debounceTimeout = setTimeout(() => searchCustomers(query), 300);
    });

    searchInput.addEventListener('focus', () => (searchInput.placeholder = ''));
    searchInput.addEventListener('blur', () => {
      searchInput.placeholder = 'جستجو با نام، ایمیل یا شماره موبایل';
    });
  }

  // ========== فیلتر ==========
  function initializeFilters() {
    const filterButton = document.querySelector('.filter-button');
    const filterModal = document.getElementById('filter-modal');
    const filterClose = document.getElementById('filter-close');
    const clearFiltersButton = document.getElementById('clear-filters');
    const filterForm = document.getElementById('filter-form');
    const clientListContainer = document.querySelector('#clients-list-container');

    // باز کردن مدال
    if (filterButton && filterModal) {
      filterButton.addEventListener('click', function () {
        filterModal.classList.add('active');
        document.body.style.overflow = 'hidden';
      });
    }

    // بستن مدال
    if (filterClose && filterModal) {
      filterClose.addEventListener('click', function () {
        filterModal.classList.remove('active');
        document.body.style.overflow = '';
      });
    }

    // پاک کردن فیلترها
    if (clearFiltersButton) {
      clearFiltersButton.addEventListener('click', function () {
        const selects = document.querySelectorAll('.filter-select');
        selects.forEach((select) => (select.selectedIndex = 0));
      });
    }

    // ارسال فرم فیلتر
    if (filterForm) {
      filterForm.addEventListener('submit', function (e) {
        e.preventDefault();

        const formData = new FormData(this);
        const searchContainer = document.querySelector('.search-container') || document.body;

        showLoadingIndicator(searchContainer);

        fetch(this.action, {
          method: 'POST',
          body: formData,
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCsrfToken(),
          },
          credentials: 'same-origin',
        })
          .then((response) => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
          })
          .then((data) => {
            if (clientListContainer) {
              renderCustomerList(data.customers || [], clientListContainer);
            }
            if (filterModal) {
              filterModal.classList.remove('active');
              document.body.style.overflow = '';
            }
          })
          .catch((error) => {
            console.error('Error applying filters:', error);
            alert('خطا در اعمال فیلترها. لطفا مجددا تلاش کنید.');
            if (filterModal) {
              filterModal.classList.remove('active');
              document.body.style.overflow = '';
            }
          })
          .finally(removeLoadingIndicator);
      });
    }
  }

  // ========== مدال افزودن مشتری ==========
  function initializeAddCustomerModal() {
    const addCustomerBtn = document.querySelector('.add-customer-button');
    const modalOverlay = document.getElementById('addCustomerModal');
    const closeModalBtn = modalOverlay?.querySelector('.close-modal');
    const saveCustomerBtn = document.getElementById('saveCustomerBtn');
    const profileImageInput = document.getElementById('id_profile_image');

    const openModal = () => {
      if (modalOverlay) modalOverlay.style.display = 'block';
    };
    const closeModal = () => {
      if (modalOverlay) modalOverlay.style.display = 'none';
    };

    addCustomerBtn?.addEventListener('click', openModal);
    closeModalBtn?.addEventListener('click', closeModal);

    // تب‌ها در مدال
    if (modalOverlay) {
      const tabs = modalOverlay.querySelectorAll('.modal-tabs li');
      const tabPanes = modalOverlay.querySelectorAll('.tab-pane');
      tabs.forEach((tab) => {
        tab.addEventListener('click', () => {
          tabs.forEach((t) => t.classList.remove('active'));
          tab.classList.add('active');
          const target = tab.getAttribute('data-tab');
          tabPanes.forEach((pane) => {
            pane.classList.toggle('active', pane.id === target);
          });
        });
      });
    }

    // تغییر عکس پروفایل
    if (profileImageInput) {
      profileImageInput.addEventListener('change', function () {
        if (this.files && this.files[0]) {
          const reader = new FileReader();
          reader.onload = function (e) {
            const avatarCircle = document.querySelector('.avatar-circle');
            if (!avatarCircle) return;

            const currentSvg = avatarCircle.querySelector('.avatar-icon');
            if (currentSvg) currentSvg.style.display = 'none';

            avatarCircle.querySelector('img')?.remove();
            const img = document.createElement('img');
            img.src = e.target.result;
            img.style.width = '100%';
            img.style.height = '100%';
            img.style.borderRadius = '50%';
            img.style.objectFit = 'cover';
            avatarCircle.insertBefore(img, avatarCircle.firstChild);
          };
          reader.readAsDataURL(this.files[0]);
        }
      });
    }

    // ارسال فرم افزودن مشتری
    if (saveCustomerBtn) {
      saveCustomerBtn.addEventListener('click', (e) => {
        e.preventDefault();
        const form = document.getElementById('customerForm');
        if (!form) return;

        const formData = new FormData(form);
        const submitUrl = typeof addCustomerUrl !== 'undefined' ? addCustomerUrl : form.action;

        fetch(submitUrl, {
          method: 'POST',
          body: formData,
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCsrfToken(),
          },
        })
          .then((response) => response.json())
          .then((data) => {
            if (data.success) {
              alert(data.message || 'مشتری با موفقیت اضافه شد');
              closeModal();
              refreshCustomerList();
            } else if (data.errors) {
              console.error(data.errors);
              alert('خطا در ثبت اطلاعات');
            }
          })
          .catch((error) => {
            console.error('Error:', error);
            alert('خطا در ارتباط با سرور');
          });
      });
    }

    function refreshCustomerList() {
      const refreshUrl =
        typeof CustomersUrl !== 'undefined' ? CustomersUrl : '/dashboards/salons_customers/';
      fetch(refreshUrl, {
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': getCsrfToken(),
        },
      })
        .then((response) => {
          if (!response.ok) throw new Error('Network response was not ok');
          return response.json();
        })
        .then((data) => {
          const clientListContainer = document.querySelector('#clients-list-container');
          if (clientListContainer && data.customers) {
            renderCustomerList(data.customers, clientListContainer);
          }
        })
        .catch((err) => console.error('Error refreshing customer list:', err));
    }
  }

  // ========== اکشن‌های عمومی ==========
  document.querySelector('.promo-button')?.addEventListener('click', () => {
    alert('نمایش اطلاعات بیشتر');
  });

  document.querySelector('.back-button')?.addEventListener('click', () => {
    history.back();
  });

  // ========== Bootstrap ==========
  initializeSearch();
  initializeFilters();
  initializeAddCustomerModal();
  attachCustomerCardEventListeners();

  console.info('[salons_customers] initialized.');
}
