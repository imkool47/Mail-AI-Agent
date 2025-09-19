"""
Mail Agent - Dedicated Email Sending Service
Handles all email sending operations in the system.
Receives content from AI agent and sends emails via various providers.
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional, List
from datetime import datetime
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MailAgent:
    def __init__(self):
        """Initialize Mail Agent with email configurations"""
        self.smtp_config = {
            "server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
            "port": int(os.getenv("SMTP_PORT", "587")),
            "username": os.getenv("SMTP_USERNAME"),
            "password": os.getenv("SMTP_PASSWORD"),
            "use_tls": os.getenv("SMTP_USE_TLS", "true").lower() == "true"
        }
        
        # Default sender info
        self.default_sender = {
            "name": os.getenv("SENDER_NAME", "Mail Agent System"),
            "email": os.getenv("SENDER_EMAIL", self.smtp_config["username"])
        }
        
        logger.info("📧 Mail Agent initialized")
    
    async def send_email(self, recipient_email: str, subject: str, content: str, 
                        email_type: str = "general", sender_info: Optional[Dict] = None) -> Dict:
        """
        Send email to recipient
        
        Args:
            recipient_email: Email address to send to
            subject: Email subject line
            content: Email body content
            email_type: Type of email ("summary", "credentials", "policy", "general")
            sender_info: Optional custom sender information
        
        Returns:
            Dict with send status and details
        """
        try:
            logger.info(f"📧 Sending {email_type} email to {recipient_email}")
            
            # Use custom sender or default
            sender = sender_info or self.default_sender
            
            # Format email content based on type
            formatted_content = self._format_email_content(content, email_type)
            
            # Create message
            message = MIMEMultipart()
            message["From"] = f"{sender['name']} <{sender['email']}>"
            message["To"] = recipient_email
            message["Subject"] = subject
            
            # Add body
            message.attach(MIMEText(formatted_content, "html" if email_type in ["credentials", "welcome"] else "plain"))
            
            # Send email
            result = await self._send_smtp_email(message, recipient_email)
            
            if result["success"]:
                logger.info(f"✅ Email sent successfully to {recipient_email}")
                return {
                    "success": True,
                    "message": f"Email sent to {recipient_email}",
                    "email_type": email_type,
                    "subject": subject,
                    "recipient": recipient_email,
                    "sent_at": datetime.utcnow().isoformat()
                }
            else:
                logger.error(f"❌ Failed to send email to {recipient_email}: {result['error']}")
                return {
                    "success": False,
                    "error": result["error"],
                    "recipient": recipient_email,
                    "email_type": email_type
                }
                
        except Exception as e:
            logger.error(f"❌ Mail sending failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "recipient": recipient_email
            }
    
    async def send_credential_email(self, recipient_email: str, credentials: Dict, 
                                  welcome_message: str = None) -> Dict:
        """
        Send email with new account credentials
        
        Args:
            recipient_email: Personal email of intern
            credentials: Dict with email and password
            welcome_message: Optional welcome message from AI
        
        Returns:
            Dict with send status
        """
        try:
            # Create professional credential email
            subject = "Your New Company Email Account - Welcome!"
            
            # HTML formatted email for credentials
            content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">
                        Welcome to Our Team! 🎉
                    </h2>
                    
                    {f'<div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;"><p>{welcome_message}</p></div>' if welcome_message else ''}
                    
                    <h3 style="color: #27ae60;">Your New Email Account Details:</h3>
                    
                    <div style="background-color: #ecf0f1; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <p><strong>📧 Email Address:</strong> <code style="background-color: #fff; padding: 5px; border-radius: 3px;">{credentials.get('email', 'Not provided')}</code></p>
                        <p><strong>🔑 Temporary Password:</strong> <code style="background-color: #fff; padding: 5px; border-radius: 3px;">{credentials.get('password', 'Not provided')}</code></p>
                    </div>
                    
                    <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h4 style="color: #856404; margin-top: 0;">🔐 Important Security Information:</h4>
                        <ul style="color: #856404;">
                            <li>Please change your password on first login</li>
                            <li>Use a strong, unique password</li>
                            <li>Enable two-factor authentication if available</li>
                            <li>Keep your credentials secure and confidential</li>
                        </ul>
                    </div>
                    
                    <h3 style="color: #8e44ad;">Next Steps:</h3>
                    <ol>
                        <li>Login to your email account using the credentials above</li>
                        <li>Change your temporary password immediately</li>
                        <li>Complete your profile setup</li>
                        <li>Start connecting with your team!</li>
                    </ol>
                    
                    <div style="background-color: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p><strong>Need Help?</strong> Contact IT support or your manager if you have any questions.</p>
                    </div>
                    
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                    <p style="color: #7f8c8d; font-size: 12px; text-align: center;">
                        This email was automatically generated by the Mail Agent System.<br>
                        Please do not reply to this email.
                    </p>
                </div>
            </body>
            </html>
            """
            
            return await self.send_email(
                recipient_email=recipient_email,
                subject=subject,
                content=content,
                email_type="credentials"
            )
            
        except Exception as e:
            logger.error(f"❌ Credential email failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "recipient": recipient_email
            }
    
    async def send_bulk_emails(self, recipients: List[Dict], subject: str, 
                              content_template: str, email_type: str = "general") -> Dict:
        """
        Send bulk emails to multiple recipients
        
        Args:
            recipients: List of dicts with recipient info
            subject: Email subject template
            content_template: Email content template
            email_type: Type of email
        
        Returns:
            Dict with bulk send results
        """
        try:
            results = []
            successful = 0
            failed = 0
            
            for recipient in recipients:
                try:
                    # Personalize content if possible
                    personalized_content = content_template.replace(
                        "{name}", recipient.get("name", "Team Member")
                    ).replace(
                        "{email}", recipient.get("email", "")
                    )
                    
                    # Personalize subject
                    personalized_subject = subject.replace(
                        "{name}", recipient.get("name", "Team Member")
                    )
                    
                    # Send email
                    result = await self.send_email(
                        recipient_email=recipient["email"],
                        subject=personalized_subject,
                        content=personalized_content,
                        email_type=email_type
                    )
                    
                    if result["success"]:
                        successful += 1
                    else:
                        failed += 1
                    
                    results.append(result)
                    
                except Exception as e:
                    failed += 1
                    results.append({
                        "success": False,
                        "error": str(e),
                        "recipient": recipient.get("email", "unknown")
                    })
            
            return {
                "success": True,
                "total_recipients": len(recipients),
                "successful": successful,
                "failed": failed,
                "results": results,
                "summary": f"Sent {successful}/{len(recipients)} emails successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Bulk email failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "total_recipients": len(recipients) if recipients else 0
            }
    
    def _format_email_content(self, content: str, email_type: str) -> str:
        """Format email content based on type"""
        try:
            if email_type == "credentials":
                # Already formatted as HTML in send_credential_email
                return content
            
            elif email_type == "summary":
                # Add professional formatting
                formatted = f"""
                Dear Recipient,
                
                Please find the requested information below:
                
                {content}
                
                Best regards,
                {self.default_sender['name']}
                
                ---
                This email was automatically generated by the Mail Agent System.
                """
                return formatted
            
            elif email_type == "policy":
                # Policy-specific formatting
                formatted = f"""
                COMPANY POLICY INFORMATION
                
                {content}
                
                Please review this information carefully and contact HR if you have any questions.
                
                Best regards,
                HR Department
                
                ---
                This is an automated message from the Mail Agent System.
                """
                return formatted
            
            else:
                # General formatting
                return f"{content}\n\n---\nSent via Mail Agent System"
                
        except Exception as e:
            logger.warning(f"⚠️ Content formatting failed: {e}")
            return content
    
    async def _send_smtp_email(self, message: MIMEMultipart, recipient: str) -> Dict:
        """Send email via SMTP"""
        try:
            if not self.smtp_config["username"] or not self.smtp_config["password"]:
                return {
                    "success": False,
                    "error": "SMTP credentials not configured"
                }
            
            # Create SMTP connection
            server = smtplib.SMTP(self.smtp_config["server"], self.smtp_config["port"])
            
            if self.smtp_config["use_tls"]:
                server.starttls()
            
            # Login and send
            server.login(self.smtp_config["username"], self.smtp_config["password"])
            text = message.as_string()
            server.sendmail(self.smtp_config["username"], recipient, text)
            server.quit()
            
            return {"success": True}
            
        except Exception as e:
            logger.error(f"❌ SMTP send failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

# Global mail agent instance
mail_agent = MailAgent()

# Public interface functions
async def send_email(recipient_email: str, subject: str, content: str, 
                    email_type: str = "general") -> Dict:
    """Send email via mail agent"""
    return await mail_agent.send_email(recipient_email, subject, content, email_type)

async def send_credential_email(recipient_email: str, credentials: Dict, 
                               welcome_message: str = None) -> Dict:
    """Send credential email via mail agent"""
    return await mail_agent.send_credential_email(recipient_email, credentials, welcome_message)

async def send_bulk_emails(recipients: List[Dict], subject: str, 
                          content_template: str, email_type: str = "general") -> Dict:
    """Send bulk emails via mail agent"""
    return await mail_agent.send_bulk_emails(recipients, subject, content_template, email_type)