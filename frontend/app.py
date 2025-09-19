"""
Streamlit Frontend - 4-Agent Mail System
Clean interface for AI Agent, Mail Agent, Database Agent, and Outlook Agent
"""

import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Mail Agent System 2.0",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Backend URL
BACKEND_URL = "http://localhost:8000"

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def check_backend_connection():
    """Check if backend is running"""
    try:
        response = requests.get(f"{BACKEND_URL}/status", timeout=5)
        return response.status_code == 200
    except:
        return False

def call_api(endpoint, method="GET", data=None):
    """Make API call to backend"""
    try:
        url = f"{BACKEND_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=30)
        
        if response.status_code == 401:
            st.error("🔒 Authentication required. Please login first.")
            st.session_state.authenticated = False
            return None
        
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"❌ API Error: {str(e)}")
        return None

def main():
    """Main application"""
    
    # Title and header
    st.title("📧 Mail Agent System 2.0")
    st.markdown("### 4-Agent Architecture: AI • Mail • Database • Outlook")
    
    # Check backend connection
    if not check_backend_connection():
        st.error("❌ Backend server is not running!")
        st.info("💡 Please start the system: `python mail.py` or backend only: `python mail.py --backend-only`")
        return
    
    # Sidebar for navigation
    st.sidebar.title("🤖 Agent Controls")
    
    # Authentication section
    if not st.session_state.authenticated:
        st.sidebar.markdown("### 🔐 Authentication")
        if st.sidebar.button("🔗 Login with Microsoft"):
            auth_result = call_api("/auth/login")
            if auth_result and auth_result.get("success"):
                st.sidebar.success("✅ Opening authentication...")
                st.sidebar.markdown(f"[Click here to authenticate]({auth_result['auth_url']})")
            else:
                st.sidebar.error("❌ Failed to get auth URL")
        
        st.sidebar.info("🔒 Please authenticate to access the system")
        
        # Show system status even without auth
        show_system_status()
        return
    
    # Main navigation for authenticated users
    agent_choice = st.sidebar.selectbox(
        "🤖 Select Agent",
        ["🤖 AI Agent", "📧 Mail Agent", "🗄️ Database Agent", "🔧 Outlook Agent", "🔄 Complete Workflow"]
    )
    
    # Logout button
    if st.sidebar.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.rerun()
    
    # Agent interfaces
    if agent_choice == "🤖 AI Agent":
        ai_agent_interface()
    elif agent_choice == "📧 Mail Agent":
        mail_agent_interface()
    elif agent_choice == "🗄️ Database Agent":
        database_agent_interface()
    elif agent_choice == "🔧 Outlook Agent":
        outlook_agent_interface()
    elif agent_choice == "🔄 Complete Workflow":
        complete_workflow_interface()

def ai_agent_interface():
    """AI Agent interface"""
    st.header("🤖 AI Agent - Intelligent Processing")
    st.markdown("*Generates content, requests database info when needed, sends to mail agent*")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("💬 Process Prompt")
        
        # Prompt input
        prompt = st.text_area(
            "Enter your request:",
            placeholder="Examples:\n- Send intern policy to manager@company.com\n- Show me intern reports for Q3\n- Generate summary of new hires",
            height=100
        )
        
        # AI service selection
        service = st.selectbox("🤖 AI Service", ["openai", "gemini"])
        
        if st.button("🚀 Process Prompt"):
            if prompt:
                with st.spinner("🤖 AI Agent processing..."):
                    result = call_api("/ai/process", "POST", {
                        "prompt": prompt,
                        "service": service
                    })
                    
                    if result:
                        if result.get("success"):
                            st.success("✅ AI processing completed!")
                            
                            # Show results
                            st.markdown("### 📋 Generated Content")
                            st.write(result["content"])
                            
                            # Show workflow details
                            if result.get("database_used"):
                                st.info(f"🗄️ Database accessed: {result['database_info']['data_type']}")
                            
                            if result.get("email_sent"):
                                st.info("📧 Email sent via Mail Agent")
                                
                            # Show full result in expander
                            with st.expander("🔍 Full Result Details"):
                                st.json(result)
                        else:
                            st.error(f"❌ AI processing failed: {result.get('error', 'Unknown error')}")
            else:
                st.warning("⚠️ Please enter a prompt")
    
    with col2:
        st.subheader("📊 Quick Stats")
        
        # Show agent capabilities
        st.markdown("""
        **🤖 AI Agent Capabilities:**
        - ✅ Process any user prompt
        - ✅ Request database info when needed
        - ✅ Generate intelligent content
        - ✅ Send emails via Mail Agent
        - ✅ Coordinate with all agents
        """)

def mail_agent_interface():
    """Mail Agent interface"""
    st.header("📧 Mail Agent - Email Operations")
    st.markdown("*Handles all email sending operations in the system*")
    
    tab1, tab2, tab3 = st.tabs(["📤 Send Email", "📋 Bulk Emails", "🔑 Credential Emails"])
    
    with tab1:
        st.subheader("📤 Send Single Email")
        
        recipient = st.text_input("📧 Recipient Email", placeholder="user@company.com")
        subject = st.text_input("📝 Subject", placeholder="Email Subject")
        content = st.text_area("💬 Content", placeholder="Email body content...", height=150)
        email_type = st.selectbox("📋 Email Type", ["general", "summary", "policy", "credentials"])
        
        if st.button("📤 Send Email"):
            if recipient and subject and content:
                with st.spinner("📧 Sending email..."):
                    result = call_api("/mail/send", "POST", {
                        "recipient_email": recipient,
                        "subject": subject,
                        "content": content,
                        "email_type": email_type
                    })
                    
                    if result and result.get("success"):
                        st.success(f"✅ Email sent to {recipient}")
                        st.json(result)
                    else:
                        st.error(f"❌ Failed to send email: {result.get('error') if result else 'Unknown error'}")
            else:
                st.warning("⚠️ Please fill in all fields")
    
    with tab2:
        st.subheader("📋 Bulk Email Sending")
        
        recipients_text = st.text_area(
            "📧 Recipients (JSON format)",
            placeholder='[{"name": "John", "email": "john@company.com"}, {"name": "Jane", "email": "jane@company.com"}]',
            height=100
        )
        
        bulk_subject = st.text_input("📝 Subject Template", placeholder="Welcome {name}!")
        bulk_content = st.text_area("💬 Content Template", placeholder="Dear {name}, welcome to {email}...", height=100)
        bulk_type = st.selectbox("📋 Bulk Email Type", ["general", "welcome", "policy", "notification"])
        
        if st.button("📋 Send Bulk Emails"):
            if recipients_text and bulk_subject and bulk_content:
                try:
                    recipients = json.loads(recipients_text)
                    with st.spinner("📧 Sending bulk emails..."):
                        result = call_api("/mail/send-bulk", "POST", {
                            "recipients": recipients,
                            "subject": bulk_subject,
                            "content_template": bulk_content,
                            "email_type": bulk_type
                        })
                        
                        if result and result.get("success"):
                            st.success(f"✅ Sent {result['successful']}/{result['total_recipients']} emails")
                            st.json(result)
                        else:
                            st.error(f"❌ Bulk email failed: {result.get('error') if result else 'Unknown error'}")
                except json.JSONDecodeError:
                    st.error("❌ Invalid JSON format for recipients")
            else:
                st.warning("⚠️ Please fill in all fields")
    
    with tab3:
        st.subheader("🔑 Send Credential Email")
        
        cred_recipient = st.text_input("📧 Personal Email", placeholder="intern@personal.com")
        
        col1, col2 = st.columns(2)
        with col1:
            cred_email = st.text_input("📧 New Email", placeholder="intern@company.com")
        with col2:
            cred_password = st.text_input("🔑 Password", placeholder="changeit@123", type="password")
        
        welcome_msg = st.text_area("💬 Welcome Message", placeholder="Welcome to our team! We're excited to have you...", height=100)
        
        if st.button("🔑 Send Credentials"):
            if cred_recipient and cred_email and cred_password:
                with st.spinner("🔑 Sending credential email..."):
                    result = call_api("/mail/send-credentials", "POST", {
                        "recipient_email": cred_recipient,
                        "credentials": {"email": cred_email, "password": cred_password},
                        "welcome_message": welcome_msg
                    })
                    
                    if result and result.get("success"):
                        st.success(f"✅ Credential email sent to {cred_recipient}")
                        st.json(result)
                    else:
                        st.error(f"❌ Failed to send credentials: {result.get('error') if result else 'Unknown error'}")
            else:
                st.warning("⚠️ Please fill in recipient, email and password")

def database_agent_interface():
    """Database Agent interface"""
    st.header("🗄️ Database Agent - Data Access")
    st.markdown("*Pure database operations - read, write, search data*")
    
    tab1, tab2, tab3 = st.tabs(["👥 Interns", "📄 Documents", "➕ Add Data"])
    
    with tab1:
        st.subheader("👥 Intern Management")
        
        if st.button("🔄 Refresh Intern Data"):
            with st.spinner("🗄️ Fetching intern data..."):
                result = call_api("/database/interns")
                
                if result and result.get("success"):
                    st.success(f"✅ Found {result['count']} interns")
                    
                    if result["data"]:
                        df = pd.DataFrame(result["data"])
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.info("ℹ️ No intern data found")
                else:
                    st.error("❌ Failed to fetch intern data")
    
    with tab2:
        st.subheader("📄 Document Collections")
        
        collection = st.selectbox("📁 Collection", ["policies", "reports", "general", "projects"])
        
        if st.button(f"📄 Get {collection.title()} Documents"):
            with st.spinner(f"🗄️ Fetching {collection} documents..."):
                result = call_api(f"/database/documents/{collection}")
                
                if result and result.get("success"):
                    st.success(f"✅ Found {result['count']} documents in {collection}")
                    
                    if result["data"]:
                        st.json(result["data"])
                    else:
                        st.info(f"ℹ️ No documents found in {collection}")
                else:
                    st.error(f"❌ Failed to fetch {collection} documents")
    
    with tab3:
        st.subheader("➕ Add New Intern")
        
        with st.form("add_intern_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("👤 Full Name", placeholder="John Doe")
                personal_email = st.text_input("📧 Personal Email", placeholder="john@personal.com")
                department = st.text_input("🏢 Department", placeholder="Engineering")
            
            with col2:
                start_date = st.date_input("📅 Start Date")
                skills = st.text_input("🛠️ Skills (comma separated)", placeholder="Python, JavaScript, React")
                education = st.text_input("🎓 Education", placeholder="Computer Science, XYZ University")
            
            submitted = st.form_submit_button("➕ Add Intern to Database")
            
            if submitted:
                if name and personal_email and department:
                    intern_data = {
                        "name": name,
                        "personal_email": personal_email,
                        "department": department,
                        "start_date": start_date.isoformat(),
                        "skills": [skill.strip() for skill in skills.split(",")] if skills else [],
                        "education": education
                    }
                    
                    with st.spinner("🗄️ Adding intern to database..."):
                        result = call_api("/database/intern", "POST", intern_data)
                        
                        if result and result.get("success"):
                            st.success(f"✅ Added {name} to database")
                            st.json(result)
                        else:
                            st.error(f"❌ Failed to add intern: {result.get('error') if result else 'Unknown error'}")
                else:
                    st.warning("⚠️ Please fill in name, personal email, and department")

def outlook_agent_interface():
    """Outlook Agent interface"""
    st.header("🔧 Outlook Agent - Email Account Creation")
    st.markdown("*Creates new email accounts and sends credentials to personal emails*")
    
    tab1, tab2 = st.tabs(["👤 Single Account", "👥 Bulk Accounts"])
    
    with tab1:
        st.subheader("👤 Create Single Email Account")
        
        with st.form("create_email_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("👤 Full Name", placeholder="John Doe")
                personal_email = st.text_input("📧 Personal Email", placeholder="john@personal.com")
                department = st.text_input("🏢 Department", placeholder="Engineering")
            
            with col2:
                start_date = st.date_input("📅 Start Date")
                skills = st.text_input("🛠️ Skills", placeholder="Python, JavaScript")
                education = st.text_input("🎓 Education", placeholder="Computer Science")
            
            submitted = st.form_submit_button("🔧 Create Email Account")
            
            if submitted:
                if name and personal_email and department:
                    intern_data = {
                        "name": name,
                        "personal_email": personal_email,
                        "department": department,
                        "start_date": start_date.isoformat(),
                        "skills": [skills] if skills else [],
                        "education": education
                    }
                    
                    with st.spinner("🔧 Creating email account..."):
                        result = call_api("/outlook/create-email", "POST", intern_data)
                        
                        if result and result.get("success"):
                            st.success(f"✅ Email account created for {name}")
                            
                            # Show account details
                            st.markdown("### 📧 Account Details")
                            st.info(f"**New Email:** {result.get('new_email', 'N/A')}")
                            st.info(f"**Password:** {result.get('password', 'N/A')}")
                            st.info(f"**Credentials sent to:** {result.get('personal_email', 'N/A')}")
                            
                            with st.expander("🔍 Full Result"):
                                st.json(result)
                        else:
                            st.error(f"❌ Failed to create email: {result.get('error') if result else 'Unknown error'}")
                else:
                    st.warning("⚠️ Please fill in name, personal email, and department")
    
    with tab2:
        st.subheader("👥 Bulk Email Account Creation")
        
        st.markdown("Upload intern data in JSON format:")
        
        bulk_interns_text = st.text_area(
            "👥 Interns Data (JSON)",
            placeholder='''[
    {"name": "John Doe", "personal_email": "john@personal.com", "department": "Engineering"},
    {"name": "Jane Smith", "personal_email": "jane@personal.com", "department": "Marketing"}
]''',
            height=200
        )
        
        if st.button("👥 Create Bulk Email Accounts"):
            if bulk_interns_text:
                try:
                    interns_data = json.loads(bulk_interns_text)
                    
                    with st.spinner("🔧 Creating multiple email accounts..."):
                        result = call_api("/outlook/create-bulk-emails", "POST", interns_data)
                        
                        if result and result.get("success"):
                            st.success(f"✅ Created {result['successful']}/{result['total_interns']} email accounts")
                            
                            # Show summary
                            st.markdown("### 📊 Creation Summary")
                            st.metric("Total Processed", result["total_interns"])
                            st.metric("Successful", result["successful"])
                            st.metric("Failed", result["failed"])
                            
                            with st.expander("🔍 Detailed Results"):
                                st.json(result["results"])
                        else:
                            st.error(f"❌ Bulk creation failed: {result.get('error') if result else 'Unknown error'}")
                            
                except json.JSONDecodeError:
                    st.error("❌ Invalid JSON format")
            else:
                st.warning("⚠️ Please enter intern data")

def complete_workflow_interface():
    """Complete workflow interface"""
    st.header("🔄 Complete Workflow - All Agents Working Together")
    st.markdown("*Database → Outlook → Mail → AI coordination*")
    
    st.subheader("🚀 Complete Intern Setup")
    st.markdown("This workflow demonstrates all 4 agents working together:")
    
    # Workflow steps
    st.markdown("""
    **🔄 Workflow Steps:**
    1. **🗄️ Database Agent** - Adds intern to database
    2. **🔧 Outlook Agent** - Creates company email account
    3. **📧 Mail Agent** - Sends credentials to personal email
    4. **🤖 AI Agent** - Generates personalized welcome message
    """)
    
    st.divider()
    
    with st.form("complete_workflow_form"):
        st.subheader("👤 Intern Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("👤 Full Name", placeholder="John Doe")
            personal_email = st.text_input("📧 Personal Email", placeholder="john@personal.com")
            department = st.selectbox("🏢 Department", ["Engineering", "Marketing", "HR", "Finance", "Operations"])
        
        with col2:
            start_date = st.date_input("📅 Start Date")
            skills = st.text_input("🛠️ Skills (comma separated)", placeholder="Python, JavaScript, React")
            education = st.text_input("🎓 Education", placeholder="Computer Science, XYZ University")
        
        submitted = st.form_submit_button("🚀 Start Complete Setup", type="primary")
        
        if submitted:
            if name and personal_email and department:
                intern_data = {
                    "name": name,
                    "personal_email": personal_email,
                    "department": department,
                    "start_date": start_date.isoformat(),
                    "skills": [skill.strip() for skill in skills.split(",")] if skills else [],
                    "education": education
                }
                
                # Progress tracking
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                with st.spinner("🚀 Running complete workflow..."):
                    # Update progress
                    progress_bar.progress(25)
                    status_text.text("🗄️ Adding to database...")
                    
                    result = call_api("/workflow/complete-intern-setup", "POST", intern_data)
                    
                    progress_bar.progress(100)
                    status_text.text("✅ Workflow completed!")
                    
                    if result and result.get("success"):
                        st.success(f"🎉 Complete setup finished for {name}!")
                        
                        # Show workflow results
                        st.markdown("### 📊 Workflow Results")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            db_status = "✅" if result["steps"]["database_added"] else "❌"
                            st.metric("🗄️ Database", db_status)
                        
                        with col2:
                            email_status = "✅" if result["steps"]["email_created"] else "❌"
                            st.metric("🔧 Email Created", email_status)
                        
                        with col3:
                            cred_status = "✅" if result["steps"]["credentials_sent"] else "❌"
                            st.metric("📧 Credentials Sent", cred_status)
                        
                        with col4:
                            ai_status = "✅" if result["steps"]["ai_welcome"] else "❌"
                            st.metric("🤖 AI Welcome", ai_status)
                        
                        # Show details
                        st.markdown("### 📋 Setup Details")
                        st.info(f"**Company Email:** {result['details'].get('new_email', 'N/A')}")
                        st.info(f"**Personal Email:** {result['details'].get('personal_email', 'N/A')}")
                        
                        with st.expander("🔍 Full Workflow Result"):
                            st.json(result)
                    else:
                        st.error(f"❌ Workflow failed: {result.get('error') if result else 'Unknown error'}")
            else:
                st.warning("⚠️ Please fill in name, personal email, and department")

def show_system_status():
    """Show system status"""
    st.header("📊 System Status")
    
    if st.button("🔄 Refresh Status"):
        with st.spinner("Checking system status..."):
            result = call_api("/status")
            
            if result:
                st.success("✅ System is operational")
                
                # Agent status
                st.markdown("### 🤖 Agent Status")
                for agent, status in result["agents"].items():
                    st.markdown(f"- **{agent}**: {status}")
                
                # System info
                with st.expander("🔍 Detailed System Info"):
                    st.json(result)
            else:
                st.error("❌ Cannot connect to system")

if __name__ == "__main__":
    main()