// static/js/pages/dashboard_home.js
// page: dashboard_home

export function init() {
  console.debug('[dashboard_home] init - Starting dashboard initialization');

  const root = document.querySelector('.dashboard-home-page');
  if (!root) {
    console.error('[dashboard_home] Root element .dashboard-home-page not found');
    return;
  }

  console.debug('[dashboard_home] Root element found, initializing...');

  // -------------------------------
  // Back button (no inline JS)
  // -------------------------------
  const backBtn = root.querySelector('[data-action="go-back"]');
  if (backBtn) {
    backBtn.addEventListener('click', (e) => {
      e.preventDefault();
      const fallback = backBtn.getAttribute('data-fallback-url') || '/';
      if (window.history.length > 1) {
        window.history.back();
      } else {
        window.location.assign(fallback);
      }
    });
    console.debug('[dashboard_home] Back button initialized');
  }

  // -------------------------------
  // Initialize Charts immediately
  // -------------------------------
  initializeDashboardCharts();

  // -------------------------------
  // Optional: switch views (home / appointments)
  // -------------------------------
  const viewHome = document.getElementById('home-view');
  const viewAppts = document.getElementById('appointments-view');
  
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-show]');
    if (!btn) return;
    const target = btn.getAttribute('data-show');
    if (!target) return;
    
    if (viewHome && viewAppts) {
      viewHome.style.display = target === 'home' ? '' : 'none';
      viewAppts.style.display = target === 'appointments' ? '' : 'none';
      
      if (target === 'home') initializeDashboardCharts();
      if (target === 'appointments') initializeDashboardCharts();
    }
  });

  console.debug('[dashboard_home] Initialization complete');
}

// -------------------------------
// Chart Functions
// -------------------------------
function initializeDashboardCharts() {
  console.debug('[dashboard_home] Initializing charts...');
  
  // بررسی وجود نمودارهای مختلف
  const salesChart = document.getElementById('salesChart');
  const appointmentsChart = document.getElementById('appointmentsChart');
  
  if (salesChart) {
    console.debug('[dashboard_home] Sales chart canvas found');
    initializeSalesChart();
  }
  
  if (appointmentsChart) {
    console.debug('[dashboard_home] Appointments chart canvas found');
    initializeAppointmentsChart();
  }
  
  // Chart.js را لود کنیم اگر وجود نداشته باشد
  maybeLoadChartJS();
}

function initializeSalesChart() {
  const canvas = document.getElementById('salesChart');
  if (!canvas) return;
  
  // بررسی وجود داده‌های نمودار در window
  if (typeof window.salesChartData !== 'undefined') {
    console.debug('[dashboard_home] Sales chart data found in window');
    createSalesChart(window.salesChartData);
  } else {
    // جستجو برای داده‌ها در script tags
    const scripts = document.querySelectorAll('script');
    for (let script of scripts) {
      if (script.textContent.includes('salesChartData')) {
        console.debug('[dashboard_home] Sales chart data found in script');
        // اجرای script برای تعریف متغیر
        try {
          eval(script.textContent);
          if (typeof salesChartData !== 'undefined') {
            createSalesChart(salesChartData);
          }
        } catch (e) {
          console.error('[dashboard_home] Error executing sales chart script:', e);
        }
        break;
      }
    }
  }
}

function initializeAppointmentsChart() {
  const canvas = document.getElementById('appointmentsChart');
  if (!canvas) return;
  
  // بررسی وجود داده‌های نمودار
  if (typeof window.upcomingAppointmentsData !== 'undefined') {
    console.debug('[dashboard_home] Appointments chart data found in window');
    createAppointmentsChart(window.upcomingAppointmentsData);
  } else {
    // جستجو برای داده‌ها در script tags
    const scripts = document.querySelectorAll('script');
    for (let script of scripts) {
      if (script.textContent.includes('upcomingAppointmentsData')) {
        console.debug('[dashboard_home] Appointments chart data found in script');
        try {
          eval(script.textContent);
          if (typeof upcomingAppointmentsData !== 'undefined') {
            createAppointmentsChart(upcomingAppointmentsData);
          }
        } catch (e) {
          console.error('[dashboard_home] Error executing appointments chart script:', e);
        }
        break;
      }
    }
  }
}

function maybeLoadChartJS() {
  if (typeof window.Chart !== 'undefined') {
    console.debug('[dashboard_home] Chart.js already loaded');
    return;
  }
  
  console.debug('[dashboard_home] Loading Chart.js...');
  loadScript('https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js')
    .then(() => {
      console.debug('[dashboard_home] Chart.js loaded successfully');
      // دوباره تلاش برای ایجاد نمودارها
      setTimeout(() => {
        initializeSalesChart();
        initializeAppointmentsChart();
      }, 100);
    })
    .catch((err) => {
      console.error('[dashboard_home] Failed to load Chart.js:', err);
    });
}

function createSalesChart(data) {
  if (typeof window.Chart === 'undefined') {
    console.warn('[dashboard_home] Chart.js not loaded yet for sales chart');
    return;
  }
  
  const canvas = document.getElementById('salesChart');
  if (!canvas) return;
  
  console.debug('[dashboard_home] Creating sales chart with data:', data);
  
  try {
    // نابود کردن نمودار قبلی اگر وجود دارد
    if (canvas._chartInstance) {
      canvas._chartInstance.destroy();
    }
    
    const ctx = canvas.getContext('2d');
    canvas._chartInstance = new window.Chart(ctx, {
      type: 'line',
      data: {
        labels: data.map(item => item.date),
        datasets: [
          {
            label: 'فروش',
            data: data.map(item => item.sales),
            borderColor: '#8B5CF6',
            backgroundColor: 'rgba(139, 92, 246, 0.1)',
            tension: 0.4
          },
          {
            label: 'نوبت‌ها',
            data: data.map(item => item.appointments),
            borderColor: '#10B981',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            tension: 0.4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    });
    
    console.debug('[dashboard_home] Sales chart created successfully');
  } catch (e) {
    console.error('[dashboard_home] Error creating sales chart:', e);
  }
}

function createAppointmentsChart(data) {
  if (typeof window.Chart === 'undefined') {
    console.warn('[dashboard_home] Chart.js not loaded yet for appointments chart');
    return;
  }
  
  const canvas = document.getElementById('appointmentsChart');
  if (!canvas) return;
  
  console.debug('[dashboard_home] Creating appointments chart with data:', data);
  
  try {
    if (canvas._chartInstance) {
      canvas._chartInstance.destroy();
    }
    
    const ctx = canvas.getContext('2d');
    canvas._chartInstance = new window.Chart(ctx, {
      type: 'bar',
      data: {
        labels: data.map(item => item.date),
        datasets: [
          {
            label: 'تایید شده',
            data: data.map(item => item.confirmed),
            backgroundColor: '#8B5CF6'
          },
          {
            label: 'لغو شده',
            data: data.map(item => item.canceled),
            backgroundColor: '#EF4444'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    });
    
    console.debug('[dashboard_home] Appointments chart created successfully');
  } catch (e) {
    console.error('[dashboard_home] Error creating appointments chart:', e);
  }
}

function loadScript(src) {
  return new Promise((resolve, reject) => {
    // بررسی اگر script قبلاً لود شده
    const existingScript = document.querySelector(`script[src="${src}"]`);
    if (existingScript) {
      resolve();
      return;
    }
    
    const script = document.createElement('script');
    script.src = src;
    script.async = true;
    script.onload = resolve;
    script.onerror = reject;
    document.head.appendChild(script);
  });
}

// تعریف توابع سراسری برای استفاده در template ها
window.createDynamicSalesChart = function(data) {
  window.salesChartData = data;
  createSalesChart(data);
};

window.createDynamicAppointmentsChart = function(data) {
  window.upcomingAppointmentsData = data;
  createAppointmentsChart(data);
};

console.debug('[dashboard_home] Module loaded successfully');