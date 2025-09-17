#!/usr/bin/env python3
"""
Test script to verify GROQ is working correctly
"""
import asyncio
import os
from config import settings
from llm_client import get_llm_client

async def test_groq():
    """Test GROQ specifically"""
    print("🧪 TESTING GROQ CONFIGURATION")
    print("=" * 50)
    
    # Check configuration
    print(f"🔑 GROQ API Key: {'✅ Set' if settings.groq_api_key else '❌ Missing'}")
    print(f"🤖 GROQ Model: {settings.groq_model}")
    print(f"🔧 LLM Provider: {settings.llm_provider}")
    
    # Force GROQ provider
    original_provider = settings.llm_provider
    settings.llm_provider = "groq"
    
    try:
        print("\n🚀 Initializing GROQ client...")
        client = get_llm_client()
        print("✅ GROQ client initialized successfully!")
        
        print("\n💬 Testing chat completion...")
        test_messages = [
            {"role": "system", "content": "You are a helpful assistant. Keep responses very brief."},
            {"role": "user", "content": "What is 2+2? Answer in one sentence only."}
        ]
        
        response = await client.chat_completion(test_messages, max_tokens=50)
        
        print("✅ GROQ chat completion successful!")
        print(f"📝 Response: {response.strip()}")
        
        return True
        
    except Exception as e:
        print(f"❌ GROQ test failed: {str(e)}")
        
        # Provide specific troubleshooting
        if "API key" in str(e).lower():
            print("\n🔧 TROUBLESHOOTING:")
            print("1. Get your API key from https://console.groq.com/keys")
            print("2. Set GROQ_API_KEY in your .env file")
            print("3. Make sure LLM_PROVIDER=groq in your .env file")
        elif "model" in str(e).lower():
            print("\n🔧 TROUBLESHOOTING:")
            print("Valid GROQ models:")
            print("- llama3-8b-8192 (recommended)")
            print("- llama3-70b-8192")
            print("- mixtral-8x7b-32768")
            print("- gemma-7b-it")
        else:
            print(f"\n🔧 Error details: {str(e)}")
        
        return False
        
    finally:
        # Restore original provider
        settings.llm_provider = original_provider

async def test_other_providers():
    """Test if other providers work as fallback"""
    print("\n" + "=" * 50)
    print("🔄 TESTING OTHER PROVIDERS AS FALLBACK")
    print("=" * 50)
    
    fallback_providers = ["openai", "ollama", "together"]
    
    for provider in fallback_providers:
        print(f"\n🧪 Testing {provider}...")
        
        original_provider = settings.llm_provider
        settings.llm_provider = provider
        
        try:
            client = get_llm_client()
            print(f"✅ {provider} client initialized successfully!")
            
        except Exception as e:
            print(f"⚠️  {provider} not available: {str(e)}")
            
        finally:
            settings.llm_provider = original_provider

async def main():
    """Main test function"""
    groq_success = await test_groq()
    
    if not groq_success:
        await test_other_providers()
    
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    if groq_success:
        print("🎉 GROQ is working correctly!")
        print("✅ You can now use GROQ in your Agentic AI Workflows")
        print("\n🚀 To use GROQ:")
        print("1. Set LLM_PROVIDER=groq in your .env file")
        print("2. Start your application: python main_working.py")
        print("3. Test in the chat interface at http://localhost:4200")
    else:
        print("⚠️  GROQ needs configuration.")
        print("\n🔧 Quick fix:")
        print("1. Get API key from https://console.groq.com/keys")
        print("2. Add to .env: GROQ_API_KEY=your_key_here")
        print("3. Set: LLM_PROVIDER=groq")
        print("4. Run this test again: python test_groq_fix.py")

if __name__ == "__main__":
    asyncio.run(main())
