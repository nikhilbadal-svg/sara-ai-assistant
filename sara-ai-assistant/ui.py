"""
SARA Web UI - JARVIS-like Interface
Created by Nikhil Badal
"""

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import json
import asyncio
import aiohttp
import threading
import time
import speech_recognition as sr
import pyttsx3
from sara.config import load_config

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sara_secret_key_by_nikhil_badal'
socketio = SocketIO(app, cors_allowed_origins="*")

class SARAInterface:
    def __init__(self):
        self.config = load_config()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine = pyttsx3.init()
        self.setup_tts()
        self.is_listening = False
        
    def setup_tts(self):
        """Configure TTS engine"""
        voices = self.tts_engine.getProperty('voices')
        # Try to set a female voice
        for voice in voices:
            if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                self.tts_engine.setProperty('voice', voice.id)
                break
        
        self.tts_engine.setProperty('rate', 180)
        self.tts_engine.setProperty('volume', 0.8)
    
    def speak(self, text):
        """Text to speech"""
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
    
    async def process_command(self, command):
        """Process user command via SARA MCP server"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "http://127.0.0.1:8000/chat",
                    json={"message": command}
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("response", "I didn't understand that.")
        except Exception as e:
            return f"Sorry, I encountered an error: {e}"
    
    def listen_continuously(self):
        """Continuous voice recognition"""
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
        
        while self.is_listening:
            try:
                with self.microphone as source:
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                
                try:
                    command = self.recognizer.recognize_google(audio)
                    if command:
                        socketio.emit('voice_input', {'text': command})
                        
                        # Process command
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        response = loop.run_until_complete(self.process_command(command))
                        loop.close()
                        
                        socketio.emit('sara_response', {'text': response})
                        
                        # Speak response
                        threading.Thread(target=self.speak, args=(response,)).start()
                        
                except sr.UnknownValueError:
                    pass
                except sr.RequestError as e:
                    socketio.emit('error', {'message': f"Recognition error: {e}"})
                    
            except sr.WaitTimeoutError:
                pass
            except Exception as e:
                socketio.emit('error', {'message': f"Listening error: {e}"})

sara_interface = SARAInterface()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    command = data.get('message', '')
    
    # Process command asynchronously
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    response = loop.run_until_complete(sara_interface.process_command(command))
    loop.close()
    
    return jsonify({'response': response})

@socketio.on('start_listening')
def start_listening():
    """Start voice recognition"""
    if not sara_interface.is_listening:
        sara_interface.is_listening = True
        thread = threading.Thread(target=sara_interface.listen_continuously)
        thread.daemon = True
        thread.start()
        emit('listening_status', {'status': 'started'})

@socketio.on('stop_listening')
def stop_listening():
    """Stop voice recognition"""
    sara_interface.is_listening = False
    emit('listening_status', {'status': 'stopped'})

@socketio.on('send_message')
def handle_message(data):
    """Handle text message"""
    command = data.get('message', '')
    
    # Process command
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    response = loop.run_until_complete(sara_interface.process_command(command))
    loop.close()
    
    emit('sara_response', {'text': response})

def main():
    print("🤖 Starting SARA Web Interface")
    print("👨‍💻 Created by Nikhil Badal")
    print("🌐 Access SARA at: http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    main()