"""
FastAPI Backend - 4-Agent Architecture
Orchestrates AI Agent, Mail Agent, Database Agent, and Outlook Agent
"""

import logging
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import uvicorn
from datetime import datetime
import asyncio

# Import all 4 agents
from agents import ai_agent, mail_agent, database_agent, outlook_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Mail Agent System - 4-Agent Architecture",
    description="AI-powered mail system with specialized agents",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication state
auth_state = {
    "authenticated": False,
    "access_token": None,
    "user_info": None
}

# Pydantic models
class AIPromptRequest(BaseModel):
    prompt: str
    service: str = "openai"

class InternData(BaseModel):
    name: str
    personal_email: str
    department: str
    start_date: Optional[str] = None
    skills: Optional[List[str]] = []
    education: Optional[str] = None

class EmailRequest(BaseModel):
    recipient_email: str
    subject: str
    content: str
    email_type: str = "general"

class BulkEmailRequest(BaseModel):
    recipients: List[Dict]
    subject: str
    content_template: str
    email_type: str = "general"

# Dependency for authentication
async def verify_auth():
    """Verify user is authenticated"""
    if not auth_state["authenticated"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    return auth_state

# Root endpoint
@app.get("/")
async def root():
    """System status"""
    return {
        "system": "Mail Agent System",
        "version": "2.0.0",
        "architecture": "4-Agent System",
        "agents": {
            "ai_agent": "Generates content and orchestrates requests",
            "mail_agent": "Handles all email sending operations", 
            "database_agent": "Manages database access only",
            "outlook_agent": "Creates email accounts and manages credentials"
        },
        "status": "operational",
        "authenticated": auth_state["authenticated"]
    }

# ===== AI AGENT ENDPOINTS =====
@app.post("/ai/process", dependencies=[Depends(verify_auth)])
async def process_ai_prompt(request: AIPromptRequest):
    """
    Main AI endpoint: Process user prompt intelligently
    AI agent will determine if database access is needed and if emails should be sent
    """
    try:
        result = await ai_agent.process_prompt(request.prompt, request.service)
        return result
    except Exception as e:
        logger.error(f"AI processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/generate-summary", dependencies=[Depends(verify_auth)])
async def generate_data_summary(data: Dict, service: str = "openai"):
    """Generate AI summary from provided data"""
    try:
        result = await ai_agent.generate_summary(data, service)
        return result
    except Exception as e:
        logger.error(f"Summary generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== MAIL AGENT ENDPOINTS =====
@app.post("/mail/send", dependencies=[Depends(verify_auth)])
async def send_email(request: EmailRequest):
    """Send email via mail agent"""
    try:
        result = await mail_agent.send_email(
            recipient_email=request.recipient_email,
            subject=request.subject,
            content=request.content,
            email_type=request.email_type
        )
        return result
    except Exception as e:
        logger.error(f"Email sending error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mail/send-bulk", dependencies=[Depends(verify_auth)])
async def send_bulk_emails(request: BulkEmailRequest):
    """Send bulk emails via mail agent"""
    try:
        result = await mail_agent.send_bulk_emails(
            recipients=request.recipients,
            subject=request.subject,
            content_template=request.content_template,
            email_type=request.email_type
        )
        return result
    except Exception as e:
        logger.error(f"Bulk email error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mail/send-credentials", dependencies=[Depends(verify_auth)])
async def send_credential_email(recipient_email: str, credentials: Dict, welcome_message: str = None):
    """Send credential email via mail agent"""
    try:
        result = await mail_agent.send_credential_email(
            recipient_email=recipient_email,
            credentials=credentials,
            welcome_message=welcome_message
        )
        return result
    except Exception as e:
        logger.error(f"Credential email error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== DATABASE AGENT ENDPOINTS =====
@app.get("/database/interns", dependencies=[Depends(verify_auth)])
async def get_all_interns():
    """Get all intern data from database"""
    try:
        result = await database_agent.fetch_data()
        return {
            "success": True,
            "count": len(result),
            "data": result
        }
    except Exception as e:
        logger.error(f"Database fetch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/database/intern", dependencies=[Depends(verify_auth)])
async def add_intern(intern: InternData):
    """Add new intern to database"""
    try:
        intern_dict = intern.dict()
        intern_dict["created_at"] = datetime.utcnow().isoformat()
        intern_dict["status"] = "pending"
        
        result = await database_agent.add_intern(intern_dict)
        return result
    except Exception as e:
        logger.error(f"Database add error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/database/documents/{collection}", dependencies=[Depends(verify_auth)])
async def get_documents(collection: str):
    """Get documents from specific collection"""
    try:
        result = await database_agent.get_documents(collection)
        return {
            "success": True,
            "collection": collection,
            "count": len(result),
            "data": result
        }
    except Exception as e:
        logger.error(f"Database documents error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== OUTLOOK AGENT ENDPOINTS =====
@app.post("/outlook/create-email", dependencies=[Depends(verify_auth)])
async def create_intern_email_account(intern: InternData):
    """Create new email account for intern via Outlook agent"""
    try:
        result = await outlook_agent.create_intern_email(intern.dict())
        return result
    except Exception as e:
        logger.error(f"Email creation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/outlook/create-bulk-emails", dependencies=[Depends(verify_auth)])
async def create_bulk_email_accounts(interns: List[InternData]):
    """Create email accounts for multiple interns"""
    try:
        intern_list = [intern.dict() for intern in interns]
        result = await outlook_agent.create_bulk_emails(intern_list)
        return result
    except Exception as e:
        logger.error(f"Bulk email creation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== AUTHENTICATION ENDPOINTS =====
@app.get("/auth/login")
async def login():
    """Get Microsoft authentication URL"""
    try:
        result = await outlook_agent.get_authentication_url()
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    except Exception as e:
        logger.error(f"Auth URL error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/auth/callback", response_class=HTMLResponse)
async def auth_callback_get(code: str, state: str = None):
    """Handle authentication callback from Microsoft (GET request)"""
    try:
        result = await outlook_agent.authenticate(code)
        
        if result["success"]:
            auth_state["authenticated"] = True
            auth_state["access_token"] = result["access_token"]
            auth_state["user_info"] = {"displayName": "Admin User"}
            
            return f"""
            <html>
                <head><title>Authentication Success</title></head>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                    <h1 style="color: green;">✅ Authentication Successful!</h1>
                    <p>Welcome to the Mail Agent System!</p>
                    <p>You can now close this window and return to the application.</p>
                    <script>
                        setTimeout(function() {{
                            window.close();
                        }}, 3000);
                    </script>
                </body>
            </html>
            """
        else:
            return f"""
            <html>
                <head><title>Authentication Failed</title></head>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                    <h1 style="color: red;">❌ Authentication Failed</h1>
                    <p>Error: {result['error']}</p>
                    <p>Please try again.</p>
                </body>
            </html>
            """
            
    except Exception as e:
        logger.error(f"Error in auth callback: {e}")
        return f"""
        <html>
            <head><title>Authentication Error</title></head>
            <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                <h1 style="color: red;">❌ Authentication Error</h1>
                <p>Error: {str(e)}</p>
                <p>Please try again.</p>
            </body>
        </html>
        """

@app.post("/auth/logout", dependencies=[Depends(verify_auth)])
async def logout():
    """Logout user"""
    auth_state["authenticated"] = False
    auth_state["access_token"] = None
    auth_state["user_info"] = None
    return {"success": True, "message": "Logged out successfully"}

# ===== WORKFLOW ENDPOINTS =====
@app.post("/workflow/complete-intern-setup", dependencies=[Depends(verify_auth)])
async def complete_intern_setup(intern: InternData):
    """
    Complete workflow: Add intern to DB, create email account, send credentials
    This demonstrates the 4-agent coordination
    """
    try:
        logger.info(f"🚀 Starting complete intern setup for {intern.name}")
        
        # Step 1: Add intern to database (Database Agent)
        intern_dict = intern.dict()
        intern_dict["created_at"] = datetime.utcnow().isoformat()
        intern_dict["status"] = "processing"
        
        db_result = await database_agent.add_intern(intern_dict)
        if not db_result.get("success"):
            raise HTTPException(status_code=500, detail="Failed to add intern to database")
        
        # Step 2: Create email account (Outlook Agent)
        email_result = await outlook_agent.create_intern_email(intern_dict)
        if not email_result.get("success"):
            # Update status in database
            intern_dict["status"] = "email_creation_failed"
            await database_agent.update_intern(intern_dict["name"], intern_dict)
            raise HTTPException(status_code=500, detail="Failed to create email account")
        
        # Step 3: Generate welcome message (AI Agent)
        ai_prompt = f"Generate a personalized welcome message for {intern.name} joining {intern.department} department"
        welcome_result = await ai_agent.process_prompt(ai_prompt, "openai")
        
        # Step 4: Update database with completion
        intern_dict["status"] = "completed"
        intern_dict["company_email"] = email_result.get("new_email")
        intern_dict["email_sent"] = email_result.get("notification_sent", {}).get("success", False)
        await database_agent.update_intern(intern_dict["name"], intern_dict)
        
        return {
            "success": True,
            "message": f"Complete setup finished for {intern.name}",
            "steps": {
                "database_added": db_result["success"],
                "email_created": email_result["success"],
                "credentials_sent": email_result.get("notification_sent", {}).get("success", False),
                "ai_welcome": welcome_result.get("success", False)
            },
            "details": {
                "new_email": email_result.get("new_email"),
                "personal_email": intern.personal_email,
                "welcome_message": welcome_result.get("content", ""),
                "created_at": intern_dict["created_at"]
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Complete intern setup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== SYSTEM STATUS =====
@app.get("/status")
async def system_status():
    """Get system status and agent health"""
    return {
        "system": "Mail Agent System 2.0",
        "agents": {
            "ai_agent": "✅ Ready - Processes prompts and orchestrates",
            "mail_agent": "✅ Ready - Sends all emails",
            "database_agent": "✅ Ready - Database access only", 
            "outlook_agent": "✅ Ready - Creates email accounts"
        },
        "authentication": {
            "status": "✅ Authenticated" if auth_state["authenticated"] else "❌ Not authenticated",
            "user": auth_state.get("user_info", {}).get("displayName", "None")
        },
        "endpoints": {
            "ai_processing": "/ai/process",
            "email_sending": "/mail/send",
            "database_access": "/database/interns",
            "account_creation": "/outlook/create-email",
            "complete_workflow": "/workflow/complete-intern-setup"
        },
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    logger.info("🚀 Starting Mail Agent System with 4-Agent Architecture")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )