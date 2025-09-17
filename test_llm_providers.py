#!/usr/bin/env python3
"""
Test script for multiple LLM providers
"""
import asyncio
import os
from llm_client import get_llm_client, initialize_llm_client
from config import settings

async def test_llm_provider():
    """Test the current LLM provider configuration"""
    print(f"Testing LLM Provider: {settings.llm_provider}")
    print("=" * 50)
    
    try:
        # Initialize LLM client
        llm_client = get_llm_client()
        
        # Get provider info
        provider_info = llm_client.get_provider_info()
        print(f"Provider: {provider_info['provider']}")
        print(f"Model: {provider_info['model']}")
        print(f"Available: {provider_info['available']}")
        
        if not provider_info['available']:
            print("❌ LLM client not available. Check your configuration.")
            return
        
        # Test chat completion
        print("\n🧪 Testing chat completion...")
        messages = [
            {"role": "user", "content": "Hello! Please respond with a brief greeting."}
        ]
        
        response = await llm_client.chat_completion(messages, max_tokens=50)
        print(f"✅ Response: {response}")
        
    except Exception as e:
        print(f"❌ Error testing LLM provider: {str(e)}")
        print(f"Provider: {settings.llm_provider}")
        
        # Provide configuration hints
        if settings.llm_provider == "openai":
            print("💡 For OpenAI: Set OPENAI_API_KEY in your .env file")
        elif settings.llm_provider == "groq":
            print("💡 For GROQ: Set GROQ_API_KEY in your .env file")
        elif settings.llm_provider == "aws":
            print("💡 For AWS Bedrock: Configure AWS credentials (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)")

def test_configuration():
    """Test configuration for all providers"""
    print("🔧 Configuration Status:")
    print("=" * 30)
    
    print(f"LLM Provider: {settings.llm_provider}")
    print(f"OpenAI API Key: {'✅ Set' if settings.openai_api_key else '❌ Not set'}")
    print(f"GROQ API Key: {'✅ Set' if settings.groq_api_key else '❌ Not set'}")
    print(f"AWS Access Key: {'✅ Set' if settings.aws_access_key_id else '❌ Not set'}")
    print(f"AWS Secret Key: {'✅ Set' if settings.aws_secret_access_key else '❌ Not set'}")
    
    print(f"\nModels:")
    print(f"OpenAI Model: {settings.openai_model}")
    print(f"GROQ Model: {settings.groq_model}")
    print(f"AWS Bedrock Model: {settings.aws_bedrock_model}")

async def main():
    """Main test function"""
    print("🚀 LLM Provider Test Suite")
    print("=" * 50)
    
    # Test configuration
    test_configuration()
    print()
    
    # Test current provider
    await test_llm_provider()
    
    print("\n" + "=" * 50)
    print("💡 To switch providers, set LLM_PROVIDER in your .env file to:")
    print("   - 'openai' for OpenAI GPT models")
    print("   - 'groq' for GROQ models")
    print("   - 'aws' for AWS Bedrock models")

if __name__ == "__main__":
    asyncio.run(main())
