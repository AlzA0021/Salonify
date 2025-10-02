// static/js/pages/select_stylists.js
// page: select_stylists

export function init() {
  console.debug('[select_stylists] init');

  /** @type {Record<string,{stylistId:string, stylistName:string, serviceName:string, profileImage:string}>} */
  const selectedStylists = {};

  const accordion = document.querySelector('.accordion');
  const bottomInfo = document.getElementById('selectedStylistsInfo');
  const proceedBtn = document.getElementById('proceedBtn');

  // ---- منابع داینامیک از تمپلیت ----
  const dynamicData = window.dynamicData || {
    salonId: '',
    nextUrl: '',
    services: [],
  };

  // ---------- آکاردئون ----------
  function toggleAccordion(headerEl) {
    const item = headerEl.closest('.accordion-item');
    if (!item) return;
    const content = item.querySelector('.accordion-content');
    headerEl.classList.toggle('active');
    content?.classList.toggle('active');
  }

  // ---------- انتخاب آرایشگر برای خدمت ----------
  function selectStylistForService(serviceId, stylistId, cardEl) {
    // پاک کردن انتخاب قبلی برای همین خدمت
    document
      .querySelectorAll(`.accordion-item[data-service-id="${CSS.escape(serviceId)}"] .detailSalon-team-member-box`)
      .forEach((el) => el.classList.remove('selected'));

    // انتخاب کارت جدید
    cardEl.classList.add('selected');

    // استخراج داده‌ها
    const profileImgEl = cardEl.querySelector('img');
    const profileImage = profileImgEl ? profileImgEl.getAttribute('src') || '' : '';
    const stylistName = cardEl.querySelector('.detailSalon-name')?.textContent?.trim() || '';
    const serviceName =
      cardEl.closest('.accordion-item')?.querySelector('.service-title')?.textContent?.trim() || '';

    selectedStylists[String(serviceId)] = {
      stylistId: String(stylistId),
      stylistName,
      serviceName,
      profileImage,
    };

    updateBottomBar();
  }

  // ---------- نوار پایین ----------
  function updateBottomBar() {
    if (!bottomInfo) return;
    bottomInfo.innerHTML = '';

    // به‌ترتیب خدمات انتخاب‌شده نمایش بده
    Object.keys(selectedStylists).forEach((serviceId) => {
      const sel = selectedStylists[serviceId];
      const wrap = document.createElement('div');
      wrap.className = 'selected-chip';

      const img = document.createElement('img');
      img.alt = sel.stylistName;
      img.src = sel.profileImage || '';

      const text = document.createElement('span');
      text.textContent = sel.serviceName;

      wrap.appendChild(img);
      wrap.appendChild(text);
      bottomInfo.appendChild(wrap);
    });
  }

  // ---------- اعتبارسنجی و ادامه ----------
  function proceedToDateTime() {
    // همه‌ی خدمات باید یک آرایشگر داشته باشند
    for (const svc of dynamicData.services || []) {
      const key = String(svc.id);
      if (!selectedStylists[key]) {
        alert(`لطفاً برای خدمت «${svc.serviceName}» یک آرایشگر انتخاب کنید.`);
        return;
      }
    }

    // ساخت پارامتر selections
    const selections = (dynamicData.services || []).map((svc) => ({
      service_id: String(svc.id),
      stylist_id: selectedStylists[String(svc.id)].stylistId,
    }));

    const params = new URLSearchParams();
    if (dynamicData.salonId) params.append('salon_id', String(dynamicData.salonId));
    params.append('selections', JSON.stringify(selections));

    const nextUrl = dynamicData.nextUrl || '/orders/select_datetime/';
    window.location.href = `${nextUrl}?${params.toString()}`;
  }

  // ---------- Event delegation ----------
  if (accordion) {
    accordion.addEventListener('click', (e) => {
      const header = e.target.closest('.accordion-header[data-accordion-toggle]');
      if (header) {
        e.preventDefault();
        toggleAccordion(header);
        return;
      }

      const card = e.target.closest('.detailSalon-team-member-box[data-service-id][data-stylist-id]');
      if (card) {
        e.preventDefault();
        const serviceId = card.getAttribute('data-service-id');
        const stylistId = card.getAttribute('data-stylist-id');
        if (serviceId && stylistId) {
          selectStylistForService(serviceId, stylistId, card);
        }
      }
    });
  }

  // دکمه ادامه
  if (proceedBtn) {
    proceedBtn.addEventListener('click', (e) => {
      e.preventDefault();
      proceedToDateTime();
    });
  }

  // سازگاری با کدهای قدیمی (در صورت وجود onclick در Html قدیمی)
  window.__selectStylists = {
    proceedToDateTime,
  };
}
