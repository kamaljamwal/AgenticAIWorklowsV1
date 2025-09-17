# 🚀 Getting Started with Agentic AI Workflows

## Quick Demo (No Setup Required)

Want to try the application immediately? Use the simple version:

```bash
# CLI demo
python simple_main.py "find Python files in my project"

# Web interface demo
python simple_main.py --web
```

Then open http://localhost:8000 in your browser.

## What You Just Created

You now have a comprehensive **multi-agent AI system** that can:

✅ **Process natural language queries** and automatically determine which data sources to search  
✅ **Run multiple agents in parallel** for faster results  
✅ **Work with 7 different data sources**: JIRA, GitHub, APIs, FileSystem, Videos, S3, URLs  
✅ **Provide both web and CLI interfaces**  
✅ **Scale from simple demos to production systems**  

## Architecture Overview

```
User Query → Orchestrator → Relevant Agents → Parallel Search → Aggregated Results
```

### Available Agents

| Agent | Purpose | Example Query |
|-------|---------|---------------|
| **JIRA** | Issues, tickets, projects | "Find high priority bugs" |
| **GitHub** | Repositories, PRs, code | "Show Python repositories" |
| **API** | External HTTP services | "Call GitHub API for user data" |
| **FileSystem** | Local files/folders | "Find config files" |
| **Video** | YouTube, Vimeo content | "Search for Python tutorials" |
| **S3** | AWS bucket objects | "List PDF files in bucket" |
| **URL** | Web content scraping | "Get content from website" |

## Next Steps

### 1. Try the Simple Version First
```bash
python simple_main.py "search for documentation files"
python simple_main.py --web
```

### 2. Install Full Dependencies (Optional)
```bash
python setup.py
```

### 3. Configure API Keys (For Full Functionality)
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 4. Run the Full Version
```bash
python main.py serve  # Web interface
python main.py query "your query here"  # CLI
```

## Example Queries to Try

### Simple Queries (Work with any version)
- "find files containing config"
- "search for Python scripts"
- "list directories in project"

### Advanced Queries (Require API setup)
- "find all high priority bugs in JIRA assigned to me"
- "show recent pull requests in my GitHub repositories"
- "get content from https://news.ycombinator.com"
- "search for machine learning tutorials on YouTube"
- "list all PDF files in my S3 bucket"

## Troubleshooting

### Import Errors
```bash
python utils.py  # Check dependency status
python setup.py  # Install missing dependencies
```

### No Results
- Try the simple version first: `python simple_main.py "your query"`
- Check if your query matches agent keywords
- Verify API credentials in `.env` file

### Web Server Issues
```bash
# Try the simple web server
python simple_main.py --web

# Check if port 8000 is available
netstat -an | findstr :8000
```

## Development

### Adding New Agents
1. Create agent class inheriting from `BaseAgent`
2. Implement `search()` and `is_relevant()` methods
3. Register in orchestrator
4. Test with simple queries

### Extending Functionality
- Add new data sources
- Implement custom query parsing
- Add authentication systems
- Create specialized UIs

## Support

- Check `README.md` for detailed documentation
- Run `python utils.py` to check system status
- Use the simple version for testing and demos
- Gradually add API integrations as needed

---

**🎉 Congratulations!** You now have a powerful agentic AI system that can intelligently search across multiple data sources based on natural language queries.
