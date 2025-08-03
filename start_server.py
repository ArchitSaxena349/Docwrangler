#!/usr/bin/env python3
"""
Startup script for LLM Document Wrangler
"""

import os
import subprocess
import sys
from dotenv import load_dotenv

def check_environment():
    """Check if environment is properly configured"""
    load_dotenv()
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        print("Please check your .env file and make sure it contains:")
        print("OPENAI_API_KEY=your_api_key_here")
        return False
    
    print("✅ Environment variables loaded successfully")
    return True

def start_server():
    """Start the FastAPI server"""
    if not check_environment():
        return
    
    print("🚀 Starting LLM Document Wrangler...")
    print("📖 API Documentation will be available at: http://localhost:8000/docs")
    print("🔍 Health check endpoint: http://localhost:8000/health")
    print("📋 Analyze endpoint: http://localhost:8000/analyze")
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    start_server()
