// page: detail_salon
/* global Swiper, L, salonLat, salonLng, salonName, allReviews, addFavoriteUrl */

export function init(){
  console.debug('[detail_salon] init');

  // ========= Helpers =========
  const $  = (sel, el=document) => el.querySelector(sel);
  const $$ = (sel, el=document) => Array.from(el.querySelectorAll(sel));

  // انیمیشن کشویی فرم دیدگاه
  const slideDown = (el, duration=300) => {
    if (!el) return;
    el.style.display = 'block';
    el.style.overflow = 'hidden';
    const h = el.scrollHeight;
    el.style.height = '0px';
    setTimeout(() => {
      el.style.transition = `height ${duration}ms ease`;
      el.style.height = h + 'px';
    }, 5);
    setTimeout(() => {
      el.style.height = '';
      el.style.transition = '';
      el.style.overflow = '';
    }, duration + 20);
  };
  const slideUp = (el, duration=300) => {
    if (!el) return;
    el.style.overflow = 'hidden';
    el.style.height = el.scrollHeight + 'px';
    setTimeout(() => {
      el.style.transition = `height ${duration}ms ease`;
      el.style.height = '0px';
    }, 5);
    setTimeout(() => {
      el.style.display = 'none';
      el.style.height = '';
      el.style.transition = '';
      el.style.overflow = '';
    }, duration + 20);
  };

  // ====================================
  // 1) اسلایدر بالای صفحه
  // ====================================
  (function heroSlider(){
    const slides = $$('.detailSalon-hero-slider .detailSalon-slide');
    if (!slides.length) return;
    let currentSlide = 0;
    const prevBtn = $('#detailSalon_prevSlide');
    const nextBtn = $('#detailSalon_nextSlide');
    const showSlide = (idx) => slides.forEach((s,i)=> s.classList.toggle('active', i===idx));
    prevBtn?.addEventListener('click', () => { currentSlide = currentSlide===0 ? slides.length-1 : currentSlide-1; showSlide(currentSlide); });
    nextBtn?.addEventListener('click', () => { currentSlide = (currentSlide+1) % slides.length; showSlide(currentSlide); });
  })();

  // ====================================
  // 2) تغییر تاپ‌بار و نمایش تب‌ها با اسکرول
  // ====================================
  (function topbarTabsOnScroll(){
    const topBar = $('#detailSalon_topBar');
    const tabNav = $('#detailSalon_tabNav');
    const salonInfo = $('#detailSalon_salonInfo');
    const hero = $('#detailSalon_heroSlider');
    if (!topBar || !tabNav || !salonInfo || !hero) return;
    const trigger = () => (hero.offsetHeight||0) + (salonInfo.offsetHeight||0);
    const onScroll = () => {
      (window.scrollY>40 ? topBar.classList.add('scrolled'): topBar.classList.remove('scrolled'));
      (window.scrollY>=trigger() ? tabNav.classList.add('show','sticky') : tabNav.classList.remove('show','sticky'));
    };
    window.addEventListener('scroll', onScroll, { passive:true });
    onScroll();
  })();

  // ====================================
  // 3) Scroll Spy
  // ====================================
  (function scrollSpy(){
    const sections = $$('.detailSalon-content-section');
    const navLinks = $$('.detailSalon-tab-nav li a');
    if (!sections.length || !navLinks.length) return;
    const clear = () => navLinks.forEach(a=>a.classList.remove('active'));
    navLinks.forEach(link=>{
      link.addEventListener('click', (e)=>{
        e.preventDefault();
        clear();
        link.classList.add('active');
        const id = link.getAttribute('href');
        const el = id ? $(id) : null;
        el?.scrollIntoView({behavior:'smooth', block:'start'});
        link.scrollIntoView({behavior:'smooth', inline:'center'});
      });
    });
    const onScroll = () => {
      sections.forEach(sec=>{
        const top = (sec.offsetTop||0) - 110;
        const bottom = top + (sec.offsetHeight||0);
        if (window.scrollY>=top && window.scrollY<bottom) {
          clear();
          const link = $(`.detailSalon-tab-nav li a[href="#${sec.id}"]`);
          link?.classList.add('active');
          link?.scrollIntoView({behavior:'smooth', inline:'center'});
        }
      });
    };
    window.addEventListener('scroll', onScroll, { passive:true });
    onScroll();
  })();

  // ====================================
  // 4) تب‌های گروه خدمات
  // ====================================
  (function groupTabs(){
    const btns = $$('.detailSalon-service-group-btn');
    const items = $$('.detailSalon-service-item');
    if (!btns.length || !items.length) return;
    btns.forEach(b=>{
      b.addEventListener('click', function(){
        btns.forEach(x=>x.classList.remove('active'));
        this.classList.add('active');
        const g = this.dataset.group;
        items.forEach(it => it.style.display = it.classList.contains(g) ? 'flex' : 'none');
      });
    });
  })();

  // ====================================
  // 5) Swiper گالری نمونه‌کارها
  // ====================================
  (function gallerySwiperInit(){
    const el = $('#detailSalon_gallerySwiper');
    if (!el) return;
    if (typeof Swiper === 'undefined') { console.warn('Swiper not loaded'); return; }
    // eslint-disable-next-line no-new
    new Swiper('#detailSalon_gallerySwiper', {
      slidesPerView: 1,
      spaceBetween: 10,
      loop: true,
      pagination: { el: '.swiper-pagination', clickable: true, dynamicBullets: true },
      navigation: { nextEl: '.swiper-button-next', prevEl: '.swiper-button-prev' }
    });
  })();

  // ====================================
  // 6) نقشه Leaflet + مسیریابی
  // ====================================
  (function leafletMap(){
    const mapContainer = $('#detailSalon_mapid');
    // اگر کلاً این سکشن در صفحه نیست، رد شو
    if (!mapContainer) return;

    // اگر Leaflet لود نشده بود، پیام و خروج (تا صفحه نشکنه)
    if (typeof L === 'undefined') {
      console.warn('Leaflet not loaded; skip map init');
      return;
    }

    // اعداد را به float امن تبدیل کن
    const lat = Number.parseFloat(typeof salonLat !== 'undefined' ? salonLat : NaN);
    const lng = Number.parseFloat(typeof salonLng !== 'undefined' ? salonLng : NaN);
    if (!Number.isFinite(lat) || !Number.isFinite(lng)) {
      console.warn('Invalid salon coordinates; skip map init');
      return;
    }

    const map = L.map('detailSalon_mapid').setView([lat, lng], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: 'Map data © <a href="https://openstreetmap.org">OpenStreetMap</a>'
    }).addTo(map);

    const marker = L.marker([lat, lng]).addTo(map);
    if (typeof salonName !== 'undefined') marker.bindPopup(salonName);

    const customIcon = L.icon({
      iconUrl: '/static/images/icons/marker.png',
      iconSize: [50, 50],
      iconAnchor: [25, 50],
    });
    L.marker([lat, lng], { icon: customIcon }).addTo(map);

    const labelIcon = L.divIcon({
      className: 'custom-label',
      html: `<div style="background:#fff;padding:5px 10px;border-radius:5px;border:1px solid #ddd;box-shadow:0 2px 5px rgba(0,0,0,.1);"><strong>${(salonName||'')}</strong></div>`,
      iconSize: [100, 40],
      iconAnchor: [50, 120],
    });
    L.marker([lat, lng], { icon: labelIcon }).addTo(map);

    const navigateBtn = $('#detailSalon_navigateBtn');
    navigateBtn?.addEventListener('click', () => {
      const q = encodeURIComponent(`${lat},${lng}`);
      window.open(`https://www.google.com/maps/search/?api=1&query=${q}`, '_blank');
    });
  })();

  // ====================================
  // 7) نمایش/مخفی کردن توضیحات
  // ====================================
  (function descriptionToggle(){
    const descriptionEl = $('#detailSalon_description');
    const toggleBtn = $('#detailSalon_toggleDescriptionBtn');
    if (!descriptionEl || !toggleBtn) return;
    const fullText = (descriptionEl.textContent||'').trim();
    const limit = 200;
    if (fullText.length <= limit) { toggleBtn.style.display='none'; return; }
    const truncated = fullText.slice(0,limit) + ' ...';
    descriptionEl.textContent = truncated;
    toggleBtn.style.display = 'inline-block';
    let isTruncated = true;
    toggleBtn.addEventListener('click', ()=>{
      if (isTruncated){ descriptionEl.textContent = fullText; toggleBtn.textContent='نمایش کمتر'; }
      else { descriptionEl.textContent = truncated; toggleBtn.textContent='نمایش بیشتر'; }
      isTruncated = !isTruncated;
    });
  })();

  // ====================================
  // 8) مودال جزییات خدمت
  // ====================================
  (function serviceModal(){
    const modal = $('#detailSalon_serviceModal');
    if (!modal) return;
    const closeBtn = $('#detailSalon_closeServiceModal');
    const modalImg = $('#detailSalon_modalServiceImage');
    const modalName= $('#detailSalon_modalServiceName');
    const modalTime= $('#detailSalon_modalServiceTime');
    const modalPrice=$('#detailSalon_modalServicePrice');
    const modalStars=$('#detailSalon_modalServiceStars');
    const modalDesc =$('#detailSalon_modalServiceDescription');

    const stars = (score) => {
      let s = parseFloat(score) || 0, f=Math.floor(s), half=s-f>=.5, emp=5-f-(half?1:0);
      return `${'<i class="fa-solid fa-star"></i>'.repeat(f)}${half?'<i class="fa-solid fa-star-half-stroke"></i>':''}${'<i class="fa-regular fa-star"></i>'.repeat(emp)}`;
    };

    $$('.detailSalon-service-item h3').forEach(title=>{
      title.addEventListener('click', ()=>{
        const card = title.closest('.detailSalon-service-item'); if (!card) return;
        const name = card.dataset.serviceName || '';
        const dur  = card.dataset.serviceDuration || '';
        const price= card.dataset.servicePrice || '';
        const desc = card.dataset.serviceDescription || '';
        const score= card.dataset.serviceScore || '';
        const img  = card.dataset.serviceImage || '';

        modalName && (modalName.textContent = name);
        modalTime && (modalTime.textContent = `${dur} دقیقه`);
        modalPrice && (modalPrice.textContent = price ? `از ${price} تومان` : 'قیمت ثبت نشده');
        modalDesc && (modalDesc.textContent = desc);
        modalStars && (modalStars.innerHTML = stars(score));

        if (modalImg){
          if (!img){ modalImg.style.display='none'; }
          else { modalImg.style.display='block'; modalImg.src = img; }
        }
        modal.style.display = 'block';
        modal.style.height  = '90vh';
      });
    });

    closeBtn?.addEventListener('click', ()=>{
      modal.style.height = '0';
      setTimeout(()=>{ modal.style.display='none'; }, 200);
    });
  })();

  // ====================================
  // 9) مودال «نمایش همه آرایشگران»
  // ====================================
  (function allStylistsModal(){
    const openBtn = $('#detailSalon_openAllStylistsModal');
    const closeBtn= $('#detailSalon_closeAllStylistsModal');
    const modal   = $('#detailSalon_allStylistsModal');
    if (!openBtn || !closeBtn || !modal) return;
    openBtn.addEventListener('click', ()=>{
      modal.style.display='block';
      modal.style.height='90vh';
    });
    closeBtn.addEventListener('click', ()=>{
      modal.style.height='0';
      setTimeout(()=>{ modal.style.display='none'; }, 200);
    });
  })();

  // ====================================
  // 10) مودال دیدگاه‌ها + «افزودن نظر»
  // ====================================
  (function reviewsModalAndForm(){
    // --- نمایش همه دیدگاه‌ها ---
    const seeAllBtn = $('#detailSalon_review_btn');
    const reviewModal = $('#detailSalon_reviewModal');
    const closeReview = $('#detailSalon_closeReviewModal');
    const list = $('#detailSalon_modalReviewsList');
    const visibleCount = $('#detailSalon_reviewsVisibleCount');
    const starCheckboxes = $$('.detailSalon-star-filter-checkbox');

    // از تمپلیت باید قبل از app.js مقداردهی شود
    const REVIEWS = Array.isArray(window.allReviews) ? window.allReviews : [];

    const starIcons = (score) => {
      let html = '';
      for (let i=1;i<=5;i++){
        html += i <= (score||0)
          ? '<i class="fa-solid fa-star detailSalon-star"></i>'
          : '<i class="fa-regular fa-star detailSalon-star"></i>';
      }
      return html;
    };

    const renderReviews = () => {
      if (!list || !visibleCount) return;
      const selected = starCheckboxes.filter(ch => ch.checked)
                          .map(ch => parseInt(ch.id.replace('detailSalon_star',''),10));
      const filtered = selected.length ? REVIEWS.filter(r => selected.includes(r.score)) : REVIEWS;
      list.innerHTML = '';
      filtered.forEach(item=>{
        const el = document.createElement('div');
        el.className = 'detailSalon-modal-review-item';
        el.innerHTML = `
          <div class="detailSalon-modal-review-user">
            ${
              item.avatar_url && item.avatar_url !== '#'
                ? `<img src="${item.avatar_url}" alt="Profile" />`
                : `<div class="detailSalon-review-avatar-placeholder">${(item.user_full_name||'U').slice(0,1).toUpperCase()}</div>`
            }
            <span class="detailSalon-username">${item.user_full_name||''}</span>
          </div>
          <p class="detailSalon-review-date">${item.date||''}</p>
          <div class="detailSalon-review-stars">${starIcons(item.score||0)}</div>
          <p class="detailSalon-review-text">${item.comment_text||''}</p>
          <p style="margin-top:.5rem;font-size:.9rem;color:#666;">
            ${item.stylist_name ? `<strong>آرایشگر:</strong> ${item.stylist_name}` : ''}
            ${item.service_name ? ` | <strong>خدمت:</strong> ${item.service_name}` : ''}
          </p>
        `;
        list.appendChild(el);
      });
      visibleCount.textContent = String(filtered.length);
    };

    if (seeAllBtn && reviewModal && closeReview) {
      seeAllBtn.addEventListener('click', ()=>{
        reviewModal.style.display='block';
        reviewModal.style.height ='90vh';
        renderReviews();
      });
      closeReview.addEventListener('click', ()=>{
        reviewModal.style.height='0';
        setTimeout(()=>{ reviewModal.style.display='none'; }, 200);
      });
      starCheckboxes.forEach(ch => ch.addEventListener('change', renderReviews));
    }

    // --- «افزودن نظر» (باز/بسته کردن فرم) ---
    const commentFormContainer = $('#commentFormContainer');
    const addCommentBtn = $('#addCommentBtn');
    const cancelCommentBtn = $('#cancelCommentBtn');
    const commentTextArea = $('#id_comment_text');
    const characterCounter = $('.character-counter');

    addCommentBtn?.addEventListener('click', function(){
      const isVisible = commentFormContainer && window.getComputedStyle(commentFormContainer).display !== 'none';
      if (isVisible) {
        slideUp(commentFormContainer, 300);
        this.innerHTML = '<i class="fas fa-plus-circle" style="color:#333;font-size:1.5rem;"></i>';
      } else {
        slideDown(commentFormContainer, 300);
        this.innerHTML = '<i class="fas fa-minus-circle" style="color:#333;font-size:1.5rem;"></i>';
      }
    });

    cancelCommentBtn?.addEventListener('click', ()=>{
      slideUp(commentFormContainer, 300);
      if (addCommentBtn) addCommentBtn.innerHTML = '<i class="fas fa-plus-circle" style="color:#333;font-size:1.5rem;"></i>';
      const form = cancelCommentBtn.closest('form');
      form?.reset();
      updateStarsVisual(); // بعد از reset
    });

    commentTextArea?.addEventListener('input', function(){
      const max = 500, len = this.value.length;
      if (characterCounter){
        characterCounter.textContent = `${len}/${max}`;
        characterCounter.classList.toggle('limit-exceeded', len>max);
      }
    });

    // ستاره‌های امتیازدهی (visual)
    const ratingInputs = $$('.detailSalon-rating-stars input[type="radio"]');
    const ratingLabels = $$('.detailSalon-rating-stars label');
    function updateStarsVisual(){
      ratingLabels.forEach(l => l.classList.remove('star-selected'));
      ratingInputs.forEach((input, idx)=>{
        if (input.checked){
          for (let i=0;i<=idx;i++) ratingLabels[i]?.classList.add('star-selected');
        }
      });
    }
    ratingInputs.forEach((input, idx)=>{
      input.addEventListener('change', updateStarsVisual);
      const label = ratingLabels[idx];
      if (label){
        label.addEventListener('mouseenter', ()=>{ for (let i=0;i<=idx;i++) ratingLabels[i]?.classList.add('star-hover'); });
        label.addEventListener('mouseleave', ()=>{ ratingLabels.forEach(s=>s.classList.remove('star-hover')); });
        label.addEventListener('click', ()=>{ input.checked = true; input.dispatchEvent(new Event('change')); });
      }
    });
    updateStarsVisual();
  })();

  // ====================================
  // 11) مودال «نمایش همه نمونه‌کارها»
  // ====================================
  (function allSamplesModal(){
    const openBtn = $('#detailSalon_openAllSamplesBtn');
    const modal   = $('#detailSalon_allSamplesModal');
    const closeBtn= $('#detailSalon_closeAllSamplesModal');
    if (!openBtn || !modal || !closeBtn) return;
    openBtn.addEventListener('click', ()=>{
      modal.style.display='block';
      modal.style.height='90vh';
    });
    closeBtn.addEventListener('click', ()=>{
      modal.style.height='0';
      setTimeout(()=>{ modal.style.display='none'; }, 200);
    });

    // لایت‌باکس تکی (روی کارت‌های گالری بالا هم کار می‌کند)
    const sampleCards = $$('.detailSalon-sample-card');
    const fullscreenBox = $('#detailSalon_fullscreenSample');
    const fullImg = $('#detailSalon_fullscreenSampleImage');
    const closeFs = $('#detailSalon_closeFullscreenSample');
    sampleCards.forEach(card=>{
      card.addEventListener('click', ()=>{
        const url = card.getAttribute('data-image-url');
        if (!url || !fullscreenBox || !fullImg) return;
        fullImg.src = url; fullscreenBox.style.display='flex';
      });
    });
    closeFs?.addEventListener('click', ()=> fullscreenBox && (fullscreenBox.style.display='none'));
    fullscreenBox?.addEventListener('click', (e)=>{ if (e.target===fullscreenBox) fullscreenBox.style.display='none'; });
  })();

  // ====================================
  // 12) نوار انتخاب خدمات و رزرو (مثل قبل)
  // ====================================
  (function bookingBar(){
    const serviceInfoEl = $('#serviceInfo');
    const totalSalonServices = parseInt(serviceInfoEl?.dataset.totalServices || '0', 10) || 0;
    let selected = [];
    const bookButtons = $$('.detailSalon-btn-book');
    const countEl = $('#detailSalon_selectedServicesCount');
    const priceEl = $('#detailSalon_selectedServicesPrice');
    const durEl   = $('#detailSalon_selectedServicesDuration');
    const updateBar = () => {
      if (!countEl || !priceEl || !durEl) return;
      if (!selected.length){
        countEl.textContent = `${totalSalonServices} خدمت`;
        priceEl.style.display = 'none'; durEl.style.display = 'none';
        return;
      }
      countEl.textContent = `${selected.length} خدمت`;
      let totalPrice=0, totalDur=0;
      selected.forEach(s=>{ totalPrice += s.price||0; totalDur += s.duration||0; });
      const h = Math.floor(totalDur/60), m= totalDur%60;
      const durTxt = h>0 ? `${h} ساعت و ${m} دقیقه` : `${m} دقیقه`;
      priceEl.textContent = `${totalPrice.toLocaleString()} تومان`;
      durEl.textContent = durTxt;
      priceEl.style.display = 'block'; durEl.style.display = 'block';
    };
    bookButtons.forEach(btn=>{
      btn.addEventListener('click', ()=>{
        const item = btn.closest('.detailSalon-service-item'); if (!item) return;
        const id = item.dataset.serviceId || '';
        const name = item.dataset.serviceName || '';
        const duration = parseInt(item.dataset.serviceDuration||'0',10) || 0;
        const raw = (item.dataset.servicePrice||'').replace(/,/g,'');
        const price = parseInt(raw||'0',10)||0;
        const selectedNow = item.classList.toggle('selected');
        const icon = btn.querySelector('i');
        if (selectedNow){
          selected.push({id,name,duration,price});
          icon && icon.classList.replace('fa-plus','fa-square-check');
        } else {
          selected = selected.filter(s=>s.id!==id);
          icon && icon.classList.replace('fa-square-check','fa-plus');
        }
        updateBar();
      });
    });
    updateBar();

    const goBtn = $('#detailSalon_bookAppointmentBtn');
    goBtn?.addEventListener('click', function(){
      const url = this.dataset.bookingUrl; const salonId = this.dataset.salonId;
      if (!url) return;
      const ids = selected.map(s=>s.id).join(',');
      window.location.href = `${url}?salon_id=${encodeURIComponent(salonId||'')}&selected_services=${encodeURIComponent(ids)}`;
    });
  })();

  // ====================================
  // 13) Like (علاقه‌مندی)
  // ====================================
  (function likeFavorite(){
    const btn = $('.like-button');
    if (!btn || typeof addFavoriteUrl === 'undefined') return;
    btn.addEventListener('click', function(){
      const salonId = this.getAttribute('data-salon-id');
      const heart = this.querySelector('i');
      fetch(addFavoriteUrl + '?salonId=' + encodeURIComponent(salonId||''), {
        method: 'GET', headers: { 'X-Requested-With': 'XMLHttpRequest' }
      })
      .then(r=>r.text())
      .then(t=>{
        if (!heart) return;
        if (t.includes('اضافه شد')) { heart.classList.remove('fa-regular'); heart.classList.add('fa-solid','liked'); }
        else if (t.includes('حذف شد')) { heart.classList.remove('fa-solid','liked'); heart.classList.add('fa-regular'); }
      })
      .catch(err=>console.error('favorite error:', err));
    });
  })();

  // ====================================
  // 14) Back & Share (اختیاری)
  // ====================================
  document.addEventListener('click', async (e)=>{
    const backBtn = e.target.closest('[data-action="go-back"]');
    if (backBtn){ e.preventDefault(); history.back(); }

    const shareBtn = e.target.closest('[data-action="share-page"]');
    if (shareBtn){
      e.preventDefault();
      try {
        const pageUrl = location.href;
        const pageTitle = document.title || (window.salonName ?? '');
        const pageText = $('.detailSalon-address')?.textContent?.trim() || '';
        if (navigator.share){ await navigator.share({ title: pageTitle, text: pageText, url: pageUrl }); }
        else if (navigator.clipboard){ await navigator.clipboard.writeText(pageUrl); alert('لینک صفحه کپی شد'); }
        else { prompt('لطفاً لینک زیر را دستی کپی کنید:', pageUrl); }
      } catch(err){ console.error('share error:', err); }
    }
  });
}
