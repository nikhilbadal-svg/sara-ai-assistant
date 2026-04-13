"""
SARA Web UI - Render.com Ready
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
from flask_socketio import SocketIO, emit
from flask_cors import CORS

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

# SocketIO setup with production config
if IS_PRODUCTION:
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')
else:
    socketio = SocketIO(app, cors_allowed_origins="*")

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
- Answer questions intelligently
- Provide helpful information
- Assist with various tasks
- Search for information when needed
- Be friendly and professional

Current user message: {command}

Respond as SARA in a helpful, intelligent manner. Keep responses concise but informative.
"""
                
                response = ai_model.generate_content(system_prompt)
                return response.text
            else:
                # Fallback responses
                fallback_responses = {
                    'hello': 'Hello! I am SARA, your Smart Autonomous Responsive Assistant created by Nikhil Badal. How can I help you?',
                    'time': f'Current time is {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
                    'who are you': 'I am SARA (Smart Autonomous Responsive Assistant), created by Nikhil Badal. I am here to help you with various tasks.',
                    'help': 'I can help you with: answering questions, providing information, web searches, and general assistance. Just ask me anything!'
                }
                
                command_lower = command.lower()
                for key, response in fallback_responses.items():
                    if key in command_lower:
                        return response
                
                return f"I heard you say: '{command}'. I'm SARA, created by Nikhil Badal. How can I assist you further?"
                
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}. Please try again."
    
    def get_system_info(self):
        """Get basic system information"""
        try:
            if self.system_stats_enabled:
                import platform
                return {
                    'system': platform.system(),
                    'python_version': platform.python_version(),
                    'time': datetime.now().strftime('%H:%M:%S')
                }
            else:
                return {
                    'system': 'Production Server',
                    'python_version': f"{sys.version_info.major}.{sys.version_info.minor}",
                    'time': datetime.now().strftime('%H:%M:%S')
                }
        except Exception:
            return {'time': datetime.now().strftime('%H:%M:%S')}

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
        
        # Process command asynchronously
        loop = None
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        response = loop.run_until_complete(sara_interface.process_command(command))
        
        return jsonify({'response': response})
        
    except Exception as e:
        return jsonify({'error': f'Processing failed: {str(e)}'})

@app.route('/api/system_stats')
def system_stats():
    try:
        stats = sara_interface.get_system_info()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/health')
def health():
    """Health check endpoint for Render"""
    return jsonify({
        'status': 'healthy',
        'service': 'SARA',
        'developer': 'Nikhil Badal',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })

# SocketIO Events
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
        loop = None
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        response = loop.run_until_complete(sara_interface.process_command(command))
        emit('sara_response', {'text': response})
        
    except Exception as e:
        emit('error', {'message': f'Error: {str(e)}'})

@socketio.on('request_system_stats')
def handle_system_stats():
    try:
        stats = sara_interface.get_system_info()
        emit('system_stats', stats)
    except Exception as e:
        emit('error', {'message': f'Stats error: {str(e)}'})

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
    
    # Port configuration for Render
    port = int(os.environ.get('PORT', 5000))
    host = '0.0.0.0' if IS_PRODUCTION else '127.0.0.1'
    
    print(f"🌐 SARA Web Interface starting on {host}:{port}")
    
    # Run with appropriate configuration
    if IS_PRODUCTION:
        socketio.run(app, host=host, port=port, debug=False)
    else:
        socketio.run(app, host=host, port=port, debug=True)

if __name__ == '__main__':
    main()
