#!/usr/bin/env python3
"""
Mail Agent System - Main Entry Point
Central launcher for the 4-Agent Mail System
"""

import os
import sys
import argparse
import subprocess
import logging
import time
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MailAgentLauncher:
    """Main launcher for the Mail Agent System"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.backend_dir = self.base_dir / "backend"
        self.frontend_dir = self.base_dir / "frontend"
        
    def check_dependencies(self):
        """Check if required dependencies are installed"""
        try:
            import fastapi
            import uvicorn
            import streamlit
            logger.info("✅ All dependencies are installed")
            return True
        except ImportError as e:
            logger.error(f"❌ Missing dependency: {e}")
            logger.info("📦 Please install dependencies: pip install -r requirements.txt")
            return False
    
    def start_backend(self, port=8000):
        """Start the FastAPI backend server"""
        logger.info("🚀 Starting Backend Server...")
        
        # Change to backend directory
        backend_app = self.backend_dir / "app.py"
        if not backend_app.exists():
            logger.error("❌ Backend app.py not found!")
            return None
            
        try:
            cmd = [
                sys.executable, "-m", "uvicorn", 
                "app:app", 
                "--host", "0.0.0.0", 
                "--port", str(port),
                "--reload"
            ]
            
            process = subprocess.Popen(
                cmd,
                cwd=str(self.backend_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            logger.info(f"📡 Backend started on http://localhost:{port}")
            return process
            
        except Exception as e:
            logger.error(f"❌ Failed to start backend: {e}")
            return None
    
    def start_frontend(self, port=8501):
        """Start the Streamlit frontend"""
        logger.info("🖥️ Starting Frontend Server...")
        
        frontend_app = self.frontend_dir / "app.py"
        if not frontend_app.exists():
            logger.error("❌ Frontend app.py not found!")
            return None
            
        try:
            cmd = [
                sys.executable, "-m", "streamlit", "run", 
                str(frontend_app),
                "--server.port", str(port),
                "--server.address", "0.0.0.0"
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            logger.info(f"🎨 Frontend started on http://localhost:{port}")
            return process
            
        except Exception as e:
            logger.error(f"❌ Failed to start frontend: {e}")
            return None
    
    def install_dependencies(self):
        """Install required dependencies"""
        logger.info("📦 Installing dependencies...")
        requirements_file = self.base_dir / "requirements.txt"
        
        if not requirements_file.exists():
            logger.error("❌ requirements.txt not found!")
            return False
            
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ], check=True)
            logger.info("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to install dependencies: {e}")
            return False
    
    def run_full_system(self, backend_port=8000, frontend_port=8501):
        """Run both backend and frontend"""
        if not self.check_dependencies():
            return
            
        logger.info("🚀 Starting Mail Agent System - 4-Agent Architecture")
        logger.info("=" * 60)
        
        # Start backend
        backend_process = self.start_backend(backend_port)
        if not backend_process:
            return
            
        # Wait a moment for backend to start
        time.sleep(3)
        
        # Start frontend
        frontend_process = self.start_frontend(frontend_port)
        if not frontend_process:
            backend_process.terminate()
            return
        
        logger.info("=" * 60)
        logger.info("🎉 Mail Agent System is running!")
        logger.info(f"📡 Backend API: http://localhost:{backend_port}")
        logger.info(f"🎨 Frontend UI: http://localhost:{frontend_port}")
        logger.info(f"📖 API Docs: http://localhost:{backend_port}/docs")
        logger.info("=" * 60)
        logger.info("Press Ctrl+C to stop all services")
        
        try:
            # Wait for processes
            while True:
                if backend_process.poll() is not None:
                    logger.error("❌ Backend process stopped")
                    break
                if frontend_process.poll() is not None:
                    logger.error("❌ Frontend process stopped")
                    break
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("🛑 Shutting down...")
            
        finally:
            # Clean shutdown
            if backend_process and backend_process.poll() is None:
                backend_process.terminate()
                logger.info("🔴 Backend stopped")
                
            if frontend_process and frontend_process.poll() is None:
                frontend_process.terminate()
                logger.info("🔴 Frontend stopped")
                
            logger.info("👋 Mail Agent System stopped")

def main():
    """Main entry point with command line arguments"""
    parser = argparse.ArgumentParser(description="Mail Agent System - 4-Agent Architecture")
    parser.add_argument("--backend-only", action="store_true", help="Start only backend server")
    parser.add_argument("--frontend-only", action="store_true", help="Start only frontend")
    parser.add_argument("--install", action="store_true", help="Install dependencies only")
    parser.add_argument("--backend-port", type=int, default=8000, help="Backend port (default: 8000)")
    parser.add_argument("--frontend-port", type=int, default=8501, help="Frontend port (default: 8501)")
    
    args = parser.parse_args()
    launcher = MailAgentLauncher()
    
    if args.install:
        launcher.install_dependencies()
        return
        
    if args.backend_only:
        if launcher.check_dependencies():
            process = launcher.start_backend(args.backend_port)
            if process:
                try:
                    process.wait()
                except KeyboardInterrupt:
                    process.terminate()
                    logger.info("🔴 Backend stopped")
        return
        
    if args.frontend_only:
        if launcher.check_dependencies():
            process = launcher.start_frontend(args.frontend_port)
            if process:
                try:
                    process.wait()
                except KeyboardInterrupt:
                    process.terminate()
                    logger.info("🔴 Frontend stopped")
        return
    
    # Default: run full system
    launcher.run_full_system(args.backend_port, args.frontend_port)

if __name__ == "__main__":
    main()