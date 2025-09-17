#!/usr/bin/env python3
"""
Agentic AI Workflows - Main Entry Point

This is the main entry point for the agentic AI application.
It can be run as a CLI tool or as a web server.
"""

import asyncio
import argparse
import json
from orchestrator import AgenticOrchestrator
from models import QueryRequest
from config import settings
import logging

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def run_cli_query(query: str, max_results: int = 10):
    """Run a query from the command line"""
    orchestrator = AgenticOrchestrator()
    
    print(f"\n🤖 Processing query: {query}")
    print("=" * 60)
    
    request = QueryRequest(prompt=query, max_results=max_results)
    response = await orchestrator.process_query(request)
    
    print(f"\n📊 Summary:")
    print(f"Query: {response.query}")
    print(f"Agents Used: {', '.join([agent.value for agent in response.agents_used])}")
    print(f"Total Results: {response.total_results}")
    print(f"Execution Time: {response.execution_time:.2f}s")
    print(f"Summary: {response.summary}")
    
    print(f"\n📋 Detailed Results:")
    print("=" * 60)
    
    for result in response.results:
        print(f"\n🔍 {result.agent_type.value.upper()} Agent:")
        
        if result.success:
            if result.data:
                for i, item in enumerate(result.data, 1):
                    print(f"\n  Result {i}:")
                    print_result_item(item, result.agent_type.value, indent="    ")
            else:
                print("    No results found")
        else:
            print(f"    ❌ Error: {result.error}")

def print_result_item(item: dict, agent_type: str, indent: str = ""):
    """Print a result item in a formatted way"""
    if agent_type == 'jira':
        print(f"{indent}Key: {item.get('key', 'N/A')}")
        print(f"{indent}Summary: {item.get('summary', 'N/A')}")
        print(f"{indent}Status: {item.get('status', 'N/A')}")
        print(f"{indent}Priority: {item.get('priority', 'N/A')}")
        print(f"{indent}Assignee: {item.get('assignee', 'Unassigned')}")
        if item.get('url'):
            print(f"{indent}URL: {item['url']}")
    
    elif agent_type == 'github':
        print(f"{indent}Name: {item.get('name', 'N/A')}")
        print(f"{indent}Type: {item.get('type', 'N/A')}")
        print(f"{indent}Author: {item.get('author', 'N/A')}")
        print(f"{indent}Description: {item.get('description', 'N/A')[:100]}...")
        if item.get('url'):
            print(f"{indent}URL: {item['url']}")
    
    elif agent_type == 'filesystem':
        print(f"{indent}Name: {item.get('name', 'N/A')}")
        print(f"{indent}Path: {item.get('path', 'N/A')}")
        print(f"{indent}Type: {item.get('type', 'N/A')}")
        print(f"{indent}Size: {item.get('size', 'N/A')} bytes")
        print(f"{indent}Modified: {item.get('modified', 'N/A')}")
    
    elif agent_type == 'video':
        print(f"{indent}Title: {item.get('title', 'N/A')}")
        print(f"{indent}Duration: {item.get('duration', 'N/A')}")
        print(f"{indent}Platform: {item.get('platform', 'N/A')}")
        if item.get('url'):
            print(f"{indent}URL: {item['url']}")
    
    elif agent_type == 's3':
        print(f"{indent}Key: {item.get('key', 'N/A')}")
        print(f"{indent}Bucket: {item.get('bucket', 'N/A')}")
        print(f"{indent}Size: {item.get('size', 'N/A')} bytes")
        print(f"{indent}Last Modified: {item.get('last_modified', 'N/A')}")
    
    elif agent_type == 'url':
        print(f"{indent}URL: {item.get('url', 'N/A')}")
        print(f"{indent}Title: {item.get('title', 'N/A')}")
        print(f"{indent}Status: {item.get('status_code', 'N/A')}")
        print(f"{indent}Content Type: {item.get('content_type', 'N/A')}")
    
    else:
        # Generic printing for unknown types
        for key, value in item.items():
            if isinstance(value, str) and len(value) > 100:
                value = value[:100] + "..."
            print(f"{indent}{key}: {value}")

async def run_health_check():
    """Run a health check on all agents"""
    orchestrator = AgenticOrchestrator()
    
    print("\n🏥 Running Health Check...")
    print("=" * 40)
    
    health_status = await orchestrator.health_check()
    
    print(f"\nOverall Health: {'✅ Healthy' if health_status['overall_healthy'] else '❌ Issues Detected'}")
    print(f"OpenAI Configured: {'✅ Yes' if health_status['openai_configured'] else '❌ No'}")
    
    print(f"\nAgent Status:")
    for agent_name, status in health_status['agents'].items():
        status_icon = "✅" if status['healthy'] else "❌"
        print(f"  {agent_name.upper()}: {status_icon} {status['status']}")
        if status.get('error'):
            print(f"    Error: {status['error']}")

def run_web_server():
    """Run the web server"""
    import uvicorn
    from api import app
    
    print(f"\n🚀 Starting Agentic AI Workflows Web Server...")
    print(f"Server will be available at: http://{settings.app_host}:{settings.app_port}")
    print("Press Ctrl+C to stop the server")
    
    uvicorn.run(
        app,
        host=settings.app_host,
        port=settings.app_port,
        log_level=settings.log_level.lower()
    )

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Agentic AI Workflows - Multi-agent information retrieval system"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Query command
    query_parser = subparsers.add_parser('query', help='Run a query using the agentic workflow')
    query_parser.add_argument('prompt', help='Natural language query')
    query_parser.add_argument('--max-results', type=int, default=10, help='Maximum number of results per agent')
    
    # Health check command
    subparsers.add_parser('health', help='Check the health of all agents')
    
    # Web server command
    server_parser = subparsers.add_parser('serve', help='Start the web server')
    
    # Interactive mode
    subparsers.add_parser('interactive', help='Start interactive mode')
    
    args = parser.parse_args()
    
    if args.command == 'query':
        asyncio.run(run_cli_query(args.prompt, args.max_results))
    
    elif args.command == 'health':
        asyncio.run(run_health_check())
    
    elif args.command == 'serve':
        run_web_server()
    
    elif args.command == 'interactive':
        asyncio.run(interactive_mode())
    
    else:
        # Default to web server if no command specified
        print("No command specified. Starting web server...")
        run_web_server()

async def interactive_mode():
    """Run in interactive mode"""
    orchestrator = AgenticOrchestrator()
    
    print("\n🤖 Agentic AI Workflows - Interactive Mode")
    print("=" * 50)
    print("Enter your queries in natural language.")
    print("Type 'health' to check system health.")
    print("Type 'help' for examples.")
    print("Type 'quit' or 'exit' to quit.")
    print("=" * 50)
    
    while True:
        try:
            query = input("\n💬 Query: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("Goodbye! 👋")
                break
            
            elif query.lower() == 'health':
                await run_health_check()
                continue
            
            elif query.lower() == 'help':
                print_help_examples()
                continue
            
            elif not query:
                continue
            
            # Process the query
            await run_cli_query(query)
            
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")

def print_help_examples():
    """Print help examples"""
    print("\n📚 Example Queries:")
    print("=" * 30)
    print("• Find all high priority bugs in JIRA")
    print("• Show me Python repositories on GitHub")
    print("• Get content from https://example.com")
    print("• Search for tutorial videos about machine learning")
    print("• List files in my project directory containing 'config'")
    print("• Find documents in S3 bucket containing 'report'")
    print("• Call API https://api.github.com/users/octocat")
    print("• Search for issues assigned to me in JIRA")

if __name__ == "__main__":
    main()
