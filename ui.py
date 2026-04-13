"""
SARA Web UI - Render.com Ready (SocketIO Fixed)
Created by Nikhil Badal
"""

import os
import sys
import json
import asyncio
import threading
import time
from datetime import datetime

# Flask imports
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

# Safe SocketIO import with fallback
try:
    from flask_socketio import SocketIO, emit
    SOCKETIO_AVAILABLE = True
    print("✅ SocketIO available")
except ImportError:
    SOCKETIO_AVAILABLE = False
    print("⚠️ SocketIO not available - using basic Flask")

# Safe imports with fallbacks
def safe_import(module_name, fallback_name=None):
    try:
        return __import__(module_name)
    except ImportError:
        print(f"⚠️ {module_name} not available - using fallback")
        return None

# Production environment detection
IS_PRODUCTION = os.getenv('FLASK_ENV') == 'production' or os.getenv('RENDER') == 'true'

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'sara_secret_key_by_nikhil_badal_render')

# CORS setup
CORS(app, origins=["*"])

# SocketIO setup with error handling
socketio = None
if SOCKETIO_AVAILABLE:
    try:
        if IS_PRODUCTION:
            # Production configuration - simple threading mode
            socketio = SocketIO(app, 
                              cors_allowed_origins="*", 
                              async_mode='threading',
                              logger=False, 
                              engineio_logger=False)
        else:
            # Development configuration
            socketio = SocketIO(app, cors_allowed_origins="*")
        print("✅ SocketIO initialized successfully")
    except Exception as e:
        print(f"⚠️ SocketIO initialization failed: {e}")
        SOCKETIO_AVAILABLE = False
        socketio = None

# AI Model setup
genai = safe_import('google.generativeai')
if genai and os.getenv('GOOGLE_API_KEY'):
    genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
    ai_model = genai.GenerativeModel('gemini-pro')
    print("✅ Google AI configured")
else:
    ai_model = None
    print("⚠️ Google AI not configured")

# Optional imports
wikipedia = safe_import('wikipedia')
requests = safe_import('requests')

class SARAInterface:
    def __init__(self):
        self.is_listening = False
        self.system_stats_enabled = not IS_PRODUCTION
        
    async def process_command(self, command):
        """Process user command with AI"""
        try:
            if ai_model:
                # Enhanced prompt for SARA
                system_prompt = f"""You are SARA (Smart Autonomous Responsive Assistant), created by Nikhil Badal.

You are a highly advanced AI assistant with the following capabilities:
- Answer questions intelligently and accurately
- Provide helpful information on various topics
- Assist with various tasks and problems
- Search for information when needed
- Be friendly, professional, and efficient

Current user message: {command}

Respond as SARA in a helpful, intelligent manner. Keep responses concise but informative.
Always be ready to assist and provide value to the user.
"""
                
                response = ai_model.generate_content(system_prompt)
                return response.text
            else:
                # Enhanced fallback responses
                command_lower = command.lower()
                
                if any(word in command_lower for word in ['hello', 'hi', 'hey']):
                    return 'Hello! I am SARA, your Smart Autonomous Responsive Assistant created by Nikhil Badal. How can I help you today?'
                
                elif any(word in command_lower for word in ['time', 'date']):
                    return f'Current date and time: {datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")}'
                
                elif any(word in command_lower for word in ['who are you', 'what are you']):
                    return 'I am SARA (Smart Autonomous Responsive Assistant), created by Nikhil Badal. I am an advanced AI assistant designed to help you with various tasks and answer your questions.'
                
                elif any(word in command_lower for word in ['help', 'what can you do']):
                    return 'I can help you with: answering questions, providing information, solving problems, general assistance, and much more. Just ask me anything you need help with!'
                
                elif 'creator' in command_lower or 'made' in command_lower or 'developer' in command_lower:
                    return 'I was created by Nikhil Badal, a skilled developer who built me to be your intelligent assistant.'
                
                elif 'joke' in command_lower:
                    jokes = [
                        "Why don't scientists trust atoms? Because they make up everything!",
                        "Why did the AI go to therapy? It had too many neural networks!",
                        "What do you call a robot that takes the long way around? R2-Detour!"
                    ]
                    import random
                    return random.choice(jokes)
                
                else:
                    return f"I understand you said: '{command}'. I'm SARA, created by Nikhil Badal. While my full AI capabilities aren't available right now, I'm still here to help! Please ask me specific questions about time, my creator, or request help."
                
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}. Please try again or ask me something else."
    
    def get_system_info(self):
        """Get basic system information"""
        try:
            if self.system_stats_enabled:
                import platform
                return {
                    'system': platform.system(),
                    'python_version': platform.python_version(),
                    'time': datetime.now().strftime('%H:%M:%S'),
                    'status': 'Active'
                }
            else:
                return {
                    'system': 'Render Production Server',
                    'python_version': f"{sys.version_info.major}.{sys.version_info.minor}",
                    'time': datetime.now().strftime('%H:%M:%S'),
                    'status': 'Active'
                }
        except Exception:
            return {
                'time': datetime.now().strftime('%H:%M:%S'),
                'status': 'Active'
            }

# Initialize SARA
sara_interface = SARAInterface()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        command = data.get('message', '')
        
        if not command:
            return jsonify({'error': 'No message provided'})
        
        # Process command
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        response = loop.run_until_complete(sara_interface.process_command(command))
        
        return jsonify({'response': response})
        
    except Exception as e:
        return jsonify({'response': f'I encountered an error: {str(e)}. Please try again.'})

@app.route('/api/system_stats')
def system_stats():
    try:
        stats = sara_interface.get_system_info()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e), 'time': datetime.now().strftime('%H:%M:%S')})

@app.route('/health')
def health():
    """Health check endpoint for Render"""
    return jsonify({
        'status': 'healthy',
        'service': 'SARA',
        'developer': 'Nikhil Badal',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'socketio_available': SOCKETIO_AVAILABLE
    })

# SocketIO Events (only if available)
if SOCKETIO_AVAILABLE and socketio:
    @socketio.on('connect')
    def handle_connect():
        print('Client connected')
        emit('status', {'message': 'Connected to SARA'})

    @socketio.on('disconnect') 
    def handle_disconnect():
        print('Client disconnected')

    @socketio.on('send_message')
    def handle_message(data):
        try:
            command = data.get('message', '')
            
            # Process command
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
            response = loop.run_until_complete(sara_interface.process_command(command))
            emit('sara_response', {'text': response})
            
        except Exception as e:
            emit('error', {'message': f'Error: {str(e)}'})

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Page not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

def main():
    """Main function to run SARA"""
    print("🤖 Starting SARA - Smart Autonomous Responsive Assistant")
    print("👨‍💻 Created by Nikhil Badal")
    
    if IS_PRODUCTION:
        print("🌐 Running in Production Mode (Render.com)")
    else:
        print("🛠️ Running in Development Mode")
    
    print(f"📡 SocketIO Status: {'Available' if SOCKETIO_AVAILABLE else 'Disabled (Using basic Flask)'}")
    
    # Port configuration for Render
    port = int(os.environ.get('PORT', 5000))
    host = '0.0.0.0' if IS_PRODUCTION else '127.0.0.1'
    
    print(f"🌐 SARA Web Interface starting on {host}:{port}")
    
    # Run with appropriate configuration
    if SOCKETIO_AVAILABLE and socketio:
        socketio.run(app, host=host, port=port, debug=not IS_PRODUCTION)
    else:
        # Fallback to basic Flask
        app.run(host=host, port=port, debug=not IS_PRODUCTION)

if __name__ == '__main__':
    main()
