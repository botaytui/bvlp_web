const configuredBase = document.querySelector('meta[name=services-api-base-url]')?.content?.trim()
  || document.querySelector('meta[name=booking-api-base-url]')?.content?.trim();
const local = ['127.0.0.1', 'localhost'].includes(window.location.hostname);
const apiBase = (configuredBase || (local ? 'http://127.0.0.1:8002' : window.location.origin)).replace(/\/$/, '');
const rows = document.querySelector('#services-rows');
const table = document.querySelector('#services-table');
const summary = document.querySelector('#services-summary');
const search = document.querySelector('#services-search');
const pagination = document.querySelector('#services-pagination');
const previous = document.querySelector('#services-prev');
const next = document.querySelector('#services-next');
const feedback = document.querySelector('#services-feedback');
const pageSize = 25;
const money = new Intl.NumberFormat('vi-VN', { maximumFractionDigits: 4 });
let items = [];
let currentPage = 1;
let loaded = false;

function normalize(value) {
  return String(value ?? '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/đ/gi, 'd').toLowerCase().trim();
}

function messageRow(message) {
  const row = document.createElement('tr');
  const cell = document.createElement('td');
  cell.colSpan = 4;
  cell.className = 'services-state';
  cell.textContent = message;
  row.append(cell);
  rows.replaceChildren(row);
}

function render() {
  if (!loaded) return;
  const query = normalize(search.value);
  const matches = items.filter(item => !query || item.searchText.includes(query));
  const pages = Math.max(1, Math.ceil(matches.length / pageSize));
  currentPage = Math.min(currentPage, pages);
  const start = (currentPage - 1) * pageSize;
  const fragment = document.createDocumentFragment();
  matches.slice(start, start + pageSize).forEach(item => {
    const row = document.createElement('tr');
    const values = [item.stt ?? '—', item.ma_dich_vu, item.ten_dich_vu,
      item.don_gia === null ? '—' : money.format(Number(item.don_gia))];
    values.forEach(value => {
      const cell = document.createElement('td');
      cell.textContent = value;
      row.append(cell);
    });
    fragment.append(row);
  });
  rows.replaceChildren(fragment);
  if (!matches.length) messageRow(items.length ? 'Không tìm thấy dịch vụ phù hợp. Vui lòng thử mã hoặc tên khác.' : 'Chưa có dữ liệu bảng giá dịch vụ.');
  summary.textContent = matches.length
    ? `Hiển thị ${start + 1}–${Math.min(start + pageSize, matches.length)} / ${matches.length} dịch vụ`
    : '0 dịch vụ';
  pagination.hidden = matches.length <= pageSize;
  previous.disabled = currentPage === 1;
  next.disabled = currentPage === pages;
  document.querySelector('#services-page-number').textContent = `Trang ${currentPage} / ${pages}`;
}

function searchServices() { currentPage = 1; render(); }
document.querySelector('#services-search-form').addEventListener('submit', event => {
  event.preventDefault();
  searchServices();
});
search.addEventListener('input', searchServices);
previous.addEventListener('click', () => { currentPage -= 1; render(); });
next.addEventListener('click', () => { currentPage += 1; render(); });
document.querySelector('#services-retry').addEventListener('click', load);

async function load() {
  loaded = false;
  table.setAttribute('aria-busy', 'true');
  feedback.hidden = true;
  pagination.hidden = true;
  summary.textContent = 'Đang tải bảng giá…';
  messageRow('Đang tải dữ liệu…');
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 15000);
  try {
    const response = await fetch(`${apiBase}/api/v1/dvkt/`, { signal: controller.signal });
    if (!response.ok) throw new Error('Không tải được bảng giá. Vui lòng thử lại.');
    const data = await response.json();
    if (!data.success || !Array.isArray(data.items)) throw new Error('Dữ liệu bảng giá chưa hợp lệ.');
    items = data.items.map(item => ({ ...item, searchText: normalize(`${item.ma_dich_vu} ${item.ten_dich_vu}`) }));
    currentPage = 1;
    loaded = true;
    render();
  } catch {
    summary.textContent = 'Chưa tải được bảng giá';
    messageRow('Bảng giá hiện chưa tải được.');
    document.querySelector('#services-error').textContent = 'Không thể tải bảng giá dịch vụ. Vui lòng kiểm tra kết nối và thử lại.';
    feedback.hidden = false;
  } finally {
    clearTimeout(timeout);
    table.setAttribute('aria-busy', 'false');
  }
}

load();
