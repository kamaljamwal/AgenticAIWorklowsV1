from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn
import logging
from orchestrator import AgenticOrchestrator
from models import QueryRequest, WorkflowResponse
from config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Agentic AI Workflows",
    description="Multi-agent system for pulling information from various sources",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator
orchestrator = AgenticOrchestrator()

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main web interface"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Agentic AI Workflows</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }
            .container {
                background: white;
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            h1 {
                color: #4a5568;
                text-align: center;
                margin-bottom: 30px;
                font-size: 2.5em;
            }
            .query-section {
                margin-bottom: 30px;
            }
            textarea {
                width: 100%;
                min-height: 120px;
                padding: 15px;
                border: 2px solid #e2e8f0;
                border-radius: 10px;
                font-size: 16px;
                resize: vertical;
                font-family: inherit;
            }
            textarea:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }
            .controls {
                display: flex;
                gap: 15px;
                align-items: center;
                margin-top: 15px;
                flex-wrap: wrap;
            }
            button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 16px;
                font-weight: 600;
                transition: transform 0.2s, box-shadow 0.2s;
            }
            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }
            button:disabled {
                background: #cbd5e0;
                cursor: not-allowed;
                transform: none;
                box-shadow: none;
            }
            .max-results {
                display: flex;
                align-items: center;
                gap: 10px;
            }
            input[type="number"] {
                width: 80px;
                padding: 8px;
                border: 2px solid #e2e8f0;
                border-radius: 6px;
                font-size: 14px;
            }
            .results {
                margin-top: 30px;
            }
            .loading {
                text-align: center;
                padding: 40px;
                color: #667eea;
                font-size: 18px;
            }
            .spinner {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #667eea;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto 20px;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .result-summary {
                background: #f7fafc;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                border-left: 4px solid #667eea;
            }
            .agent-results {
                margin-bottom: 25px;
            }
            .agent-header {
                background: #667eea;
                color: white;
                padding: 12px 20px;
                border-radius: 8px 8px 0 0;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            .agent-content {
                border: 2px solid #667eea;
                border-top: none;
                border-radius: 0 0 8px 8px;
                padding: 20px;
            }
            .result-item {
                background: #f8f9fa;
                padding: 15px;
                margin-bottom: 15px;
                border-radius: 8px;
                border-left: 3px solid #28a745;
            }
            .result-item:last-child {
                margin-bottom: 0;
            }
            .result-title {
                font-weight: 600;
                color: #2d3748;
                margin-bottom: 8px;
            }
            .result-meta {
                font-size: 14px;
                color: #718096;
                margin-bottom: 10px;
            }
            .result-content {
                color: #4a5568;
                line-height: 1.6;
            }
            .error {
                background: #fed7d7;
                color: #c53030;
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid #e53e3e;
            }
            .agents-info {
                background: #e6fffa;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
            }
            .agents-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 15px;
                margin-top: 15px;
            }
            .agent-card {
                background: white;
                padding: 15px;
                border-radius: 8px;
                border: 1px solid #bee3f8;
            }
            .agent-name {
                font-weight: 600;
                color: #2b6cb0;
                margin-bottom: 5px;
            }
            .agent-desc {
                font-size: 14px;
                color: #4a5568;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Agentic AI Workflows</h1>
            
            <div class="agents-info">
                <h3>Available Data Sources</h3>
                <div class="agents-grid">
                    <div class="agent-card">
                        <div class="agent-name">JIRA</div>
                        <div class="agent-desc">Issues, tickets, projects</div>
                    </div>
                    <div class="agent-card">
                        <div class="agent-name">GitHub</div>
                        <div class="agent-desc">Repositories, PRs, issues</div>
                    </div>
                    <div class="agent-card">
                        <div class="agent-name">API</div>
                        <div class="agent-desc">External HTTP services</div>
                    </div>
                    <div class="agent-card">
                        <div class="agent-name">FileSystem</div>
                        <div class="agent-desc">Local files and folders</div>
                    </div>
                    <div class="agent-card">
                        <div class="agent-name">Video</div>
                        <div class="agent-desc">YouTube, Vimeo content</div>
                    </div>
                    <div class="agent-card">
                        <div class="agent-name">S3</div>
                        <div class="agent-desc">AWS S3 bucket objects</div>
                    </div>
                    <div class="agent-card">
                        <div class="agent-name">URL</div>
                        <div class="agent-desc">Web pages and content</div>
                    </div>
                </div>
            </div>
            
            <div class="query-section">
                <textarea id="queryInput" placeholder="Enter your query in plain English...

Examples:
• Find all high priority bugs in JIRA
• Show me Python repositories on GitHub
• Get content from https://example.com
• Search for tutorial videos about machine learning
• List files in my project directory
• Find documents in S3 bucket containing 'report'"></textarea>
                
                <div class="controls">
                    <button onclick="executeQuery()" id="searchBtn">🔍 Search</button>
                    <div class="max-results">
                        <label for="maxResults">Max Results:</label>
                        <input type="number" id="maxResults" value="10" min="1" max="50">
                    </div>
                    <button onclick="checkHealth()" id="healthBtn">🏥 Health Check</button>
                </div>
            </div>
            
            <div id="results" class="results"></div>
        </div>

        <script>
            async function executeQuery() {
                const query = document.getElementById('queryInput').value.trim();
                const maxResults = parseInt(document.getElementById('maxResults').value);
                const resultsDiv = document.getElementById('results');
                const searchBtn = document.getElementById('searchBtn');
                
                if (!query) {
                    alert('Please enter a query');
                    return;
                }
                
                searchBtn.disabled = true;
                resultsDiv.innerHTML = '<div class="loading"><div class="spinner"></div>Processing your query...</div>';
                
                try {
                    const response = await fetch('/query', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            prompt: query,
                            max_results: maxResults
                        })
                    });
                    
                    const data = await response.json();
                    displayResults(data);
                } catch (error) {
                    resultsDiv.innerHTML = `<div class="error">Error: ${error.message}</div>`;
                } finally {
                    searchBtn.disabled = false;
                }
            }
            
            function displayResults(data) {
                const resultsDiv = document.getElementById('results');
                
                let html = `
                    <div class="result-summary">
                        <h3>📊 Query Summary</h3>
                        <p><strong>Query:</strong> ${data.query}</p>
                        <p><strong>Agents Used:</strong> ${data.agents_used.join(', ')}</p>
                        <p><strong>Total Results:</strong> ${data.total_results}</p>
                        <p><strong>Execution Time:</strong> ${data.execution_time.toFixed(2)}s</p>
                        <p><strong>Summary:</strong> ${data.summary}</p>
                    </div>
                `;
                
                data.results.forEach(result => {
                    html += `<div class="agent-results">`;
                    html += `<div class="agent-header">${result.agent_type} Agent</div>`;
                    html += `<div class="agent-content">`;
                    
                    if (result.success) {
                        if (result.data.length > 0) {
                            result.data.forEach(item => {
                                html += `<div class="result-item">`;
                                html += formatResultItem(item, result.agent_type);
                                html += `</div>`;
                            });
                        } else {
                            html += `<p>No results found</p>`;
                        }
                    } else {
                        html += `<div class="error">Error: ${result.error}</div>`;
                    }
                    
                    html += `</div></div>`;
                });
                
                resultsDiv.innerHTML = html;
            }
            
            function formatResultItem(item, agentType) {
                let html = '';
                
                switch(agentType) {
                    case 'jira':
                        html += `<div class="result-title">${item.key}: ${item.summary}</div>`;
                        html += `<div class="result-meta">Status: ${item.status} | Priority: ${item.priority || 'N/A'} | Assignee: ${item.assignee || 'Unassigned'}</div>`;
                        if (item.description) {
                            html += `<div class="result-content">${item.description.substring(0, 200)}...</div>`;
                        }
                        if (item.url) {
                            html += `<div class="result-meta"><a href="${item.url}" target="_blank">View in JIRA</a></div>`;
                        }
                        break;
                        
                    case 'github':
                        html += `<div class="result-title">${item.name}</div>`;
                        html += `<div class="result-meta">Type: ${item.type} | Author: ${item.author || 'N/A'}</div>`;
                        if (item.description) {
                            html += `<div class="result-content">${item.description}</div>`;
                        }
                        if (item.url) {
                            html += `<div class="result-meta"><a href="${item.url}" target="_blank">View on GitHub</a></div>`;
                        }
                        break;
                        
                    case 'filesystem':
                        html += `<div class="result-title">${item.name}</div>`;
                        html += `<div class="result-meta">Type: ${item.type} | Size: ${item.size || 'N/A'} bytes | Modified: ${item.modified}</div>`;
                        html += `<div class="result-content">Path: ${item.path}</div>`;
                        if (item.content_preview) {
                            html += `<div class="result-content">Preview: ${item.content_preview.substring(0, 200)}...</div>`;
                        }
                        break;
                        
                    case 'video':
                        html += `<div class="result-title">${item.title}</div>`;
                        html += `<div class="result-meta">Duration: ${item.duration || 'N/A'} | Platform: ${item.platform || 'Unknown'}</div>`;
                        if (item.description) {
                            html += `<div class="result-content">${item.description}</div>`;
                        }
                        if (item.url) {
                            html += `<div class="result-meta"><a href="${item.url}" target="_blank">Watch Video</a></div>`;
                        }
                        break;
                        
                    case 's3':
                        html += `<div class="result-title">${item.key}</div>`;
                        html += `<div class="result-meta">Size: ${item.size} bytes | Modified: ${item.last_modified} | Storage: ${item.storage_class}</div>`;
                        html += `<div class="result-content">Bucket: ${item.bucket}</div>`;
                        break;
                        
                    case 'url':
                        html += `<div class="result-title">${item.title || 'Web Content'}</div>`;
                        html += `<div class="result-meta">Status: ${item.status_code} | Type: ${item.content_type}</div>`;
                        html += `<div class="result-content">URL: <a href="${item.url}" target="_blank">${item.url}</a></div>`;
                        if (item.content && item.content.text_content) {
                            html += `<div class="result-content">${item.content.text_content.substring(0, 300)}...</div>`;
                        }
                        break;
                        
                    default:
                        html += `<div class="result-content">${JSON.stringify(item, null, 2)}</div>`;
                }
                
                return html;
            }
            
            async function checkHealth() {
                const resultsDiv = document.getElementById('results');
                const healthBtn = document.getElementById('healthBtn');
                
                healthBtn.disabled = true;
                resultsDiv.innerHTML = '<div class="loading"><div class="spinner"></div>Checking system health...</div>';
                
                try {
                    const response = await fetch('/health');
                    const data = await response.json();
                    
                    let html = `<div class="result-summary">
                        <h3>🏥 System Health Check</h3>
                        <p><strong>Overall Status:</strong> ${data.overall_healthy ? '✅ Healthy' : '❌ Issues Detected'}</p>
                        <p><strong>OpenAI Configured:</strong> ${data.openai_configured ? '✅ Yes' : '❌ No'}</p>
                    </div>`;
                    
                    html += '<div class="agents-grid">';
                    Object.entries(data.agents).forEach(([agent, status]) => {
                        html += `<div class="agent-card">
                            <div class="agent-name">${agent.toUpperCase()}</div>
                            <div class="agent-desc">${status.healthy ? '✅ Healthy' : '❌ Error'}</div>
                            ${status.error ? `<div style="color: red; font-size: 12px;">${status.error}</div>` : ''}
                        </div>`;
                    });
                    html += '</div>';
                    
                    resultsDiv.innerHTML = html;
                } catch (error) {
                    resultsDiv.innerHTML = `<div class="error">Health check failed: ${error.message}</div>`;
                } finally {
                    healthBtn.disabled = false;
                }
            }
            
            // Allow Enter key to submit
            document.getElementById('queryInput').addEventListener('keydown', function(event) {
                if (event.ctrlKey && event.key === 'Enter') {
                    executeQuery();
                }
            });
        </script>
    </body>
    </html>
    """

@app.post("/query", response_model=WorkflowResponse)
async def process_query(request: QueryRequest):
    """Process a natural language query using the agentic workflow"""
    try:
        logger.info(f"Processing query: {request.prompt}")
        response = await orchestrator.process_query(request)
        logger.info(f"Query processed successfully. Total results: {response.total_results}")
        return response
    except Exception as e:
        logger.error(f"Query processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Check the health of all agents"""
    try:
        health_status = await orchestrator.health_check()
        return health_status
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/capabilities")
async def get_capabilities():
    """Get information about agent capabilities"""
    try:
        capabilities = await orchestrator.get_agent_capabilities()
        return capabilities
    except Exception as e:
        logger.error(f"Failed to get capabilities: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agents/{agent_type}/search")
async def search_specific_agent(agent_type: str, request: QueryRequest):
    """Search using a specific agent"""
    try:
        from models import AgentType
        agent_enum = AgentType(agent_type.lower())
        
        if agent_enum not in orchestrator.agents:
            raise HTTPException(status_code=404, detail=f"Agent {agent_type} not found")
        
        agent = orchestrator.agents[agent_enum]
        result = await agent.search(request.prompt, request.max_results)
        
        return result
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid agent type: {agent_type}")
    except Exception as e:
        logger.error(f"Agent search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    logger.info("Starting Agentic AI Workflows server...")
    uvicorn.run(
        "api:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=True,
        log_level=settings.log_level.lower()
    )
