// page: search_page
export function init(){
  console.debug('[search_page] init');
  // TODO: /*** متغیرهای سراسری ***/
  let map, markersLayer;
  let allSalons = [];

  /*** تابع دریافت CSRF Token ***/
  const getCookie = (name) => {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name + "=")) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  };
  /*** تابع تنظیم کوکی ***/
  const setCookie = (name, value, days) => {
    let expires = "";
    if (days) {
      const date = new Date();
      date.setTime(date.getTime() + days * 24 * 60 * 60 * 1000);
      expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "") + expires + "; path=/";
  };

  /*** مدیریت موقعیت کاربر با callback اختیاری ***/
  const handleUserLocation = (callback = () => {}) => {
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          const openLocationModalBtn =
            document.getElementById("openLocationModal");
          const locationInput = document.getElementById("locationSearchInput");

          // به جای نمایش مختصات، فقط عبارت "موقعیت فعلی" نمایش داده می‌شود
          const locationText = `موقعیت فعلی`;
          openLocationModalBtn.innerHTML = `<i class="fa-solid fa-location-dot"></i> ${locationText}`;
          locationInput.value = locationText;

          if (map) {
            map.setView([latitude, longitude], 14);
            L.marker([latitude, longitude], {
              icon: L.icon({
                iconUrl: "/static/images/icons/user_marker.png",
                iconSize: [40, 40],
                iconAnchor: [20, 40],
              }),
            }).addTo(markersLayer);
          }
          callback();
        },
        (error) => {
          console.error("خطا در دریافت موقعیت:", error);
          map.setView([35.6892, 51.389], 12);
          callback();
        },
        { enableHighAccuracy: true, timeout: 10000 }
      );
    } else {
      alert("مرورگر شما از سرویس مکانیابی پشتیبانی نمی‌کند!");
      map.setView([35.6892, 51.389], 12);
      callback();
    }
  };

  /*** مدیریت پاپ‌آپ درخواست دسترسی به موقعیت ***/
  const initLocationPermission = () => {
    // اگر کوکی "location_set" وجود داشته باشد، پاپ‌آپ نمایش داده نمی‌شود
    if (getCookie("location_set") === "true") {
      handleUserLocation();
      return;
    }

    const initialLocationModal = document.getElementById(
      "initialLocationModal"
    );
    const allowLocationBtn = document.getElementById("allowLocation");
    const denyLocationBtn = document.getElementById("denyLocation");

    // نمایش مدال به محض بارگیری صفحه
    initialLocationModal.style.display = "block";

    allowLocationBtn.addEventListener("click", () => {
      handleUserLocation(() => {
        // ذخیره کوکی برای جلوگیری از نمایش مجدد پاپ‌آپ (به مدت ۳۰ روز)
        setCookie("location_set", "true", 30);
        initialLocationModal.style.display = "none";
      });
    });

    denyLocationBtn.addEventListener("click", () => {
      map.setView([35.6892, 51.389], 12);
      // حتی در صورت عدم دریافت موقعیت، کوکی تنظیم می‌شود تا پاپ‌آپ دوباره نشان داده نشود
      setCookie("location_set", "true", 30);
      initialLocationModal.style.display = "none";
    });
  };

  /*** راه‌اندازی نقشه ***/
  const initMap = () => {
    map = L.map("map", { zoomControl: false });
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution:
        'Map data © <a href="https://openstreetmap.org">OpenStreetMap</a> contributors',
    }).addTo(map);

    const tehranBounds = L.latLngBounds(
      L.latLng(35.5, 50.9),
      L.latLng(35.9, 51.6)
    );
    map.setMaxBounds(tehranBounds);
    markersLayer = L.layerGroup().addTo(map);
  };

  /*** نمایش سالن‌ها روی نقشه ***/
  const displaySalonsOnMap = (salons) => {
    markersLayer.clearLayers();
    salons.forEach((salon) => {
      const [lng, lat] = salon.location.coordinates;
      if (lat && lng) {
        const customIcon = L.icon({
          iconUrl: "/static/images/icons/marker.png",
          iconSize: [50, 50],
          iconAnchor: [25, 50],
        });

        const popupContent = `
          <div class="salons-card">
            <a href="/detail_salon/${
              salon.id
            }" class="salons-card-image">
              <img src="${salon.banner_image}" alt="${salon.salon_name}" />
            </a>
            <div class="salons-card-details">
              <h3 class="salons-card-title">
                ${salon.salon_name}
                ${
                  salon.discount
                    ? `<span class="salons-card-discount">${salon.discount}%</span>`
                    : ""
                }
              </h3>
              <p class="salons-card-address">${salon.address}</p>
              <div class="salons-card-body">
                <p><i class="fas fa-star"></i> &nbsp&nbsp ${
                  salon.get_average_score
                }</p>
                <p><i class="fas fa-location-dot"></i> &nbsp&nbsp ${
                  salon.zone
                } کیلومتر</p>
              </div>
            </div>
          </div>
        `;

        L.marker([lat, lng], { icon: customIcon })
          .addTo(markersLayer)
          .bindPopup(popupContent, { maxWidth: 180, minWidth: 160 });
      }
    });
  };

  /*** نمایش نتایج در پنل ***/
  const displayResults = (salons) => {
    const resultsContent = document.getElementById("results-content");
    resultsContent.innerHTML = "";

    if (!salons.length) {
      resultsContent.innerHTML = "<p>نتیجه‌ای یافت نشد</p>";
      return;
    }

    salons.forEach((salon) => {
      const card = document.createElement("div");
      card.classList.add("salons-card");
      card.innerHTML = `
        <a href="/detail_salon/${salon.id}" class="salons-card-image">
          <img src="${salon.banner_image}" alt="${salon.salon_name}" />
        </a>
        <div class="salons-card-details">
          <h3 class="salons-card-title">${salon.salon_name}</h3>
          <p class="salons-card-address">${salon.address}</p>
          <div class="salons-card-body">
            <p><i class="fas fa-star"></i> ${salon.get_average_score}</p>
            <p><i class="fas fa-map-marker-alt"></i> ${salon.neighborhood}</p>
          </div>
        </div>
      `;
      resultsContent.appendChild(card);
    });
  };

  /*** دریافت لیست سالن‌ها ***/
  const fetchSalonList = () => {
    fetch("/search/salon_list/")
      .then((response) => response.json())
      .then((data) => {
        allSalons = data.salons;
        displaySalonsOnMap(allSalons);
        displayResults(allSalons);
      })
      .catch((error) => console.error("خطا در دریافت سالن‌ها:", error));
  };

  /*** مدیریت فیلترها ***/
  const initFiltersPanel = () => {
    const filtersContainer = document.getElementById("filters-container");
    const handle = document.getElementById("handle");

    handle.addEventListener("click", () =>
      filtersContainer.classList.toggle("open")
    );

    let startY = 0,
      currentY = 0,
      isDragging = false;
    handle.addEventListener("touchstart", (e) => {
      startY = e.touches[0].clientY;
      isDragging = true;
    });
    handle.addEventListener("touchmove", (e) => {
      if (!isDragging) return;
      currentY = e.touches[0].clientY;
    });
    handle.addEventListener("touchend", () => {
      isDragging = false;
      if (startY - currentY > 50) filtersContainer.classList.add("open");
      if (currentY - startY > 50) filtersContainer.classList.remove("open");
    });

    document.querySelectorAll(".dropdown > button").forEach((button) => {
      button.addEventListener("click", function (e) {
        e.stopPropagation();
        document.querySelectorAll(".dropdown").forEach((drop) => {
          if (drop !== this.parentElement) drop.classList.remove("active");
        });
        this.parentElement.classList.toggle("active");
      });
    });

    document.querySelectorAll(".dropdown-content a").forEach((link) => {
      link.addEventListener("click", function (e) {
        e.preventDefault();
        const dropdown = this.closest(".dropdown");
        const button = dropdown.querySelector("button");
        button.innerHTML = `${this.textContent.trim()} `;
        button.classList.add("selected");
        dropdown.classList.remove("active");
      });
    });

    document.addEventListener("click", () => {
      document
        .querySelectorAll(".dropdown")
        .forEach((drop) => drop.classList.remove("active"));
    });

    const filterButton = document.getElementById("filter-button");
    const handleFilterButton = (e) => {
      e.preventDefault();
      e.stopPropagation();
      const sortButton = document.getElementById("sort-button");
      const priceButton = document.getElementById("price-button");
      const typeButton = document.getElementById("type-button");

      let sortValue = sortButton.classList.contains("selected")
        ? sortButton.textContent.trim()
        : "";
      let priceValue = priceButton.classList.contains("selected")
        ? priceButton.textContent.trim()
        : "";
      let neighborhood = typeButton.classList.contains("selected")
        ? typeButton.textContent.trim()
        : "";

      if (sortValue === "مرتب‌سازی") sortValue = "";
      if (priceValue === "قیمت") priceValue = "";
      if (neighborhood === "محله") neighborhood = "";

      let filterData = {
        sort: sortValue,
        price: priceValue,
        type: neighborhood,
      };

      if (sortValue === "نزدیکترین") {
        if ("geolocation" in navigator) {
          navigator.geolocation.getCurrentPosition(
            (position) => {
              filterData.latitude = position.coords.latitude;
              filterData.longitude = position.coords.longitude;
              fetch("/search/filter_salon/", {
                method: "POST",
                credentials: "same-origin", // ارسال کوکی‌ها
                headers: {
                  "Content-Type": "application/json",
                  "X-CSRFToken": getCookie("csrftoken"),
                },
                body: JSON.stringify(filterData),
              })
                .then((response) => response.json())
                .then((data) => {
                  displaySalonsOnMap(data.salons);
                  displayResults(data.salons);
                })
                .catch((error) =>
                  console.error("خطا در فیلتر کردن سالن‌ها:", error)
                );
            },
            (error) => {
              console.error("خطا در دریافت موقعیت کاربر:", error);
              alert("امکان دریافت موقعیت شما وجود ندارد.");
            }
          );
        } else {
          alert("مرورگر شما از Geolocation پشتیبانی نمی‌کند.");
        }
      } else {
        fetch("/search/filter_salon/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
          },
          body: JSON.stringify(filterData),
        })
          .then((response) => response.json())
          .then((data) => {
            displaySalonsOnMap(data.salons);
            displayResults(data.salons);
          })
          .catch((error) => console.error("خطا در فیلتر کردن سالن‌ها:", error));
      }
    };

    // استفاده از رویداد مناسب برای دستگاه‌های لمسی
    if ("ontouchstart" in window) {
      filterButton.addEventListener("touchend", (e) => {
        e.preventDefault();
        handleFilterButton(e);
      });
    } else {
      filterButton.addEventListener("click", handleFilterButton);
    }
  };

  /*** مدیریت جستجو ***/
  const initSearch = () => {
    const searchMenuButton = document.getElementById("searchMenu-button");
    const searchModal = document.getElementById("searchModal");
    const closeModalBtn = document.querySelector(".close-modal");
    const searchButton = document.getElementById("search-button");
    const searchInput = document.getElementById("search-input");
    const resultsContent = document.getElementById("results-content");
    const filtersContainer = document.getElementById("filters-container");

    searchMenuButton.addEventListener("click", (e) => {
      e.stopPropagation();
      searchModal.style.display = "block";
    });

    closeModalBtn.addEventListener(
      "click",
      () => (searchModal.style.display = "none")
    );

    window.addEventListener("click", (e) => {
      if (e.target === searchModal) searchModal.style.display = "none";
    });

    searchButton.addEventListener("click", () => {
      const query = searchInput.value.trim();
      resultsContent.innerHTML = "";
      filtersContainer.classList.add("open");
      resultsContent.innerHTML = "<p>در حال جستجو...</p>";

      if (!query) {
        resultsContent.innerHTML = "<p>لطفاً عبارت جستجو را وارد کنید</p>";
        return;
      }

      fetch(`/search/salon_search/?q=${encodeURIComponent(query)}`)
        .then((response) => response.json())
        .then((data) => {
          displaySalonsOnMap(data.salons);
          displayResults(data.salons);
          resultsContent.scrollTo(0, 0);
        })
        .catch((error) => {
          console.error("خطا در جستجو:", error);
          resultsContent.innerHTML = "<p>خطا در دریافت نتایج</p>";
        });
    });
  };

  /*** مدیریت مدال موقعیت ***/
  const initLocationModal = () => {
    const openLocationModalBtn = document.getElementById("openLocationModal");
    const locationModalElem = document.getElementById("locationModal");
    const backToSearchModalBtn = document.getElementById("backToSearchModal");
    const useCurrentLocationBtn = document.getElementById("useCurrentLocation");
    const locationInput = document.getElementById("locationSearchInput");
    const suggestionsContainer = document.getElementById("locationSuggestions");

    openLocationModalBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      // پاک کردن مقدار اینپوت تا placeholder نمایش داده شود
      locationInput.value = "";
      suggestionsContainer.innerHTML = "";
      locationModalElem.style.display = "block";
    });

    backToSearchModalBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      locationModalElem.style.display = "none";
    });

    window.addEventListener("click", (e) => {
      if (e.target === locationModalElem)
        locationModalElem.style.display = "none";
    });

    useCurrentLocationBtn.addEventListener("click", (e) => {
      e.preventDefault();
      // در اینجا می‌توانیم بدون callback، به صورت دستی مدال را ببندیم
      handleUserLocation();
      locationModalElem.style.display = "none";
    });

    let debounceTimerLocation = null;
    locationInput.addEventListener("input", () => {
      const query = locationInput.value.trim();
      suggestionsContainer.innerHTML = "";
      if (debounceTimerLocation) clearTimeout(debounceTimerLocation);
      if (query.length < 3) return;

      debounceTimerLocation = setTimeout(() => {
        const nominatimURL = `https://nominatim.openstreetmap.org/search?format=json&addressdetails=1&viewbox=50.9,35.5,51.6,35.9&bounded=1&limit=5&q=${encodeURIComponent(
          query
        )}`;
        fetch(nominatimURL)
          .then((response) => response.json())
          .then((data) => {
            if (!data || data.length === 0) {
              suggestionsContainer.innerHTML =
                "<div class='suggestion-item'>نتیجه‌ای یافت نشد</div>";
              return;
            }
            data.forEach((item) => {
              const parts = item.display_name.split(",");
              const suggestionText = parts.slice(0, 2).join(",").trim();
              const suggestionDiv = document.createElement("div");
              suggestionDiv.classList.add("suggestion-item");
              suggestionDiv.textContent = suggestionText;
              suggestionDiv.addEventListener("click", () => {
                locationInput.value = suggestionText;
                suggestionsContainer.innerHTML = "";
                if (map) {
                  const lat = parseFloat(item.lat);
                  const lon = parseFloat(item.lon);
                  map.setView([lat, lon], 16);
                  L.marker([lat, lon]).addTo(map);
                }
                openLocationModalBtn.innerHTML = `<i class="fa-solid fa-location-dot"></i> ${suggestionText}`;
                locationModalElem.style.display = "none";
              });
              suggestionsContainer.appendChild(suggestionDiv);
            });
          })
          .catch((error) =>
            console.error("خطا در دریافت پیشنهادات موقعیت:", error)
          );
      }, 300);
    });
  };

  /*** مدیریت مدال تاریخ ***/
  const initDateModal = () => {
    const openDateModalBtn = document.getElementById("openDateModal");
    const dateModalElem = document.getElementById("dateModal");
    const backToSearchModalFromDateBtn = document.getElementById(
      "backToSearchModalFromDate"
    );
    const confirmDateBtn = document.getElementById("confirmDate");
    const dateInput = document.getElementById("dateInput");
    const quickDateButtons = document.querySelectorAll(".quick-date");

    openDateModalBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      dateModalElem.style.display = "block";
    });

    backToSearchModalFromDateBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      dateModalElem.style.display = "none";
    });

    quickDateButtons.forEach((btn) => {
      btn.addEventListener("click", () => {
        quickDateButtons.forEach((b) => b.classList.remove("selected"));
        btn.classList.add("selected");
        const value = btn.getAttribute("data-value");
        if (value === "today") {
          dateInput.value = new Date().toISOString().split("T")[0];
        } else if (value === "tomorrow") {
          const tomorrow = new Date();
          tomorrow.setDate(tomorrow.getDate() + 1);
          dateInput.value = tomorrow.toISOString().split("T")[0];
        } else if (value === "all") {
          dateInput.value = "";
        }
      });
    });

    confirmDateBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      const selectedDate = dateInput.value;
      openDateModalBtn.innerHTML = `<i class="fa-solid fa-calendar"></i> ${
        selectedDate || "هر تاریخی"
      }`;
      dateModalElem.style.display = "none";
    });
  };

  /*** مدیریت مدال زمان ***/
  const initTimeModal = () => {
    const openTimeModalBtn = document.getElementById("openTimeModal");
    const timeModalElem = document.getElementById("timeModal");
    const backToSearchModalFromTimeBtn = document.getElementById(
      "backToSearchModalFromTime"
    );
    const confirmTimeBtn = document.getElementById("confirmTime");
    const timeFromSelect = document.getElementById("timeFrom");
    const timeToSelect = document.getElementById("timeTo");
    const quickTimeButtons = document.querySelectorAll(".quick-time");

    openTimeModalBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      timeModalElem.style.display = "block";
    });

    backToSearchModalFromTimeBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      timeModalElem.style.display = "none";
    });

    quickTimeButtons.forEach((btn) => {
      btn.addEventListener("click", () => {
        quickTimeButtons.forEach((b) => b.classList.remove("selected"));
        btn.classList.add("selected");
      });
    });

    confirmTimeBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      let selectedTime = "";
      const selectedQuick = document.querySelector(".quick-time.selected");
      if (selectedQuick) {
        selectedTime = selectedQuick.textContent.trim();
      } else {
        const fromTime = timeFromSelect.value;
        const toTime = timeToSelect.value;
        if (fromTime && toTime) selectedTime = `از ${fromTime} تا ${toTime}`;
      }
      selectedTime = selectedTime || "هر زمانی";
      openTimeModalBtn.innerHTML = `<i class="fa-solid fa-clock"></i> ${selectedTime}`;
      timeModalElem.style.display = "none";
    });
  };
  // اضافه کردن event listener به دکمه پاک کردن
  const clearBtn = document.querySelector(".clear-btn");
  clearBtn.addEventListener("click", () => {
    // ریست کردن فیلتر موقعیت
    const locationBtn = document.getElementById("openLocationModal");
    if (locationBtn) {
      locationBtn.innerHTML =
        '<i class="fa-solid fa-location-dot"></i>&nbsp;&nbsp;موقعیت فعلی';
    }
    const locationInput = document.getElementById("locationSearchInput");
    if (locationInput) {
      locationInput.value = "";
    }
    const suggestionsContainer = document.getElementById("locationSuggestions");
    if (suggestionsContainer) {
      suggestionsContainer.innerHTML = "";
    }

    // ریست کردن فیلتر تاریخ
    const dateBtn = document.getElementById("openDateModal");
    if (dateBtn) {
      dateBtn.innerHTML =
        '<i class="fa-solid fa-calendar"></i>&nbsp;&nbsp;هر تاریخی';
    }
    const dateInput = document.getElementById("dateInput");
    if (dateInput) {
      dateInput.value = "";
    }

    // ریست کردن فیلتر زمان
    const timeBtn = document.getElementById("openTimeModal");
    if (timeBtn) {
      timeBtn.innerHTML =
        '<i class="fa-solid fa-clock"></i>&nbsp;&nbsp;هر زمانی';
    }
    const timeFrom = document.getElementById("timeFrom");
    const timeTo = document.getElementById("timeTo");
    if (timeFrom) {
      timeFrom.selectedIndex = 0;
    }
    if (timeTo) {
      timeTo.selectedIndex = 0;
    }
  });

  /*** جستجوی Fresha ***/
  const initFreshaSearch = () => {
    const freshaSearchButton = document.getElementById("freshaSearchButton");
    freshaSearchButton.addEventListener("click", (e) => {
      e.stopPropagation();
      document.getElementById("searchModal").style.display = "none";

      const locationText = document
        .getElementById("openLocationModal")
        .innerText.trim();
      const dateText = document
        .getElementById("openDateModal")
        .innerText.trim();
      const timeText = document
        .getElementById("openTimeModal")
        .innerText.trim();
      const serviceGroupElem = document.querySelector(
        ".category-item.selected"
      );
      const serviceGroup = serviceGroupElem
        ? serviceGroupElem.getAttribute("data-service-id") ||
          serviceGroupElem.innerText.trim()
        : "";

      const resultsContent = document.getElementById("results-content");
      resultsContent.innerHTML = "<p>در حال جستجو...</p>";
      document.getElementById("filters-container").classList.add("open");

      const data = {
        location: locationText,
        date: dateText,
        time: timeText,
        service_group: serviceGroup,
      };

      fetch("/search/salonify_search/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify(data),
      })
        .then((response) => response.json())
        .then((data) => {
          displaySalonsOnMap(data.salons);
          displayResults(data.salons);
        })
        .catch((error) => {
          console.error("خطا در جستجو در Fresha:", error);
          resultsContent.innerHTML = "<p>خطا در دریافت نتایج</p>";
        });
    });
  };

  /*** راه‌اندازی اولیه ***/
  const initApp = () => {
    initMap();
    initLocationPermission(); // در این تابع بررسی می‌شود که آیا کوکی ذخیره شده؛ در غیر اینصورت پاپ‌آپ نمایش داده می‌شود.
    fetchSalonList();
    initFiltersPanel();
    initSearch();
    initLocationModal();
    initDateModal();
    initTimeModal();
    initFreshaSearch();
  };

    initApp();

}


