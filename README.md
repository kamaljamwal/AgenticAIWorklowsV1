# 🤖 Agentic AI Workflows

A comprehensive multi-agent system that can pull information from various sources based on natural language prompts. The system automatically determines which agents to use and processes queries across multiple data sources simultaneously.

## 🌟 Features

- **Multi-Agent Architecture**: 7 specialized agents for different data sources
- **🆓 Multiple LLM Providers**: Support for 9 providers including **6 FREE options**!
  - **Free**: **Google Gemini** (recommended), Ollama, Hugging Face, Together AI, Replicate, Local OpenAI servers
  - **Paid**: OpenAI, AWS Bedrock, GROQ
- **Natural Language Processing**: Query in plain English
- **Content-Based Search**: Extracts and indexes content for accurate question answering
- **Parallel Processing**: Agents work simultaneously for faster results
- **Modern Angular Frontend**: Professional chat interface with real-time updates
- **CLI Support**: Command-line interface for automation
- **Health Monitoring**: Built-in health checks for all agents
- **Extensible**: Easy to add new agents and data sources

## 🔧 Available Agents

| Agent | Description | Keywords |
|-------|-------------|----------|
| **JIRA** | Search issues, tickets, projects | jira, issue, ticket, bug, story, task |
| **GitHub** | Search repositories, PRs, issues | github, repository, pull request, commit, code |
| **API** | Make HTTP requests to external services | api, http, rest, endpoint, service |
| **FileSystem** | Search local files and directories | file, folder, directory, local, disk |
| **Video** | Search video content (YouTube, Vimeo) | video, youtube, vimeo, movie, clip |
| **S3** | Search AWS S3 bucket objects | s3, bucket, aws, cloud storage |
| **URL** | Fetch and parse web content | url, website, web page, link, scrape |

## 🚀 Quick Start

> **Quick Demo**: If you want to try the application immediately without setting up external APIs, use the simple version:
> ```bash
> python simple_main.py "search for Python files"
> python simple_main.py --web
> ```

### 1. Installation

#### Option A: Automatic Setup (Recommended)
```bash
# Run the setup script
python setup.py
```

#### Option B: Manual Installation
```bash
# Install minimal dependencies
python -m pip install -r requirements_minimal.txt

# Or install all dependencies
python -m pip install -r requirements.txt
```

#### Option C: Windows Users
```bash
# Double-click setup.bat or run:
setup.bat
```

### 2. Configuration

Copy the example environment file and configure your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your API keys and credentials:

```env
# LLM Provider Configuration (choose one: openai, aws, groq)
LLM_PROVIDER=openai

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo

# AWS Bedrock Configuration (for LLM_PROVIDER=aws)
AWS_BEDROCK_REGION=us-east-1
AWS_BEDROCK_MODEL=anthropic.claude-3-sonnet-20240229-v1:0

# GROQ Configuration (for LLM_PROVIDER=groq)
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama3-8b-8192

# JIRA Configuration
JIRA_SERVER=https://your-company.atlassian.net
JIRA_EMAIL=your-email@company.com
JIRA_API_TOKEN=your_jira_api_token

# GitHub Configuration
GITHUB_TOKEN=your_github_personal_access_token

# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-s3-bucket-name
```

### 3. Run the Application

#### Web Interface (Recommended)
```bash
# Full version (requires all dependencies)
python main.py serve

# Simple version (minimal dependencies)
python simple_main.py --web
```
Then open http://localhost:8000 in your browser.

#### Command Line Interface
```bash
# Full version
python main.py query "Find all high priority bugs in JIRA"
python main.py interactive
python main.py health

# Simple version (works without external APIs)
python simple_main.py "Find files in my project"
python simple_main.py  # Interactive mode
```

## 💡 Example Queries

### JIRA Queries
- "Find all high priority bugs assigned to me"
- "Show open issues in project ABC"
- "List all stories in the current sprint"

### GitHub Queries
- "Find Python repositories with machine learning"
- "Show recent pull requests in my organization"
- "Search for issues labeled 'bug' in repository XYZ"

### File System Queries
- "Find all Python files in my project"
- "Search for configuration files containing 'database'"
- "List all log files modified today"

### Video Queries
- "Find tutorial videos about Docker"
- "Search for Python programming courses on YouTube"
- "Get information about video https://youtube.com/watch?v=..."

### S3 Queries
- "Find all PDF files in my S3 bucket"
- "List objects containing 'report' in the key"
- "Show recent uploads to bucket 'my-data'"

### URL Queries
- "Get content from https://example.com"
- "Scrape data from https://news.ycombinator.com"
- "Extract text from multiple URLs"

### API Queries
- "Call GitHub API to get user information"
- "Make a GET request to https://api.example.com/data"
- "Fetch weather data from OpenWeatherMap API"

## 🏗️ Architecture

```
┌─────────────────┐
│   Web Interface │
│   (FastAPI)     │
└─────────┬───────┘
          │
┌─────────▼───────┐
│  Orchestrator   │
│  (Query Router) │
└─────────┬───────┘
          │
    ┌─────▼─────┐
    │  Agents   │
    └───────────┘
    │ │ │ │ │ │ │
    ▼ ▼ ▼ ▼ ▼ ▼ ▼
   ┌─┐┌─┐┌─┐┌─┐┌─┐┌─┐┌─┐
   │J││G││A││F││V││S││U│
   │I││I││P││S││I││3││R│
   │R││T││I││ ││D││││L│
   │A││H││ ││ ││E││ ││ │
   │ ││U││ ││ ││O││ ││ │
   │ ││B││ ││ ││ ││ ││ │
   └─┘└─┘└─┘└─┘└─┘└─┘└─┘
```

## 🔌 API Endpoints

### REST API

- `POST /query` - Process a natural language query
- `GET /health` - Check system health
- `GET /capabilities` - Get agent capabilities
- `POST /agents/{agent_type}/search` - Search using a specific agent

### Example API Usage

```bash
# Process a query
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Find Python repositories on GitHub", "max_results": 5}'

# Health check
curl "http://localhost:8000/health"
```

## 🛠️ Development

### Adding a New Agent

1. Create a new agent class inheriting from `BaseAgent`:

```python
from agents.base_agent import BaseAgent
from models import AgentType, AgentResponse

class MyCustomAgent(BaseAgent):
    def __init__(self):
        super().__init__(AgentType.CUSTOM)
    
    async def is_relevant(self, query: str) -> bool:
        # Implement relevance logic
        return "custom" in query.lower()
    
    async def search(self, query: str, max_results: int = 10) -> AgentResponse:
        # Implement search logic
        pass
```

2. Add the agent type to `models.py`:

```python
class AgentType(str, Enum):
    # ... existing types
    CUSTOM = "custom"
```

3. Register the agent in `orchestrator.py`:

```python
def _initialize_agents(self):
    # ... existing agents
    self.agents[AgentType.CUSTOM] = MyCustomAgent()
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/
```

## 🔒 Security Considerations

- Store API keys and credentials in environment variables
- Use secure authentication for production deployments
- Implement rate limiting for API endpoints
- Validate and sanitize user inputs
- Use HTTPS in production

## 📊 Monitoring and Logging

The application includes comprehensive logging and health monitoring:

- All agent operations are logged
- Health checks verify agent connectivity
- Performance metrics are tracked
- Error handling with detailed error messages

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

1. **Agent Health Check Failures**
   - Verify API credentials in `.env` file
   - Check network connectivity
   - Ensure required services are accessible

2. **No Results Found**
   - Check if the query matches agent keywords
   - Verify data sources contain relevant information
   - Try more specific or different query terms

3. **Performance Issues**
   - Reduce `max_results` parameter
   - Use specific agent types instead of all agents
   - Check network latency to external services

### Getting Help

- Check the logs for detailed error messages
- Use the health check endpoint to verify system status
- Review the example queries for proper syntax
- Ensure all required environment variables are set

## 🔮 Future Enhancements

- [ ] Database integration (PostgreSQL, MongoDB)
- [ ] Slack/Teams integration
- [ ] Email search capabilities
- [ ] Document parsing (PDF, Word, Excel)
- [ ] Real-time notifications
- [ ] Query history and favorites
- [ ] Advanced filtering and sorting
- [ ] Export results to various formats
- [ ] Multi-language support
- [ ] Voice query interface
