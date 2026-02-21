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

## Often Used Foods (Agent-Curated)

You are the curator of the user's "Often Used" tab. The dashboard does NOT auto-generate this list — you build it by reading raw history, deduplicating, normalizing, and writing a clean list.

### Step 1 — Read raw frequency data
```bash
curl -s "$NUTRITRACK_URL/api/food/history/frequent"
```
Returns items grouped by name with `count`, `min_cal/avg_cal/max_cal`, etc. This is your raw material.

### Step 2 — Think (do NOT skip)
- Merge duplicates: "Protein Powder", "Protein Powder (2 tbsp)", "protein powder" → one entry
- Pick the **minimum sensible base unit** for each item (1 egg, 100g chicken, 1 tbsp oil)
- Name format: `"Food Name (amount unit)"` — e.g. `"Boiled Egg (1 egg)"`, `"Greek Yogurt (100g)"`, `"Olive Oil (1 tbsp)"`
- Discard junk entries (unnamed, placeholder, or one-off exotic items)
- Sort by how useful/frequent the item is (most useful first)
- Max 15 items

### Step 3 — Write the curated list
```bash
curl -s -X PUT "$NUTRITRACK_URL/api/food/often-used" \
  -H "Content-Type: application/json" \
  -d '{"items": [
    {"name": "Boiled Egg (1 egg)", "calories": 78, "protein_g": 6, "carbs_g": 1, "fat_g": 5, "meal_type": "breakfast"},
    {"name": "Chicken Breast (100g)", "calories": 165, "protein_g": 31, "carbs_g": 0, "fat_g": 3.6, "meal_type": "lunch"}
  ]}'
```
This **replaces** the entire list. First item in the array = sort_order 0 (top of dashboard list).

### Step 4 — Verify
```bash
curl -s "$NUTRITRACK_URL/api/food/often-used"
```

### Quick-add (used by dashboard + button)
```bash
curl -s -X POST "$NUTRITRACK_URL/api/food/often-used/42/add"
```
Copies the item into today's food log.

### API Reference

| Action | Method | Endpoint |
|--------|--------|----------|
| Raw frequency data (for agent) | GET | `/api/food/history/frequent` |
| Write curated list (agent only) | PUT | `/api/food/often-used` |
| Read curated list (dashboard) | GET | `/api/food/often-used` |
| Quick-add to today | POST | `/api/food/often-used/{id}/add` |

### When to curate
- When the user says "update my often used tab" or similar
- After the user has 2+ weeks of food history and the list is empty
- When you notice the list is stale (items the user no longer eats)

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

## Daily Post-Meal Coaching

After EVERY time you log a food entry with POST /api/food, you MUST also update today's coaching tip. This is how it works:

1. Log the food: POST /api/food
2. Fetch the current daily summary: GET /api/daily-summary
3. Analyze the current state (calories remaining, macro balance, meal count)
4. Write a short coaching tip and save it: PUT /api/coaching/daily

PUT /api/coaching/daily
Content-Type: application/json

```json
{
    "coaching_date": "2026-02-23",
    "coaching_text": "Good protein start with eggs at breakfast. You have 1,200 kcal left and need about 80g more protein. Aim for chicken or fish at lunch to front-load protein. Keep carbs moderate — you've already had toast and oatmeal. A light dinner with salad and lean protein would close this day perfectly.",
    "meal_count": 2,
    "calories_so_far": 850,
    "calories_remaining": 1200,
    "protein_status": "low",
    "top_priority": "Get 80g more protein — chicken or fish at lunch"
}
```

### How to write coaching_text

Keep it conversational, 3-5 sentences max. Structure it as:
1. Quick assessment of what they've eaten so far (positive note first)
2. What's missing or needs attention (be specific with numbers)
3. Concrete suggestion for the next meal
4. Optional: one warning if something is trending badly (e.g., fat already at 90% of goal)

### How to set protein_status

Look at the daily summary. Calculate protein eaten vs protein goal:
- "on_track": protein is at or above expected pace for this time of day (e.g., 50%+ of goal by lunch)
- "low": protein is behind pace but recoverable (e.g., 30% of goal by lunch)
- "critical": protein is severely behind and will be very hard to catch up (e.g., <20% of goal by dinner)
- "exceeded": protein already exceeds the daily goal

### How to set top_priority

One short sentence that the user sees at a glance without expanding the panel. This is the MOST IMPORTANT thing to focus on for the rest of the day. Examples:
- "Get 80g more protein — chicken or fish at lunch"
- "You're on track! Keep dinner under 600 kcal"
- "Fat is at 95% of goal — avoid fried food and sauces tonight"
- "Great day so far — a light salad dinner gets you to elite 💠"
- "Over calorie goal by 200 — consider skipping the evening snack"

### When to update

Update the daily coaching tip EVERY time you log food. The tip should reflect the latest state. After breakfast the tip talks about lunch and dinner planning. After lunch it focuses on dinner. After dinner it either congratulates or suggests a light evening.

GET /api/coaching/daily?date=YYYY-MM-DD
Returns the current tip for a given date (defaults to today). The dashboard calls this automatically.

## Weekly Coaching Report

Your weekly coaching report appears on the dashboard's Coaching tab. Write it every Sunday or when the user asks.

### Writing a Report

1. GET /api/weekly-report — fetch weekly aggregated data
2. GET /api/gamification — fetch streak and XP
3. GET /api/food/range?start=MONDAY&end=SUNDAY — fetch individual food entries
4. Analyze all data
5. POST /api/coaching/report — save to dashboard

POST /api/coaching/report
Content-Type: application/json

```json
{
    "week_start": "2026-02-17",
    "week_end": "2026-02-23",
    "report_text": "WEEKLY HEALTH REPORT — Feb 17–23, 2026\n\nTHE NUMBERS\nYou averaged 1,850 kcal per day against a 2,100 goal...",
    "summary_json": "{\"avg_calories\": 1850, \"calorie_goal\": 2100, \"avg_protein_g\": 95, \"protein_goal_g\": 120, \"weight_start\": 84.2, \"weight_end\": 83.8, \"weight_change\": -0.4, \"streak_days\": 5, \"days_on_track\": 5, \"days_total\": 7, \"grade\": \"B+\", \"action_items\": [\"Add eggs to breakfast for +25g protein\", \"Replace afternoon biscuits with Greek yogurt\", \"Log a 30-min walk on rest days\"]}"
}
```

### Report Text Format

Use these section headers on their own lines in ALL CAPS:
WEEKLY HEALTH REPORT — [date range]
THE NUMBERS
WEIGHT CHECK
WINS THIS WEEK
WATCH OUT
FOOD SPOTLIGHT
ACTIVITY SUMMARY
ACTION ITEMS FOR NEXT WEEK
STREAK AND GAMIFICATION

Use "- " prefix for bullet points. Dashboard auto-formats these.

### summary_json Fields (all optional)

avg_calories, calorie_goal, avg_protein_g, protein_goal_g, weight_start, weight_end, weight_change, streak_days, days_on_track, days_total (always 7), grade (A+ through F), action_items (array of 3 strings)

### Grading Scale

A+: All 7 days under goal, protein met 6+, weight trending right
A: 6+ days under, protein met 5+, good activity
B+: 5 days under, decent protein, some activity
B: 4-5 days under, macros roughly on track
C+: 3-4 days under, protein consistently low
C: 2-3 days under, poor macro balance
D: 1-2 days under, minimal effort
F: 0-1 days under, no logging most days

### Reading Reports

GET /api/coaching/reports — All reports, newest first (default limit 12)
GET /api/coaching/reports/latest — Most recent only
DELETE /api/coaching/reports/{id} — Delete a report

## Troubleshooting

- **Server not responding**: Check if Docker container is running (`docker ps | grep nutritrack`) or if the Python process is active
- **"No profile set" error**: The user needs to create their profile first (PUT /api/profile)
- **Calorie goal seems wrong**: Check if exercise has been logged — exercise calories increase the daily goal
- **Data not showing on dashboard**: The dashboard auto-refreshes every 30 seconds, or the user can manually refresh
