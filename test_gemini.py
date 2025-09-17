#!/usr/bin/env python3
"""
Test script specifically for Google Gemini integration
"""
import asyncio
from config import settings
from llm_client import get_llm_client

async def test_gemini():
    """Test Google Gemini specifically"""
    print("🤖 TESTING GOOGLE GEMINI")
    print("=" * 40)
    
    # Check configuration
    print(f"🔑 Gemini API Key: {'✅ Set' if settings.gemini_api_key else '❌ Missing'}")
    print(f"🧠 Gemini Model: {settings.gemini_model}")
    print(f"🔧 LLM Provider: {settings.llm_provider}")
    
    if not settings.gemini_api_key:
        print("\n❌ GEMINI API KEY MISSING")
        print("🔧 To get your free API key:")
        print("1. Go to https://aistudio.google.com/app/apikey")
        print("2. Sign in with your Google account")
        print("3. Click 'Create API Key'")
        print("4. Add to .env: GEMINI_API_KEY=your_key_here")
        print("5. Set: LLM_PROVIDER=gemini")
        return False
    
    # Force Gemini provider
    original_provider = settings.llm_provider
    settings.llm_provider = "gemini"
    
    try:
        print("\n🚀 Initializing Gemini client...")
        client = get_llm_client()
        print("✅ Gemini client initialized successfully!")
        
        print("\n💬 Testing chat completion...")
        test_messages = [
            {"role": "system", "content": "You are a helpful assistant. Be concise."},
            {"role": "user", "content": "What are 3 benefits of using Google Gemini? Answer briefly."}
        ]
        
        response = await client.chat_completion(test_messages, max_tokens=200)
        
        print("✅ Gemini chat completion successful!")
        print(f"📝 Response: {response}")
        
        return True
        
    except Exception as e:
        print(f"❌ Gemini test failed: {str(e)}")
        
        # Provide specific troubleshooting
        if "API key" in str(e).lower():
            print("\n🔧 TROUBLESHOOTING:")
            print("1. Get your API key from https://aistudio.google.com/app/apikey")
            print("2. Set GEMINI_API_KEY in your .env file")
            print("3. Make sure LLM_PROVIDER=gemini in your .env file")
        elif "quota" in str(e).lower() or "limit" in str(e).lower():
            print("\n🔧 QUOTA ISSUE:")
            print("You may have exceeded the free tier limits.")
            print("Gemini has generous free limits, but they do exist.")
            print("Try again later or check your usage at https://aistudio.google.com/")
        elif "import" in str(e).lower():
            print("\n🔧 MISSING DEPENDENCY:")
            print("Install the Google Generative AI package:")
            print("pip install google-generativeai")
        else:
            print(f"\n🔧 Error details: {str(e)}")
        
        return False
        
    finally:
        # Restore original provider
        settings.llm_provider = original_provider

async def compare_with_other_providers():
    """Compare Gemini with other available providers"""
    print("\n" + "=" * 40)
    print("🔄 COMPARING WITH OTHER PROVIDERS")
    print("=" * 40)
    
    providers_to_test = ["gemini", "groq", "ollama"]
    test_query = "What is 2+2? Answer in one sentence."
    
    for provider in providers_to_test:
        print(f"\n🧪 Testing {provider}...")
        
        original_provider = settings.llm_provider
        settings.llm_provider = provider
        
        try:
            client = get_llm_client()
            messages = [{"role": "user", "content": test_query}]
            response = await client.chat_completion(messages, max_tokens=50)
            
            print(f"✅ {provider}: {response.strip()}")
            
        except Exception as e:
            print(f"⚠️  {provider}: Not available - {str(e)}")
            
        finally:
            settings.llm_provider = original_provider

async def main():
    """Main test function"""
    gemini_success = await test_gemini()
    
    if gemini_success:
        await compare_with_other_providers()
    
    print("\n" + "=" * 40)
    print("📊 GEMINI TEST SUMMARY")
    print("=" * 40)
    
    if gemini_success:
        print("🎉 GEMINI IS WORKING!")
        print("✅ Google Gemini is ready to use")
        print("\n🌟 Gemini Benefits:")
        print("• FREE with generous limits")
        print("• High-quality responses")
        print("• Fast response times")
        print("• Multimodal capabilities")
        print("• Regular model updates")
        
        print("\n🚀 To use Gemini:")
        print("1. Set LLM_PROVIDER=gemini in your .env file")
        print("2. Start your application: python main_working.py")
        print("3. Test in the chat interface at http://localhost:4200")
        
    else:
        print("⚠️  Gemini needs configuration.")
        print("\n🔧 Quick setup:")
        print("1. Get free API key: https://aistudio.google.com/app/apikey")
        print("2. Install: pip install google-generativeai")
        print("3. Add to .env: GEMINI_API_KEY=your_key_here")
        print("4. Set: LLM_PROVIDER=gemini")
        print("5. Run this test again: python test_gemini.py")

if __name__ == "__main__":
    asyncio.run(main())
