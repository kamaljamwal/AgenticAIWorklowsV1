#!/usr/bin/env python3
"""
Debug script to check what the backend actually returns
"""
import requests
import json

def test_backend_response():
    """Test what the backend actually returns"""
    print("🔍 Testing backend response structure...")
    
    try:
        response = requests.post(
            "http://localhost:8001/search",
            json={"prompt": "who is prime minister of india", "max_results": 3},
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Response received!")
            print(f"📊 Response keys: {list(data.keys())}")
            
            # Check each field
            for key, value in data.items():
                if key == "results":
                    print(f"🔧 {key}: {len(value)} items")
                elif key in ["summary", "answer"]:
                    print(f"💬 {key}: {str(value)[:100]}...")
                else:
                    print(f"📝 {key}: {value}")
            
            # Pretty print the full response
            print("\n🔍 FULL RESPONSE:")
            print(json.dumps(data, indent=2))
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_backend_response()
