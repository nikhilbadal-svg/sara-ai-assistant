"""
SARA System Tools - Basic Version
"""
import platform
import os

def register(mcp):
    """Register system tools"""
    
    @mcp.tool()
    def get_system_info():
        """Get system information"""
        try:
            return {
                'system': platform.system(),
                'platform': platform.platform(), 
                'processor': platform.processor(),
                'python_version': platform.python_version()
            }
        except Exception as e:
            return {'error': str(e)}
    
    @mcp.tool()
    def open_application(app_name: str):
        """Open an application"""
        try:
            if platform.system() == "Windows":
                os.system(f"start {app_name}")
            return {'status': f"Opened {app_name}"}
        except Exception as e:
            return {'error': str(e)}