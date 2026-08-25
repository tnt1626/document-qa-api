// State Management
let documentList = [];
let selectedDocumentId = ""; // Default to Search All
let chatHistory = []; // Array of {role: 'user'|'assistant', content: string}

// DOM Elements
const docListContainer = document.getElementById('doc-list');
const docCountEl = document.getElementById('doc-count');
const docSelect = document.getElementById('doc-select');
const fileInput = document.getElementById('file-input');
const uploadDropzone = document.getElementById('upload-dropzone');
const chatBox = document.getElementById('chat-box');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const clearChatBtn = document.getElementById('clear-chat-btn');
const toastEl = document.getElementById('toast-notification');

// Initialize Icons
function initIcons() {
    if (window.lucide) {
        window.lucide.createIcons();
    }
}

// Show Toast Notifications
function showToast(message, type = 'info') {
    toastEl.textContent = message;
    toastEl.className = `toast show ${type}`;
    
    // Add icon to toast
    const iconName = type === 'success' ? 'check-circle' : type === 'error' ? 'alert-triangle' : 'info';
    const icon = document.createElement('i');
    icon.setAttribute('data-lucide', iconName);
    toastEl.insertBefore(icon, toastEl.firstChild);
    initIcons();

    setTimeout(() => {
        toastEl.classList.remove('show');
    }, 4000);
}

// Fetch Document List from API
async function fetchDocuments() {
    try {
        const response = await fetch('/documents/?limit=50');
        if (!response.ok) throw new Error("Failed to fetch documents");
        documentList = await response.json();
        renderDocuments();
        updateDocumentDropdown();
    } catch (error) {
        console.error(error);
        showToast("Error loading document list", "error");
    }
}

// Render Documents in Sidebar
function renderDocuments() {
    docCountEl.textContent = documentList.length;
    docListContainer.innerHTML = '';

    if (documentList.length === 0) {
        docListContainer.innerHTML = `
            <div style="text-align: center; padding: 2rem; color: var(--text-secondary); font-size: 0.85rem;">
                No documents uploaded yet.
            </div>
        `;
        return;
    }

    documentList.forEach(doc => {
        const isActive = doc.id === selectedDocumentId;
        const item = document.createElement('div');
        item.className = `document-item ${isActive ? 'active' : ''}`;
        item.onclick = () => selectDocument(doc.id);

        const dateStr = new Date(doc.created_at).toLocaleString();

        item.innerHTML = `
            <div class="doc-header">
                <span class="doc-name" title="${doc.filename}">${doc.filename}</span>
                <div class="doc-actions">
                    <button class="doc-btn delete-btn" title="Delete Document" onclick="event.stopPropagation(); deleteDoc('${doc.id}')">
                        <i data-lucide="trash-2" style="width: 14px; height: 14px;"></i>
                    </button>
                </div>
            </div>
            <div class="doc-info">
                <span>Uploaded: ${dateStr.split(',')[0]}</span>
            </div>
            <div>
                <span class="doc-id-badge" onclick="event.stopPropagation(); copyToClipboard('${doc.id}')" title="Click to copy UUID">
                    <i data-lucide="copy" style="width: 10px; height: 10px;"></i>
                    ${doc.id.substring(0, 8)}...
                </span>
            </div>
        `;
        docListContainer.appendChild(item);
    });
    initIcons();
}

// Select a document from sidebar
function selectDocument(docId) {
    if (selectedDocumentId === docId) {
        selectedDocumentId = ""; // Toggle off
    } else {
        selectedDocumentId = docId;
    }
    docSelect.value = selectedDocumentId;
    renderDocuments();
    showToast(selectedDocumentId ? `Selected document context.` : `Switched to global search.`, "info");
}

// Update the Document Selection Dropdown
function updateDocumentDropdown() {
    // Keep the default option
    docSelect.innerHTML = '<option value="">🔍 Search All Documents</option>';
    documentList.forEach(doc => {
        const option = document.createElement('option');
        option.value = doc.id;
        option.textContent = `📄 ${doc.filename}`;
        docSelect.appendChild(option);
    });
    docSelect.value = selectedDocumentId;
}

// Dropdown Change Handler
docSelect.onchange = (e) => {
    selectedDocumentId = e.target.value;
    renderDocuments();
};

// Copy Document UUID
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast("Copied Document ID to clipboard!", "success");
    }).catch(err => {
        console.error("Could not copy text: ", err);
    });
}

// Delete Document
async function deleteDoc(docId) {
    if (!confirm("Are you sure you want to delete this document? All embedded chunks will be deleted permanently.")) return;
    
    try {
        const response = await fetch(`/documents/${docId}/`, {
            method: 'DELETE'
        });
        if (!response.ok) throw new Error("Delete failed");
        
        showToast("Document deleted successfully", "success");
        if (selectedDocumentId === docId) selectedDocumentId = "";
        await fetchDocuments();
    } catch (error) {
        console.error(error);
        showToast("Failed to delete document", "error");
    }
}

// Drag and Drop File Upload
uploadDropzone.onclick = () => fileInput.click();
fileInput.onchange = () => handleFileUpload(fileInput.files[0]);

uploadDropzone.ondragover = (e) => {
    e.preventDefault();
    uploadDropzone.classList.add('dragover');
};

uploadDropzone.ondragleave = () => {
    uploadDropzone.classList.remove('dragover');
};

uploadDropzone.ondrop = (e) => {
    e.preventDefault();
    uploadDropzone.classList.remove('dragover');
    if (e.dataTransfer.files.length > 0) {
        handleFileUpload(e.dataTransfer.files[0]);
    }
};

async function handleFileUpload(file) {
    if (!file) return;
    
    const ALLOWED_EXTENSIONS = ['.txt', '.md', '.html', '.css', '.csv', '.xml', '.json'];
    const extension = '.' + file.name.split('.').pop().toLowerCase();
    
    if (!ALLOWED_EXTENSIONS.includes(extension)) {
        showToast("Unsupported file format! Supported: " + ALLOWED_EXTENSIONS.join(', '), "error");
        return;
    }

    showToast(`Uploading and embedding '${file.name}'...`, "info");

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/documents/?chunk_size=500&overlap=50', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errDetail = await response.json();
            throw new Error(errDetail.detail || "Upload failed");
        }

        const data = await response.json();
        showToast(`Document uploaded successfully! Indexing task scheduled.`, "success");
        await fetchDocuments();
    } catch (error) {
        console.error(error);
        showToast(`Upload failed: ${error.message}`, "error");
    }
}

// Chat Implementation
sendBtn.onclick = () => submitQuestion();
userInput.onkeypress = (e) => {
    if (e.key === 'Enter') submitQuestion();
};

async function submitQuestion() {
    const questionText = userInput.value.trim();
    if (!questionText) return;

    // 1. Add User Message to Chat UI
    appendMessage(questionText, 'user');
    userInput.value = '';
    
    // Disable inputs during processing
    sendBtn.disabled = true;
    userInput.disabled = true;

    // 2. Add Loading Indicator
    const loadingMessageId = appendLoadingIndicator();

    try {
        // Prepare request body
        const requestBody = {
            question: questionText,
            chat_history: chatHistory
        };
        if (selectedDocumentId) {
            requestBody.document_id = selectedDocumentId;
        }

        const response = await fetch('/agent/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });

        // Remove loading indicator
        removeLoadingIndicator(loadingMessageId);

        if (!response.ok) {
            const errBody = await response.json();
            throw new Error(errBody.detail || "Server error");
        }

        const data = await response.json();
        
        // 3. Render Assistant Response
        appendMessage(data.answer, 'assistant', data.thought_steps);

        // 4. Update memory (Save user & assistant history)
        chatHistory.push({ role: 'user', content: questionText });
        chatHistory.push({ role: 'assistant', content: data.answer });

    } catch (error) {
        removeLoadingIndicator(loadingMessageId);
        console.error(error);
        appendMessage(`Sorry, I encountered an error: ${error.message}`, 'assistant');
        showToast("Error retrieving answer", "error");
    } finally {
        sendBtn.disabled = false;
        userInput.disabled = false;
        userInput.focus();
    }
}

// Append bubble to chat console
function appendMessage(text, role, thoughtSteps = []) {
    const messageContainer = document.createElement('div');
    messageContainer.className = `message ${role}`;

    const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const metaText = role === 'user' ? 'You' : 'Agent';

    let bubbleContent = '';
    if (role === 'assistant') {
        // Parse markdown text using Marked JS
        const parsedText = window.marked ? window.marked.parse(text) : escapeHtml(text);
        bubbleContent = `
            <div class="message-bubble markdown-body">
                ${parsedText}
                ${thoughtSteps && thoughtSteps.length > 0 ? renderThoughtSteps(thoughtSteps) : ''}
            </div>
        `;
    } else {
        bubbleContent = `
            <div class="message-bubble">
                ${escapeHtml(text)}
            </div>
        `;
    }

    messageContainer.innerHTML = `
        ${bubbleContent}
        <div class="message-meta">${metaText} • ${timestamp}</div>
    `;

    chatBox.appendChild(messageContainer);
    chatBox.scrollTop = chatBox.scrollHeight;
    initIcons();
}

// Render Collapsible Accordion for Thought Traces
function renderThoughtSteps(steps) {
    const accordionId = `accordion-${Math.random().toString(36).substr(2, 9)}`;
    const totalTokens = steps.reduce((sum, step) => sum + (step.token || 0), 0);
    let stepsHtml = '';

    steps.forEach(step => {
        let toolCallsHtml = '';
        if (step.tool_calls && step.tool_calls.length > 0) {
            step.tool_calls.forEach(tc => {
                const argsStr = typeof tc.arguments === 'object' ? JSON.stringify(tc.arguments) : tc.arguments;
                toolCallsHtml += `
                    <div class="step-tool">
                        <div class="tool-name"><i data-lucide="wrench" style="width: 12px; height: 12px; display: inline; vertical-align: middle;"></i> Calling Skill: ${tc.name}</div>
                        <div class="tool-args"><b>Args:</b> ${escapeHtml(argsStr)}</div>
                        <div class="tool-result"><b>Result:</b>\n${escapeHtml(tc.result || '')}</div>
                    </div>
                `;
            });
        }

        stepsHtml += `
            <div class="thought-step">
                <div class="step-label">▶ Loop Step ${step.loop_index + 1} (${step.token || 0} tokens)</div>
                ${step.thought ? `<div class="step-thought">${escapeHtml(step.thought)}</div>` : ''}
                ${toolCallsHtml}
            </div>
        `;
    });

    return `
        <div class="thought-accordion" id="${accordionId}">
            <div class="thought-header" onclick="toggleAccordion('${accordionId}')">
                <span><i data-lucide="eye" style="width: 14px; height: 14px; display: inline; vertical-align: middle; margin-right: 4px;"></i> View Agent Reasoning (${steps.length} steps | ${totalTokens} tokens)</span>
                <i data-lucide="chevron-down" class="thought-header-icon" style="width: 14px; height: 14px;"></i>
            </div>
            <div class="thought-content">
                ${stepsHtml}
            </div>
        </div>
    `;
}

// Toggle accordion open/close
window.toggleAccordion = function(accordionId) {
    const el = document.getElementById(accordionId);
    el.classList.toggle('open');
};

// HTML Escaping to prevent XSS and formatting issues
function escapeHtml(unsafe) {
    return unsafe
         .replace(/&/g, "&amp;")
         .replace(/</g, "&lt;")
         .replace(/>/g, "&gt;")
         .replace(/"/g, "&quot;")
         .replace(/'/g, "&#039;");
}

// Append Loading indicator bubble
function appendLoadingIndicator() {
    const id = `loading-${Math.random().toString(36).substr(2, 9)}`;
    const messageContainer = document.createElement('div');
    messageContainer.className = 'message assistant';
    messageContainer.id = id;

    messageContainer.innerHTML = `
        <div class="message-bubble" style="display: flex; gap: 8px; align-items: center; padding: 0.75rem 1.25rem;">
            <span>Agent is thinking</span>
            <span style="display: flex; gap: 3px;">
                <span style="width: 6px; height: 6px; background-color: var(--accent-cyan); border-radius: 50%; animation: pulse-glow 1s infinite alternate;"></span>
                <span style="width: 6px; height: 6px; background-color: var(--accent-cyan); border-radius: 50%; animation: pulse-glow 1s infinite alternate; animation-delay: 0.2s;"></span>
                <span style="width: 6px; height: 6px; background-color: var(--accent-cyan); border-radius: 50%; animation: pulse-glow 1s infinite alternate; animation-delay: 0.4s;"></span>
            </span>
        </div>
    `;
    chatBox.appendChild(messageContainer);
    chatBox.scrollTop = chatBox.scrollHeight;
    return id;
}

// Remove Loading indicator
function removeLoadingIndicator(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

// Clear Chat History
clearChatBtn.onclick = () => {
    if (!confirm("Clear this conversation history?")) return;
    chatHistory = [];
    chatBox.innerHTML = `
        <div class="message assistant">
            <div class="message-bubble">
                Conversation history cleared. Feel free to ask a new question!
            </div>
            <div class="message-meta">Agent • Just now</div>
        </div>
    `;
    showToast("Conversation cleared", "info");
};

// Initial Setup on load
window.onload = () => {
    fetchDocuments();
};
