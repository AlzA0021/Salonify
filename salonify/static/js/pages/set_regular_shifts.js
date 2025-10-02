// static/js/pages/set_regular_shifts.js
// page: set_regular_shifts
// وابسته به jQuery و persian-datepicker که از CDN لود می‌شوند

export function init() {
  if (document.body.dataset.page !== 'set_regular_shifts') return;
  console.debug('[set_regular_shifts] init');

  // اطمینان از وجود jQuery و پلاگین تاریخ
  if (!window.jQuery) {
    console.error('[set_regular_shifts] jQuery not found');
    return;
  }
  const $ = window.jQuery;

  // --- تقویم‌های شمسی ---
  $('#start_date_input').persianDatepicker({
    observer: true,
    format: 'YYYY/MM/DD',
    altField: '#start_date',
    altFormat: 'YYYY-MM-DD',
    initialValue: false,
  });
  $('#end_date_input').persianDatepicker({
    observer: true,
    format: 'YYYY/MM/DD',
    altField: '#end_date',
    altFormat: 'YYYY-MM-DD',
    initialValue: false,
  });

  // --- دریافت ساعات کاری سالن از اسکریپت JSON تعبیه‌شده در تمپلیت ---
  let salonHours = {};
  try {
    const jsonEl = document.getElementById('salon-hours-json');
    salonHours = jsonEl ? JSON.parse(jsonEl.textContent || '{}') : {};
  } catch (e) {
    console.warn('[set_regular_shifts] failed to parse salonHours JSON', e);
    salonHours = {};
  }

  // ساخت گزینه‌های ساعت با گام ۳۰ دقیقه
  function generateTimeOptions(startTime, endTime) {
    let optionsHtml = '<option value="" disabled selected>انتخاب</option>';
    if (!startTime || !endTime) return optionsHtml;

    const start = new Date(`1970-01-01T${startTime}:00`);
    const end = new Date(`1970-01-01T${endTime}:00`);

    let current = start;
    while (current <= end) {
      const hours = String(current.getHours()).padStart(2, '0');
      const minutes = String(current.getMinutes()).padStart(2, '0');
      const timeValue = `${hours}:${minutes}`;
      optionsHtml += `<option value="${timeValue}">${timeValue}</option>`;
      current.setMinutes(current.getMinutes() + 30);
    }
    return optionsHtml;
  }

  const $modal = $('#shiftModal');
  const $modalBody = $('#modalBody');
  const $addShiftBtn = $('#addShiftBtn');
  let currentEditingDayIndex = null;

  // باز کردن مودال برای هر روز هفته
  $('.day-row').on('click', function () {
    currentEditingDayIndex = $(this).data('day-index');
    const dayName = $(this).data('day-name');
    const dayHours = salonHours[currentEditingDayIndex]; // {open, close} یا undefined

    $('#modalTitle').text(`شیفت‌های ${dayName}`);
    $modalBody.empty();

    if (!dayHours) {
      // روز تعطیل
      $modalBody.html(
        '<p style="text-align: center; color: #888; padding: 20px 0;">این روز برای سالن تعطیل است و امکان افزودن شیفت وجود ندارد.</p>',
      );
      $addShiftBtn.hide();
    } else {
      $addShiftBtn.show();
      const shiftsStr = $(`#shifts-${currentEditingDayIndex}`).val();
      if (shiftsStr) {
        shiftsStr.split(',').forEach((part) => {
          const [start, end] = part.split('-');
          addShiftRowToModal(start, end);
        });
      } else {
        addShiftRowToModal();
      }
    }
    $modal.css('display', 'flex');
  });

  // بستن مودال
  $('#modalCloseBtn').on('click', () => $modal.hide());
  $modal.on('click', (e) => {
    if ($(e.target).is($modal)) $modal.hide();
  });

  // افزودن شیفت
  $addShiftBtn.on('click', () => addShiftRowToModal());

  // حذف یک ردیف شیفت
  $modalBody.on('click', '.delete-shift-btn', function () {
    if ($modalBody.find('.shift-editor-row').length > 1) {
      $(this).closest('.shift-editor-row').remove();
    } else {
      $(this).closest('.shift-editor-row').find('select').val('');
    }
  });

  // حذف تمام شیفت‌های روز
  $('#modal-delete-day-btn').on('click', function () {
    $(`#shifts-${currentEditingDayIndex}`).val('');
    updateSummary(currentEditingDayIndex);
    $modal.hide();
  });

  // ذخیره تغییرات
  $('#modal-save-btn').on('click', function () {
    const shifts = [];
    let isValid = true;

    $modalBody.find('.shift-editor-row').each(function () {
      const start = $(this).find('.start-time').val();
      const end = $(this).find('.end-time').val();

      if (start && end) {
        if (end <= start) {
          alert('ساعت پایان باید بعد از ساعت شروع باشد.');
          isValid = false;
          return false;
        }
        shifts.push(`${start}-${end}`);
      } else if (start || end) {
        alert('لطفاً هم ساعت شروع و هم پایان را برای هر شیفت مشخص کنید.');
        isValid = false;
        return false;
      }
    });

    if (!isValid) return;

    $(`#shifts-${currentEditingDayIndex}`).val(shifts.join(','));
    updateSummary(currentEditingDayIndex);
    $modal.hide();
  });

  // افزودن یک ردیف شیفت به مودال با توجه به ساعات کاری همان روز
  function addShiftRowToModal(startVal = '', endVal = '') {
    const dayHours = salonHours[currentEditingDayIndex];
    const timeOptions = dayHours ? generateTimeOptions(dayHours.open, dayHours.close) : '';

    const newRow = $('#shiftRowTemplate').html();
    $modalBody.append(newRow);
    const $addedRow = $modalBody.find('.shift-editor-row').last();

    $addedRow.find('select').html(timeOptions);
    $addedRow.find('.start-time').val(startVal);
    $addedRow.find('.end-time').val(endVal);
  }

  // بروزرسانی خلاصه شیفت‌ها در ردیف روز
  function updateSummary(dayIndex) {
    const shiftsStr = $(`#shifts-${dayIndex}`).val();
    const $summaryDiv = $(`#summary-${dayIndex}`);
    $summaryDiv.empty();

    if (shiftsStr) {
      shiftsStr.split(',').forEach((part) => {
        $summaryDiv.append(`<span>${part.replace('-', ' - ')}</span>`);
      });
    } else {
      $summaryDiv.text('بدون شیفت');
    }
  }
}
