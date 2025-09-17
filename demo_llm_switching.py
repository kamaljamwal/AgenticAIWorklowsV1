#!/usr/bin/env python3
"""
Demo script showing how to switch between different LLM providers
"""
import asyncio
import os
from config import settings
from llm_client import get_llm_client

async def demo_provider_switching():
    """Demonstrate switching between different LLM providers"""
    
    print("🔄 DEMO: LLM Provider Switching")
    print("=" * 50)
    print("This demo shows how easy it is to switch between different LLM providers")
    print("in the Agentic AI Workflows system.\n")
    
    # Test message
    test_messages = [
        {"role": "system", "content": "You are a helpful assistant. Keep responses brief."},
        {"role": "user", "content": "What is 2+2? Answer in one sentence."}
    ]
    
    # Available providers to demo (only ones likely to work without setup)
    demo_providers = [
        ("groq", "GROQ (if API key configured)"),
        ("openai", "OpenAI (if API key configured)"),
        ("ollama", "Ollama (if running locally)"),
        ("local_openai", "Local OpenAI Server (if running)")
    ]
    
    print("🧪 Testing different providers with the same query:")
    print(f"Query: '{test_messages[1]['content']}'")
    print("-" * 50)
    
    successful_tests = 0
    
    for provider_id, provider_name in demo_providers:
        print(f"\n🔹 Testing {provider_name}...")
        
        # Store original provider
        original_provider = settings.llm_provider
        
        try:
            # Switch to new provider
            settings.llm_provider = provider_id
            
            # Get fresh client instance
            client = get_llm_client()
            
            # Test the provider
            response = await client.chat_completion(test_messages, max_tokens=50)
            
            print(f"   ✅ Success!")
            print(f"   📝 Response: {response.strip()}")
            successful_tests += 1
            
        except Exception as e:
            print(f"   ⚠️  Not available: {str(e)}")
            
        finally:
            # Restore original provider
            settings.llm_provider = original_provider
    
    print("\n" + "=" * 50)
    print("📊 DEMO RESULTS")
    print("=" * 50)
    
    if successful_tests > 0:
        print(f"✅ Successfully tested {successful_tests} provider(s)!")
        print("\n🎯 How to switch providers:")
        print("1. Update LLM_PROVIDER in your .env file")
        print("2. Restart your application")
        print("3. The system automatically uses the new provider!")
        
        print("\n💡 Example .env configurations:")
        print("   LLM_PROVIDER=ollama     # For local Ollama")
        print("   LLM_PROVIDER=groq       # For GROQ API")
        print("   LLM_PROVIDER=together   # For Together AI")
        print("   LLM_PROVIDER=huggingface # For local HF models")
        
    else:
        print("⚠️  No providers were available for testing.")
        print("\n🔧 To set up free providers:")
        print("1. Ollama: Install from https://ollama.ai/ and run 'ollama pull llama2'")
        print("2. Together AI: Sign up at https://together.ai/ for free credits")
        print("3. Replicate: Sign up at https://replicate.com/ for free credits")
        print("4. Hugging Face: Run 'pip install transformers torch'")
    
    print("\n📖 For detailed setup instructions, see: LLM_PROVIDERS_GUIDE.md")

async def demo_real_world_usage():
    """Show how the system would work in a real scenario"""
    
    print("\n" + "=" * 50)
    print("🌟 REAL-WORLD USAGE EXAMPLE")
    print("=" * 50)
    
    print("Here's how the LLM provider system works in the actual application:")
    print()
    print("1. 🔍 User asks: 'What Python files are in my project?'")
    print("2. 🤖 Orchestrator processes the query using the configured LLM")
    print("3. 🎯 Agents search and return results")
    print("4. 📝 LLM generates a natural language summary")
    print("5. 💬 User sees formatted results in the chat interface")
    print()
    print("The beauty is: regardless of which LLM provider you choose,")
    print("the user experience remains exactly the same!")
    print()
    print("🆓 Free options make this accessible to everyone:")
    print("   • Students can use Ollama locally")
    print("   • Startups can use Together AI free tier")
    print("   • Enterprises can use OpenAI or AWS Bedrock")
    print("   • Privacy-focused users can run everything locally")

async def main():
    """Main demo function"""
    await demo_provider_switching()
    await demo_real_world_usage()
    
    print("\n" + "=" * 50)
    print("🎉 DEMO COMPLETE!")
    print("=" * 50)
    print("Your Agentic AI Workflows system now supports multiple LLM providers!")
    print("Choose the one that best fits your needs and budget.")

if __name__ == "__main__":
    asyncio.run(main())
