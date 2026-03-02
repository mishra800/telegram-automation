@echo off
echo ========================================
echo Telegram Content Automation System
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate
echo.

REM Check if requirements are installed
echo Checking dependencies...
pip install -q -r requirements.txt
echo.

REM Check if .env exists
if not exist ".env" (
    echo WARNING: .env file not found!
    echo Please copy .env.example to .env and configure it.
    echo.
    pause
    exit /b 1
)

REM Start the system
echo Starting automation system...
echo Dashboard will be available at: http://localhost:5000
echo Press Ctrl+C to stop
echo.
python main.py

pause
