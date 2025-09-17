#!/usr/bin/env python3
"""
Comprehensive test script for all LLM providers in the Agentic AI Workflows system
"""
import asyncio
import os
import sys
from typing import Dict, Any
from config import settings
from llm_client import LLMClient

class LLMProviderTester:
    """Test all available LLM providers"""
    
    def __init__(self):
        self.test_messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the capital of France? Answer in one sentence."}
        ]
    
    async def test_provider(self, provider_name: str) -> Dict[str, Any]:
        """Test a specific LLM provider"""
        print(f"\n🧪 Testing {provider_name.upper()} provider...")
        
        # Temporarily change provider
        original_provider = settings.llm_provider
        settings.llm_provider = provider_name
        
        try:
            # Initialize client
            client = LLMClient()
            
            # Test connection/initialization
            provider_info = client.get_provider_info()
            print(f"   ✅ Provider initialized: {provider_info}")
            
            # Test chat completion
            print(f"   🔄 Testing chat completion...")
            response = await client.chat_completion(self.test_messages, max_tokens=100)
            
            result = {
                "provider": provider_name,
                "status": "success",
                "response": response[:100] + "..." if len(response) > 100 else response,
                "provider_info": provider_info
            }
            
            print(f"   ✅ Success! Response: {result['response']}")
            return result
            
        except ImportError as e:
            result = {
                "provider": provider_name,
                "status": "missing_dependency",
                "error": str(e),
                "provider_info": None
            }
            print(f"   ⚠️  Missing dependency: {e}")
            return result
            
        except Exception as e:
            result = {
                "provider": provider_name,
                "status": "error",
                "error": str(e),
                "provider_info": None
            }
            print(f"   ❌ Error: {e}")
            return result
            
        finally:
            # Restore original provider
            settings.llm_provider = original_provider
    
    async def test_all_providers(self):
        """Test all available LLM providers"""
        print("🚀 TESTING ALL LLM PROVIDERS")
        print("=" * 60)
        
        providers = [
            "openai",
            "aws", 
            "groq",
            "gemini",
            "ollama",
            "huggingface",
            "together",
            "replicate",
            "local_openai"
        ]
        
        results = []
        
        for provider in providers:
            result = await self.test_provider(provider)
            results.append(result)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        working_providers = []
        missing_deps = []
        error_providers = []
        
        for result in results:
            if result["status"] == "success":
                working_providers.append(result["provider"])
                print(f"✅ {result['provider'].upper()}: Working")
            elif result["status"] == "missing_dependency":
                missing_deps.append(result["provider"])
                print(f"⚠️  {result['provider'].upper()}: Missing dependency")
            else:
                error_providers.append(result["provider"])
                print(f"❌ {result['provider'].upper()}: Error - {result['error']}")
        
        print(f"\n📈 Results:")
        print(f"   ✅ Working: {len(working_providers)} providers")
        print(f"   ⚠️  Missing deps: {len(missing_deps)} providers")
        print(f"   ❌ Errors: {len(error_providers)} providers")
        
        if working_providers:
            print(f"\n🎉 Ready to use: {', '.join(working_providers)}")
        
        if missing_deps:
            print(f"\n📦 Install dependencies for: {', '.join(missing_deps)}")
            print("   Run: pip install -r requirements_llm_providers.txt")
        
        return results
    
    def print_setup_instructions(self):
        """Print setup instructions for each provider"""
        print("\n" + "=" * 60)
        print("🔧 SETUP INSTRUCTIONS")
        print("=" * 60)
        
        instructions = {
            "ollama": [
                "1. Install Ollama from https://ollama.ai/",
                "2. Run: ollama pull llama2",
                "3. Set LLM_PROVIDER=ollama in .env"
            ],
            "huggingface": [
                "1. Run: pip install transformers torch",
                "2. Set LLM_PROVIDER=huggingface in .env",
                "3. Models will download automatically"
            ],
            "together": [
                "1. Sign up at https://together.ai/",
                "2. Get your API key",
                "3. Set TOGETHER_API_KEY in .env"
            ],
            "replicate": [
                "1. Sign up at https://replicate.com/",
                "2. Get your API token",
                "3. Set REPLICATE_API_TOKEN in .env"
            ],
            "local_openai": [
                "1. Install LM Studio or similar",
                "2. Start local server on port 1234",
                "3. Set LLM_PROVIDER=local_openai in .env"
            ]
        }
        
        for provider, steps in instructions.items():
            print(f"\n🔹 {provider.upper()}:")
            for step in steps:
                print(f"   {step}")

async def main():
    """Main test function"""
    tester = LLMProviderTester()
    
    print("🤖 AGENTIC AI WORKFLOWS - LLM PROVIDER TEST")
    print("Testing all available LLM providers...")
    print("This will help you identify which providers are ready to use.")
    
    # Test all providers
    results = await tester.test_all_providers()
    
    # Show setup instructions
    tester.print_setup_instructions()
    
    print("\n" + "=" * 60)
    print("✨ TEST COMPLETE!")
    print("Choose a working provider and update your .env file.")
    print("For free options, try: ollama, huggingface, together, or replicate")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
