#!/usr/bin/env python3
"""
Diagnostic script to identify GROQ integration issues
"""
import asyncio
import os
from config import settings

def check_environment():
    """Check environment configuration"""
    print("🔍 ENVIRONMENT DIAGNOSTICS")
    print("=" * 40)
    
    print(f"🔧 LLM_PROVIDER: {settings.llm_provider}")
    print(f"🔑 GROQ_API_KEY: {'✅ Set' if settings.groq_api_key else '❌ Missing'}")
    print(f"🤖 GROQ_MODEL: {settings.groq_model}")
    
    # Check .env file
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"📄 .env file: ✅ Found")
        with open(env_file, 'r') as f:
            content = f.read()
            if "LLM_PROVIDER=groq" in content:
                print("✅ LLM_PROVIDER=groq found in .env")
            else:
                print("⚠️  LLM_PROVIDER=groq not found in .env")
    else:
        print(f"📄 .env file: ❌ Not found")
    
    return settings.llm_provider == "groq" and settings.groq_api_key

async def test_llm_client_direct():
    """Test LLM client directly"""
    print("\n🧪 TESTING LLM CLIENT DIRECTLY")
    print("=" * 40)
    
    try:
        from llm_client import get_llm_client
        
        # Force GROQ provider
        original_provider = settings.llm_provider
        settings.llm_provider = "groq"
        
        print("🚀 Initializing LLM client...")
        client = get_llm_client()
        print("✅ LLM client initialized")
        
        print("💬 Testing chat completion...")
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello, GROQ is working!' in exactly those words."}
        ]
        
        response = await client.chat_completion(messages, max_tokens=50)
        print(f"✅ Chat completion successful!")
        print(f"📝 Response: {response}")
        
        # Restore original provider
        settings.llm_provider = original_provider
        return True
        
    except Exception as e:
        print(f"❌ LLM client test failed: {str(e)}")
        settings.llm_provider = original_provider
        return False

async def test_orchestrator():
    """Test the orchestrator's LLM integration"""
    print("\n🎯 TESTING ORCHESTRATOR LLM INTEGRATION")
    print("=" * 40)
    
    try:
        # Import the working orchestrator
        from main_working import WorkingOrchestrator
        from models import QueryRequest
        
        print("🚀 Initializing orchestrator...")
        orchestrator = WorkingOrchestrator()
        
        if orchestrator.llm_client:
            print("✅ Orchestrator has LLM client")
        else:
            print("❌ Orchestrator missing LLM client")
            return False
        
        print("💬 Testing query processing...")
        request = QueryRequest(prompt="Hello, can you help me find files?", max_results=5)
        result = await orchestrator.process_query(request)
        
        print(f"✅ Query processed successfully!")
        print(f"📊 Results: {len(result.results)} agent results")
        
        if result.answer:
            print(f"🤖 LLM Answer: {result.answer[:100]}...")
            return True
        else:
            print("⚠️  No LLM answer generated")
            return False
            
    except Exception as e:
        print(f"❌ Orchestrator test failed: {str(e)}")
        return False

async def test_backend_integration():
    """Test full backend integration"""
    print("\n🌐 TESTING BACKEND INTEGRATION")
    print("=" * 40)
    
    try:
        import requests
        
        print("🔍 Testing search endpoint...")
        response = requests.post(
            "http://localhost:8001/search",
            json={"prompt": "Find Python files in this project"},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend request successful!")
            
            if "answer" in data and data["answer"]:
                print(f"🤖 Backend LLM Answer: {data['answer'][:100]}...")
                return True
            else:
                print("⚠️  Backend returned no LLM answer")
                print(f"📊 Response keys: {list(data.keys())}")
                return False
        else:
            print(f"❌ Backend request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Backend test failed: {str(e)}")
        return False

async def main():
    """Main diagnostic function"""
    print("🔧 GROQ INTEGRATION DIAGNOSTICS")
    print("=" * 50)
    
    # Step 1: Check environment
    env_ok = check_environment()
    
    if not env_ok:
        print("\n❌ ENVIRONMENT ISSUES DETECTED")
        print("🔧 Fix these issues first:")
        print("1. Create a .env file in the project root")
        print("2. Add: LLM_PROVIDER=groq")
        print("3. Add: GROQ_API_KEY=your_actual_key")
        print("4. Add: GROQ_MODEL=llama3-8b-8192")
        return
    
    # Step 2: Test LLM client
    client_ok = await test_llm_client_direct()
    
    # Step 3: Test orchestrator
    orchestrator_ok = await test_orchestrator()
    
    # Step 4: Test backend
    backend_ok = await test_backend_integration()
    
    print("\n" + "=" * 50)
    print("📊 DIAGNOSTIC RESULTS")
    print("=" * 50)
    
    print(f"🔧 Environment: {'✅' if env_ok else '❌'}")
    print(f"🤖 LLM Client: {'✅' if client_ok else '❌'}")
    print(f"🎯 Orchestrator: {'✅' if orchestrator_ok else '❌'}")
    print(f"🌐 Backend: {'✅' if backend_ok else '❌'}")
    
    if all([env_ok, client_ok, orchestrator_ok, backend_ok]):
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ GROQ is working correctly with your system")
    else:
        print("\n⚠️  ISSUES DETECTED")
        print("🔧 Follow the specific error messages above to fix the issues")

if __name__ == "__main__":
    asyncio.run(main())
