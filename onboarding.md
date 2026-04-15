# NutriTrack Onboarding & Reference

Companion to `SKILL.md`. Load this only when needed — install/setup, demo seeding, troubleshooting, or background on how calorie goals are derived.

## Installation

If NutriTrack is not running yet, deploy it with one command:

```bash
git clone https://github.com/BenZenTuna/Nutritrack.git
cd Nutritrack
chmod +x deploy.sh
./deploy.sh
```

The script auto-detects Docker (if available) or falls back to Python venv — no prompts, no sudo.

Management:
- `./deploy.sh stop` — stop the server
- `./deploy.sh status` — check if running
- `./deploy.sh update` — pull latest code and restart

After install, verify with: `curl -s http://localhost:8000/api/profile`

For detailed agent deployment docs, see [docs/AGENT_DEPLOY.md](docs/AGENT_DEPLOY.md).

## First-Time Setup

Before logging any data, the user needs a profile. Ask for their details and create one:

```bash
curl -s -X PUT "$NUTRITRACK_URL/api/profile" \
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

## Demo Data

To seed 30 days of realistic sample data (DESTRUCTIVE — clears existing data):
```bash
curl -s -X POST "$NUTRITRACK_URL/api/seed-demo-data"
```

## Calorie Calculation Engine (background reference)

NutriTrack computes these server-side; you don't need to. Included for context when explaining the numbers to the user.

- Male BMR: `10 × weight(kg) + 6.25 × height(cm) - 5 × age + 5`
- Female BMR: `10 × weight(kg) + 6.25 × height(cm) - 5 × age - 161`
- TDEE = BMR × activity multiplier (sedentary=1.2, light=1.375, moderate=1.55, active=1.725, very_active=1.9)
- Daily calorie goal = (TDEE + exercise_calories) - deficit
- Macro split: 30% protein (÷4 cal/g), 40% carbs (÷4 cal/g), 30% fat (÷9 cal/g)

## Troubleshooting

- **Server not responding**: Check if Docker container is running (`docker ps | grep nutritrack`) or if the Python process is active
- **"No profile set" error**: The user needs to create their profile first (PUT /api/profile)
- **Calorie goal seems wrong**: Check if exercise has been logged — exercise calories increase the daily goal
- **Data not showing on dashboard**: The dashboard auto-refreshes every 30 seconds, or the user can manually refresh
