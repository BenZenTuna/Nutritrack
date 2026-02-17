#!/bin/bash
# NutriTrack Setup & Run Script
set -e

echo "╔══════════════════════════════════════╗"
echo "║ NutriTrack — Setup & Launch          ║"
echo "╚══════════════════════════════════════╝"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is required. Please install Python 3.10+."
    exit 1
fi

echo "📦 Installing dependencies..."
pip install -r requirements.txt --break-system-packages --quiet 2>/dev/null || \
pip install -r requirements.txt --quiet

echo "🗄️ Initializing database..."
python3 database.py

echo ""
echo "🚀 Starting NutriTrack server..."
echo "   Dashboard: http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo ""
echo "   Press Ctrl+C to stop."
echo ""

python3 app.py
