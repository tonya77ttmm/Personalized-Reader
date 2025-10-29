#!/usr/bin/env python3
"""
Development server runner for AI Reader Agent backend.
This script activates the virtual environment and runs the FastAPI server.
"""

import subprocess
import sys
import os

def main():
    # Change to backend directory
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(backend_dir)
    
    # Check if virtual environment exists
    venv_path = os.path.join(backend_dir, 'venv')
    if not os.path.exists(venv_path):
        print("❌ Virtual environment not found. Please run: python3 -m venv venv")
        sys.exit(1)
    
    # Run the FastAPI server with uvicorn
    try:
        print("🚀 Starting AI Reader Agent backend server...")
        print("📍 Server will be available at: http://localhost:8000")
        print("📖 API docs will be available at: http://localhost:8000/docs")
        print("🔄 Press Ctrl+C to stop the server")
        print("-" * 50)
        
        subprocess.run([
            os.path.join(venv_path, 'bin', 'python'),
            '-m', 'uvicorn',
            'main:app',
            '--reload',
            '--host', '0.0.0.0',
            '--port', '8000'
        ])
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()