"""
SARA - Minimal Version for Render.com
Created by Nikhil Badal
"""

import os
from flask import Flask, render_template, request, jsonify
from datetime import datetime

# Create Flask app
app = Flask(__name__)

print("🤖 Starting SARA - Smart Autonomous Responsive Assistant")
print("👨‍💻 Created by Nikhil Badal")

# Basic AI response function
def get_sara_response(user_message):
    """Simple response function"""
    message_lower = user_message.lower()
    
    # Basic responses
    if any(word in message_lower for word in ['hello', 'hi', 'hey']):
        return 'Hello! I am SARA, your Smart Autonomous Responsive Assistant created by Nikhil Badal. How can I help you?'
    
    elif any(word in message_lower for word in ['time', 'date']):
        return f'Current time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
    
    elif any(word in message_lower for word in ['who are you', 'what are you']):
        return 'I am SARA (Smart Autonomous Responsive Assistant), created by Nikhil Badal. I am here to help you!'
    
    elif 'creator' in message_lower or 'made' in message_lower:
        return 'I was created by Nikhil Badal, a talented developer.'
    
    elif any(word in message_lower for word in ['help', 'what can you do']):
        return 'I can help you with answering questions, providing information, and general assistance. Just ask me anything!'
    
    elif 'joke' in message_lower:
        return "Why don't scientists trust atoms? Because they make up everything! 😄"
    
    else:
        return f'I heard you say: "{user_message}". I\'m SARA, created by Nikhil Badal. How can I assist you further?'

# Routes
@app.route('/')
def index():
    """Home page"""
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SARA - Smart Autonomous Responsive Assistant</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0c0c0c, #1a1a2e, #16213e);
            color: #00ff88;
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: rgba(0, 0, 0, 0.7);
            border: 1px solid #00ff88;
            border-radius: 15px;
            padding: 20px;
        }
        h1 {
            text-align: center;
            font-size: 3rem;
            background: linear-gradient(45deg, #00ff88, #00ccff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        .subtitle {
            text-align: center;
            color: #00ccff;
            margin-bottom: 30px;
        }
        .chat-container {
            height: 400px;
            overflow-y: auto;
            border: 1px solid #00ff88;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            background: rgba(0, 255, 136, 0.1);
        }
        .message {
            margin-bottom: 15px;
            padding: 10px;
            border-radius: 8px;
        }
        .user-message {
            background: rgba(0, 204, 255, 0.2);
            border-left: 3px solid #00ccff;
        }
        .sara-message {
            background: rgba(0, 255, 136, 0.2);
            border-left: 3px solid #00ff88;
        }
        .input-container {
            display: flex;
            gap: 10px;
        }
        input {
            flex: 1;
            padding: 12px;
            border: 1px solid #00ff88;
            border-radius: 25px;
            background: rgba(0, 255, 136, 0.1);
            color: #00ff88;
            outline: none;
        }
        button {
            padding: 12px 20px;
            background: linear-gradient(45deg, #00ff88, #00ccff);
            border: none;
            border-radius: 25px;
            color: #000;
            cursor: pointer;
            font-weight: bold;
        }
        button:hover {
            transform: translateY(-2px);
        }
        .quick-actions {
            margin-top: 20px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
        }
        .action-btn {
            background: rgba(0, 255, 136, 0.2);
            border: 1px solid #00ff88;
            color: #00ff88;
            padding: 8px;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>S.A.R.A.</h1>
        <p class="subtitle">Smart Autonomous Responsive Assistant - Created by Nikhil Badal</p>
        
        <div class="chat-container" id="chat-container">
            <div class="message sara-message">
                <strong>SARA:</strong> Hello! I am SARA, your Smart Autonomous Responsive Assistant created by Nikhil Badal. How can I assist you today?
            </div>
        </div>
        
        <div class="input-container">
            <input type="text" id="user-input" placeholder="Ask SARA anything..." onkeypress="if(event.key==='Enter') sendMessage()">
            <button onclick="sendMessage()">Send</button>
        </div>
        
        <div class="quick-actions">
            <button class="action-btn" onclick="quickMessage('Hello SARA')">Greet SARA</button>
            <button class="action-btn" onclick="quickMessage('What time is it?')">Current Time</button>
            <button class="action-btn" onclick="quickMessage('Who created you?')">About Creator</button>
            <button class="action-btn" onclick="quickMessage('Tell me a joke')">Tell Joke</button>
            <button class="action-btn" onclick="quickMessage('What can you do?')">Your Capabilities</button>
            <button class="action-btn" onclick="quickMessage('Help me')">Get Help</button>
        </div>
    </div>

    <script>
        function addMessage(text, sender) {
            const chatContainer = document.getElementById('chat-container');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message`;
            messageDiv.innerHTML = `<strong>${sender.toUpperCase()}:</strong> ${text}`;
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        async function sendMessage() {
            const input = document.getElementById('user-input');
            const message = input.value.trim();
            
            if (!message) return;
            
            addMessage(message, 'user');
            input.value = '';
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message })
                });
                
                const data = await response.json();
                addMessage(data.response || 'Sorry, I could not process that.', 'sara');
            } catch (error) {
                addMessage('Sorry, there was an error. Please try again.', 'sara');
            }
        }
        
        function quickMessage(message) {
            document.getElementById('user-input').value = message;
            sendMessage();
        }
        
        // Focus input on load
        document.getElementById('user-input').focus();
    </script>
</body>
</html>
    '''

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat API endpoint"""
    try:
        data = request.json
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'No message provided'})
        
        response = get_sara_response(user_message)
        return jsonify({'response': response})
        
    except Exception as e:
        return jsonify({'response': f'Error: {str(e)}'})

@app.route('/health')
def health():
    """Health check for Render"""
    return jsonify({
        'status': 'healthy',
        'service': 'SARA',
        'developer': 'Nikhil Badal',
        'timestamp': datetime.now().isoformat()
    })

# Main function
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🌐 SARA starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
