"""
Utility functions for the Agentic AI Workflows application
"""

import sys
import os
import importlib
from typing import Optional, Any

def setup_imports():
    """Setup import paths for the application"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

def safe_import(module_name: str, package: Optional[str] = None) -> Optional[Any]:
    """Safely import a module, returning None if import fails"""
    try:
        if package:
            return importlib.import_module(module_name, package)
        else:
            return importlib.import_module(module_name)
    except ImportError as e:
        print(f"Warning: Could not import {module_name}: {e}")
        return None

def check_dependencies() -> dict:
    """Check which dependencies are available"""
    dependencies = {
        'fastapi': safe_import('fastapi'),
        'uvicorn': safe_import('uvicorn'),
        'pydantic': safe_import('pydantic'),
        'pydantic_settings': safe_import('pydantic_settings'),
        'jira': safe_import('jira'),
        'github': safe_import('github'),
        'boto3': safe_import('boto3'),
        'yt_dlp': safe_import('yt_dlp'),
        'beautifulsoup4': safe_import('bs4'),
        'aiohttp': safe_import('aiohttp'),
        'requests': safe_import('requests'),
        'openai': safe_import('openai')
    }
    
    available = {k: v is not None for k, v in dependencies.items()}
    return available

def get_missing_dependencies() -> list:
    """Get list of missing dependencies"""
    available = check_dependencies()
    missing = [k for k, v in available.items() if not v]
    return missing

def print_dependency_status():
    """Print the status of all dependencies"""
    print("📦 Dependency Status:")
    print("=" * 30)
    
    available = check_dependencies()
    for dep, is_available in available.items():
        status = "✅ Available" if is_available else "❌ Missing"
        print(f"{dep:15} {status}")
    
    missing = get_missing_dependencies()
    if missing:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing)}")
        print("Run 'python setup.py' to install them.")
    else:
        print("\n🎉 All dependencies are available!")

if __name__ == "__main__":
    setup_imports()
    print_dependency_status()
