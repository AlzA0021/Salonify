// page: salons
/* global Swiper */
export function init(){
  console.debug('[salons] init');

  // اگر Swiper لود نشده بود، فقط رد شو تا صفحه نشکنه
  if (typeof Swiper === 'undefined') {
    console.warn('Swiper not found on salons page');
    return;
  }

  const commonOptions = {
    loop: true,
    slidesPerView: 1.2,
    spaceBetween: 20,
    // اگر pagination یا navigation در HTML گذاشتی، این‌ها را اضافه کن:
    // pagination: { el: '.swiper-pagination', clickable: true },
    // navigation: { nextEl: '.swiper-button-next', prevEl: '.swiper-button-prev' },
    breakpoints: {
      640:  { slidesPerView: 1.5 },
      1024: { slidesPerView: 1.8 }
    }
  };

  // برای هر باکس recent یک Swiper بساز
  document.querySelectorAll('.salons-recent-swiper').forEach((el) => {
    // eslint-disable-next-line no-new
    new Swiper(el, commonOptions);
  });

  // برای باکس top هم یک Swiper
  document.querySelectorAll('.salons-top-swiper').forEach((el) => {
    // eslint-disable-next-line no-new
    new Swiper(el, commonOptions);
  });
}
