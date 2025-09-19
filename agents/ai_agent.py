"""
AI Agent - Central Intelligence Orchestrator
Generates data by given prompt, requests database info when needed,
and sends to mail agent for email delivery.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import openai
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIAgent:
    def __init__(self):
        """Initialize AI Agent with API configurations"""
        self.openai_client = None
        self.gemini_client = None
        
        # Initialize OpenAI if key available
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            openai.api_key = openai_key
            self.openai_client = openai
            logger.info("✅ OpenAI client initialized")
        
        # Initialize Gemini if key available
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            genai.configure(api_key=gemini_key)
            self.gemini_client = genai.GenerativeModel('gemini-pro')
            logger.info("✅ Gemini client initialized")
    
    async def process_user_prompt(self, prompt: str, service: str = "openai") -> Dict:
        """
        Main AI function: Process user prompt and generate intelligent response
        
        Args:
            prompt: User's request/question
            service: AI service to use ("openai" or "gemini")
        
        Returns:
            Dict with generated content and any additional actions taken
        """
        try:
            logger.info(f"🤖 Processing prompt with {service}: {prompt[:100]}...")
            
            # Step 1: Analyze if database information is needed
            needs_data = await self._analyze_data_needs(prompt, service)
            
            database_info = None
            if needs_data["requires_database"]:
                logger.info(f"🗄️ Requesting database info: {needs_data['data_type']}")
                database_info = await self._request_database_info(needs_data["data_type"], needs_data.get("query_details"))
            
            # Step 2: Generate comprehensive response
            generated_content = await self._generate_content(prompt, database_info, service)
            
            # Step 3: Check if email needs to be sent
            needs_email = await self._analyze_email_needs(prompt, generated_content, service)
            
            email_result = None
            if needs_email["should_send_email"]:
                logger.info(f"📧 Sending email to: {needs_email['recipient']}")
                email_result = await self._send_via_mail_agent(
                    recipient=needs_email["recipient"],
                    subject=needs_email["subject"],
                    content=generated_content["content"],
                    email_type=needs_email.get("email_type", "summary")
                )
            
            return {
                "success": True,
                "prompt": prompt,
                "content": generated_content["content"],
                "database_used": needs_data["requires_database"],
                "database_info": database_info,
                "email_sent": needs_email["should_send_email"],
                "email_result": email_result,
                "service_used": service,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ AI processing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "prompt": prompt
            }
    
    async def _analyze_data_needs(self, prompt: str, service: str) -> Dict:
        """Analyze if prompt needs database information"""
        try:
            analysis_prompt = f"""
            Analyze this user prompt and determine if it needs database information:
            
            Prompt: "{prompt}"
            
            Return JSON with:
            - requires_database: true/false
            - data_type: "interns", "policies", "reports", "general" or null
            - query_details: specific search criteria or null
            
            Examples:
            - "Show me intern details" → requires_database: true, data_type: "interns"
            - "What's the weather?" → requires_database: false
            - "Send policy to manager" → requires_database: true, data_type: "policies"
            """
            
            if service == "openai" and self.openai_client:
                response = await self.openai_client.ChatCompletion.acreate(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": analysis_prompt}],
                    max_tokens=200
                )
                content = response.choices[0].message.content
            elif service == "gemini" and self.gemini_client:
                response = await self.gemini_client.generate_content_async(analysis_prompt)
                content = response.text
            else:
                # Fallback analysis
                content = '{"requires_database": false, "data_type": null, "query_details": null}'
            
            # Parse JSON response
            result = json.loads(content.strip().replace('```json', '').replace('```', ''))
            return result
            
        except Exception as e:
            logger.warning(f"⚠️ Data analysis failed, using fallback: {e}")
            # Simple keyword-based fallback
            keywords = ["intern", "policy", "report", "data", "database", "fetch", "get", "show"]
            needs_data = any(keyword in prompt.lower() for keyword in keywords)
            
            return {
                "requires_database": needs_data,
                "data_type": "general" if needs_data else None,
                "query_details": prompt if needs_data else None
            }
    
    async def _request_database_info(self, data_type: str, query_details: Optional[str] = None) -> Dict:
        """Request information from database agent"""
        try:
            # Import database agent functions
            from .database_agent import get_documents, search_documents, fetch_data
            
            logger.info(f"🗄️ Requesting {data_type} data from database")
            
            if data_type == "interns":
                data = await fetch_data()
            elif data_type == "policies":
                data = await get_documents("policies")
            elif data_type == "reports":
                data = await get_documents("reports")
            else:
                # General search
                data = await get_documents("general")
            
            return {
                "success": True,
                "data_type": data_type,
                "count": len(data) if data else 0,
                "data": data[:10] if data else [],  # Limit to 10 items
                "query_details": query_details
            }
            
        except Exception as e:
            logger.error(f"❌ Database request failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "data_type": data_type
            }
    
    async def _generate_content(self, prompt: str, database_info: Optional[Dict], service: str) -> Dict:
        """Generate intelligent content using AI"""
        try:
            # Build comprehensive prompt
            full_prompt = f"User Request: {prompt}\n\n"
            
            if database_info and database_info.get("success"):
                full_prompt += f"Database Information Available:\n"
                full_prompt += f"- Data Type: {database_info['data_type']}\n"
                full_prompt += f"- Count: {database_info['count']} records\n"
                full_prompt += f"- Data: {json.dumps(database_info['data'][:3], indent=2)}\n\n"
            
            full_prompt += """
            Please provide a comprehensive, professional response that:
            1. Addresses the user's request directly
            2. Uses the database information if provided
            3. Is clear and actionable
            4. Includes relevant details and insights
            """
            
            if service == "openai" and self.openai_client:
                response = await self.openai_client.ChatCompletion.acreate(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": full_prompt}],
                    max_tokens=1000
                )
                content = response.choices[0].message.content
                
            elif service == "gemini" and self.gemini_client:
                response = await self.gemini_client.generate_content_async(full_prompt)
                content = response.text
                
            else:
                # Fallback response
                content = f"Response to: {prompt}\n\n"
                if database_info and database_info.get("success"):
                    content += f"Found {database_info['count']} records in database.\n"
                    content += f"Data summary: {database_info['data'][:2] if database_info['data'] else 'No data available'}"
                else:
                    content += "Generated response based on request (no database access needed)."
            
            return {
                "success": True,
                "content": content,
                "service_used": service
            }
            
        except Exception as e:
            logger.error(f"❌ Content generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "content": f"I apologize, but I couldn't generate a response for: {prompt}"
            }
    
    async def _analyze_email_needs(self, prompt: str, generated_content: Dict, service: str) -> Dict:
        """Analyze if generated content should be sent via email"""
        try:
            # Simple keyword analysis for email sending
            email_keywords = ["send", "mail", "email", "notify", "inform", "share"]
            recipient_keywords = ["to", "@", "manager", "intern", "hr"]
            
            should_send = any(keyword in prompt.lower() for keyword in email_keywords)
            has_recipient = any(keyword in prompt.lower() for keyword in recipient_keywords)
            
            if should_send and has_recipient:
                # Extract recipient from prompt (simple extraction)
                recipient = "default@company.com"  # Default
                
                # Look for email pattern
                import re
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                emails = re.findall(email_pattern, prompt)
                if emails:
                    recipient = emails[0]
                
                # Generate subject
                subject = f"AI Generated Response - {datetime.now().strftime('%Y-%m-%d')}"
                
                return {
                    "should_send_email": True,
                    "recipient": recipient,
                    "subject": subject,
                    "email_type": "ai_response"
                }
            
            return {"should_send_email": False}
            
        except Exception as e:
            logger.warning(f"⚠️ Email analysis failed: {e}")
            return {"should_send_email": False}
    
    async def _send_via_mail_agent(self, recipient: str, subject: str, content: str, email_type: str = "summary") -> Dict:
        """Send content via mail agent"""
        try:
            # Import mail agent
            from .mail_agent import send_email
            
            result = await send_email(
                recipient_email=recipient,
                subject=subject,
                content=content,
                email_type=email_type
            )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Mail agent sending failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "recipient": recipient
            }

# Global AI agent instance
ai_agent = AIAgent()

# Public interface functions
async def process_prompt(prompt: str, service: str = "openai") -> Dict:
    """Process user prompt and generate intelligent response"""
    return await ai_agent.process_user_prompt(prompt, service)

async def generate_summary(data: Dict, service: str = "openai") -> Dict:
    """Generate summary from provided data"""
    prompt = f"Please create a professional summary of this data: {json.dumps(data, indent=2)}"
    return await ai_agent.process_user_prompt(prompt, service)

async def analyze_and_respond(prompt: str, context: Optional[Dict] = None, service: str = "openai") -> Dict:
    """Analyze prompt with optional context and respond"""
    full_prompt = prompt
    if context:
        full_prompt += f"\n\nContext: {json.dumps(context, indent=2)}"
    
    return await ai_agent.process_user_prompt(full_prompt, service)