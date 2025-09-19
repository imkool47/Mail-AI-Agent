# Mail Agent - Simplified Intern Management System

A streamlined Python application that automates intern onboarding by integrating Microsoft Outlook, Firebase database, and AI services (OpenAI/Gemini).

## Features

- **Admin Authentication**: Connect your Microsoft admin account
- **AI-Powered Processing**: Generate personalized summaries and emails using OpenAI or Gemini
- **Automated Account Creation**: Create Outlook accounts for interns with temp password `changeit@123`
- **Email Automation**: Send welcome emails with credentials and personalized content
- **Database Management**: Store and manage intern data in Firebase
- **Web Interface**: Simple Streamlit frontend for easy management

## Quick Start

1. **Clone and Setup**:
   ```bash
   git clone <repository-url>
   cd "Mail Agent"
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   - Copy `.env.example` to `.env`
   - Fill in your API keys and credentials

3. **Run the Application**:
   ```bash
   python main.py
   ```
   - Backend API: http://localhost:8000
   - Frontend UI: http://localhost:8501

## Project Structure

```
Mail Agent/
├── agents/                 # Core business logic
│   ├── __init__.py        # Package initialization
│   ├── database_agent.py   # Firebase database operations
│   ├── outlook_agent.py    # Microsoft Graph API integration
│   └── ai_agent.py         # OpenAI/Gemini AI processing
├── backend/
│   └── main.py            # FastAPI REST API
├── frontend/
│   └── app.py             # Streamlit web interface
├── main.py                # Application launcher
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
└── README.md             # This file
```

## Configuration

### Required Environment Variables

Create a `.env` file with:

```env
# Microsoft Graph API (Required)
MICROSOFT_CLIENT_ID=your_client_id
MICROSOFT_CLIENT_SECRET=your_client_secret
MICROSOFT_TENANT_ID=your_tenant_id
MICROSOFT_REDIRECT_URI=http://localhost:8000/auth/callback

# Firebase (Required)
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_PRIVATE_KEY_ID=your_private_key_id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=your_client_email
FIREBASE_CLIENT_ID=your_client_id
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token

# AI Services (Choose one or both)
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key

# Application Settings
CORS_ORIGINS=http://localhost:8501,http://localhost:3000
```

### Service Setup

#### Microsoft Azure App Registration
1. Go to [Azure Portal](https://portal.azure.com)
2. Register a new application
3. Configure API permissions:
   - `User.ReadWrite.All`
   - `Mail.Send`
   - `Directory.ReadWrite.All`
4. Add redirect URI: `http://localhost:8000/auth/callback`

#### Firebase Setup
1. Create a Firebase project
2. Enable Firestore database
3. Generate service account credentials
4. Extract values for `.env` file

## Usage

### 1. Admin Authentication
- Open the Streamlit interface at http://localhost:8501
- Click "Connect Outlook Account"
- Sign in with your Microsoft admin account

### 2. Process Interns
- Navigate to "Add New Intern"
- Fill in intern details
- Click "Process Intern" to:
  - Generate AI summary
  - Create Outlook account with password `changeit@123`
  - Send welcome email to personal email
  - Save credentials to database

### 3. Manage Interns
- View all processed interns
- Check processing status
- Monitor email sending logs

## Password Policy

- **Temporary Password**: `changeit@123` (fixed for simplicity)
- Interns must change password on first login
- No complex password generation

## Manual Testing

Test through the web interface:
- Test authentication flow
- Process sample intern data
- Verify email delivery
- Check database storage

## Command Line Options

```bash
# Install dependencies only
python main.py --install

# Validate environment setup
python main.py --validate

# Start backend only
python main.py --backend-only

# Start frontend only  
python main.py --frontend-only

# Custom ports
python main.py --backend-port 8080 --frontend-port 8502
```

## API Documentation

Access interactive API docs at http://localhost:8000/docs

## Troubleshooting

1. **Import Errors**: Run `pip install -r requirements.txt`
2. **Authentication Issues**: Check Microsoft app registration
3. **Firebase Errors**: Verify service account credentials
4. **AI Errors**: Confirm API keys are valid

## Support

This is a simplified version focused on core functionality. Check the console logs and API documentation for debugging.