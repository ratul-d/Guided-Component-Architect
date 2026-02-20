// State
let framework = 'tailwind';
let sessionId = generateUUID();
const messages = [];

// DOM Elements
const frameworkSelect = document.getElementById('frameworkSelect');
const messagesContainer = document.getElementById('messagesContainer');
const promptInput = document.getElementById('promptInput');
const generateForm = document.getElementById('generateForm');
const resetBtn = document.getElementById('resetBtn');

// Utility Functions
function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

function getFrameworkLabel(fw) {
  const labels = {
    'tailwind': 'Tailwind CSS',
    'angular-material': 'Angular Material',
    'custom': 'Custom CSS'
  };
  return labels[fw] || fw;
}

function escapeHtml(text) {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };
  return text.replace(/[&<>"']/g, m => map[m]);
}

function scrollToBottom() {
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function renderWelcome() {
  messagesContainer.innerHTML = `
    <div class="welcome">
      <div class="welcome-icon">🎨</div>
      <h2>Ready to generate components</h2>
      <p>Describe the component you want to create</p>
    </div>
  `;
}

function renderMessages() {
  if (messages.length === 0) {
    renderWelcome();
    return;
  }

  let html = '';

  messages.forEach((msg) => {
    if (msg.type === 'user') {
      html += `
        <div class="message user">
          <div class="message-content">
            ${escapeHtml(msg.prompt)}
            <div style="font-size: 0.75rem; opacity: 0.8; margin-top: 0.25rem;">${getFrameworkLabel(msg.framework)}</div>
          </div>
        </div>
      `;
    } else {
      html += `
        <div class="message assistant">
          <div class="message-content">
            <div class="code-wrapper">
              <div class="code-header">
                <span>Generated Component</span>
                <div class="code-actions">
                  <button type="button" class="copy-button" data-message-id="${msg.id}">
                    <span>Copy</span>
                  </button>
                  <button type="button" class="download-button" data-message-id="${msg.id}">
                    <span>Download</span>
                  </button>
                </div>
              </div>
              <pre><code id="code-${msg.id}">${escapeHtml(msg.code)}</code></pre>
            </div>
          </div>
        </div>
      `;
    }
  });

  messagesContainer.innerHTML = html;

  // Add syntax highlighting
  document.querySelectorAll('pre code').forEach((block) => {
    hljs.highlightElement(block);
  });

  // Add copy button listeners
  document.querySelectorAll('.copy-button').forEach(btn => {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      const messageId = this.dataset.messageId;
      const codeElement = document.getElementById(`code-${messageId}`);
      const code = codeElement.textContent;

      navigator.clipboard.writeText(code).then(() => {
        this.classList.add('copied');
        this.innerHTML = '<span>Copied!</span>';

        setTimeout(() => {
          this.classList.remove('copied');
          this.innerHTML = '<span>Copy</span>';
        }, 2000);
      });
    });
  });

  // Add download button listeners
  document.querySelectorAll('.download-button').forEach(btn => {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      const url = `http://localhost:8000/export/${sessionId}`;

      const link = document.createElement('a');
      link.href = url;
      link.download = 'generated.component.ts';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    });
  });

  scrollToBottom();
}

function addMessage(type, prompt = null, code = null, msgFramework = null) {
  const messageId = `msg-${Date.now()}-${Math.random()}`;
  messages.push({ id: messageId, type, prompt, code, framework: msgFramework });
  renderMessages();
}

// Event Listeners
frameworkSelect.addEventListener('change', (e) => {
  framework = e.target.value;
});

// Reset chat
resetBtn.addEventListener('click', async () => {
  try {
    await fetch(`http://localhost:8000/reset/${sessionId}`, {
      method: 'POST',
    });
  } catch (error) {
    console.error('Error resetting session:', error);
  }

  messages.length = 0;
  sessionId = generateUUID();
  renderWelcome();
});

generateForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const prompt = promptInput.value.trim();
  if (!prompt) return;

  const currentFramework = framework;

  // Add user message
  addMessage('user', prompt, null, currentFramework);
  promptInput.value = '';
  promptInput.disabled = true;

  // Add loading message to messages array
  const loadingMsgId = `loading-${Date.now()}`;
  messages.push({ id: loadingMsgId, type: 'loading' });

  // Show loading state
  const loadingHtml = `
    <div class="message assistant">
      <div class="message-content">
        <div class="loading">
          <div class="dot"></div>
          <div class="dot"></div>
          <div class="dot"></div>
        </div>
      </div>
    </div>
  `;
  messagesContainer.innerHTML += loadingHtml;
  scrollToBottom();

  try {
    const response = await fetch('http://localhost:8000/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        prompt: prompt,
        css_framework: currentFramework,
        session_id: sessionId,
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to generate component');
    }

    const data = await response.json();
    messages.pop(); // Remove loading message
    addMessage('assistant', null, data.code);
  } catch (error) {
    console.error('Error:', error);
    messages.pop(); // Remove loading message
    addMessage('assistant', null, 'Error generating component. Please try again.');
  } finally {
    promptInput.disabled = false;
    promptInput.focus();
  }
});

// Initialize
renderWelcome();
