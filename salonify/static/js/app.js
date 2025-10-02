// salonify: app.js (ES Modules) — نسخه همگام با data-page="search_page"
const controllers = {
  /* صفحات عمومی */
  home:             () => import('./pages/home.js').then(m => m.init?.()),
  search_page:      () => import('./pages/search_page.js').then(m => m.init?.()),
  salons:           () => import('./pages/salons.js').then(m => m.init?.()),
  detail_salon:     () => import('./pages/detail_salon.js').then(m => m.init?.()),
  select_datetime:  () => import('./pages/select_datetime.js').then(m => m.init?.()),
  select_stylists:  () => import('./pages/select_stylists.js').then(m => m.init?.()),
  appointments:     () => import('./pages/appointments.js').then(m => m.init?.()),
  appointment_detail:() => import('./pages/appointment_detail.js').then(m => m.init?.()),

  /* سفارش/رزرو */
  order_cart:        () => import('./pages/order_cart.js').then(m => m.init?.()),
  reservation_detail:() => import('./pages/reservation_detail.js').then(m => m.init?.()),
  reservation_preview:() => import('./pages/reservation_preview.js').then(m => m.init?.()),
  check_out:         () => import('./pages/check_out.js').then(m => m.init?.()),

  /* داشبورد */
  dashboard_home:     () => import('./pages/dashboard_home.js').then(m => m.init?.()),
  add_services:       () => import('./pages/add_services.js').then(m => m.init?.()),
  add_stylist:        () => import('./pages/add_stylist.js').then(m => m.init?.()),
  salons_customers:   () => import('./pages/salons_customers.js').then(m => m.init?.()),
  salon_profile_creator:() => import('./pages/salon_profile_creator.js').then(m => m.init?.()),
  service_menu:       () => import('./pages/service_menu.js').then(m => m.init?.()),
  team_member:        () => import('./pages/team_member.js').then(m => m.init?.()),
  add_time_off:       () => import('./pages/add_time_off.js').then(m => m.init?.()),
  set_regular_shifts: () => import('./pages/set_regular_shifts.js').then(m => m.init?.()),
  scheduled_shifts:   () => import('./pages/scheduled_shifts.js').then(m => m.init?.()),
  membership:         () => import('./pages/dashboard_membership.js').then(m => m.init?.()),

  /* متفرقه */
  catalog:            () => import('./pages/catalog.js').then(m => m.init?.()),
  online_booking:     () => import('./pages/dashboard_online_booking.js').then(m => m.init?.()),
  all_stylists:       () => import('./pages/all_stylists.js').then(m => m.init?.()),
  stylist_detail:     () => import('./pages/stylist_detail.js').then(m => m.init?.()),
};

document.addEventListener('DOMContentLoaded', () => {
  const page = document.body.dataset.page;
  console.debug('[app] page =', page);  // برای تست
  if (page && controllers[page]) controllers[page]().catch(console.error);
});
