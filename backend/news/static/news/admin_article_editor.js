/* Admin Article Editor for Django - Rich Blocks & Inline Images */
document.addEventListener('DOMContentLoaded', () => {
  const contentTextarea = document.querySelector('textarea#id_content');
  if (!contentTextarea) return;

  // Extract post_id from URL if available
  const matchPostId = window.location.pathname.match(/\/newspost\/(\d+)\//);
  const postId = matchPostId ? matchPostId[1] : '';

  // Hide the default textarea initially, but keep it in DOM for Django form submission
  contentTextarea.style.display = 'none';

  // State
  let blocks = [];
  let currentMode = 'visual'; // 'visual' | 'raw'
  let insertAtIndex = null;

  // Create UI Container
  const wrapper = document.createElement('div');
  wrapper.className = 'article-editor-wrapper';

  // Toolbar
  const toolbar = document.createElement('div');
  toolbar.className = 'article-editor-toolbar';
  toolbar.innerHTML = `
    <div class="editor-toolbar-group">
      <button type="button" class="editor-btn editor-btn-primary" id="btn-add-image">
        📷 + Tải ảnh & Chèn vào bài
      </button>
      <button type="button" class="editor-btn" id="btn-open-gallery">
        🖼️ Thư viện ảnh đã tải
      </button>
      <button type="button" class="editor-btn" id="btn-add-paragraph">
        📝 + Thêm đoạn văn
      </button>
      <button type="button" class="editor-btn" id="btn-preview-article">
        👁️ Xem trước bài viết
      </button>
    </div>
    <div class="editor-toolbar-group">
      <div class="editor-mode-toggle">
        <button type="button" class="editor-mode-btn active" data-mode="visual">🔲 Trực quan (Khối & Ảnh)</button>
        <button type="button" class="editor-mode-btn" data-mode="raw">📄 Mã HTML / Văn bản</button>
      </div>
    </div>
  `;

  // Hidden File Input
  const fileInput = document.createElement('input');
  fileInput.type = 'file';
  fileInput.accept = 'image/png, image/jpeg, image/jpg, image/webp, image/gif, image/svg+xml';
  fileInput.multiple = true;
  fileInput.style.display = 'none';

  // Status Banner
  const statusBanner = document.createElement('div');
  statusBanner.className = 'editor-uploading-banner';
  statusBanner.style.display = 'none';

  // Visual Blocks Container
  const blocksContainer = document.createElement('div');
  blocksContainer.className = 'editor-blocks-container';

  // Raw HTML Editor Container (for raw mode)
  const rawContainer = document.createElement('div');
  rawContainer.style.display = 'none';
  rawContainer.style.padding = '14px 18px';

  wrapper.appendChild(toolbar);
  wrapper.appendChild(statusBanner);
  wrapper.appendChild(blocksContainer);
  wrapper.appendChild(rawContainer);
  wrapper.appendChild(fileInput);

  contentTextarea.parentNode.insertBefore(wrapper, contentTextarea);

  // -------------------------------------------------------------
  // Parse Content into Blocks
  // -------------------------------------------------------------
  function parseContentToBlocks(raw) {
    if (!raw || !raw.trim()) {
      return [{ type: 'text', content: '' }];
    }

    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = raw;

    const parsedBlocks = [];
    const childNodes = Array.from(tempDiv.childNodes);

    // If no HTML tags found, split by double line breaks (paragraphs)
    const hasHtmlTags = /<[a-z][\s\S]*>/i.test(raw);
    if (!hasHtmlTags) {
      const paras = raw.split(/\n\s*\n/).map(p => p.trim()).filter(Boolean);
      if (paras.length === 0) return [{ type: 'text', content: '' }];
      return paras.map(p => ({ type: 'text', content: p }));
    }

    // Process HTML nodes
    childNodes.forEach(node => {
      if (node.nodeType === Node.TEXT_NODE) {
        const text = node.textContent.trim();
        if (text) parsedBlocks.push({ type: 'text', content: text });
      } else if (node.nodeType === Node.ELEMENT_NODE) {
        const tag = node.tagName.toLowerCase();
        if (tag === 'figure' || tag === 'img') {
          const imgEl = tag === 'img' ? node : node.querySelector('img');
          const figcap = node.querySelector('figcaption');
          if (imgEl && imgEl.src) {
            parsedBlocks.push({
              type: 'image',
              url: imgEl.getAttribute('src') || imgEl.src,
              caption: figcap ? figcap.textContent.trim() : (imgEl.alt || ''),
              align: node.dataset.align || 'center'
            });
          }
        } else {
          // Standard paragraphs or other elements
          const htmlContent = node.innerHTML.trim();
          if (htmlContent) {
            parsedBlocks.push({ type: 'text', content: node.textContent.trim() });
          }
        }
      }
    });

    if (parsedBlocks.length === 0) {
      parsedBlocks.push({ type: 'text', content: '' });
    }
    return parsedBlocks;
  }

  // -------------------------------------------------------------
  // Serialize Blocks back to HTML string
  // -------------------------------------------------------------
  function serializeBlocksToContent() {
    if (currentMode === 'raw') {
      return contentTextarea.value;
    }

    const htmlParts = [];
    blocks.forEach(b => {
      if (b.type === 'text') {
        const trimmed = (b.content || '').trim();
        if (trimmed) {
          // Convert line breaks to paragraphs or clean text
          const subParas = trimmed.split(/\n\s*\n/).filter(Boolean);
          subParas.forEach(sp => {
            htmlParts.push(`<p>${escapeHtml(sp.trim())}</p>`);
          });
        }
      } else if (b.type === 'image' && b.url) {
        const caption = escapeHtml(b.caption || '');
        const align = b.align || 'center';
        htmlParts.push(
          `<figure class="article-image" data-align="${align}">\n` +
          `  <img src="${escapeHtml(b.url)}" alt="${caption || 'Hình ảnh bài viết'}" />\n` +
          (caption ? `  <figcaption>${caption}</figcaption>\n` : '') +
          `</figure>`
        );
      }
    });

    const finalHtml = htmlParts.join('\n\n');
    contentTextarea.value = finalHtml;
    return finalHtml;
  }

  function escapeHtml(str) {
    return String(str || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  // -------------------------------------------------------------
  // Render Blocks in Visual Mode
  // -------------------------------------------------------------
  function renderBlocks() {
    blocksContainer.innerHTML = '';

    blocks.forEach((block, index) => {
      // 1. Insert Divider before this block
      const divider = createInsertDivider(index);
      blocksContainer.appendChild(divider);

      // 2. The block itself
      if (block.type === 'text') {
        const textBlockEl = createTextBlock(block, index);
        blocksContainer.appendChild(textBlockEl);
      } else if (block.type === 'image') {
        const imageBlockEl = createImageBlock(block, index);
        blocksContainer.appendChild(imageBlockEl);
      }
    });

    // Final Insert Divider at the very end
    const lastDivider = createInsertDivider(blocks.length);
    blocksContainer.appendChild(lastDivider);

    // Save to hidden textarea
    serializeBlocksToContent();
  }

  function createInsertDivider(atIndex) {
    const div = document.createElement('div');
    div.className = 'editor-insert-divider';
    div.innerHTML = `
      <button type="button" class="editor-insert-btn" title="Chèn một hoặc nhiều ảnh vào đúng vị trí này">
        📷 + Chèn ảnh vào đây
      </button>
    `;
    const btn = div.querySelector('button');
    btn.addEventListener('click', () => {
      insertAtIndex = atIndex;
      fileInput.click();
    });
    return div;
  }

  function createTextBlock(block, index) {
    const wrap = document.createElement('div');
    wrap.className = 'editor-block-item';

    const textarea = document.createElement('textarea');
    textarea.className = 'editor-block-text';
    textarea.placeholder = 'Nhập nội dung đoạn văn bản tại đây...';
    textarea.value = block.content || '';

    // Auto resize
    function autoResize() {
      textarea.style.height = 'auto';
      textarea.style.height = Math.max(60, textarea.scrollHeight) + 'px';
    }

    textarea.addEventListener('input', () => {
      block.content = textarea.value;
      autoResize();
      serializeBlocksToContent();
    });

    wrap.appendChild(textarea);
    setTimeout(autoResize, 10);
    return wrap;
  }

  function createImageBlock(block, index) {
    const wrap = document.createElement('div');
    wrap.className = 'editor-block-image';
    wrap.dataset.index = index;

    wrap.innerHTML = `
      <div class="editor-image-preview-wrap">
        <img src="${escapeHtml(block.url)}" alt="${escapeHtml(block.caption || '')}" class="editor-image-preview" />
      </div>
      <input type="text" class="editor-image-caption-input" placeholder="Nhập chú thích cho hình ảnh này (tùy chọn)..." value="${escapeHtml(block.caption || '')}" />
      <div class="editor-image-actions">
        <button type="button" class="editor-image-action-btn btn-move-up" ${index === 0 ? 'disabled' : ''} title="Chuyển ảnh lên trên">⬆️ Lên</button>
        <button type="button" class="editor-image-action-btn btn-move-down" ${index === blocks.length - 1 ? 'disabled' : ''} title="Chuyển ảnh xuống dưới">⬇️ Xuống</button>
        <button type="button" class="editor-image-action-btn btn-set-cover" title="Sao chép làm ảnh đại diện bài viết">⭐ Đặt làm ảnh bìa</button>
        <button type="button" class="editor-image-action-btn btn-delete" title="Xóa hình ảnh này khỏi bài viết">🗑️ Xóa ảnh</button>
      </div>
    `;

    // Caption input
    const captionInput = wrap.querySelector('.editor-image-caption-input');
    captionInput.addEventListener('input', () => {
      block.caption = captionInput.value;
      serializeBlocksToContent();
    });

    // Move Up
    wrap.querySelector('.btn-move-up').addEventListener('click', () => {
      if (index > 0) {
        const item = blocks.splice(index, 1)[0];
        blocks.splice(index - 1, 0, item);
        renderBlocks();
      }
    });

    // Move Down
    wrap.querySelector('.btn-move-down').addEventListener('click', () => {
      if (index < blocks.length - 1) {
        const item = blocks.splice(index, 1)[0];
        blocks.splice(index + 1, 0, item);
        renderBlocks();
      }
    });

    // Set as Cover
    wrap.querySelector('.btn-set-cover').addEventListener('click', () => {
      const coverInput = document.querySelector('input#id_cover_image_url');
      if (coverInput) {
        coverInput.value = block.url;
        showToast('✓ Đã cập nhật làm Ảnh đại diện bài viết!');
      }
    });

    // Delete
    wrap.querySelector('.btn-delete').addEventListener('click', () => {
      if (confirm('Bạn có chắc muốn xóa hình ảnh này khỏi bài viết?')) {
        blocks.splice(index, 1);
        renderBlocks();
      }
    });

    return wrap;
  }

  // -------------------------------------------------------------
  // Upload Files Handler
  // -------------------------------------------------------------
  async function handleFilesUpload(files, targetIndex) {
    if (!files || files.length === 0) return;

    statusBanner.style.display = 'flex';
    statusBanner.textContent = `⏳ Đang tải lên ${files.length} hình ảnh...`;

    let successCount = 0;
    const insertPos = targetIndex !== null && targetIndex !== undefined ? targetIndex : blocks.length;
    let currentInsert = insertPos;

    for (const file of files) {
      const formData = new FormData();
      formData.append('image', file);
      if (postId) formData.append('post_id', postId);

      try {
        const res = await fetch('/api/v1/news/upload-image/', {
          method: 'POST',
          body: formData
        });
        const data = await res.json();
        if (!res.ok || !data.success) {
          throw new Error(data.message || 'Lỗi tải ảnh');
        }

        const newImageBlock = {
          type: 'image',
          url: data.url,
          caption: data.name ? data.name.replace(/\.[^/.]+$/, '').replace(/[-_]/g, ' ') : ''
        };

        blocks.splice(currentInsert, 0, newImageBlock);
        currentInsert++;
        successCount++;
      } catch (err) {
        alert(`Không thể tải ảnh "${file.name}": ${err.message}`);
      }
    }

    statusBanner.style.display = 'none';
    fileInput.value = '';
    insertAtIndex = null;

    if (successCount > 0) {
      showToast(`✓ Đã chèn thành công ${successCount} ảnh vào bài viết!`);
      renderBlocks();
    }
  }

  fileInput.addEventListener('change', () => {
    handleFilesUpload(Array.from(fileInput.files), insertAtIndex);
  });

  // Topbar Button: Add Image
  document.getElementById('btn-add-image').addEventListener('click', () => {
    insertAtIndex = blocks.length;
    fileInput.click();
  });

  // Topbar Button: Add Paragraph
  document.getElementById('btn-add-paragraph').addEventListener('click', () => {
    blocks.push({ type: 'text', content: '' });
    renderBlocks();
    const allTextareas = blocksContainer.querySelectorAll('textarea');
    if (allTextareas.length > 0) {
      allTextareas[allTextareas.length - 1].focus();
    }
  });

  // Mode Toggle (Visual vs Raw HTML)
  document.querySelectorAll('.editor-mode-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.editor-mode-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const mode = btn.dataset.mode;

      if (mode === 'raw') {
        currentMode = 'raw';
        serializeBlocksToContent();
        blocksContainer.style.display = 'none';
        rawContainer.style.display = 'block';
        rawContainer.innerHTML = '';

        const rawTextarea = document.createElement('textarea');
        rawTextarea.style.width = '100%';
        rawTextarea.style.minHeight = '360px';
        rawTextarea.style.padding = '12px';
        rawTextarea.style.fontFamily = 'monospace';
        rawTextarea.style.fontSize = '13px';
        rawTextarea.style.lineHeight = '1.6';
        rawTextarea.style.border = '1px solid #cbd5e1';
        rawTextarea.style.borderRadius = '6px';
        rawTextarea.value = contentTextarea.value;

        rawTextarea.addEventListener('input', () => {
          contentTextarea.value = rawTextarea.value;
        });

        rawContainer.appendChild(rawTextarea);
      } else {
        currentMode = 'visual';
        blocks = parseContentToBlocks(contentTextarea.value);
        rawContainer.style.display = 'none';
        blocksContainer.style.display = 'block';
        renderBlocks();
      }
    });
  });

  // Drag & Drop support
  blocksContainer.addEventListener('dragover', e => {
    e.preventDefault();
    blocksContainer.classList.add('drag-over');
  });

  blocksContainer.addEventListener('dragleave', e => {
    if (!blocksContainer.contains(e.relatedTarget)) {
      blocksContainer.classList.remove('drag-over');
    }
  });

  blocksContainer.addEventListener('drop', e => {
    e.preventDefault();
    blocksContainer.classList.remove('drag-over');
    if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFilesUpload(Array.from(e.dataTransfer.files), blocks.length);
    }
  });

  // Gallery Modal
  document.getElementById('btn-open-gallery').addEventListener('click', async () => {
    const modal = document.createElement('div');
    modal.className = 'editor-modal-backdrop';
    modal.innerHTML = `
      <div class="editor-modal-dialog">
        <div class="editor-modal-header">
          <h3>🖼️ Thư viện ảnh đã tải lên</h3>
          <button type="button" class="editor-modal-close">✕</button>
        </div>
        <div class="editor-modal-body">
          <p style="color: #64748b; font-size: 12px; margin-top: 0;">Các hình ảnh đã tải lên hệ thống. Bấm "+ Chèn vào bài" để chèn ảnh vào cuối bài viết.</p>
          <div class="editor-gallery-grid" id="gallery-grid">
            <p>Đang tải danh sách ảnh…</p>
          </div>
        </div>
      </div>
    `;

    document.body.appendChild(modal);

    modal.querySelector('.editor-modal-close').addEventListener('click', () => modal.remove());
    modal.addEventListener('click', e => {
      if (e.target === modal) modal.remove();
    });

    try {
      const url = postId ? `/api/v1/news/images/?post_id=${postId}` : `/api/v1/news/images/`;
      const res = await fetch(url);
      const data = await res.json();
      const grid = modal.querySelector('#gallery-grid');
      grid.innerHTML = '';

      if (!data.items || data.items.length === 0) {
        grid.innerHTML = '<p style="color: #94a3b8; font-style: italic;">Chưa có ảnh nào được tải lên.</p>';
        return;
      }

      data.items.forEach(item => {
        const card = document.createElement('div');
        card.className = 'editor-gallery-card';
        card.innerHTML = `
          <img src="${escapeHtml(item.url)}" alt="${escapeHtml(item.caption || '')}" />
          <div class="editor-gallery-card-info">
            <strong>${escapeHtml(item.caption || 'Hình ảnh')}</strong>
          </div>
          <div class="editor-gallery-card-actions">
            <button type="button" class="editor-image-action-btn btn-insert-from-gallery">+ Chèn vào bài</button>
            <button type="button" class="editor-image-action-btn btn-gallery-cover" title="Đặt làm ảnh bìa">⭐ Bìa</button>
          </div>
        `;

        card.querySelector('.btn-insert-from-gallery').addEventListener('click', () => {
          blocks.push({
            type: 'image',
            url: item.url,
            caption: item.caption || ''
          });
          renderBlocks();
          modal.remove();
          showToast('✓ Đã chèn ảnh vào bài viết!');
        });

        card.querySelector('.btn-gallery-cover').addEventListener('click', () => {
          const coverInput = document.querySelector('input#id_cover_image_url');
          if (coverInput) {
            coverInput.value = item.url;
            showToast('✓ Đã đặt làm Ảnh đại diện bài viết!');
          }
        });

        grid.appendChild(card);
      });
    } catch (e) {
      modal.querySelector('#gallery-grid').innerHTML = `<p style="color: red;">Lỗi tải ảnh: ${e.message}</p>`;
    }
  });

  // Preview Modal
  document.getElementById('btn-preview-article').addEventListener('click', () => {
    serializeBlocksToContent();
    const titleVal = document.querySelector('input#id_title')?.value || 'Tiêu đề bài viết';
    const summaryVal = document.querySelector('input#id_summary')?.value || '';
    const contentHtml = contentTextarea.value;

    const modal = document.createElement('div');
    modal.className = 'editor-modal-backdrop';
    modal.innerHTML = `
      <div class="editor-modal-dialog" style="max-width: 840px;">
        <div class="editor-modal-header">
          <h3>👁️ Xem trước hiển thị bài viết trên Website</h3>
          <button type="button" class="editor-modal-close">✕</button>
        </div>
        <div class="editor-modal-body" style="background: #fafcfb;">
          <article style="max-width: 720px; margin: 0 auto; background: #fff; padding: 24px; border-radius: 8px; border: 1px solid #e5ebe8;">
            <h1 style="color: #0b6076; font-size: 24px; line-height: 1.4; margin-top: 0;">${escapeHtml(titleVal)}</h1>
            ${summaryVal ? `<p style="font-size: 15px; font-weight: 500; color: #475569; line-height: 1.6; border-left: 3px solid #0b6076; padding-left: 12px; margin-bottom: 20px;">${escapeHtml(summaryVal)}</p>` : ''}
            <div class="article-preview-body" style="font-size: 15px; line-height: 1.8; color: #1e293b;">
              ${contentHtml}
            </div>
          </article>
        </div>
      </div>
    `;

    document.body.appendChild(modal);
    modal.querySelector('.editor-modal-close').addEventListener('click', () => modal.remove());
    modal.addEventListener('click', e => {
      if (e.target === modal) modal.remove();
    });
  });

  // Toast Notification
  function showToast(msg) {
    const toast = document.createElement('div');
    toast.style.position = 'fixed';
    toast.style.bottom = '24px';
    toast.style.right = '24px';
    toast.style.background = '#0b6076';
    toast.style.color = '#ffffff';
    toast.style.padding = '10px 18px';
    toast.style.borderRadius = '8px';
    toast.style.boxShadow = '0 4px 16px rgba(0,0,0,0.2)';
    toast.style.fontSize = '13px';
    toast.style.fontWeight = '600';
    toast.style.zIndex = '99999';
    toast.style.transition = 'opacity 0.3s';
    toast.textContent = msg;

    document.body.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      setTimeout(() => toast.remove(), 300);
    }, 2800);
  }

  // Before form submit, ensure content is serialized
  const form = contentTextarea.closest('form');
  if (form) {
    form.addEventListener('submit', () => {
      serializeBlocksToContent();
    });
  }

  // Initial load
  blocks = parseContentToBlocks(contentTextarea.value);
  renderBlocks();
});
