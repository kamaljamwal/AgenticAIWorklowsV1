#!/usr/bin/env python3
"""
Test script to verify Angular frontend and FastAPI backend integration
"""
import requests
import json
import time

def test_backend_health():
    """Test backend health endpoint"""
    try:
        response = requests.get("http://localhost:8002/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend Health Check: PASSED")
            print(f"   Status: {data.get('status')}")
            print(f"   Agents: {data.get('agents')}")
            return True
        else:
            print(f"❌ Backend Health Check: FAILED (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Backend Health Check: ERROR - {e}")
        return False

def test_search_endpoint():
    """Test search endpoint with a sample query"""
    try:
        payload = {
            "prompt": "What files are in the project?",
            "max_results": 5
        }
        
        print("\n🔍 Testing Search Endpoint...")
        print(f"   Query: {payload['prompt']}")
        
        response = requests.post(
            "http://localhost:8001/search",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Search Endpoint: PASSED")
            print(f"   Query: {data.get('query')}")
            print(f"   Agents Used: {data.get('agents_used')}")
            print(f"   Results Count: {len(data.get('results', []))}")
            
            # Show first result as example
            results = data.get('results', [])
            if results:
                first_result = results[0]
                print(f"   Sample Result: {first_result.get('title', 'N/A')}")
                print(f"   Agent: {first_result.get('agent', 'N/A')}")
            
            return True
        else:
            print(f"❌ Search Endpoint: FAILED (Status: {response.status_code})")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Search Endpoint: ERROR - {e}")
        return False

def test_frontend_availability():
    """Test if Angular frontend is accessible"""
    try:
        response = requests.get("http://localhost:4200")
        if response.status_code == 200:
            print("✅ Frontend Availability: PASSED")
            print("   Angular app is accessible at http://localhost:4200")
            return True
        else:
            print(f"❌ Frontend Availability: FAILED (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Frontend Availability: ERROR - {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Agentic AI Workflows - Frontend & Backend Integration")
    print("=" * 70)
    
    # Test backend health
    backend_healthy = test_backend_health()
    
    # Test frontend availability
    frontend_available = test_frontend_availability()
    
    # Test search functionality
    search_working = test_search_endpoint()
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    all_passed = backend_healthy and frontend_available and search_working
    
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("\n✨ Your Agentic AI Workflows application is fully functional!")
        print("   • Backend API: http://localhost:8002")
        print("   • Frontend UI: http://localhost:4200")
        print("   • Ready for user queries and agent processing")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
    
    return all_passed

if __name__ == "__main__":
    main()
