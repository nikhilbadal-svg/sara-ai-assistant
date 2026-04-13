"""
SARA Tools Registration
"""

def register_all_tools(mcp):
    """Register all SARA tools"""
    print("🔧 Registering SARA tools...")
    
    # Basic tools registration
    try:
        from .web import register as register_web
        register_web(mcp)
        print("✅ Web tools registered")
    except ImportError:
        print("⚠️ Web tools not available")
    
    try:
        from .system import register as register_system  
        register_system(mcp)
        print("✅ System tools registered")
    except ImportError:
        print("⚠️ System tools not available")
        
    try:
        from .applications import register as register_applications
        register_applications(mcp)
        print("✅ Application tools registered")
    except ImportError:
        print("⚠️ Application tools not available")
        
    try:
        from .files import register as register_files
        register_files(mcp)
        print("✅ File tools registered")
    except ImportError:
        print("⚠️ File tools not available")
        
    try:
        from .utils import register as register_utils
        register_utils(mcp)
        print("✅ Utility tools registered")
    except ImportError:
        print("⚠️ Utility tools not available")
    
    print("🎯 SARA tools registration completed!")