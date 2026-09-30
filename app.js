// ==========================================================================
// BỆNH VIỆN LAO VÀ BỆNH PHỐI BẠC LIÊU - Logic giao diện
// ==========================================================================

const menuButton = document.querySelector('.mobile-menu-toggle, .menu-toggle');
const navigation = document.querySelector('.main-navigation, .main-nav');
const bookingDialog = document.querySelector('#booking-dialog');
const bookingForm = document.querySelector('#booking-form');
const dateInput = bookingForm?.querySelector('[name=appointmentDate]');
const specialtyInput = bookingForm?.querySelector('[name=specialty]');
const symptomsInput = bookingForm?.querySelector('[name=symptoms]');

// Mở biểu mẫu trống khi chọn Đăng ký tiếp từ trang thành công.
if (bookingDialog && new URLSearchParams(window.location.search).get('dat-lich') === '1') {
  bookingForm?.reset();
  bookingDialog.showModal();
}

// Giới hạn ngày đặt lịch từ ngày hiện tại
if (dateInput) {
  const today = new Date();
  const localDate = new Date(today.getTime() - today.getTimezoneOffset() * 60000);
  dateInput.min = localDate.toISOString().split('T')[0];
  dateInput.value = localDate.toISOString().split('T')[0];
  const latestDate = new Date(localDate);
  latestDate.setDate(latestDate.getDate() + 90);
  dateInput.max = latestDate.toISOString().split('T')[0];
}

// Bật/tắt menu trên di động
menuButton?.addEventListener('click', () => {
  const isOpen = menuButton.getAttribute('aria-expanded') === 'true';
  menuButton.setAttribute('aria-expanded', String(!isOpen));
  navigation?.classList.toggle('open', !isOpen);
});

// Đóng menu khi nhấp vào liên kết điều hướng
navigation?.querySelectorAll('a').forEach((link) => {
  link.addEventListener('click', () => {
    navigation.classList.remove('open');
    menuButton?.setAttribute('aria-expanded', 'false');
  });
});

// Mở Modal Đặt lịch khám
document.querySelectorAll('[data-open-booking]').forEach((button) => {
  button.addEventListener('click', () => {
    navigation?.classList.remove('open');
    menuButton?.setAttribute('aria-expanded', 'false');
    if (bookingDialog?.showModal) {
      bookingDialog.showModal();
    } else {
      document.querySelector('#dat-lich')?.scrollIntoView({ behavior: 'smooth' });
    }
  });
});

// Đóng Modal Đặt lịch
document.querySelectorAll('[data-close-booking]').forEach((button) => {
  button.addEventListener('click', () => bookingDialog?.close());
});

// Đóng dialog khi click ra ngoài khung trắng
bookingDialog?.addEventListener('click', (event) => {
  const bounds = bookingDialog.getBoundingClientRect();
  const outside = event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom;
  if (outside) bookingDialog.close();
});

// Kiểm tra dữ liệu form đặt lịch
const messages = {
  fullName: 'Vui lòng nhập họ và tên bệnh nhân.',
  phone: 'Vui lòng nhập số điện thoại hợp lệ (10 số).',
  appointmentDate: 'Vui lòng chọn ngày khám.',
  specialty: 'Vui lòng chọn chuyên khoa hoặc mô tả triệu chứng.',
  symptoms: 'Vui lòng chọn chuyên khoa hoặc mô tả triệu chứng.'
};

function updateCareDetailsValidity() {
  const hasCareDetails = Boolean(specialtyInput?.value.trim() || symptomsInput?.value.trim());
  const message = hasCareDetails ? '' : messages.symptoms;
  specialtyInput?.setCustomValidity(message);
  symptomsInput?.setCustomValidity(message);

  if (hasCareDetails) {
    [specialtyInput, symptomsInput].filter(Boolean).forEach((field) => {
      const wrapper = field.closest('.form-group, .field');
      wrapper?.classList.remove('invalid');
      field.setAttribute('aria-invalid', 'false');
      const error = wrapper?.querySelector('.field-error');
      if (error) error.textContent = '';
    });
  }
  return hasCareDetails;
}

updateCareDetailsValidity();

function showFieldState(field) {
  const wrapper = field.closest('.form-group, .field');
  if (!wrapper) return field.checkValidity();
  const valid = field.checkValidity();
  wrapper.classList.toggle('invalid', !valid);
  field.setAttribute('aria-invalid', String(!valid));
  const error = wrapper.querySelector('.field-error');
  if (error) error.textContent = valid ? '' : messages[field.name] || 'Vui lòng kiểm tra lại thông tin.';
  return valid;
}

bookingForm?.querySelectorAll('input:not([type=checkbox]), select, textarea').forEach((field) => {
  field.addEventListener('blur', () => showFieldState(field));
  field.addEventListener('input', () => {
    if (field === specialtyInput || field === symptomsInput) updateCareDetailsValidity();
    if (field.closest('.form-group, .field')?.classList.contains('invalid')) {
      showFieldState(field);
    }
  });
  field.addEventListener('change', () => {
    if (field === specialtyInput || field === symptomsInput) updateCareDetailsValidity();
  });
});

const configuredApiBase = document.querySelector('meta[name=booking-api-base-url]')?.content?.trim();
const isLocalWebsite = ['127.0.0.1', 'localhost'].includes(window.location.hostname);
const bookingApiBase = configuredApiBase || (isLocalWebsite ? 'http://127.0.0.1:8002' : '');

function showServerErrors(errors = {}) {
  Object.entries(errors).forEach(([name, message]) => {
    const field = bookingForm?.elements.namedItem(name);
    const wrapper = field?.closest('.form-group, .field');
    if (field) field.setAttribute('aria-invalid', 'true');
    wrapper?.classList.add('invalid');
    const error = wrapper?.querySelector('.field-error');
    if (error) error.textContent = message;
  });
}

bookingForm?.addEventListener('submit', async (event) => {
  event.preventDefault();
  if (bookingForm.querySelector('[type=submit]')?.disabled) return;
  updateCareDetailsValidity();
  const fields = [...bookingForm.querySelectorAll('input:not([type=checkbox]):not(.hp-field), select, textarea')];
  const fieldsValid = fields.map(showFieldState).every(Boolean);
  const consent = bookingForm.querySelector('[name=consent]');
  const status = bookingForm.querySelector('.form-status');
  const submitButton = bookingForm.querySelector('[type=submit]');

  if (consent && !consent.checked) {
    status.textContent = 'Vui lòng đồng ý để bệnh viện liên hệ theo thông tin đã cung cấp.';
    status.style.color = '#d32f2f';
    consent.focus();
    return;
  }

  if (!fieldsValid) {
    status.textContent = 'Vui lòng điền đầy đủ các thông tin bắt buộc.';
    status.style.color = '#d32f2f';
    bookingForm.querySelector('[aria-invalid=true]')?.focus();
    return;
  }

  if (!bookingApiBase) {
    status.textContent = 'Hệ thống đặt lịch trực tuyến chưa được cấu hình. Vui lòng gọi hotline bệnh viện.';
    status.style.color = '#d32f2f';
    return;
  }

  const formData = new FormData(bookingForm);
  const payload = Object.fromEntries(formData.entries());
  payload.consent = Boolean(consent?.checked);
  payload.idempotencyKey = window.crypto?.randomUUID?.()
    || `booking-${Date.now()}-${Math.random().toString(16).slice(2)}`;

  submitButton.disabled = true;
  submitButton.setAttribute('aria-busy', 'true');
  status.textContent = 'Đang gửi thông tin đăng ký...';
  status.style.color = '#00758a';

  try {
    const response = await fetch(`${bookingApiBase}/api/v1/appointments/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const result = await response.json().catch(() => ({}));
    if (!response.ok || !result.success) {
      showServerErrors(result.errors);
      throw new Error(result.message || 'Máy chủ chưa thể tiếp nhận đăng ký.');
    }

    status.textContent = `✓ Đã tiếp nhận đăng ký. Mã của bạn: ${result.bookingCode}`;
    status.style.color = '#00758a';
    bookingForm.reset();
    if (dateInput) dateInput.value = dateInput.min;
    updateCareDetailsValidity();
    const successUrl = new URL('./dang-ky-thanh-cong.html', window.location.href);
    successUrl.hash = new URLSearchParams({
      code: result.bookingCode || '',
      from: bookingDialog ? 'home' : 'booking'
    }).toString();
    window.location.assign(successUrl.href);
  } catch (error) {
    status.textContent = `${error.message} Vui lòng thử lại hoặc gọi hotline bệnh viện.`;
    status.style.color = '#d32f2f';
  } finally {
    submitButton.disabled = false;
    submitButton.removeAttribute('aria-busy');
  }
});

// Homepage service information and the full specialty list.
const pricesDialog = document.querySelector('#gia-dich-vu.info-dialog');
document.querySelectorAll('[data-open-prices]').forEach((link) => {
  link.addEventListener('click', (event) => {
    if (!pricesDialog) return;
    event.preventDefault();
    pricesDialog.showModal();
  });
});
document.querySelector('[data-close-prices]')?.addEventListener('click', () => pricesDialog?.close());
pricesDialog?.addEventListener('click', (event) => {
  const bounds = pricesDialog.getBoundingClientRect();
  if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) pricesDialog.close();
});
document.querySelector('[data-expand-specialties]')?.addEventListener('click', (event) => {
  event.preventDefault();
  const link = event.currentTarget;
  const expanded = link.getAttribute('aria-expanded') !== 'true';
  link.setAttribute('aria-expanded', String(expanded));
  document.querySelector('.specialties-grid')?.classList.toggle('expanded', expanded);
  link.textContent = expanded ? 'Thu gọn ↑' : 'Xem tất cả →';
});
document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape' && navigation?.classList.contains('open')) {
    navigation.classList.remove('open');
    menuButton?.setAttribute('aria-expanded', 'false');
    menuButton?.focus();
  }
});

// ==========================================================================
// QUY TRÌNH KHÁM BỆNH: Tabs switching & Lightbox Modal
// ==========================================================================
const qtTabButtons = document.querySelectorAll('.qt-tab-btn');
const qtTabPanes = document.querySelectorAll('.qt-tab-pane');
const qtLightbox = document.querySelector('#qt-lightbox-dialog');
const qtLightboxImg = document.querySelector('#qt-lightbox-img');
const qtLightboxTitle = document.querySelector('#qt-lightbox-title');
const qtLightboxDownload = document.querySelector('#qt-lightbox-download');
const qtLightboxClose = document.querySelector('#qt-lightbox-close');

function switchQtTab(targetId) {
  if (!targetId) return;
  qtTabButtons.forEach((btn) => {
    const isTarget = btn.getAttribute('data-target') === targetId;
    btn.classList.toggle('active', isTarget);
    btn.setAttribute('aria-selected', String(isTarget));
  });

  qtTabPanes.forEach((pane) => {
    const isTarget = pane.id === targetId;
    pane.classList.toggle('active', isTarget);
  });
}

qtTabButtons.forEach((btn) => {
  btn.addEventListener('click', () => {
    const targetId = btn.getAttribute('data-target');
    switchQtTab(targetId);
  });
});

// Hỗ trợ Hash URL cho các tab trực tiếp
function checkQtHash() {
  const hash = window.location.hash.toLowerCase();
  if (hash === '#quy-trinh-dat-lich') switchQtTab('qt-pane-booking');
  else if (hash === '#quy-trinh-thu-phi' || hash === '#quy-trinh-vien-phi') switchQtTab('qt-pane-vp');
  else if (hash === '#quy-trinh-bhyt') switchQtTab('qt-pane-bh');
}

window.addEventListener('hashchange', checkQtHash);
checkQtHash();

// Mở Lightbox xem sơ đồ phóng to
document.querySelectorAll('[data-lightbox]').forEach((el) => {
  el.addEventListener('click', (e) => {
    e.preventDefault();
    const imgSrc = el.getAttribute('data-lightbox');
    const title = el.getAttribute('data-lightbox-title') || 'Sơ đồ quy trình khám bệnh';
    if (!qtLightbox || !imgSrc) return;

    if (qtLightboxImg) {
      qtLightboxImg.src = imgSrc;
      qtLightboxImg.alt = title;
    }
    if (qtLightboxTitle) {
      qtLightboxTitle.textContent = title;
    }
    if (qtLightboxDownload) {
      qtLightboxDownload.href = imgSrc;
      qtLightboxDownload.download = imgSrc.split('/').pop() || 'so-do-quy-trinh.png';
    }

    if (qtLightbox.showModal) {
      qtLightbox.showModal();
    }
  });
});

// Đóng Lightbox
qtLightboxClose?.addEventListener('click', () => qtLightbox?.close());
qtLightbox?.addEventListener('click', (event) => {
  const box = qtLightbox.querySelector('.qt-lightbox-box');
  if (!box) return;
  const bounds = box.getBoundingClientRect();
  const outside = event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom;
  if (outside) qtLightbox.close();
});


// Hiệu ứng cuộn trang cho Header (thu gọn nhẹ và tăng bóng đổ)
const siteHeader = document.querySelector('.site-header');
if (siteHeader) {
  const onHeaderScroll = () => {
    if (window.scrollY > 25) {
      siteHeader.classList.add('scrolled');
    } else {
      siteHeader.classList.remove('scrolled');
    }
  };
  window.addEventListener('scroll', onHeaderScroll, { passive: true });
  onHeaderScroll();
}
