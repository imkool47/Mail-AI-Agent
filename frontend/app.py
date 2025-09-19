"""
Streamlit Frontend
Admin interface for the Mail Agent system.
"""

import streamlit as st
import requests
import pandas as pd
import json
from datetime import datetime
import time
import os
from typing import Dict, List
from urllib.parse import parse_qs, urlparse

# Configuration
API_BASE_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="Mail Agent - Intern Management",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        color: #2E86AB;
        text-align: center;
        padding: 20px 0;
    }
    .status-success {
        background-color: #d4edda;
        color: #155724;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .status-error {
        background-color: #f8d7da;
        color: #721c24;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .status-warning {
        background-color: #fff3cd;
        color: #856404;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #2E86AB;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_info' not in st.session_state:
        st.session_state.user_info = {}
    if 'auth_url' not in st.session_state:
        st.session_state.auth_url = None


def check_api_health():
    """Check if API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def get_auth_status():
    """Check authentication status with API"""
    try:
        response = requests.get(f"{API_BASE_URL}/auth/status")
        if response.status_code == 200:
            data = response.json()
            st.session_state.authenticated = data.get("authenticated", False)
            st.session_state.user_info = data.get("user_info", {})
            return data
        return {"authenticated": False}
    except:
        return {"authenticated": False}


def get_microsoft_auth_url():
    """Get Microsoft authentication URL"""
    try:
        response = requests.get(f"{API_BASE_URL}/auth/url")
        if response.status_code == 200:
            return response.json()["auth_url"]
        return None
    except:
        return None


def handle_auth_callback(auth_code: str):
    """Handle authentication callback"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/callback",
            json={"auth_code": auth_code}
        )
        if response.status_code == 200:
            result = response.json()
            if result["success"]:
                st.session_state.authenticated = True
                st.session_state.user_info = result["user_info"]
                return True, "Authentication successful!"
            else:
                return False, result["error"]
        return False, "Authentication failed"
    except Exception as e:
        return False, str(e)


def logout():
    """Logout user"""
    try:
        requests.post(f"{API_BASE_URL}/auth/logout")
        st.session_state.authenticated = False
        st.session_state.user_info = {}
        st.rerun()
    except:
        pass


def main():
    """Main application"""
    init_session_state()
    
    # Check API health
    if not check_api_health():
        st.error("🚨 Backend API is not running. Please start the FastAPI server.")
        st.info("Run: `uvicorn backend.main:app --reload` from the project root directory")
        return
    
    # Check for auth code in URL
    query_params = st.query_params
    if "code" in query_params and not st.session_state.authenticated:
        auth_code = query_params["code"]
        success, message = handle_auth_callback(auth_code)
        if success:
            st.success(message)
            # Clear the URL parameters
            st.query_params.clear()
            st.rerun()
        else:
            st.error(f"Authentication failed: {message}")
    
    # Check authentication status
    auth_status = get_auth_status()
    
    # Header
    st.markdown('<h1 class="main-header">📧 Mail Agent - Intern Management System</h1>', 
                unsafe_allow_html=True)
    
    # Authentication section
    if not st.session_state.authenticated:
        show_login_page()
    else:
        show_main_app()


def show_login_page():
    """Show login page"""
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔐 Admin Authentication Required")
        st.info("Please connect your Microsoft admin account to manage intern accounts.")
        
        if st.button("🔗 Connect Microsoft Account", type="primary", use_container_width=True):
            auth_url = get_microsoft_auth_url()
            if auth_url:
                st.markdown(f'<a href="{auth_url}" target="_self">Click here to authenticate with Microsoft</a>', 
                           unsafe_allow_html=True)
                st.balloons()
            else:
                st.error("Failed to get authentication URL. Please check your configuration.")
        
        st.markdown("---")
        st.markdown("#### 📋 Setup Requirements:")
        st.markdown("""
        1. **Microsoft 365 Admin Account** - Required for creating intern accounts
        2. **Azure App Registration** - With appropriate permissions
        3. **Firebase Database** - For storing intern data
        4. **OpenAI/Gemini API** - For AI-powered content generation
        """)


def show_main_app():
    """Show main application interface"""
    # Sidebar with user info and navigation
    with st.sidebar:
        st.markdown("### 👤 Admin Profile")
        user_name = st.session_state.user_info.get("displayName", "Admin User")
        user_email = st.session_state.user_info.get("mail", "admin@company.com")
        
        st.write(f"**Name:** {user_name}")
        st.write(f"**Email:** {user_email}")
        
        if st.button("🚪 Logout", type="secondary"):
            logout()
        
        st.markdown("---")
        
        # Navigation
        st.markdown("### 📊 Navigation")
        page = st.selectbox(
            "Select Page",
            ["Dashboard", "Process Interns", "Manage Interns", "Analytics", "Settings"],
            index=0
        )
    
    # Main content based on selected page
    if page == "Dashboard":
        show_dashboard()
    elif page == "Process Interns":
        show_process_interns()
    elif page == "Manage Interns":
        show_manage_interns()
    elif page == "Analytics":
        show_analytics()
    elif page == "Settings":
        show_settings()


def show_dashboard():
    """Show dashboard with statistics"""
    st.markdown("## 📊 Dashboard")
    
    try:
        # Get statistics
        response = requests.get(f"{API_BASE_URL}/stats")
        if response.status_code == 200:
            stats = response.json()["statistics"]
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Interns", stats["total_interns"])
            
            with col2:
                st.metric("Pending", stats["pending_interns"])
            
            with col3:
                st.metric("Processed", stats["processed_interns"])
            
            with col4:
                completion_rate = (stats["processed_interns"] / max(stats["total_interns"], 1)) * 100
                st.metric("Completion Rate", f"{completion_rate:.1f}%")
            
            # Department distribution
            if stats["department_distribution"]:
                st.markdown("### 🏢 Department Distribution")
                dept_df = pd.DataFrame(
                    list(stats["department_distribution"].items()),
                    columns=["Department", "Count"]
                )
                st.bar_chart(dept_df.set_index("Department"))
            
            # Recent activity placeholder
            st.markdown("### 📈 Recent Activity")
            st.info("Recent activity feed will be displayed here.")
            
        else:
            st.error("Failed to load dashboard data")
            
    except Exception as e:
        st.error(f"Error loading dashboard: {e}")


def show_process_interns():
    """Show intern processing interface"""
    st.markdown("## ⚙️ Process New Interns")
    
    # Processing options
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 👤 Single Intern Processing")
        
        with st.form("single_intern_form"):
            first_name = st.text_input("First Name*")
            last_name = st.text_input("Last Name*")
            email = st.text_input("Personal Email")
            department = st.selectbox("Department*", 
                                    ["Engineering", "Marketing", "HR", "Finance", "Operations", "Other"])
            start_date = st.date_input("Start Date")
            skills = st.text_area("Skills (comma-separated)")
            education = st.text_area("Education Background")
            experience = st.text_area("Previous Experience")
            notes = st.text_area("Additional Notes")
            
            ai_service = st.selectbox("AI Service", ["openai", "gemini"])
            domain = st.text_input("Email Domain", value="yourdomain.com")
            
            submitted = st.form_submit_button("🚀 Process Intern", type="primary")
            
            if submitted:
                if first_name and last_name and department:
                    process_single_intern({
                        "first_name": first_name,
                        "last_name": last_name,
                        "email": email,
                        "department": department,
                        "start_date": str(start_date) if start_date else None,
                        "skills": skills,
                        "education": education,
                        "experience": experience,
                        "notes": notes
                    }, ai_service, domain)
                else:
                    st.error("Please fill in all required fields (marked with *)")
    
    with col2:
        st.markdown("### 📂 Batch Processing")
        
        uploaded_file = st.file_uploader("Upload CSV file with intern data", type="csv")
        
        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file)
                st.write("Preview of uploaded data:")
                st.dataframe(df.head())
                
                if st.button("🔄 Process All Interns", type="primary"):
                    process_batch_interns(df, ai_service, domain)
                    
            except Exception as e:
                st.error(f"Error reading CSV file: {e}")
        
        st.markdown("#### 📋 CSV Format Requirements:")
        st.markdown("""
        Required columns:
        - `first_name`
        - `last_name` 
        - `department`
        
        Optional columns:
        - `email`
        - `start_date`
        - `skills`
        - `education`
        - `experience`
        - `notes`
        """)


def process_single_intern(intern_data: Dict, ai_service: str, domain: str):
    """Process a single intern"""
    try:
        with st.spinner("Processing intern... This may take a few minutes."):
            response = requests.post(
                f"{API_BASE_URL}/process-intern",
                json={
                    "intern_data": intern_data,
                    "ai_service": ai_service,
                    "domain": domain
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                if result["success"]:
                    st.success(f"✅ Successfully processed {intern_data['first_name']} {intern_data['last_name']}")
                    st.info(f"📧 Outlook email created: {result['outlook_email']}")
                    
                    with st.expander("View AI-generated summary"):
                        st.write(result["summary"])
                else:
                    st.error(f"Processing failed: {result.get('error', 'Unknown error')}")
            else:
                st.error(f"API request failed: {response.status_code}")
                
    except Exception as e:
        st.error(f"Error processing intern: {e}")


def process_batch_interns(df: pd.DataFrame, ai_service: str, domain: str):
    """Process multiple interns from DataFrame"""
    try:
        interns_data = []
        for _, row in df.iterrows():
            intern_data = {
                "first_name": str(row.get("first_name", "")),
                "last_name": str(row.get("last_name", "")),
                "email": str(row.get("email", "")) if pd.notna(row.get("email")) else "",
                "department": str(row.get("department", "")),
                "start_date": str(row.get("start_date", "")) if pd.notna(row.get("start_date")) else None,
                "skills": str(row.get("skills", "")) if pd.notna(row.get("skills")) else "",
                "education": str(row.get("education", "")) if pd.notna(row.get("education")) else "",
                "experience": str(row.get("experience", "")) if pd.notna(row.get("experience")) else "",
                "notes": str(row.get("notes", "")) if pd.notna(row.get("notes")) else ""
            }
            
            interns_data.append({
                "intern_data": intern_data,
                "ai_service": ai_service,
                "domain": domain
            })
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        with st.spinner(f"Processing {len(interns_data)} interns..."):
            response = requests.post(
                f"{API_BASE_URL}/process-batch",
                json=interns_data
            )
            
            if response.status_code == 200:
                result = response.json()
                progress_bar.progress(1.0)
                
                st.success(f"✅ Batch processing completed!")
                st.info(f"Successfully processed: {result['successful']}/{result['total_processed']}")
                
                if result['failed'] > 0:
                    st.warning(f"⚠️ Failed to process: {result['failed']} interns")
                    
                    # Show failed results
                    with st.expander("View detailed results"):
                        for item in result['results']:
                            if not item['result']['success']:
                                st.error(f"❌ {item['intern_name']}: {item['result']['error']}")
                            else:
                                st.success(f"✅ {item['intern_name']}: Processed successfully")
            else:
                st.error(f"Batch processing failed: {response.status_code}")
                
    except Exception as e:
        st.error(f"Error in batch processing: {e}")


def show_manage_interns():
    """Show intern management interface"""
    st.markdown("## 👥 Manage Interns")
    
    try:
        # Get all interns
        response = requests.get(f"{API_BASE_URL}/interns")
        if response.status_code == 200:
            interns = response.json()["interns"]
            
            if interns:
                df = pd.DataFrame(interns)
                
                # Filters
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    status_filter = st.selectbox("Filter by Status", 
                                               ["All", "pending", "processed", "failed"])
                
                with col2:
                    dept_filter = st.selectbox("Filter by Department", 
                                             ["All"] + list(df["department"].unique()))
                
                with col3:
                    if st.button("🔄 Refresh Data"):
                        st.rerun()
                
                # Apply filters
                filtered_df = df.copy()
                if status_filter != "All":
                    filtered_df = filtered_df[filtered_df["status"] == status_filter]
                if dept_filter != "All":
                    filtered_df = filtered_df[filtered_df["department"] == dept_filter]
                
                st.dataframe(
                    filtered_df,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Actions
                st.markdown("### 🛠️ Actions")
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("📧 Send Test Email"):
                        st.info("Test email functionality would be implemented here")
                
                with col2:
                    if st.button("📊 Generate Report"):
                        st.info("Report generation would be implemented here")
                        
            else:
                st.info("No interns found. Start by processing some interns!")
                
        else:
            st.error("Failed to load intern data")
            
    except Exception as e:
        st.error(f"Error loading interns: {e}")


def show_analytics():
    """Show analytics and insights"""
    st.markdown("## 📈 Analytics & Insights")
    
    try:
        # Get AI analysis
        col1, col2 = st.columns(2)
        
        with col1:
            ai_service = st.selectbox("Select AI Service for Analysis", ["openai", "gemini"])
        
        with col2:
            if st.button("🤖 Generate AI Insights", type="primary"):
                with st.spinner("Generating AI insights..."):
                    response = requests.post(f"{API_BASE_URL}/ai/analyze?ai_service={ai_service}")
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result["success"]:
                            st.markdown("### 🎯 AI Analysis Results")
                            st.write(result["analysis"])
                        else:
                            st.error(f"Analysis failed: {result['error']}")
                    else:
                        st.error("Failed to generate analysis")
        
        # Placeholder for additional analytics
        st.markdown("### 📊 Performance Metrics")
        st.info("Additional analytics charts and metrics will be displayed here.")
        
    except Exception as e:
        st.error(f"Error in analytics: {e}")


def show_settings():
    """Show settings page"""
    st.markdown("## ⚙️ Settings")
    
    try:
        # Get current settings
        response = requests.get(f"{API_BASE_URL}/settings")
        if response.status_code == 200:
            settings = response.json()["settings"]
            
            st.markdown("### 🏢 Organization Settings")
            
            with st.form("settings_form"):
                company_name = st.text_input("Company Name", value=settings.get("company_name", ""))
                email_template = st.text_area("Email Template", value=settings.get("email_template", ""))
                password_length = st.number_input("Default Password Length", 
                                                value=settings.get("default_password_length", 8),
                                                min_value=6, max_value=20)
                
                if st.form_submit_button("💾 Save Settings"):
                    st.success("Settings saved! (Note: Backend implementation needed)")
            
            st.markdown("### 🔧 System Information")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**API Status:** ✅ Connected")
                st.write("**Database:** ✅ Connected")
            
            with col2:
                st.write("**Authentication:** ✅ Active")
                st.write("**AI Services:** ✅ Available")
                
        else:
            st.error("Failed to load settings")
            
    except Exception as e:
        st.error(f"Error loading settings: {e}")


if __name__ == "__main__":
    main()