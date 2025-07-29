@echo off
echo 🎨 Starting Texture Reference Vault...

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate

REM Install/update dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Create uploads directory if it doesn't exist
if not exist "uploads" (
    echo 📁 Creating uploads directory...
    mkdir uploads
)

REM Start the application
echo 🚀 Starting Flask application...
echo 📍 Application will be available at: http://localhost:5000
echo 🛑 Press Ctrl+C to stop the server
echo.

python app.py

pause
