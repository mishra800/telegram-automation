#!/bin/bash

echo "========================================"
echo "Telegram Content Automation System"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo ""

# Check if requirements are installed
echo "Checking dependencies..."
pip install -q -r requirements.txt
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found!"
    echo "Please copy .env.example to .env and configure it."
    echo ""
    exit 1
fi

# Start the system
echo "Starting automation system..."
echo "Dashboard will be available at: http://localhost:5000"
echo "Press Ctrl+C to stop"
echo ""
python main.py
