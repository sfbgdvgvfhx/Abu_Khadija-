from flask import Flask, render_template_string, request, jsonify, send_from_directory
import requests
import os
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {
    'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
    'py', 'java', 'html', 'css', 'js', 'json', 'xml', 'csv', 'sql', 'c', 'cpp', 'php', 'rb', 'go', 'swift', 'kt', 'ts'
}

# إنشاء مجلد التحميل إذا لم يكن موجودًا
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>AI Assistant</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/marked/9.1.6/marked.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/highlight.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/styles/atom-one-dark.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap" rel="stylesheet">
    <style>
        /* CSS Reset and Variables */
        :root {
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --text-primary: #e2e8f0;
            --text-secondary: #94a3b8;
            --accent: #3b82f6;
            --accent-hover: #2563eb;
            --error: #ef4444;
            --success: #10b981;
            --warning: #f59e0b;
            --font-scale: 1vmin;
            --font-family: 'Tajawal', sans-serif;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
        }

        /* Responsive Font Size Calculation */
        @media (max-width: 480px) {
            :root { --font-scale: 0.9vmin; }
        }

        @media (min-width: 481px) and (max-width: 768px) {
            :root { --font-scale: 1vmin; }
        }

        @media (min-width: 769px) and (max-width: 1024px) {
            :root { --font-scale: 1.1vmin; }
        }

        @media (min-width: 1025px) {
            :root { --font-scale: 1.2vmin; }
        }

        /* Base Styles */
        html {
            font-size: calc(var(--font-scale) * 2.2);
        }

        body {
            font-family: var(--font-family);
            background-color: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            overflow-x: hidden;
            font-size: 1rem;
        }

        /* Container */
        .container {
            max-width: 100%;
            margin: 0 auto;
            padding: calc(var(--font-scale) * 2);
            flex-grow: 1;
            display: flex;
            flex-direction: column;
            height: 100vh;
        }

        /* Header */
        header {
            text-align: center;
            margin-bottom: calc(var(--font-scale) * 3);
            padding: calc(var(--font-scale) * 3);
            background-color: var(--bg-secondary);
            border-radius: calc(var(--font-scale) * 3);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }

        .app-title {
            font-size: calc(var(--font-scale) * 8);
            background: linear-gradient(45deg, var(--accent), #8b5cf6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: bold;
            margin-bottom: calc(var(--font-scale) * 2);
        }

        .app-subtitle {
            font-size: calc(var(--font-scale) * 4);
            color: var(--text-secondary);
        }

        /* Chat Container */
        .chat-container {
            flex-grow: 1;
            background-color: var(--bg-secondary);
            border-radius: calc(var(--font-scale) * 3);
            padding: calc(var(--font-scale) * 3);
            margin-bottom: calc(var(--font-scale) * 3);
            overflow-y: auto;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }

        /* Messages */
        .message {
            margin-bottom: calc(var(--font-scale) * 3);
            padding: calc(var(--font-scale) * 3);
            border-radius: calc(var(--font-scale) * 2);
            animation: fadeIn 0.3s ease-in;
            max-width: 85%;
            font-size: calc(var(--font-scale) * 4);
            word-wrap: break-word;
        }

        .user-message {
            background-color: var(--accent);
            margin-left: auto;
            color: white;
        }

        .ai-message {
            background-color: var(--bg-primary);
            margin-right: auto;
        }

        /* Input Area */
        .input-container {
            display: flex;
            flex-direction: column;
            gap: calc(var(--font-scale) * 2);
            padding: calc(var(--font-scale) * 3);
            background-color: var(--bg-secondary);
            border-radius: calc(var(--font-scale) * 3);
            box-shadow: 0 -4px 6px -1px rgba(0, 0, 0, 0.1);
        }

        .input-wrapper {
            position: relative;
            flex-grow: 1;
        }

        textarea {
            width: 100%;
            padding: calc(var(--font-scale) * 3);
            border: 2px solid var(--bg-primary);
            border-radius: calc(var(--font-scale) * 2);
            background-color: var(--bg-primary);
            color: var(--text-primary);
            resize: none;
            font-size: calc(var(--font-scale) * 4);
            min-height: calc(var(--font-scale) * 12);
            max-height: calc(var(--font-scale) * 30);
            line-height: 1.5;
        }

        textarea:focus {
            outline: none;
            border-color: var(--accent);
        }

        /* Buttons */
        .action-buttons {
            display: flex;
            gap: calc(var(--font-scale) * 2);
            justify-content: flex-end;
        }

        button {
            padding: calc(var(--font-scale) * 2);
            border: none;
            border-radius: calc(var(--font-scale) * 2);
            background-color: var(--accent);
            color: white;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: calc(var(--font-scale) * 3.5);
            display: flex;
            align-items: center;
            justify-content: center;
            min-width: calc(var(--font-scale) * 15);
        }

        button:disabled {
            background-color: var(--text-secondary);
            cursor: not-allowed;
        }

        .clear-btn {
            background-color: var(--error);
        }

        .upload-btn {
            background-color: var(--warning);
        }

        .copy-code-btn {
            background-color: var(--success);
            padding: calc(var(--font-scale) * 1.5);
            font-size: calc(var(--font-scale) * 3);
            min-width: calc(var(--font-scale) * 12);
            margin-bottom: 5px;
        }

        /* Loading Animation */
        .loading {
            display: none;
            padding: calc(var(--font-scale) * 3);
            text-align: center;
            background-color: var(--bg-primary);
            border-radius: calc(var(--font-scale) * 2);
            margin: calc(var(--font-scale) * 3) 0;
        }

        .loading-spinner {
            display: inline-block;
            width: calc(var(--font-scale) * 8);
            height: calc(var(--font-scale) * 8);
            border: calc(var(--font-scale) * 0.8) solid var(--text-secondary);
            border-top-color: var(--accent);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        /* Code Blocks */
        pre {
            background-color: #282c34;
            padding: calc(var(--font-scale) * 3);
            border-radius: calc(var(--font-scale) * 2);
            overflow-x: auto;
            margin: calc(var(--font-scale) * 3) 0;
            font-size: calc(var(--font-scale) * 3.5);
        }

        code {
            font-family: 'Fira Code', 'Courier New', monospace;
        }

        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        /* Scrollbar */
        ::-webkit-scrollbar {
            width: calc(var(--font-scale) * 2);
        }

        ::-webkit-scrollbar-track {
            background: var(--bg-primary);
        }

        ::-webkit-scrollbar-thumb {
            background: var(--accent);
            border-radius: calc(var(--font-scale) * 1);
        }

        /* Toast Notifications */
        .toast {
            position: fixed;
            top: calc(var(--font-scale) * 3);
            right: calc(var(--font-scale) * 3);
            padding: calc(var(--font-scale) * 3);
            border-radius: calc(var(--font-scale) * 2);
            color: white;
            font-size: calc(var(--font-scale) * 4);
            animation: slideIn 0.3s ease-out;
            z-index: 1000;
        }

        .toast-error {
            background-color: var(--error);
        }

        .toast-success {
            background-color: var(--success);
        }

        .toast-warning {
            background-color: var(--warning);
        }

        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="app-title">خادمك المطيع</div>
            <p class="app-subtitle">اسألني او اطلب اي شئ</p>
        </header>

        <div class="chat-container" id="chatContainer"></div>

        <div class="loading" id="loading">
            <div class="loading-spinner"></div>
        </div>

        <div class="input-container">
            <div class="input-wrapper">
                <textarea 
                    id="userInput" 
                    placeholder="اكتب هنا ما تريد..."
                    rows="1"
                ></textarea>
            </div>
            <div class="action-buttons">
                <button onclick="sendMessage()" id="sendButton">أرسال</button>
                <button onclick="clearChat()" class="clear-btn">مسح</button>
                <button onclick="uploadFile()" class="upload-btn">رفع ملف</button>
            </div>
        </div>
    </div>

    <script>
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
    </script>
</body>
</html>
'''

GEMINI_API_KEY = "AIzaSyDV1Hwzgo6HaUctAch0B6qzXZ8ujr14jIM"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/ask', methods=['POST'])
def ask_ai():
    message = request.form.get('message', '')
    file = request.files.get('file', None)
    
    if not message and not file:
        return jsonify({'error': 'Message or file is required'}), 400
    
    try:
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            with open(filepath, 'r') as f:
                content = f.read()
            payload = {
                "contents": [{
                    "parts": [{
                        "text": f"Process this file:\n{content}\n\nUser message: {message}"
                    }]
                }]
            }
        else:
            payload = {
                "contents": [{
                    "parts": [{
                        "text": message
                    }]
                }]
            }
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'candidates' in data:
                ai_reply = data['candidates'][0]['content']['parts'][0]['text']
                return jsonify({'response': ai_reply})
            return jsonify({'error': 'Invalid response format'}), 500
            
        elif response.status_code == 429:
            return jsonify({'error': 'Rate limit exceeded'}), 429
        else:
            return jsonify({'error': 'Service error'}), 500
        
    except requests.Timeout:
        return jsonify({'error': 'Request timed out'}), 504
    except requests.RequestException:
        return jsonify({'error': 'Network error'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
