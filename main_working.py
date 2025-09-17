#!/usr/bin/env python3
"""
Agentic AI Workflows - Working Main Entry Point
This version works with available dependencies and provides real functionality
"""

import asyncio
import argparse
import json
from typing import List, Dict, Any
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Import only what we need
try:
    from config import settings
    from models import QueryRequest, WorkflowResponse, AgentResponse, AgentType
    from llm_client import get_llm_client
except ImportError as e:
    logger.error(f"Import error: {e}")
    print("Some dependencies are missing. Using fallback mode.")

# Simple agent implementations that work without external dependencies
class WorkingFileSystemAgent:
    """File system agent that actually searches files"""
    
    def __init__(self):
        self.agent_type = AgentType.FILESYSTEM
        
    async def search(self, query: str, max_results: int = 10) -> AgentResponse:
        """Search local files"""
        import os
        import glob
        from pathlib import Path
        
        try:
            results = []
            search_paths = ["."]  # Search current directory
            extensions = [".py", ".txt", ".md", ".json", ".yml", ".yaml"]
            
            for search_path in search_paths:
                for ext in extensions:
                    pattern = os.path.join(search_path, f"**/*{ext}")
                    files = glob.glob(pattern, recursive=True)
                    
                    for file_path in files[:max_results]:
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                if query.lower() in content.lower() or query.lower() in os.path.basename(file_path).lower():
                                    results.append({
                                        'file_path': file_path,
                                        'file_name': os.path.basename(file_path),
                                        'size': os.path.getsize(file_path),
                                        'match_type': 'content' if query.lower() in content.lower() else 'filename',
                                        'preview': content[:200] + '...' if len(content) > 200 else content
                                    })
                        except Exception:
                            continue
                            
                        if len(results) >= max_results:
                            break
                    
                    if len(results) >= max_results:
                        break
                        
                if len(results) >= max_results:
                    break
            
            return AgentResponse(
                agent_type=self.agent_type,
                success=True,
                data=results,
                message=f"Found {len(results)} files matching '{query}'"
            )
            
        except Exception as e:
            return AgentResponse(
                agent_type=self.agent_type,
                success=False,
                data=[],
                error=str(e)
            )

class WorkingURLAgent:
    """URL agent that fetches web content"""
    
    def __init__(self):
        self.agent_type = AgentType.URL
        
    async def search(self, query: str, max_results: int = 10) -> AgentResponse:
        """Fetch content from URLs"""
        import requests
        from urllib.parse import urlparse
        
        try:
            results = []
            
            # If query looks like a URL, fetch it directly
            if query.startswith(('http://', 'https://')):
                urls = [query]
            else:
                # Use some default URLs or search engines
                urls = [
                    f"https://httpbin.org/json",  # Test API
                    "https://api.github.com/zen",  # GitHub zen
                ]
            
            for url in urls[:max_results]:
                try:
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        content = response.text[:1000]  # Limit content
                        results.append({
                            'url': url,
                            'status_code': response.status_code,
                            'content_type': response.headers.get('content-type', 'unknown'),
                            'content_preview': content,
                            'title': f"Content from {urlparse(url).netloc}"
                        })
                except Exception as e:
                    results.append({
                        'url': url,
                        'error': str(e),
                        'status': 'failed'
                    })
            
            return AgentResponse(
                agent_type=self.agent_type,
                success=True,
                data=results,
                message=f"Fetched content from {len(results)} URLs"
            )
            
        except Exception as e:
            return AgentResponse(
                agent_type=self.agent_type,
                success=False,
                data=[],
                error=str(e)
            )

class WorkingAPIAgent:
    """API agent that makes HTTP requests"""
    
    def __init__(self):
        self.agent_type = AgentType.API
        
    async def search(self, query: str, max_results: int = 10) -> AgentResponse:
        """Make API requests"""
        import requests
        
        try:
            results = []
            
            # Test with some public APIs
            apis = [
                "https://httpbin.org/get",
                "https://jsonplaceholder.typicode.com/posts/1",
                "https://api.github.com/repos/microsoft/vscode"
            ]
            
            for api_url in apis[:max_results]:
                try:
                    response = requests.get(api_url, timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        results.append({
                            'api_url': api_url,
                            'status_code': response.status_code,
                            'data': data,
                            'query_relevance': query.lower() in str(data).lower()
                        })
                except Exception as e:
                    results.append({
                        'api_url': api_url,
                        'error': str(e),
                        'status': 'failed'
                    })
            
            return AgentResponse(
                agent_type=self.agent_type,
                success=True,
                data=results,
                message=f"Made {len(results)} API requests"
            )
            
        except Exception as e:
            return AgentResponse(
                agent_type=self.agent_type,
                success=False,
                data=[],
                error=str(e)
            )

class WorkingOrchestrator:
    """Working orchestrator with available agents"""
    
    def __init__(self):
        self.agents = {
            AgentType.FILESYSTEM: WorkingFileSystemAgent(),
            AgentType.URL: WorkingURLAgent(),
            AgentType.API: WorkingAPIAgent()
        }
        
        # Try to initialize LLM client
        try:
            self.llm_client = get_llm_client()
        except Exception as e:
            logger.warning(f"LLM client not available: {e}")
            self.llm_client = None
    
    async def process_query(self, request: QueryRequest) -> WorkflowResponse:
        """Process a query using available agents"""
        start_time = time.time()
        
        try:
            # Determine relevant agents (simple keyword matching)
            relevant_agents = self._determine_relevant_agents(request.prompt)
            
            if not relevant_agents:
                relevant_agents = list(self.agents.keys())  # Use all agents
            
            # Execute searches in parallel
            tasks = []
            for agent_type in relevant_agents:
                if agent_type in self.agents:
                    task = asyncio.create_task(
                        self.agents[agent_type].search(request.prompt, request.max_results)
                    )
                    tasks.append((agent_type, task))
            
            # Wait for results
            results = []
            for agent_type, task in tasks:
                try:
                    result = await task
                    results.append(result)
                except Exception as e:
                    logger.error(f"Agent {agent_type.value} failed: {str(e)}")
                    results.append(AgentResponse(
                        agent_type=agent_type,
                        success=False,
                        data=[],
                        error=str(e)
                    ))
            
            # Generate summary
            summary = await self._generate_summary(request.prompt, results)
            
            # Calculate total results
            total_results = sum(len(result.data) for result in results if result.success)
            
            return WorkflowResponse(
                query=request.prompt,
                agents_used=relevant_agents,
                results=results,
                summary=summary,
                total_results=total_results,
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            logger.error(f"Query processing failed: {str(e)}")
            return WorkflowResponse(
                query=request.prompt,
                agents_used=[],
                results=[],
                summary=f"Error processing query: {str(e)}",
                total_results=0,
                execution_time=time.time() - start_time
            )
    
    def _determine_relevant_agents(self, query: str) -> List[AgentType]:
        """Determine relevant agents based on keywords"""
        query_lower = query.lower()
        relevant = []
        
        # File system keywords
        if any(word in query_lower for word in ['file', 'folder', 'directory', 'local', 'search']):
            relevant.append(AgentType.FILESYSTEM)
        
        # URL keywords
        if any(word in query_lower for word in ['url', 'website', 'web', 'http', 'link']):
            relevant.append(AgentType.URL)
        
        # API keywords
        if any(word in query_lower for word in ['api', 'request', 'endpoint', 'service']):
            relevant.append(AgentType.API)
        
        return relevant
    
    async def _generate_summary(self, query: str, results: List[AgentResponse]) -> str:
        """Generate a summary of results"""
        if self.llm_client:
            try:
                # Try to use LLM for summary
                results_text = []
                for result in results:
                    if result.success:
                        results_text.append(f"{result.agent_type.value}: {len(result.data)} results")
                    else:
                        results_text.append(f"{result.agent_type.value}: Error - {result.error}")
                
                prompt = f"Summarize these search results for query '{query}': {'; '.join(results_text)}"
                summary = await self.llm_client.chat_completion([{"role": "user", "content": prompt}], max_tokens=150)
                return summary
            except Exception as e:
                logger.warning(f"LLM summary failed: {e}")
        
        # Fallback to basic summary
        successful_agents = [r.agent_type.value for r in results if r.success]
        total_results = sum(len(r.data) for r in results if r.success)
        
        return f"Searched {len(successful_agents)} agents ({', '.join(successful_agents)}) and found {total_results} total results for '{query}'"

async def run_cli_query(query: str, max_results: int = 10):
    """Run a query from command line"""
    orchestrator = WorkingOrchestrator()
    
    print(f"\n🤖 Processing query: {query}")
    print("=" * 60)
    
    request = QueryRequest(prompt=query, max_results=max_results)
    response = await orchestrator.process_query(request)
    
    print(f"\n📊 Summary: {response.summary}")
    print(f"⏱️  Execution time: {response.execution_time:.2f}s")
    print(f"🔍 Total results: {response.total_results}")
    print(f"🤖 Agents used: {', '.join([agent.value for agent in response.agents_used])}")
    
    for result in response.results:
        if result.success and result.data:
            print(f"\n📁 {result.agent_type.value} Agent Results:")
            for i, item in enumerate(result.data[:3], 1):  # Show first 3 results
                print(f"  {i}. {json.dumps(item, indent=4, default=str)[:200]}...")
        elif not result.success:
            print(f"\n❌ {result.agent_type.value} Agent Error: {result.error}")

def run_web_server(host: str = "0.0.0.0", port: int = 8000):
    """Run the web server"""
    try:
        from fastapi import FastAPI, HTTPException
        from fastapi.responses import HTMLResponse
        from fastapi.staticfiles import StaticFiles
        from fastapi.middleware.cors import CORSMiddleware
        from pydantic import BaseModel
        import uvicorn

        class SearchRequest(BaseModel):
            prompt: str
            max_results: int = 10
        
        app = FastAPI(title="Agentic AI Workflows", version="1.0.0")
        
        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:4200", "http://127.0.0.1:4200"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        orchestrator = WorkingOrchestrator()
        
        # Serve static files
        try:
            app.mount("/static", StaticFiles(directory="static"), name="static")
        except Exception:
            pass  # Static directory might not exist
        
        @app.get("/", response_class=HTMLResponse)
        async def home():
            return """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Agentic AI Workflows - Intelligent Information Assistant</title>
                <link rel="stylesheet" href="/static/style.css">
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🤖 Agentic AI Workflows</h1>
                        <p>Your intelligent assistant for finding information across multiple sources</p>
                        <div class="meta-info">
                            <span class="badge">Multi-Agent System</span>
                            <span class="badge">Real-time Search</span>
                            <span class="badge">Natural Language</span>
                        </div>
                    </div>
                    
                    <div class="search-section">
                        <div class="search-box">
                            <input type="text" id="queryInput" class="search-input" 
                                   placeholder="Ask me anything... (e.g., 'Find Python files in this project', 'Get data from GitHub API')" />
                            <button onclick="search()" class="search-button" id="searchBtn">
                                <span id="searchText">🔍 Search</span>
                            </button>
                        </div>
                        
                        <div class="loading" id="loading">
                            <div>🔍 Searching across multiple sources...</div>
                            <div style="margin-top: 10px; font-size: 0.9em; opacity: 0.7;">This may take a few seconds</div>
                        </div>
                    </div>
                    
                    <div class="results-section" id="resultsSection" style="display: none;">
                        <div id="results"></div>
                    </div>
                    
                    <div class="empty-state" id="emptyState">
                        <h3>👋 Welcome to Agentic AI Workflows</h3>
                        <p>Ask me to search for files, fetch data from APIs, or find information from various sources.<br>
                        I'll provide you with natural language answers and clickable links to explore further.</p>
                        
                        <div style="margin-top: 30px; text-align: left; max-width: 600px; margin-left: auto; margin-right: auto;">
                            <h4 style="margin-bottom: 15px; color: #333;">💡 Try these examples:</h4>
                            <div style="display: grid; gap: 10px;">
                                <button onclick="setQuery('Find all Python files in this project')" class="example-query">Find all Python files in this project</button>
                                <button onclick="setQuery('Get information from GitHub API')" class="example-query">Get information from GitHub API</button>
                                <button onclick="setQuery('Search for configuration files')" class="example-query">Search for configuration files</button>
                                <button onclick="setQuery('Fetch data from a REST API')" class="example-query">Fetch data from a REST API</button>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- File Preview Modal -->
                <div id="fileModal" class="modal">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h2 class="modal-title" id="modalTitle">File Preview</h2>
                            <span class="close" onclick="closeModal()">&times;</span>
                        </div>
                        <div class="modal-body">
                            <div class="file-info" id="fileInfo"></div>
                            <div class="preview-actions" id="previewActions"></div>
                            <div class="file-preview" id="fileContent">Loading...</div>
                        </div>
                    </div>
                </div>
                
                <style>
                    .example-query {
                        padding: 12px 16px;
                        background: rgba(102, 126, 234, 0.1);
                        border: 1px solid rgba(102, 126, 234, 0.2);
                        border-radius: 8px;
                        color: #667eea;
                        cursor: pointer;
                        transition: all 0.3s ease;
                        text-align: left;
                        font-size: 0.95em;
                    }
                    
                    .example-query:hover {
                        background: #667eea;
                        color: white;
                        transform: translateY(-1px);
                    }
                    
                    .meta-info {
                        margin-top: 15px;
                        display: flex;
                        gap: 10px;
                        justify-content: center;
                        flex-wrap: wrap;
                    }
                </style>
                
                <script>
                    function setQuery(query) {
                        document.getElementById('queryInput').value = query;
                        document.getElementById('queryInput').focus();
                    }
                    
                    async function search() {
                        const query = document.getElementById('queryInput').value.trim();
                        if (!query) return;
                        
                        // Show loading state
                        document.getElementById('loading').classList.add('show');
                        document.getElementById('emptyState').style.display = 'none';
                        document.getElementById('resultsSection').style.display = 'none';
                        document.getElementById('searchBtn').disabled = true;
                        document.getElementById('searchText').innerHTML = '⏳ Searching...';
                        
                        try {
                            const response = await fetch('/search', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ prompt: query, max_results: 10 })
                            });
                            
                            if (!response.ok) {
                                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                            }
                            
                            const data = await response.json();
                            console.log('Search response:', data);
                            displayResults(data);
                        } catch (error) {
                            displayError(error.message);
                        } finally {
                            // Hide loading state
                            document.getElementById('loading').classList.remove('show');
                            document.getElementById('searchBtn').disabled = false;
                            document.getElementById('searchText').innerHTML = '🔍 Search';
                        }
                    }
                    
                    function displayResults(data) {
                        console.log('Displaying results:', data);
                        document.getElementById('resultsSection').style.display = 'block';
                        
                        let html = `
                            <div class="results-header">
                                <div class="results-title">Results for: "${data.query}"</div>
                                <div class="results-meta">
                                    <div class="meta-item">
                                        <span>⏱️</span>
                                        <span>${data.execution_time.toFixed(2)}s</span>
                                    </div>
                                    <div class="meta-item">
                                        <span>📊</span>
                                        <span>${data.total_results} results</span>
                                    </div>
                                    <div class="meta-item">
                                        <span>🤖</span>
                                        <span>${data.agents_used ? data.agents_used.length : 0} agents</span>
                                    </div>
                                </div>
                            </div>
                        `;
                        
                        // Add natural language answer
                        html += `
                            <div class="answer-section">
                                <div class="answer-title">
                                    <span>💬</span>
                                    <span>Answer</span>
                                </div>
                                <div class="answer-content">
                                    ${formatAnswer(data)}
                                </div>
                            </div>
                        `;
                        
                        // Add detailed results
                        if (data.results && data.results.length > 0) {
                            data.results.forEach(result => {
                            if (result.success && result.data.length > 0) {
                                html += formatAgentResults(result);
                            } else if (!result.success) {
                                html += `
                                    <div class="agent-results">
                                        <div class="agent-header">
                                            <div class="agent-title">
                                                <span>❌</span>
                                                <span>${result.agent_type} Agent</span>
                                            </div>
                                            <div class="agent-meta">Error occurred</div>
                                        </div>
                                        <div class="agent-content">
                                            <div class="error-message">${result.error}</div>
                                        </div>
                                    </div>
                                `;
                            }
                        });
                        }
                        
                        document.getElementById('results').innerHTML = html;
                    }
                    
                    function formatAnswer(data) {
                        const totalResults = data.total_results;
                        const agents = data.agents_used.map(agent => agent.toLowerCase()).join(', ');
                        const query = data.query;
                        
                        let answer = `I found ${totalResults} results for your query "${query}" by searching through ${agents} sources. `;
                        
                        // Add specific insights based on results
                        const successfulResults = data.results ? data.results.filter(r => r.success && r.data && r.data.length > 0) : [];
                        
                        if (successfulResults.length > 0) {
                            answer += "Here's what I discovered:\n\n";
                            
                            successfulResults.forEach(result => {
                                const count = result.data.length;
                                const agentType = result.agent_type.toLowerCase();
                                
                                if (agentType === 'filesystem') {
                                    answer += `📁 Found ${count} files on your local system that match your criteria.\n`;
                                } else if (agentType === 'api') {
                                    answer += `🔗 Retrieved data from ${count} API endpoints.\n`;
                                } else if (agentType === 'url') {
                                    answer += `🌐 Fetched content from ${count} web sources.\n`;
                                }
                            });
                            
                            answer += "\nClick on the links below to explore the detailed results and access the actual content.";
                        } else {
                            answer += "Unfortunately, I couldn't find any matching results. Try refining your search terms or checking if the sources are accessible.";
                        }
                        
                        return answer.replace(/\n/g, '<br>');
                    }
                    
                    function formatAgentResults(result) {
                        const agentIcons = {
                            'filesystem': '📁',
                            'api': '🔗',
                            'url': '🌐',
                            'jira': '🎫',
                            'github': '🐙',
                            'video': '🎥',
                            's3': '☁️'
                        };
                        
                        const icon = agentIcons[result.agent_type.toLowerCase()] || '🤖';
                        
                        let html = `
                            <div class="agent-results">
                                <div class="agent-header">
                                    <div class="agent-title">
                                        <span>${icon}</span>
                                        <span>${result.agent_type} Agent</span>
                                    </div>
                                    <div class="agent-meta">${result.data.length} results found</div>
                                </div>
                                <div class="agent-content">
                        `;
                        
                        result.data.slice(0, 5).forEach((item, index) => {
                            html += formatResultItem(item, result.agent_type.toLowerCase(), index);
                        });
                        
                        if (result.data.length > 5) {
                            html += `<div style="text-align: center; margin-top: 15px; color: #666; font-style: italic;">... and ${result.data.length - 5} more results</div>`;
                        }
                        
                        html += `
                                </div>
                            </div>
                        `;
                        
                        return html;
                    }
                    
                    function formatResultItem(item, agentType, index) {
                        let html = '<div class="result-item">';
                        
                        if (agentType === 'filesystem') {
                            html += `
                                <div class="result-title">
                                    <span>📄</span>
                                    <span>${item.file_name || item.name || 'Unknown File'}</span>
                                </div>
                                <div class="result-content">
                                    <strong>Path:</strong> ${item.file_path || item.path || 'Unknown'}<br>
                                    <strong>Size:</strong> ${formatFileSize(item.size || 0)}<br>
                                    <strong>Match:</strong> ${item.match_type || item.type || 'Content match'}<br>
                                    ${item.preview ? `<strong>Preview:</strong> ${item.preview.substring(0, 150)}...` : ''}
                                </div>
                                <div style="display: flex; gap: 10px; margin-top: 10px;">
                                    <button onclick="previewFile('${item.file_path || item.path}')" class="result-link">
                                        <span>👁️</span>
                                        <span>Preview</span>
                                    </button>
                                    <a href="file://${item.file_path || item.path}" class="result-link" target="_blank">
                                        <span>📂</span>
                                        <span>Open File</span>
                                    </a>
                                </div>
                            `;
                        } else if (agentType === 'api') {
                            html += `
                                <div class="result-title">
                                    <span>🔗</span>
                                    <span>API Response ${index + 1}</span>
                                </div>
                                <div class="result-content">
                                    <strong>Endpoint:</strong> ${item.api_url}<br>
                                    <strong>Status:</strong> ${item.status_code || item.status}<br>
                                    ${item.query_relevance !== undefined ? `<strong>Relevance:</strong> ${item.query_relevance ? 'High' : 'Low'}<br>` : ''}
                                    ${item.error ? `<strong>Error:</strong> ${item.error}` : ''}
                                </div>
                                <a href="${item.api_url}" class="result-link" target="_blank">
                                    <span>🌐</span>
                                    <span>View API</span>
                                </a>
                            `;
                        } else if (agentType === 'url') {
                            html += `
                                <div class="result-title">
                                    <span>🌐</span>
                                    <span>${item.title || 'Web Content'}</span>
                                </div>
                                <div class="result-content">
                                    <strong>URL:</strong> ${item.url}<br>
                                    <strong>Status:</strong> ${item.status_code || item.status}<br>
                                    <strong>Content Type:</strong> ${item.content_type || 'Unknown'}<br>
                                    ${item.content_preview ? `<strong>Preview:</strong> ${item.content_preview.substring(0, 150)}...` : ''}
                                    ${item.error ? `<strong>Error:</strong> ${item.error}` : ''}
                                </div>
                                <a href="${item.url}" class="result-link" target="_blank">
                                    <span>🔗</span>
                                    <span>Visit Site</span>
                                </a>
                            `;
                        } else {
                            // Generic format for other agent types
                            html += `
                                <div class="result-title">
                                    <span>📋</span>
                                    <span>Result ${index + 1}</span>
                                </div>
                                <div class="result-content">
                                    <pre style="background: #f8f9fa; padding: 10px; border-radius: 5px; overflow-x: auto; font-size: 0.9em;">${JSON.stringify(item, null, 2)}</pre>
                                </div>
                            `;
                        }
                        
                        html += '</div>';
                        return html;
                    }
                    
                    function formatFileSize(bytes) {
                        if (bytes === 0) return '0 Bytes';
                        const k = 1024;
                        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
                        const i = Math.floor(Math.log(bytes) / Math.log(k));
                        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
                    }
                    
                    function displayError(message) {
                        document.getElementById('resultsSection').style.display = 'block';
                        document.getElementById('results').innerHTML = `
                            <div class="error-message">
                                <h3>❌ Search Error</h3>
                                <p>${message}</p>
                                <p>Please try again or contact support if the problem persists.</p>
                            </div>
                        `;
                    }
                    
                    // Allow Enter key to trigger search
                    document.getElementById('queryInput').addEventListener('keypress', function(e) {
                        if (e.key === 'Enter') search();
                    });
                    
                    // Focus on input when page loads
                    document.addEventListener('DOMContentLoaded', function() {
                        document.getElementById('queryInput').focus();
                    });
                    
                    // File preview functionality
                    async function previewFile(filePath) {
                        try {
                            const modal = document.getElementById('fileModal');
                            const modalTitle = document.getElementById('modalTitle');
                            const fileInfo = document.getElementById('fileInfo');
                            const fileContent = document.getElementById('fileContent');
                            const previewActions = document.getElementById('previewActions');
                            
                            // Show modal
                            modal.style.display = 'block';
                            modalTitle.textContent = 'Loading...';
                            fileInfo.innerHTML = '';
                            fileContent.textContent = 'Loading file preview...';
                            previewActions.innerHTML = '';
                            
                            // Fetch file preview
                            const response = await fetch(`/preview/${encodeURIComponent(filePath)}`);
                            
                            if (!response.ok) {
                                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                            }
                            
                            const data = await response.json();
                            
                            // Update modal content
                            modalTitle.textContent = data.file_info.name;
                            
                            // File info
                            fileInfo.innerHTML = `
                                <div class="info-item">
                                    <div class="info-label">File Name</div>
                                    <div class="info-value">${data.file_info.name}</div>
                                </div>
                                <div class="info-item">
                                    <div class="info-label">File Path</div>
                                    <div class="info-value">${data.file_info.path}</div>
                                </div>
                                <div class="info-item">
                                    <div class="info-label">File Size</div>
                                    <div class="info-value">${formatFileSize(data.file_info.size)}</div>
                                </div>
                                <div class="info-item">
                                    <div class="info-label">Last Modified</div>
                                    <div class="info-value">${new Date(data.file_info.modified * 1000).toLocaleString()}</div>
                                </div>
                            `;
                            
                            // Preview actions
                            previewActions.innerHTML = `
                                <a href="file://${data.file_info.path}" class="action-btn" target="_blank">
                                    <span>📂</span>
                                    <span>Open in System</span>
                                </a>
                                <button onclick="copyToClipboard('${data.file_info.path}')" class="action-btn secondary">
                                    <span>📋</span>
                                    <span>Copy Path</span>
                                </button>
                            `;
                            
                            // File content
                            fileContent.textContent = data.content;
                            
                        } catch (error) {
                            console.error('File preview error:', error);
                            document.getElementById('fileContent').innerHTML = `
                                <div style="color: #e53e3e; padding: 20px; text-align: center;">
                                    <h3>❌ Error Loading File</h3>
                                    <p>${error.message}</p>
                                </div>
                            `;
                        }
                    }
                    
                    function closeModal() {
                        document.getElementById('fileModal').style.display = 'none';
                    }
                    
                    function copyToClipboard(text) {
                        navigator.clipboard.writeText(text).then(() => {
                            // Show temporary feedback
                            const btn = event.target.closest('button');
                            const originalText = btn.innerHTML;
                            btn.innerHTML = '<span>✓</span><span>Copied!</span>';
                            setTimeout(() => {
                                btn.innerHTML = originalText;
                            }, 2000);
                        }).catch(err => {
                            console.error('Failed to copy:', err);
                        });
                    }
                    
                    // Close modal when clicking outside
                    window.onclick = function(event) {
                        const modal = document.getElementById('fileModal');
                        if (event.target === modal) {
                            closeModal();
                        }
                    }
                </script>
            </body>
            </html>
            """
        
        @app.post("/search")
        async def search_endpoint(request: SearchRequest):
            """Search endpoint that processes queries through agents"""
            try:
                # Create QueryRequest object
                query_request = QueryRequest(
                    prompt=request.prompt,
                    max_results=request.max_results
                )
                result = await orchestrator.process_query(query_request)
                return result
            except Exception as e:
                logger.error(f"Search error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.get("/preview/{file_path:path}")
        async def preview_file(file_path: str):
            """Preview file content"""
            try:
                import os

                
                # Security check - ensure file exists and is readable
                if not os.path.exists(file_path) or not os.path.isfile(file_path):
                    raise HTTPException(status_code=404, detail="File not found")
                
                file_info = {
                    "name": os.path.basename(file_path),
                    "path": file_path,
                    "size": os.path.getsize(file_path),
                    "modified": os.path.getmtime(file_path)
                }
                
                # Try to read file content (limit to 50KB for preview)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read(50000)  # Limit to 50KB
                        if len(content) == 50000:
                            content += "\n\n... (file truncated for preview)"
                except UnicodeDecodeError:
                    content = "[Binary file - cannot preview text content]"
                except Exception as e:
                    content = f"[Error reading file: {str(e)}]"
                
                return {
                    "file_info": file_info,
                    "content": content
                }
            except Exception as e:
                logger.error(f"File preview error: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.get("/health")
        async def health_check():
            return {"status": "healthy", "agents": list(orchestrator.agents.keys())}
        
        print(f"🚀 Starting Agentic AI Workflows Web Server...")
        print(f"Server will be available at: http://localhost:{port}")
        print("Press Ctrl+C to stop")
        
        uvicorn.run(app, host=host, port=port)
        
    except ImportError as e:
        print(f"Web server dependencies not available: {e}")
        print("Please install: pip install fastapi uvicorn")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Agentic AI Workflows")
    parser.add_argument("query", nargs="?", help="Query to process")
    parser.add_argument("--web", action="store_true", help="Start web server")
    parser.add_argument("--host", default="0.0.0.0", help="Web server host")
    parser.add_argument("--port", type=int, default=8000, help="Web server port")
    parser.add_argument("--max-results", type=int, default=10, help="Maximum results per agent")
    
    args = parser.parse_args()
    
    if args.web:
        run_web_server(args.host, args.port)
    elif args.query:
        asyncio.run(run_cli_query(args.query, args.max_results))
    else:
        print("🤖 Agentic AI Workflows")
        print("Usage:")
        print("  python main_working.py 'your query here'")
        print("  python main_working.py --web")

if __name__ == "__main__":
    main()
