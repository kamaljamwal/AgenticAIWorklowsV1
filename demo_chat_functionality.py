#!/usr/bin/env python3
"""
Demo script showing the complete Agentic AI Workflows functionality
"""
import requests
import json
import time

def demo_search_query(query):
    """Demonstrate a search query through the backend API"""
    print(f"\n🔍 Demo Query: '{query}'")
    print("-" * 50)
    
    try:
        payload = {
            "prompt": query,
            "max_results": 3
        }
        
        print("📤 Sending request to backend...")
        start_time = time.time()
        
        response = requests.post(
            "http://localhost:8001/search",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        end_time = time.time()
        response_time = round((end_time - start_time) * 1000, 2)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response received in {response_time}ms")
            print(f"🤖 Agents used: {', '.join(data.get('agents_used', []))}")
            print(f"📊 Results found: {len(data.get('results', []))}")
            
            # Display results
            results = data.get('results', [])
            for i, result in enumerate(results[:3], 1):
                print(f"\n   {i}. {result.get('title', 'Untitled')}")
                print(f"      Agent: {result.get('agent', 'Unknown')}")
                print(f"      Type: {result.get('type', 'Unknown')}")
                if result.get('content'):
                    content_preview = result['content'][:100] + "..." if len(result['content']) > 100 else result['content']
                    print(f"      Preview: {content_preview}")
            
            # Show summary if available
            if data.get('summary'):
                print(f"\n💡 AI Summary:")
                summary_preview = data['summary'][:200] + "..." if len(data['summary']) > 200 else data['summary']
                print(f"   {summary_preview}")
                
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Run demo queries"""
    print("🎯 AGENTIC AI WORKFLOWS - CHAT FUNCTIONALITY DEMO")
    print("=" * 60)
    print("This demo shows what happens when you type queries in the Angular frontend")
    print("and how the backend processes them through multiple AI agents.")
    print("=" * 60)
    
    # Demo queries that showcase different agents
    demo_queries = [
        "What Python files are in this project?",
        "Show me the configuration files",
        "Find any documentation or README files"
    ]
    
    for query in demo_queries:
        demo_search_query(query)
        time.sleep(1)  # Brief pause between queries
    
    print("\n" + "=" * 60)
    print("🎉 DEMO COMPLETE!")
    print("=" * 60)
    print("✨ This is exactly what happens when you:")
    print("   1. Type a question in the Angular chat interface")
    print("   2. Click the blue send button (➤)")
    print("   3. The frontend sends the query to the backend")
    print("   4. Multiple AI agents process your request")
    print("   5. Results are formatted and displayed in the chat")
    print("\n🌐 Try it yourself at: http://localhost:4200")
    print("🔧 Backend API docs at: http://localhost:8001/docs")

if __name__ == "__main__":
    main()
