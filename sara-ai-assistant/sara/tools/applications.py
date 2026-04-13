"""
SARA Applications Tools - Basic Version
"""

def register(mcp):
    """Register application tools"""
    
    @mcp.tool()
    def calculator():
        """Open calculator"""
        try:
            import os
            os.system("calc")
            return {'status': 'Calculator opened'}
        except Exception as e:
            return {'error': str(e)}
    
    @mcp.tool() 
    def notepad():
        """Open notepad"""
        try:
            import os
            os.system("notepad")
            return {'status': 'Notepad opened'}
        except Exception as e:
            return {'error': str(e)}