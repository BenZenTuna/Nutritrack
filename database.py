"""
NutriTrack Database Module
Handles SQLite database initialization and helper functions.
"""
import sqlite3
import os
from datetime import datetime, date, timedelta

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
        
        CREATE TABLE IF NOT EXISTS often_used_foods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            calories REAL NOT NULL DEFAULT 0,
            protein_g REAL NOT NULL DEFAULT 0,
            carbs_g REAL NOT NULL DEFAULT 0,
            fat_g REAL NOT NULL DEFAULT 0,
            meal_type TEXT DEFAULT 'snack',
            quantity TEXT,
            use_count INTEGER NOT NULL DEFAULT 1,
            last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(name, meal_type)
        );

        CREATE INDEX IF NOT EXISTS idx_food_logged_at ON food_entries(logged_at);
        CREATE INDEX IF NOT EXISTS idx_weight_measured_at ON weight_logs(measured_at);
        CREATE INDEX IF NOT EXISTS idx_activity_performed_at ON sport_activities(performed_at);
        CREATE INDEX IF NOT EXISTS idx_health_measured_at ON health_measurements(measured_at);
    """)
    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

# ── Calorie & Macro Calculation ──────────────────────────────────────

ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9,
}

def calculate_bmr(weight_kg: float, height_cm: float, age: int, sex: str) -> float:
    """Mifflin-St Jeor BMR equation."""
    bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age
    if sex == "male":
        bmr += 5
    else:
        bmr -= 161
    return round(bmr, 1)

def calculate_tdee(bmr: float, activity_level: str) -> float:
    """TDEE = BMR × activity multiplier."""
    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, 1.55)
    return round(bmr * multiplier, 1)

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

if __name__ == "__main__":
    init_db()
