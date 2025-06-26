"""
Main entry point for CodeGenie system.
This file initializes the agent hierarchy and starts the interactive server.
"""

import asyncio
import uvicorn
from server import app

def main():
    """Main entry point for the CodeGenie system."""
    print("🚀 Starting CodeGenie - Automated Software Development System")
    print("📋 Initializing agent hierarchy...")
    print("🌐 Starting web server on http://127.0.0.1:8000")
    
    # Start the FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()