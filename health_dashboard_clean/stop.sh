#!/bin/bash
pkill -f "python3 app.py" 2>/dev/null && echo "NutriTrack stopped" || echo "NutriTrack is not running"
