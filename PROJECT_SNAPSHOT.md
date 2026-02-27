# NutriTrack — Complete Project Snapshot

> **Generated**: 2026-02-27
> **Purpose**: Full knowledge transfer document for onboarding a fresh Claude session with zero context.
> **Branch**: `main` at commit `8947080`

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
- **Agent-Curated Philosophy**: Often-used foods, coaching tips, and weekly reports are all agent-curated — the AI agent decides what goes in, not auto-generated algorithms.
- **Gamification**: Streaks, best streak record, elite status, activity emoji chips, and macro achievement badges keep users motivated.
- **Two-Tier AI Coaching**: Daily post-meal tips + weekly health reports, both written by the AI agent.
- **Self-Hosted / Local-First**: Runs on the user's machine, no cloud accounts, no external services, no data leaves the machine.
- **Zero Configuration**: SQLite database, no database server needed. One command to deploy.
- **LLM-Agnostic**: Any agent that can make HTTP calls works. The SKILL.md file gives any agent everything it needs.

---

## 2. COMPLETE FILE TREE

```
TT-Nutritrack/
├── .env.example                   22 lines   4K   — Example environment variable configuration
├── .gitignore                     17 lines   4K   — Git ignore rules (db, pycache, venv, data/, etc.)
├── Dockerfile                     21 lines   4K   — Docker image definition (Python 3.11-slim)
├── LICENSE                        21 lines   4K   — MIT License
├── PROJECT_SNAPSHOT.md                             — THIS FILE (project knowledge transfer)
├── README.md                     336 lines  16K   — Project README with install guide and API reference
├── SKILL.md                      449 lines  20K   — OpenClaw agent skill file (full API + nutrition reference)
├── app.py                       1266 lines  52K   — FastAPI server: all endpoints, Pydantic models, CORS
├── database.py                   228 lines  12K   — SQLite schema, init, calorie/macro calculation engine
├── deploy.sh                     366 lines  16K   — One-command deploy (auto-detects Docker or Python)
├── dev.sh                         27 lines   4K   — Development mode with auto-reload
├── docker-compose.dev.yml         19 lines   4K   — Docker dev overrides (live mount + reload)
├── docker-compose.yml             27 lines   4K   — Production Docker Compose
├── docs/
│   ├── AGENT_DEPLOY.md           116 lines   4K   — Agent deployment guide (commands, env vars, troubleshooting)
│   ├── AGENT_README.md          1328 lines  44K   — Complete AI agent integration guide (full API reference)
│   └── screenshots/
│       ├── charts.png            264K              — Screenshot of Charts tab
│       ├── health.png            252K              — Screenshot of Health tab
│       └── overview.png          160K              — Screenshot of Overview tab
├── fix_timestamps.py              29 lines   4K   — One-time migration utility: fix timestamp format
├── install.sh                     97 lines   4K   — Interactive installer (venv + deps + optional seed)
├── migrate.py                    113 lines   8K   — One-time migration from old nutrition tracker DB
├── requirements.txt                4 lines   4K   — Python dependencies
├── scripts/
│   └── install.sh                  4 lines   4K   — Wrapper for OpenClaw skill install
├── seed.py                       187 lines   8K   — Standalone demo data seeder (30 days of data)
├── setup.sh                       31 lines   4K   — Simple setup & run script (no venv)
├── start.sh                        5 lines   4K   — Start server (requires prior install)
├── static/
│   └── dashboard.html           2277 lines 116K   — Single-page dashboard (HTML + CSS + JS, all inline)
├── stop.sh                         2 lines   4K   — Stop server (pkill)
└── test_profile_update.py         23 lines   4K   — Simple test script for profile PUT endpoint
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
- **Docker** — Python 3.11-slim base image
- **Docker Compose** — Named volume for data persistence, healthcheck

---

## 4. DATABASE SCHEMA — FULL DUMP

All tables are created in `database.py:init_db()`. The database uses SQLite with WAL mode and foreign keys enabled.

### Tables

#### user_profile (agent-managed)
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
```

#### food_entries (agent-managed)
```sql
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
```

#### weight_logs (agent-managed)
```sql
CREATE TABLE IF NOT EXISTS weight_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    weight_kg REAL NOT NULL,
    notes TEXT,
    measured_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

#### sport_activities (agent-managed)
```sql
CREATE TABLE IF NOT EXISTS sport_activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    activity_type TEXT NOT NULL,
    duration_minutes INTEGER NOT NULL DEFAULT 0,
    calories_burned REAL NOT NULL DEFAULT 0,
    intensity TEXT DEFAULT 'moderate' CHECK(intensity IN ('low', 'moderate', 'high')),
    notes TEXT,
    performed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

#### health_measurements (agent-managed)
```sql
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

#### often_used_foods (agent-curated — replaced entirely by agent)
```sql
DROP TABLE IF EXISTS often_used_foods;
CREATE TABLE IF NOT EXISTS often_used_foods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    calories REAL NOT NULL DEFAULT 0,
    protein_g REAL NOT NULL DEFAULT 0,
    carbs_g REAL NOT NULL DEFAULT 0,
    fat_g REAL NOT NULL DEFAULT 0,
    meal_type TEXT DEFAULT 'snack',
    sort_order INTEGER NOT NULL DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
**Note**: The `DROP TABLE IF EXISTS` is intentional — the table is recreated on every `init_db()` call. This is safe because the often-used list is agent-curated and can always be regenerated.

#### daily_coaching (agent-written daily tips)
```sql
CREATE TABLE IF NOT EXISTS daily_coaching (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    coaching_date TEXT NOT NULL UNIQUE,
    coaching_text TEXT NOT NULL,
    meal_count INTEGER DEFAULT 0,
    calories_so_far REAL DEFAULT 0,
    calories_remaining REAL DEFAULT 0,
    protein_status TEXT DEFAULT 'unknown',
    top_priority TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### coaching_reports (agent-written weekly reports)
```sql
CREATE TABLE IF NOT EXISTS coaching_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    week_start TEXT NOT NULL,
    week_end TEXT NOT NULL,
    report_text TEXT NOT NULL,
    summary_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Indexes
```sql
CREATE INDEX IF NOT EXISTS idx_often_used_updated ON often_used_foods(updated_at);
CREATE INDEX IF NOT EXISTS idx_food_logged_at ON food_entries(logged_at);
CREATE INDEX IF NOT EXISTS idx_weight_measured_at ON weight_logs(measured_at);
CREATE INDEX IF NOT EXISTS idx_activity_performed_at ON sport_activities(performed_at);
CREATE INDEX IF NOT EXISTS idx_health_measured_at ON health_measurements(measured_at);
CREATE INDEX IF NOT EXISTS idx_daily_coaching_date ON daily_coaching(coaching_date);
CREATE INDEX IF NOT EXISTS idx_coaching_created ON coaching_reports(created_at);
CREATE INDEX IF NOT EXISTS idx_coaching_week ON coaching_reports(week_start, week_end);
```

### Relationships
There are **no foreign keys between tables**. Each table is independent. The user_profile table has at most one row (upsert pattern). All other tables have timestamps for date-based querying.

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

class OftenUsedItem(BaseModel):
    name: str
    calories: float = 0
    protein_g: float = 0
    carbs_g: float = 0
    fat_g: float = 0
    meal_type: str = "snack"

class OftenUsedUpdate(BaseModel):
    items: list[OftenUsedItem]

class DailyCoaching(BaseModel):
    coaching_date: str  # YYYY-MM-DD
    coaching_text: str  # Full coaching tip (can be multi-line)
    meal_count: Optional[int] = 0
    calories_so_far: Optional[float] = 0
    calories_remaining: Optional[float] = 0
    protein_status: Optional[str] = "unknown"  # on_track, low, critical, exceeded
    top_priority: Optional[str] = None  # One-line priority

class CoachingReport(BaseModel):
    week_start: str
    week_end: str
    report_text: str
    summary_json: Optional[str] = None
```

### Endpoint Details

#### Profile

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/profile` | Returns `{profile: {...}}` or `{profile: null, message: "..."}` |
| `PUT` | `/api/profile` | **Upsert** — creates if none exists, updates if exists. On first create, also logs initial weight to `weight_logs`. Returns `{profile: {...}, message: "..."}` |

**Side effects of PUT /api/profile**: When creating a new profile (no existing row), it also inserts a `weight_logs` entry with the initial weight.

#### Food

| Method | Path | Query Params | Description |
|--------|------|-------------|-------------|
| `POST` | `/api/food` | — | Log a food entry. Returns `{entry, message, coaching_tips}`. **Side effect**: generates server-side coaching tips based on updated daily totals. |
| `GET` | `/api/food` | `?date=YYYY-MM-DD` (optional, default: today) | Get food entries for a date |
| `GET` | `/api/food/search` | `?q=string` (min 1 char) | Search past food entries by name. Returns DISTINCT results by name. |
| `GET` | `/api/food/range` | `?start=YYYY-MM-DD&end=YYYY-MM-DD` | Get food entries for a date range |
| `PUT` | `/api/food/{id}` | — | Update a food entry |
| `DELETE` | `/api/food/{id}` | — | Delete a food entry |

#### Often-Used Foods (Agent-Curated)

| Method | Path | Query Params | Description |
|--------|------|-------------|-------------|
| `GET` | `/api/food/history/frequent` | `?days=14` (default 14) | Get frequency-sorted food history for agent analysis. Returns `{days_analyzed, items[], instruction}`. Agent uses this to build the curated list. |
| `PUT` | `/api/food/often-used` | — | **Replace entire list** with agent-curated items. Max 15 items. Deletes all existing items first, then inserts new ones. |
| `GET` | `/api/food/often-used` | — | Get the curated often-used foods list, sorted by `sort_order` |
| `POST` | `/api/food/often-used/{id}/add` | — | Quick-add one portion of an often-used item to today's food log. Creates a `food_entries` row with current timestamp. |

#### Weight

| Method | Path | Query Params | Description |
|--------|------|-------------|-------------|
| `POST` | `/api/weight` | — | Log a weight measurement. **Side effect**: also updates `user_profile.current_weight_kg` |
| `GET` | `/api/weight` | `?limit=90` (default 90) | Get weight history, ordered by `measured_at DESC` |

#### Activity

| Method | Path | Query Params | Description |
|--------|------|-------------|-------------|
| `POST` | `/api/activity` | — | Log an exercise activity |
| `GET` | `/api/activity` | `?date=YYYY-MM-DD` (optional, default: today) | Get activities for a date |
| `GET` | `/api/activity/range` | `?start=YYYY-MM-DD&end=YYYY-MM-DD` | Get activities for a date range |
| `PUT` | `/api/activity/{id}` | — | Update an activity entry |
| `DELETE` | `/api/activity/{id}` | — | Delete an activity entry |

#### Health

| Method | Path | Query Params | Description |
|--------|------|-------------|-------------|
| `POST` | `/api/health` | — | Log a health measurement |
| `GET` | `/api/health` | `?limit=90` (default 90) | Get health history, ordered by `measured_at DESC` |
| `PUT` | `/api/health/{id}` | — | Update a health measurement |
| `DELETE` | `/api/health/{id}` | — | Delete a health measurement |

#### Reports & Summaries

| Method | Path | Query Params | Description |
|--------|------|-------------|-------------|
| `GET` | `/api/daily-summary` | `?date=YYYY-MM-DD` (optional, default: today) | Full daily summary with profile, goals, intake, remaining, food entries, activities, latest weight |
| `GET` | `/api/weekly-report` | `?date=YYYY-MM-DD` (end date, default: today) | 7-day aggregated report. Includes daily nutrition breakdown, weight change, activity summary, health averages |
| `GET` | `/api/history/daily-totals` | `?days=30` (default 30) | Daily calorie/macro totals for charting. Fills gaps with zeros. Includes per-day goals adjusted for activity. |

#### Coaching

| Method | Path | Query Params | Description |
|--------|------|-------------|-------------|
| `GET` | `/api/coaching` | `?date=YYYY-MM-DD` | Server-generated coaching tips (based on current intake vs goals). Not agent-written. |
| `PUT` | `/api/coaching/daily` | — | **Upsert** agent-written daily coaching tip. Keyed by `coaching_date`. |
| `GET` | `/api/coaching/daily` | `?date=YYYY-MM-DD` | Get agent-written daily coaching for a date |
| `POST` | `/api/coaching/report` | — | **Upsert** weekly coaching report. Keyed by `(week_start, week_end)`. |
| `GET` | `/api/coaching/reports` | `?limit=12` | List all weekly reports, ordered by `week_end DESC` |
| `GET` | `/api/coaching/reports/latest` | — | Get most recent weekly report |
| `DELETE` | `/api/coaching/reports/{id}` | — | Delete a weekly report |

#### Gamification

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/gamification` | Returns `{streak_days, best_streak, today_points, is_elite, calorie_success, tags[], activities_today[]}` |

#### Export

| Method | Path | Query Params | Description |
|--------|------|-------------|-------------|
| `GET` | `/api/export/csv` | `?type=food|weight|activity|health` + optional `start` and `end` dates | Export data as CSV download |

#### Seed

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/seed-demo-data` | Populate DB with 30 days of realistic demo data. **Clears all existing data first.** |

#### Dashboard

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Serves `dashboard.html` with `Cache-Control: no-cache` |

---

## 6. CALORIE & MACRO CALCULATION ENGINE

All calculations live in `database.py`. These are the core formulas that drive all calorie goals throughout the app.

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

### BMR Calculation (Mifflin-St Jeor Equation)
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

### TDEE Calculation
```python
def calculate_tdee(bmr: float, activity_level: str) -> float:
    """TDEE = BMR × activity multiplier."""
    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, 1.55)
    return round(bmr * multiplier, 1)
```

### Full Daily Goals
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

**Key design decisions:**
- Exercise calories are added to TDEE **before** applying the deficit (so you get them back)
- Macro split is fixed at **30% protein / 40% carbs / 30% fat**
- Protein and carbs use 4 cal/g, fat uses 9 cal/g
- Default deficit is 500 kcal

---

## 7. COACHING SYSTEM (TWO-TIER)

### Tier 1: Server-Generated Coaching Tips

When food is logged via `POST /api/food`, the server automatically generates simple coaching tips in the response. This is the `generate_coaching_tips()` function in `app.py`:

```python
def generate_coaching_tips(profile: dict, intake: dict, goals: dict) -> list:
    """Generate contextual coaching tips based on current intake vs goals."""
    tips = []
    remaining_cal = goals["calorie_goal"] - intake["calories"]
    remaining_prot = goals["protein_goal_g"] - intake["protein_g"]
    remaining_carbs = goals["carbs_goal_g"] - intake["carbs_g"]
    remaining_fat = goals["fat_goal_g"] - intake["fat_g"]

    # Calorie tips
    if remaining_cal < 0:
        tips.append(f"You're {abs(round(remaining_cal))} kcal over your goal. Consider a lighter next meal or a short walk to offset.")
    elif remaining_cal < 200 and remaining_cal >= 0:
        tips.append(f"Only {round(remaining_cal)} kcal left today. A light snack like veggies or a small fruit would fit well.")
    elif remaining_cal > 800:
        tips.append(f"You still have {round(remaining_cal)} kcal available. Make sure to eat enough to fuel your body.")

    # Protein tips
    if remaining_prot > 30:
        tips.append(f"You need {round(remaining_prot)}g more protein today. Consider chicken, fish, eggs, or a protein shake.")
    elif remaining_prot <= 0:
        tips.append("Great job hitting your protein target!")

    # Fat tips
    if remaining_fat < 0:
        tips.append(f"You're {abs(round(remaining_fat))}g over your fat goal. Choose leaner options for your remaining meals.")

    # Carbs tips
    if remaining_carbs < 0:
        tips.append(f"Carbs are {abs(round(remaining_carbs))}g over goal. Swap starchy sides for vegetables if eating again today.")

    if not tips:
        tips.append("You're on track! Keep it up.")

    return tips
```

These tips are returned in the `coaching_tips` field of the `POST /api/food` response but are **not stored** in the database.

There is also a dedicated `GET /api/coaching?date=` endpoint that computes these tips on demand.

### Tier 2: Agent-Written Daily Coaching

The AI agent writes richer coaching tips and stores them via `PUT /api/coaching/daily`. The dashboard displays these in a collapsible panel below the macro bars:

- **One-line priority** (`top_priority` field) — always visible as the panel header
- **Protein status badge** (`protein_status` field: `on_track`, `low`, `critical`, `exceeded`)
- **Full coaching text** (`coaching_text` field) — visible when expanded
- **Meta info** — meal count, calories so far, calories remaining

**Agent workflow**: After every `POST /api/food`, the agent should call `GET /api/daily-summary`, analyze the data, and call `PUT /api/coaching/daily` with an updated coaching tip.

### Tier 3: Agent-Written Weekly Reports

The agent writes comprehensive weekly reports stored via `POST /api/coaching/report`. Each report has:
- `report_text`: The full text of the report (multi-line, formatted)
- `summary_json`: A JSON string with structured data for dashboard summary cards

**Expected summary_json structure:**
```json
{
    "grade": "B+",
    "avg_calories": 1850,
    "calorie_goal": 2000,
    "weight_change": -0.5,
    "days_on_track": 5,
    "days_total": 7,
    "streak_days": 4,
    "action_items": [
        "Increase protein at breakfast",
        "Add one more workout day",
        "Reduce evening snacking"
    ]
}
```

The dashboard renders these in the **Coaching tab** with:
- Week selector pills (up to 12 weeks)
- Summary stat cards (grade, avg calories, weight change, days on track)
- Formatted report text with section headers, bullet items
- Action items card

---

## 8. OFTEN-USED FOODS SYSTEM (Agent-Curated)

This is NOT an auto-generated list. The AI agent curates it by:

1. **Analyzing history**: Agent calls `GET /api/food/history/frequent?days=14` to get frequency-sorted food data
2. **Curating**: Agent deduplicates, normalizes to base units (1 egg, 100g, 1 scoop), limits to max 15 items
3. **Replacing**: Agent calls `PUT /api/food/often-used` with the curated list (this deletes ALL existing items and inserts new ones)

### API Endpoints

**GET /api/food/history/frequent** — Returns frequency data for agent analysis:
```python
@app.get("/api/food/history/frequent")
def get_frequent_foods(days: int = 14):
    """Get frequency-sorted food history for agent analysis."""
    conn = get_db()
    rows = conn.execute("""
        SELECT name,
               meal_type,
               COUNT(*) as times_logged,
               ROUND(MIN(calories), 1) as min_cal,
               ROUND(AVG(calories), 1) as avg_cal,
               ROUND(MAX(calories), 1) as max_cal,
               ROUND(MIN(protein_g), 1) as min_prot,
               ROUND(AVG(protein_g), 1) as avg_prot,
               ROUND(MIN(carbs_g), 1) as min_carb,
               ROUND(AVG(carbs_g), 1) as avg_carb,
               ROUND(MIN(fat_g), 1) as min_fat,
               ROUND(AVG(fat_g), 1) as avg_fat,
               quantity
        FROM food_entries
        WHERE logged_at >= date('now', '-' || ? || ' days')
        GROUP BY LOWER(TRIM(name))
        ORDER BY times_logged DESC
        LIMIT 30
    """, (days,)).fetchall()
    conn.close()

    return {
        "days_analyzed": days,
        "items": rows_to_list(rows),
        "instruction": "Analyze these items. Deduplicate similar entries, normalize each to its minimum base unit (1 egg, 100g, 1 scoop). Include the unit in the name. Then call PUT /api/food/often-used with the curated list of max 15 items."
    }
```

**PUT /api/food/often-used** — Replace entire list:
```python
@app.put("/api/food/often-used")
def update_often_used(data: OftenUsedUpdate):
    """Replace the entire often-used foods list with agent-curated items."""
    if len(data.items) > 15:
        raise HTTPException(status_code=400, detail="Maximum 15 items allowed")

    conn = get_db()
    conn.execute("DELETE FROM often_used_foods")

    for i, item in enumerate(data.items):
        conn.execute(
            "INSERT INTO often_used_foods (name, calories, protein_g, carbs_g, fat_g, meal_type, sort_order) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (item.name, item.calories, item.protein_g, item.carbs_g, item.fat_g,
             item.meal_type, i)
        )

    conn.commit()
    items = conn.execute("SELECT * FROM often_used_foods ORDER BY sort_order").fetchall()
    conn.close()

    return {
        "message": f"Often-used list updated with {len(data.items)} items.",
        "count": len(data.items),
        "items": rows_to_list(items)
    }
```

**POST /api/food/often-used/{item_id}/add** — Quick-add to today:
```python
@app.post("/api/food/often-used/{item_id}/add")
def add_often_used_to_today(item_id: int):
    """Quick-add one portion of an often-used food item to today's log."""
    conn = get_db()
    item = conn.execute("SELECT * FROM often_used_foods WHERE id = ?", (item_id,)).fetchone()

    if not item:
        conn.close()
        raise HTTPException(status_code=404, detail="Item not found in often-used list")

    now = datetime.now()
    conn.execute(
        "INSERT INTO food_entries (name, calories, protein_g, carbs_g, fat_g, meal_type, logged_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (item["name"], item["calories"], item["protein_g"], item["carbs_g"],
         item["fat_g"], item["meal_type"], now.isoformat())
    )
    conn.commit()
    conn.close()

    today_str = now.strftime("%d.%m.%y")
    return {
        "message": f"Added {item['name']} to your {today_str} consumed items",
        "entry_name": item["name"],
        "date": today_str,
        "calories": item["calories"],
    }
```

### Dashboard UI

The food log has a **segmented control** (sub-tabs) switching between "Food Log" and "Often Used":
- Food Log panel: standard meal table with time, meal badge, name, quantity, macros, duplicate/delete buttons
- Often Used panel: list of agent-curated items with name, macros, and a `+` quick-add button

---

## 9. FRONTEND ARCHITECTURE

### File Structure

Everything is in a single file: `static/dashboard.html` (2277 lines). Three major sections:

| Section | Lines | Description |
|---------|-------|-------------|
| **CSS** | 10–510 (~500 lines) | All styles, CSS variables, responsive breakpoints |
| **HTML Body** | 512–1057 (~545 lines) | Header, gamification bar, calorie ring, tabs, modals |
| **JavaScript** | 1059–2275 (~1216 lines) | 47 functions for all interactivity |

### CSS Custom Properties (Theme)
```css
:root {
    --bg: #0d0f11;
    --surface: #161a1f;
    --surface2: #1c2127;
    --border: #2a3038;
    --text: #e8ecf0;
    --text-dim: #8892a0;
    --accent: #3ecf8e;
    --accent-dim: rgba(62, 207, 142, 0.15);
    --protein: #60a5fa;
    --carbs: #fbbf24;
    --fat: #f87171;
    --calories: #3ecf8e;
    --danger: #ef4444;
    --warning: #f59e0b;
    --radius: 12px;
    --shadow: 0 2px 12px rgba(0,0,0,0.3);
}
```

### Page Layout (top to bottom)

1. **Sticky Header** — Date navigation (`‹` prev, date picker, `›` next, "Today" button) + gear button (opens profile modal)
2. **Gamification Bar** — Streak pill, best streak pill, activity emoji chips
3. **Calorie Ring** — SVG progress ring showing calories eaten vs goal, with remaining count
4. **Tab Bar** — Overview | Charts | Health | Coaching (segmented control style)
5. **Tab Panels**:
   - **Overview**: Macros card → Daily Coaching panel → Food Log/Often Used card → Status card → Activities card
   - **Charts**: 2×2 grid of Calorie History, Macro Tracking, Weight Trend, Sport Activity
   - **Health**: 4 health cards (BP, Sugar, Oxygen, HR) + 2 charts (BP History, Sugar & Oxygen History)
   - **Coaching**: Week selector pills → Summary stat cards → Report text → Action items
6. **5 Modals**: Food entry, Weight entry, Activity entry, Health entry, Profile settings
7. **Toast**: Fixed bottom notification

### Tabs System

```javascript
function initTabs() {
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
            tab.classList.add('active');
            document.getElementById('tab-' + tab.dataset.tab).classList.add('active');

            if (tab.dataset.tab === 'charts') loadCharts(7, document.querySelector('.chart-range-btns .active'));
            if (tab.dataset.tab === 'health') loadHealth();
            if (tab.dataset.tab === 'coaching') loadCoachingTab();
        });
    });
}
```

### JavaScript State Variables
```javascript
const API = '';                    // Empty string = relative API calls
let currentDate = new Date().toISOString().split('T')[0];
let charts = {};                   // Chart.js instances by name
let pollInterval = null;
const POLL_INTERVAL_MS = 30000;    // 30-second auto-refresh
let coachingPanelOpen = false;     // Daily coaching panel expanded state
let coachingReports = [];          // Cached weekly reports
let coachingTabLoaded = false;     // Whether coaching tab has been loaded
```

### Polling System
```javascript
function startPolling() {
    stopPolling();
    pollInterval = setInterval(() => {
        const activeTab = document.querySelector('.tab.active');
        if (activeTab && activeTab.dataset.tab === 'overview') {
            loadOverview();
        }
    }, POLL_INTERVAL_MS);
}

function stopPolling() {
    if (pollInterval) { clearInterval(pollInterval); pollInterval = null; }
}
```
Polling stops when the browser tab is hidden (via `visibilitychange` event) and resumes when visible.

### Chart.js Configuration

```javascript
const chartDefaults = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
        x: { grid: { color: 'rgba(42,48,56,0.5)' }, ticks: { color: '#8892a0', font: { size: 11 } } },
        y: { grid: { color: 'rgba(42,48,56,0.5)' }, ticks: { color: '#8892a0', font: { size: 11 } } },
    },
    plugins: {
        legend: { labels: { color: '#8892a0', font: { size: 12 } } },
    },
};
```

### Charts (4 types)

1. **Calorie History** — Bar chart (intake) with line overlay (goal, dashed red)
2. **Macro Tracking** — Line chart with 6 datasets: Protein/Carbs/Fat actual (filled) + Protein/Carbs/Fat targets (dashed). Custom legend grid (not Chart.js built-in).
3. **Weight Trend** — Line chart, sorted chronologically, green line with filled area
4. **Sport Activity** — Stacked bar chart by activity type, auto-colored

### Key JavaScript Functions (47 total)

| Function | Lines | Purpose |
|----------|-------|---------|
| `DOMContentLoaded` | 1070–1083 | Init: set date, init tabs, load overview, load profile, start polling |
| `startPolling`/`stopPolling` | 1086–1098 | 30-second auto-refresh on overview tab |
| `openModal`/`closeModal` | 1110–1117 | Modal show/hide helpers |
| `submitFood` | 1127–1154 | POST /api/food from modal form |
| `submitWeight` | 1156–1177 | POST /api/weight from modal form |
| `quickLogWeight` | 1179–1199 | POST /api/weight from inline input in status card |
| `submitActivity` | 1201–1224 | POST /api/activity from modal form |
| `submitHealth` | 1226–1252 | POST /api/health from modal form |
| `loadGamification` | 1256–1300 | GET /api/gamification → update streak, best streak, activity chips |
| `changeDate`/`onDateChange`/`goToday` | 1303–1323 | Date navigation |
| `initTabs` | 1326–1340 | Tab switching with lazy loading |
| `loadOverview` | 1345–1415 | GET /api/daily-summary → update ring, macros, status labels, food log, activities |
| `updateMacroBar` | 1417–1422 | Update a single macro progress bar |
| `renderFoodLog` | 1424–1458 | Render food entries table from data |
| `renderActivities` | 1460–1481 | Render activity cards from data |
| `deleteFood` | 1483–1487 | DELETE /api/food/{id} |
| `duplicateFood` | 1489–1531 | Fetch entry, POST /api/food with same data + new timestamp |
| `showToast` | 1536–1541 | Show/hide toast notification |
| `switchFoodSubTab` | 1546–1552 | Toggle between Food Log and Often Used panels |
| `loadOftenUsed` | 1554–1576 | GET /api/food/often-used → render list |
| `addOftenUsed` | 1578–1591 | POST /api/food/often-used/{id}/add → quick-add to today |
| `loadCharts` | 1596–1622 | Fetch data and render all 4 charts |
| `renderCalorieChart` | 1653–1682 | Bar + line chart for calories |
| `renderMacroChart` | 1684–1759 | 6-dataset line chart for macros |
| `renderWeightChart` | 1761–1783 | Weight trend line chart |
| `renderActivityChart` | 1785–1857 | Stacked bar chart by activity type |
| `loadHealth` | 1862–1926 | GET /api/health → update cards + render charts |
| `renderBPChart` | 1928–1956 | Blood pressure line chart |
| `renderSugarOxyChart` | 1958–2004 | Blood sugar + oxygen dual-axis chart |
| `toggleCoachingPanel` | 2011–2015 | Expand/collapse daily coaching panel |
| `loadDailyCoaching` | 2017–2065 | GET /api/coaching/daily → render coaching panel |
| `loadCoachingTab` | 2073–2107 | GET /api/coaching/reports → render week pills + first report |
| `selectCoachingWeek` | 2109–2113 | Select a different week's report |
| `renderCoachingReport` | 2115–2175 | Render report summary cards, text, action items |
| `formatReportText` | 2177–2203 | Parse report text into HTML sections |
| `loadProfile` | 2208–2226 | GET /api/profile → populate form |
| `updateCalcTargets` | 2228–2243 | Client-side BMR/TDEE/goals preview |
| `saveProfile` | 2245–2274 | PUT /api/profile from modal form |

### Modals (5)

| Modal ID | Trigger | Submit Function | Fields |
|----------|---------|----------------|--------|
| `modal-food` | `+` button on food card | `submitFood()` | name, calories, meal_type, protein, carbs, fat, quantity, notes |
| `modal-weight` | `+` button on status card | `submitWeight()` | weight_kg, notes |
| `modal-activity` | `+` button on activities card | `submitActivity()` | activity_type, duration, calories_burned, intensity, notes |
| `modal-health` | `+` button on health tab | `submitHealth()` | systolic_bp, diastolic_bp, blood_sugar, blood_oxygen, heart_rate, notes |
| `modal-profile` | Gear button in header | `saveProfile()` | age, sex, height, weight, activity_level, goal_weight, deficit + calculated targets display |

---

## 10. GAMIFICATION SYSTEM

### Backend (database.py)

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

### Point System
| Achievement | Points |
|------------|--------|
| Protein target met (≥ goal) | +50 |
| Carbs under goal | +25 |
| Fat under goal | +25 |
| Perfect day bonus (all 3 macros met) | +50 |
| **Max daily points** | **150** |

### Streak Logic (app.py `get_gamification_status()`)

- **Current streak**: Iterates backwards from **yesterday** (not today), counting consecutive days where `calories ≤ calorie_goal`. Breaks on any day with zero food logged or calories over goal. Max lookback: 30 days.
- **Best streak**: Uses efficient GROUP BY queries over last 180 days to find the longest consecutive run of days under calorie goal.
- **Elite status**: True when today's data shows all macros met AND calories under goal.
- **Activities today**: List of activity type strings for the current day.

### Frontend — Activity Emoji Map

```javascript
const ACTIVITY_EMOJIS = {
    'running': '🏃', 'run': '🏃',
    'cycling': '🚴', 'bike': '🚴', 'biking': '🚴',
    'swimming': '🏊', 'swim': '🏊',
    'weight training': '🏋️', 'weights': '🏋️', 'lifting': '🏋️',
    'yoga': '🧘',
    'hiit': '🔥',
    'walking': '🚶', 'walk': '🚶',
    'hiking': '🥾',
    'dancing': '💃', 'dance': '💃',
    'rowing': '🚣',
    'basketball': '🏀', 'soccer': '⚽', 'football': '🏈', 'tennis': '🎾',
};
```

Activities are displayed as colored chips in the gamification bar: `emoji + activity_type` (e.g., "🏃 Running"). Fallback emoji is 💪 for unknown activities.

### Frontend — Gamification Bar HTML
```html
<div class="gamification-bar">
    <div class="gamification-streak">
        <span class="gami-pill">
            <span id="streak-icon">🔥</span>
            <span><span id="streak-days">0</span> streak</span>
        </span>
        <span class="gami-dot">·</span>
        <span class="gami-pill gami-pill-dim">
            <span>🏆</span>
            <span><span id="best-streak">0</span> best</span>
        </span>
    </div>
    <div class="gamification-activities" id="activity-emojis"></div>
</div>
```

When elite status is active, the streak icon changes from 🔥 to 💠.

### Frontend — Macro Status Labels

Calculated client-side in `loadOverview()` from daily-summary data (not from gamification endpoint):
- **Protein**: `good` (green) if intake ≥ goal, else `low` (red)
- **Carbs**: `good` (green) if intake ≤ goal, else `over` (red)
- **Fat**: `good` (green) if intake ≤ goal, else `over` (red)

---

## 11. DEPLOYMENT CONFIGURATION

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NUTRITRACK_DB_PATH` | `nutritrack.db` (in project root) | Path to SQLite database file |
| `NUTRITRACK_HOST` | `0.0.0.0` | Server bind address |
| `NUTRITRACK_PORT` | `8000` | Server port |
| `NUTRITRACK_CORS_ORIGINS` | `*` | CORS allowed origins (comma-separated or `*` for all) |
| `SEED_DEMO_DATA` | `false` | Auto-seed demo data on first startup when DB is empty |
| `TZ` | `UTC` | Timezone for Docker container |

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/profile || exit 1

CMD ["python", "app.py"]
```

### docker-compose.yml
```yaml
version: "3.8"
services:
  nutritrack:
    build: .
    container_name: nutritrack
    ports:
      - "${NUTRITRACK_PORT:-8000}:8000"
    volumes:
      - nutritrack_data:/app/data
    environment:
      - NUTRITRACK_DB_PATH=/app/data/nutritrack.db
      - NUTRITRACK_HOST=0.0.0.0
      - NUTRITRACK_PORT=8000
      - TZ=${TZ:-UTC}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/profile"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s

volumes:
  nutritrack_data:
```

### docker-compose.dev.yml
```yaml
version: "3.8"
services:
  nutritrack:
    build: .
    container_name: nutritrack-dev
    ports:
      - "${NUTRITRACK_PORT:-8000}:8000"
    volumes:
      - .:/app
    environment:
      - NUTRITRACK_DB_PATH=/app/data/nutritrack.db
      - NUTRITRACK_HOST=0.0.0.0
      - NUTRITRACK_PORT=8000
    command: ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

### deploy.sh (366 lines)

One-command deploy script that:
1. Auto-detects Docker vs Python
2. Supports `start`, `stop`, `status`, `update` commands
3. Creates `data/` directory for DB persistence
4. Uses colored output with status icons
5. Runs health checks after startup
6. Handles port configuration via `NUTRITRACK_PORT` env var

### Shell Scripts

| Script | Purpose |
|--------|---------|
| `deploy.sh` | Primary deploy (auto Docker/Python, start/stop/status/update) |
| `install.sh` | Interactive installer (checks Python 3.10+, creates venv, installs deps, optional seed) |
| `start.sh` | Start server using venv Python |
| `stop.sh` | Stop server via `pkill -f "python.*app.py"` |
| `dev.sh` | Development mode with `uvicorn --reload` |
| `setup.sh` | Simple setup (no venv, global pip install, start) |
| `scripts/install.sh` | 4-line wrapper for OpenClaw skill install |

---

## 12. CORS & MIDDLEWARE

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

Default allows all origins (`*`). Can be restricted via `NUTRITRACK_CORS_ORIGINS` env var.

### Static Files
```python
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
```

### Dashboard Serving
```python
@app.get("/")
def serve_dashboard():
    with open(os.path.join(STATIC_DIR, "dashboard.html"), "r") as f:
        html = f.read()
    return HTMLResponse(content=html, headers={"Cache-Control": "no-cache, no-store, must-revalidate"})
```
Dashboard is served with no-cache headers to ensure latest version is always loaded.

---

## 13. KEY CODE SECTIONS — VERBATIM

### app.py — Profile Endpoints

```python
@app.get("/api/profile")
def get_profile():
    conn = get_db()
    row = conn.execute("SELECT * FROM user_profile ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    if not row:
        return {"profile": None, "message": "No profile set. Please create your profile first."}
    return {"profile": row_to_dict(row)}

@app.put("/api/profile")
def update_profile(profile: ProfileCreate):
    conn = get_db()
    existing = conn.execute("SELECT id FROM user_profile LIMIT 1").fetchone()

    if existing:
        conn.execute("""
            UPDATE user_profile
            SET age=?, sex=?, height_cm=?, current_weight_kg=?, activity_level=?, weight_goal_kg=?, calorie_deficit=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        """, (profile.age, profile.sex, profile.height_cm, profile.current_weight_kg, profile.activity_level, profile.weight_goal_kg, profile.calorie_deficit, existing["id"]))
    else:
        conn.execute("""
            INSERT INTO user_profile (age, sex, height_cm, current_weight_kg, activity_level, weight_goal_kg, calorie_deficit)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (profile.age, profile.sex, profile.height_cm, profile.current_weight_kg, profile.activity_level, profile.weight_goal_kg, profile.calorie_deficit))

        # Also log initial weight
        conn.execute("""
            INSERT INTO weight_logs (weight_kg, notes, measured_at)
            VALUES (?, 'Profile update', CURRENT_TIMESTAMP)
        """, (profile.current_weight_kg,))

    conn.commit()
    row = conn.execute("SELECT * FROM user_profile ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    return {"profile": row_to_dict(row), "message": "Profile updated successfully."}
```

### app.py — Food Log with Coaching Tips

```python
@app.post("/api/food")
def log_food(entry: FoodEntry):
    conn = get_db()
    logged_at = entry.logged_at or datetime.now().isoformat()

    conn.execute("""
        INSERT INTO food_entries (name, calories, protein_g, carbs_g, fat_g, meal_type, quantity, notes, logged_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (entry.name, entry.calories, entry.protein_g, entry.carbs_g, entry.fat_g, entry.meal_type, entry.quantity, entry.notes, logged_at))
    conn.commit()

    last_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    row = conn.execute("SELECT * FROM food_entries WHERE id=?", (last_id,)).fetchone()

    # Generate coaching tips based on updated daily totals
    tips = []
    profile_row = conn.execute("SELECT * FROM user_profile ORDER BY id DESC LIMIT 1").fetchone()
    if profile_row:
        profile = row_to_dict(profile_row)
        entry_date = logged_at[:10]
        start, end = get_date_range(entry_date)
        totals = conn.execute(
            "SELECT COALESCE(SUM(calories),0) as cal, COALESCE(SUM(protein_g),0) as prot, "
            "COALESCE(SUM(carbs_g),0) as carb, COALESCE(SUM(fat_g),0) as fat "
            "FROM food_entries WHERE logged_at BETWEEN ? AND ?", (start, end)
        ).fetchone()
        act = conn.execute(
            "SELECT COALESCE(SUM(calories_burned),0) as burned "
            "FROM sport_activities WHERE performed_at BETWEEN ? AND ?", (start, end)
        ).fetchone()
        goals = calculate_daily_goals(profile, act["burned"])
        intake = {"calories": totals["cal"], "protein_g": totals["prot"], "carbs_g": totals["carb"], "fat_g": totals["fat"]}
        tips = generate_coaching_tips(profile, intake, goals)

    conn.close()
    return {"entry": row_to_dict(row), "message": f"Logged: {entry.name} ({entry.calories} kcal)", "coaching_tips": tips}
```

### app.py — Weight Log (updates profile)

```python
@app.post("/api/weight")
def log_weight(entry: WeightEntry):
    conn = get_db()
    measured_at = entry.measured_at or datetime.now().isoformat()

    conn.execute(
        "INSERT INTO weight_logs (weight_kg, notes, measured_at) VALUES (?, ?, ?)",
        (entry.weight_kg, entry.notes, measured_at)
    )
    # Also update profile's current weight
    conn.execute(
        "UPDATE user_profile SET current_weight_kg=?, updated_at=CURRENT_TIMESTAMP", (entry.weight_kg,)
    )
    conn.commit()

    last_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    row = conn.execute("SELECT * FROM weight_logs WHERE id=?", (last_id,)).fetchone()
    conn.close()
    return {"entry": row_to_dict(row), "message": f"Weight logged: {entry.weight_kg} kg"}
```

### app.py — Daily Summary

```python
@app.get("/api/daily-summary")
def get_daily_summary(date: Optional[str] = None):
    target_date = date or datetime.now().date().isoformat()
    start, end = get_date_range(target_date)

    conn = get_db()

    profile_row = conn.execute("SELECT * FROM user_profile ORDER BY id DESC LIMIT 1").fetchone()
    if not profile_row:
        conn.close()
        return {"error": "No profile set. Create your profile first."}
    profile = row_to_dict(profile_row)

    food_rows = conn.execute(
        "SELECT * FROM food_entries WHERE logged_at BETWEEN ? AND ? ORDER BY logged_at", (start, end)
    ).fetchall()
    food = rows_to_list(food_rows)

    activity_rows = conn.execute(
        "SELECT * FROM sport_activities WHERE performed_at BETWEEN ? AND ? ORDER BY performed_at", (start, end)
    ).fetchall()
    activities = rows_to_list(activity_rows)

    weight_row = conn.execute(
        "SELECT * FROM weight_logs ORDER BY measured_at DESC LIMIT 1"
    ).fetchone()

    conn.close()

    total_calories = sum(f["calories"] for f in food)
    total_protein = sum(f["protein_g"] for f in food)
    total_carbs = sum(f["carbs_g"] for f in food)
    total_fat = sum(f["fat_g"] for f in food)

    activity_calories = sum(a["calories_burned"] for a in activities)

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

### app.py — Gamification Endpoint

```python
@app.get("/api/gamification")
def get_gamification_status():
    """Calculate current streak, elite status, and daily points."""
    conn = get_db()

    profile_row = conn.execute("SELECT * FROM user_profile ORDER BY id DESC LIMIT 1").fetchone()
    if not profile_row:
        conn.close()
        return {"error": "No profile set"}
    profile = row_to_dict(profile_row)

    streak_count = 0
    elite_streak = False

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

    today_activity_rows = conn.execute(
        "SELECT activity_type FROM sport_activities WHERE performed_at BETWEEN ? AND ? ORDER BY performed_at",
        (start, end)
    ).fetchall()
    activities_today = [r["activity_type"] for r in today_activity_rows]

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

    # Calculate best streak over last 180 days using efficient GROUP BY
    lookback_start = datetime.combine(today - timedelta(days=180), datetime.min.time()).isoformat()
    lookback_end = datetime.combine(today, datetime.max.time()).isoformat()

    daily_cals = conn.execute("""
        SELECT DATE(logged_at) as day, COALESCE(SUM(calories),0) as cal
        FROM food_entries
        WHERE logged_at BETWEEN ? AND ?
        GROUP BY DATE(logged_at)
        ORDER BY day
    """, (lookback_start, lookback_end)).fetchall()

    daily_burned = conn.execute("""
        SELECT DATE(performed_at) as day, COALESCE(SUM(calories_burned),0) as burned
        FROM sport_activities
        WHERE performed_at BETWEEN ? AND ?
        GROUP BY DATE(performed_at)
    """, (lookback_start, lookback_end)).fetchall()

    conn.close()

    burned_map = {r["day"]: r["burned"] for r in daily_burned}

    best_streak = 0
    current_run = 0
    for row in daily_cals:
        day_burned = burned_map.get(row["day"], 0)
        day_goals = calculate_daily_goals(profile, day_burned)
        if row["cal"] <= day_goals["calorie_goal"]:
            current_run += 1
            if current_run > best_streak:
                best_streak = current_run
        else:
            current_run = 0

    return {
        "streak_days": streak_count,
        "best_streak": best_streak,
        "today_points": today_gamification["points"],
        "is_elite": today_gamification["is_elite"],
        "calorie_success": today_gamification["calorie_success"],
        "tags": today_gamification["tags"],
        "activities_today": activities_today,
    }
```

### app.py — Weekly Report

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

    profile_row = conn.execute("SELECT * FROM user_profile ORDER BY id DESC LIMIT 1").fetchone()
    profile = row_to_dict(profile_row) if profile_row else None

    food_rows = conn.execute(
        "SELECT * FROM food_entries WHERE logged_at BETWEEN ? AND ? ORDER BY logged_at", (s, e)
    ).fetchall()
    food = rows_to_list(food_rows)

    activity_rows = conn.execute(
        "SELECT * FROM sport_activities WHERE performed_at BETWEEN ? AND ? ORDER BY performed_at", (s, e)
    ).fetchall()
    activities = rows_to_list(activity_rows)

    weight_rows = conn.execute(
        "SELECT * FROM weight_logs WHERE measured_at BETWEEN ? AND ? ORDER BY measured_at", (s, e)
    ).fetchall()
    weights = rows_to_list(weight_rows)

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

    goals = None
    if profile:
        activity_cal = sum(a["calories_burned"] for a in activities) / 7
        goals = calculate_daily_goals(profile, activity_cal)

    days_over = 0
    days_under = 0
    if goals:
        for day_data in daily_nutrition.values():
            if day_data["calories"] > goals["calorie_goal"]:
                days_over += 1
            else:
                days_under += 1

    weight_start = weights[0]["weight_kg"] if weights else None
    weight_end = weights[-1]["weight_kg"] if weights else None
    weight_change = round(weight_end - weight_start, 2) if weight_start and weight_end else None

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

### app.py — Daily Totals for Charts

```python
@app.get("/api/history/daily-totals")
def get_daily_totals(days: int = 30):
    """Get daily calorie/macro totals for the last N days (for charts)."""
    end_d = datetime.now().date()
    start_d = end_d - timedelta(days=days - 1)

    start_iso = datetime.combine(start_d, datetime.min.time()).isoformat()
    end_iso = datetime.combine(end_d, datetime.max.time()).isoformat()

    conn = get_db()

    profile_row = conn.execute("SELECT * FROM user_profile ORDER BY id DESC LIMIT 1").fetchone()
    profile = row_to_dict(profile_row) if profile_row else None

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

    activity_rows = conn.execute("""
        SELECT DATE(performed_at) as day,
               COALESCE(SUM(calories_burned), 0) as burned
        FROM sport_activities
        WHERE performed_at BETWEEN ? AND ?
        GROUP BY DATE(performed_at)
    """, (start_iso, end_iso)).fetchall()

    conn.close()

    food_by_day = {r["day"]: r for r in food_rows}
    activity_by_day = {r["day"]: r for r in activity_rows}

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

### app.py — Coaching Endpoints (Agent-Written)

```python
@app.put("/api/coaching/daily")
def update_daily_coaching(coaching: DailyCoaching):
    conn = get_db()
    cursor = conn.cursor()

    existing = cursor.execute(
        "SELECT id FROM daily_coaching WHERE coaching_date = ?", (coaching.coaching_date,)
    ).fetchone()

    if existing:
        cursor.execute(
            """UPDATE daily_coaching SET coaching_text = ?, meal_count = ?, calories_so_far = ?,
               calories_remaining = ?, protein_status = ?, top_priority = ?, updated_at = CURRENT_TIMESTAMP
               WHERE coaching_date = ?""",
            (coaching.coaching_text, coaching.meal_count, coaching.calories_so_far,
             coaching.calories_remaining, coaching.protein_status, coaching.top_priority,
             coaching.coaching_date)
        )
    else:
        cursor.execute(
            """INSERT INTO daily_coaching (coaching_date, coaching_text, meal_count, calories_so_far,
               calories_remaining, protein_status, top_priority) VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (coaching.coaching_date, coaching.coaching_text, coaching.meal_count,
             coaching.calories_so_far, coaching.calories_remaining, coaching.protein_status,
             coaching.top_priority)
        )

    conn.commit()
    row = cursor.execute(
        "SELECT * FROM daily_coaching WHERE coaching_date = ?", (coaching.coaching_date,)
    ).fetchone()
    conn.close()

    return {"coaching": row_to_dict(row), "message": f"Daily coaching updated for {coaching.coaching_date}"}

@app.post("/api/coaching/report")
def create_coaching_report(report: CoachingReport):
    conn = get_db()
    cursor = conn.cursor()
    existing = cursor.execute(
        "SELECT id FROM coaching_reports WHERE week_start = ? AND week_end = ?",
        (report.week_start, report.week_end)
    ).fetchone()
    if existing:
        cursor.execute(
            "UPDATE coaching_reports SET report_text = ?, summary_json = ?, created_at = CURRENT_TIMESTAMP WHERE id = ?",
            (report.report_text, report.summary_json, existing["id"])
        )
    else:
        cursor.execute(
            "INSERT INTO coaching_reports (week_start, week_end, report_text, summary_json) VALUES (?, ?, ?, ?)",
            (report.week_start, report.week_end, report.report_text, report.summary_json)
        )
    conn.commit()
    entry_id = existing["id"] if existing else cursor.lastrowid
    row = cursor.execute("SELECT * FROM coaching_reports WHERE id = ?", (entry_id,)).fetchone()
    conn.close()
    return {"report": row_to_dict(row), "message": f"Coaching report saved for {report.week_start} to {report.week_end}"}
```

### app.py — CSV Export

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

### app.py — Demo Data Seeder

```python
@app.post("/api/seed-demo-data")
def seed_demo_data():
    """Populate the database with 30 days of realistic demo data."""
    conn = get_db()

    # Clear existing data
    for table in ["food_entries", "weight_logs", "sport_activities", "health_measurements", "often_used_foods", "daily_coaching", "coaching_reports", "user_profile"]:
        conn.execute(f"DELETE FROM {table}")
    conn.commit()

    # Profile
    conn.execute("""
        INSERT INTO user_profile (age, sex, height_cm, current_weight_kg, activity_level, weight_goal_kg, calorie_deficit)
        VALUES (30, 'male', 180, 85.0, 'moderate', 78.0, 500)
    """)

    today_d = datetime.now().date()
    random.seed(42)

    # ... (30 days of food, weight, activity, health data generation)
    # See full function in app.py lines 1141-1263

    return {"message": "Demo data seeded: 30 days of food, weight, activity, and health data."}
```

### dashboard.html — Key Frontend Functions

**loadOverview (with macro status logic):**
```javascript
async function loadOverview() {
    try {
        loadGamification();
        loadDailyCoaching();
        const res = await fetch(`${API}/api/daily-summary?date=${currentDate}`);
        const data = await res.json();

        if (data.error) { console.warn(data.error); return; }

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

        // Macro status labels (calculated from daily-summary, not gamification)
        const proteinEl = document.getElementById('status-protein');
        if (intake.protein_g >= goals.protein_goal_g) {
            proteinEl.textContent = 'good'; proteinEl.style.color = '#3ecf8e';
        } else {
            proteinEl.textContent = 'low'; proteinEl.style.color = '#f87171';
        }

        const carbsEl = document.getElementById('status-carbs');
        if (intake.carbs_g <= goals.carbs_goal_g) {
            carbsEl.textContent = 'good'; carbsEl.style.color = '#3ecf8e';
        } else {
            carbsEl.textContent = 'over'; carbsEl.style.color = '#f87171';
        }

        const fatEl = document.getElementById('status-fat');
        if (intake.fat_g <= goals.fat_goal_g) {
            fatEl.textContent = 'good'; fatEl.style.color = '#3ecf8e';
        } else {
            fatEl.textContent = 'over'; fatEl.style.color = '#f87171';
        }

        // Quick stats
        document.getElementById('currentWeight').textContent = latest_weight ? latest_weight.weight_kg : '—';
        document.getElementById('goalWeight').textContent = profile?.weight_goal_kg || '—';
        document.getElementById('deficitTarget').textContent = profile?.calorie_deficit || 500;

        const burned = activities.reduce((sum, a) => sum + a.calories_burned, 0);
        document.getElementById('activityBurned').textContent = Math.round(burned);

        renderFoodLog(food_entries);
        renderActivities(activities);

    } catch (err) {
        console.error('Failed to load overview:', err);
    }
}
```

**loadGamification (with ACTIVITY_EMOJIS):**
```javascript
async function loadGamification() {
    try {
        const res = await fetch(`${API}/api/gamification`);
        const data = await res.json();
        if (data.error) return;

        document.getElementById('streak-days').textContent = data.streak_days;
        document.getElementById('streak-icon').textContent = data.is_elite ? '💠' : '🔥';
        document.getElementById('best-streak').textContent = data.best_streak || 0;

        const ACTIVITY_EMOJIS = {
            'running': '🏃', 'run': '🏃',
            'cycling': '🚴', 'bike': '🚴', 'biking': '🚴',
            'swimming': '🏊', 'swim': '🏊',
            'weight training': '🏋️', 'weights': '🏋️', 'lifting': '🏋️',
            'yoga': '🧘', 'hiit': '🔥',
            'walking': '🚶', 'walk': '🚶', 'hiking': '🥾',
            'dancing': '💃', 'dance': '💃', 'rowing': '🚣',
            'basketball': '🏀', 'soccer': '⚽', 'football': '🏈', 'tennis': '🎾',
        };
        const actContainer = document.getElementById('activity-emojis');
        actContainer.innerHTML = '';
        const acts = data.activities_today || [];
        if (acts.length > 0) {
            acts.forEach(a => {
                const key = a.toLowerCase();
                const emoji = ACTIVITY_EMOJIS[key] || '💪';
                const chip = document.createElement('span');
                chip.className = 'activity-chip';
                chip.textContent = `${emoji} ${a}`;
                actContainer.appendChild(chip);
            });
        }
    } catch (err) {
        console.error('Gamification load error:', err);
    }
}
```

**loadDailyCoaching:**
```javascript
async function loadDailyCoaching() {
    try {
        const res = await fetch(`${API}/api/coaching/daily?date=${currentDate}`);
        const data = await res.json();
        const panel = document.getElementById('dailyCoachingPanel');

        if (!data.coaching) { panel.style.display = 'none'; return; }

        panel.style.display = 'block';
        const c = data.coaching;

        document.getElementById('coachingPriority').textContent = c.top_priority || 'Check your coaching tip';

        const badge = document.getElementById('coachingProteinBadge');
        const statusMap = {
            'on_track': { text: 'protein ✓', cls: 'on-track' },
            'low': { text: 'protein low', cls: 'low' },
            'critical': { text: 'protein ⚠', cls: 'critical' },
            'exceeded': { text: 'protein ++', cls: 'exceeded' },
            'unknown': { text: '', cls: '' }
        };
        const st = statusMap[c.protein_status] || statusMap['unknown'];
        badge.textContent = st.text;
        badge.className = 'coaching-protein-badge ' + st.cls;

        const textHtml = c.coaching_text.split('\n').filter(l => l.trim()).map(l => '<p>' + l + '</p>').join('');
        document.getElementById('coachingFullText').innerHTML = textHtml;

        const meta = [];
        if (c.meal_count) meta.push('After meal ' + c.meal_count);
        if (c.calories_so_far) meta.push(Math.round(c.calories_so_far) + ' kcal so far');
        if (c.calories_remaining > 0) meta.push(Math.round(c.calories_remaining) + ' remaining');
        document.getElementById('coachingMeta').textContent = meta.join(' · ');

        document.getElementById('coachingExpanded').style.display = coachingPanelOpen ? 'block' : 'none';
        document.getElementById('coachingChevron').classList.toggle('open', coachingPanelOpen);

    } catch (err) {
        console.error('Daily coaching load error:', err);
    }
}
```

**renderCoachingReport (with grade colors):**
```javascript
function renderCoachingReport(report) {
    const summaryDiv = document.getElementById('coachingSummaryCards');
    const actionsDiv = document.getElementById('coachingActionsCard');
    let summary = null;
    try { if (report.summary_json) summary = JSON.parse(report.summary_json); } catch (e) {}

    if (summary) {
        summaryDiv.style.display = 'flex';
        let cards = '';
        if (summary.grade) {
            const gradeColor = {'A+':'#3ecf8e','A':'#3ecf8e','B+':'#60a5fa','B':'#60a5fa',
                'C+':'#fbbf24','C':'#fbbf24','D':'#f87171','F':'#ef4444'}[summary.grade] || 'var(--text)';
            cards += '<div class="coaching-stat-card"><div class="label">Grade</div><div class="coaching-grade" style="color:' + gradeColor + '">' + summary.grade + '</div></div>';
        }
        if (summary.avg_calories != null) {
            const calColor = summary.calorie_goal && summary.avg_calories <= summary.calorie_goal ? '#3ecf8e' : '#f87171';
            cards += '<div class="coaching-stat-card"><div class="label">Avg Calories</div><div class="value" style="color:' + calColor + '">' + Math.round(summary.avg_calories) + '</div>' + (summary.calorie_goal ? '<div class="label">goal ' + Math.round(summary.calorie_goal) + '</div>' : '') + '</div>';
        }
        if (summary.weight_change != null) {
            const wColor = summary.weight_change < 0 ? '#3ecf8e' : summary.weight_change > 0 ? '#f87171' : 'var(--text-dim)';
            const wArrow = summary.weight_change < 0 ? '↓' : summary.weight_change > 0 ? '↑' : '—';
            cards += '<div class="coaching-stat-card"><div class="label">Weight</div><div class="value" style="color:' + wColor + '">' + wArrow + ' ' + Math.abs(summary.weight_change).toFixed(1) + ' kg</div></div>';
        }
        if (summary.days_on_track != null) {
            const dtColor = summary.days_on_track >= 5 ? '#3ecf8e' : summary.days_on_track >= 3 ? '#fbbf24' : '#f87171';
            cards += '<div class="coaching-stat-card"><div class="label">Days on Track</div><div class="value" style="color:' + dtColor + '">' + summary.days_on_track + '/' + (summary.days_total || 7) + '</div></div>';
        }
        summaryDiv.innerHTML = cards;

        if (summary.action_items && summary.action_items.length > 0) {
            actionsDiv.style.display = 'block';
            actionsDiv.innerHTML = '<div class="coaching-actions-card"><div class="action-title">📋 Action Items for Next Week</div>' +
                summary.action_items.map(item => '<div class="action-item">' + item + '</div>').join('') + '</div>';
        } else { actionsDiv.style.display = 'none'; }
    } else {
        summaryDiv.style.display = 'none';
        actionsDiv.style.display = 'none';
    }

    const reportCard = document.getElementById('coachingReportCard');
    const reportBody = document.getElementById('coachingReportBody');
    if (report.report_text) {
        reportCard.style.display = 'block';
        reportBody.innerHTML = formatReportText(report.report_text);
    } else { reportCard.style.display = 'none'; }
}
```

**formatReportText:**
```javascript
function formatReportText(text) {
    if (!text) return '';
    const lines = text.split('\n');
    let html = '';
    const headerPatterns = [
        'WEEKLY HEALTH REPORT', 'THE NUMBERS', 'WEIGHT CHECK', 'WINS THIS WEEK',
        'WATCH OUT', 'FOOD SPOTLIGHT', 'ACTIVITY SUMMARY', 'ACTION ITEMS',
        'STREAK AND GAMIFICATION', 'STREAK &'
    ];

    for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed) continue;

        const isHeader = headerPatterns.some(p => trimmed.toUpperCase().startsWith(p)) ||
                         (trimmed.length >= 4 && trimmed === trimmed.toUpperCase() && /[A-Z]/.test(trimmed));

        if (isHeader) {
            html += '<div class="section-header">' + trimmed + '</div>';
        } else if (trimmed.startsWith('- ')) {
            html += '<div class="bullet-item">' + trimmed.slice(2) + '</div>';
        } else {
            html += '<p>' + trimmed + '</p>';
        }
    }
    return html;
}
```

---

## 14. AGENT INTEGRATION

NutriTrack provides three agent documentation files:

### SKILL.md (449 lines) — The Primary Agent Skill File

Location: `SKILL.md` in project root. This is the **single file** an AI agent needs to operate NutriTrack. Contains:

**Frontmatter:**
```yaml
name: nutritrack
description: Log food, weight, exercise, and health vitals to your self-hosted NutriTrack nutrition tracker.
homepage: https://github.com/BenZenTuna/Nutritrack
metadata: { "openclaw": { "emoji": "🥗", "category": "health", "requires": { "bins": ["curl"] } } }
```

**Sections:**
1. **Connection** — Base URL from `NUTRITRACK_URL` env var (default `http://localhost:8000`), health check command
2. **Installation** — `git clone` + `./deploy.sh`, management commands
3. **First-Time Setup** — Profile creation via PUT /api/profile
4. **Core Workflow — Food Logging** — How to estimate macros, log food, handle coaching tips response
5. **Food Reference Table** — Common foods with calories, protein, carbs, fat per serving
6. **Weight Tracking** — POST /api/weight (also updates profile)
7. **Exercise Logging** — POST /api/activity with MET-based calorie calculation
8. **Exercise MET Reference** — MET values for 12 common activities
9. **Calorie Burn Formula** — `Calories = MET × weight_kg × (duration_min / 60)`
10. **Health Vitals** — POST /api/health for BP, blood sugar, SpO2, heart rate
11. **Querying Data** — GET endpoints for daily summary, weekly report, food search
12. **Often-Used Foods Curation** — Agent workflow for curating the often-used list
13. **Daily Post-Meal Coaching** — Agent writes coaching tips after every meal
14. **Weekly Coaching Reports** — Agent writes weekly health reports with grade + summary_json
15. **Grading Scale** — A+ through F definitions
16. **Gamification** — Rules for streaks, points, elite status
17. **Troubleshooting** — Common issues and solutions

### docs/AGENT_README.md (1328 lines) — Comprehensive Agent Guide

The most detailed agent documentation. Includes complete curl examples for every API endpoint, detailed food logging guidelines with extensive nutrition reference tables, exercise MET values, health measurement interpretation ranges, report reading guide, and error handling.

**Key Sections:**
- Server configuration and first-time setup
- Complete API reference with curl examples for ALL endpoints
- Food logging guidelines with 50+ food items reference table
- Exercise MET values table (12 activities × 3 intensities)
- Health measurement normal/warning/danger ranges
- Coaching tip format specification
- Weekly report writing instructions
- Error handling and recovery patterns

### docs/AGENT_DEPLOY.md (116 lines) — Deployment Guide

```markdown
# NutriTrack — Agent Deployment Guide

One-command deploy for AI agents. No prompts, no decisions, no sudo.

## Deploy
git clone https://github.com/BenZenTuna/Nutritrack.git
cd Nutritrack
chmod +x deploy.sh
./deploy.sh

## Management
./deploy.sh          # Start or restart
./deploy.sh stop     # Stop the server
./deploy.sh status   # Check if running
./deploy.sh update   # git pull + restart

## Verify
curl -s http://localhost:8000/api/profile

## Environment Variables
| Variable | Default | Description |
| NUTRITRACK_PORT | 8000 | Server port |
| NUTRITRACK_HOST | 0.0.0.0 | Bind address |

## Data Safety
- ./data/nutritrack.db persists across restarts and updates
- data/ is gitignored
- Docker uses named volume nutritrack_data

## Optional: systemd User Service (no sudo)
- Creates ~/.config/systemd/user/nutritrack.service
- Requires loginctl enable-linger

## Troubleshooting
- Port in use → change NUTRITRACK_PORT
- python3 not found → apt install python3 python3-venv python3-pip
- venv fails → apt install python3-venv
- Permission denied → chmod +x deploy.sh
- Docker no daemon → start docker or fallback to Python
- Health check fails → check nutritrack.log or docker compose logs
- DB locked → stop duplicates: ./deploy.sh stop && ./deploy.sh
```

---

## 15. CURRENT STATE & KNOWN ISSUES

### Working Features (all verified)
- Profile CRUD with Mifflin-St Jeor calorie calculation
- Food logging with 4 meal types, coaching tips in response
- Weight logging with automatic profile weight update
- Activity logging with calorie burn tracking
- Health vitals logging (BP, blood sugar, SpO2, heart rate)
- Daily summary with goals, intake, remaining
- Weekly report aggregation with daily breakdown
- Gamification with streaks, best streak, elite status, activity emoji chips
- Often-used foods (agent-curated) with quick-add
- Daily coaching panel (collapsible, with protein badge)
- Weekly coaching reports with summary cards and formatted text
- 4 chart types (calorie, macro, weight, activity)
- 4 health cards with status indicators + 2 health charts
- CSV export for all data types
- Demo data seeder (30 days)
- Docker and bare-metal deployment
- 30-second auto-refresh polling
- Responsive mobile layout

### Known Issues / Quirks
- `often_used_foods` table is DROPped and recreated on every `init_db()` call (intentional — agent-curated list is disposable)
- `weekly-report` endpoint has a redundant `date_obj` variable assignment: `end_d = date_obj = __import__('datetime').date.fromisoformat(end_date)`
- No authentication — single-user, local-first design
- No input sanitization on food names displayed in HTML (potential XSS if malicious data entered via API)
- Food search uses `LIKE %q%` — no full-text search index
- Gamification streak calculation iterates day-by-day (could be slow with very large datasets)
- No pagination on food log display (all entries for a day shown at once)
- `duplicateFood()` re-fetches all food entries to find the one to duplicate (no single-item GET endpoint)

### No TODO/FIXME/HACK Comments
Grep across all source files found zero TODO, FIXME, HACK, or XXX comments.

---

## 16. GIT STATUS

### Remote
```
origin  https://github.com/BenZenTuna/Nutritrack.git (fetch)
origin  https://github.com/BenZenTuna/Nutritrack.git (push)
```

### Branch
`main` (only branch)

### Recent Commits (latest 25)
| Hash | Description |
|------|-------------|
| `8947080` | style: refine coaching dashboard with animations, grade colors, and UX fixes |
| `0f6d6da` | feat: add AI coaching system with daily tips and weekly reports |
| `0b350b6` | docs: update PROJECT_SNAPSHOT.md with agent-curated often-used, gamification pills, and segmented tabs |
| `f239587` | style: redesign food log sub-tabs as segmented control |
| `430c699` | style: redesign gamification bar with pill layout and responsive wrap |
| `4aaace4` | feat: replace auto-generated often-used list with agent-curated system |
| `da3ff16` | docs: regenerate PROJECT_SNAPSHOT.md with full codebase analysis |
| `949f6c5` | feat: add Often Used foods tab with quick-add and toast notifications |
| `596f7e4` | feat: add post-meal coaching tips and coaching endpoint |
| `5161944` | feat: replace XP points with activity emoji chips in gamification bar |
| `d1a9659` | feat: show best streak record alongside current streak |
| `0810e42` | feat: add quick weight entry input in status panel |
| `e71d666` | ui: replace macro chart built-in legend with custom 3-column grid |
| `92df6e0` | ui: move activity panel below status panel in overview tab |
| `934006c` | fix: calculate macro status labels from daily-summary instead of gamification |
| `243bb51` | fix: correct broken SKILL.md and install script URLs in README |
| `2142cdf` | Remove instructions for other AI agents |
| `2a273bb` | style: remove Seed Demo Data button from profile section |
| `5e9683d` | docs: make AI agent install the primary option in README |
| `851fbec` | feat: add one-command deploy system and AI agent setup guide |
| `c91a9c2` | refactor: consolidate skill files into SKILL.md per OpenClaw convention |
| `59e6d9c` | feat: add compact SKILL.md for OpenClaw agent discovery |
| `f1312a4` | docs: clarify agent skill file (nutritrack.md) in README |
| `57982f6` | style: move calorie ring below gamification bar and enlarge gamification 2x |
| `917741e` | style: move activities panel below food log in overview tab |

### Working Tree
```
(clean)
```

---

## 17. DEPENDENCIES & VERSIONS

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

## 18. DESIGN DECISIONS & ARCHITECTURE NOTES

1. **Single-file frontend**: All CSS, HTML, and JS are in one `dashboard.html` file. No build step, no bundler, no npm. This keeps deployment trivial and avoids the complexity of a frontend build pipeline.

2. **No frontend framework**: Vanilla JavaScript with direct DOM manipulation. Avoids framework churn, keeps the codebase simple, and eliminates bundle size concerns.

3. **SQLite with WAL mode**: Write-Ahead Logging allows concurrent reads while a write is in progress. Perfect for a single-user app where the dashboard polls while the agent writes.

4. **No foreign keys between tables**: Each table is independent and queryable on its own. This simplifies the schema and avoids cascade deletion issues.

5. **Agent-first design**: The dashboard is read-only visualization. All data entry comes through the REST API, which is designed to be called by AI agents, not humans.

6. **Upsert patterns**: Profile (PUT) and daily coaching (PUT) both use upsert — check if exists, update or insert. Weekly reports are keyed by `(week_start, week_end)` for the same pattern.

7. **Weight logging updates profile**: When weight is logged via POST /api/weight, the profile's `current_weight_kg` is also updated. This keeps goals recalculated with the latest weight.

8. **Exercise calories feed back into goals**: Activity calories are added to TDEE before applying the deficit, so exercising gives you more food budget.

9. **30% / 40% / 30% macro split**: Fixed protein/carbs/fat ratio. Not configurable by the user. This is a deliberate simplification.

10. **Agent-curated often-used foods**: The often-used list is NOT auto-generated from frequency data. The agent analyzes frequency data, deduplicates, normalizes to base units, and pushes a curated list. This ensures quality over automation.

11. **Two-tier coaching**: Server generates simple rule-based tips (generate_coaching_tips). The agent writes richer, context-aware coaching via the daily coaching API. The dashboard shows the agent-written version when available.

12. **Gamification streak counts from yesterday**: Today doesn't count toward the streak because the day isn't over yet. The streak is calculated by iterating backwards from yesterday.

13. **Best streak uses GROUP BY optimization**: Instead of iterating day-by-day for 180 days, the best streak calculation uses a single GROUP BY query and then iterates the aggregated results.

14. **Polling-based dashboard refresh**: The dashboard polls every 30 seconds on the overview tab. Polling stops when the tab is hidden (visibilitychange API) and resumes when visible.

15. **No-cache dashboard serving**: The HTML is served with `Cache-Control: no-cache, no-store, must-revalidate` to ensure the latest version is always loaded after code updates.

16. **Seed data uses deterministic randomness**: `random.seed(42)` ensures demo data is reproducible across runs.

17. **One-command deploy**: `deploy.sh` auto-detects Docker or Python and handles everything. No prompts, no sudo, no decisions. Designed to be run by AI agents.

18. **Data directory isolation**: The deploy script stores the database in `./data/nutritrack.db` (not project root) so git operations never affect data. Docker uses a named volume.

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
