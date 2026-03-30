@echo off
REM This script runs the Library Management System

echo Starting Library Management System...
cd /d "%~dp0"

REM Check if venv exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install/update requirements if needed
echo Installing dependencies...
python -m pip install -r requirements.txt --quiet

REM Run the Flask app
echo.
echo Starting Flask app on http://127.0.0.1:5000
echo Press CTRL+C to stop the server
echo.
python app.py

pause
