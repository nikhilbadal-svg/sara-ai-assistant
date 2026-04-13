// SARA Interface JavaScript
// Created by Nikhil Badal

class SARAInterface {
    constructor() {
        this.socket = io();
        this.isListening = false;
        this.isConnected = false;
        
        this.initializeElements();
        this.bindEvents();
        this.connectSocket();
        this.updateTime();
        this.updateSystemStats();
        
        // Update time every second
        setInterval(() => this.updateTime(), 1000);
        
        // Update system stats every 5 seconds
        setInterval(() => this.updateSystemStats(), 5000);
    }
    
    initializeElements() {
        this.userInput = document.getElementById('user-input');
        this.sendBtn = document.getElementById('send-btn');
        this.voiceBtn = document.getElementById('voice-btn');
        this.voiceBtnText = document.getElementById('voice-btn-text');
        this.chatMessages = document.getElementById('chat-messages');
        this.statusIndicator = document.getElementById('status');
        this.audioVisualizer = document.getElementById('audio-visualizer');
        this.cpuUsage = document.getElementById('cpu-usage');
        this.ramUsage = document.getElementById('ram-usage');
        this.currentTime = document.getElementById('current-time');
    }
    
    bindEvents() {
        // Send message on Enter key
        this.userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });
        
        // Send button click
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        
        // Voice button click
        this.voiceBtn.addEventListener('click', () => this.toggleVoiceRecording());
        
        // Auto-focus on input
        this.userInput.focus();
    }
    
    connectSocket() {
        this.socket.on('connect', () => {
            console.log('Connected to SARA server');
            this.isConnected = true;
            this.updateStatus('Connected', 'success');
        });
        
        this.socket.on('disconnect', () => {
            console.log('Disconnected from SARA server');
            this.isConnected = false;
            this.updateStatus('Disconnected', 'error');
        });
        
        this.socket.on('sara_response', (data) => {
            this.addMessage(data.text, 'sara');
            this.speak(data.text);
        });
        
        this.socket.on('voice_input', (data) => {
            this.addMessage(data.text, 'user');
        });
        
        this.socket.on('listening_status', (data) => {
            if (data.status === 'started') {
                this.isListening = true;
                this.voiceBtn.classList.add('active');
                this.voiceBtnText.textContent = '🔴 Stop Voice';
                this.audioVisualizer.classList.add('active');
                this.updateStatus('Listening', 'listening');
            } else if (data.status === 'stopped') {
                this.isListening = false;
                this.voiceBtn.classList.remove('active');
                this.voiceBtnText.textContent = '🎤 Start Voice';
                this.audioVisualizer.classList.remove('active');
                this.updateStatus('Ready', 'success');
            }
        });
        
        this.socket.on('error', (data) => {
            this.addMessage(`Error: ${data.message}`, 'sara', 'error');
        });
    }
    
    sendMessage() {
        const message = this.userInput.value.trim();
        if (!message) return;
        
        // Add user message to chat
        this.addMessage(message, 'user');
        
        // Show typing indicator
        this.showTypingIndicator();
        
        // Send to server
        this.socket.emit('send_message', { message: message });
        
        // Clear input
        this.userInput.value = '';
        this.userInput.focus();
    }
    
    toggleVoiceRecording() {
        if (this.isListening) {
            this.socket.emit('stop_listening');
        } else {
            this.socket.emit('start_listening');
        }
    }
    
    addMessage(text, sender, type = 'normal') {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${sender}-message`);
        
        if (type === 'error') {
            messageDiv.classList.add('error-message');
        } else if (type === 'success') {
            messageDiv.classList.add('success-message');
        }
        
        const now = new Date();
        const timeString = now.toLocaleTimeString();
        
        messageDiv.innerHTML = `
            <div class="message-content">
                <strong>${sender.toUpperCase()}:</strong> ${this.formatMessage(text)}
            </div>
            <div class="message-time">${timeString}</div>
        `;
        
        this.chatMessages.appendChild(messageDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        
        // Remove typing indicator if exists
        this.hideTypingIndicator();
    }
    
    formatMessage(text) {
        // Convert URLs to links
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        text = text.replace(urlRegex, '<a href="$1" target="_blank" style="color: #00ccff;">$1</a>');
        
        // Convert **text** to bold
        text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Convert *text* to italic
        text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
        
        return text;
    }
    
    showTypingIndicator() {
        this.hideTypingIndicator(); // Remove existing indicator
        
        const typingDiv = document.createElement('div');
        typingDiv.classList.add('message', 'sara-message', 'typing-message');
        typingDiv.innerHTML = `
            <div class="message-content">
                <strong>SARA:</strong> 
                <span class="typing-indicator">
                    <span class="dot"></span>
                    <span class="dot"></span>
                    <span class="dot"></span>
                    <span style="margin-left: 10px;">Thinking...</span>
                </span>
            </div>
        `;
        
        this.chatMessages.appendChild(typingDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    hideTypingIndicator() {
        const typingMessage = this.chatMessages.querySelector('.typing-message');
        if (typingMessage) {
            typingMessage.remove();
        }
    }
    
    updateStatus(text, type = 'normal') {
        const statusText = this.statusIndicator.querySelector('.status-text');
        statusText.textContent = text;
        
        // Remove existing classes
        this.statusIndicator.classList.remove('success', 'error', 'listening');
        
        // Add new class
        if (type !== 'normal') {
            this.statusIndicator.classList.add(type);
        }
    }
    
    updateTime() {
        const now = new Date();
        const timeString = now.toLocaleTimeString();
        if (this.currentTime) {
            this.currentTime.textContent = timeString;
        }
    }
    
    async updateSystemStats() {
        try {
            const response = await fetch('/api/system_stats');
            if (response.ok) {
                const stats = await response.json();
                
                if (this.cpuUsage) {
                    this.cpuUsage.textContent = `${stats.cpu || '--'}%`;
                }
                
                if (this.ramUsage) {
                    this.ramUsage.textContent = `${stats.memory || '--'}%`;
                }
            }
        } catch (error) {
            console.warn('Failed to update system stats:', error);
        }
    }
    
    speak(text) {
        // Use Web Speech API for text-to-speech
        if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 0.9;
            utterance.pitch = 1;
            utterance.volume = 0.8;
            
            // Try to use a female voice
            const voices = speechSynthesis.getVoices();
            const femaleVoice = voices.find(voice => 
                voice.name.includes('Female') || 
                voice.name.includes('Zira') ||
                voice.name.includes('Samantha')
            );
            
            if (femaleVoice) {
                utterance.voice = femaleVoice;
            }
            
            speechSynthesis.speak(utterance);
        }
    }
    
    playSound(type) {
        // Play UI sounds
        const audio = new Audio();
        switch (type) {
            case 'send':
                audio.src = '/static/audio/send.mp3';
                break;
            case 'receive':
                audio.src = '/static/audio/receive.mp3';
                break;
            case 'error':
                audio.src = '/static/audio/error.mp3';
                break;
            default:
                return;
        }
        
        audio.volume = 0.3;
        audio.play().catch(e => console.warn('Could not play sound:', e));
    }
}

// Quick action functions
function sendQuickCommand(command) {
    const sara = window.saraInterface;
    if (sara) {
        sara.userInput.value = command;
        sara.sendMessage();
    }
}

// Initialize SARA interface when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.saraInterface = new SARAInterface();
    
    // Show welcome message
    setTimeout(() => {
        window.saraInterface.addMessage(
            'Welcome to SARA! I am your Smart Autonomous Responsive Assistant, created by Nikhil Badal. I can help you with various tasks including web search, system control, file management, and much more. How can I assist you today?',
            'sara'
        );
    }, 1000);
});

// Add some global keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + / to focus input
    if ((e.ctrlKey || e.metaKey) && e.key === '/') {
        e.preventDefault();
        if (window.saraInterface) {
            window.saraInterface.userInput.focus();
        }
    }
    
    // Ctrl/Cmd + Shift + V to toggle voice
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'V') {
        e.preventDefault();
        if (window.saraInterface) {
            window.saraInterface.toggleVoiceRecording();
        }
    }
});