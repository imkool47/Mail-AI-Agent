# Mail Agent - 4-Agent Architecture System

A sophisticated Python application that automates intern onboarding using a specialized 4-agent architecture: **AI Agent**, **Mail Agent**, **Database Agent**, and **Outlook Agent**. Integrates Microsoft Outlook, Firebase database, and AI services (OpenAI/Gemini) with clean separation of concerns.

## Features

- **🤖 AI Agent**: Processes prompts, orchestrates workflows, generates content
- **📧 Mail Agent**: Dedicated email operations with HTML templates and bulk sending
- **🗄️ Database Agent**: Pure data access layer for Firebase operations
- **🔧 Outlook Agent**: Microsoft Graph API integration for account creation
- **Admin Authentication**: Secure Microsoft admin account connection
- **AI-Powered Processing**: Generate personalized summaries using OpenAI or Gemini
- **Automated Account Creation**: Create Outlook accounts with secure credentials
- **Email Automation**: Send welcome emails with credentials and personalized content
- **Database Management**: Store and manage intern data in Firebase
- **Web Interface**: Clean Streamlit frontend for easy management

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
   
   **🚀 Full System (Recommended):**
   ```bash
   python mail.py
   ```
   
   **⚙️ Individual Components:**
   ```bash
   # Backend only
   python mail.py --backend-only
   
   # Frontend only  
   python mail.py --frontend-only
   ```
   
   **📦 Install Dependencies:**
   ```bash
   python mail.py --install
   ```
   
   - Backend API: http://localhost:8000
   - Frontend UI: http://localhost:8501

## Project Structure

```
Mail Agent/
├── agents/                    # 4-Agent System
│   ├── __init__.py           # Package initialization
│   ├── ai_agent.py           # 🤖 AI orchestrator
│   ├── mail_agent.py         # 📧 Email sender  
│   ├── database_agent.py     # 🗄️ Data access
│   └── outlook_agent.py      # 🔧 Account creation
├── backend/                   # Backend API Server
│   └── app.py                # FastAPI REST API
├── frontend/                  # Frontend UI
│   └── app.py                # Streamlit web interface
├── mail.py                   # 🚀 Main entry point
├── requirements.txt          # Python dependencies
├── .env.example             # Environment template
└── README.md                # This file
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

### 4-Agent Workflow

The system uses a specialized 4-agent architecture for clean separation of concerns:

1. **🤖 AI Agent**: Processes user prompts, analyzes data needs, generates content
2. **🗄️ Database Agent**: Provides data access when AI Agent needs information
3. **📧 Mail Agent**: Handles all email operations (sending, templates, bulk emails)
4. **🔧 Outlook Agent**: Creates Microsoft accounts and manages credentials

### Complete Intern Setup Process

1. **Admin Authentication**
   - Open the Streamlit interface at http://localhost:8501
   - Click "Connect Outlook Account"
   - Sign in with your Microsoft admin account

2. **Process Interns**
   - Navigate to "Add New Intern"
   - Fill in intern details
   - Click "Process Intern" to trigger the complete workflow:
     - **AI Agent** generates personalized summary and email content
     - **Database Agent** retrieves any needed data
     - **Outlook Agent** creates Microsoft account with secure credentials
     - **Mail Agent** sends welcome email with credentials to personal email
     - All data saved to Firebase database

3. **Manage Interns**
   - View all processed interns
   - Check processing status
   - Monitor email sending logs

### Individual Agent Operations

- **AI Processing**: Use `/ai/process` endpoint for content generation
- **Email Sending**: Use `/mail/send` endpoint for direct email operations
- **Database Access**: Use `/database/interns` endpoint for data operations
- **Account Creation**: Use `/outlook/create-email` endpoint for Microsoft accounts

## Security & Password Policy

- **Secure Credentials**: Outlook Agent generates unique, secure passwords for each intern
- **Credential Delivery**: Mail Agent sends credentials securely to personal email addresses
- **First Login**: Interns must change password on first Microsoft account login
- **No Hardcoded Passwords**: System generates unique credentials for each account
- **Encrypted Storage**: All sensitive data stored securely in Firebase

## Manual Testing

Test the complete 4-agent system through the web interface:

- **Authentication Flow**: Test Microsoft admin account connection
- **Complete Workflow**: Process sample intern data to test all 4 agents
- **Individual Agents**: Test each agent endpoint independently via API
- **Email Delivery**: Verify welcome emails are sent with correct credentials
- **Database Operations**: Check that intern data is stored correctly
- **Error Handling**: Test system behavior with invalid inputs

### Testing Individual Agents

```bash
# Test AI Agent
curl -X POST "http://localhost:8000/ai/process" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Generate welcome message for new intern"}'

# Test Database Agent
curl "http://localhost:8000/database/interns"

# Test Mail Agent
curl -X POST "http://localhost:8000/mail/send" \
  -H "Content-Type: application/json" \
  -d '{"to": "test@example.com", "subject": "Test", "body": "Test message"}'

# Test Outlook Agent (requires authentication)
curl -X POST "http://localhost:8000/outlook/create-email" \
  -H "Content-Type: application/json" \
  -d '{"intern_data": {...}}'
```

## Command Line Options

The `mail.py` launcher provides flexible deployment options:

```bash
# Full system (recommended)
python mail.py

# Individual components
python mail.py --backend-only        # Start only FastAPI backend
python mail.py --frontend-only       # Start only Streamlit frontend

# Development options
python mail.py --install             # Install dependencies
python mail.py --backend-port 8080   # Custom backend port
python mail.py --frontend-port 8502  # Custom frontend port

# Help
python mail.py --help                # Show all options
```

## API Endpoints

The FastAPI backend provides dedicated endpoints for each agent:

- `GET /status` - System health and agent status
- `POST /ai/process` - AI content generation and processing
- `POST /mail/send` - Email sending operations
- `GET /database/interns` - Database queries and operations
- `POST /outlook/create-email` - Microsoft account creation
- `POST /workflow/complete-intern-setup` - Complete intern onboarding workflow

Access interactive API docs at http://localhost:8000/docs

## Architecture Overview

### 4-Agent Design Principles

- **Single Responsibility**: Each agent has one clear purpose
- **Clean Interfaces**: Agents communicate through well-defined APIs
- **Scalability**: Agents can be deployed independently
- **Maintainability**: Changes to one agent don't affect others
- **Testability**: Each agent can be tested in isolation

### Agent Responsibilities

| Agent | Responsibility | Technologies |
|-------|---------------|-------------|
| 🤖 AI Agent | Content generation, workflow orchestration | OpenAI/Gemini APIs |
| 📧 Mail Agent | Email operations, templates, bulk sending | SMTP, HTML templates |
| 🗄️ Database Agent | Data access, queries, storage | Firebase/Firestore |
| 🔧 Outlook Agent | Account creation, credential management | Microsoft Graph API |

## Troubleshooting

1. **Import Errors**: Run `python mail.py --install`
2. **Authentication Issues**: Check Microsoft app registration and credentials
3. **Firebase Errors**: Verify service account credentials in `.env`
4. **AI Errors**: Confirm OpenAI/Gemini API keys are valid
5. **Port Conflicts**: Use `--backend-port` or `--frontend-port` options
6. **Agent Communication**: Check backend logs for inter-agent communication issues

## Support

This is a production-ready 4-agent system with clean architecture and comprehensive error handling. Each agent is designed for reliability and can operate independently. Check the console logs and API documentation for detailed debugging information.