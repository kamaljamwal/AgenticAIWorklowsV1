#!/usr/bin/env python3
"""
Simple test to verify the system is working
"""
import requests

def test_simple():
    """Simple test"""
    print("🧪 SIMPLE TEST")
    print("=" * 30)
    
    try:
        response = requests.post(
            "http://localhost:8002/search",
            json={"prompt": "hello world", "max_results": 3},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend working")
            print(f"Summary: {data.get('summary', 'No summary')[:100]}...")
        else:
            print(f"❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    test_simple()
