#!/usr/bin/env python3
"""
Setup script for Agentic AI Workflows
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def check_package(package_name):
    """Check if a package is installed"""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

def main():
    """Main setup function"""
    print("🔧 Setting up Agentic AI Workflows...")
    
    # Essential packages for basic functionality
    essential_packages = [
        "fastapi==0.109.0",
        "uvicorn==0.27.0", 
        "pydantic==2.5.3",
        "pydantic-settings==2.1.0",
        "python-dotenv==1.0.0",
        "aiohttp==3.9.1",
        "requests==2.31.0"
    ]
    
    # Optional packages for full functionality
    optional_packages = [
        "jira==3.5.2",
        "PyGithub==1.59.1", 
        "boto3==1.34.34",
        "yt-dlp==2024.1.6",
        "beautifulsoup4==4.12.2",
        "lxml==4.9.4",
        "aiofiles==23.2.0",
        "python-multipart==0.0.6"
    ]
    
    print("Installing essential packages...")
    failed_essential = []
    for package in essential_packages:
        print(f"  Installing {package}...")
        if not install_package(package):
            failed_essential.append(package)
            print(f"    ❌ Failed to install {package}")
        else:
            print(f"    ✅ Installed {package}")
    
    if failed_essential:
        print(f"\n⚠️  Some essential packages failed to install: {failed_essential}")
        print("You can still use the simple version with: python simple_main.py")
        return False
    
    print("\nInstalling optional packages...")
    failed_optional = []
    for package in optional_packages:
        print(f"  Installing {package}...")
        if not install_package(package):
            failed_optional.append(package)
            print(f"    ❌ Failed to install {package}")
        else:
            print(f"    ✅ Installed {package}")
    
    if failed_optional:
        print(f"\n⚠️  Some optional packages failed to install: {failed_optional}")
        print("Some agents may not work without these packages.")
    
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Copy .env.example to .env and configure your API keys")
    print("2. Run the application:")
    print("   - Web interface: python main.py serve")
    print("   - CLI: python main.py query 'your query here'")
    print("   - Simple version: python simple_main.py 'your query here'")
    
    return True

if __name__ == "__main__":
    main()
