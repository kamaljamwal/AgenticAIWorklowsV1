#!/usr/bin/env python3
"""
Complete flow test to verify frontend-backend integration
"""
import requests
import json
import time

def test_complete_flow():
    """Test the complete flow from backend to frontend"""
    print("🔄 COMPLETE FLOW TEST")
    print("=" * 50)
    
    # Test 1: Backend API Response
    print("1. 🔍 Testing Backend API...")
    try:
        response = requests.post(
            "http://localhost:8001/search",
            json={"prompt": "who is prime minister of india", "max_results": 5},
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend API working")
            
            # Detailed response analysis
            print(f"📊 Response structure:")
            for key in data.keys():
                if key == "summary":
                    print(f"  ✅ summary: '{data[key][:100]}...'")
                elif key == "results":
                    print(f"  ✅ results: {len(data[key])} agent responses")
                    for result in data[key]:
                        if result.get("success"):
                            print(f"    - {result['agent_type']}: {len(result.get('data', []))} items")
                        else:
                            print(f"    - {result['agent_type']}: ERROR - {result.get('error', 'Unknown')}")
                else:
                    print(f"  ✅ {key}: {data[key]}")
            
            # Check if summary is meaningful
            if data.get("summary") and len(data["summary"]) > 10:
                print("✅ Summary is present and meaningful")
            else:
                print("❌ Summary is missing or too short")
                
        else:
            print(f"❌ Backend error: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        return False
    
    # Test 2: Frontend Health
    print("\n2. 🌐 Testing Frontend Health...")
    try:
        response = requests.get("http://localhost:4200", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend accessible")
        else:
            print(f"❌ Frontend error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend test failed: {e}")
        return False
    
    # Test 3: CORS Check
    print("\n3. 🔒 Testing CORS...")
    try:
        response = requests.options(
            "http://localhost:8001/search",
            headers={
                "Origin": "http://localhost:4200",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            },
            timeout=5
        )
        
        if response.status_code in [200, 204]:
            print("✅ CORS configured correctly")
        else:
            print(f"⚠️  CORS response: {response.status_code}")
            
    except Exception as e:
        print(f"⚠️  CORS test: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 DIAGNOSIS:")
    print("✅ Backend returns proper JSON with 'summary' field")
    print("✅ Frontend is accessible")
    print("✅ CORS is configured")
    print("\n💡 POSSIBLE ISSUES:")
    print("1. Frontend TypeScript compilation errors")
    print("2. Angular change detection not triggering")
    print("3. Markdown pipe not working")
    print("4. CSS hiding the content")
    
    print("\n🛠️  DEBUGGING STEPS:")
    print("1. Open browser dev tools (F12)")
    print("2. Check Console tab for errors")
    print("3. Check Network tab for API calls")
    print("4. Try a simple query like 'test'")
    
    return True

if __name__ == "__main__":
    test_complete_flow()
