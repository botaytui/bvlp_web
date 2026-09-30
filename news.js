const configuredApiBase = document.querySelector('meta[name=news-api-base-url]')?.content?.trim();
const isLocalWebsite = ['127.0.0.1', 'localhost'].includes(window.location.hostname);
const newsApiBase = configuredApiBase || (isLocalWebsite ? 'http://127.0.0.1:8002' : '');
const view = document.body.dataset.newsView;

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function formatDate(value) {
  if (!value) return '';
  return new Intl.DateTimeFormat('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' }).format(new Date(value));
}

function normalized(value) {
  return String(value || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/đ/gi, 'd').toLowerCase().trim();
}

function postUrl(post) {
  return `./chi-tiet-tin.html?slug=${encodeURIComponent(post.slug)}`;
}

function categoryBadge(post) {
  return element('span', `news-badge${post.category === 'announcement' ? ' announcement' : ''}`, post.categoryLabel);
}

function postTime(post, prefix = '') {
  const time = element('time', '', `${prefix}${formatDate(post.publishedAt)}`);
  time.dateTime = post.publishedAt;
  return time;
}

function resolveMediaUrl(url) {
  if (!url) return '';
  if (url.startsWith('http://') || url.startsWith('https://') || url.startsWith('data:') || url.startsWith('./')) return url;
  const base = newsApiBase || 'http://127.0.0.1:8002';
  return `${base}${url.startsWith('/') ? '' : '/'}${url}`;
}

function addImage(container, src, alt) {
  if (!src) {
    container.append(element('span', 'news-image-placeholder', '✚'));
    return;
  }
  const image = element('img');
  image.src = resolveMediaUrl(src);
  image.alt = alt;
  image.loading = 'lazy';
  image.decoding = 'async';
  image.addEventListener('error', () => {
    container.replaceChildren(element('span', 'news-image-placeholder', '✚'));
  }, { once: true });
  container.append(image);
}

function createCard(post) {
  const article = element('article', 'news-card');
  const media = element('a', 'news-card-media');
  media.href = postUrl(post);
  media.setAttribute('aria-label', post.title);
  addImage(media, post.coverImage, '');
  const body = element('div', 'news-card-body');
  body.append(categoryBadge(post));
  const title = element('h2');
  const link = element('a', '', post.title);
  link.href = postUrl(post);
  title.append(link);
  body.append(title, element('p', '', post.summary));
  const meta = element('div', 'news-meta');
  meta.append(postTime(post));
  body.append(meta);
  article.append(media, body);
  return article;
}

function renderFeatured(post) {
  const region = document.querySelector('#featured-news');
  if (!region) return;
  region.hidden = !post;
  if (!post) return;
  const media = element('a', 'featured-media');
  media.href = postUrl(post);
  media.setAttribute('aria-label', post.title);
  addImage(media, post.coverImage, '');
  const content = element('div', 'featured-content');
  content.append(categoryBadge(post));
  const title = element('h2');
  const titleLink = element('a', '', post.title);
  titleLink.href = postUrl(post);
  title.append(titleLink);
  content.append(title, element('p', '', post.summary));
  const meta = element('div', 'news-meta');
  meta.append(postTime(post), element('span', '', post.isFeatured ? 'Tin nổi bật' : 'Mới cập nhật'));
  const readMore = element('a', 'news-read-more', 'Xem chi tiết →');
  readMore.href = postUrl(post);
  content.append(meta, readMore);
  region.replaceChildren(media, content);
}

function renderNotices(items) {
  const container = document.querySelector('#news-notices');
  if (!container) return;
  const notices = items.filter(post => post.category === 'announcement').slice(0, 4);
  container.replaceChildren(...notices.map(post => {
    const link = element('a', 'notice-link');
    link.href = postUrl(post);
    link.append(postTime(post), element('strong', '', post.title));
    return link;
  }));
  if (!notices.length) container.append(element('p', 'news-result-summary', 'Chưa có thông báo mới.'));
}

async function fetchJson(url) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 10000);
  try {
    const response = await fetch(url, { headers: { Accept: 'application/json' }, signal: controller.signal });
    const data = await response.json().catch(() => ({}));
    if (!response.ok || !data.success) throw new Error(data.message || 'Không thể tải dữ liệu tin tức.');
    return data;
  } catch (error) {
    if (error.name === 'AbortError' || error instanceof TypeError) {
      throw new Error('Chưa kết nối được với hệ thống tin tức.');
    }
    throw error;
  } finally {
    clearTimeout(timeout);
  }
}

function showError(container, message, retry) {
  const state = element('div', 'news-state');
  state.append(element('p', '', message));
  if (retry) {
    const button = element('button', 'news-retry', 'Thử lại');
    button.type = 'button';
    button.addEventListener('click', retry);
    state.append(button);
  }
  container.replaceChildren(state);
}

async function initList() {
  const grid = document.querySelector('#news-list');
  const summary = document.querySelector('#news-result-summary');
  const search = document.querySelector('#news-search');
  const tabs = [...document.querySelectorAll('[data-news-category]')];
  if (!grid) return;
  if (!newsApiBase) {
    renderFeatured(null);
    renderNotices([]);
    if (summary) summary.textContent = '';
    grid.setAttribute('aria-busy', 'false');
    showError(grid, 'Hệ thống tin tức chưa được cấu hình.');
    return;
  }
  const state = { items: [], category: 'all', query: '', loaded: false };

  function render() {
    if (!state.loaded) return;
    const query = normalized(state.query);
    const filtered = state.items.filter(post => {
      const categoryMatch = state.category === 'all' || post.category === state.category;
      const textMatch = !query || normalized(`${post.title} ${post.summary}`).includes(query);
      return categoryMatch && textMatch;
    });
    grid.replaceChildren(...filtered.map(createCard));
    if (!filtered.length) {
      const message = !state.items.length ? 'Chưa có bài viết được xuất bản.'
        : 'Không tìm thấy bài viết phù hợp.';
      grid.append(element('div', 'news-state', message));
    }
    if (summary) summary.textContent = `${filtered.length} bài viết`;
  }

  tabs.forEach(tab => tab.addEventListener('click', () => {
    state.category = tab.dataset.newsCategory;
    tabs.forEach(item => {
      item.classList.toggle('active', item === tab);
      item.setAttribute('aria-pressed', String(item === tab));
    });
    render();
  }));
  search?.addEventListener('input', () => { state.query = search.value; render(); });

  async function load() {
    state.loaded = false;
    grid.setAttribute('aria-busy', 'true');
    if (summary) summary.textContent = 'Đang tải danh sách…';
    grid.replaceChildren(element('div', 'news-state news-loading', 'Đang tải tin tức và thông báo…'));
    try {
      const data = await fetchJson(`${newsApiBase}/api/v1/news/?limit=50`);
      state.items = data.items;
      state.loaded = true;
      renderNotices(state.items);
      render();
    } catch (error) {
      renderFeatured(null);
      if (summary) summary.textContent = '';
      document.querySelector('#news-notices')?.replaceChildren(element('p', 'news-result-summary', 'Chưa tải được thông báo.'));
      showError(grid, error.message, load);
    } finally {
      grid.setAttribute('aria-busy', 'false');
    }
  }
  await load();
}

function renderArticle(post) {
  const article = document.querySelector('#article-main');
  if (!article) return;
  document.title = `${post.title} | Bệnh viện Lao và Bệnh phổi Bạc Liêu`;
  document.querySelector('meta[name=description]')?.setAttribute('content', post.summary);
  article.replaceChildren();
  const content = element('div', 'article-content');
  content.append(categoryBadge(post), element('h1', '', post.title));
  const meta = element('div', 'news-meta');
  meta.append(postTime(post, 'Đăng ngày '));
  content.append(meta, element('p', 'article-lead', post.summary));

  const body = element('div', 'article-body');
  let rawContent = String(post.content || '').trim();

  // If content was entity-escaped, unescape it safely
  if (/&lt;(?:figure|p|img|div|span|h[1-6]|ul|ol|li)/i.test(rawContent)) {
    const decoder = document.createElement('textarea');
    decoder.innerHTML = rawContent;
    rawContent = decoder.value;
  }

  const hasHtml = /<[a-z][\s\S]*>/i.test(rawContent);

  if (hasHtml) {
    body.innerHTML = rawContent;
    // Resolve relative media image URLs
    body.querySelectorAll('img').forEach(img => {
      const src = img.getAttribute('src');
      if (src) img.src = resolveMediaUrl(src);
      img.loading = 'lazy';
      img.decoding = 'async';
    });
  } else {
    rawContent.split(/\n\s*\n/).filter(Boolean).forEach(paragraph => {
      body.append(element('p', '', paragraph.trim()));
    });
  }

  content.append(body);
  const back = element('a', 'article-back', '← Quay lại Tin tức & Thông báo');
  back.href = './tin-tuc.html';
  content.append(back);
  article.append(content);
}

function renderRelated(items) {
  const container = document.querySelector('#related-news');
  if (!container) return;
  container.replaceChildren(...items.map(post => {
    const link = element('a', 'related-item');
    link.href = postUrl(post);
    link.append(categoryBadge(post), element('strong', '', post.title));
    return link;
  }));
  if (!items.length) container.append(element('p', 'news-result-summary', 'Chưa có bài viết liên quan.'));
}

async function initDetail() {
  const article = document.querySelector('#article-main');
  const slug = new URLSearchParams(window.location.search).get('slug');
  if (!article) return;
  if (!newsApiBase || !slug) {
    showError(article, !slug ? 'Không xác định được bài viết cần xem.' : 'Hệ thống tin tức chưa được cấu hình.');
    renderRelated([]);
    article.setAttribute('aria-busy', 'false');
    return;
  }
  article.setAttribute('aria-busy', 'true');
  let post;
  try {
    const data = await fetchJson(`${newsApiBase}/api/v1/news/${encodeURIComponent(slug)}/`);
    post = data.item;
    renderArticle(post);
  } catch (error) {
    showError(article, error.message, initDetail);
    renderRelated([]);
    return;
  } finally {
    article.setAttribute('aria-busy', 'false');
  }
  // A failed related-news request must not remove an already loaded article.
  try {
    const related = await fetchJson(`${newsApiBase}/api/v1/news/?category=${encodeURIComponent(post.category)}&limit=5`);
    renderRelated(related.items.filter(item => item.slug !== slug).slice(0, 4));
  } catch {
    document.querySelector('#related-news')?.replaceChildren(element('p', 'news-result-summary', 'Chưa tải được bài viết liên quan.'));
  }
}

function createHomeCard(post) {
  const article = element('article', 'news-item-card');
  const media = element('a', 'news-thumb-wrap');
  media.href = postUrl(post);
  media.setAttribute('aria-label', post.title);
  addImage(media, post.coverImage, '');
  const content = element('div', 'news-item-content');
  const time = postTime(post);
  time.className = 'news-date';
  const title = element('h3', 'news-item-title');
  const link = element('a', '', post.title);
  link.href = postUrl(post);
  title.append(link);
  content.append(time, title, element('p', 'news-item-desc', post.summary));
  article.append(media, content);
  return article;
}

async function initHome() {
  const container = document.querySelector('#home-news-list');
  if (!container) return;
  container.setAttribute('aria-busy', 'true');
  container.replaceChildren(element('p', 'news-state', 'Đang tải tin tức và thông báo…'));
  try {
    if (!newsApiBase) throw new Error('Hệ thống tin tức chưa được cấu hình.');
    const data = await fetchJson(`${newsApiBase}/api/v1/news/?category=news&limit=3`);
    container.replaceChildren(...data.items.map(createHomeCard));
    if (!data.items.length) container.append(element('p', 'news-state', 'Chưa có bài viết được xuất bản.'));
  } catch (error) {
    showError(container, error.message, initHome);
  } finally {
    container.setAttribute('aria-busy', 'false');
  }
}

if (view === 'home') initHome();
if (view === 'list') initList();
if (view === 'detail') initDetail();
