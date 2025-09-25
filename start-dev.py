#!/usr/bin/env python3
"""
Development Server Starter Script
Starts both backend and frontend servers for the Kochi Metro Trainset Induction Planner
"""

import os
import subprocess
import sys
import time
from pathlib import Path

def print_header():
    print("=" * 60)
    print("🚀 Kochi Metro Trainset Induction Planner - Dev Starter")
    print("=" * 60)

def check_prerequisites():
    """Check if required tools are installed"""
    try:
        subprocess.run(["python", "--version"], capture_output=True, check=True)
        print("✅ Python is available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Python is not installed or not in PATH")
        return False
    
    try:
        subprocess.run(["npm", "--version"], capture_output=True, check=True)
        print("✅ Node.js/NPM is available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Node.js/NPM is not installed or not in PATH")
        return False
    
    return True

def start_backend():
    """Start the FastAPI backend server"""
    print("\n🔧 Starting Backend Server...")
    backend_dir = Path("backend")
    
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return None
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    # Start backend server
    backend_process = subprocess.Popen([
        "uvicorn", "main:app", 
        "--host", "0.0.0.0", 
        "--port", "8001",
        "--reload"
    ])
    
    os.chdir("..")  # Go back to root directory
    print("✅ Backend server started on http://localhost:8001")
    return backend_process

def start_frontend():
    """Start the React frontend server"""
    print("\n🌐 Starting Frontend Server...")
    frontend_dir = Path("frontend")
    
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return None
    
    # Change to frontend directory
    os.chdir(frontend_dir)
    
    # Start frontend server
    frontend_process = subprocess.Popen(["npm", "start"])
    
    os.chdir("..")  # Go back to root directory
    print("✅ Frontend server started on http://localhost:3000")
    return frontend_process

def main():
    print_header()
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n⚠️  Please install the required tools and try again.")
        sys.exit(1)
    
    # Check if we're in the right directory
    root_dir = Path(__file__).parent
    os.chdir(root_dir)
    
    if not (root_dir / "backend").exists() or not (root_dir / "frontend").exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    print(f"\n📂 Working directory: {root_dir}")
    
    # Start servers
    backend_process = start_backend()
    frontend_process = start_frontend()
    
    if not backend_process or not frontend_process:
        print("\n❌ Failed to start one or more servers")
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✨ Both servers are now running!")
    print("   Backend:  http://localhost:8001")
    print("   Frontend: http://localhost:3000")
    print("\n📝 Press Ctrl+C to stop both servers")
    print("=" * 60)
    
    try:
        # Wait for both processes
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down servers...")
        backend_process.terminate()
        frontend_process.terminate()
        backend_process.wait()
        frontend_process.wait()
        print("✅ Servers stopped. Goodbye!")
        sys.exit(0)

if __name__ == "__main__":
    main()