#!/bin/bash

# Texture Reference Vault Startup Script

echo "🎨 Starting Texture Reference Vault..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create uploads directory if it doesn't exist
if [ ! -d "uploads" ]; then
    echo "📁 Creating uploads directory..."
    mkdir uploads
fi

# Start the application
echo "🚀 Starting Flask application..."
echo "📍 Application will be available at: http://localhost:5000"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

python run.py
