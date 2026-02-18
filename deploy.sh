#!/usr/bin/env bash
set -e

# ═══════════════════════════════════════════════════════════════════════
# NutriTrack — One-Command Deploy
# ═══════════════════════════════════════════════════════════════════════
#
# Usage:
#   ./deploy.sh            Start (or restart) NutriTrack
#   ./deploy.sh stop       Stop the running instance
#   ./deploy.sh status     Check if NutriTrack is running
#   ./deploy.sh update     Pull latest code and restart
#
# Environment variables:
#   NUTRITRACK_PORT   Server port         (default: 8000)
#   NUTRITRACK_HOST   Bind address        (default: 0.0.0.0)
#
# The script auto-detects Docker. If Docker is available and the daemon
# is accessible, it uses docker compose. Otherwise it falls back to a
# Python venv — no sudo required.
# ═══════════════════════════════════════════════════════════════════════

# ── Configuration ─────────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

PORT="${NUTRITRACK_PORT:-8000}"
HOST="${NUTRITRACK_HOST:-0.0.0.0}"
PID_FILE="$SCRIPT_DIR/.nutritrack.pid"
LOG_FILE="$SCRIPT_DIR/nutritrack.log"
DATA_DIR="$SCRIPT_DIR/data"
DB_PATH="$DATA_DIR/nutritrack.db"
HEALTH_URL="http://127.0.0.1:$PORT/api/profile"
HEALTH_TIMEOUT=20

# ── Colors ────────────────────────────────────────────────────────────

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

ok()   { echo -e "  ${GREEN}✓${NC} $1"; }
warn() { echo -e "  ${YELLOW}⚠${NC} $1"; }
fail() { echo -e "  ${RED}✗${NC} $1"; }

# ── Helpers ───────────────────────────────────────────────────────────

has_docker() {
    command -v docker &>/dev/null && docker info &>/dev/null 2>&1
}

find_python() {
    for cmd in python3 python; do
        if command -v "$cmd" &>/dev/null; then
            local major minor
            major=$("$cmd" -c "import sys; print(sys.version_info.major)" 2>/dev/null) || continue
            minor=$("$cmd" -c "import sys; print(sys.version_info.minor)" 2>/dev/null) || continue
            if [ "$major" -ge 3 ] && [ "$minor" -ge 10 ]; then
                echo "$cmd"
                return 0
            fi
        fi
    done
    return 1
}

# Check if a process is listening on the configured port
port_in_use() {
    if command -v ss &>/dev/null; then
        ss -tlnp 2>/dev/null | grep -q ":${PORT} " && return 0
    elif command -v lsof &>/dev/null; then
        lsof -iTCP:"$PORT" -sTCP:LISTEN &>/dev/null && return 0
    elif command -v netstat &>/dev/null; then
        netstat -tlnp 2>/dev/null | grep -q ":${PORT} " && return 0
    fi
    return 1
}

# Wait for the server to respond, up to HEALTH_TIMEOUT seconds
health_check() {
    local elapsed=0
    while [ "$elapsed" -lt "$HEALTH_TIMEOUT" ]; do
        if curl -sf "$HEALTH_URL" >/dev/null 2>&1; then
            return 0
        fi
        sleep 1
        elapsed=$((elapsed + 1))
    done
    return 1
}

# Kill a running bare-metal instance by PID file and/or port
stop_bare_metal() {
    local stopped=false

    # Kill by PID file
    if [ -f "$PID_FILE" ]; then
        local pid
        pid=$(cat "$PID_FILE" 2>/dev/null)
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null && stopped=true
            # Wait briefly for clean shutdown
            local wait=0
            while kill -0 "$pid" 2>/dev/null && [ "$wait" -lt 5 ]; do
                sleep 1
                wait=$((wait + 1))
            done
            # Force kill if still alive
            if kill -0 "$pid" 2>/dev/null; then
                kill -9 "$pid" 2>/dev/null
            fi
        fi
        rm -f "$PID_FILE"
    fi

    # Also kill any lingering process on the port
    if port_in_use; then
        pkill -f "uvicorn.*app:app.*$PORT" 2>/dev/null || true
        pkill -f "python.*app.py" 2>/dev/null || true
        sleep 1
    fi

    $stopped && return 0 || return 1
}

# Print the final summary box
print_summary() {
    local mode="$1"
    echo ""
    echo -e "${BOLD}${GREEN}╔══════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}${GREEN}║         NutriTrack is running!           ║${NC}"
    echo -e "${BOLD}${GREEN}╚══════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  ${BOLD}Dashboard${NC}   http://${HOST}:${PORT}"
    echo -e "  ${BOLD}API Docs${NC}    http://${HOST}:${PORT}/docs"
    echo -e "  ${BOLD}Mode${NC}        $mode"
    echo ""
    echo -e "  ${CYAN}./deploy.sh stop${NC}     Stop the server"
    echo -e "  ${CYAN}./deploy.sh status${NC}   Check status"
    echo -e "  ${CYAN}./deploy.sh update${NC}   Pull latest + restart"
    echo ""
}

# ── Commands ──────────────────────────────────────────────────────────

cmd_stop() {
    echo ""
    echo -e "${BOLD}Stopping NutriTrack...${NC}"

    # Try Docker first
    if has_docker && docker compose ps --status running 2>/dev/null | grep -q nutritrack; then
        docker compose down
        ok "Docker container stopped"
        return 0
    fi

    # Try bare-metal
    if stop_bare_metal; then
        ok "Server stopped"
        return 0
    fi

    warn "NutriTrack is not running"
}

cmd_status() {
    echo ""
    echo -e "${BOLD}NutriTrack Status${NC}"
    echo ""

    # Check Docker
    if has_docker && docker compose ps --status running 2>/dev/null | grep -q nutritrack; then
        ok "Running via Docker on port $PORT"
        docker compose ps 2>/dev/null | grep nutritrack || true
        return 0
    fi

    # Check PID file
    if [ -f "$PID_FILE" ]; then
        local pid
        pid=$(cat "$PID_FILE" 2>/dev/null)
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            ok "Running via Python (PID $pid) on port $PORT"
            if curl -sf "$HEALTH_URL" >/dev/null 2>&1; then
                ok "Health check passed"
            else
                warn "Process alive but not responding"
            fi
            return 0
        fi
    fi

    # Check port as fallback
    if port_in_use; then
        warn "Something is listening on port $PORT (not managed by deploy.sh)"
        return 0
    fi

    fail "NutriTrack is not running"
    return 1
}

cmd_update() {
    echo ""
    echo -e "${BOLD}Updating NutriTrack...${NC}"

    if ! command -v git &>/dev/null; then
        fail "git is not installed"
        exit 1
    fi

    echo -e "  Pulling latest code..."
    git pull --ff-only || {
        fail "git pull failed — resolve conflicts manually"
        exit 1
    }
    ok "Code updated"

    # Restart
    cmd_start
}

cmd_start() {
    echo ""
    echo -e "${BOLD}${CYAN}═══════════════════════════════════════${NC}"
    echo -e "${BOLD}${CYAN}       NutriTrack Deploy${NC}"
    echo -e "${BOLD}${CYAN}═══════════════════════════════════════${NC}"
    echo ""

    # ── Stop any existing instance ────────────────────────────────────
    if has_docker && docker compose ps --status running 2>/dev/null | grep -q nutritrack; then
        warn "Stopping existing Docker instance..."
        docker compose down
    fi
    if [ -f "$PID_FILE" ] || port_in_use; then
        warn "Stopping existing instance..."
        stop_bare_metal
    fi

    # ── Detect deployment mode ────────────────────────────────────────
    if has_docker; then
        ok "Docker detected — using container deployment"
        start_docker
    else
        warn "Docker not available — using Python deployment"
        start_python
    fi
}

start_docker() {
    echo ""
    echo -e "  ${BOLD}Building and starting container...${NC}"

    # Export port so docker-compose.yml can read it
    export NUTRITRACK_PORT="$PORT"
    docker compose up -d --build

    ok "Container started"

    # Health check
    echo -e "  Waiting for server to be ready..."
    if health_check; then
        ok "Health check passed"
        print_summary "Docker"
    else
        fail "Server did not respond within ${HEALTH_TIMEOUT}s"
        echo ""
        echo -e "  Check logs: ${CYAN}docker compose logs -f${NC}"
        exit 1
    fi
}

start_python() {
    # ── Find Python ───────────────────────────────────────────────────
    local PYTHON
    PYTHON=$(find_python) || {
        fail "Python 3.10+ not found"
        echo ""
        echo "  Install Python for your system:"
        echo "    Ubuntu/Debian:  sudo apt install python3 python3-venv python3-pip"
        echo "    Fedora/RHEL:    sudo dnf install python3 python3-pip"
        echo "    Arch:           sudo pacman -S python python-pip"
        echo "    macOS:          brew install python@3.11"
        exit 1
    }
    ok "Python: $($PYTHON --version 2>&1)"

    # ── Create venv ───────────────────────────────────────────────────
    if [ ! -d "venv" ]; then
        echo -e "  Creating virtual environment..."
        $PYTHON -m venv venv || {
            fail "Failed to create venv (install python3-venv: sudo apt install python3-venv)"
            exit 1
        }
        ok "Virtual environment created"
    else
        ok "Virtual environment exists"
    fi

    # shellcheck disable=SC1091
    source venv/bin/activate

    # ── Install dependencies ──────────────────────────────────────────
    echo -e "  Installing dependencies..."
    pip install -q --upgrade pip 2>/dev/null
    pip install -q -r requirements.txt 2>/dev/null
    ok "Dependencies installed"

    # ── Prepare data directory ────────────────────────────────────────
    mkdir -p "$DATA_DIR"
    ok "Data directory ready ($DATA_DIR)"

    # ── Initialize database ───────────────────────────────────────────
    NUTRITRACK_DB_PATH="$DB_PATH" $PYTHON database.py
    ok "Database initialized"

    # ── Start server in background ────────────────────────────────────
    echo ""
    echo -e "  ${BOLD}Starting server...${NC}"
    NUTRITRACK_DB_PATH="$DB_PATH" \
    NUTRITRACK_HOST="$HOST" \
    NUTRITRACK_PORT="$PORT" \
        nohup "$PYTHON" app.py > "$LOG_FILE" 2>&1 &
    local pid=$!
    echo "$pid" > "$PID_FILE"
    ok "Server started (PID $pid)"

    # ── Health check ──────────────────────────────────────────────────
    echo -e "  Waiting for server to be ready..."
    if health_check; then
        ok "Health check passed"
        print_summary "Python (venv)"
    else
        fail "Server did not respond within ${HEALTH_TIMEOUT}s"
        echo ""
        echo -e "  Check logs: ${CYAN}cat $LOG_FILE${NC}"
        # Clean up PID file if server failed
        if ! kill -0 "$pid" 2>/dev/null; then
            rm -f "$PID_FILE"
            fail "Server process exited — check log for errors"
        fi
        exit 1
    fi
}

# ── Main ──────────────────────────────────────────────────────────────

case "${1:-start}" in
    start)  cmd_start  ;;
    stop)   cmd_stop   ;;
    status) cmd_status ;;
    update) cmd_update ;;
    *)
        echo "Usage: ./deploy.sh [start|stop|status|update]"
        echo ""
        echo "  start    Start or restart NutriTrack (default)"
        echo "  stop     Stop the running instance"
        echo "  status   Check if NutriTrack is running"
        echo "  update   Pull latest code and restart"
        exit 1
        ;;
esac
