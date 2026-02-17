@echo off
REM KAIROS Setup Script for Windows
REM Run this script to set up your Kairos AI environment

echo ==================================
echo   ⚡ KAIROS Setup Assistant ⚡
echo ==================================
echo.

REM Check Python version
echo Checking Python version...
python --version
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)
echo ✅ Python found
echo.

REM Create virtual environment
set /p VENV="Create virtual environment? (recommended) [y/N]: "
if /i "%VENV%"=="y" (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo ✅ Virtual environment created and activated
    echo.
)

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)
echo ✅ Dependencies installed
echo.

REM Set up .env file
if not exist .env (
    echo Setting up configuration file...
    copy .env.example .env
    echo ✅ Created .env file
    echo.
    echo ⚠️  IMPORTANT: Edit the .env file and add your Gemini API key
    echo    Get your key from: https://makersuite.google.com/app/apikey
    echo.
) else (
    echo ℹ️  .env file already exists
    echo.
)

REM Final instructions
echo ==================================
echo   Setup Complete! 🎉
echo ==================================
echo.
echo Next steps:
echo 1. Edit .env file and add your GEMINI_API_KEY
echo 2. Run: python main.py
echo 3. Open browser to: http://localhost:5000
echo.

if /i "%VENV%"=="y" (
    echo Note: Virtual environment is active. To deactivate later, run: deactivate
    echo.
)

set /p EDIT="Open .env file for editing now? [y/N]: "
if /i "%EDIT%"=="y" (
    notepad .env
)

echo.
echo All done! May Kairos guide you to wisdom. ⚡
pause
