const chatContainer = document.getElementById('chatContainer');
const userInput = document.getElementById('userInput');
const loading = document.getElementById('loading');
const sendButton = document.getElementById('sendButton');
let uploadedFile = null; // لتخزين الملف المرفوع مؤقتًا

function loadChatHistory() {
    const history = localStorage.getItem('chatHistory');
    if (history) {
        const messages = JSON.parse(history);
        messages.forEach(msg => {
            appendMessage(msg.content, msg.type);
        });
    }
}

function saveMessage(content, type) {
    const history = localStorage.getItem('chatHistory');
    const messages = history ? JSON.parse(history) : [];
    messages.push({ content, type });
    localStorage.setItem('chatHistory', JSON.stringify(messages));
}

function clearChat() {
    if (confirm('Clear chat history?')) {
        chatContainer.innerHTML = '';
        localStorage.removeItem('chatHistory');
        showToast('Chat cleared', 'success');
    }
}

function showToast(message, type = 'error') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

function adjustTextareaHeight() {
    userInput.style.height = 'auto';
    const maxHeight = window.innerHeight * 0.2;
    userInput.style.height = Math.min(userInput.scrollHeight, maxHeight) + 'px';
}

async function sendMessage() {
    const message = userInput.value.trim();
    if (!message && !uploadedFile) return;

    userInput.disabled = true;
    sendButton.disabled = true;

    if (uploadedFile) {
        appendMessage(`تم رفع الملف: ${uploadedFile.name}`, 'user');
    }
    if (message) {
        appendMessage(message, 'user');
    }
    
    saveMessage(message, 'user');
    userInput.value = '';
    adjustTextareaHeight();
    loading.style.display = 'block';

    try {
        const formData = new FormData();
        if (uploadedFile) {
            formData.append('file', uploadedFile);
        }
        formData.append('message', message);

        const response = await fetch('/ask', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.error) {
            showToast(data.error, 'error');
            appendMessage('عذرًا، حدث خطأ. يرجى المحاولة مرة أخرى.', 'ai');
        } else {
            appendMessage(data.response, 'ai');
            saveMessage(data.response, 'ai');
        }
    } catch (error) {
        showToast('خطأ بالأتصال', 'error');
        appendMessage('عذرًا، حدث خطأ. يرجى المحاولة مرة أخرى.', 'ai');
    }

    userInput.disabled = false;
    sendButton.disabled = false;
    loading.style.display = 'none';
    userInput.focus();
    uploadedFile = null; // إعادة تعيين الملف بعد الإرسال
}

function appendMessage(message, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    messageDiv.innerHTML = marked.parse(message);
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;

    // Add copy button above each code block
    messageDiv.querySelectorAll('pre code').forEach((block) => {
        hljs.highlightBlock(block);

        const copyButton = document.createElement('button');
        copyButton.textContent = 'نسخ الكود';
        copyButton.className = 'copy-code-btn';
        copyButton.onclick = () => {
            const codeToCopy = block.innerText;
            navigator.clipboard.writeText(codeToCopy)
                .then(() => {
                    showToast('تم نسخ الكود بنجاح!', 'success');
                })
                .catch(() => {
                    showToast('فشل نسخ الكود', 'error');
                });
        };

        block.parentElement.insertBefore(copyButton, block);
    });
}

userInput.addEventListener('input', adjustTextareaHeight);

userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

loadChatHistory();
userInput.focus();

// Handle viewport height on mobile
function adjustViewportHeight() {
    document.documentElement.style.setProperty('--vh', `${window.innerHeight * 0.01}px`);
}

window.addEventListener('resize', adjustViewportHeight);
window.addEventListener('orientationchange', adjustViewportHeight);
adjustViewportHeight();

// File Upload
async function uploadFile() {
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = '*/*';
    fileInput.onchange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        uploadedFile = file; // تخزين الملف مؤقتًا
        appendMessage(`تم رفع الملف: ${file.name}`, 'user');
        showToast('تم رفع الملف بنجاح!', 'success');
    };
    fileInput.click();
}