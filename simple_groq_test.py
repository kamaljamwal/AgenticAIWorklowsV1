#!/usr/bin/env python3
"""
Simple test to verify GROQ is working
"""
import asyncio
import requests
import json

def test_backend_health():
    """Test if backend is healthy"""
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend is healthy")
            print(f"📊 Available agents: {', '.join(data.get('agents', []))}")
            return True
        else:
            print(f"❌ Backend unhealthy: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend not accessible: {str(e)}")
        return False

def test_groq_search():
    """Test GROQ through search endpoint"""
    try:
        print("\n🔍 Testing search with GROQ...")
        
        response = requests.post(
            "http://localhost:8001/search",
            json={"prompt": "Hello, can you help me?"},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Search request successful!")
            
            if "answer" in data and data["answer"]:
                print(f"🤖 GROQ Response: {data['answer'][:100]}...")
                return True
            else:
                print("⚠️  No answer received from GROQ")
                return False
        else:
            print(f"❌ Search failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Search test failed: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🧪 SIMPLE GROQ TEST")
    print("=" * 30)
    
    # Test 1: Backend health
    backend_ok = test_backend_health()
    
    if not backend_ok:
        print("\n❌ Backend is not running!")
        print("🔧 Start it with: python main_working.py")
        return
    
    # Test 2: GROQ search
    groq_ok = test_groq_search()
    
    print("\n" + "=" * 30)
    print("📊 RESULTS")
    print("=" * 30)
    
    if groq_ok:
        print("🎉 GROQ IS WORKING!")
        print("✅ You can now use the chat interface")
        print("🌐 Frontend: http://localhost:4200")
        print("🔧 Backend: http://localhost:8001")
    else:
        print("⚠️  GROQ needs attention")
        print("🔧 Check your .env file:")
        print("   LLM_PROVIDER=groq")
        print("   GROQ_API_KEY=your_key_here")
        print("   GROQ_MODEL=llama3-8b-8192")

if __name__ == "__main__":
    main()
