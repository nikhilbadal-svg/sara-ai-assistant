"""
SARA Utility Tools - Basic Version
"""

def register(mcp):
    """Register utility tools"""
    
    @mcp.tool()
    def word_count(text: str):
        """Count words in text"""
        try:
            words = len(text.split())
            chars = len(text)
            return {
                'text': text[:50] + "..." if len(text) > 50 else text,
                'words': words,
                'characters': chars
            }
        except Exception as e:
            return {'error': str(e)}