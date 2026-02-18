# NutriTrack — Agent Deployment Guide

One-command deploy for AI agents. No prompts, no decisions, no sudo.

## Deploy

```bash
git clone https://github.com/BenZenTuna/Nutritrack.git
cd Nutritrack
chmod +x deploy.sh
./deploy.sh
```

Auto-detects Docker (if daemon is accessible) or falls back to Python venv.

## Management

```bash
./deploy.sh          # Start or restart
./deploy.sh stop     # Stop the server
./deploy.sh status   # Check if running
./deploy.sh update   # git pull + restart
```

## Verify

```bash
curl -s http://localhost:8000/api/profile
```

A JSON response (even `{"detail":"No profile set"}`) means the server is up.

## First-Time Setup

Create the user profile before logging any data:

```bash
curl -s -X PUT http://localhost:8000/api/profile \
  -H "Content-Type: application/json" \
  -d '{
    "age": 30,
    "sex": "male",
    "height_cm": 180,
    "current_weight_kg": 85.0,
    "activity_level": "moderate",
    "weight_goal_kg": 78.0,
    "calorie_deficit": 500
  }'
```

Activity levels: `sedentary`, `light`, `moderate`, `active`, `very_active`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NUTRITRACK_PORT` | `8000` | Server port |
| `NUTRITRACK_HOST` | `0.0.0.0` | Bind address |

Example: `NUTRITRACK_PORT=9000 ./deploy.sh`

## Data Safety

The database persists across all operations:

| Operation | DB Location | Survives? |
|-----------|-------------|-----------|
| `./deploy.sh` (restart) | `./data/nutritrack.db` | Yes |
| `./deploy.sh update` (git pull) | `./data/nutritrack.db` | Yes — `data/` is gitignored |
| `docker compose up --build` | Named volume `nutritrack_data` | Yes — Docker volumes persist |

Never store data in the project root for bare-metal deploys. The script sets `NUTRITRACK_DB_PATH=./data/nutritrack.db` automatically.

## Optional: systemd User Service (no sudo)

```bash
mkdir -p ~/.config/systemd/user

cat > ~/.config/systemd/user/nutritrack.service << 'EOF'
[Unit]
Description=NutriTrack Nutrition Tracker
After=network.target

[Service]
Type=simple
WorkingDirectory=/path/to/Nutritrack
ExecStart=/path/to/Nutritrack/venv/bin/python app.py
Environment=NUTRITRACK_DB_PATH=/path/to/Nutritrack/data/nutritrack.db
Environment=NUTRITRACK_HOST=0.0.0.0
Environment=NUTRITRACK_PORT=8000
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
EOF

# Edit paths in the file, then:
systemctl --user daemon-reload
systemctl --user enable --now nutritrack
systemctl --user status nutritrack
```

Requires `loginctl enable-linger $USER` for the service to run without an active login session.

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| Port 8000 in use | Another process on the port | `NUTRITRACK_PORT=9000 ./deploy.sh` or stop the other process |
| `python3` not found | Python not installed | `sudo apt install python3 python3-venv python3-pip` |
| venv creation fails | Missing venv module | `sudo apt install python3-venv` |
| Permission denied on deploy.sh | Execute bit not set | `chmod +x deploy.sh` |
| Docker mode but no daemon | Docker installed but not running | Start Docker: `sudo systemctl start docker`, or let script fall back to Python |
| Health check fails | Server crashed on startup | Check `nutritrack.log` (bare-metal) or `docker compose logs` (Docker) |
| DB locked errors | Multiple processes writing | Stop duplicate instances: `./deploy.sh stop && ./deploy.sh` |
