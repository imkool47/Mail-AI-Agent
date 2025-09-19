"""
Mail Agent System Launcher - Simplified Version
Run backend and frontend in separate terminals for better control
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MailAgentLauncher:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"
        
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
    
    def start_backend_only(self, port=8000):
        """Start only the backend server"""
        if not self.check_dependencies():
            return
            
        logger.info("🚀 Starting Backend Server...")
        backend_app = self.backend_dir / "app.py"
        if not backend_app.exists():
            logger.error("❌ Backend app.py not found!")
            return
            
        # Change to backend directory and run uvicorn
        os.chdir(str(self.backend_dir))
        cmd = f'python -m uvicorn app:app --host localhost --port {port} --reload'
        logger.info(f"📡 Backend starting on http://localhost:{port}")
        logger.info(f"📖 API Docs: http://localhost:{port}/docs")
        logger.info(f"🔧 Running: {cmd}")
        os.system(cmd)
    
    def start_frontend_only(self, port=8501):
        """Start only the frontend"""
        if not self.check_dependencies():
            return
            
        logger.info("🖥️ Starting Frontend Server...")
        frontend_app = self.frontend_dir / "app.py"
        if not frontend_app.exists():
            logger.error("❌ Frontend app.py not found!")
            return
            
        # Change to frontend directory and run streamlit
        os.chdir(str(self.frontend_dir))
        cmd = f'python -m streamlit run app.py --server.port {port} --server.address localhost'
        logger.info(f"🎨 Frontend starting on http://localhost:{port}")
        logger.info(f"🔧 Running: {cmd}")
        os.system(cmd)
    
    def show_usage(self):
        """Show usage instructions"""
        logger.info("=" * 60)
        logger.info("🚀 Mail Agent System - 4-Agent Architecture")
        logger.info("=" * 60)
        logger.info("📋 Usage Instructions:")
        logger.info("")
        logger.info("1. Start Backend (Terminal 1):")
        logger.info("   python main.py --backend-only")
        logger.info("   or: cd backend && python -m uvicorn app:app --host localhost --port 8000 --reload")
        logger.info("")
        logger.info("2. Start Frontend (Terminal 2):")
        logger.info("   python main.py --frontend-only") 
        logger.info("   or: cd frontend && python -m streamlit run app.py --server.port 8501 --server.address localhost")
        logger.info("")
        logger.info("🌐 Access Points:")
        logger.info("   📡 Backend API: http://localhost:8000")
        logger.info("   🎨 Frontend UI: http://localhost:8501")
        logger.info("   📖 API Docs: http://localhost:8000/docs")
        logger.info("=" * 60)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Mail Agent System - Simple Launcher")
    parser.add_argument("--backend-only", action="store_true", help="Start only backend server")
    parser.add_argument("--frontend-only", action="store_true", help="Start only frontend")
    parser.add_argument("--backend-port", type=int, default=8000, help="Backend port (default: 8000)")
    parser.add_argument("--frontend-port", type=int, default=8501, help="Frontend port (default: 8501)")
    
    args = parser.parse_args()
    launcher = MailAgentLauncher()
    
    if args.backend_only:
        launcher.start_backend_only(args.backend_port)
    elif args.frontend_only:
        launcher.start_frontend_only(args.frontend_port)
    else:
        launcher.show_usage()

if __name__ == "__main__":
    main()