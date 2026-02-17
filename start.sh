#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate 2>/dev/null || { echo "Run ./install.sh first"; exit 1; }
echo "NutriTrack starting at http://localhost:${NUTRITRACK_PORT:-8000}"
python3 app.py
