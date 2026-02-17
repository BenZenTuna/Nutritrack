#!/bin/bash
set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo -e "${CYAN}==============================${NC}"
echo -e "${CYAN}  NutriTrack Installer${NC}"
echo -e "${CYAN}==============================${NC}"
echo ""

# ── Check Python ────────────────────────────────────────────────────
echo -e "${YELLOW}Checking Python...${NC}"
PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        version=$("$cmd" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null)
        major=$("$cmd" -c "import sys; print(sys.version_info.major)" 2>/dev/null)
        minor=$("$cmd" -c "import sys; print(sys.version_info.minor)" 2>/dev/null)
        if [ "$major" -ge 3 ] && [ "$minor" -ge 10 ]; then
            PYTHON="$cmd"
            echo -e "  ${GREEN}Found $cmd ($version)${NC}"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo -e "  ${RED}Python 3.10+ not found.${NC}"
    echo ""
    echo "  Install Python 3.10+ for your system:"
    echo "    Ubuntu/Debian:  sudo apt install python3 python3-venv python3-pip"
    echo "    Fedora/RHEL:    sudo dnf install python3 python3-pip"
    echo "    Arch:           sudo pacman -S python python-pip"
    echo "    macOS:          brew install python@3.11"
    echo ""
    exit 1
fi

# ── Create virtual environment ──────────────────────────────────────
echo -e "${YELLOW}Setting up virtual environment...${NC}"
if [ ! -d "venv" ]; then
    $PYTHON -m venv venv
    echo -e "  ${GREEN}Created venv/${NC}"
else
    echo -e "  ${GREEN}venv/ already exists${NC}"
fi

# Activate
source venv/bin/activate

# ── Install dependencies ────────────────────────────────────────────
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo -e "  ${GREEN}Dependencies installed${NC}"

# ── Initialize database ────────────────────────────────────────────
echo -e "${YELLOW}Initializing database...${NC}"
$PYTHON database.py
echo -e "  ${GREEN}Database ready${NC}"

# ── Seed demo data (optional) ──────────────────────────────────────
echo ""
read -p "Load 30 days of sample data? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    $PYTHON seed.py --force
    echo -e "  ${GREEN}Demo data loaded${NC}"
fi

# ── Done ────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}==============================${NC}"
echo -e "${GREEN}  NutriTrack is ready!${NC}"
echo -e "${GREEN}==============================${NC}"
echo ""
echo -e "  Dashboard:  ${CYAN}http://localhost:8000${NC}"
echo -e "  API Docs:   ${CYAN}http://localhost:8000/docs${NC}"
echo ""
echo -e "  Next time:  ${YELLOW}./start.sh${NC}"
echo -e "  Stop:       ${YELLOW}./stop.sh${NC}"
echo ""
echo -e "  Connect an AI agent: see ${CYAN}docs/AGENT_README.md${NC}"
echo ""

# ── Start server ────────────────────────────────────────────────────
echo -e "${YELLOW}Starting server...${NC}"
$PYTHON app.py
