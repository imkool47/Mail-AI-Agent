"""
Main Application Entry Point
Simplified launcher for the Mail Agent system.
"""

import sys
import os
import subprocess
import argparse
import logging
import signal
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MailAgentLauncher:
    """Simplified launcher for the Mail Agent system"""
    
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.running = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info("Received shutdown signal. Stopping services...")
        self.stop_all()
        sys.exit(0)
    
    def validate_environment(self) -> bool:
        """Basic environment validation"""
        logger.info("Validating environment...")
        
        # Check if .env file exists
        env_file = project_root / ".env"
        if not env_file.exists():
            logger.error(".env file not found. Copy .env.example to .env and configure it.")
            return False
        
        logger.info("Environment validation completed")
        return True
    
    def install_dependencies(self):
        """Install Python dependencies"""
        logger.info("Installing dependencies...")
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ], check=True, cwd=project_root)
            logger.info("Dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install dependencies: {e}")
            return False
        return True
    
    def start_backend(self, host: str = "localhost", port: int = 8000):
        """Start the FastAPI backend"""
        logger.info(f"Starting backend server on {host}:{port}...")
        
        try:
            cmd = [
                sys.executable, "-m", "uvicorn",
                "backend.main:app",
                "--host", host,
                "--port", str(port),
                "--reload"
            ]
            
            self.backend_process = subprocess.Popen(
                cmd,
                cwd=project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            logger.info(f"Backend started with PID: {self.backend_process.pid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start backend: {e}")
            return False
    
    def start_frontend(self, port: int = 8501):
        """Start the Streamlit frontend"""
        logger.info(f"Starting frontend on port {port}...")
        
        try:
            cmd = [
                sys.executable, "-m", "streamlit", "run",
                "frontend/app.py",
                "--server.port", str(port),
                "--server.address", "localhost"
            ]
            
            self.frontend_process = subprocess.Popen(
                cmd,
                cwd=project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            logger.info(f"Frontend started with PID: {self.frontend_process.pid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start frontend: {e}")
            return False
    
    def stop_backend(self):
        """Stop the backend server"""
        if self.backend_process:
            logger.info("Stopping backend server...")
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
            self.backend_process = None
    
    def stop_frontend(self):
        """Stop the frontend server"""
        if self.frontend_process:
            logger.info("Stopping frontend server...")
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
            self.frontend_process = None
    
    def stop_all(self):
        """Stop all services"""
        self.stop_frontend()
        self.stop_backend()
        self.running = False
    
    def start_all(self, backend_port: int = 8000, frontend_port: int = 8501):
        """Start all services"""
        if not self.validate_environment():
            logger.error("Environment validation failed. Please fix the issues and try again.")
            return False
        
        # Start backend
        if not self.start_backend(port=backend_port):
            logger.error("Failed to start backend")
            return False
        
        # Give backend time to start
        import time
        time.sleep(3)
        
        # Start frontend
        if not self.start_frontend(port=frontend_port):
            logger.error("Failed to start frontend")
            self.stop_backend()
            return False
        
        self.running = True
        logger.info("Mail Agent system started successfully!")
        logger.info(f"Backend API: http://localhost:{backend_port}")
        logger.info(f"Frontend UI: http://localhost:{frontend_port}")
        
        return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Mail Agent - Intern Management System")
    parser.add_argument("--install", action="store_true", help="Install dependencies")
    parser.add_argument("--validate", action="store_true", help="Validate environment only")
    parser.add_argument("--backend-only", action="store_true", help="Start backend only")
    parser.add_argument("--frontend-only", action="store_true", help="Start frontend only")
    parser.add_argument("--backend-port", type=int, default=8000, help="Backend port")
    parser.add_argument("--frontend-port", type=int, default=8501, help="Frontend port")
    
    args = parser.parse_args()
    
    launcher = MailAgentLauncher()
    
    if args.install:
        success = launcher.install_dependencies()
        sys.exit(0 if success else 1)
    
    if args.validate:
        success = launcher.validate_environment()
        sys.exit(0 if success else 1)
    
    if args.backend_only:
        if launcher.validate_environment():
            launcher.start_backend(port=args.backend_port)
            try:
                # Keep running until interrupted
                while True:
                    import time
                    time.sleep(1)
            except KeyboardInterrupt:
                launcher.stop_backend()
        sys.exit(0)
    
    if args.frontend_only:
        launcher.start_frontend(port=args.frontend_port)
        try:
            # Keep running until interrupted
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            launcher.stop_frontend()
        sys.exit(0)
    
    # Default: start all services
    if launcher.start_all(backend_port=args.backend_port, frontend_port=args.frontend_port):
        try:
            # Keep running until interrupted
            while launcher.running:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            launcher.stop_all()
    else:
        logger.error("Failed to start the Mail Agent system")
        sys.exit(1)


if __name__ == "__main__":
    main()