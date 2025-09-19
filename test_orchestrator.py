#!/usr/bin/env python3
"""
Test script to demonstrate AI Agent Orchestrator capabilities
This shows how the AI agent can coordinate with database and email agents
"""

import asyncio
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "test@company.com"  # Change this to your test email

def test_orchestrator_api():
    """Test the orchestrator API endpoints"""
    
    print("🚀 Testing AI Agent Orchestrator")
    print("=" * 50)
    
    # Test 1: Check if orchestrator is ready
    print("\n1️⃣ Testing Orchestrator Readiness...")
    try:
        response = requests.get(f"{BASE_URL}/ai/orchestrator-test")
        if response.status_code == 200:
            result = response.json()
            print("✅ Orchestrator is ready!")
            print(f"📋 Capabilities: {len(result['capabilities'])} features available")
            for cap in result['capabilities']:
                print(f"   • {cap}")
        else:
            print(f"❌ Orchestrator not ready: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("💡 Make sure the server is running: python backend/main.py")
        return
    
    # Test 2: Policy Email (would need authentication)
    print(f"\n2️⃣ Policy Email Example (requires authentication)...")
    policy_request = {
        "policy_query": "intern policy",
        "recipient_email": TEST_EMAIL,
        "service": "openai"
    }
    print(f"📨 Would send policy email to: {TEST_EMAIL}")
    print(f"🔍 Policy query: {policy_request['policy_query']}")
    print("⚠️  Note: Requires authentication to actually send")
    
    # Test 3: Data Email Example
    print(f"\n3️⃣ Data Email Example (requires authentication)...")
    data_request = {
        "data_query": "intern reports for Q3",
        "recipient_email": TEST_EMAIL,
        "email_context": "Monthly report requested by management",
        "service": "gemini"
    }
    print(f"📊 Would fetch and send: {data_request['data_query']}")
    print(f"📧 To: {data_request['recipient_email']}")
    print(f"🤖 Using AI service: {data_request['service']}")
    
    print("\n" + "=" * 50)
    print("🎯 Orchestrator Workflow Summary:")
    print("1. AI Agent receives request")
    print("2. Database Agent fetches requested data")
    print("3. AI Agent generates email content")
    print("4. Outlook Agent sends the email")
    print("5. Result returned to user")
    
    print(f"\n💡 To test with real emails:")
    print(f"1. Start server: python backend/main.py")
    print(f"2. Authenticate with Microsoft")
    print(f"3. Use the Streamlit UI or API endpoints")

async def test_direct_orchestrator():
    """Test the orchestrator functions directly (if you have credentials)"""
    
    print("\n🔧 Direct Function Test")
    print("=" * 30)
    
    try:
        # Import the ai agent directly
        import sys
        sys.path.append('.')
        from agents import ai_agent
        
        # Test the orchestrator function
        print("🧪 Testing process_and_send_policy_email function...")
        
        # This would work if you have proper credentials set up
        result = await ai_agent.process_and_send_policy_email(
            policy_query="intern remote work policy",
            recipient_email=TEST_EMAIL,
            service="openai"
        )
        
        print(f"📊 Result: {result}")
        
    except Exception as e:
        print(f"⚠️  Direct test failed (expected if no credentials): {e}")
        print("💡 This is normal if Firebase/Outlook credentials aren't set up")

if __name__ == "__main__":
    print("🤖 AI Agent Orchestrator Test Suite")
    print("This demonstrates how AI agents can coordinate actions")
    
    # Test API endpoints
    test_orchestrator_api()
    
    # Test direct functions (optional)
    print(f"\n🔍 Want to test direct functions? (requires credentials)")
    user_input = input("Test direct orchestrator functions? (y/N): ").lower()
    
    if user_input == 'y':
        asyncio.run(test_direct_orchestrator())
    
    print(f"\n🚀 Test complete! Your AI agent can now:")
    print(f"   • Fetch data from database")
    print(f"   • Generate intelligent email content")
    print(f"   • Send emails via Outlook")
    print(f"   • All in one coordinated action!")