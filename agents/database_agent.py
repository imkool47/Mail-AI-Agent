"""
Database Agent - Pure Database Access Layer
ONLY handles database operations - no business logic, no email sending, no AI processing.
Provides clean data access interface for other agents.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class FirebaseDatabaseAgent:
    """
    Pure Database Agent - Firebase Operations Only
    
    Responsibilities:
    - Connect to Firebase
    - Read/Write data
    - Search and filter data
    - Return raw data to requesting agents
    
    Does NOT:
    - Process business logic
    - Send emails
    - Generate content
    - Make decisions about data usage
    """
    
    def __init__(self):
        self.db = None
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Initialize Firebase connection"""
        try:
            # Check if Firebase is already initialized
            if not firebase_admin._apps:
                # Try environment variables first (for production)
                project_id = os.getenv('FIREBASE_PROJECT_ID')
                private_key = os.getenv('FIREBASE_PRIVATE_KEY')
                client_email = os.getenv('FIREBASE_CLIENT_EMAIL')
                
                if project_id and private_key and client_email:
                    # Use environment variables
                    cred_dict = {
                        "type": "service_account",
                        "project_id": project_id,
                        "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
                        "private_key": private_key.replace('\\n', '\n'),
                        "client_email": client_email,
                        "client_id": os.getenv('FIREBASE_CLIENT_ID'),
                        "auth_uri": os.getenv('FIREBASE_AUTH_URI', 'https://accounts.google.com/o/oauth2/auth'),
                        "token_uri": os.getenv('FIREBASE_TOKEN_URI', 'https://oauth2.googleapis.com/token'),
                    }
                    cred = credentials.Certificate(cred_dict)
                    firebase_admin.initialize_app(cred)
                else:
                    # Fallback to credentials file
                    credentials_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
                    if credentials_path and os.path.exists(credentials_path):
                        cred = credentials.Certificate(credentials_path)
                        firebase_admin.initialize_app(cred)
                    else:
                        # No credentials found - this will be handled gracefully
                        raise Exception("No Firebase credentials found. Please set up your .env file.")
            
            self.db = firestore.client()
            logger.info("Firebase initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
            self.db = None  # Set to None so we can check later
    
    async def fetch_intern_data(self, filters: Optional[Dict] = None) -> List[Dict]:
        """
        Fetch intern data from the database based on filters.
        
        Args:
            filters: Optional filters to apply to the query
            
        Returns:
            List of intern data documents
        """
        try:
            query = self.db.collection('interns')
            
            if filters:
                for field, value in filters.items():
                    query = query.where(filter=FieldFilter(field, "==", value))
            
            docs = query.stream()
            result = []
            
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                result.append(data)
            
            logger.info(f"Fetched {len(result)} intern records")
            return result
            
        except Exception as e:
            logger.error(f"Error fetching intern data: {e}")
            raise
    
    async def save_intern_credentials(self, intern_data: Dict) -> str:
        """
        Save new intern credentials to the database.
        
        Args:
            intern_data: Dictionary containing intern information and credentials
            
        Returns:
            Document ID of the saved record
        """
        try:
            # Add timestamp
            intern_data['created_at'] = datetime.utcnow()
            intern_data['updated_at'] = datetime.utcnow()
            
            # Save to database
            doc_ref = self.db.collection('intern_credentials').add(intern_data)
            doc_id = doc_ref[1].id
            
            logger.info(f"Saved intern credentials with ID: {doc_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Error saving intern credentials: {e}")
            raise
    
    async def get_intern_by_id(self, intern_id: str) -> Optional[Dict]:
        """
        Get specific intern data by ID.
        
        Args:
            intern_id: The intern's document ID
            
        Returns:
            Intern data or None if not found
        """
        try:
            doc_ref = self.db.collection('interns').document(intern_id)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id
                return data
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting intern by ID {intern_id}: {e}")
            raise
    
    async def update_intern_status(self, intern_id: str, status: str) -> bool:
        """
        Update intern's status in the database.
        
        Args:
            intern_id: The intern's document ID
            status: New status to set
            
        Returns:
            True if successful, False otherwise
        """
        try:
            doc_ref = self.db.collection('interns').document(intern_id)
            doc_ref.update({
                'status': status,
                'updated_at': datetime.utcnow()
            })
            
            logger.info(f"Updated intern {intern_id} status to {status}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating intern status: {e}")
            return False
    
    async def get_organization_settings(self) -> Dict:
        """
        Get organization settings from the database.
        
        Returns:
            Organization settings dictionary
        """
        try:
            doc_ref = self.db.collection('settings').document('organization')
            doc = doc_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            
            # Return default settings if none exist
            return {
                'company_name': 'Your Company',
                'email_template': 'Welcome to {company_name}!',
                'default_password_length': 8
            }
            
        except Exception as e:
            logger.error(f"Error getting organization settings: {e}")
            return {}
    
    async def save_email_log(self, email_log: Dict) -> str:
        """
        Save email sending log to the database.
        
        Args:
            email_log: Dictionary containing email log information
            
        Returns:
            Document ID of the saved log
        """
        try:
            email_log['timestamp'] = datetime.utcnow()
            
            doc_ref = self.db.collection('email_logs').add(email_log)
            doc_id = doc_ref[1].id
            
            logger.info(f"Saved email log with ID: {doc_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Error saving email log: {e}")
            raise
    
    async def get_pending_interns(self) -> List[Dict]:
        """
        Get all interns with pending status.
        
        Returns:
            List of pending intern records
        """
        try:
            query = self.db.collection('interns').where(
                filter=FieldFilter('status', '==', 'pending')
            )
            
            docs = query.stream()
            result = []
            
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                result.append(data)
            
            logger.info(f"Found {len(result)} pending interns")
            return result
            
        except Exception as e:
            logger.error(f"Error getting pending interns: {e}")
            raise

    async def add_intern(self, intern_data: Dict) -> Dict:
        """
        Add a new intern to the database.
        
        Args:
            intern_data: Dictionary containing intern information
            
        Returns:
            Result dictionary with success status and intern ID
        """
        try:
            # Add timestamp
            intern_data['created_at'] = datetime.utcnow().isoformat()
            intern_data['updated_at'] = datetime.utcnow().isoformat()
            
            # Add to Firestore
            doc_ref = self.db.collection('interns').add(intern_data)
            intern_id = doc_ref[1].id
            
            logger.info(f"✅ Added intern to database: {intern_data.get('name', 'Unknown')} (ID: {intern_id})")
            
            return {
                "success": True,
                "intern_id": intern_id,
                "message": f"Intern {intern_data.get('name', 'Unknown')} added successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to add intern: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def update_intern(self, intern_identifier: str, update_data: Dict) -> Dict:
        """
        Update an intern's data in the database.
        
        Args:
            intern_identifier: Name or ID of the intern
            update_data: Dictionary containing fields to update
            
        Returns:
            Result dictionary with success status
        """
        try:
            # Add timestamp
            update_data['updated_at'] = datetime.utcnow().isoformat()
            
            # Try to find by name first, then by ID
            query = self.db.collection('interns').where(
                filter=FieldFilter('name', '==', intern_identifier)
            )
            docs = list(query.stream())
            
            if not docs:
                # Try to find by document ID
                try:
                    doc_ref = self.db.collection('interns').document(intern_identifier)
                    if doc_ref.get().exists:
                        docs = [doc_ref.get()]
                except:
                    pass
            
            if not docs:
                return {
                    "success": False,
                    "error": f"Intern not found: {intern_identifier}"
                }
            
            # Update the first match
            doc = docs[0]
            doc.reference.update(update_data)
            
            logger.info(f"✅ Updated intern: {intern_identifier}")
            
            return {
                "success": True,
                "message": f"Intern {intern_identifier} updated successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to update intern {intern_identifier}: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_documents(self, collection_name: str) -> List[Dict]:
        """
        Get all documents from a specific collection.
        
        Args:
            collection_name: Name of the Firestore collection
            
        Returns:
            List of documents from the collection
        """
        try:
            docs = self.db.collection(collection_name).stream()
            result = []
            
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                result.append(data)
            
            logger.info(f"Retrieved {len(result)} documents from {collection_name}")
            return result
            
        except Exception as e:
            logger.error(f"Error getting documents from {collection_name}: {e}")
            return []


# Global instance (lazy initialization)
_database_agent = None

def get_database_agent():
    """Get or create the database agent instance"""
    global _database_agent
    if _database_agent is None:
        _database_agent = FirebaseDatabaseAgent()
    return _database_agent


# Agent interface functions that other components can call
async def fetch_data(filters: Optional[Dict] = None) -> List[Dict]:
    """Public interface for fetching intern data"""
    agent = get_database_agent()
    if agent.db is None:
        raise Exception("Firebase not initialized. Please check your credentials.")
    return await agent.fetch_intern_data(filters)


async def save_credentials(intern_data: Dict) -> str:
    """Public interface for saving intern credentials"""
    agent = get_database_agent()
    if agent.db is None:
        raise Exception("Firebase not initialized. Please check your credentials.")
    return await agent.save_intern_credentials(intern_data)


async def get_settings() -> Dict:
    """Public interface for getting organization settings"""
    agent = get_database_agent()
    if agent.db is None:
        raise Exception("Firebase not initialized. Please check your credentials.")
    return await agent.get_organization_settings()


async def log_email(email_log: Dict) -> str:
    """Public interface for logging email operations"""
    agent = get_database_agent()
    if agent.db is None:
        raise Exception("Firebase not initialized. Please check your credentials.")
    return await agent.save_email_log(email_log)


async def add_intern(intern_data: Dict) -> Dict:
    """Public interface for adding intern data"""
    agent = get_database_agent()
    if agent.db is None:
        raise Exception("Firebase not initialized. Please check your credentials.")
    return await agent.add_intern(intern_data)


async def update_intern(intern_identifier: str, update_data: Dict) -> Dict:
    """Public interface for updating intern data"""
    agent = get_database_agent()
    if agent.db is None:
        raise Exception("Firebase not initialized. Please check your credentials.")
    return await agent.update_intern(intern_identifier, update_data)


async def get_documents(collection_name: str) -> List[Dict]:
    """Public interface for getting documents from a collection"""
    agent = get_database_agent()
    if agent.db is None:
        raise Exception("Firebase not initialized. Please check your credentials.")
    return await agent.get_documents(collection_name)
    agent = get_database_agent()
    if agent.db is None:
        raise Exception("Firebase not initialized. Please check your credentials.")
    return await agent.save_email_log(email_log)