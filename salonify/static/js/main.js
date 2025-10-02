// // =============================================================================
// // // Index Slider
// // document.addEventListener('DOMContentLoaded', function () {
// //     var swiper = new Swiper('.index_slider-main-slider', {
// //         loop: true,
// //         autoplay: {
// //             delay: 5000,
// //         },
// //         speed: 1000,
// //         navigation: {
// //             nextEl: '.swiper-button-next',
// //             prevEl: '.swiper-button-prev',
// //         },
// //         pagination: {
// //             el: '.swiper-pagination',
// //             clickable: true,
// //         },
// //         effect: 'slide',
// //         rtl: true, // برای راست‌چین بودن اسلایدر
// //     });
// // });

// // ===================================================================================
// // Service_card
// document.addEventListener("DOMContentLoaded", function() {
//     var tabs = document.querySelectorAll('.service-card-tab');
//     tabs.forEach(function(tab) {
//         tab.addEventListener("click", function(event) {
//             event.preventDefault();
//             var currentPanel = document.querySelector(this.getAttribute("data-target"));
//             // پیدا کردن تمام پنل‌ها و بستن آنها
//             var allPanels = this.closest('.service-card-container').querySelectorAll('.tab-pane');
//             allPanels.forEach(function(panel) {
//                 if (panel !== currentPanel) {
//                     panel.style.display = "none"; // بستن سایر پنل‌ها
//                 }
//             });
//             // تعویض وضعیت پنل فعلی
//             if (currentPanel.style.display === "none" || !currentPanel.style.display) {
//                 currentPanel.style.display = "block";
//             } else {
//                 currentPanel.style.display = "none";
//             }
//         });
//     });
// });

// // =======================================================================================
// // Detail-Salon
// document.addEventListener('DOMContentLoaded', function() {
//     const tabs = document.querySelectorAll('.group-service-tab');
//     tabs.forEach(tab => {
//         tab.addEventListener('click', function() {
//             console.log('Tab clicked:', this.getAttribute('data-target')); // اضافه کردن برای اشکال‌زدایی

//             // مخفی کردن تمام بخش‌های محتوای گروه خدمات
//             document.querySelectorAll('.group-service-pane').forEach(pane => {
//                 pane.style.display = 'none';
//                 pane.classList.remove('show');
//             });

//             // حذف کلاس فعال از تمام تب‌ها
//             tabs.forEach(t => t.classList.remove('active-tab'));

//             // اضافه کردن کلاس فعال به تب انتخابی
//             this.classList.add('active-tab');

//             // نمایش بخش محتوای مرتبط با تب انتخاب شده
//             const target = document.querySelector(this.getAttribute('data-target'));
//             if (target) {
//                 target.style.display = 'block';
//                 setTimeout(() => target.classList.add('show'), 10); // اضافه کردن کلاس برای انتقال فید
//             } else {
//                 console.error('Target not found:', this.getAttribute('data-target')); // برای اشکال‌زدایی در صورت نیافتن المان هدف
//             }
//         });
//     });
// });

// function openImageModal(src) {
//     const modal = document.getElementById("imageModal");
//     const modalImg = document.getElementById("modalImage");
//     modal.style.display = "block";
//     modalImg.src = src;
// }

// function closeImageModal() {
//     const modal = document.getElementById("imageModal");
//     modal.style.display = "none";
// }

// // ========================================================================================
// // Services

// document.addEventListener('DOMContentLoaded', function() {
//     const tabs = document.querySelectorAll('.group-service-tab');
//     tabs.forEach(tab => {
//         tab.addEventListener('click', function() {
//             // مخفی کردن تمام بخش‌های محتوای گروه خدمات
//             document.querySelectorAll('.group-service-pane').forEach(pane => {
//                 pane.style.display = 'none';
//                 pane.classList.remove('show');
//             });

//             // حذف کلاس فعال از تمام تب‌ها
//             tabs.forEach(t => t.classList.remove('active-tab'));

//             // اضافه کردن کلاس فعال به تب انتخابی
//             this.classList.add('active-tab');

//             // نمایش بخش محتوای مرتبط با تب انتخاب شده
//             const target = document.querySelector(this.getAttribute('data-target'));
//             if (target) {
//                 target.style.display = 'block';
//                 setTimeout(() => target.classList.add('show'), 10); // اضافه کردن کلاس برای انتقال فید
//             }
//         });
//     });
// });

// function applyFilters() {
//     const group = document.getElementById('service-group').value;
//     const minPrice = document.getElementById('min-price').value;
//     const maxPrice = document.getElementById('max-price').value;
//     console.log('Filter applied:', { group, minPrice, maxPrice });
//     // TODO: Implement filtering logic here
// }

// function applySorting() {
//     const sortBy = document.getElementById('sort-by').value;
//     console.log('Sorting applied:', { sortBy });
//     // TODO: Implement sorting logic here
// }

// document.addEventListener('DOMContentLoaded', function() {
//     const tabs = document.querySelectorAll('.group-service-tab');
//     tabs.forEach(tab => {
//         tab.addEventListener('click', function() {
//             // مخفی کردن تمام بخش‌های محتوای گروه خدمات
//             document.querySelectorAll('.group-service-pane').forEach(pane => {
//                 pane.style.display = 'none';
//                 pane.classList.remove('show');
//             });

//             // حذف کلاس فعال از تمام تب‌ها
//             tabs.forEach(t => t.classList.remove('active-tab'));

//             // اضافه کردن کلاس فعال به تب انتخابی
//             this.classList.add('active-tab');

//             // نمایش بخش محتوای مرتبط با تب انتخاب شده
//             const target = document.querySelector(this.getAttribute('data-target'));
//             if (target) {
//                 target.style.display = 'block';
//                 setTimeout(() => target.classList.add('show'), 10); // اضافه کردن کلاس برای انتقال فید
//             }
//         });
//     });
// });

// function applyFilters() {
//     const group = document.getElementById('service-group').value;
//     const minPrice = document.getElementById('min-price').value;
//     const maxPrice = document.getElementById('max-price').value;
//     console.log('Filter applied:', { group, minPrice, maxPrice });
//     // TODO: Implement filtering logic here
// }

// function applySorting() {
//     const sortBy = document.getElementById('sort-by').value;
//     console.log('Sorting applied:', { sortBy });
//     // TODO: Implement sorting logic here
// }

// // ==============================================================================
// //  Stylist Card

//   function toggleComments(stylistId) {
//       const commentsSection = document.getElementById('comments-' + stylistId);
//       if (commentsSection.style.display === 'none' || commentsSection.style.display === '') {
//           commentsSection.style.display = 'block';
//       } else {
//           commentsSection.style.display = 'none';
//       }
//   }

// // ==============================================================================================
// // Salons Card
// // تعریف تابع در سطح جهانی
// function attachCommentsToggle() {
//     const commentToggles = document.querySelectorAll('.salon_card-comments-toggle');
//     commentToggles.forEach(function(toggle) {
//       toggle.addEventListener('click', function(event) {
//         event.preventDefault();
//         const commentsId = this.getAttribute('data-comments-id');
//         const commentsSection = document.getElementById(commentsId);
//         if (commentsSection.style.display === 'none' || commentsSection.style.display === '') {
//           commentsSection.style.display = 'block';
//         } else {
//           commentsSection.style.display = 'none';
//         }
//       });
//     });
//   }

//   // فراخوانی تابع پس از بارگذاری اولیه صفحه
//   document.addEventListener('DOMContentLoaded', function() {
//     attachCommentsToggle();
//   });

// // ============================================================================
// //  Top Section
//   document.addEventListener('DOMContentLoaded', function() {
//     const radios = document.querySelectorAll('input[type="radio"][name="radio"]');

//     // تابع برای بارگذاری محتوا
//     function loadContent(url) {
//       fetch(url)
//         .then(response => response.text())
//         .then(html => {
//           const contentArea = document.getElementById('content-area');
//           if(contentArea) {
//             contentArea.innerHTML = html;
//             // فراخوانی تابع برای اضافه کردن رویدادها به محتوای جدید
//             attachCommentsToggle();
//           } else {
//             console.error('No content area found');
//           }
//         })
//         .catch(error => console.error('Error loading the content: ', error));
//     }

//     // اضافه کردن رویداد تغییر به رادیو باتن‌ها
//     radios.forEach(radio => {
//       radio.addEventListener('change', function() {
//         if (this.checked) {
//           loadContent(this.getAttribute('data-url'));
//         }
//       });
//     });

//     // بارگذاری محتوای رادیو باتن انتخاب‌شده هنگام بارگذاری صفحه
//     const checkedRadio = document.querySelector('input[type="radio"][name="radio"]:checked');
//     if (checkedRadio) {
//       loadContent(checkedRadio.getAttribute('data-url'));
//     }
//   });

// // ===================================================================
// function status_of_order_cart() {
//     $.ajax({
//         type: "GET",
//         url: "/orders/status_of_order_cart",
//         success: function (res) {
//             $("#indicator__value").text(res)
//         }
//     })
// }
// status_of_order_cart()
// ==================================================================
// Search Toggle
// document.addEventListener("DOMContentLoaded", function () {
//   const searchToggle = document.getElementById("searchToggle");
//   const searchInput = document.querySelector(".search-input");
//   const searchForm = document.getElementById("searchForm");

//   // تابع باز کردن اینپوت و نمایش صفحه‌کلید
//   function toggleSearchInput(e) {
//     e.preventDefault(); // جلوگیری از رفتار پیش‌فرض
//     if (!searchInput.classList.contains("active")) {
//       searchInput.classList.add("active");
//       setTimeout(() => {
//         searchInput.focus(); // فوکوس روی اینپوت برای باز کردن صفحه‌کلید
//       }, 100); // تاخیر کوچک برای هماهنگی بهتر با انیمیشن‌ها
//     } else اگر (searchInput.value.trim()) {
//       searchForm.submit(); // ارسال فرم در صورت داشتن مقدار
//     }
//   }

//   // رویداد کلیک یا لمس روی آیکون سرچ
//   searchToggle.addEventListener("click", toggleSearchInput);
//   searchToggle.addEventListener("touchstart", toggleSearchInput);

//   // جلوگیری از ارسال فرم هنگام تایپ در اینپوت
//   searchForm.addEventListener("submit", function (e) {
//     if (!searchInput.value.trim()) {
//       e.preventDefault();
//       alert("لطفاً عبارتی برای جستجو وارد کنید!");
//     }
//   });

//   // بستن اینپوت با کلیک در خارج از آن
//   document.addEventListener("click", function (e) {
//     if (!searchForm.contains(e.target) && searchInput.classList.contains("active")) {
//       searchInput.classList.remove("active");
//       searchInput.blur(); // برداشتن فوکوس برای بستن صفحه‌کلید
//     }
//   });

//   document.addEventListener("touchstart", function (e) {
//     if (!searchForm.contains(e.target) && searchInput.classList.contains("active")) {
//       searchInput.classList.remove("active");
//       searchInput.blur(); // برداشتن فوکوس برای بستن صفحه‌کلید
//     }
//   });
// });

// // ==================================================================
// //Header-Slider

// const swiper = new Swiper('.header-swiper', {
//   // Enable infinite loop
//   loop: true,

//   // Autoplay settings
//   autoplay: {
//     delay: 5000,
//     disableOnInteraction: false,
//   },

//   // Pagination settings
//   pagination: {
//     el: '.swiper-pagination',
//     clickable: true,
//   },

//   // Navigation buttons
//   navigation: {
//     nextEl: '.swiper-button-next',
//     prevEl: '.swiper-button-prev',
//   },

//   // Slide transition effect
//   effect: 'fade',
//   speed: 800,
// });

// // ------------------------------------------------------------
// // Top-Secction-Slider
// document.addEventListener('DOMContentLoaded', function () {
//   // تابع عمومی برای تنظیم اسلایدرها
//   function initializeSwiper(containerSelector, nextButtonSelector, prevButtonSelector) {
//     const container = document.querySelector(containerSelector);
//     if (container) {
//       new Swiper(containerSelector, {
//         effect: 'cards', // استفاده از افکت کارت
//         speed: 500,
//         grabCursor: true, // تغییر ظاهر موس
//         slidesPerView: 1, // تعداد اسلایدهای همزمان
//         loop: true, // تکرار اسلایدها
//         // autoplay: {
//         //   delay: 5000,
//         //   disableOnInteraction: false,
//         // },
//         navigation: {
//           nextEl: nextButtonSelector,
//           prevEl: prevButtonSelector,
//         },
//       });
//     } else {
//       console.error(`Element ${containerSelector} not found!`);
//     }
//   }

//   // تنظیم اسلایدرهای مختلف
//   initializeSwiper('.topSalon-swiper-container', '.swiper-button-next', '.swiper-button-prev');
//   initializeSwiper('.topStylist-swiper-container', '.swiper-button-next', '.swiper-button-prev');
//   initializeSwiper('.topService-swiper-container', '.swiper-button-next', '.swiper-button-prev');

// });

// // ================================================================
// // Back TO TOp
// const backToTopButton = document.querySelector('.back-to-top');

// // نمایش یا مخفی کردن دکمه هنگام اسکرول
// window.addEventListener('scroll', () => {
//   if (window.scrollY > 200) {
//     backToTopButton.style.display = 'flex'; // نمایش دکمه
//   } else {
//     backToTopButton.style.display = 'none'; // مخفی کردن دکمه
//   }
// });

// // عملکرد کلیک دکمه
// backToTopButton.addEventListener('click', () => {
//   window.scrollTo({
//     top: 0,
//     behavior: 'smooth'
//   });
// });

// // ============================================================

// /*********************************************************************
//  * نام فایل: modals.js
//  * توضیح: مدیریت مودال‌ها (بازکردن، بستن و AJAX) به‌گونه‌ای که هر مودال
//  *        مستقل عمل کند و بستن یک مودال باعث بسته‌شدنِ مودال دیگر نشود.
//  *********************************************************************/

// /**
//  * دریافت کامنت‌های استایلیست و نمایش آن‌ها در مودال #commentModal
//  * @param {number} stylist_id
//  */
// function get_stylist_comments(stylist_id) {
//   $.ajax({
//     type: "GET",
//     url: `/csf/get_stylist_comments/${stylist_id}/`,
//     success: function (res) {
//       // درج محتوای دریافت‌شده در مودال
//       $("#commentModal .modal-body").html(res);
//       // نمایش مودال
//       $("#commentModal").fadeIn();
//     },
//     error: function () {
//       alert("خطایی رخ داده است، لطفاً مجدداً تلاش کنید.");
//     }
//   });
// }

// /**
//  * دریافت لیست قیمت استایلیست و نمایش آن در مودال #priceListModal
//  * @param {number} stylist_id
//  */
// function get_stylist_priceList(stylist_id) {
//   $.ajax({
//     type: "GET",
//     url: `/stylists/get_stylist_priceList/${stylist_id}/`,
//     success: function (res) {
//       $("#priceListModal .modal-body").html(res);
//       $("#priceListModal").fadeIn();
//     },
//     error: function () {
//       alert("خطایی رخ داده است، لطفاً مجدداً تلاش کنید.");
//     }
//   });
// }

// /**
//  * دریافت نمونه‌کار استایلیست (نسخهٔ کارت) و نمایش آن در مودال #workSamplesModal
//  * @param {number} stylist_id
//  */
// function get_stylist_worksample_card(stylist_id) {
//   $.ajax({
//     type: "GET",
//     url: `/stylists/get_worksamples_stylist_card/${stylist_id}/`,
//     success: function (res) {
//       $("#workSamplesModal .modal-body").html(res);
//       $("#workSamplesModal").fadeIn();
//     },
//     error: function () {
//       alert("خطایی رخ داده است، لطفاً مجدداً تلاش کنید.");
//     }
//   });
// }

// /**
//  * بزرگ‌نمایی یک تصویر در مودال مجزا (#imageModal)
//  * بدون بستن سایر مودال‌ها
//  * @param {string} imageUrl
//  */
// function enlargeImage(imageUrl) {
//   // ابتدا محتوای قبلی مودال تصویر را پاک کنیم
//   $("#imageModal .modal-body").empty();

//   // ساخت تگ <img> برای تصویر بزرگ
//   const largeImage = `
//     <img
//       src="${imageUrl}"
//       alt="تصویر بزرگ"
//       class="full-screen-img"
//       style="width: 100%; height: auto;"
//     />
//   `;

//   // افزودن تصویر به بدنهٔ مودال
//   $("#imageModal .modal-body").html(largeImage);

//   // نمایش مودال
//   $("#imageModal").fadeIn();
// }

// /**********************************************************************
//  * مدیریت رویدادِ بسته‌شدنِ مودال‌ها
//  * - با کلیک روی دکمهٔ بستن (کلاس .modal-close)
//  * - با کلیک بیرون از محتوای مودال (اما فقط همان مودال بسته شود)
//  **********************************************************************/

// /**
//  * بستن هر مودال با کلیک روی دکمهٔ ضربدر داخل آن
//  * نکته:  از آن‌جا که همهٔ دکمه‌های بستن دارای کلاس .modal-close هستند،
//  *        تنها کاری که می‌کنیم گرفتن نزدیک‌ترین .modal والد آن است و بستن آن.
//  */
// $(document).on("click touchend", ".modal-close", function (e) {
//   e.preventDefault();
//   // نزدیک‌ترین پدرِ دارای کلاس .modal را محو می‌کنیم
//   $(this).closest(".modal").fadeOut();
// });

// /**
//  * بستن اختصاصی هریک از مودال‌ها با کلیک بیرون از ناحیهٔ .modal-content
//  * تا فقط همان مودال بسته شود، نه سایر مودال‌ها.
//  *
//  * برای هر مودال جداگانه یک رویداد می‌نویسیم؛
//  * مثلاً اگر در پشتِ #workSamplesModal کلیک شد، فقط آن مودال بسته شود.
//  */

// // بستن مودال کامنت‌ها (commentModal)
// $(document).on("click touchend", "#commentModal", function (e) {
//   // اگر روی خودِ پس‌زمینه (و نه فرزند آن) کلیک شده باشد...
//   if (e.target.id === "commentModal") {
//     $("#commentModal").fadeOut();
//   }
// });

// // بستن مودال لیست قیمت (priceListModal)
// $(document).on("click touchend", "#priceListModal", function (e) {
//   if (e.target.id === "priceListModal") {
//     $("#priceListModal").fadeOut();
//   }
// });

// // بستن مودال نمونه‌کار (workSamplesModal)
// $(document).on("click touchend", "#workSamplesModal", function (e) {
//   if (e.target.id === "workSamplesModal") {
//     $("#workSamplesModal").fadeOut();
//   }
// });

// // بستن مودال تصویر (imageModal)
// $(document).on("click touchend", "#imageModal", function (e) {
//   if (e.target.id === "imageModal") {
//     $("#imageModal").fadeOut();
//   }
// });

// // ================================================================================

// function get_service_comments(service_id) {
//   $.ajax({
//     type: "GET",
//     url: `/csf/get_service_comments/${service_id}/`,
//     success: function (res) {
//       // درج محتوای دریافت‌شده در مودال
//       $("#commentModal .modal-body").html(res);
//       // نمایش مودال
//       $("#commentModal").fadeIn();
//     },
//     error: function () {
//       alert("خطایی رخ داده است، لطفاً مجدداً تلاش کنید.");
//     }
//   });
// }

// /**
//  * دریافت لیست قیمت استایلیست و نمایش آن در مودال #priceListModal
//  * @param {number} service_id
//  */
// function get_service_priceList(service_id) {
//   $.ajax({
//     type: "GET",
//     url: `/services/service_card_priceList/${service_id}/`,
//     success: function (res) {
//       $("#priceListModal .modal-body").html(res);
//       $("#priceListModal").fadeIn();
//     },
//     error: function () {
//       alert("خطایی رخ داده است، لطفاً مجدداً تلاش کنید.");
//     }
//   });
// }

// /**
//  * دریافت نمونه‌کار استایلیست (نسخهٔ کارت) و نمایش آن در مودال #workSamplesModal
//  * @param {number} service_id
//  */
// function get_service_worksample_card(stylist_id) {
//   $.ajax({
//     type: "GET",
//     url: `/services/service_card_workSamples/${stylist_id}/`,
//     success: function (res) {
//       $("#workSamplesModal .modal-body").html(res);
//       $("#workSamplesModal").fadeIn();
//     },
//     error: function () {
//       alert("خطایی رخ داده است، لطفاً مجدداً تلاش کنید.");
//     }
//   });
// }

// /**********************************************************************
//  * مدیریت رویدادِ بسته‌شدنِ مودال‌ها
//  * - با کلیک روی دکمهٔ بستن (کلاس .modal-close)
//  * - با کلیک بیرون از محتوای مودال (اما فقط همان مودال بسته شود)
//  **********************************************************************/

// /**
//  * بستن هر مودال با کلیک روی دکمهٔ ضربدر داخل آن
//  * نکته:  از آن‌جا که همهٔ دکمه‌های بستن دارای کلاس .modal-close هستند،
//  *        تنها کاری که می‌کنیم گرفتن نزدیک‌ترین .modal والد آن است و بستن آن.
//  */
// $(document).on("click touchend", ".modal-close", function (e) {
//   e.preventDefault();
//   // نزدیک‌ترین پدرِ دارای کلاس .modal را محو می‌کنیم
//   $(this).closest(".modal").fadeOut();
// });

// /**
//  * بستن اختصاصی هریک از مودال‌ها با کلیک بیرون از ناحیهٔ .modal-content
//  * تا فقط همان مودال بسته شود، نه سایر مودال‌ها.
//  *
//  * برای هر مودال جداگانه یک رویداد می‌نویسیم؛
//  * مثلاً اگر در پشتِ #workSamplesModal کلیک شد، فقط آن مودال بسته شود.
//  */

// // بستن مودال کامنت‌ها (commentModal)
// $(document).on("click touchend", "#commentModal", function (e) {
//   // اگر روی خودِ پس‌زمینه (و نه فرزند آن) کلیک شده باشد...
//   if (e.target.id === "commentModal") {
//     $("#commentModal").fadeOut();
//   }
// });

// // بستن مودال لیست قیمت (priceListModal)
// $(document).on("click touchend", "#priceListModal", function (e) {
//   if (e.target.id === "priceListModal") {
//     $("#priceListModal").fadeOut();
//   }
// });

// // بستن مودال نمونه‌کار (workSamplesModal)
// $(document).on("click touchend", "#workSamplesModal", function (e) {
//   if (e.target.id === "workSamplesModal") {
//     $("#workSamplesModal").fadeOut();
//   }
// });

// // بستن مودال تصویر (imageModal)
// $(document).on("click touchend", "#imageModal", function (e) {
//   if (e.target.id === "imageModal") {
//     $("#imageModal").fadeOut();
//   }
// });

// // ===============================================================================================
// // All Services
// let selectedSubGroupID = null;
// let currentSortType = 0; // 0 برای "محبوب‌ترین‌ها" به عنوان پیش‌فرض
// let currentSortTitle = "محبوب‌ترین‌ها";

// // ------------------------ AJAX ها ------------------------
// function get_subgroups(group_id) {
//   $.ajax({
//     type: 'GET',
//     url: `/services/get_subgroups/${group_id}/`,
//     success: function (data) {
//       if (data.error) {
//         console.log(data.error)
//       } else {
//         // تغییر عنوان گروه انتخابی
//         $('#all-services-selected-group-title').text(data.group_title)
//         // پاک کردن لیست زیرگروه‌های قبلی
//         const $subgroupsContainer = $('#all-services-filters-container')
//         $subgroupsContainer.empty()

//         // ساخت دکمه‌های جدید
//         data.subgroups.forEach((subgroup) => {
//           const $button = $('<button>')
//             .attr('id', subgroup.id)
//             .text(subgroup.title)
//             .on('click', function () {
//               // حذف کلاس active از همه دکمه‌های قدیمی
//               $('.all-services-filters-container button').removeClass('active')
//               // افزودن کلاس active به دکمه کلیک شده
//               $(this).addClass('active')
//               // بارگذاری خدمات زیرگروه
//               get_service_of_subgroups(subgroup.id)
//             })
//           $subgroupsContainer.append($button)
//         })
//         // بعد از ایجاد دکمه‌ها و رندر، دکمه های اسکرول را مجدد بررسی کن
//         updateScrollButtons()
//       }
//     },
//     error: function () {
//       alert('خطایی رخ داده است، لطفاً مجدداً تلاش کنید.')
//     }
//   })
// }

// function get_service_of_subgroups(subgroup_id) {
//   $.ajax({
//     type: 'GET',
//     url: `/services/get_service_of_sorting/${subgroup_id}/${currentSortType}/`,
//     success: function (htmlContent) {
//       $('#all-services-services-container').html(htmlContent);
//       selectedSubGroupID = subgroup_id;
//     },
//     error: function () {
//       alert('خطایی در بارگذاری خدمات رخ داده است.');
//     }
//   });
// }

// function selectSortOption(sort_type, sort_title) {
//   if (!selectedSubGroupID) {
//     alert('ابتدا یک گروه را انتخاب کنید!');
//     $('#all-services-sortOptions').removeClass('show');
//     return;
//   }
//   currentSortType = sort_type;
//   currentSortTitle = sort_title;
//   $('#all-services-sortTitleSpan').text(sort_title);
//   $('#all-services-sortOptions').removeClass('show');

//   $.ajax({
//     type: 'GET',
//     url: `/services/get_service_of_sorting/${selectedSubGroupID}/${sort_type}/`,
//     success: function (htmlContent) {
//       $('#all-services-services-container').html(htmlContent);
//     },
//     error: function () {
//       alert('خطایی در مرتب‌سازی خدمات رخ داده است.');
//     }
//   });
// }

// // ------------------------ مرتب‌سازی منوی کشویی ------------------------
// function setupSortDropdown() {
//   // کلیک روی دکمه
//   $('#all-services-sortDropdownButton').click(function (e) {
//     e.preventDefault()
//     $('#all-services-sortOptions').toggleClass('show')
//   })
//   // کلیک خارج از منوی کشویی
//   $(document).click(function (event) {
//     if (!$(event.target).closest('.all-services-sort-dropdown').length) {
//       $('#all-services-sortOptions').removeClass('show')
//     }
//   })
// }

// // ------------------------ مدیریت دکمه‌های اسکرول چپ/راست ------------------------
// function updateScrollButtons() {
//   const $scrollLeftBtn = $('#all-services-scrollLeftBtn')
//   const $scrollRightBtn = $('#all-services-scrollRightBtn')
//   const $filtersContainer = $('#all-services-filters-container')

//   const scrollLeft = $filtersContainer.scrollLeft()
//   const scrollWidth = $filtersContainer[0].scrollWidth
//   const clientWidth = $filtersContainer.outerWidth()

//   // اگر در ابتدای لیست هستیم
//   if (scrollLeft <= 0) {
//     $scrollLeftBtn.hide()
//   } else {
//     $scrollLeftBtn.show()
//   }

//   // اگر در انتهای لیست هستیم
//   if (scrollLeft + clientWidth >= scrollWidth - 1) {
//     $scrollRightBtn.hide()
//   } else {
//     $scrollRightBtn.show()
//   }
// }

// function setupScrollButtons() {
//   const $filtersContainer = $('#all-services-filters-container')
//   const $scrollLeftBtn = $('#all-services-scrollLeftBtn')
//   const $scrollRightBtn = $('#all-services-scrollRightBtn')

//   // رویداد اسکرول برای به‌روزرسانی دکمه‌ها
//   $filtersContainer.on('scroll', function () {
//     updateScrollButtons()
//   })

//   // کلیک روی دکمه چپ
//   $scrollLeftBtn.on('click', function () {
//     $filtersContainer.animate({ scrollLeft: '-=100' }, 300, updateScrollButtons)
//   })

//   // کلیک روی دکمه راست
//   $scrollRightBtn.on('click', function () {
//     $filtersContainer.animate({ scrollLeft: '+=100' }, 300, updateScrollButtons)
//   })

//   // برای بار اول نیز اجرا شود
//   updateScrollButtons()
// }

// // ------------------------ فعال‌سازی دکمه فیلتر انتخاب‌شده ------------------------
// function setupStickyHover() {
//   $(document).on('click', '.all-services-filters-container button', function () {
//     $('.all-services-filters-container button').removeClass('active')
//     $(this).addClass('active')
//   })
// }

// // ------------------------ ready ------------------------
// $(document).ready(function () {
//   setupStickyHover()
//   setupSortDropdown()
//   setupScrollButtons()
// })

// // ==============================================================
// //  Service_Detail

// // // --- اسکریپت آکاردیون ---
// // const accordionHeaders = document.querySelectorAll('.serviceDetails-accordion-header');

// // accordionHeaders.forEach(header => {
// //   header.addEventListener('click', function () {
// //     const contentId = header.getAttribute('data-accordion');
// //     const content = document.getElementById(contentId);

// //     // اگر همین آکاردیون باز باشد، ببندیم
// //     if (header.classList.contains('active')) {
// //       header.classList.remove('active');
// //       content.classList.remove('show');
// //       header.querySelector('i').classList.remove('fa-chevron-up');
// //       header.querySelector('i').classList.add('fa-chevron-down');
// //     } else {
// //       // بقیه آکاردیون‌ها را ببند
// //       accordionHeaders.forEach(h => {
// //         h.classList.remove('active');
// //         h.querySelector('i').classList.remove('fa-chevron-up');
// //         h.querySelector('i').classList.add('fa-chevron-down');
// //       });
// //       document.querySelectorAll('.serviceDetails-accordion-content').forEach(c => c.classList.remove('show'));

// //       // آکاردیون کلیک‌شده را باز کن
// //       header.classList.add('active');
// //       content.classList.add('show');
// //       // آیکن را تغییر بده
// //       header.querySelector('i').classList.remove('fa-chevron-down');
// //       header.querySelector('i').classList.add('fa-chevron-up');
// //     }
// //   });
// // });

// // --- اسلایدر مقالات (Swiper) ---
// var articleSwiper = new Swiper('.myArticleSwiper', {
//   loop: true,
//   slidesPerView: 1,
//   spaceBetween: 20,
//   breakpoints: {
//     768: {
//       slidesPerView: 2,
//     },
//     1024: {
//       slidesPerView: 3,
//     },
//   },
//   // اگر خواستید ناوبری داشته باشید
//   // navigation: {
//   //   nextEl: '.myArticleSwiper .swiper-button-next',
//   //   prevEl: '.myArticleSwiper .swiper-button-prev',
//   // },
//   pagination: {
//     el: '.myArticleSwiper .swiper-pagination',
//     clickable: true,
//   },
// });

// // ===========================================
// // Filter

// document.addEventListener('DOMContentLoaded', function () {
//   // هدرهای آکاردیون ساده (نمایش توضیحات و آرایشگران)
//   const accordions = document.querySelectorAll('.serviceDetails-accordion-header');
//   accordions.forEach(header => {
//     header.addEventListener('click', () => {
//       // کلاس active عوض شود
//       header.classList.toggle('active');
//       // فلش بالا/پایین
//       let icon = header.querySelector('i.fa');
//       if (icon) {
//         icon.classList.toggle('fa-chevron-up');
//         icon.classList.toggle('fa-chevron-down');
//       }
//       // محتوای مربوطه
//       let contentId = header.getAttribute('data-accordion');
//       let contentEl = document.getElementById(contentId);
//       if (contentEl) {
//         contentEl.classList.toggle('show');
//       }
//     });
//   });

//   // باز کردن کشو با کلیک روی آیکن فیلتر
//   const openFilterBtn = document.getElementById('openFilterModal');
//   // بستن کشو با کلیک روی آیکن ضربدر
//   const closeFilterBtn = document.getElementById('closeFilterModal');
//   const filterDrawer = document.getElementById('filterDrawer');

//   if (openFilterBtn && closeFilterBtn && filterDrawer) {
//     openFilterBtn.addEventListener('click', function () {
//       filterDrawer.classList.add('active');
//     });
//     closeFilterBtn.addEventListener('click', function () {
//       filterDrawer.classList.remove('active');
//     });
//   }
// });

// ======================================== (ذخیره لوکیشن کاربر درسشن )=====================================
