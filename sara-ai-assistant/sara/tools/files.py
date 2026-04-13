"""
SARA File Tools - Basic Version
"""
import os

def register(mcp):
    """Register file tools"""
    
    @mcp.tool()
    def list_files(directory: str = "."):
        """List files in directory"""
        try:
            files = os.listdir(directory)
            return {
                'directory': directory,
                'files': files[:10],  # First 10 files
                'total': len(files)
            }
        except Exception as e:
            return {'error': str(e)}