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
- **Convention**: examples below omit `-H "Content-Type: application/json"` for brevity — always include it on POST/PUT.

## Setup & Onboarding

If the server isn't running, the user has no profile yet, or you need to seed demo data — see `onboarding.md` (installation, first-time profile creation, demo seeding).

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
  -d '{"name":"Grilled chicken breast with rice","calories":520,"protein_g":42,"carbs_g":55,"fat_g":12,"meal_type":"lunch","quantity":"200g chicken + 1 cup rice"}'
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
curl -s -X POST "$NUTRITRACK_URL/api/weight" -d '{"weight_kg":84.2,"notes":"Morning weigh-in"}'
```

Side effect: also updates the user's profile weight, recalculating calorie goals.

## Logging Exercise

```bash
curl -s -X POST "$NUTRITRACK_URL/api/activity" \
  -d '{"activity_type":"Running","duration_minutes":30,"calories_burned":350,"intensity":"moderate"}'
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

Note: exercise calories raise the day's calorie goal by the same amount (added to TDEE before the deficit).

## Logging Health Vitals

```bash
curl -s -X POST "$NUTRITRACK_URL/api/health" \
  -d '{"systolic_bp":118,"diastolic_bp":76,"blood_sugar":92,"blood_oxygen":98,"heart_rate":68}'
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
curl -s "$NUTRITRACK_URL/api/food?date=2026-02-17"                       # today
curl -s "$NUTRITRACK_URL/api/food/range?start=2026-02-10&end=2026-02-17" # range
curl -s "$NUTRITRACK_URL/api/food/search?q=chicken"                      # search
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
  -d '{"items":[{"name":"Boiled Egg (1 egg)","calories":78,"protein_g":6,"carbs_g":1,"fat_g":5,"meal_type":"breakfast"},{"name":"Chicken Breast (100g)","calories":165,"protein_g":31,"carbs_g":0,"fat_g":3.6,"meal_type":"lunch"}]}'
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

### When to curate
- When the user says "update my often used tab" or similar
- After the user has 2+ weeks of food history and the list is empty
- When you notice the list is stale (items the user no longer eats)

## Goal Mode

The user can set their daily calorie goal mode via the dashboard slider or via `PUT /api/goal-mode` with body `{"goal_mode": "deficit|maintain|surplus", "calorie_adjustment": 500}`.

**Modes:**
- `deficit`: Calorie Goal = TDEE − calorie_adjustment (weight loss)
- `maintain`: Calorie Goal = TDEE (keep current weight)
- `surplus`: Calorie Goal = TDEE + calorie_adjustment (weight gain)

`calorie_adjustment` is optional: 0–2000 in deficit, 0–1000 in surplus, ignored in maintain. `GET /api/daily-summary` returns `goal_mode`, `tdee`, `calorie_deficit`, `calorie_surplus`.

**Agent coaching awareness**: When writing daily coaching tips, reference the current mode:
- Deficit: "You have X kcal remaining in your deficit budget..."
- Maintain: "You're eating at maintenance today. X kcal left to hit your TDEE..."
- Surplus: "You still need X more kcal to hit your surplus target..."

## Editing and Deleting

```bash
curl -s -X PUT "$NUTRITRACK_URL/api/food/42" \
  -d '{"name":"Updated meal","calories":400,"protein_g":30,"carbs_g":40,"fat_g":15,"meal_type":"lunch"}'
curl -s -X DELETE "$NUTRITRACK_URL/api/food/42"
```
Same `PUT/DELETE /api/{food|activity|health}/{id}` pattern for activity and health.

## CSV Export

```bash
curl -s "$NUTRITRACK_URL/api/export/csv?type=food&start=2026-02-01&end=2026-02-17" -o food_export.csv
```
Types: `food`, `weight`, `activity`, `health`

## Background Reference

For demo-data seeding and the Mifflin-St Jeor calorie/macro formulas the server uses, see `onboarding.md`. The server computes goals automatically — you don't need the formulas to operate.

## Response Style

When summarizing nutrition data for the user:
- Lead with the most important number (calories remaining or over)
- Mention protein specifically (users care about this most)
- Note the streak if it's 3+ days
- Celebrate perfect days or elite status
- If over on calories, be encouraging not judgmental
- Use the user's actual numbers, not generic advice

## Daily Post-Meal Coaching

After EVERY `POST /api/food`, also update today's tip: fetch `GET /api/daily-summary`, analyze, then `PUT /api/coaching/daily` with these fields:

- `coaching_date` (YYYY-MM-DD)
- `coaching_text` (3–5 sentences: positive note on what they ate → what's missing with specific numbers → concrete next-meal suggestion → optional warning if a macro is trending bad, e.g. fat at 90% of goal)
- `meal_count` (int)
- `calories_so_far`, `calories_remaining` (int)
- `protein_status` — vs. protein goal, paced by time of day:
  - `"on_track"` (≥50% by lunch / on pace)
  - `"low"` (~30% by lunch, recoverable)
  - `"critical"` (<20% by dinner)
  - `"exceeded"` (over goal)
- `top_priority` — one short sentence, the single focus for the rest of the day. E.g. `"Get 80g more protein — chicken or fish at lunch"` or `"Over calorie goal by 200 — skip the evening snack"`.

`GET /api/coaching/daily?date=YYYY-MM-DD` returns the current tip (dashboard auto-fetches).

## Weekly Coaching Report

Your weekly coaching report appears on the dashboard's Coaching tab. Write it every Sunday or when the user asks.

### Writing a Report

1. GET /api/weekly-report — fetch weekly aggregated data
2. GET /api/gamification — fetch streak and XP
3. GET /api/food/range?start=MONDAY&end=SUNDAY — fetch individual food entries
4. Analyze all data
5. POST /api/coaching/report — save to dashboard

`POST /api/coaching/report` — JSON body fields:
- `week_start`, `week_end` (date, YYYY-MM-DD)
- `report_text` (string, uses ALL-CAPS section headers — see format below)
- `summary_json` (stringified JSON — see fields list below)

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

See `onboarding.md` for common issues (server down, no profile, wrong calorie goal, dashboard refresh).
