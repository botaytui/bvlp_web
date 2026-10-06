/**
 * ==========================================================================
 * BỆNH VIỆN LAO VÀ BỆNH PHỔI BẠC LIÊU - CHATBOT TRỢ LÝ Y TẾ AI
 * Client-side widget with dynamic On/Off config, FAQ & DVKT lookup
 * ==========================================================================
 */

(function () {
  'use strict';

  // Prevent multiple script execution
  if (window.__HOSPITAL_CHATBOT_INITIALIZED__) return;
  window.__HOSPITAL_CHATBOT_INITIALIZED__ = true;

  // Resolve API Base URL
  const configuredApiBase = document.querySelector('meta[name="booking-api-base-url"]')?.content?.trim();
  const isLocalHost = ['127.0.0.1', 'localhost'].includes(window.location.hostname);
  const API_BASE = configuredApiBase || (isLocalHost ? 'http://127.0.0.1:8002' : '');

  // Session ID
  let sessionId = localStorage.getItem('hospital_chat_session_id');
  if (!sessionId) {
    sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substring(2, 9);
    localStorage.setItem('hospital_chat_session_id', sessionId);
  }

  let chatbotConfig = {
    is_enabled: false,
    bot_name: 'Trợ lý Y tế<br>Bệnh viện Lao và Bệnh phổi Bạc Liêu',
    welcome_message: 'Xin chào! Tôi có thể hỗ trợ bạn tìm hiểu thông tin khám chữa bệnh.',
    emergency_hotline: '0291 3 678 977',
    disclaimer_text: 'Thông tin mang tính tham khảo y tế, không thay thế chẩn đoán trực tiếp của Bác sĩ.',
    quick_prompts: [
      '🕒 Giờ làm việc & Lịch khám',
      '💳 Khám BHYT cần giấy tờ gì?',
      '🩺 Triệu chứng nghi ngờ Lao phổi',
      '💰 Tra cứu giá X-quang & Xét nghiệm',
    ],
  };

  let isChatOpen = false;
  let chatMessagesHistory = [];

  // Simple Markdown to HTML parser
  function parseMarkdown(text) {
    if (!text) return '';
    let html = text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');

    // Bold **text**
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    // Italic *text*
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
    // Links [title](url)
    html = html.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
    // Inline code `code`
    html = html.replace(/`(.*?)`/g, '<code>$1</code>');
    // Line breaks
    html = html.replace(/\n/g, '<br>');

    return html;
  }

  // Fetch remote config & initialize
  async function checkAndInitChatbot() {
    try {
      const response = await fetch(`${API_BASE}/api/v1/chatbot/config/`, {
        method: 'GET',
        headers: { 'Accept': 'application/json' },
      });

      if (!response.ok) return;

      const data = await response.json();
      if (data && data.success && data.data) {
        chatbotConfig = { ...chatbotConfig, ...data.data };

        // If Disabled in Admin, do not mount the widget!
        if (!chatbotConfig.is_enabled) {
          console.log('[Chatbot] Disabled via Admin configuration.');
          return;
        }

        // Render Widget
        renderChatbotWidget();
      }
    } catch (err) {
      console.warn('[Chatbot] Could not load config:', err);
    }
  }

  function renderChatbotWidget() {
    const root = document.createElement('div');
    root.id = 'hospital-chatbot-root';
    root.innerHTML = `
      <!-- Launcher Button -->
      <div id="hospital-chatbot-launcher" role="button" aria-label="Mở Trợ lý Y tế AI">
        <div class="cb-tooltip-badge" id="cb-tooltip">
          <span>💬 Bác sĩ AI</span> · Tư vấn 24/7
        </div>
        <button class="cb-launcher-btn" type="button" aria-expanded="false">
          <div class="cb-pulse-ring"></div>
          <!-- Chat Icon (Medical Stethoscope / Message) -->
          <svg class="cb-icon-chat" viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path>
          </svg>
          <!-- Close Icon -->
          <svg class="cb-icon-close" viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>

      <!-- Main Chat Window -->
      <div id="hospital-chatbot-window" role="dialog" aria-modal="true" aria-hidden="true">
        <!-- Header -->
        <div class="cb-header">
          <div class="cb-header-profile">
            <div class="cb-avatar">
              <svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor">
                <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-2 10h-4v4h-2v-4H7v-2h4V7h2v4h4v2z"/>
              </svg>
              <div class="cb-status-dot"></div>
            </div>
            <div class="cb-header-info">
              <h4 id="cb-bot-title">${(chatbotConfig.bot_name || '').replace(/\n/g, '<br>').replace(/Trợ lý Y tế BV Lao & Bệnh Phổi Bạc Liêu/g, 'Trợ lý Y tế<br>Bệnh viện Lao và Bệnh phổi Bạc Liêu')}</h4>
              <p>
                <span style="display:inline-block; width:6px; height:6px; background:#4ade80; border-radius:50%;"></span>
                Trực tuyến · Sẵn sàng giải đáp
              </p>
            </div>
          </div>
          <div class="cb-header-actions">
            <button class="cb-header-btn" id="cb-btn-reset" title="Làm mới cuộc trò chuyện" aria-label="Làm mới">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"></path>
                <path d="M3 3v5h5"></path>
              </svg>
            </button>
            <button class="cb-header-btn" id="cb-btn-minimize" title="Thu nhỏ" aria-label="Thu nhỏ">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <line x1="5" y1="12" x2="19" y2="12"></line>
              </svg>
            </button>
          </div>
        </div>

        <!-- Body / Chat log -->
        <div class="cb-body" id="cb-messages-body">
          <!-- Initial Welcome Card -->
          <div class="cb-welcome-box">
            <h5>
              <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>
              </svg>
              Tư vấn & Hướng dẫn y tế
            </h5>
            <div>${parseMarkdown(chatbotConfig.welcome_message)}</div>
            <div class="cb-disclaimer">
              <span>⚠️</span>
              <span>${chatbotConfig.disclaimer_text}</span>
            </div>
          </div>

          <!-- Quick Prompts Section -->
          <div id="cb-quick-prompts-container">
            <div class="cb-quick-prompts-title">Câu hỏi thường gặp:</div>
            <div class="cb-quick-prompts" id="cb-quick-prompts-list">
              ${chatbotConfig.quick_prompts.map(p => `<button type="button" class="cb-chip-btn" data-prompt="${p}">${p}</button>`).join('')}
            </div>
          </div>
        </div>

        <!-- Footer / Input Form -->
        <div class="cb-footer">
          <form class="cb-input-form" id="cb-chat-form">
            <input 
              type="text" 
              class="cb-input-field" 
              id="cb-user-input" 
              placeholder="Nhập câu hỏi (VD: BHYT, giá X-quang, lịch khám...)..." 
              autocomplete="off" 
              maxlength="500"
              required
            />
            <button type="submit" class="cb-send-btn" id="cb-btn-send" title="Gửi tin nhắn" aria-label="Gửi">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
              </svg>
            </button>
          </form>
          <div class="cb-footer-hint">Nhấn <b>Enter</b> để gửi tin nhắn</div>
        </div>
      </div>
    `;

    document.body.appendChild(root);
    setupEventListeners();
  }

  function setupEventListeners() {
    const launcher = document.querySelector('#hospital-chatbot-launcher');
    const launcherBtn = launcher.querySelector('.cb-launcher-btn');
    const chatWindow = document.querySelector('#hospital-chatbot-window');
    const tooltip = document.querySelector('#cb-tooltip');
    const minimizeBtn = document.querySelector('#cb-btn-minimize');
    const resetBtn = document.querySelector('#cb-btn-reset');
    const chatForm = document.querySelector('#cb-chat-form');
    const inputField = document.querySelector('#cb-user-input');
    const messagesBody = document.querySelector('#cb-messages-body');

    // Toggle Chat
    function toggleChat(openState) {
      isChatOpen = openState !== undefined ? openState : !isChatOpen;
      launcher.classList.toggle('active', isChatOpen);
      chatWindow.classList.toggle('open', isChatOpen);
      chatWindow.setAttribute('aria-hidden', String(!isChatOpen));
      launcherBtn.setAttribute('aria-expanded', String(isChatOpen));

      if (isChatOpen) {
        if (tooltip) tooltip.style.display = 'none';
        setTimeout(() => inputField?.focus(), 300);
        scrollToBottom();
      }
    }

    launcher.addEventListener('click', () => toggleChat());
    minimizeBtn.addEventListener('click', () => toggleChat(false));

    // Reset conversation
    resetBtn.addEventListener('click', () => {
      if (confirm('Bạn có muốn làm mới cuộc trò chuyện này không?')) {
        sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substring(2, 9);
        localStorage.setItem('hospital_chat_session_id', sessionId);
        
        // Remove dynamic user/bot message nodes, keep welcome card
        const dynamicNodes = messagesBody.querySelectorAll('.cb-message, .cb-typing-indicator');
        dynamicNodes.forEach(n => n.remove());

        // Restore quick prompts
        const promptsContainer = document.querySelector('#cb-quick-prompts-container');
        if (promptsContainer) promptsContainer.style.display = 'block';
      }
    });

    // Handle Quick Prompt Chip Click
    messagesBody.addEventListener('click', (e) => {
      const chip = e.target.closest('.cb-chip-btn');
      if (chip && chip.dataset.prompt) {
        // Strip emoji icons for cleaner query if needed or send as is
        const cleanText = chip.dataset.prompt.replace(/^[^\w\s\d\p{L}]+/u, '').trim();
        sendMessage(cleanText);
      }

      // Handle action buttons inside replies
      const actionBtn = e.target.closest('.cb-action-btn');
      if (actionBtn) {
        const actionType = actionBtn.dataset.action;
        if (actionType === 'open_booking') {
          toggleChat(false);
          // Trigger native website booking modal
          const bookingDialog = document.querySelector('#booking-dialog');
          if (bookingDialog && typeof bookingDialog.showModal === 'function') {
            bookingDialog.showModal();
          } else {
            const bookingSec = document.querySelector('#dat-lich');
            if (bookingSec) bookingSec.scrollIntoView({ behavior: 'smooth' });
          }
        }
      }

      // Handle Feedback like/dislike
      const feedbackBtn = e.target.closest('.cb-feedback-btn');
      if (feedbackBtn && feedbackBtn.dataset.logId) {
        const logId = feedbackBtn.dataset.logId;
        const feedback = feedbackBtn.dataset.type;
        sendFeedback(logId, feedback, feedbackBtn);
      }
    });

    // Handle Form Submit
    chatForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const text = inputField.value.trim();
      if (!text) return;
      inputField.value = '';
      sendMessage(text);
    });
  }

  function scrollToBottom() {
    const body = document.querySelector('#cb-messages-body');
    if (body) {
      setTimeout(() => {
        body.scrollTop = body.scrollHeight;
      }, 50);
    }
  }

  function appendUserMessage(text) {
    const body = document.querySelector('#cb-messages-body');
    const msgDiv = document.createElement('div');
    msgDiv.className = 'cb-message user';
    msgDiv.innerHTML = `
      <div class="cb-msg-avatar">Bạn</div>
      <div class="cb-msg-content">${parseMarkdown(text)}</div>
    `;
    body.appendChild(msgDiv);
    scrollToBottom();
  }

  function showTypingIndicator() {
    const body = document.querySelector('#cb-messages-body');
    const typingDiv = document.createElement('div');
    typingDiv.id = 'cb-typing-indicator-box';
    typingDiv.className = 'cb-typing-indicator';
    typingDiv.innerHTML = `
      <div class="cb-typing-dot"></div>
      <div class="cb-typing-dot"></div>
      <div class="cb-typing-dot"></div>
    `;
    body.appendChild(typingDiv);
    scrollToBottom();
    return typingDiv;
  }

  function hideTypingIndicator() {
    document.querySelector('#cb-typing-indicator-box')?.remove();
  }

  function appendBotMessage(data) {
    hideTypingIndicator();
    const body = document.querySelector('#cb-messages-body');
    const msgDiv = document.createElement('div');
    msgDiv.className = `cb-message bot ${data.is_emergency ? 'emergency' : ''}`;

    let actionsHtml = '';
    if (data.actions && data.actions.length > 0) {
      actionsHtml = '<div class="cb-msg-actions">';
      data.actions.forEach((act) => {
        const cleanLabel = (act.label || '').replace(/^[^\w\s\d\p{L}]+/u, '').trim();
        if (act.type === 'modal') {
          actionsHtml += `<button type="button" class="cb-action-btn" data-action="${act.action}">📅 ${cleanLabel}</button>`;
        } else if (act.type === 'call') {
          actionsHtml += `<a href="tel:${act.value.replace(/[^0-9]/g, '')}" class="cb-action-btn call-btn">📞 ${cleanLabel}</a>`;
        } else if (act.type === 'link') {
          actionsHtml += `<a href="${act.url}" class="cb-action-btn">🔗 ${cleanLabel}</a>`;
        }
      });
      actionsHtml += '</div>';
    }

    let feedbackHtml = '';
    if (data.log_id) {
      feedbackHtml = `
        <div class="cb-feedback-row">
          <span>Câu trả lời có hữu ích không?</span>
          <button type="button" class="cb-feedback-btn" data-log-id="${data.log_id}" data-type="like" title="Hài lòng">👍</button>
          <button type="button" class="cb-feedback-btn" data-log-id="${data.log_id}" data-type="dislike" title="Chưa hài lòng">👎</button>
        </div>
      `;
    }

    let suggestionsHtml = '';
    if (data.suggestions && data.suggestions.length > 0) {
      suggestionsHtml = `
        <div style="margin-top: 10px;">
          <div style="font-size:11.5px; color:#64748b; margin-bottom:4px; font-weight:600;">Gợi ý câu hỏi liên quan:</div>
          <div class="cb-quick-prompts">
            ${data.suggestions.map(s => `<button type="button" class="cb-chip-btn" data-prompt="${s}">${s}</button>`).join('')}
          </div>
        </div>
      `;
    }

    msgDiv.innerHTML = `
      <div class="cb-msg-avatar">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
          <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-2 10h-4v4h-2v-4H7v-2h4V7h2v4h4v2z"/>
        </svg>
      </div>
      <div class="cb-msg-content">
        <div>${parseMarkdown(data.reply || '')}</div>
        ${actionsHtml}
        ${suggestionsHtml}
        ${feedbackHtml}
      </div>
    `;

    body.appendChild(msgDiv);
    scrollToBottom();
  }

  async function sendMessage(text) {
    appendUserMessage(text);
    showTypingIndicator();

    const sendBtn = document.querySelector('#cb-btn-send');
    if (sendBtn) sendBtn.disabled = true;

    try {
      const response = await fetch(`${API_BASE}/api/v1/chatbot/chat/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({
          message: text,
          session_id: sessionId,
        }),
      });

      const result = await response.json().catch(() => ({}));
      if (response.ok && result && result.success) {
        appendBotMessage(result);
      } else {
        appendBotMessage({
          reply: result.message || 'Xin lỗi, hệ thống máy chủ đang bận xử lý. Vui lòng thử lại sau giây lát hoặc gọi hotline 0291 3 678 977.',
          is_emergency: false,
        });
      }
    } catch (error) {
      appendBotMessage({
        reply: 'Không thể kết nối đến máy chủ. Quý khách vui lòng kiểm tra kết nối internet hoặc gọi hotline **0291 3 678 977** để được hỗ trợ trực tiếp.',
        is_emergency: false,
      });
    } finally {
      if (sendBtn) sendBtn.disabled = false;
    }
  }

  async function sendFeedback(logId, feedbackType, btnElement) {
    try {
      const row = btnElement.closest('.cb-feedback-row');
      row.querySelectorAll('.cb-feedback-btn').forEach(b => b.classList.remove('active'));
      btnElement.classList.add('active');

      await fetch(`${API_BASE}/api/v1/chatbot/feedback/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ log_id: logId, feedback: feedbackType }),
      });

      row.innerHTML = '<span style="color:#00a896; font-weight:500;">✓ Cảm ơn bạn đã phản hồi!</span>';
    } catch (e) {
      console.warn('Feedback send failed:', e);
    }
  }

  // Run on DOM Ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', checkAndInitChatbot);
  } else {
    checkAndInitChatbot();
  }
})();
