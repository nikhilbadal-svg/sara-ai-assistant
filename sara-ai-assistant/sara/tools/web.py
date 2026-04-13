"""
SARA Web Tools - Basic Version
"""
import requests

def register(mcp):
    """Register web tools"""
    
    @mcp.tool()
    def search_web(query: str):
        """Search the web"""
        try:
            return {
                'query': query,
                'result': f"Web search for: {query}",
                'status': 'success'
            }
        except Exception as e:
            return {'error': str(e)}
    
    @mcp.tool()
    def get_time():
        """Get current time"""
        from datetime import datetime
        now = datetime.now()
        return {
            'time': now.strftime('%H:%M:%S'),
            'date': now.strftime('%Y-%m-%d'),
            'formatted': now.strftime('%A, %B %d, %Y at %H:%M:%S')
        }