# NutriTrack — Complete Project Snapshot

**Generated:** 2026-02-17
**Purpose:** Complete knowledge transfer document for onboarding a fresh Claude session with zero prior context.

---

## 1. PROJECT OVERVIEW

### What NutriTrack Is

NutriTrack is a self-hosted, AI-agent-first nutrition and health tracking platform. It is a FastAPI (Python) backend with an SQLite database and a single-page vanilla JavaScript dashboard. There is no authentication — it's designed for single-user, local-first use.

### The Problem It Solves

Instead of manually entering food data into an app with tiny forms, the user talks to their AI assistant (any LLM — ChatGPT, Claude, Gemini, OpenClaw, etc.) in natural language. The AI agent translates natural language into structured HTTP API calls to log meals, exercise, weight, and health vitals. The dashboard then visualizes everything in real time.

### User Workflow

```
User (natural language) → AI Agent → HTTP API calls → NutriTrack Server (FastAPI) → SQLite DB
                                                              ↓
                                                      Web Dashboard (browser)
```

1. User tells their AI agent: "I had oatmeal with banana for breakfast"
2. Agent estimates macros and calls `POST /api/food` with `{"name": "Oatmeal with banana", "calories": 350, "protein_g": 12, ...}`
3. Dashboard auto-refreshes every 30 seconds and shows updated calorie ring, macro bars, food log table
4. User asks "how am I doing today?" → Agent calls `GET /api/daily-summary` and summarizes remaining calories/macros

### Key Differentiators

- **AI-Agent-First Design**: The REST API is the primary interface; the dashboard is for visualization only. Any LLM that can make HTTP calls works as the user's nutrition assistant.
- **Gamification**: Streaks (consecutive days under calorie goal), daily XP points (protein met, carbs/fat under goal, perfect day bonus), elite status badges.
- **Self-Hosted / Local-First**: Runs on localhost with SQLite. No cloud accounts, no external services. Zero-config deployment.
- **Single-File Frontend**: The entire dashboard is one HTML file (`static/dashboard.html`) with inline CSS and JS. No build step, no npm, no bundler.

---

## 2. COMPLETE FILE TREE

```
TT-Nutritrack/
├── .env.example                  # Environment variable template with defaults and docs         (22 lines,    634 bytes)
├── .gitignore                    # Git ignore rules for db, pycache, venv, .env, images        (16 lines,    163 bytes)
├── Dockerfile                    # Production Docker image based on python:3.11-slim            (21 lines,    494 bytes)
├── LICENSE                       # MIT License                                                  (21 lines,  1,101 bytes)
├── README.md                     # Project readme with features, quick start, API reference     (192 lines, 7,573 bytes)
├── app.py                        # FastAPI server — all API endpoints, Pydantic models, CORS    (917 lines, 37,940 bytes)
├── database.py                   # SQLite schema init, BMR/TDEE/macro calculations, gamification(190 lines, 6,648 bytes)
├── dev.sh                        # Dev mode launcher (Docker or bare metal with auto-reload)    (27 lines,  1,104 bytes)
├── docker-compose.dev.yml        # Dev overrides: live code mount + uvicorn --reload             (19 lines,    741 bytes)
├── docker-compose.yml            # Production Docker Compose with named volume                  (27 lines,    702 bytes)
├── docs/
│   └── AGENT_README.md           # Comprehensive AI agent integration guide with all endpoints  (1,286 lines, 39,675 bytes)
├── fix_timestamps.py             # One-time migration utility: converts space to T in timestamps(29 lines,    744 bytes)
├── install.sh                    # Interactive installer: checks Python, creates venv, seeds DB (97 lines,  3,894 bytes)
├── migrate.py                    # One-time migration from old nutrition tracker DB format       (113 lines, 4,424 bytes)
├── requirements.txt              # Python dependencies: fastapi, uvicorn, aiofiles, pydantic    (4 lines,     34 bytes)
├── seed.py                       # Standalone seeder: 30 days of realistic demo data            (187 lines, 7,396 bytes)
├── setup.sh                      # Simple setup script: pip install + init db + start server    (31 lines,    936 bytes)
├── start.sh                      # Start server (requires venv from install.sh)                 (5 lines,    208 bytes)
├── static/
│   └── dashboard.html            # Complete single-page dashboard: HTML + CSS + JS              (1,647 lines, 84,966 bytes)
├── stop.sh                       # Kill running server process                                  (2 lines,    117 bytes)
└── test_profile_update.py        # Quick test script for PUT /api/profile endpoint              (23 lines,    590 bytes)
```

**Total non-git files:** 21 source files
**Note:** `migrate.py` and `fix_timestamps.py` are one-time migration utilities from a previous tracker format. They reference hardcoded paths to the old database and are not used in normal operation.

---

## 3. TECH STACK

### Backend

| Technology | Version / Detail |
|---|---|
| Python | 3.11 (Docker image) / 3.14.2 (host system) |
| FastAPI | Latest (no pinned version in requirements.txt) |
| Uvicorn | Latest (ASGI server) |
| Pydantic | Latest (request validation) |
| aiofiles | Latest (async file serving) |
| SQLite | Built-in (stdlib `sqlite3`), WAL mode, foreign keys ON |

### requirements.txt (exact contents)

```
fastapi
uvicorn
aiofiles
pydantic
```

### Frontend (CDN Dependencies)

| Library | CDN URL |
|---|---|
| Chart.js 4.4.1 | `https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js` |
| chartjs-adapter-date-fns 3.0.0 | `https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns@3.0.0/dist/chartjs-adapter-date-fns.bundle.min.js` |
| Google Fonts (DM Sans + Space Mono) | `https://fonts.googleapis.com/css2?family=DM+Sans:...&family=Space+Mono:...` |

### System Dependencies

- Python 3.10+ (3.11 in Docker image)
- Docker & Docker Compose (optional, for containerized deployment)
- No external database server (SQLite is embedded)
- No Node.js, no npm, no build tools

---

## 4. DATABASE SCHEMA — FULL DUMP

The database is a single SQLite file. Default path: `nutritrack.db` in the project directory (overridden by `NUTRITRACK_DB_PATH` env var). WAL journal mode and foreign keys are enabled on every connection.

### Exact CREATE TABLE Statements (from `database.py` `init_db()`)

```sql
CREATE TABLE IF NOT EXISTS user_profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    age INTEGER NOT NULL,
    sex TEXT NOT NULL CHECK(sex IN ('male', 'female')),
    height_cm REAL NOT NULL,
    current_weight_kg REAL NOT NULL,
    activity_level TEXT NOT NULL DEFAULT 'moderate' CHECK(activity_level IN ('sedentary', 'light', 'moderate', 'active', 'very_active')),
    weight_goal_kg REAL,
    calorie_deficit INTEGER NOT NULL DEFAULT 500,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS food_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    calories REAL NOT NULL DEFAULT 0,
    protein_g REAL NOT NULL DEFAULT 0,
    carbs_g REAL NOT NULL DEFAULT 0,
    fat_g REAL NOT NULL DEFAULT 0,
    meal_type TEXT DEFAULT 'snack' CHECK(meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')),
    quantity TEXT,
    notes TEXT,
    logged_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS weight_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    weight_kg REAL NOT NULL,
    notes TEXT,
    measured_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sport_activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    activity_type TEXT NOT NULL,
    duration_minutes INTEGER NOT NULL DEFAULT 0,
    calories_burned REAL NOT NULL DEFAULT 0,
    intensity TEXT DEFAULT 'moderate' CHECK(intensity IN ('low', 'moderate', 'high')),
    notes TEXT,
    performed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS health_measurements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    systolic_bp INTEGER,
    diastolic_bp INTEGER,
    blood_sugar REAL,
    blood_oxygen REAL,
    heart_rate INTEGER,
    notes TEXT,
    measured_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### Indexes

```sql
CREATE INDEX IF NOT EXISTS idx_food_logged_at ON food_entries(logged_at);
CREATE INDEX IF NOT EXISTS idx_weight_measured_at ON weight_logs(measured_at);
CREATE INDEX IF NOT EXISTS idx_activity_performed_at ON sport_activities(performed_at);
CREATE INDEX IF NOT EXISTS idx_health_measured_at ON health_measurements(measured_at);
```

### Table Relationships and Side Effects

- **user_profile**: Single-row table (app always reads `ORDER BY id DESC LIMIT 1`). `PUT /api/profile` does upsert logic: UPDATE if exists, INSERT if not. On first INSERT, also inserts a weight_logs entry.
- **weight_logs → user_profile**: `POST /api/weight` inserts into weight_logs AND runs `UPDATE user_profile SET current_weight_kg=?` to keep the profile in sync. This means logging weight also changes the calorie calculation base.
- **food_entries**: No foreign keys. Standalone table. `logged_at` is the user-specified or auto-generated timestamp used for date filtering.
- **sport_activities**: No foreign keys. `calories_burned` feeds back into the daily calorie goal calculation via the `calculate_daily_goals()` function.
- **health_measurements**: No foreign keys. All measurement columns are nullable — you can log just one vital per entry.

---

## 5. COMPLETE API REFERENCE

Base URL: `http://localhost:8000`
Auto-generated Swagger docs: `http://localhost:8000/docs`
Content-Type: `application/json`
Authentication: None

### Pydantic Models (exact definitions from `app.py`)

```python
class ProfileCreate(BaseModel):
    age: int = Field(..., ge=10, le=120)
    sex: str = Field(..., pattern="^(male|female)$")
    height_cm: float = Field(..., ge=50, le=300)
    current_weight_kg: float = Field(..., ge=20, le=500)
    activity_level: str = Field(default="moderate")
    weight_goal_kg: Optional[float] = None
    calorie_deficit: int = Field(default=500, ge=0, le=2000)

class FoodEntry(BaseModel):
    name: str
    calories: float = 0
    protein_g: float = 0
    carbs_g: float = 0
    fat_g: float = 0
    meal_type: str = "snack"
    quantity: Optional[str] = None
    notes: Optional[str] = None
    logged_at: Optional[str] = None # ISO format, defaults to now

class WeightEntry(BaseModel):
    weight_kg: float = Field(..., ge=20, le=500)
    notes: Optional[str] = None
    measured_at: Optional[str] = None

class ActivityEntry(BaseModel):
    activity_type: str
    duration_minutes: int = 0
    calories_burned: float = 0
    intensity: str = "moderate"
    notes: Optional[str] = None
    performed_at: Optional[str] = None

class HealthEntry(BaseModel):
    systolic_bp: Optional[int] = None
    diastolic_bp: Optional[int] = None
    blood_sugar: Optional[float] = None
    blood_oxygen: Optional[float] = None
    heart_rate: Optional[int] = None
    notes: Optional[str] = None
    measured_at: Optional[str] = None
```

### Endpoint Reference

#### Dashboard

| Method | Path | Description |
|---|---|---|
| GET | `/` | Serves `static/dashboard.html` with no-cache headers |

#### Profile

| Method | Path | Query Params | Request Body | Response | Side Effects |
|---|---|---|---|---|---|
| GET | `/api/profile` | — | — | `{"profile": {...} or null, "message": "..."}` | — |
| PUT | `/api/profile` | — | `ProfileCreate` | `{"profile": {...}, "message": "..."}` | Upserts profile. On first create, also inserts a weight_logs entry. |

#### Food

| Method | Path | Query Params | Request Body | Response |
|---|---|---|---|---|
| POST | `/api/food` | — | `FoodEntry` | `{"entry": {...}, "message": "Logged: ... (X kcal)"}` |
| GET | `/api/food` | `date` (optional, YYYY-MM-DD, default=today) | — | `{"entries": [...], "count": N}` |
| GET | `/api/food/search` | `q` (required, min 1 char) | — | `{"results": [...], "count": N}` (max 20 distinct) |
| GET | `/api/food/range` | `start`, `end` (YYYY-MM-DD) | — | `{"entries": [...], "count": N}` |
| PUT | `/api/food/{entry_id}` | — | `FoodEntry` | `{"entry": {...}, "message": "..."}` or 404 |
| DELETE | `/api/food/{entry_id}` | — | — | `{"message": "Food entry N deleted."}` |

#### Weight

| Method | Path | Query Params | Request Body | Response | Side Effects |
|---|---|---|---|---|---|
| POST | `/api/weight` | — | `WeightEntry` | `{"entry": {...}, "message": "Weight logged: X kg"}` | Also updates `user_profile.current_weight_kg` |
| GET | `/api/weight` | `limit` (default=90) | — | `{"entries": [...], "count": N}` (newest first) |

#### Activity

| Method | Path | Query Params | Request Body | Response |
|---|---|---|---|---|
| POST | `/api/activity` | — | `ActivityEntry` | `{"entry": {...}, "message": "Activity logged: ..."}` |
| GET | `/api/activity` | `date` (optional, default=today) | — | `{"entries": [...], "count": N}` |
| GET | `/api/activity/range` | `start`, `end` (YYYY-MM-DD) | — | `{"entries": [...], "count": N}` |
| PUT | `/api/activity/{entry_id}` | — | `ActivityEntry` | `{"entry": {...}, "message": "..."}` or 404 |
| DELETE | `/api/activity/{entry_id}` | — | — | `{"message": "Activity entry N deleted."}` |

#### Health

| Method | Path | Query Params | Request Body | Response |
|---|---|---|---|---|
| POST | `/api/health` | — | `HealthEntry` | `{"entry": {...}, "message": "Health measurement logged."}` |
| GET | `/api/health` | `limit` (default=90) | — | `{"entries": [...], "count": N}` (newest first) |
| PUT | `/api/health/{entry_id}` | — | `HealthEntry` | `{"entry": {...}, "message": "..."}` or 404 |
| DELETE | `/api/health/{entry_id}` | — | — | `{"message": "Health entry N deleted."}` |

#### Reports

| Method | Path | Query Params | Response |
|---|---|---|---|
| GET | `/api/daily-summary` | `date` (optional, default=today) | Full daily overview: profile, goals, intake, remaining, food_entries, activities, latest_weight |
| GET | `/api/weekly-report` | `date` (optional, default=today, end of 7-day window) | 7-day aggregated: nutrition averages, weight change, activity totals, health averages |
| GET | `/api/history/daily-totals` | `days` (default=30) | Array of `{date, calories, protein_g, carbs_g, fat_g, activity_calories, calorie_goal, ...}` for charting |

#### Gamification

| Method | Path | Query Params | Response |
|---|---|---|---|
| GET | `/api/gamification` | — | `{streak_days, today_points, is_elite, calorie_success, tags: [...]}` |

#### Export

| Method | Path | Query Params | Response |
|---|---|---|---|
| GET | `/api/export/csv` | `type` (required: food/weight/activity/health), `start`/`end` (optional YYYY-MM-DD) | CSV file download |

#### Seed

| Method | Path | Request Body | Response | Side Effects |
|---|---|---|---|---|
| POST | `/api/seed-demo-data` | — | `{"message": "Demo data seeded..."}` | **DESTRUCTIVE**: Deletes ALL existing data, then inserts 30 days of demo data |

---

## 6. CALORIE & MACRO CALCULATION ENGINE

All calculation functions live in `database.py`.

### Activity Multipliers

```python
ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9,
}
```

### BMR Calculation (Mifflin-St Jeor)

```python
def calculate_bmr(weight_kg: float, height_cm: float, age: int, sex: str) -> float:
    """Mifflin-St Jeor BMR equation."""
    bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age
    if sex == "male":
        bmr += 5
    else:
        bmr -= 161
    return round(bmr, 1)
```

**Formula:**
- Male: `BMR = 10 × weight(kg) + 6.25 × height(cm) - 5 × age + 5`
- Female: `BMR = 10 × weight(kg) + 6.25 × height(cm) - 5 × age - 161`

### TDEE Calculation

```python
def calculate_tdee(bmr: float, activity_level: str) -> float:
    """TDEE = BMR × activity multiplier."""
    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, 1.55)
    return round(bmr * multiplier, 1)
```

### Daily Goals Calculation (with Dynamic Exercise Adjustment)

```python
def calculate_daily_goals(profile: dict, activity_calories: float = 0) -> dict:
    """Calculate full daily goals from profile + extra activity."""
    bmr = calculate_bmr(
        profile["current_weight_kg"], profile["height_cm"], profile["age"], profile["sex"]
    )
    tdee = calculate_tdee(bmr, profile["activity_level"])
    deficit = profile.get("calorie_deficit", 500)

    # Add exercise calories to TDEE before applying deficit
    effective_tdee = tdee + activity_calories
    calorie_goal = effective_tdee - deficit

    # Macro split: 30% protein, 40% carbs, 30% fat
    protein_goal = round((calorie_goal * 0.30) / 4, 1)   # 4 cal/g protein
    carbs_goal = round((calorie_goal * 0.40) / 4, 1)     # 4 cal/g carbs
    fat_goal = round((calorie_goal * 0.30) / 9, 1)       # 9 cal/g fat

    return {
        "bmr": bmr,
        "tdee": tdee,
        "activity_calories": activity_calories,
        "effective_tdee": effective_tdee,
        "calorie_deficit": deficit,
        "calorie_goal": round(calorie_goal, 1),
        "protein_goal_g": protein_goal,
        "carbs_goal_g": carbs_goal,
        "fat_goal_g": fat_goal,
    }
```

**Key insight — dynamic exercise adjustment:** Exercise calories are added to TDEE BEFORE subtracting the deficit. This means if you burn 300 kcal running, your allowed calorie intake for the day increases by 300 kcal. The formula is:

```
calorie_goal = (TDEE + exercise_calories) - deficit
```

### Macro Split

- **Protein**: 30% of calorie_goal ÷ 4 cal/g
- **Carbs**: 40% of calorie_goal ÷ 4 cal/g
- **Fat**: 30% of calorie_goal ÷ 9 cal/g

---

## 7. FRONTEND ARCHITECTURE

The entire frontend is `static/dashboard.html` — a single 1,647-line HTML file with inline `<style>` and `<script>` blocks. No external JS files, no build step.

### Tabs

| Tab | ID | What It Displays |
|---|---|---|
| Overview | `tab-overview` | Calorie ring, macro progress bars, weight/goal/deficit stats, food log table, activities list |
| Charts | `tab-charts` | Calorie history (bar+line), macro tracking (line), weight trend (line), activity chart (bar+line) |
| Health | `tab-health` | Latest health vitals cards (BP, sugar, O2, HR) with status badges, BP history chart, sugar/oxygen chart |
| Profile | `tab-profile` | Profile edit form, calculated targets display, "Seed Demo Data" button |

### JavaScript Functions

#### State & Init

| Function | Description |
|---|---|
| `DOMContentLoaded` handler | Sets date selector to today, inits tabs, loads overview, loads profile, starts polling, sets up modal close on overlay click |
| `startPolling()` | Sets 30-second interval to auto-refresh overview tab if it's active |
| `stopPolling()` | Clears the polling interval |
| `visibilitychange` handler | Stops polling when tab is hidden, resumes + refreshes when visible |

#### Date Navigation

| Function | Description |
|---|---|
| `changeDate(delta)` | Moves currentDate by +/- 1 day, refreshes overview |
| `onDateChange()` | Reads date from the date picker input, refreshes overview |
| `goToday()` | Resets to today's date, refreshes overview |

#### Tabs

| Function | Description |
|---|---|
| `initTabs()` | Attaches click handlers to tab buttons; activates corresponding panel; triggers data load for charts/health/profile tabs |

#### Modal Helpers

| Function | Description |
|---|---|
| `openModal(type)` | Shows the modal overlay for food/weight/activity/health |
| `closeModal(type)` | Hides the modal overlay |
| `showModalMsg(id, text, isError)` | Shows a temporary message in a modal (auto-hides after 3s) |
| `submitFood()` | Validates food form, POSTs to `/api/food`, refreshes overview |
| `submitWeight()` | Validates weight form, POSTs to `/api/weight`, refreshes overview |
| `submitActivity()` | Validates activity form, POSTs to `/api/activity`, refreshes overview |
| `submitHealth()` | Validates health form, POSTs to `/api/health`, refreshes health tab |
| `seedDemoData()` | Confirms with user, POSTs to `/api/seed-demo-data`, refreshes all |

#### Gamification

| Function | Description |
|---|---|
| `loadGamification()` | Fetches `/api/gamification`, updates streak count, daily points, and status badges. Shows blue diamond icon for elite, fire icon for normal. Renders badge pills for protein_met, carbs_good, fat_good, perfect_bonus. |

#### Overview

| Function | Description |
|---|---|
| `loadOverview()` | Main data loader. Calls `loadGamification()`, fetches `/api/daily-summary?date=currentDate`, updates calorie ring, macro bars, weight/goal stats, food log, activities list |
| `updateMacroBar(macro, value, goal)` | Updates a single macro progress bar (protein/carbs/fat) |
| `renderFoodLog(entries)` | Renders the food log `<table>` with time, meal badge, name, qty, kcal, P/C/F, duplicate/delete buttons |
| `renderActivities(activities)` | Renders the activity list with type, duration, intensity, calories burned |
| `deleteFood(id)` | Confirms and DELETEs `/api/food/{id}`, refreshes overview |
| `duplicateFood(id)` | Fetches current food entries, finds matching id, POSTs a copy with current timestamp |

#### Charts

| Function | Description |
|---|---|
| `loadCharts(days, btn)` | Fetches daily totals, weight, and activity data in parallel, renders all 4 charts |
| `daysAgo(n)` | Returns ISO date string for N days ago |
| `today()` | Returns today's ISO date string |
| `destroyChart(key)` | Destroys an existing Chart.js instance before re-creating |
| `renderCalorieChart(data)` | Bar chart of daily calorie intake + dashed line for goal |
| `renderMacroChart(data)` | Line chart with 3 datasets: protein, carbs, fat (all with fill) |
| `renderWeightChart(entries)` | Line chart of weight over time (purple, filled) |
| `renderActivityChart(entries)` | Grouped by date. Bar chart for duration (yellow), line for calories burned (red, right Y axis) |

#### Health

| Function | Description |
|---|---|
| `loadHealth()` | Fetches `/api/health?limit=90`, updates latest vital cards with values and status badges (Normal/Elevated/High etc.), renders BP and sugar/oxygen charts |
| `renderBPChart(entries)` | Line chart: systolic (red) + diastolic (blue) |
| `renderSugarOxyChart(entries)` | Dual-axis line chart: blood sugar (yellow, left Y) + SpO2 (green, right Y, min 85 max 100) |

#### Profile

| Function | Description |
|---|---|
| `loadProfile()` | Fetches `/api/profile`, fills the form inputs, calls `updateCalcTargets()` |
| `updateCalcTargets(p)` | Client-side calculation of BMR/TDEE/goals (mirrors server logic) for instant display |
| `saveProfile()` | Reads form inputs, PUTs to `/api/profile`, shows success message, refreshes overview |

### Chart.js Charts (6 total)

| Chart ID | Type | Data Source | X Axis | Y Axis | Notes |
|---|---|---|---|---|---|
| `calorieChart` | Bar + Line | `/api/history/daily-totals` | Date (MM-DD) | Calories | Green bars = intake, red dashed line = goal |
| `macroChart` | Line (3 datasets) | `/api/history/daily-totals` | Date (MM-DD) | Grams | Protein (blue), carbs (yellow), fat (red), all filled |
| `weightChart` | Line | `/api/weight` | Date | kg | Purple line with fill, 4px point radius |
| `activityChart` | Bar + Line | `/api/activity/range` | Date (MM-DD) | Duration (left), Calories (right) | Yellow bars = duration, red line = calories burned |
| `bpChart` | Line (2 datasets) | `/api/health` | Date | mmHg | Red = systolic, blue = diastolic |
| `sugarOxyChart` | Line (2 datasets, dual axis) | `/api/health` | Date | mg/dL (left), % (right) | Yellow = blood sugar, green = SpO2 |

### Gamification UI Elements

- **Streak Display**: Fire icon (🔥) or blue diamond (💠 for elite) + number + "days under limit" text
- **Daily XP**: Lightning bolt (⚡) + number + "points" text
- **Status Badges**: Colored pills rendered dynamically:
  - `protein_met` → "Protein Goal" (blue)
  - `carbs_good` → "Carbs OK" (yellow)
  - `fat_good` → "Fat OK" (red)
  - `perfect_bonus` → "PERFECT DAY" (green)
  - No tags → "No activity yet" (gray)

### CSS Custom Properties (Theme Variables)

```css
:root {
    --bg: #0d0f11;            /* Page background (near-black) */
    --surface: #161a1f;       /* Card background */
    --surface2: #1c2127;      /* Nested surface / input background */
    --border: #2a3038;        /* Border color */
    --text: #e8ecf0;          /* Primary text */
    --text-dim: #8892a0;      /* Secondary/muted text */
    --accent: #3ecf8e;        /* Primary accent (green) */
    --accent-dim: rgba(62, 207, 142, 0.15); /* Accent background */
    --protein: #60a5fa;       /* Protein color (blue) */
    --carbs: #fbbf24;         /* Carbs color (yellow) */
    --fat: #f87171;           /* Fat color (red) */
    --calories: #3ecf8e;      /* Calories color (green, same as accent) */
    --danger: #ef4444;        /* Error/danger (red) */
    --warning: #f59e0b;       /* Warning (amber) */
    --radius: 12px;           /* Border radius */
    --shadow: 0 2px 12px rgba(0,0,0,0.3); /* Card shadow */
}
```

### Auto-Refresh / Polling Behavior

- **30-second polling**: When the Overview tab is active, `loadOverview()` is called every 30 seconds (`POLL_INTERVAL_MS = 30000`).
- **Visibility change**: Polling stops when the browser tab is hidden, resumes when visible.
- **Manual refresh**: Any data entry (food, weight, activity) triggers `loadOverview()` after a 800ms delay.

---

## 8. GAMIFICATION SYSTEM

### Gamification Calculation Function (from `database.py`)

```python
def calculate_gamification(daily_data: dict, goals: dict):
    """
    Calculate points and streak status for a single day.
    daily_data: {'calories': x, 'protein_g': y, 'carbs_g': z, 'fat_g': w}
    goals: output of calculate_daily_goals
    """
    points = 0
    status = []

    # 1. Calorie Check (Basis for Streak)
    calorie_success = daily_data['calories'] <= goals['calorie_goal']

    # 2. Protein Check (High Priority)
    protein_success = daily_data['protein_g'] >= goals['protein_goal_g']
    if protein_success:
        points += 50
        status.append("protein_met")

    # 3. Carbs Check
    carbs_success = daily_data['carbs_g'] <= goals['carbs_goal_g']
    if carbs_success:
        points += 25
        status.append("carbs_good")

    # 4. Fat Check
    fat_success = daily_data['fat_g'] <= goals['fat_goal_g']
    if fat_success:
        points += 25
        status.append("fat_good")

    # 5. Perfect Day Bonus
    is_elite = False
    if protein_success and carbs_success and fat_success:
        points += 50
        status.append("perfect_bonus")
        if calorie_success:
            is_elite = True

    return {
        "points": int(points),
        "calorie_success": calorie_success,
        "is_elite": is_elite,
        "tags": status
    }
```

### How Streaks Work

- A streak counts **consecutive days (backwards from yesterday)** where the user stayed at or under their calorie goal.
- Today does NOT count toward the streak (it's still in progress). Today's status is shown as "elite" or not.
- The streak calculation starts from yesterday and goes back up to 30 days.
- **Streak breaks when**: A day has zero food logged (no data), OR calories exceeded the calorie goal for that day.
- Streak is calculated in `GET /api/gamification` endpoint.

### How XP Points Are Earned (per day)

| Condition | Points |
|---|---|
| Protein intake >= protein goal | +50 |
| Carbs intake <= carbs goal | +25 |
| Fat intake <= fat goal | +25 |
| ALL THREE above met (perfect bonus) | +50 |
| **Maximum possible per day** | **150** |

Note: Calorie success is NOT directly worth points — it determines streak and elite status.

### Elite Status

A day is "elite" when ALL of the following are true:
1. Protein met (>= goal)
2. Carbs under (≤ goal)
3. Fat under (≤ goal)
4. Calories under (≤ goal)

Elite shows as 💠 blue diamond icon instead of 🔥 fire.

### Badges / Status Tags

| Tag | Display Text | Color | Condition |
|---|---|---|---|
| `protein_met` | "Protein Goal" | Blue (#60a5fa) | protein_g >= protein_goal_g |
| `carbs_good` | "Carbs OK" | Yellow (#fbbf24) | carbs_g <= carbs_goal_g |
| `fat_good` | "Fat OK" | Red (#f87171) | fat_g <= fat_goal_g |
| `perfect_bonus` | "PERFECT DAY" | Green (#3ecf8e) | All three macro checks pass |

### Database Tables Powering Gamification

The gamification system does NOT have its own database table. It's calculated on-the-fly from:
- `food_entries` (calorie and macro totals per day)
- `sport_activities` (exercise calories for goal adjustment)
- `user_profile` (for calculating daily goals)

The `GET /api/gamification` endpoint queries these tables directly.

### Levels System

There is currently **no persistent level system**. XP points are calculated per-day only and not accumulated. There are no level thresholds or lifetime XP tracking. This would be a natural extension point.

---

## 9. DEPLOYMENT CONFIGURATION

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `NUTRITRACK_DB_PATH` | `nutritrack.db` (in project dir) | Path to SQLite database file |
| `NUTRITRACK_HOST` | `0.0.0.0` | Server bind address |
| `NUTRITRACK_PORT` | `8000` | Server port |
| `NUTRITRACK_CORS_ORIGINS` | `*` | CORS allowed origins (comma-separated or `*`) |
| `SEED_DEMO_DATA` | `false` | Auto-seed demo data on first startup when DB is empty |
| `TZ` | `UTC` | Timezone (Docker) |
| `NUTRITRACK_DEV_MODE` | (unset) | Set in docker-compose.dev.yml (currently unused in code) |

### .env.example (full contents)

```
# NutriTrack Configuration
# Copy this to .env and modify as needed

# Port to expose NutriTrack on (default: 8000)
NUTRITRACK_PORT=8000

# Server bind address (default: 0.0.0.0)
# Use 127.0.0.1 to restrict to localhost only
NUTRITRACK_HOST=0.0.0.0

# Path to SQLite database file (default: nutritrack.db in project dir)
# NUTRITRACK_DB_PATH=/app/data/nutritrack.db

# CORS allowed origins (default: * for all origins)
# Comma-separated list or * for all
NUTRITRACK_CORS_ORIGINS=*

# Timezone (default: UTC)
TZ=UTC

# Auto-seed demo data on first run when database is empty (default: false)
SEED_DEMO_DATA=false
```

### Dockerfile (full contents)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/data

ENV NUTRITRACK_DB_PATH=/app/data/nutritrack.db
ENV NUTRITRACK_HOST=0.0.0.0
ENV NUTRITRACK_PORT=8000

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/profile')" || exit 1

CMD ["python3", "app.py"]
```

### docker-compose.yml (full contents)

```yaml
version: "3.8"

services:
  nutritrack:
    build: .
    container_name: nutritrack
    restart: unless-stopped
    ports:
      - "${NUTRITRACK_PORT:-8000}:8000"
    volumes:
      - nutritrack_data:/app/data
    environment:
      - NUTRITRACK_DB_PATH=/app/data/nutritrack.db
      - NUTRITRACK_HOST=0.0.0.0
      - NUTRITRACK_PORT=8000
      - SEED_DEMO_DATA=${SEED_DEMO_DATA:-false}
      - TZ=${TZ:-UTC}
    healthcheck:
      test: ["CMD", "python3", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/profile')"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s

volumes:
  nutritrack_data:
    driver: local
```

### docker-compose.dev.yml (full contents)

```yaml
# docker-compose.dev.yml — DEVELOPMENT OVERRIDES
# Usage: docker compose -f docker-compose.yml -f docker-compose.dev.yml up
version: "3.8"

services:
  nutritrack:
    volumes:
      # Mount live source code — changes on host are instantly visible in container
      - ./app.py:/app/app.py
      - ./database.py:/app/database.py
      - ./seed.py:/app/seed.py
      - ./static:/app/static
      - ./docs:/app/docs
      # Keep the persistent data volume from the base compose
      - nutritrack_data:/app/data
    environment:
      - NUTRITRACK_DEV_MODE=true
    # Override CMD to enable auto-reload on Python file changes
    command: python3 -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload --reload-dir /app
```

### install.sh Logic (step by step)

1. Checks for Python 3.10+ (tries `python3` then `python`)
2. Creates a `venv/` virtual environment if it doesn't exist
3. Activates the venv
4. Installs/upgrades pip, installs requirements.txt
5. Initializes the database by running `python3 database.py`
6. Asks user if they want to seed 30 days of demo data (interactive y/n)
7. If yes, runs `python3 seed.py --force`
8. Prints dashboard URL and startup instructions
9. Starts the server with `python3 app.py`

### start.sh (full contents)

```bash
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate 2>/dev/null || { echo "Run ./install.sh first"; exit 1; }
echo "NutriTrack starting at http://localhost:${NUTRITRACK_PORT:-8000}"
python3 app.py
```

### stop.sh (full contents)

```bash
#!/bin/bash
pkill -f "python3 app.py" 2>/dev/null && echo "NutriTrack stopped" || echo "NutriTrack is not running"
```

### dev.sh (full contents)

```bash
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
```

### setup.sh (full contents)

```bash
#!/bin/bash
# NutriTrack Setup & Run Script
set -e

echo "╔══════════════════════════════════════╗"
echo "║ NutriTrack — Setup & Launch          ║"
echo "╚══════════════════════════════════════╝"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is required. Please install Python 3.10+."
    exit 1
fi

echo "📦 Installing dependencies..."
pip install -r requirements.txt --break-system-packages --quiet 2>/dev/null || \
pip install -r requirements.txt --quiet

echo "🗄️ Initializing database..."
python3 database.py

echo ""
echo "🚀 Starting NutriTrack server..."
echo "   Dashboard: http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo ""
echo "   Press Ctrl+C to stop."
echo ""

python3 app.py
```

---

## 10. CORS & MIDDLEWARE

### CORS Configuration (from `app.py`)

```python
cors_origins_raw = os.environ.get("NUTRITRACK_CORS_ORIGINS", "*")
CORS_ORIGINS = ["*"] if cors_origins_raw == "*" else [o.strip() for o in cors_origins_raw.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

- Default: Allow all origins (`*`)
- Can be restricted via `NUTRITRACK_CORS_ORIGINS` env var (comma-separated list)
- All methods and headers are allowed
- Credentials are allowed

### Other Middleware

- **Static files**: `app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")` — serves the `static/` directory
- **No authentication middleware** — the app has no auth
- **No rate limiting** — no rate limit middleware
- **No logging middleware** — uses default FastAPI/uvicorn logging

### Startup Event

```python
@app.on_event("startup")
def startup():
    init_db()
    # Auto-seed demo data on first run if configured
    if os.environ.get("SEED_DEMO_DATA", "false").lower() == "true":
        conn = get_db()
        has_data = conn.execute("SELECT COUNT(*) FROM food_entries").fetchone()[0]
        conn.close()
        if has_data == 0:
            seed_demo_data()
            print("Auto-seeded demo data.")
```

---

## 11. KEY CODE SECTIONS — VERBATIM

### database.py: DB_PATH and get_db()

```python
DB_PATH = os.environ.get(
    "NUTRITRACK_DB_PATH",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "nutritrack.db")
)

def get_db():
    """Get a database connection with row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn
```

### database.py: init_db() — full function

```python
def init_db():
    """Initialize all database tables."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS user_profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            age INTEGER NOT NULL,
            sex TEXT NOT NULL CHECK(sex IN ('male', 'female')),
            height_cm REAL NOT NULL,
            current_weight_kg REAL NOT NULL,
            activity_level TEXT NOT NULL DEFAULT 'moderate' CHECK(activity_level IN ('sedentary', 'light', 'moderate', 'active', 'very_active')),
            weight_goal_kg REAL,
            calorie_deficit INTEGER NOT NULL DEFAULT 500,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS food_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            calories REAL NOT NULL DEFAULT 0,
            protein_g REAL NOT NULL DEFAULT 0,
            carbs_g REAL NOT NULL DEFAULT 0,
            fat_g REAL NOT NULL DEFAULT 0,
            meal_type TEXT DEFAULT 'snack' CHECK(meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')),
            quantity TEXT,
            notes TEXT,
            logged_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS weight_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            weight_kg REAL NOT NULL,
            notes TEXT,
            measured_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS sport_activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_type TEXT NOT NULL,
            duration_minutes INTEGER NOT NULL DEFAULT 0,
            calories_burned REAL NOT NULL DEFAULT 0,
            intensity TEXT DEFAULT 'moderate' CHECK(intensity IN ('low', 'moderate', 'high')),
            notes TEXT,
            performed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS health_measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            systolic_bp INTEGER,
            diastolic_bp INTEGER,
            blood_sugar REAL,
            blood_oxygen REAL,
            heart_rate INTEGER,
            notes TEXT,
            measured_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_food_logged_at ON food_entries(logged_at);
        CREATE INDEX IF NOT EXISTS idx_weight_measured_at ON weight_logs(measured_at);
        CREATE INDEX IF NOT EXISTS idx_activity_performed_at ON sport_activities(performed_at);
        CREATE INDEX IF NOT EXISTS idx_health_measured_at ON health_measurements(measured_at);
    """)
    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")
```

### database.py: calculate_daily_goals() — full function

```python
def calculate_daily_goals(profile: dict, activity_calories: float = 0) -> dict:
    """Calculate full daily goals from profile + extra activity."""
    bmr = calculate_bmr(
        profile["current_weight_kg"], profile["height_cm"], profile["age"], profile["sex"]
    )
    tdee = calculate_tdee(bmr, profile["activity_level"])
    deficit = profile.get("calorie_deficit", 500)

    # Add exercise calories to TDEE before applying deficit
    effective_tdee = tdee + activity_calories
    calorie_goal = effective_tdee - deficit

    # Macro split: 30% protein, 40% carbs, 30% fat
    protein_goal = round((calorie_goal * 0.30) / 4, 1)
    carbs_goal = round((calorie_goal * 0.40) / 4, 1)
    fat_goal = round((calorie_goal * 0.30) / 9, 1)

    return {
        "bmr": bmr,
        "tdee": tdee,
        "activity_calories": activity_calories,
        "effective_tdee": effective_tdee,
        "calorie_deficit": deficit,
        "calorie_goal": round(calorie_goal, 1),
        "protein_goal_g": protein_goal,
        "carbs_goal_g": carbs_goal,
        "fat_goal_g": fat_goal,
    }
```

### database.py: calculate_gamification() — full function

```python
def calculate_gamification(daily_data: dict, goals: dict):
    """
    Calculate points and streak status for a single day.
    daily_data: {'calories': x, 'protein_g': y, 'carbs_g': z, 'fat_g': w}
    goals: output of calculate_daily_goals
    """
    points = 0
    status = []

    # 1. Calorie Check (Basis for Streak)
    calorie_success = daily_data['calories'] <= goals['calorie_goal']

    # 2. Protein Check (High Priority)
    protein_success = daily_data['protein_g'] >= goals['protein_goal_g']
    if protein_success:
        points += 50
        status.append("protein_met")

    # 3. Carbs Check
    carbs_success = daily_data['carbs_g'] <= goals['carbs_goal_g']
    if carbs_success:
        points += 25
        status.append("carbs_good")

    # 4. Fat Check
    fat_success = daily_data['fat_g'] <= goals['fat_goal_g']
    if fat_success:
        points += 25
        status.append("fat_good")

    # 5. Perfect Day Bonus
    is_elite = False
    if protein_success and carbs_success and fat_success:
        points += 50
        status.append("perfect_bonus")
        if calorie_success:
            is_elite = True

    return {
        "points": int(points),
        "calorie_success": calorie_success,
        "is_elite": is_elite,
        "tags": status
    }
```

### app.py: Helper functions

```python
def row_to_dict(row):
    if row is None: return None
    return dict(row)

def rows_to_list(rows):
    return [dict(r) for r in rows]

def get_date_range(date_str: str):
    """Return start and end datetime strings for a given date."""
    d = date.fromisoformat(date_str)
    start = datetime.combine(d, datetime.min.time()).isoformat()
    end = datetime.combine(d, datetime.max.time()).isoformat()
    return start, end
```

### app.py: CORS middleware setup

```python
cors_origins_raw = os.environ.get("NUTRITRACK_CORS_ORIGINS", "*")
CORS_ORIGINS = ["*"] if cors_origins_raw == "*" else [o.strip() for o in cors_origins_raw.split(",")]

app = FastAPI(title="NutriTrack API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### app.py: /api/daily-summary endpoint — full function

```python
@app.get("/api/daily-summary")
def get_daily_summary(date: Optional[str] = None):
    target_date = date or datetime.now().date().isoformat()
    start, end = get_date_range(target_date)

    conn = get_db()

    # Get profile
    profile_row = conn.execute("SELECT * FROM user_profile ORDER BY id DESC LIMIT 1").fetchone()
    if not profile_row:
        conn.close()
        return {"error": "No profile set. Create your profile first."}
    profile = row_to_dict(profile_row)

    # Get today's food
    food_rows = conn.execute(
        "SELECT * FROM food_entries WHERE logged_at BETWEEN ? AND ? ORDER BY logged_at", (start, end)
    ).fetchall()
    food = rows_to_list(food_rows)

    # Get today's activities
    activity_rows = conn.execute(
        "SELECT * FROM sport_activities WHERE performed_at BETWEEN ? AND ? ORDER BY performed_at", (start, end)
    ).fetchall()
    activities = rows_to_list(activity_rows)

    # Get latest weight
    weight_row = conn.execute(
        "SELECT * FROM weight_logs ORDER BY measured_at DESC LIMIT 1"
    ).fetchone()

    conn.close()

    # Calculate totals
    total_calories = sum(f["calories"] for f in food)
    total_protein = sum(f["protein_g"] for f in food)
    total_carbs = sum(f["carbs_g"] for f in food)
    total_fat = sum(f["fat_g"] for f in food)

    activity_calories = sum(a["calories_burned"] for a in activities)

    # Calculate goals
    goals = calculate_daily_goals(profile, activity_calories)

    return {
        "date": target_date,
        "profile": profile,
        "goals": goals,
        "intake": {
            "calories": round(total_calories, 1),
            "protein_g": round(total_protein, 1),
            "carbs_g": round(total_carbs, 1),
            "fat_g": round(total_fat, 1),
        },
        "remaining": {
            "calories": round(goals["calorie_goal"] - total_calories, 1),
            "protein_g": round(goals["protein_goal_g"] - total_protein, 1),
            "carbs_g": round(goals["carbs_goal_g"] - total_carbs, 1),
            "fat_g": round(goals["fat_goal_g"] - total_fat, 1),
        },
        "food_entries": food,
        "activities": activities,
        "latest_weight": row_to_dict(weight_row) if weight_row else None,
    }
```

### app.py: /api/weekly-report endpoint — full function

```python
@app.get("/api/weekly-report")
def get_weekly_report(date: Optional[str] = None):
    """Generate a weekly report for the agent to analyze."""
    end_date = date or datetime.now().date().isoformat()
    end_d = date_obj = __import__('datetime').date.fromisoformat(end_date)
    start_d = end_d - timedelta(days=6)
    start_date = start_d.isoformat()

    s = datetime.combine(start_d, datetime.min.time()).isoformat()
    e = datetime.combine(end_d, datetime.max.time()).isoformat()

    conn = get_db()

    # Profile
    profile_row = conn.execute("SELECT * FROM user_profile ORDER BY id DESC LIMIT 1").fetchone()
    profile = row_to_dict(profile_row) if profile_row else None

    # Food for the week
    food_rows = conn.execute(
        "SELECT * FROM food_entries WHERE logged_at BETWEEN ? AND ? ORDER BY logged_at", (s, e)
    ).fetchall()
    food = rows_to_list(food_rows)

    # Activities for the week
    activity_rows = conn.execute(
        "SELECT * FROM sport_activities WHERE performed_at BETWEEN ? AND ? ORDER BY performed_at", (s, e)
    ).fetchall()
    activities = rows_to_list(activity_rows)

    # Weight for the week
    weight_rows = conn.execute(
        "SELECT * FROM weight_logs WHERE measured_at BETWEEN ? AND ? ORDER BY measured_at", (s, e)
    ).fetchall()
    weights = rows_to_list(weight_rows)

    # Health measurements for the week
    health_rows = conn.execute(
        "SELECT * FROM health_measurements WHERE measured_at BETWEEN ? AND ? ORDER BY measured_at", (s, e)
    ).fetchall()
    health = rows_to_list(health_rows)

    conn.close()

    # Aggregate food by day
    daily_nutrition = {}
    for f in food:
        day = f["logged_at"][:10]
        if day not in daily_nutrition:
            daily_nutrition[day] = {"calories": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0}

        daily_nutrition[day]["calories"] += f["calories"]
        daily_nutrition[day]["protein_g"] += f["protein_g"]
        daily_nutrition[day]["carbs_g"] += f["carbs_g"]
        daily_nutrition[day]["fat_g"] += f["fat_g"]

    days_logged = len(daily_nutrition) or 1
    avg_calories = round(sum(d["calories"] for d in daily_nutrition.values()) / days_logged, 1)
    avg_protein = round(sum(d["protein_g"] for d in daily_nutrition.values()) / days_logged, 1)
    avg_carbs = round(sum(d["carbs_g"] for d in daily_nutrition.values()) / days_logged, 1)
    avg_fat = round(sum(d["fat_g"] for d in daily_nutrition.values()) / days_logged, 1)

    # Goals (use profile if available)
    goals = None
    if profile:
        activity_cal = sum(a["calories_burned"] for a in activities) / 7
        goals = calculate_daily_goals(profile, activity_cal)

    # Count days over/under goal
    days_over = 0
    days_under = 0
    if goals:
        for day_data in daily_nutrition.values():
            if day_data["calories"] > goals["calorie_goal"]:
                days_over += 1
            else:
                days_under += 1

    # Weight change
    weight_start = weights[0]["weight_kg"] if weights else None
    weight_end = weights[-1]["weight_kg"] if weights else None
    weight_change = round(weight_end - weight_start, 2) if weight_start and weight_end else None

    # Health averages
    bp_systolic = [h["systolic_bp"] for h in health if h["systolic_bp"]]
    bp_diastolic = [h["diastolic_bp"] for h in health if h["diastolic_bp"]]
    sugars = [h["blood_sugar"] for h in health if h["blood_sugar"]]
    oxygen = [h["blood_oxygen"] for h in health if h["blood_oxygen"]]

    return {
        "period": f"{start_date} to {end_date}",
        "days_with_data": days_logged,
        "nutrition": {
            "avg_calories": avg_calories,
            "avg_protein_g": avg_protein,
            "avg_carbs_g": avg_carbs,
            "avg_fat_g": avg_fat,
            "days_over_goal": days_over,
            "days_under_goal": days_under,
            "daily_breakdown": daily_nutrition,
        },
        "weight": {
            "start_weight": weight_start,
            "end_weight": weight_end,
            "change_kg": weight_change,
            "all_entries": weights,
        },
        "activity": {
            "total_sessions": len(activities),
            "total_duration_min": sum(a["duration_minutes"] for a in activities),
            "total_calories_burned": round(sum(a["calories_burned"] for a in activities), 1),
            "activities": activities,
            "types": list(set(a["activity_type"] for a in activities)),
        },
        "health": {
            "avg_systolic": round(sum(bp_systolic) / len(bp_systolic), 1) if bp_systolic else None,
            "avg_diastolic": round(sum(bp_diastolic) / len(bp_diastolic), 1) if bp_diastolic else None,
            "avg_blood_sugar": round(sum(sugars) / len(sugars), 1) if sugars else None,
            "avg_blood_oxygen": round(sum(oxygen) / len(oxygen), 1) if oxygen else None,
            "all_entries": health,
        },
        "goals": goals,
        "profile": profile,
    }
```

### app.py: /api/gamification endpoint — full function

```python
@app.get("/api/gamification")
def get_gamification_status():
    """Calculate current streak, elite status, and daily points."""
    conn = get_db()

    # Get profile
    profile_row = conn.execute("SELECT * FROM user_profile ORDER BY id DESC LIMIT 1").fetchone()
    if not profile_row:
        conn.close()
        return {"error": "No profile set"}
    profile = row_to_dict(profile_row)

    # Calculate streak (backwards from yesterday to find consecutive success)
    streak_count = 0
    elite_streak = False

    # Look back 30 days max for streak
    today = datetime.now().date()

    # Check TODAY first for "Elite" status display
    today_iso = today.isoformat()
    start, end = get_date_range(today_iso)

    today_food = conn.execute(
        "SELECT COALESCE(SUM(calories),0) as cal, COALESCE(SUM(protein_g),0) as prot, "
        "COALESCE(SUM(carbs_g),0) as carb, COALESCE(SUM(fat_g),0) as fat "
        "FROM food_entries WHERE logged_at BETWEEN ? AND ?", (start, end)
    ).fetchone()

    today_activity = conn.execute(
        "SELECT COALESCE(SUM(calories_burned),0) as burned "
        "FROM sport_activities WHERE performed_at BETWEEN ? AND ?", (start, end)
    ).fetchone()

    today_goals = calculate_daily_goals(profile, today_activity["burned"])

    today_stats = {
        "calories": today_food["cal"],
        "protein_g": today_food["prot"],
        "carbs_g": today_food["carb"],
        "fat_g": today_food["fat"]
    }

    today_gamification = calculate_gamification(today_stats, today_goals)

    # Calculate historical streak
    # Iterate backwards from YESTERDAY
    for i in range(1, 31):
        d = today - timedelta(days=i)
        ds = d.isoformat()
        s, e = get_date_range(ds)

        day_food = conn.execute(
            "SELECT COALESCE(SUM(calories),0) as cal "
            "FROM food_entries WHERE logged_at BETWEEN ? AND ?", (s, e)
        ).fetchone()

        # If no food logged, streak breaks
        if day_food["cal"] == 0:
            break

        day_activity = conn.execute(
            "SELECT COALESCE(SUM(calories_burned),0) as burned "
            "FROM sport_activities WHERE performed_at BETWEEN ? AND ?", (s, e)
        ).fetchone()

        day_goals = calculate_daily_goals(profile, day_activity["burned"])

        if day_food["cal"] <= day_goals["calorie_goal"]:
            streak_count += 1
        else:
            break

    conn.close()

    return {
        "streak_days": streak_count,
        "today_points": today_gamification["points"],
        "is_elite": today_gamification["is_elite"],
        "calorie_success": today_gamification["calorie_success"],
        "tags": today_gamification["tags"]
    }
```

### app.py: /api/seed-demo-data endpoint — full function

```python
@app.post("/api/seed-demo-data")
def seed_demo_data():
    """Populate the database with 30 days of realistic demo data."""
    conn = get_db()

    # Clear existing data
    for table in ["food_entries", "weight_logs", "sport_activities", "health_measurements", "user_profile"]:
        conn.execute(f"DELETE FROM {table}")
    conn.commit()

    # Profile
    conn.execute("""
        INSERT INTO user_profile (age, sex, height_cm, current_weight_kg, activity_level, weight_goal_kg, calorie_deficit)
        VALUES (30, 'male', 180, 85.0, 'moderate', 78.0, 500)
    """)

    today_d = datetime.now().date()
    random.seed(42)

    meal_foods = {
        "breakfast": [
            ("Oatmeal with banana", 350, 12, 58, 8, "1 bowl"),
            ("Greek yogurt with honey", 280, 20, 30, 8, "200g"),
            ("Scrambled eggs on toast", 420, 25, 30, 22, "2 eggs + 1 slice"),
            ("Protein smoothie", 310, 30, 35, 6, "1 glass"),
            ("Avocado toast", 380, 10, 32, 24, "2 slices"),
        ],
        "lunch": [
            ("Grilled chicken salad", 450, 40, 15, 25, "1 plate"),
            ("Turkey wrap", 520, 35, 45, 20, "1 wrap"),
            ("Lentil soup with bread", 480, 22, 65, 12, "1 bowl + bread"),
            ("Tuna sandwich", 430, 30, 40, 16, "1 sandwich"),
            ("Chicken rice bowl", 550, 38, 55, 18, "1 bowl"),
        ],
        "dinner": [
            ("Salmon with vegetables", 520, 42, 20, 28, "200g salmon"),
            ("Pasta with meat sauce", 620, 30, 70, 22, "1 plate"),
            ("Stir-fried tofu with rice", 480, 25, 55, 18, "1 plate"),
            ("Grilled steak with salad", 550, 45, 10, 35, "250g steak"),
            ("Chicken curry with rice", 580, 35, 60, 20, "1 serving"),
        ],
        "snack": [
            ("Protein bar", 220, 20, 25, 8, "1 bar"),
            ("Apple with peanut butter", 250, 7, 30, 14, "1 apple + 1 tbsp"),
            ("Mixed nuts", 180, 5, 8, 16, "30g"),
            ("Rice cakes with cottage cheese", 160, 12, 20, 4, "2 cakes"),
        ],
    }

    activity_types = [
        ("Running", 30, 350, "moderate"),
        ("Running", 45, 520, "high"),
        ("Cycling", 40, 400, "moderate"),
        ("Weight training", 50, 300, "high"),
        ("Swimming", 35, 380, "moderate"),
        ("Yoga", 45, 180, "low"),
        ("HIIT", 25, 350, "high"),
        ("Walking", 60, 250, "low"),
    ]

    start_weight = 85.0
    weight = start_weight

    for day_offset in range(30):
        d = today_d - timedelta(days=29 - day_offset)
        ds = d.isoformat()

        # Weight (gradual decline + noise)
        weight = start_weight - (day_offset * 0.065) + random.uniform(-0.3, 0.3)
        weight = round(weight, 1)
        conn.execute(
            "INSERT INTO weight_logs (weight_kg, notes, measured_at) VALUES (?, ?, ?)",
            (weight, "Morning weigh-in", f"{ds}T07:{random.randint(0,30):02d}:00")
        )

        # Food entries
        for meal in ["breakfast", "lunch", "dinner"]:
            food = random.choice(meal_foods[meal])
            name, cal, prot, carb, fat, qty = food
            hour = {"breakfast": 8, "lunch": 12, "dinner": 19}[meal]
            conn.execute(
                "INSERT INTO food_entries (name, calories, protein_g, carbs_g, fat_g, meal_type, quantity, logged_at) VALUES (?,?,?,?,?,?,?,?)",
                (name, cal + random.randint(-30, 30), prot, carb, fat, meal, qty,
                 f"{ds}T{hour:02d}:{random.randint(0,45):02d}:00")
            )

        # Snack on ~70% of days
        if random.random() < 0.7:
            food = random.choice(meal_foods["snack"])
            name, cal, prot, carb, fat, qty = food
            conn.execute(
                "INSERT INTO food_entries (name, calories, protein_g, carbs_g, fat_g, meal_type, quantity, logged_at) VALUES (?,?,?,?,?,?,?,?)",
                (name, cal + random.randint(-10, 10), prot, carb, fat, "snack", qty,
                 f"{ds}T{random.randint(15,17):02d}:{random.randint(0,59):02d}:00")
            )

        # Activity on ~60% of days
        if random.random() < 0.6:
            act = random.choice(activity_types)
            act_type, duration, burned, intensity = act
            conn.execute(
                "INSERT INTO sport_activities (activity_type, duration_minutes, calories_burned, intensity, performed_at) VALUES (?,?,?,?,?)",
                (act_type, duration, burned + random.randint(-20, 20), intensity,
                 f"{ds}T{random.randint(6,18):02d}:{random.randint(0,59):02d}:00")
            )

        # Health every ~3 days
        if day_offset % 3 == 0:
            conn.execute(
                "INSERT INTO health_measurements (systolic_bp, diastolic_bp, blood_sugar, blood_oxygen, heart_rate, measured_at) VALUES (?,?,?,?,?,?)",
                (random.randint(110, 130), random.randint(70, 85),
                 round(random.uniform(85, 105), 1), round(random.uniform(96, 99), 1),
                 random.randint(62, 82),
                 f"{ds}T{random.randint(7,20):02d}:{random.randint(0,59):02d}:00")
            )

    # Update profile with latest weight
    conn.execute("UPDATE user_profile SET current_weight_kg=?", (weight,))
    conn.commit()
    conn.close()

    return {"message": "Demo data seeded: 30 days of food, weight, activity, and health data."}
```

### app.py: uvicorn startup block

```python
if __name__ == "__main__":
    uvicorn.run("app:app", host=HOST, port=PORT)
```

### app.py: /api/history/daily-totals endpoint — full function

```python
@app.get("/api/history/daily-totals")
def get_daily_totals(days: int = 30):
    """Get daily calorie/macro totals for the last N days (for charts)."""
    end_d = datetime.now().date()
    start_d = end_d - timedelta(days=days - 1)

    start_iso = datetime.combine(start_d, datetime.min.time()).isoformat()
    end_iso = datetime.combine(end_d, datetime.max.time()).isoformat()

    conn = get_db()

    # Get profile for goals
    profile_row = conn.execute("SELECT * FROM user_profile ORDER BY id DESC LIMIT 1").fetchone()
    profile = row_to_dict(profile_row) if profile_row else None

    # Single query for food totals grouped by date
    food_rows = conn.execute("""
        SELECT DATE(logged_at) as day,
               COALESCE(SUM(calories), 0) as cal,
               COALESCE(SUM(protein_g), 0) as prot,
               COALESCE(SUM(carbs_g), 0) as carb,
               COALESCE(SUM(fat_g), 0) as fat
        FROM food_entries
        WHERE logged_at BETWEEN ? AND ?
        GROUP BY DATE(logged_at)
    """, (start_iso, end_iso)).fetchall()

    # Single query for activity totals grouped by date
    activity_rows = conn.execute("""
        SELECT DATE(performed_at) as day,
               COALESCE(SUM(calories_burned), 0) as burned
        FROM sport_activities
        WHERE performed_at BETWEEN ? AND ?
        GROUP BY DATE(performed_at)
    """, (start_iso, end_iso)).fetchall()

    conn.close()

    # Index results by date for O(1) lookup
    food_by_day = {r["day"]: r for r in food_rows}
    activity_by_day = {r["day"]: r for r in activity_rows}

    # Build result array, filling gaps with zeros
    results = []
    for i in range(days):
        d = start_d + timedelta(days=i)
        ds = d.isoformat()

        food = food_by_day.get(ds)
        cal = round(food["cal"], 1) if food else 0
        prot = round(food["prot"], 1) if food else 0
        carb = round(food["carb"], 1) if food else 0
        fat = round(food["fat"], 1) if food else 0

        act = activity_by_day.get(ds)
        burned = round(act["burned"], 1) if act else 0

        goals = calculate_daily_goals(profile, burned) if profile else None

        results.append({
            "date": ds,
            "calories": cal,
            "protein_g": prot,
            "carbs_g": carb,
            "fat_g": fat,
            "activity_calories": burned,
            "calorie_goal": goals["calorie_goal"] if goals else None,
            "protein_goal_g": goals["protein_goal_g"] if goals else None,
            "carbs_goal_g": goals["carbs_goal_g"] if goals else None,
            "fat_goal_g": goals["fat_goal_g"] if goals else None,
        })

    return {"daily_totals": results}
```

### dashboard.html: loadOverview() function

```javascript
async function loadOverview() {
    try {
        loadGamification(); // Refresh gamification status
        const res = await fetch(`${API}/api/daily-summary?date=${currentDate}`);
        const data = await res.json();

        if (data.error) {
            console.warn(data.error);
            return;
        }

        const { goals, intake, remaining, food_entries, activities, latest_weight, profile } = data;

        // Calorie ring
        const pct = goals.calorie_goal > 0 ? Math.min(intake.calories / goals.calorie_goal, 1.5) : 0;
        const circumference = 314.16;
        const offset = circumference * (1 - Math.min(pct, 1));
        const ring = document.getElementById('calorieRing');
        ring.style.strokeDashoffset = offset;
        ring.style.stroke = pct > 1 ? 'var(--danger)' : 'var(--accent)';

        document.getElementById('caloriesEaten').textContent = Math.round(intake.calories);
        document.getElementById('calorieGoal').textContent = Math.round(goals.calorie_goal);
        document.getElementById('caloriesRemaining').textContent = Math.round(Math.max(remaining.calories, 0));

        // Macros
        updateMacroBar('protein', intake.protein_g, goals.protein_goal_g);
        updateMacroBar('carbs', intake.carbs_g, goals.carbs_goal_g);
        updateMacroBar('fat', intake.fat_g, goals.fat_goal_g);

        // Quick stats
        document.getElementById('currentWeight').textContent = latest_weight ? latest_weight.weight_kg : '—';
        document.getElementById('goalWeight').textContent = profile?.weight_goal_kg || '—';
        document.getElementById('deficitTarget').textContent = profile?.calorie_deficit || 500;

        const burned = activities.reduce((sum, a) => sum + a.calories_burned, 0);
        document.getElementById('activityBurned').textContent = Math.round(burned);

        // Food log
        renderFoodLog(food_entries);

        // Activities
        renderActivities(activities);

    } catch (err) {
        console.error('Failed to load overview:', err);
    }
}
```

### dashboard.html: loadGamification() function

```javascript
async function loadGamification() {
    try {
        const res = await fetch(`${API}/api/gamification`);
        const data = await res.json();

        // Update Streak
        const streakEl = document.getElementById('streak-days');
        const streakIcon = document.getElementById('streak-icon');
        streakEl.textContent = data.streak_days;

        if (data.is_elite) {
            streakIcon.textContent = '💠'; // Blue Plasma for Elite
        } else {
            streakIcon.textContent = '🔥';
        }

        // Update Points
        document.getElementById('daily-points').textContent = data.today_points;

        // Update Badges
        const badgeContainer = document.getElementById('status-badges');
        badgeContainer.innerHTML = '';

        if (data.tags.length === 0) {
             badgeContainer.innerHTML = '<span class="badge" style="background: var(--surface2); padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; color: var(--text-dim);">No activity yet</span>';
        } else {
            const badgeMap = {
                'protein_met': { text: 'Protein Goal', color: '#60a5fa', bg: 'rgba(96,165,250,0.15)' },
                'carbs_good': { text: 'Carbs OK', color: '#fbbf24', bg: 'rgba(251,191,36,0.15)' },
                'fat_good': { text: 'Fat OK', color: '#f87171', bg: 'rgba(248,113,113,0.15)' },
                'perfect_bonus': { text: 'PERFECT DAY', color: '#3ecf8e', bg: 'rgba(62,207,142,0.15)' }
            };

            data.tags.forEach(tag => {
                const style = badgeMap[tag];
                if (style) {
                    const badge = document.createElement('span');
                    badge.className = 'badge';
                    badge.textContent = style.text;
                    badge.style.cssText = `background: ${style.bg}; color: ${style.color}; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;`;
                    badgeContainer.appendChild(badge);
                }
            });
        }

    } catch (err) {
        console.error('Gamification load error:', err);
    }
}
```

### dashboard.html: All chart rendering functions

```javascript
function renderCalorieChart(data) {
    destroyChart('calorie');
    const ctx = document.getElementById('calorieChart').getContext('2d');

    charts.calorie = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(d => d.date.slice(5)),
            datasets: [
                {
                    label: 'Intake',
                    data: data.map(d => d.calories),
                    backgroundColor: 'rgba(62,207,142,0.6)',
                    borderRadius: 4,
                },
                {
                    label: 'Goal',
                    data: data.map(d => d.calorie_goal),
                    type: 'line',
                    borderColor: '#f87171',
                    borderDash: [5, 5],
                    pointRadius: 0,
                    borderWidth: 2,
                    fill: false,
                },
            ],
        },
        options: { ...chartDefaults },
    });
}

function renderMacroChart(data) {
    destroyChart('macro');
    const ctx = document.getElementById('macroChart').getContext('2d');

    charts.macro = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(d => d.date.slice(5)),
            datasets: [
                {
                    label: 'Protein (g)',
                    data: data.map(d => d.protein_g),
                    borderColor: '#60a5fa',
                    backgroundColor: 'rgba(96,165,250,0.1)',
                    fill: true,
                    tension: 0.3,
                    pointRadius: 2
                },
                {
                    label: 'Carbs (g)',
                    data: data.map(d => d.carbs_g),
                    borderColor: '#fbbf24',
                    backgroundColor: 'rgba(251,191,36,0.1)',
                    fill: true,
                    tension: 0.3,
                    pointRadius: 2
                },
                {
                    label: 'Fat (g)',
                    data: data.map(d => d.fat_g),
                    borderColor: '#f87171',
                    backgroundColor: 'rgba(248,113,113,0.1)',
                    fill: true,
                    tension: 0.3,
                    pointRadius: 2
                },
            ],
        },
        options: { ...chartDefaults },
    });
}

function renderWeightChart(entries) {
    destroyChart('weight');
    const sorted = [...entries].sort((a, b) => a.measured_at.localeCompare(b.measured_at));
    const ctx = document.getElementById('weightChart').getContext('2d');

    charts.weight = new Chart(ctx, {
        type: 'line',
        data: {
            labels: sorted.map(e => e.measured_at.slice(0, 10)),
            datasets: [{
                label: 'Weight (kg)',
                data: sorted.map(e => e.weight_kg),
                borderColor: '#a78bfa',
                backgroundColor: 'rgba(167,139,250,0.1)',
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointBackgroundColor: '#a78bfa',
            }],
        },
        options: { ...chartDefaults },
    });
}

function renderActivityChart(entries) {
    destroyChart('activity');
    // Group by date
    const byDate = {};
    entries.forEach(e => {
        const day = e.performed_at.slice(0, 10);
        if (!byDate[day]) byDate[day] = { duration: 0, burned: 0, count: 0 };
        byDate[day].duration += e.duration_minutes;
        byDate[day].burned += e.calories_burned;
        byDate[day].count++;
    });

    const dates = Object.keys(byDate).sort();
    const ctx = document.getElementById('activityChart').getContext('2d');

    charts.activity = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: dates.map(d => d.slice(5)),
            datasets: [
                {
                    label: 'Duration (min)',
                    data: dates.map(d => byDate[d].duration),
                    backgroundColor: 'rgba(251,191,36,0.6)',
                    borderRadius: 4,
                    yAxisID: 'y',
                },
                {
                    label: 'Calories Burned',
                    data: dates.map(d => byDate[d].burned),
                    type: 'line',
                    borderColor: '#f87171',
                    pointRadius: 3,
                    borderWidth: 2,
                    yAxisID: 'y1',
                },
            ],
        },
        options: {
            ...chartDefaults,
            scales: {
                ...chartDefaults.scales,
                y1: {
                    position: 'right',
                    ticks: { color: '#f87171', font: { family: 'Space Mono', size: 10 } },
                    grid: { display: false },
                },
            },
        },
    });
}
```

### seed.py — entire file

```python
#!/usr/bin/env python3
"""
NutriTrack Demo Data Seeder
Populates the database with 30 days of realistic sample data.
Usage: python3 seed.py [--force]
"""
import sys
import os
import random
from datetime import datetime, timedelta

# Ensure we can import database module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from database import get_db, init_db

MEAL_FOODS = {
    "breakfast": [
        ("Oatmeal with banana", 350, 12, 58, 8, "1 bowl"),
        ("Greek yogurt with honey", 280, 20, 30, 8, "200g"),
        ("Scrambled eggs on toast", 420, 25, 30, 22, "2 eggs + 1 slice"),
        ("Protein smoothie", 310, 30, 35, 6, "1 glass"),
        ("Avocado toast", 380, 10, 32, 24, "2 slices"),
        ("Pancakes with maple syrup", 400, 8, 55, 16, "3 pancakes"),
        ("Fruit and granola bowl", 320, 8, 48, 12, "1 bowl"),
    ],
    "lunch": [
        ("Grilled chicken salad", 450, 40, 15, 25, "1 plate"),
        ("Turkey wrap", 520, 35, 45, 20, "1 wrap"),
        ("Lentil soup with bread", 480, 22, 65, 12, "1 bowl + bread"),
        ("Tuna sandwich", 430, 30, 40, 16, "1 sandwich"),
        ("Chicken rice bowl", 550, 38, 55, 18, "1 bowl"),
        ("Caesar salad with croutons", 380, 28, 20, 22, "1 plate"),
        ("Vegetable stir-fry with tofu", 420, 22, 45, 18, "1 plate"),
    ],
    "dinner": [
        ("Salmon with vegetables", 520, 42, 20, 28, "200g salmon"),
        ("Pasta with meat sauce", 620, 30, 70, 22, "1 plate"),
        ("Stir-fried tofu with rice", 480, 25, 55, 18, "1 plate"),
        ("Grilled steak with salad", 550, 45, 10, 35, "250g steak"),
        ("Chicken curry with rice", 580, 35, 60, 20, "1 serving"),
        ("Baked cod with potatoes", 440, 38, 35, 14, "1 fillet + potatoes"),
        ("Vegetable lasagna", 510, 22, 52, 24, "1 serving"),
    ],
    "snack": [
        ("Protein bar", 220, 20, 25, 8, "1 bar"),
        ("Apple with peanut butter", 250, 7, 30, 14, "1 apple + 1 tbsp"),
        ("Mixed nuts", 180, 5, 8, 16, "30g"),
        ("Rice cakes with cottage cheese", 160, 12, 20, 4, "2 cakes"),
        ("Dark chocolate square", 150, 2, 15, 10, "30g"),
        ("Banana", 105, 1, 27, 0, "1 medium"),
    ],
}

ACTIVITY_TYPES = [
    ("Running", 30, 350, "moderate"),
    ("Running", 45, 520, "high"),
    ("Cycling", 40, 400, "moderate"),
    ("Weight training", 50, 300, "high"),
    ("Swimming", 35, 380, "moderate"),
    ("Yoga", 45, 180, "low"),
    ("HIIT", 25, 350, "high"),
    ("Walking", 60, 250, "low"),
    ("Cycling", 60, 550, "high"),
    ("Weight training", 40, 250, "moderate"),
]


def seed(force=False):
    """Seed the database with demo data. Returns summary dict."""
    init_db()
    conn = get_db()

    # Check if data already exists
    existing = conn.execute("SELECT COUNT(*) FROM food_entries").fetchone()[0]
    if existing > 0 and not force:
        conn.close()
        return None  # Signal that data already exists

    # Clear existing data if force
    if force:
        for table in ["food_entries", "weight_logs", "sport_activities", "health_measurements", "user_profile"]:
            conn.execute(f"DELETE FROM {table}")
        conn.commit()

    # Profile
    conn.execute("""
        INSERT INTO user_profile (age, sex, height_cm, current_weight_kg, activity_level, weight_goal_kg, calorie_deficit)
        VALUES (32, 'male', 178, 85.0, 'moderate', 78.0, 500)
    """)

    today = datetime.now().date()
    random.seed(42)

    counts = {"food": 0, "weight": 0, "activity": 0, "health": 0}
    start_weight = 85.0
    weight = start_weight

    for day_offset in range(30):
        d = today - timedelta(days=29 - day_offset)
        ds = d.isoformat()

        # Weight (gradual decline + noise)
        weight = start_weight - (day_offset * 0.055) + random.uniform(-0.3, 0.3)
        weight = round(weight, 1)
        conn.execute(
            "INSERT INTO weight_logs (weight_kg, notes, measured_at) VALUES (?, ?, ?)",
            (weight, "Morning weigh-in", f"{ds}T07:{random.randint(0, 30):02d}:00")
        )
        counts["weight"] += 1

        # Food: breakfast + lunch + dinner
        for meal in ["breakfast", "lunch", "dinner"]:
            food = random.choice(MEAL_FOODS[meal])
            name, cal, prot, carb, fat, qty = food
            hour = {"breakfast": 8, "lunch": 12, "dinner": 19}[meal]
            conn.execute(
                "INSERT INTO food_entries (name, calories, protein_g, carbs_g, fat_g, meal_type, quantity, logged_at) VALUES (?,?,?,?,?,?,?,?)",
                (name, cal + random.randint(-30, 30), prot, carb, fat, meal, qty,
                 f"{ds}T{hour:02d}:{random.randint(0, 45):02d}:00")
            )
            counts["food"] += 1

        # Snack on ~70% of days
        if random.random() < 0.7:
            food = random.choice(MEAL_FOODS["snack"])
            name, cal, prot, carb, fat, qty = food
            conn.execute(
                "INSERT INTO food_entries (name, calories, protein_g, carbs_g, fat_g, meal_type, quantity, logged_at) VALUES (?,?,?,?,?,?,?,?)",
                (name, cal + random.randint(-10, 10), prot, carb, fat, "snack", qty,
                 f"{ds}T{random.randint(15, 17):02d}:{random.randint(0, 59):02d}:00")
            )
            counts["food"] += 1

        # Activity on ~60% of days
        if random.random() < 0.6:
            act = random.choice(ACTIVITY_TYPES)
            act_type, duration, burned, intensity = act
            conn.execute(
                "INSERT INTO sport_activities (activity_type, duration_minutes, calories_burned, intensity, performed_at) VALUES (?,?,?,?,?)",
                (act_type, duration, burned + random.randint(-20, 20), intensity,
                 f"{ds}T{random.randint(6, 18):02d}:{random.randint(0, 59):02d}:00")
            )
            counts["activity"] += 1

        # Health every ~3 days
        if day_offset % 3 == 0:
            conn.execute(
                "INSERT INTO health_measurements (systolic_bp, diastolic_bp, blood_sugar, blood_oxygen, heart_rate, measured_at) VALUES (?,?,?,?,?,?)",
                (random.randint(110, 130), random.randint(70, 85),
                 round(random.uniform(85, 105), 1), round(random.uniform(96, 99), 1),
                 random.randint(62, 82),
                 f"{ds}T{random.randint(7, 20):02d}:{random.randint(0, 59):02d}:00")
            )
            counts["health"] += 1

    # Update profile with latest weight
    conn.execute("UPDATE user_profile SET current_weight_kg=?", (weight,))
    conn.commit()
    conn.close()

    return counts


def main():
    force = "--force" in sys.argv

    print("NutriTrack Demo Data Seeder")
    print("=" * 40)

    result = seed(force=force)

    if result is None:
        print("Database already has data.")
        print("Use --force to clear and re-seed.")
        print("  python3 seed.py --force")
        sys.exit(0)

    print(f"  Food entries:         {result['food']}")
    print(f"  Weight logs:          {result['weight']}")
    print(f"  Activity sessions:    {result['activity']}")
    print(f"  Health measurements:  {result['health']}")
    print("=" * 40)
    print("Demo data seeded successfully!")


if __name__ == "__main__":
    main()
```

---

## 12. AGENT INTEGRATION

The full agent integration guide is in `docs/AGENT_README.md` (1,286 lines). Key sections:

### How Agents Discover and Use the API

1. **Base URL**: `http://localhost:8000` (or user-configured host/port)
2. **Content-Type**: Always `application/json`
3. **Authentication**: None required
4. **Auto-generated Swagger docs**: `http://localhost:8000/docs`
5. **Workflow**: Check profile → log food/activity/weight/health → read summaries

### Agent System Prompt Template (from README)

> You are a nutrition tracking assistant. When the user tells you what they ate, log it by calling POST /api/food with the meal name, estimated calories, protein, carbs, fat, and meal type. When they ask for a summary, call GET /api/daily-summary. Use the NutriTrack API at http://localhost:8000.

### Key Agent Behaviors

- **Food estimation**: Agent estimates calories/macros from natural language descriptions using nutritional knowledge
- **Exercise calculation**: Use MET formula: `calories_burned = MET × weight_kg × duration_hours`
- **Meal type assignment**: breakfast (<11:00), lunch (11:00-15:00), dinner (>17:00), snack (everything else)
- **Weight sync**: POST /api/weight also updates profile weight, which changes calorie calculations
- **Search reuse**: GET /api/food/search?q=chicken to find previously logged foods for quick re-logging

### Example Payloads

**Log food:**
```json
POST /api/food
{"name": "Grilled chicken breast", "calories": 165, "protein_g": 31, "carbs_g": 0, "fat_g": 3.6, "meal_type": "lunch", "quantity": "100g"}
```

**Log weight:**
```json
POST /api/weight
{"weight_kg": 84.2, "notes": "Morning weigh-in"}
```

**Log activity:**
```json
POST /api/activity
{"activity_type": "Running", "duration_minutes": 30, "calories_burned": 350, "intensity": "moderate"}
```

**Log health:**
```json
POST /api/health
{"systolic_bp": 118, "diastolic_bp": 76, "blood_sugar": 92, "blood_oxygen": 98, "heart_rate": 68}
```

**Get daily summary:**
```
GET /api/daily-summary?date=2026-02-17
```

**Get weekly report:**
```
GET /api/weekly-report?date=2026-02-17
```

---

## 13. CURRENT STATE & KNOWN ISSUES

### What Works Perfectly

- All CRUD endpoints for food, weight, activity, and health
- Profile creation/update with upsert logic
- Daily summary with dynamic goal calculation (exercise calories adjust goals)
- Weekly report with nutrition, weight, activity, and health aggregation
- Daily totals history endpoint for charting
- Gamification (streak calculation, XP points, elite status, badges)
- Dashboard with all 4 tabs (Overview, Charts, Health, Profile)
- All 6 Chart.js charts render correctly
- Date navigation (prev/next day, date picker, Today button)
- 30-second auto-polling on overview tab
- Visibility change detection (pause polling when tab hidden)
- Modal forms for manual food/weight/activity/health entry
- Food duplicate and delete from the food log table
- CSV export for all data types with optional date range
- Demo data seeding (both API endpoint and standalone script)
- Docker deployment with named volume for data persistence
- Dev mode with auto-reload (both Docker and bare metal)
- Mobile responsive layout

### What Has Bugs or Is Incomplete

- **No `GET /api/food/{id}` endpoint**: The `duplicateFood()` function in the dashboard works around this by fetching all entries for the day and filtering client-side. A dedicated single-entry endpoint would be cleaner.
- **`activity_level` validation not enforced in Pydantic**: The `ProfileCreate` model has `activity_level: str = Field(default="moderate")` but no regex/enum constraint. Validation only happens at the database level via CHECK constraint. Invalid values would cause a 500 error, not a 422.
- **Weekly report uses `__import__('datetime')`**: Line 463 of app.py has `end_d = date_obj = __import__('datetime').date.fromisoformat(end_date)` — the `__import__` call is unnecessary since `date` is already imported. The `date_obj` variable is unused. This works but is messy.
- **No persistent XP/level system**: XP points are calculated per-day only, not accumulated. There's no lifetime XP tracking or level progression.
- **Streak only checks calories, not all macros**: The streak calculation only checks if calories were under the goal. It doesn't consider protein/carbs/fat targets.
- **No user authentication**: Completely open. Anyone on the network can access the API and dashboard.
- **No rate limiting**: The API has no request rate limiting.
- **`NUTRITRACK_DEV_MODE` env var is set but never read**: docker-compose.dev.yml sets it, but no code uses it.

### Recently Changed or Added

Based on git history (4 commits total):
1. Initial commit (2026-02-16)
2. Full platform features, deployment infra, and documentation (2026-02-16)
3. Move project files to repo root for cleaner structure (2026-02-17)
4. Fix placeholder GitHub URLs in README (2026-02-17)

### TODO/FIXME/HACK/XXX Comments

**None found in any file.** The codebase has zero TODO/FIXME/HACK/XXX comments.

### Hardcoded Values That Could Be Configurable

- **Macro split ratio** (30/30/40) is hardcoded in `calculate_daily_goals()` — not user-configurable
- **Streak lookback** is hardcoded to 30 days in the gamification endpoint
- **Polling interval** is hardcoded to 30000ms in the dashboard JavaScript
- **Demo profile** in `seed_demo_data()` is hardcoded (age 30, male, 180cm, 85kg, moderate, goal 78kg, deficit 500)
- **Standalone seeder** `seed.py` creates a slightly different profile (age 32, 178cm) than the API seeder (age 30, 180cm)
- **Food search limit** is hardcoded to 20 results
- **Health/weight default limit** is hardcoded to 90 entries

### Performance Concerns

- **Gamification endpoint makes N+1 queries**: The streak calculation loops through up to 30 days, making 2 queries per day (food + activity). This is up to 60 queries per gamification request. Could be optimized with a single date-range query.
- **Database connections are not pooled**: Each request calls `get_db()` which creates a new SQLite connection. For a single-user app this is fine but would not scale.
- **Daily totals endpoint is efficient**: Uses grouped queries with `DATE()` and dict indexing — no N+1 problem.

---

## 14. GIT STATUS

### Current Branch

`main`

### Remote URL

`https://github.com/BenZenTuna/Nutritrack.git`

### Last 4 Commits (all commits in the repo)

| Hash | Date | Message |
|---|---|---|
| `855a7f8` | 2026-02-17 20:43:37 +0100 | docs: fix placeholder GitHub URLs in README quick start sections |
| `600ccfe` | 2026-02-17 20:40:20 +0100 | Move project files to repo root for cleaner structure |
| `5256aca` | 2026-02-16 22:21:46 +0100 | feat: add full platform features, deployment infra, and documentation |
| `642ccc1` | 2026-02-16 21:24:23 +0100 | Initial commit |

### Uncommitted Changes

None. Working tree is clean. Branch is up to date with `origin/main`.

---

## 15. DEPENDENCIES & VERSIONS

### Python Version

- Host system: Python 3.14.2
- Docker image: Python 3.11-slim

### Python Packages (from requirements.txt)

```
fastapi     (no pinned version)
uvicorn     (no pinned version)
aiofiles    (no pinned version)
pydantic    (no pinned version)
```

Note: Versions are NOT pinned in requirements.txt. The Docker build will install whatever is latest at build time.

### Standard Library Modules Used

- `sqlite3` — database
- `os` — environment variables, file paths
- `datetime` — date/time handling
- `random` — demo data generation
- `csv` — CSV export
- `io` — in-memory string buffer for CSV
- `sys` — command-line args (seed.py)
- `re` — regex (migrate.py only)

### System Packages Required

- Python 3.10+ with `venv` module
- No other system packages required
- Docker & Docker Compose (optional, for containerized deployment)

---

## END OF SNAPSHOT

This document contains the complete knowledge of the NutriTrack codebase as of 2026-02-17. A fresh Claude session reading this file should be able to understand every file, endpoint, database table, calculation, and UI element without accessing any other source.
