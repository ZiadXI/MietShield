// ======================================================
// MIETSHIELD v3 — ChatGPT-Style JS
// ======================================================

const API_BASE = "http://127.0.0.1:8000/api";

// ======================================================
// STATE
// ======================================================
let currentThreadId = null;
let sessions        = loadSessions();
let selectedFile    = null;

function loadSessions() {
  try { return JSON.parse(localStorage.getItem("mietshield_sessions_v3")) || {}; }
  catch { return {}; }
}
function saveSessions() {
  localStorage.setItem("mietshield_sessions_v3", JSON.stringify(sessions));
}

// Configure Marked.js for safe markdown rendering
if (typeof marked !== 'undefined') {
  marked.setOptions({ breaks: true, gfm: true });
}

// ======================================================
// STARTUP
// ======================================================
document.addEventListener("DOMContentLoaded", () => {
  renderSidebarHistory();
  const lastId = localStorage.getItem("mietshield_last_thread_v3");
  if (lastId && sessions[lastId]) {
    switchToSession(lastId);
  } else {
    startNewChat(); // Always start with a new chat if none exists
  }

  // Setup Rename Modal listeners
  document.getElementById("btn-save-rename").onclick = saveRename;
  document.getElementById("rename-input").addEventListener("keypress", (e) => {
    if (e.key === "Enter") saveRename();
  });
});

// ======================================================
// NEW CHAT
// ======================================================
function startNewChat() {
  const newId = crypto.randomUUID();
  const label = `New Chat`;
  sessions[newId] = { label, messages: [] };
  saveSessions();
  switchToSession(newId);
  renderSidebarHistory();
  clearAttachment();
}

// ======================================================
// SWITCH SESSION
// ======================================================
function switchToSession(threadId) {
  currentThreadId = threadId;
  localStorage.setItem("mietshield_last_thread_v3", threadId);

  // Update badge
  document.getElementById("session-label").textContent = threadId.slice(0, 8) + "…";
  document.getElementById("status-dot").classList.add("active");

  // Restore chat messages
  const chatWindow = document.getElementById("chat-window");
  chatWindow.innerHTML = "";
  const session = sessions[threadId];
  
  if (!session || session.messages.length === 0) {
    chatWindow.innerHTML = `
      <div class="chat-welcome" id="chat-welcome">
        <span class="chat-welcome-icon">🛡️</span>
        <h2 class="chat-welcome-title">How can I help with your lease?</h2>
        <p class="chat-welcome-sub">Ask a question about German tenant law, or attach your lease PDF and I'll analyze it for red flags.</p>
      </div>`;
  } else {
    session.messages.forEach(msg => {
      renderMessage(msg.role, msg.content, msg.attachmentName, false);
    });
    scrollChatToBottom();
  }

  document.querySelectorAll(".history-item").forEach(el => {
    el.classList.toggle("active", el.dataset.id === threadId);
  });
}

// ======================================================
// SIDEBAR
// ======================================================
function renderSidebarHistory() {
  const container = document.getElementById("chat-history");
  container.querySelectorAll(".history-item").forEach(el => el.remove());
  Object.entries(sessions).reverse().forEach(([id, session]) => {
    const item = document.createElement("div");
    item.className = "history-item" + (id === currentThreadId ? " active" : "");
    item.dataset.id = id;
    
    // Title text
    const textSpan = document.createElement("span");
    textSpan.className = "history-text";
    textSpan.textContent = session.label;
    item.appendChild(textSpan);
    
    // Edit button
    const editBtn = document.createElement("button");
    editBtn.className = "btn-edit-title";
    editBtn.innerHTML = "✏️";
    editBtn.title = "Rename Chat";
    editBtn.onclick = (e) => {
      e.stopPropagation(); // prevent switching sessions
      openRenameModal(id, session.label);
    };
    item.appendChild(editBtn);

    item.onclick = () => switchToSession(id);
    container.appendChild(item);
  });
}

function toggleSidebar() {
  document.getElementById("sidebar").classList.toggle("collapsed");
}

// ======================================================
// FILE ATTACHMENT
// ======================================================
function handleFileSelect(event) {
  const file = event.target.files[0];
  if (!file) return;
  if (!file.name.endsWith(".pdf")) {
    alert("Please attach a PDF file.");
    event.target.value = "";
    return;
  }
  selectedFile = file;
  document.getElementById("attachment-name").textContent = file.name;
  document.getElementById("attachment-preview").classList.remove("hidden");
  document.getElementById("chat-input").focus();
}

function clearAttachment() {
  selectedFile = null;
  document.getElementById("file-input").value = "";
  document.getElementById("attachment-preview").classList.add("hidden");
}

// ======================================================
// SEND MESSAGE
// ======================================================
async function sendMessage(event) {
  event.preventDefault();
  const inputEl = document.getElementById("chat-input");
  const text = inputEl.value.trim();
  
  // Need either text or a file to send
  if (!text && !selectedFile) return;
  if (!currentThreadId) startNewChat();

  const fileToSend = selectedFile; // Capture current file
  const textToSend = text;
  
  // Clear UI immediately
  inputEl.value = "";
  clearAttachment();
  document.getElementById("btn-send").disabled = true;

  // Remove welcome screen
  const welcome = document.getElementById("chat-welcome");
  if (welcome) welcome.remove();

  // Render user message immediately
  renderMessage("user", textToSend, fileToSend ? fileToSend.name : null);
  
  // Save to session history
  sessions[currentThreadId].messages.push({ 
    role: "user", 
    content: textToSend,
    attachmentName: fileToSend ? fileToSend.name : null
  });
  
  // Update session label if it's the first message
  if (sessions[currentThreadId].label === "New Chat") {
    sessions[currentThreadId].label = fileToSend ? fileToSend.name.replace(".pdf", "") : (textToSend.substring(0, 30) || "Chat");
    renderSidebarHistory();
  }
  saveSessions();

  const typingEl = showTypingIndicator();

  // Prepare FormData
  const formData = new FormData();
  formData.append("message", textToSend);
  formData.append("thread_id", currentThreadId);
  if (fileToSend) formData.append("file", fileToSend);

  try {
    const res = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      body: formData // Note: fetch automatically sets the correct multipart/form-data boundary
    });
    
    typingEl.remove();

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Chat error");
    }
    const data = await res.json();
    
    renderMessage("assistant", data.response);
    sessions[currentThreadId].messages.push({ role: "assistant", content: data.response });
    saveSessions();

  } catch (err) {
    typingEl.remove();
    renderMessage("assistant", "⚠️ Error: " + err.message);
  } finally {
    document.getElementById("btn-send").disabled = false;
    document.getElementById("chat-input").focus();
  }
}

// ======================================================
// RENDER HELPERS
// ======================================================
function renderMessage(role, content, attachmentName = null, scroll = true) {
  const chatWindow = document.getElementById("chat-window");
  const wrapper = document.createElement("div");
  wrapper.className = `message ${role}`;
  
  // Format content
  let displayContent = "";
  
  if (role === "user") {
    // Show attachment pill if present
    if (attachmentName) {
      displayContent += `
        <div class="msg-attachment">
          <span class="msg-attachment-icon">📄</span>
          <span class="msg-attachment-name">${escapeHtml(attachmentName)}</span>
        </div>
      `;
    }
    if (content) displayContent += `<div>${escapeHtml(content)}</div>`;
  } else {
    // Assistant message -> parse Markdown
    displayContent = typeof marked !== 'undefined' ? marked.parse(content) : escapeHtml(content);
  }

  wrapper.innerHTML = `
    <div class="message-avatar">${role === "user" ? "👤" : "🛡️"}</div>
    <div class="message-bubble">${displayContent}</div>
  `;
  
  chatWindow.appendChild(wrapper);
  if (scroll) scrollChatToBottom();
}

function showTypingIndicator() {
  const chatWindow = document.getElementById("chat-window");
  const el = document.createElement("div");
  el.className = "message assistant";
  el.innerHTML = `<div class="message-avatar">🛡️</div><div class="message-bubble"><div class="typing-dots"><span></span><span></span><span></span></div></div>`;
  chatWindow.appendChild(el);
  scrollChatToBottom();
  return el;
}

function scrollChatToBottom() {
  const cw = document.getElementById("chat-window");
  if (cw) cw.scrollTop = cw.scrollHeight;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

// ======================================================
// RENAME MODAL
// ======================================================
let chatToRename = null;

function openRenameModal(id, currentName) {
  chatToRename = id;
  const modal = document.getElementById("rename-modal");
  const input = document.getElementById("rename-input");
  input.value = currentName;
  modal.classList.remove("hidden");
  setTimeout(() => {
    input.focus();
    input.select();
  }, 100);
}

function closeRenameModal() {
  chatToRename = null;
  document.getElementById("rename-modal").classList.add("hidden");
}

function saveRename() {
  if (!chatToRename) return;
  const newName = document.getElementById("rename-input").value.trim();
  if (newName !== "") {
    sessions[chatToRename].label = newName;
    saveSessions();
    renderSidebarHistory();
    if (chatToRename === currentThreadId) {
      document.getElementById("session-label").textContent = newName.slice(0, 8) + (newName.length > 8 ? "…" : "");
    }
  }
  closeRenameModal();
}
