// static/js/pages/service_menu.js
// page: service_menu
// نقش: مدیریت منوی خدمات سالن (مودال، تب‌ها، اسکرول تب‌ها، فرمت زمان، ...)
// نکته: این ماژول با app.js و data-page="service_menu" لود می‌شود.

export function init() {
  if (document.body.dataset.page !== 'service_menu') return;
  console.debug('[service_menu] init');

  // عناصر اصلی (ممکنه بعضی‌ها در صفحه نباشن؛ کد تحمل خطا داره)
  const categoryTabs = document.querySelectorAll('.category-tab');
  const searchInput = document.getElementById('searchInput');
  const serviceItems = document.querySelectorAll('.service-item');
  const serviceCategories = document.querySelectorAll('.service-category');
  const noResults = document.getElementById('noResults');
  const sortBtn = document.getElementById('sortBtn');
  const tabsContainer = document.getElementById('categoryTabs');

  // وضعیت‌ها
  let activeCategory = 'all';
  let sortOrder = 'asc'; // 'asc' | 'desc'
  let currentServiceId = null;

  // اگر modal از قبل در تمپلیت هست از همون استفاده کن؛ وگرنه بساز
  function getOrCreateModal() {
    let modalEl = document.getElementById('serviceModal');
    let closeBtn;
    if (!modalEl) {
      // فقط اگر وجود نداشت، بساز و استایل تزریق کن
      addModalStyles();
      modalEl = document.createElement('div');
      modalEl.id = 'serviceModal';
      modalEl.className = 'service-modal';
      modalEl.innerHTML = `
        <div class="modal-content">
          <div class="modal-header">
            <span class="close-modal">&times;</span>
          </div>
          <div class="modal-body">
            <div class="modal-option" id="editOption">
              <i class="fa-solid fa-edit"></i>
              <span>ویرایش</span>
            </div>
            <div class="modal-option" id="quickBookingOption">
              <i class="fa-solid fa-link"></i>
              <span>لینک رزرو سریع</span>
            </div>
            <div class="modal-option" id="archiveOption">
              <i class="fa-solid fa-archive"></i>
              <span>بایگانی</span>
            </div>
            <div class="modal-option delete-option" id="deleteOption">
              <i class="fa-solid fa-trash"></i>
              <span>حذف دائمی</span>
            </div>
          </div>
        </div>`;
      document.body.appendChild(modalEl);
      closeBtn = modalEl.querySelector('.close-modal');
    } else {
      closeBtn = modalEl.querySelector('.close-modal');
    }

    // بستن مودال
    if (closeBtn) {
      closeBtn.addEventListener('click', () => (modalEl.style.display = 'none'));
    }
    window.addEventListener('click', (evt) => {
      if (evt.target === modalEl) modalEl.style.display = 'none';
    });

    // گزینه‌ها
    setupModalOptions(modalEl);
    return modalEl;
  }

  function addModalStyles() {
    if (document.getElementById('service-modal-inline-style')) return;
    const styleEl = document.createElement('style');
    styleEl.id = 'service-modal-inline-style';
    styleEl.textContent = `
      .service-modal{display:none;position:fixed;z-index:1000;left:0;top:0;width:100%;height:100%;overflow:auto;background-color:rgba(0,0,0,.4);animation:fadeIn .3s}
      .service-modal .modal-content{background:#fff;margin:auto;width:90%;max-width:400px;border-radius:12px;position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);box-shadow:0 4px 20px rgba(0,0,0,.15);animation:slideUp .3s}
      .service-modal .modal-header{padding:15px;display:flex;justify-content:flex-end;border-bottom:1px solid #f0f0f0}
      .service-modal .close-modal{color:#aaa;font-size:24px;font-weight:700;cursor:pointer;width:30px;height:30px;display:flex;align-items:center;justify-content:center;border-radius:50%;transition:background-color .2s}
      .service-modal .close-modal:hover{background:#f8f9fa;color:#555}
      .service-modal .modal-body{padding:15px 0}
      .service-modal .modal-option{padding:15px 20px;display:flex;align-items:center;cursor:pointer;transition:background-color .2s}
      .service-modal .modal-option:hover{background:#f8f9fa}
      .service-modal .modal-option i{margin-left:12px;width:24px;color:#555}
      .service-modal .delete-option,.service-modal .delete-option i{color:#e53935}
      @keyframes fadeIn{from{opacity:0}to{opacity:1}}
      @keyframes slideUp{from{top:60%;opacity:0}to{top:50%;opacity:1}}
    `;
    document.head.appendChild(styleEl);
  }

  function setupModalOptions(modal) {
    const $ = (sel) => modal.querySelector(sel);

    const editBtn = $('#editOption');
    const quickBtn = $('#quickBookingOption');
    const archiveBtn = $('#archiveOption');
    const deleteBtn = $('#deleteOption');

    editBtn?.addEventListener('click', () => {
      modal.style.display = 'none';
      const meta = document.querySelector('meta[name="service-edit-url"]');
      const tpl = meta?.getAttribute('content');
      if (!tpl) return console.warn('meta service-edit-url not found');
      if (!currentServiceId) return;
      window.location.href = tpl.replace('0', currentServiceId);
    });

    quickBtn?.addEventListener('click', () => {
      modal.style.display = 'none';
      if (!currentServiceId) return;
      generateQuickBookingLink(currentServiceId);
    });

    archiveBtn?.addEventListener('click', () => {
      modal.style.display = 'none';
      const meta = document.querySelector('meta[name="service-archive-url"]');
      const tpl = meta?.getAttribute('content');
      if (!tpl) return console.warn('meta service-archive-url not found');
      if (!currentServiceId) return;
      window.location.href = tpl.replace('0', currentServiceId);
    });

    deleteBtn?.addEventListener('click', () => {
      modal.style.display = 'none';
      const meta = document.querySelector('meta[name="service-remove-url"]');
      const tpl = meta?.getAttribute('content');
      if (!tpl) return console.warn('meta service-remove-url not found');
      if (!currentServiceId) return;
      if (confirm('آیا از حذف دائمی این خدمت اطمینان دارید؟')) {
        window.location.href = tpl.replace('0', currentServiceId);
      }
    });
  }

  // ساخت/کپی لینک رزرو سریع (نمونه با کپی به کلیپ‌بورد)
  function generateQuickBookingLink(serviceId) {
    const url = `${window.location.origin}/orders/quick-book/?service=${serviceId}`;
    try {
      navigator.clipboard.writeText(url);
      alert('لینک رزرو سریع کپی شد:\n' + url);
    } catch {
      prompt('این لینک را کپی کنید:', url);
    }
  }

  // تب‌های دسته‌بندی
  function setupCategoryTabs() {
    if (!categoryTabs.length) return;
    categoryTabs.forEach((tab) => {
      tab.addEventListener('click', function (e) {
        e.preventDefault();
        categoryTabs.forEach((t) => t.classList.remove('active'));
        this.classList.add('active');

        activeCategory = this.dataset.category;

        serviceCategories.forEach((category) => category.classList.remove('active'));

        if (activeCategory === 'all') {
          serviceCategories.forEach((category) => {
            category.classList.remove('hidden');
            setTimeout(() => category.classList.add('active'), 10);
          });
        } else {
          serviceCategories.forEach((category) => {
            if (category.id === 'group-' + activeCategory) {
              category.classList.remove('hidden');
              setTimeout(() => category.classList.add('active'), 10);
            } else {
              category.classList.add('hidden');
            }
          });
        }

        const targetId = this.getAttribute('href');
        const target = document.querySelector(targetId);
        if (target) {
          window.scrollTo({ top: target.offsetTop - 200, behavior: 'smooth' });
        }
      });
    });
  }

  // فرمت مدت‌زمان در کارت‌ها
  function formatServiceDurations() {
    document.querySelectorAll('.service-duration').forEach((el) => {
      const text = el.textContent.trim();
      const match = text.match(/(\d+)/);
      if (!match) return;

      const minutes = parseInt(match[1], 10);
      let iconSpan = el.querySelector('.duration-icon');
      let formattedTime = '';

      if (minutes >= 60) {
        const h = Math.floor(minutes / 60);
        const rm = minutes % 60;
        formattedTime = h + ' ساعت' + (rm > 0 ? ' و ' + rm + ' دقیقه' : '');
      } else {
        formattedTime = minutes + ' دقیقه';
      }

      el.innerHTML = '';
      if (iconSpan) {
        el.appendChild(iconSpan);
      } else {
        const newIcon = document.createElement('span');
        newIcon.className = 'duration-icon';
        newIcon.innerHTML = '<i class="fa-regular fa-clock"></i>';
        el.appendChild(newIcon);
      }
      el.appendChild(document.createTextNode(' ' + formattedTime));
    });
  }

  // اسکرول افقی تب‌ها با درگ
  function setupDragScroll() {
    if (!tabsContainer) return;
    let isDown = false, startX = 0, scrollLeft = 0;

    tabsContainer.addEventListener('mousedown', (e) => {
      isDown = true;
      tabsContainer.style.cursor = 'grabbing';
      startX = e.pageX - tabsContainer.offsetLeft;
      scrollLeft = tabsContainer.scrollLeft;
    });
    tabsContainer.addEventListener('mouseleave', () => {
      isDown = false;
      tabsContainer.style.cursor = 'grab';
    });
    tabsContainer.addEventListener('mouseup', () => {
      isDown = false;
      tabsContainer.style.cursor = 'grab';
    });
    tabsContainer.addEventListener('mousemove', (e) => {
      if (!isDown) return;
      e.preventDefault();
      const x = e.pageX - tabsContainer.offsetLeft;
      const walk = (x - startX) * 0.8;
      tabsContainer.scrollLeft = scrollLeft - walk;
    });
  }

  // سایه هدر هنگام اسکرول
  function setupHeaderShadow() {
    const header = document.querySelector('.header');
    if (!header) return;
    window.addEventListener('scroll', () => {
      header.style.boxShadow = window.scrollY > 10 ? '0 2px 5px rgba(0,0,0,0.1)' : 'none';
    });
  }

  // کلیک روی کارت‌های خدمت → نمایش مودال
  function attachServiceItemClickHandlers(items, modalEl) {
    if (!items.length) return;
    items.forEach((item) => {
      item.addEventListener('click', (e) => {
        e.preventDefault();
        currentServiceId = item.dataset.serviceId;
        if (!currentServiceId) return;
        modalEl.style.display = 'block';
      });
    });
  }

  // ---- اجرای اولیه
  const modal = getOrCreateModal();
  attachServiceItemClickHandlers(serviceItems, modal);
  setupCategoryTabs();
  formatServiceDurations();
  setupDragScroll();
  setupHeaderShadow();

  console.info('[service_menu] initialized.');
}
