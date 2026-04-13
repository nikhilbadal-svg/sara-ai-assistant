"""
SARA Server - Basic Version  
Created by Nikhil Badal
"""
print("🤖 Starting SARA - Smart Autonomous Responsive Assistant")
print("👨‍💻 Created by Nikhil Badal")

try:
    # Try to import FastMCP
    from fastmcp import FastMCP
    print("✅ FastMCP imported")
    
    # Import SARA tools
    from sara.config import load_config
    from sara.tools import register_all_tools
    print("✅ SARA modules imported")
    
    # Create MCP server
    mcp = FastMCP("SARA Assistant")
    
    # Load config
    config = load_config()
    print(f"✅ Configuration loaded")
    
    # Register tools
    register_all_tools(mcp)
    
    # Server info
    @mcp.resource("sara://info")
    def get_sara_info():
        return {
            "name": "SARA",
            "developer": "Nikhil Badal",
            "version": "1.0.0",
            "status": "Running"
        }
    
    print("🌐 Starting SARA server on http://127.0.0.1:8000")
    mcp.run(transport="sse", port=8000)
    
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("📝 Running basic SARA without FastMCP...")
    
    # Basic Flask server as fallback
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return jsonify({
            'name': 'SARA',
            'developer': 'Nikhil Badal',
            'status': 'Basic mode running',
            'message': 'SARA is running in basic mode'
        })
    
    print("🌐 SARA basic server running on http://127.0.0.1:8000")
    app.run(host='127.0.0.1', port=8000)

except Exception as e:
    print(f"❌ Error starting server: {e}")
    print("💡 Try installing missing packages:")
    print("pip install fastmcp flask")