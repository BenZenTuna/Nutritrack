#!/bin/bash
cd "$(dirname "$0")"

echo "Starting NutriTrack in DEVELOPMENT mode..."

# Check if Docker is available and user wants Docker dev mode
if command -v docker &>/dev/null && [ -f docker-compose.dev.yml ]; then
    read -p "Use Docker dev mode? (y/N): " use_docker
    if [[ "$use_docker" =~ ^[Yy]$ ]]; then
        echo "Starting with Docker (live mount + auto-reload)..."
        echo "   Dashboard: http://localhost:8000"
        echo "   API Docs:  http://localhost:8000/docs"
        echo ""
        docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
        exit 0
    fi
fi

# Bare metal dev mode with auto-reload
echo "Starting bare metal with auto-reload..."
source venv/bin/activate 2>/dev/null || { echo "Run ./install.sh first"; exit 1; }
echo "   Dashboard: http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo "   Auto-reload ON -- server restarts on .py file changes"
echo "   HTML/CSS/JS changes: just refresh browser"
echo ""
python3 -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload --reload-dir .
