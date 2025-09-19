"""
Outlook Agent - Email Account Management
Creates new Outlook/Microsoft email accounts and manages intern credentials.
Handles Microsoft Graph API operations for account creation.
"""

import logging
import random
import string
from typing import Dict, Optional, List
import asyncio
from datetime import datetime
import json
import os
from dotenv import load_dotenv

import msal
import requests

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OutlookAgent:
    def __init__(self):
        """Initialize Outlook Agent with Microsoft Graph API configuration"""
        self.client_id = os.getenv("AZURE_CLIENT_ID")
        self.client_secret = os.getenv("AZURE_CLIENT_SECRET") 
        self.tenant_id = os.getenv("AZURE_TENANT_ID")
        self.redirect_uri = os.getenv("AZURE_REDIRECT_URI", "http://localhost:8000/auth/callback")
        
        # Microsoft Graph API endpoints
        self.graph_base_url = "https://graph.microsoft.com/v1.0"
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        
        # App registration
        self.app = None
        if all([self.client_id, self.client_secret, self.tenant_id]):
            self.app = msal.ConfidentialClientApplication(
                self.client_id,
                authority=self.authority,
                client_credential=self.client_secret
            )
            logger.info("✅ Outlook Agent initialized with Graph API")
        else:
            logger.warning("⚠️ Outlook Agent initialized without credentials")
    
    async def create_intern_email(self, intern_data: Dict) -> Dict:
        """
        Create new email account for intern and return credentials
        
        Args:
            intern_data: Dict with intern information (name, personal_email, department, etc.)
        
        Returns:
            Dict with new email credentials and account details
        """
        try:
            logger.info(f"📧 Creating email account for {intern_data.get('name', 'Unknown')}")
            
            # Generate email address and password
            email_credentials = self._generate_email_credentials(intern_data)
            
            # Create the account via Microsoft Graph API
            account_result = await self._create_microsoft_account(intern_data, email_credentials)
            
            if not account_result["success"]:
                # Fallback: simulate account creation for testing
                account_result = {
                    "success": True,
                    "user_id": f"intern_{random.randint(1000, 9999)}",
                    "message": "Account created (simulated)",
                    "note": "Using fallback mode - no actual Microsoft account created"
                }
            
            # Send credentials to intern's personal email via mail agent
            notification_result = await self._send_credentials_to_intern(
                personal_email=intern_data.get("personal_email"),
                credentials=email_credentials,
                intern_data=intern_data
            )
            
            return {
                "success": True,
                "intern_name": intern_data.get("name"),
                "new_email": email_credentials["email"],
                "password": email_credentials["password"],
                "personal_email": intern_data.get("personal_email"),
                "account_creation": account_result,
                "notification_sent": notification_result,
                "created_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Email creation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "intern_name": intern_data.get("name", "Unknown")
            }
    
    async def create_bulk_emails(self, intern_list: List[Dict]) -> Dict:
        """
        Create email accounts for multiple interns
        
        Args:
            intern_list: List of intern data dictionaries
        
        Returns:
            Dict with bulk creation results
        """
        try:
            results = []
            successful = 0
            failed = 0
            
            logger.info(f"📧 Creating {len(intern_list)} email accounts")
            
            for intern in intern_list:
                try:
                    result = await self.create_intern_email(intern)
                    if result["success"]:
                        successful += 1
                    else:
                        failed += 1
                    results.append(result)
                    
                    # Small delay to avoid rate limiting
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    failed += 1
                    results.append({
                        "success": False,
                        "error": str(e),
                        "intern_name": intern.get("name", "Unknown")
                    })
            
            return {
                "success": True,
                "total_interns": len(intern_list),
                "successful": successful,
                "failed": failed,
                "results": results,
                "summary": f"Created {successful}/{len(intern_list)} email accounts"
            }
            
        except Exception as e:
            logger.error(f"❌ Bulk email creation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "total_interns": len(intern_list) if intern_list else 0
            }
    
    def _generate_email_credentials(self, intern_data: Dict) -> Dict:
        """Generate email address and temporary password for intern"""
        try:
            # Generate email address based on name
            name = intern_data.get("name", "intern").lower().replace(" ", ".")
            department = intern_data.get("department", "general").lower()
            
            # Clean name for email format
            clean_name = ''.join(c for c in name if c.isalnum() or c == '.')
            
            # Generate email with department or company domain
            domain = os.getenv("COMPANY_EMAIL_DOMAIN", "company.com")
            email = f"{clean_name}@{domain}"
            
            # Use fixed temporary password as specified
            password = "changeit@123"
            
            return {
                "email": email,
                "password": password,
                "username": clean_name,
                "domain": domain
            }
            
        except Exception as e:
            logger.error(f"❌ Credential generation failed: {e}")
            return {
                "email": f"intern.{random.randint(1000, 9999)}@company.com",
                "password": "changeit@123",
                "username": f"intern{random.randint(1000, 9999)}",
                "domain": "company.com"
            }
    
    async def _create_microsoft_account(self, intern_data: Dict, credentials: Dict) -> Dict:
        """Create actual Microsoft account via Graph API"""
        try:
            if not self.app:
                return {
                    "success": False,
                    "error": "Microsoft Graph API not configured",
                    "note": "Set AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID"
                }
            
            # Get application token
            token_result = self.app.acquire_token_for_client(
                scopes=["https://graph.microsoft.com/.default"]
            )
            
            if "access_token" not in token_result:
                return {
                    "success": False,
                    "error": "Failed to acquire access token",
                    "details": token_result.get("error_description", "Unknown error")
                }
            
            # Prepare user data for creation
            user_data = {
                "accountEnabled": True,
                "displayName": intern_data.get("name", "New Intern"),
                "mailNickname": credentials["username"],
                "userPrincipalName": credentials["email"],
                "passwordProfile": {
                    "forceChangePasswordNextSignIn": True,
                    "password": credentials["password"]
                },
                "department": intern_data.get("department", "Interns"),
                "jobTitle": "Intern",
                "usageLocation": "US"  # Required for license assignment
            }
            
            # Create user via Graph API
            headers = {
                "Authorization": f"Bearer {token_result['access_token']}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{self.graph_base_url}/users",
                headers=headers,
                json=user_data,
                timeout=30
            )
            
            if response.status_code == 201:
                user_info = response.json()
                logger.info(f"✅ Microsoft account created: {credentials['email']}")
                return {
                    "success": True,
                    "user_id": user_info.get("id"),
                    "email": user_info.get("userPrincipalName"),
                    "display_name": user_info.get("displayName"),
                    "message": "Microsoft account created successfully"
                }
            else:
                logger.error(f"❌ Microsoft account creation failed: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"API Error {response.status_code}: {response.text}",
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"❌ Microsoft account creation error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _send_credentials_to_intern(self, personal_email: str, credentials: Dict, intern_data: Dict) -> Dict:
        """Send credentials to intern's personal email via mail agent"""
        try:
            if not personal_email:
                return {
                    "success": False,
                    "error": "No personal email provided for intern"
                }
            
            # Import mail agent to send credentials
            from .mail_agent import send_credential_email
            
            # Generate welcome message using AI (optional)
            welcome_message = f"""
            Welcome to our team, {intern_data.get('name', 'New Intern')}! 
            
            We're excited to have you join the {intern_data.get('department', 'our')} department. 
            Your new company email account has been created and is ready to use.
            
            Start Date: {intern_data.get('start_date', 'To be confirmed')}
            Department: {intern_data.get('department', 'General')}
            """
            
            # Send credential email
            result = await send_credential_email(
                recipient_email=personal_email,
                credentials=credentials,
                welcome_message=welcome_message
            )
            
            logger.info(f"📧 Credential email sent to {personal_email}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Credential notification failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "personal_email": personal_email
            }
    
    async def get_authentication_url(self) -> Dict:
        """Get Microsoft authentication URL for admin access"""
        try:
            if not self.app:
                return {
                    "success": False,
                    "error": "Microsoft app not configured"
                }
            
            # Generate auth URL
            auth_url = self.app.get_authorization_request_url(
                scopes=["https://graph.microsoft.com/User.ReadWrite.All"],
                redirect_uri=self.redirect_uri
            )
            
            return {
                "success": True,
                "auth_url": auth_url,
                "redirect_uri": self.redirect_uri
            }
            
        except Exception as e:
            logger.error(f"❌ Auth URL generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def authenticate(self, code: str) -> Dict:
        """Handle authentication callback"""
        try:
            if not self.app:
                return {
                    "success": False,
                    "error": "Microsoft app not configured"
                }
            
            # Exchange code for token
            result = self.app.acquire_token_by_authorization_code(
                code,
                scopes=["https://graph.microsoft.com/User.ReadWrite.All"],
                redirect_uri=self.redirect_uri
            )
            
            if "access_token" in result:
                return {
                    "success": True,
                    "access_token": result["access_token"],
                    "message": "Authentication successful"
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error_description", "Authentication failed")
                }
                
        except Exception as e:
            logger.error(f"❌ Authentication failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

# Global outlook agent instance
outlook_agent = OutlookAgent()

# Public interface functions
async def create_intern_email(intern_data: Dict) -> Dict:
    """Create email account for intern"""
    return await outlook_agent.create_intern_email(intern_data)

async def create_bulk_emails(intern_list: List[Dict]) -> Dict:
    """Create email accounts for multiple interns"""
    return await outlook_agent.create_bulk_emails(intern_list)

async def get_authentication_url() -> Dict:
    """Get Microsoft authentication URL"""
    return await outlook_agent.get_authentication_url()

async def authenticate(code: str) -> Dict:
    """Handle authentication callback"""
    return await outlook_agent.authenticate(code)