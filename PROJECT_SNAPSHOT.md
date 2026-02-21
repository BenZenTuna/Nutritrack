# NutriTrack — Complete Project Snapshot

> **Generated**: 2026-02-21
> **Purpose**: Full knowledge transfer document for onboarding a fresh Claude session with zero context.
> **Branch**: `main` at commit `243bb51`

---

## 1. PROJECT OVERVIEW

### What NutriTrack Is

NutriTrack is a **self-hosted, AI-agent-first nutrition and health tracking platform**. It is a FastAPI + SQLite backend with a single-page vanilla JavaScript dashboard. The user never interacts with the API directly — instead, they talk to an AI agent (any LLM — OpenClaw, Claude, ChatGPT, etc.) in natural language, and the agent translates those conversations into HTTP API calls.

### The Problem It Solves

Manual calorie/macro tracking is tedious. NutriTrack eliminates friction by letting users describe meals conversationally ("I had oatmeal with banana for breakfast") while the AI agent estimates nutritional values and logs them via the REST API. The dashboard visualizes everything automatically.

### User Workflow

```
User talks naturally → AI Agent estimates macros → Agent calls REST API → SQLite stores data → Dashboard auto-refreshes every 30 seconds
```

1. User says "I had pizza for dinner" to their AI agent
2. Agent estimates calories (~800 kcal), protein (~35g), carbs (~90g), fat (~35g)
3. Agent calls `POST /api/food` with the structured data
4. Data stored in SQLite
5. Dashboard at `http://localhost:8000` shows updated charts, progress rings, gamification stats

### Key Differentiators

- **AI-Agent-First Design**: Built to be operated by LLMs via HTTP, not by humans clicking buttons. The dashboard is read-only visualization; all data entry comes from API calls.
- **Gamification**: Streaks, XP points, elite status, and macro achievement badges keep users motivated.
- **Self-Hosted / Local-First**: Runs on the user's machine, no cloud accounts, no external services, no data leaves the machine.
- **Zero Configuration**: SQLite database, no database server needed. One command to deploy.
- **LLM-Agnostic**: Any agent that can make HTTP calls works. The SKILL.md file gives any agent everything it needs.

---

## 2. COMPLETE FILE TREE

```
TT-Nutritrack/
├── .env.example                    634 bytes     22 lines  — Example environment variable configuration
├── .gitignore                      180 bytes     17 lines  — Git ignore rules (db, pycache, venv, data/, etc.)
├── Dockerfile                      494 bytes     21 lines  — Docker image definition (Python 3.11-slim)
├── LICENSE                        1101 bytes     21 lines  — MIT License
├── PROJECT_SNAPSHOT.md                                     — THIS FILE (project knowledge transfer)
├── README.md                     10738 bytes    297 lines  — Project README with install guide and API reference
├── SKILL.md                       9262 bytes    269 lines  — OpenClaw agent skill file (full API + nutrition reference)
├── app.py                        37940 bytes    917 lines  — FastAPI server: all endpoints, Pydantic models, CORS
├── database.py                    6648 bytes    190 lines  — SQLite schema, init, calorie/macro calculation engine
├── deploy.sh                     13339 bytes    366 lines  — One-command deploy (auto-detects Docker or Python)
├── dev.sh                         1104 bytes     27 lines  — Development mode with auto-reload
├── docker-compose.dev.yml          741 bytes     19 lines  — Docker dev overrides (live mount + reload)
├── docker-compose.yml              702 bytes     27 lines  — Production Docker Compose
├── docs/
│   ├── AGENT_DEPLOY.md            3574 bytes    116 lines  — Agent deployment guide (commands, env vars, troubleshooting)
│   ├── AGENT_README.md           39675 bytes   1286 lines  — Complete AI agent integration guide (full API reference)
│   └── screenshots/
│       ├── charts.png                                      — Screenshot of Charts tab
│       ├── health.png                                      — Screenshot of Health tab
│       └── overview.png                                    — Screenshot of Overview tab
├── fix_timestamps.py               744 bytes     29 lines  — One-time migration utility: fix timestamp format
├── install.sh                     3894 bytes     97 lines  — Interactive installer (venv + deps + optional seed)
├── migrate.py                     4424 bytes    113 lines  — One-time migration from old nutrition tracker DB
├── requirements.txt                 34 bytes      4 lines  — Python dependencies
├── scripts/
│   └── install.sh                  168 bytes      4 lines  — Wrapper for OpenClaw skill install
├── seed.py                        7396 bytes    187 lines  — Standalone demo data seeder (30 days of data)
├── setup.sh                        936 bytes     31 lines  — Simple setup & run script (no venv)
├── start.sh                        208 bytes      5 lines  — Start server (requires prior install)
├── static/
│   └── dashboard.html            85078 bytes   1664 lines  — Single-page dashboard (HTML + CSS + JS, all inline)
├── stop.sh                         117 bytes      2 lines  — Stop server (pkill)
└── test_profile_update.py          590 bytes     23 lines  — Simple test script for profile PUT endpoint
```

---

## 3. TECH STACK

### Backend
- **Python 3.10+** (developed with 3.11, tested on 3.14)
- **FastAPI** — Async web framework, serves REST API + auto-generated Swagger at `/docs`
- **uvicorn** — ASGI server
- **Pydantic** — Request/response validation models
- **aiofiles** — Async file serving (for static files)
- **SQLite 3** — Embedded database with WAL mode and foreign key enforcement

### Frontend (all inline in `static/dashboard.html`)
- **Vanilla JavaScript** — Zero framework dependencies, no build step
- **Chart.js 4.4.1** (CDN: `https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js`)
- **chartjs-adapter-date-fns 3.0.0** (CDN: `https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns@3.0.0/dist/chartjs-adapter-date-fns.bundle.min.js`)
- **Google Fonts** — DM Sans (body) + Space Mono (monospace numbers)

### Python Packages (from requirements.txt — NO pinned versions)
```
fastapi
uvicorn
aiofiles
pydantic
```

### Containerization
- **Docker** with `python:3.11-slim` base image
- **Docker Compose** v3.8 with named volume for data persistence

### System Dependencies
- Python 3.10+ with `venv` module
- `pip` for package management
- `curl` for health checks (deploy.sh)
- Docker + Docker Compose (optional, auto-detected)

---

## 4. DATABASE SCHEMA — FULL DUMP

### Database Location

```python
DB_PATH = os.environ.get(
    "NUTRITRACK_DB_PATH",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "nutritrack.db")
)
```

Default: `nutritrack.db` in the project root (bare metal) or `/app/data/nutritrack.db` (Docker).

### Connection Settings

```python
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn
```

- WAL mode for concurrent reads
- Foreign keys enforced
- Row factory returns dict-like Row objects

### CREATE TABLE Statements (verbatim from database.py)

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

### Table Relationships & Side Effects

- **No foreign keys** between tables. All tables are independent.
- **`user_profile`**: Single-row table. Only one profile exists at a time. Read with `ORDER BY id DESC LIMIT 1`.
- **Side effect**: `POST /api/weight` also runs `UPDATE user_profile SET current_weight_kg=?` — logging weight auto-updates the profile, which recalculates all calorie goals.
- **Side effect**: `PUT /api/profile` (first creation) also inserts a weight log entry with "Profile update" note.
- **`food_entries.logged_at`** vs **`food_entries.created_at`**: `logged_at` is when the food was eaten (user-provided or defaulted to now); `created_at` is when the record was inserted.

---

## 5. COMPLETE API REFERENCE

### Pydantic Models (verbatim from app.py)

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
|--------|------|-------------|
| GET | `/` | Serves dashboard.html with no-cache headers |

#### Profile
| Method | Path | Params | Response |
|--------|------|--------|----------|
| GET | `/api/profile` | — | `{"profile": {...} or null, "message": "..."}` |
| PUT | `/api/profile` | Body: ProfileCreate | `{"profile": {...}, "message": "Profile updated successfully."}` |

**PUT side effects**: On first creation, also inserts a weight_logs entry. On update, sets `updated_at=CURRENT_TIMESTAMP`.

#### Food
| Method | Path | Params | Response |
|--------|------|--------|----------|
| POST | `/api/food` | Body: FoodEntry | `{"entry": {...}, "message": "Logged: name (cal kcal)"}` |
| GET | `/api/food` | `?date=YYYY-MM-DD` (optional, defaults to today) | `{"entries": [...], "count": N}` |
| GET | `/api/food/search` | `?q=string` (required, min_length=1) | `{"results": [...], "count": N}` (max 20 distinct results) |
| GET | `/api/food/range` | `?start=YYYY-MM-DD&end=YYYY-MM-DD` | `{"entries": [...], "count": N}` |
| PUT | `/api/food/{entry_id}` | Body: FoodEntry | `{"entry": {...}, "message": "..."}` (404 if not found) |
| DELETE | `/api/food/{entry_id}` | — | `{"message": "Food entry {id} deleted."}` |

#### Weight
| Method | Path | Params | Response |
|--------|------|--------|----------|
| POST | `/api/weight` | Body: WeightEntry | `{"entry": {...}, "message": "Weight logged: X kg"}` |
| GET | `/api/weight` | `?limit=N` (default 90) | `{"entries": [...], "count": N}` (desc by measured_at) |

**POST side effect**: Also runs `UPDATE user_profile SET current_weight_kg=?` — this recalculates all calorie goals.

#### Activity
| Method | Path | Params | Response |
|--------|------|--------|----------|
| POST | `/api/activity` | Body: ActivityEntry | `{"entry": {...}, "message": "Activity logged: type (cal kcal burned)"}` |
| GET | `/api/activity` | `?date=YYYY-MM-DD` (optional, defaults to today) | `{"entries": [...], "count": N}` |
| GET | `/api/activity/range` | `?start=YYYY-MM-DD&end=YYYY-MM-DD` | `{"entries": [...], "count": N}` |
| PUT | `/api/activity/{entry_id}` | Body: ActivityEntry | `{"entry": {...}, "message": "..."}` (404 if not found) |
| DELETE | `/api/activity/{entry_id}` | — | `{"message": "Activity entry {id} deleted."}` |

#### Health
| Method | Path | Params | Response |
|--------|------|--------|----------|
| POST | `/api/health` | Body: HealthEntry | `{"entry": {...}, "message": "Health measurement logged."}` |
| GET | `/api/health` | `?limit=N` (default 90) | `{"entries": [...], "count": N}` (desc by measured_at) |
| PUT | `/api/health/{entry_id}` | Body: HealthEntry | `{"entry": {...}, "message": "..."}` (404 if not found) |
| DELETE | `/api/health/{entry_id}` | — | `{"message": "Health entry {id} deleted."}` |

#### Reports
| Method | Path | Params | Response |
|--------|------|--------|----------|
| GET | `/api/daily-summary` | `?date=YYYY-MM-DD` (optional, defaults to today) | See Section 11 for full response shape |
| GET | `/api/weekly-report` | `?date=YYYY-MM-DD` (optional, defaults to today) | 7-day aggregated report ending on that date |
| GET | `/api/history/daily-totals` | `?days=N` (default 30) | Daily calorie/macro totals + goals for chart rendering |

#### Gamification
| Method | Path | Params | Response |
|--------|------|--------|----------|
| GET | `/api/gamification` | — | `{"streak_days": N, "today_points": N, "is_elite": bool, "calorie_success": bool, "tags": [...]}` |

#### Export
| Method | Path | Params | Response |
|--------|------|--------|----------|
| GET | `/api/export/csv` | `?type=food|weight|activity|health` (required), `?start=YYYY-MM-DD&end=YYYY-MM-DD` (optional) | CSV file download |

#### Seed
| Method | Path | Params | Response |
|--------|------|--------|----------|
| POST | `/api/seed-demo-data` | — | `{"message": "Demo data seeded: 30 days of food, weight, activity, and health data."}` |

**WARNING**: `POST /api/seed-demo-data` is **DESTRUCTIVE** — it deletes ALL existing data before seeding.

---

## 6. CALORIE & MACRO CALCULATION ENGINE

### Activity Multipliers (verbatim from database.py)

```python
ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9,
}
```

### BMR Calculation — Mifflin-St Jeor (verbatim)

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

### TDEE Calculation (verbatim)

```python
def calculate_tdee(bmr: float, activity_level: str) -> float:
    """TDEE = BMR × activity multiplier."""
    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, 1.55)
    return round(bmr * multiplier, 1)
```

### Daily Goals Calculation with Dynamic Exercise Adjustment (verbatim)

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

### Key Formula Summary

```
BMR (male)   = 10 × weight_kg + 6.25 × height_cm - 5 × age + 5
BMR (female) = 10 × weight_kg + 6.25 × height_cm - 5 × age - 161
TDEE         = BMR × activity_multiplier
Effective TDEE = TDEE + exercise_calories_burned_today
Calorie Goal = Effective TDEE - calorie_deficit
Protein Goal = (Calorie Goal × 0.30) / 4 grams
Carbs Goal   = (Calorie Goal × 0.40) / 4 grams
Fat Goal     = (Calorie Goal × 0.30) / 9 grams
```

**Critical behavior**: Exercise calories are added to TDEE **before** the deficit is subtracted. This means if a user burns 300 kcal running, their calorie goal increases by 300 kcal. This is the "dynamic exercise adjustment" — daily goals change based on logged activities for that day.

---

## 7. FRONTEND ARCHITECTURE

### Single-File Architecture

The entire frontend lives in `static/dashboard.html` — a single 1,664-line file containing HTML, CSS, and JavaScript inline. No build step, no modules, no framework.

### Tabs

| Tab | ID | What It Displays |
|-----|----|-----------------|
| Overview | `tab-overview` | Macros progress bars, food log table, activities list, weight/deficit status |
| Charts | `tab-charts` | Calorie history bar chart, macro tracking line chart, weight trend line chart, activity bar chart |
| Health | `tab-health` | Latest health measurement cards (BP, sugar, SpO₂, HR), BP history chart, sugar/oxy chart |
| Profile | `tab-profile` | Profile edit form, calculated daily targets display |

### Global Above-Tab Elements (always visible)

1. **Header with date navigation**: Previous/next day buttons, date picker input, "Today" button
2. **Gamification bar**: Fire/diamond emoji + streak count + XP points
3. **Calorie ring**: SVG progress ring showing calories eaten vs goal, with remaining count

### JavaScript Functions

#### State & Initialization
| Function | Description |
|----------|-------------|
| `DOMContentLoaded` handler | Sets date, inits tabs, loads overview + profile, starts polling, attaches modal close handlers |
| `startPolling()` | Sets 30-second interval to reload overview if the Overview tab is active |
| `stopPolling()` | Clears the polling interval |
| `visibilitychange` handler | Stops polling when page hidden, reloads + restarts when visible |

#### Modal Helpers
| Function | Description |
|----------|-------------|
| `openModal(type)` | Opens the modal overlay for food/weight/activity/health |
| `closeModal(type)` | Closes the modal overlay |
| `showModalMsg(id, text, isError)` | Shows success/error message in modal, auto-hides after 3s |
| `submitFood()` | Validates and POSTs food entry, refreshes overview |
| `submitWeight()` | Validates and POSTs weight entry, refreshes overview |
| `submitActivity()` | Validates and POSTs activity entry, refreshes overview |
| `submitHealth()` | Validates and POSTs health entry, refreshes health tab |

#### Gamification
| Function | Description |
|----------|-------------|
| `loadGamification()` | Fetches `/api/gamification`, updates streak icon (🔥 or 💠 if elite), XP points, and macro status badges (good/low/over) |

#### Date Navigation
| Function | Description |
|----------|-------------|
| `changeDate(delta)` | Moves date forward/back by delta days, reloads overview |
| `onDateChange()` | Handles manual date picker change |
| `goToday()` | Resets to today's date |

#### Tabs
| Function | Description |
|----------|-------------|
| `initTabs()` | Attaches click handlers to tab buttons, lazy-loads tab content on switch |

#### Overview Tab
| Function | Description |
|----------|-------------|
| `loadOverview()` | Main data loader: fetches `/api/daily-summary`, updates calorie ring, macro bars, food log, activities, weight/deficit stats. Also calls `loadGamification()`. |
| `updateMacroBar(macro, value, goal)` | Updates a single macro progress bar width and value text |
| `renderFoodLog(entries)` | Renders food entries into table rows with time, meal badge, macros, duplicate/delete buttons |
| `renderActivities(activities)` | Renders activity entries with type, duration, intensity, calories burned |
| `deleteFood(id)` | Confirms and DELETEs a food entry, reloads overview |
| `duplicateFood(id)` | Fetches today's food, finds entry by id, POSTs a copy with current timestamp |

#### Charts Tab
| Function | Description |
|----------|-------------|
| `loadCharts(days, btn)` | Fetches daily-totals + weight + activity range data, renders all 4 charts |
| `daysAgo(n)` | Returns ISO date string for N days ago |
| `today()` | Returns today's ISO date string |
| `destroyChart(key)` | Destroys an existing Chart.js instance to prevent memory leaks |
| `renderCalorieChart(data)` | Bar chart: daily calorie intake with goal line overlay |
| `renderMacroChart(data)` | Line chart: protein/carbs/fat actuals + dashed target lines |
| `renderWeightChart(entries)` | Line chart: weight trend over time |
| `renderActivityChart(entries)` | Combo bar+line chart: duration bars + calories burned line, dual Y axes |

#### Health Tab
| Function | Description |
|----------|-------------|
| `loadHealth()` | Fetches `/api/health`, updates latest measurement cards with status badges, renders BP and sugar/oxy charts |
| `renderBPChart(entries)` | Line chart: systolic and diastolic over time |
| `renderSugarOxyChart(entries)` | Dual-axis line chart: blood sugar (left Y) and SpO₂ (right Y) |

#### Profile Tab
| Function | Description |
|----------|-------------|
| `loadProfile()` | Fetches `/api/profile`, populates form inputs, updates calculated targets |
| `updateCalcTargets(p)` | Client-side BMR/TDEE/goal calculation for live preview display |
| `saveProfile()` | PUTs profile data, shows success message, recalculates targets, reloads overview |

### Chart.js Charts (6 total)

| Chart Key | Canvas ID | Type | X Axis | Y Axis | Data Source |
|-----------|-----------|------|--------|--------|-------------|
| `calorie` | `calorieChart` | bar + line overlay | Date (MM-DD) | Calories (kcal) | `/api/history/daily-totals` |
| `macro` | `macroChart` | line (6 datasets) | Date (MM-DD) | Grams | `/api/history/daily-totals` |
| `weight` | `weightChart` | line | Date (YYYY-MM-DD) | Weight (kg) | `/api/weight` |
| `activity` | `activityChart` | bar + line combo | Date (MM-DD) | Duration (min) / Calories | `/api/activity/range` |
| `bp` | `bpChart` | line (2 datasets) | Date (YYYY-MM-DD) | mmHg | `/api/health` |
| `sugarOxy` | `sugarOxyChart` | line (dual axis) | Date (YYYY-MM-DD) | mg/dL / % | `/api/health` |

### Gamification UI Elements

- **Streak counter**: Shows `🔥 N day streak` (or `💠` diamond emoji if elite today)
- **XP counter**: Shows `⚡ N XP`
- **Macro status badges**: Per-macro indicators next to progress bars:
  - Protein: "good" (green) or "low" (red)
  - Carbs: "good" (green) or "over" (red)
  - Fat: "good" (green) or "over" (red)

### CSS Custom Properties / Theme Variables

```css
:root {
    --bg: #0d0f11;           /* Page background (near-black) */
    --surface: #161a1f;      /* Card backgrounds */
    --surface2: #1c2127;     /* Input/track backgrounds */
    --border: #2a3038;       /* Border color */
    --text: #e8ecf0;         /* Primary text */
    --text-dim: #8892a0;     /* Secondary/dim text */
    --accent: #3ecf8e;       /* Primary accent (green) */
    --accent-dim: rgba(62, 207, 142, 0.15);  /* Accent with transparency */
    --protein: #60a5fa;      /* Protein color (blue) */
    --carbs: #fbbf24;        /* Carbs color (yellow) */
    --fat: #f87171;          /* Fat color (red) */
    --calories: #3ecf8e;     /* Calories color (green) */
    --danger: #ef4444;       /* Error/danger (red) */
    --warning: #f59e0b;      /* Warning (amber) */
    --radius: 12px;          /* Border radius */
    --shadow: 0 2px 12px rgba(0,0,0,0.3);  /* Card shadow */
}
```

### Auto-Refresh / Polling Behavior

- **30-second polling interval** (`POLL_INTERVAL_MS = 30000`): Reloads overview data only when the Overview tab is active
- **Visibility-based**: Polling stops when the page is hidden (tab switch, minimize) and resumes when visible
- **On resume**: Immediately reloads overview then restarts the interval
- **Tab lazy-loading**: Charts load on first Charts tab click; Health loads on first Health tab click; Profile loads on first Profile tab click

### Modals (4 total)

1. **Food modal** (`modal-food`): Name, calories, meal type, protein, carbs, fat, quantity, notes
2. **Weight modal** (`modal-weight`): Weight (kg), notes
3. **Activity modal** (`modal-activity`): Activity type, duration, calories burned, intensity, notes
4. **Health modal** (`modal-health`): Systolic BP, diastolic BP, blood sugar, blood oxygen, heart rate, notes

All modals close on overlay click or X button. After submission, they auto-close after 800ms and reload relevant data.

---

## 8. GAMIFICATION SYSTEM

### Gamification Calculation Function (verbatim from database.py)

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

**Streaks count consecutive past days where the user stayed at or under their calorie goal.**

The streak calculation (from `GET /api/gamification` in app.py):
1. Start from **yesterday** and go backwards up to 30 days
2. For each day, check if any food was logged (if `cal == 0`, streak breaks — the user didn't log)
3. If food was logged, fetch that day's activity calories and recalculate the calorie goal for that specific day
4. If `calories_eaten <= calorie_goal`, increment streak; otherwise, break

**Important nuances:**
- Today does NOT count toward the streak (today isn't over yet)
- Days with zero food logged break the streak (even if the user simply forgot to log)
- The calorie goal is recalculated per-day based on that day's actual exercise, so a day with heavy exercise gets a higher calorie allowance

### How XP Is Earned

| Condition | Points |
|-----------|--------|
| Protein intake >= protein goal | +50 XP |
| Carbs intake <= carbs goal | +25 XP |
| Fat intake <= fat goal | +25 XP |
| All three macros met (perfect day bonus) | +50 XP |
| **Maximum per day** | **150 XP** |

Note: Protein check is "met or exceeded" (>=), while carbs and fat are "at or under" (<=).

### Elite Status

A day is "Elite" when:
1. Protein goal is met (>=)
2. Carbs are under goal (<=)
3. Fat is under goal (<=)
4. **AND** calories are under the calorie goal (<=)

All four conditions must be true. Elite status changes the streak icon from 🔥 to 💠 on the dashboard.

### Tags / Badges

The `tags` array in the gamification response can contain:
- `"protein_met"` — Protein intake meets or exceeds goal
- `"carbs_good"` — Carbs at or under goal
- `"fat_good"` — Fat at or under goal
- `"perfect_bonus"` — All three macros met (triggers +50 bonus)

### Database Tables / Endpoints

- No dedicated gamification table — all gamification is **calculated on-the-fly** from `food_entries` and `sport_activities` data
- Single endpoint: `GET /api/gamification` — calculates today's XP, streak from yesterday backwards, and elite status

### Gamification API Endpoint (verbatim from app.py)

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

    # Calculate historical streak — iterate backwards from YESTERDAY
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

---

## 9. DEPLOYMENT CONFIGURATION

### Environment Variables

| Variable | Default | Where Read | Description |
|----------|---------|-----------|-------------|
| `NUTRITRACK_DB_PATH` | `nutritrack.db` in project dir | `database.py` line 9 | Path to SQLite database file |
| `NUTRITRACK_HOST` | `0.0.0.0` | `app.py` line 18 | Server bind address |
| `NUTRITRACK_PORT` | `8000` | `app.py` line 19 | Server port |
| `NUTRITRACK_CORS_ORIGINS` | `*` | `app.py` line 21 | CORS allowed origins (comma-separated or `*`) |
| `SEED_DEMO_DATA` | `false` | `app.py` line 43 | Auto-seed demo data on first run when DB is empty |
| `TZ` | `UTC` | `docker-compose.yml` | Container timezone |
| `NUTRITRACK_DEV_MODE` | not set | `docker-compose.dev.yml` | Marker for dev mode (currently unused in code) |

### Dockerfile (verbatim)

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

### docker-compose.yml (verbatim)

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

### docker-compose.dev.yml (verbatim)

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

### install.sh Summary (step by step)

1. Check for Python 3.10+ (tries `python3` then `python`)
2. Create virtual environment (`python -m venv venv`) if not exists
3. Activate venv
4. `pip install --upgrade pip` + `pip install -r requirements.txt`
5. Initialize database (`python database.py`)
6. Ask user if they want to load 30 days of demo data (`python seed.py --force`)
7. Start server (`python app.py`)

### deploy.sh Summary

The main deployment script. Supports 4 subcommands: `start` (default), `stop`, `status`, `update`.

**`deploy.sh start`:**
1. Stop any existing instance (Docker or bare-metal PID)
2. Auto-detect Docker — if Docker daemon is accessible, use Docker; otherwise Python venv
3. **Docker path**: `docker compose up -d --build`, then health check
4. **Python path**: Find Python 3.10+, create venv, install deps, init DB, start with `nohup` in background, write PID file, health check
5. Print success summary with URLs

**`deploy.sh stop`:** Stop Docker container or kill bare-metal process by PID/port.
**`deploy.sh status`:** Check Docker or PID file, run health check.
**`deploy.sh update`:** `git pull --ff-only`, then `cmd_start`.

### start.sh (verbatim)

```bash
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate 2>/dev/null || { echo "Run ./install.sh first"; exit 1; }
echo "NutriTrack starting at http://localhost:${NUTRITRACK_PORT:-8000}"
python3 app.py
```

### stop.sh (verbatim)

```bash
#!/bin/bash
pkill -f "python3 app.py" 2>/dev/null && echo "NutriTrack stopped" || echo "NutriTrack is not running"
```

### dev.sh Summary

1. Check if Docker available and ask user if they want Docker dev mode
2. Docker path: `docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build`
3. Bare metal path: Activate venv, start uvicorn with `--reload --reload-dir .`

### .env.example (verbatim)

```bash
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

---

## 10. CORS & MIDDLEWARE

### CORS Configuration (verbatim from app.py)

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

### Middleware Stack

1. **CORSMiddleware** — The only middleware. Allows all origins by default (`*`), all methods, all headers, with credentials.

### Static File Serving

```python
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
```

The dashboard is NOT served from the static mount — it's served by the `GET /` endpoint which reads `dashboard.html` and returns it as `HTMLResponse` with `Cache-Control: no-cache, no-store, must-revalidate` headers.

---

## 11. KEY CODE SECTIONS — VERBATIM

### database.py — Full `init_db()` function

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

### database.py — Helper functions and DB_PATH

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

### app.py — Helper functions

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

### app.py — `/api/daily-summary` endpoint (verbatim)

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

### app.py — `/api/weekly-report` endpoint (verbatim)

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

### app.py — CORS middleware setup

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

### app.py — uvicorn startup block

```python
if __name__ == "__main__":
    uvicorn.run("app:app", host=HOST, port=PORT)
```

### app.py — Startup event (auto-seed logic)

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

### app.py — `/api/history/daily-totals` endpoint (verbatim)

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

### app.py — CSV Export endpoint (verbatim)

```python
@app.get("/api/export/csv")
def export_csv(type: str = Query(..., pattern="^(food|weight|activity|health)$"),
               start: Optional[str] = None, end: Optional[str] = None):
    """Export data as CSV. Type: food, weight, activity, health."""
    import csv
    import io

    conn = get_db()
    table_map = {
        "food": ("food_entries", "logged_at"),
        "weight": ("weight_logs", "measured_at"),
        "activity": ("sport_activities", "performed_at"),
        "health": ("health_measurements", "measured_at"),
    }
    table, ts_col = table_map[type]

    query = f"SELECT * FROM {table}"
    params = []
    if start and end:
        s = datetime.combine(date.fromisoformat(start), datetime.min.time()).isoformat()
        e = datetime.combine(date.fromisoformat(end), datetime.max.time()).isoformat()
        query += f" WHERE {ts_col} BETWEEN ? AND ?"
        params = [s, e]
    query += f" ORDER BY {ts_col}"

    rows = conn.execute(query, params).fetchall()
    conn.close()

    if not rows:
        return StreamingResponse(
            iter(["No data found for the specified range.\n"]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=nutritrack_{type}.csv"},
        )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(rows[0].keys())
    for row in rows:
        writer.writerow(tuple(row))

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=nutritrack_{type}.csv"},
    )
```

### dashboard.html — `loadOverview()` function (verbatim)

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

### dashboard.html — `loadGamification()` function (verbatim)

```javascript
async function loadGamification() {
    try {
        const res = await fetch(`${API}/api/gamification`);
        const data = await res.json();
        if (data.error) return;

        // Streak
        document.getElementById('streak-days').textContent = data.streak_days;
        document.getElementById('streak-icon').textContent = data.is_elite ? '💠' : '🔥';

        // Points
        document.getElementById('daily-points').textContent = data.today_points;

        // Macro status badges
        const tags = data.tags || [];

        const proteinEl = document.getElementById('status-protein');
        if (tags.includes('protein_met')) {
            proteinEl.textContent = 'good';
            proteinEl.style.color = '#3ecf8e';
        } else {
            proteinEl.textContent = 'low';
            proteinEl.style.color = '#f87171';
        }

        const carbsEl = document.getElementById('status-carbs');
        if (tags.includes('carbs_good')) {
            carbsEl.textContent = 'good';
            carbsEl.style.color = '#3ecf8e';
        } else {
            carbsEl.textContent = 'over';
            carbsEl.style.color = '#f87171';
        }

        const fatEl = document.getElementById('status-fat');
        if (tags.includes('fat_good')) {
            fatEl.textContent = 'good';
            fatEl.style.color = '#3ecf8e';
        } else {
            fatEl.textContent = 'over';
            fatEl.style.color = '#f87171';
        }

    } catch (err) {
        console.error('Gamification load error:', err);
    }
}
```

### dashboard.html — All chart rendering functions (verbatim)

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
                {
                    label: 'Protein Target',
                    data: data.map(d => d.protein_goal_g),
                    borderColor: 'rgba(96,165,250,0.4)',
                    borderDash: [6, 4],
                    borderWidth: 1.5,
                    pointRadius: 0,
                    fill: false,
                    tension: 0.3,
                },
                {
                    label: 'Carbs Target',
                    data: data.map(d => d.carbs_goal_g),
                    borderColor: 'rgba(251,191,36,0.4)',
                    borderDash: [6, 4],
                    borderWidth: 1.5,
                    pointRadius: 0,
                    fill: false,
                    tension: 0.3,
                },
                {
                    label: 'Fat Target',
                    data: data.map(d => d.fat_goal_g),
                    borderColor: 'rgba(248,113,113,0.4)',
                    borderDash: [6, 4],
                    borderWidth: 1.5,
                    pointRadius: 0,
                    fill: false,
                    tension: 0.3,
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

    const byDate = {};
    entries.forEach(e => {
        const day = e.performed_at.slice(0, 10);
        if (!byDate[day]) byDate[day] = { duration: 0, burned: 0, count: 0 };
        byDate[day].duration += e.duration_minutes;
        byDate[day].burned += e.calories_burned;
        byDate[day].count++;
    });

    const allDates = Object.keys(byDate).sort();
    let dates = [];

    if (allDates.length > 0) {
        const earliest = new Date(allDates[0]);
        const latest = new Date(allDates[allDates.length - 1]);
        const rangeDays = Math.round((latest - earliest) / (1000 * 60 * 60 * 24)) + 1;
        const minDays = Math.max(rangeDays, 7);

        for (let i = 0; i < minDays; i++) {
            const d = new Date(earliest);
            d.setDate(d.getDate() + i);
            const ds = d.toISOString().slice(0, 10);
            dates.push(ds);
            if (!byDate[ds]) byDate[ds] = { duration: 0, burned: 0, count: 0 };
        }
    }

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
                    maxBarThickness: 28,
                    barPercentage: 0.6,
                    categoryPercentage: 0.7,
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

### seed.py — Entire file

(See Section 8 of this document — the full seed.py is reproduced there verbatim.)

---

## 12. AGENT INTEGRATION

### How Agents Discover and Use the API

1. Agent receives the **SKILL.md** file (9,262 bytes) which contains everything: API reference, nutrition estimation tables, MET values for exercise, gamification rules, deployment instructions
2. Agent reads the `NUTRITRACK_URL` environment variable (defaults to `http://localhost:8000`)
3. Agent health-checks with `GET /api/profile`
4. Agent creates user profile with `PUT /api/profile` if none exists
5. Agent translates natural language into structured API calls

### docs/AGENT_README.md Summary

The AGENT_README.md is 1,286 lines and covers:
- Server configuration (base URL, content type, no auth)
- First-time profile setup with field descriptions and constraints
- Complete API reference with curl examples for every endpoint
- Common food reference table (20+ items with macros)
- MET values for 15+ exercise types
- Health measurement interpretation (BP, sugar, SpO₂, HR ranges)
- Error handling (HTTP status codes and recommended actions)
- Full workflow summary (10-step interaction pattern)

### docs/AGENT_DEPLOY.md Summary

Covers:
- One-command deploy (`git clone` + `./deploy.sh`)
- Management commands (start/stop/status/update)
- Verify with `curl`
- Environment variables (NUTRITRACK_PORT, NUTRITRACK_HOST)
- Data safety (DB location, Docker volumes, git safety)
- Optional systemd user service setup (no sudo)
- Troubleshooting table

### Key Agent Behaviors

- **No authentication**: Single-user, local-first design
- **Content-Type**: Always `application/json`
- **Timestamps**: ISO 8601 format. Omit to default to server time.
- **Food estimation**: Agent estimates macros from natural language. SKILL.md provides a reference table.
- **Exercise calories**: Agent calculates using `MET x weight_kg x duration_hours` formula
- **Weight logging side effect**: `POST /api/weight` updates profile, recalculating all goals

---

## 13. CURRENT STATE & KNOWN ISSUES

### What Works Perfectly

- All CRUD operations for food, weight, activity, health
- Profile create/update with calorie goal recalculation
- Daily summary and weekly report generation
- All 6 Chart.js charts render correctly
- Gamification (streaks, XP, elite status) calculates correctly
- CSV export for all data types
- Demo data seeding (both API endpoint and standalone script)
- Docker and bare-metal deployment
- Auto-polling every 30 seconds on the overview tab
- Date navigation (forward/back/today/picker)
- Mobile responsive layout
- Modals for manual data entry

### Known Issues / Areas for Improvement

1. **`activity_level` not validated in Pydantic model**: `ProfileCreate.activity_level` uses `Field(default="moderate")` but has no `pattern` or enum validation — any string is accepted. The database CHECK constraint catches invalid values, but the error message is a generic 500 rather than a clean 422. The database constraint is: `CHECK(activity_level IN ('sedentary', 'light', 'moderate', 'active', 'very_active'))`.

2. **`meal_type` not validated in Pydantic model**: `FoodEntry.meal_type` defaults to `"snack"` but has no pattern validation. Invalid values pass Pydantic but fail at the database CHECK constraint.

3. **`intensity` not validated in Pydantic model**: Same issue — `ActivityEntry.intensity` accepts any string, but DB constrains to `('low', 'moderate', 'high')`.

4. **No GET /api/food/{id}** endpoint: The `duplicateFood()` JavaScript function has to re-fetch the entire day's food list and find the entry by ID, instead of fetching a single entry directly. Comment in code acknowledges this.

5. **Weekly report uses `__import__('datetime')`**: Line 463 of app.py has `end_d = date_obj = __import__('datetime').date.fromisoformat(end_date)` — the `date` import from `datetime` is already available at module level, so this is unnecessarily convoluted. Also `date_obj` is assigned but never used.

6. **Unused variable `elite_streak`**: In the gamification endpoint (app.py line 673), `elite_streak = False` is set but never used or returned.

7. **No authentication/authorization**: Intentional design choice for single-user local deployment, but anyone on the network can access the API if the host is `0.0.0.0`.

8. **No rate limiting**: API has no rate limiting or abuse protection.

9. **CSV export SQL injection surface**: The `export_csv` function uses f-string for table name (`f"SELECT * FROM {table}"`), but the `type` parameter is validated by Pydantic regex to only allow `food|weight|activity|health`, so this is safe in practice.

10. **Polling only on Overview tab**: Charts, Health, and Profile tabs don't auto-refresh. Users must manually switch tabs to trigger a reload.

### Recently Changed / Added

Based on the last 10 commits (all from 2026-02-17 and 2026-02-18):
- Added one-command deploy system (`deploy.sh`)
- Added AI agent setup guide (SKILL.md, AGENT_DEPLOY.md)
- Consolidated skill files into single SKILL.md per OpenClaw convention
- Removed Seed Demo Data button from profile section (data entry is agent-only)
- Moved calorie ring below gamification bar
- Moved activities panel below food log in overview tab

### TODO/FIXME/HACK/XXX Comments

**None found in any source file.** The codebase has zero TODO/FIXME/HACK/XXX comments.

### Hardcoded Values That Could Be Configurable

- **Macro split**: 30% protein / 40% carbs / 30% fat is hardcoded in `calculate_daily_goals()`
- **Polling interval**: 30 seconds hardcoded in `dashboard.html` (`POLL_INTERVAL_MS = 30000`)
- **Streak lookback**: 30 days max (`range(1, 31)` in gamification endpoint)
- **Food search limit**: 20 results max (hardcoded in SQL query)
- **Default weight/health history limit**: 90 entries
- **Chart range options**: 7, 14, 30, 90 days (hardcoded in HTML buttons)
- **Demo data profile**: age=30, male, 180cm, 85kg in API seed endpoint (age=32 in seed.py standalone)

### Performance Considerations

- **Gamification endpoint makes N+1 queries**: For a 30-day streak, it runs ~60 individual SELECT queries (food + activity for each day). Could be optimized with a single GROUP BY query.
- **Daily totals endpoint is well-optimized**: Uses GROUP BY for aggregation with O(1) dictionary lookups.
- **No connection pooling**: Each endpoint creates a new SQLite connection and closes it. Fine for single-user, but could be an issue at scale.
- **Dashboard loads all data at once**: `loadOverview()` fetches the entire daily summary in one call, which is efficient.

---

## 14. GIT STATUS

### Current Branch
```
main
```

### Remote URL
```
origin  https://github.com/BenZenTuna/Nutritrack.git
```

### Last 10 Commits

| Hash | Date | Message |
|------|------|---------|
| `243bb51` | 2026-02-18 | fix: correct broken SKILL.md and install script URLs in README |
| `2142cdf` | 2026-02-18 | Remove instructions for other AI agents |
| `2a273bb` | 2026-02-18 | style: remove Seed Demo Data button from profile section |
| `5e9683d` | 2026-02-18 | docs: make AI agent install the primary option in README |
| `851fbec` | 2026-02-18 | feat: add one-command deploy system and AI agent setup guide |
| `c91a9c2` | 2026-02-17 | refactor: consolidate skill files into SKILL.md per OpenClaw convention |
| `59e6d9c` | 2026-02-17 | feat: add compact SKILL.md for OpenClaw agent discovery |
| `f1312a4` | 2026-02-17 | docs: clarify agent skill file (nutritrack.md) in README |
| `57982f6` | 2026-02-17 | style: move calorie ring below gamification bar and enlarge gamification 2x |
| `917741e` | 2026-02-17 | style: move activities panel below food log in overview tab |

### Uncommitted Changes
```
(clean)
```

---

## 15. DEPENDENCIES & VERSIONS

### Python Packages (from requirements.txt)

```
fastapi     (no version pin)
uvicorn     (no version pin)
aiofiles    (no version pin)
pydantic    (no version pin)
```

No pinned versions — `pip install -r requirements.txt` installs latest compatible versions.

### Python Version

- **Development**: Python 3.11-slim (Docker image)
- **Minimum required**: Python 3.10+ (checked in install.sh and deploy.sh)
- **Current host**: Python 3.14.2

### Frontend CDN Dependencies

| Library | Version | URL |
|---------|---------|-----|
| Chart.js | 4.4.1 | `https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js` |
| chartjs-adapter-date-fns | 3.0.0 | `https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns@3.0.0/dist/chartjs-adapter-date-fns.bundle.min.js` |
| Google Fonts (DM Sans + Space Mono) | — | `https://fonts.googleapis.com/css2?family=DM+Sans:...&family=Space+Mono:...` |

### System Packages Needed

- `python3` (3.10+)
- `python3-venv` (for virtual environment creation)
- `python3-pip` (for package installation)
- `curl` (used by deploy.sh health checks)
- `docker` + `docker compose` (optional, auto-detected)

---

## APPENDIX: Utility Scripts

### migrate.py

One-time migration script from an older nutrition tracker database. Maps old `users` table to new `user_profile`, converts food and exercise log entries. Hardcoded paths to old DB. Not used in normal operation.

### fix_timestamps.py

One-time utility that converts space-separated timestamps (`YYYY-MM-DD HH:MM:SS`) to ISO format with `T` separator (`YYYY-MM-DDTHH:MM:SS`). Was needed after migration. Not used in normal operation.

### test_profile_update.py

Simple test script that sends a PUT request to `/api/profile` using the `requests` library. Requires the server to be running. Not part of any test suite.

### scripts/install.sh

4-line wrapper for OpenClaw skill installation — just delegates to the main `install.sh`.

### setup.sh

Simplified setup script (no venv): installs deps globally with `--break-system-packages`, inits DB, starts server. Alternative to install.sh for simple setups.
