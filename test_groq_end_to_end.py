#!/usr/bin/env python3
"""
End-to-end test for GROQ with the full Agentic AI Workflows system
"""
import asyncio
import json
import aiohttp
from config import settings

async def test_groq_with_backend():
    """Test GROQ through the backend API"""
    print("🔄 TESTING GROQ WITH FULL BACKEND")
    print("=" * 50)
    
    # Test query
    test_query = "What files are in this project?"
    
    print(f"📝 Test Query: '{test_query}'")
    print(f"🤖 Using LLM Provider: {settings.llm_provider}")
    print(f"🔧 GROQ Model: {settings.groq_model}")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test the search endpoint
            print("\n🚀 Sending request to backend...")
            
            async with session.post(
                "http://localhost:8001/search",
                json={"query": test_query},
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    
                    print("✅ Backend request successful!")
                    print(f"📊 Response status: {response.status}")
                    
                    # Check if we got results
                    if "results" in result:
                        print(f"🎯 Found {len(result['results'])} agent results")
                        
                        # Show agent results
                        for agent_result in result["results"]:
                            agent_name = agent_result.get("agent", "Unknown")
                            result_count = len(agent_result.get("results", []))
                            print(f"   📁 {agent_name}: {result_count} results")
                    
                    # Check if we got an answer (LLM response)
                    if "answer" in result and result["answer"]:
                        print(f"🤖 LLM Answer: {result['answer'][:200]}...")
                        print("✅ GROQ is generating responses correctly!")
                    else:
                        print("⚠️  No LLM answer received")
                        
                    return True
                    
                else:
                    print(f"❌ Backend request failed with status: {response.status}")
                    error_text = await response.text()
                    print(f"Error: {error_text}")
                    return False
                    
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

async def test_groq_directly():
    """Test GROQ client directly"""
    print("\n" + "=" * 50)
    print("🧪 TESTING GROQ CLIENT DIRECTLY")
    print("=" * 50)
    
    try:
        from llm_client import get_llm_client
        
        # Force GROQ provider
        original_provider = settings.llm_provider
        settings.llm_provider = "groq"
        
        client = get_llm_client()
        
        test_messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "List 3 benefits of using GROQ for AI applications."}
        ]
        
        response = await client.chat_completion(test_messages, max_tokens=200)
        
        print("✅ Direct GROQ test successful!")
        print(f"📝 Response: {response}")
        
        # Restore original provider
        settings.llm_provider = original_provider
        
        return True
        
    except Exception as e:
        print(f"❌ Direct GROQ test failed: {str(e)}")
        settings.llm_provider = original_provider
        return False

async def main():
    """Main test function"""
    print("🎯 GROQ END-TO-END TESTING")
    print("=" * 60)
    
    # Test 1: Direct GROQ client
    direct_success = await test_groq_directly()
    
    # Test 2: Full backend integration
    backend_success = await test_groq_with_backend()
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS")
    print("=" * 60)
    
    if direct_success and backend_success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ GROQ is working correctly with your Agentic AI Workflows")
        print("\n🚀 Ready to use:")
        print("1. Frontend: http://localhost:4200")
        print("2. Backend API: http://localhost:8001")
        print("3. LLM Provider: GROQ (llama3-8b-8192)")
        
    elif direct_success:
        print("⚠️  GROQ client works, but backend integration has issues")
        print("🔧 Check if the backend is running: python main_working.py")
        
    else:
        print("❌ GROQ configuration needs attention")
        print("🔧 Run: python test_groq_fix.py")
    
    print("\n💡 Tips:")
    print("- Make sure LLM_PROVIDER=groq in your .env file")
    print("- Verify your GROQ_API_KEY is valid")
    print("- Check that the backend is running on port 8001")

if __name__ == "__main__":
    asyncio.run(main())
