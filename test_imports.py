#!/usr/bin/env python3
"""
Test script to verify all imports work correctly
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test all imports"""
    try:
        print("Testing basic imports...")
        from config import settings
        from models import QueryRequest, WorkflowResponse, AgentResponse, AgentType
        print("✅ Basic imports successful")
        
        print("Testing agent imports...")
        from agents.base_agent import BaseAgent
        from agents.jira_agent import JiraAgent
        from agents.github_agent import GitHubAgent
        from agents.api_agent import APIAgent
        from agents.filesystem_agent import FileSystemAgent
        from agents.video_agent import VideoAgent
        from agents.s3_agent import S3Agent
        from agents.url_agent import URLAgent
        print("✅ Agent imports successful")
        
        print("Testing orchestrator import...")
        from orchestrator import AgenticOrchestrator
        print("✅ Orchestrator import successful")
        
        print("Testing API import...")
        from api import app
        print("✅ API import successful")
        
        print("\n🎉 All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
