@echo off
echo Setting up Agentic AI Workflows...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo Python found. Running setup...
python setup.py

echo.
echo Setup complete! You can now run:
echo   python simple_main.py "your query here"
echo   python simple_main.py --web
echo.
pause
