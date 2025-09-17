#!/usr/bin/env python3
"""
Simple version of the Agentic AI application that works without external dependencies
"""

import asyncio
import json
import os
import sys
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleAgent:
    """Simple base agent for demonstration"""
    
    def __init__(self, name: str):
        self.name = name
    
    async def search(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """Simple search implementation"""
        return {
            'agent': self.name,
            'query': query,
            'results': [f"Mock result {i+1} for '{query}' from {self.name}" for i in range(min(3, max_results))],
            'success': True,
            'timestamp': datetime.now().isoformat()
        }
    
    def is_relevant(self, query: str) -> bool:
        """Check if agent is relevant for query"""
        keywords = {
            'FileSystem': ['file', 'folder', 'directory', 'local'],
            'API': ['api', 'http', 'request', 'endpoint'],
            'URL': ['url', 'website', 'web', 'link'],
            'JIRA': ['jira', 'issue', 'ticket', 'bug'],
            'GitHub': ['github', 'repository', 'repo', 'code'],
            'Video': ['video', 'youtube', 'movie'],
            'S3': ['s3', 'bucket', 'aws', 'storage']
        }
        
        agent_keywords = keywords.get(self.name, [])
        return any(keyword in query.lower() for keyword in agent_keywords)

class SimpleOrchestrator:
    """Simple orchestrator for demonstration"""
    
    def __init__(self):
        self.agents = {
            'FileSystem': SimpleAgent('FileSystem'),
            'API': SimpleAgent('API'),
            'URL': SimpleAgent('URL'),
            'JIRA': SimpleAgent('JIRA'),
            'GitHub': SimpleAgent('GitHub'),
            'Video': SimpleAgent('Video'),
            'S3': SimpleAgent('S3')
        }
    
    async def process_query(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """Process a query using relevant agents"""
        start_time = datetime.now()
        
        # Find relevant agents
        relevant_agents = []
        for name, agent in self.agents.items():
            if agent.is_relevant(query):
                relevant_agents.append(name)
        
        # If no specific agents found, use a few default ones
        if not relevant_agents:
            relevant_agents = ['FileSystem', 'API', 'URL']
        
        # Execute searches
        results = []
        for agent_name in relevant_agents:
            try:
                result = await self.agents[agent_name].search(query, max_results)
                results.append(result)
            except Exception as e:
                results.append({
                    'agent': agent_name,
                    'query': query,
                    'error': str(e),
                    'success': False
                })
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        return {
            'query': query,
            'agents_used': relevant_agents,
            'results': results,
            'total_results': sum(len(r.get('results', [])) for r in results if r.get('success')),
            'execution_time': execution_time,
            'summary': f"Searched {len(relevant_agents)} agents and found {sum(len(r.get('results', [])) for r in results if r.get('success'))} results"
        }

async def main():
    """Main function for CLI usage"""
    print("🤖 Simple Agentic AI Workflows")
    print("=" * 50)
    
    orchestrator = SimpleOrchestrator()
    
    if len(sys.argv) > 1:
        # Command line query
        query = ' '.join(sys.argv[1:])
        print(f"Processing query: {query}")
        
        response = await orchestrator.process_query(query)
        
        print(f"\n📊 Results:")
        print(f"Query: {response['query']}")
        print(f"Agents Used: {', '.join(response['agents_used'])}")
        print(f"Total Results: {response['total_results']}")
        print(f"Execution Time: {response['execution_time']:.2f}s")
        print(f"Summary: {response['summary']}")
        
        print(f"\n📋 Detailed Results:")
        for result in response['results']:
            print(f"\n🔍 {result['agent']} Agent:")
            if result.get('success'):
                for i, item in enumerate(result.get('results', []), 1):
                    print(f"  {i}. {item}")
            else:
                print(f"  ❌ Error: {result.get('error')}")
    
    else:
        # Interactive mode
        print("Enter your queries (type 'quit' to exit):")
        
        while True:
            try:
                query = input("\n💬 Query: ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye! 👋")
                    break
                
                if not query:
                    continue
                
                response = await orchestrator.process_query(query)
                
                print(f"\n📊 Results for: {query}")
                print(f"Agents: {', '.join(response['agents_used'])}")
                print(f"Results: {response['total_results']}")
                print(f"Time: {response['execution_time']:.2f}s")
                
                for result in response['results']:
                    if result.get('success'):
                        print(f"\n{result['agent']}: {len(result.get('results', []))} results")
                        for item in result.get('results', [])[:2]:  # Show first 2
                            print(f"  • {item}")
                
            except KeyboardInterrupt:
                print("\nGoodbye! 👋")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")

def create_web_server():
    """Create a simple web server"""
    try:
        from fastapi import FastAPI
        from fastapi.responses import HTMLResponse
        import uvicorn
        
        app = FastAPI(title="Simple Agentic AI Workflows")
        orchestrator = SimpleOrchestrator()
        
        @app.get("/", response_class=HTMLResponse)
        async def root():
            return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Simple Agentic AI Workflows</title>
                <style>
                    body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                    .container { background: #f5f5f5; padding: 20px; border-radius: 10px; }
                    textarea { width: 100%; height: 100px; margin: 10px 0; }
                    button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
                    .results { margin-top: 20px; padding: 20px; background: white; border-radius: 5px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🤖 Simple Agentic AI Workflows</h1>
                    <textarea id="query" placeholder="Enter your query here..."></textarea><br>
                    <button onclick="search()">Search</button>
                    <div id="results" class="results" style="display:none;"></div>
                </div>
                
                <script>
                    async function search() {
                        const query = document.getElementById('query').value;
                        const resultsDiv = document.getElementById('results');
                        
                        if (!query.trim()) return;
                        
                        resultsDiv.style.display = 'block';
                        resultsDiv.innerHTML = 'Processing...';
                        
                        try {
                            const response = await fetch('/search', {
                                method: 'POST',
                                headers: {'Content-Type': 'application/json'},
                                body: JSON.stringify({query: query})
                            });
                            
                            const data = await response.json();
                            
                            let html = `<h3>Results for: "${data.query}"</h3>`;
                            html += `<p>Agents: ${data.agents_used.join(', ')}</p>`;
                            html += `<p>Total Results: ${data.total_results}</p>`;
                            
                            data.results.forEach(result => {
                                html += `<h4>${result.agent} Agent</h4>`;
                                if (result.success) {
                                    result.results.forEach(item => {
                                        html += `<p>• ${item}</p>`;
                                    });
                                } else {
                                    html += `<p style="color: red;">Error: ${result.error}</p>`;
                                }
                            });
                            
                            resultsDiv.innerHTML = html;
                        } catch (error) {
                            resultsDiv.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
                        }
                    }
                </script>
            </body>
            </html>
            """
        
        @app.post("/search")
        async def search(request: dict):
            query = request.get('query', '')
            return await orchestrator.process_query(query)
        
        print("🚀 Starting Simple Agentic AI Workflows Web Server...")
        print("Server will be available at: http://localhost:8000")
        print("Press Ctrl+C to stop")
        
        uvicorn.run(app, host="0.0.0.0", port=8000)
        
    except ImportError:
        print("❌ FastAPI not available. Please install with: python -m pip install fastapi uvicorn")
        print("Or run in CLI mode: python simple_main.py 'your query here'")

if __name__ == "__main__":
    if '--web' in sys.argv:
        create_web_server()
    else:
        asyncio.run(main())
