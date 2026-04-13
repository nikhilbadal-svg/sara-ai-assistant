"""
SARA Configuration - Basic Version
"""
import os
from dotenv import load_dotenv

def load_config():
    """Load SARA configuration"""
    load_dotenv()
    
    return {
        'name': 'SARA',
        'developer': 'Nikhil Badal', 
        'google_api_key': os.getenv('GOOGLE_API_KEY'),
        'openai_api_key': os.getenv('OPENAI_API_KEY'),
        'voice_enabled': True
    }