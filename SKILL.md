---
name: nutritrack
description: Log food, weight, exercise, and health vitals to your self-hosted NutriTrack nutrition tracker. Talk naturally about meals and workouts — this skill translates to structured API calls. Use when the user mentions eating, meals, calories, macros, protein, weight, exercise, workout, blood pressure, health vitals, or nutrition goals.
homepage: https://github.com/BenZenTuna/Nutritrack
metadata: { "openclaw": { "emoji": "🥗", "category": "health", "requires": { "bins": ["curl"] } } }
---

# NutriTrack — AI-Agent Nutrition & Health Tracker

You are connected to NutriTrack, a self-hosted nutrition and health tracking platform. Your job is to translate the user's natural language about food, exercise, weight, and health into structured HTTP API calls. The dashboard at the same URL visualizes everything automatically.

## Connection

- **Base URL**: Read from the environment variable `NUTRITRACK_URL`. If not set, default to `http://localhost:8000`.
- **Content-Type**: Always `application/json`
- **Authentication**: None required (single-user, local-first design)
- **Health check**: `curl -s $NUTRITRACK_URL/api/profile` — if you get a JSON response, the server is up.
- **Dashboard**: `$NUTRITRACK_URL` in a browser
- **Swagger docs**: `$NUTRITRACK_URL/docs`

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

## Core Workflow

1. **User says what they ate** → You estimate calories and macros → `POST /api/food`
2. **User mentions exercise** → You estimate calories burned → `POST /api/activity`
3. **User reports weight** → `POST /api/weight`
4. **User shares health vitals** → `POST /api/health`
5. **User asks "how am I doing?"** → `GET /api/daily-summary` and summarize
6. **User asks for weekly review** → `GET /api/weekly-report` and analyze

## Logging Food

When the user mentions eating anything, estimate the nutritional values and log it:

```bash
curl -s -X POST "$NUTRITRACK_URL/api/food" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Grilled chicken breast with rice",
    "calories": 520,
    "protein_g": 42,
    "carbs_g": 55,
    "fat_g": 12,
    "meal_type": "lunch",
    "quantity": "200g chicken + 1 cup rice"
  }'
```

**Fields:**
- `name` (required): Descriptive food name
- `calories`, `protein_g`, `carbs_g`, `fat_g`: Nutritional estimates (default 0)
- `meal_type`: `breakfast`, `lunch`, `dinner`, or `snack`
- `quantity`: Human-readable portion description
- `notes`: Optional extra info
- `logged_at`: ISO timestamp (defaults to now). Use this for backdating: `"2026-02-17T08:30:00"`

**Meal type assignment by time:**
- Before 11:00 → `breakfast`
- 11:00–15:00 → `lunch`
- After 17:00 → `dinner`
- Everything else → `snack`

**Estimation guidelines:**
- Be reasonably accurate but don't overthink — estimates within 10-20% are fine
- When unsure about portion size, ask the user
- For packaged foods, use standard label values
- For restaurant meals, estimate on the higher side
- Round calories to nearest 5, macros to nearest 1g

## Logging Weight

```bash
curl -s -X POST "$NUTRITRACK_URL/api/weight" \
  -H "Content-Type: application/json" \
  -d '{"weight_kg": 84.2, "notes": "Morning weigh-in"}'
```

**Important side effect:** This also updates the user's profile weight, which recalculates all calorie goals.

## Logging Exercise

```bash
curl -s -X POST "$NUTRITRACK_URL/api/activity" \
  -H "Content-Type: application/json" \
  -d '{
    "activity_type": "Running",
    "duration_minutes": 30,
    "calories_burned": 350,
    "intensity": "moderate"
  }'
```

**Calorie estimation formula:** `calories_burned = MET × weight_kg × duration_hours`

Common MET values:
- Walking (3.5 mph): 4.3
- Running (6 mph): 9.8
- Cycling (moderate): 8.0
- Swimming: 7.0
- Weight training: 5.0
- Yoga: 3.0
- HIIT: 8.0

Intensity: `low`, `moderate`, or `high`

**Important:** Exercise calories are added to the daily TDEE before the deficit is applied. So if the user burns 300 kcal running, their calorie goal increases by 300 kcal.

## Logging Health Vitals

```bash
curl -s -X POST "$NUTRITRACK_URL/api/health" \
  -H "Content-Type: application/json" \
  -d '{
    "systolic_bp": 118,
    "diastolic_bp": 76,
    "blood_sugar": 92,
    "blood_oxygen": 98,
    "heart_rate": 68
  }'
```

All fields are optional — log whatever the user provides.

## Coaching Tips

After logging food, the response includes a `coaching_tips` array with contextual advice based on current intake vs goals. Share these tips with the user naturally.

You can also fetch coaching tips independently:
```bash
curl -s "$NUTRITRACK_URL/api/coaching?date=2026-02-17"
```
Returns: tips array, current intake, and goals. Use this when the user asks for advice on what to eat next or how they're doing.

## Reading Data

### Daily Summary (most useful for "how am I doing?" questions)
```bash
curl -s "$NUTRITRACK_URL/api/daily-summary?date=2026-02-17"
```
Returns: profile, goals (BMR/TDEE/calorie goal/macro goals), intake totals, remaining amounts, food entries, activities, latest weight. Date defaults to today if omitted.

### Weekly Report
```bash
curl -s "$NUTRITRACK_URL/api/weekly-report?date=2026-02-17"
```
Returns: 7-day nutrition averages, weight change, activity totals, health averages, days over/under goal.

### Gamification Status
```bash
curl -s "$NUTRITRACK_URL/api/gamification"
```
Returns: streak_days (consecutive days under calorie goal), today_points (XP earned today), is_elite (all macros + calories met), tags (badges earned).

**XP system:** Protein met = +50, Carbs under goal = +25, Fat under goal = +25, All three (perfect bonus) = +50. Max 150/day.

### Food History
```bash
# Today's food
curl -s "$NUTRITRACK_URL/api/food?date=2026-02-17"

# Date range
curl -s "$NUTRITRACK_URL/api/food/range?start=2026-02-10&end=2026-02-17"

# Search previously logged foods
curl -s "$NUTRITRACK_URL/api/food/search?q=chicken"
```

### Weight History
```bash
curl -s "$NUTRITRACK_URL/api/weight?limit=30"
```

### Activity History
```bash
curl -s "$NUTRITRACK_URL/api/activity?date=2026-02-17"
curl -s "$NUTRITRACK_URL/api/activity/range?start=2026-02-10&end=2026-02-17"
```

### Chart Data (for analysis)
```bash
curl -s "$NUTRITRACK_URL/api/history/daily-totals?days=30"
```

## Editing and Deleting

```bash
# Update a food entry
curl -s -X PUT "$NUTRITRACK_URL/api/food/42" \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated meal", "calories": 400, "protein_g": 30, "carbs_g": 40, "fat_g": 15, "meal_type": "lunch"}'

# Delete a food entry
curl -s -X DELETE "$NUTRITRACK_URL/api/food/42"

# Same pattern for activity and health:
# PUT/DELETE /api/activity/{id}
# PUT/DELETE /api/health/{id}
```

## CSV Export

```bash
curl -s "$NUTRITRACK_URL/api/export/csv?type=food&start=2026-02-01&end=2026-02-17" -o food_export.csv
```
Types: `food`, `weight`, `activity`, `health`

## Demo Data

To seed 30 days of realistic sample data (DESTRUCTIVE — clears existing data):
```bash
curl -s -X POST "$NUTRITRACK_URL/api/seed-demo-data"
```

## Calorie Calculation Engine

NutriTrack uses the Mifflin-St Jeor equation:
- Male BMR: `10 × weight(kg) + 6.25 × height(cm) - 5 × age + 5`
- Female BMR: `10 × weight(kg) + 6.25 × height(cm) - 5 × age - 161`
- TDEE = BMR × activity multiplier (sedentary=1.2, light=1.375, moderate=1.55, active=1.725, very_active=1.9)
- Daily calorie goal = (TDEE + exercise_calories) - deficit
- Macro split: 30% protein (÷4 cal/g), 40% carbs (÷4 cal/g), 30% fat (÷9 cal/g)

## Response Style

When summarizing nutrition data for the user:
- Lead with the most important number (calories remaining or over)
- Mention protein specifically (users care about this most)
- Note the streak if it's 3+ days
- Celebrate perfect days or elite status
- If over on calories, be encouraging not judgmental
- Use the user's actual numbers, not generic advice

## Troubleshooting

- **Server not responding**: Check if Docker container is running (`docker ps | grep nutritrack`) or if the Python process is active
- **"No profile set" error**: The user needs to create their profile first (PUT /api/profile)
- **Calorie goal seems wrong**: Check if exercise has been logged — exercise calories increase the daily goal
- **Data not showing on dashboard**: The dashboard auto-refreshes every 30 seconds, or the user can manually refresh
