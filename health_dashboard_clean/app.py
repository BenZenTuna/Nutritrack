"""
NutriTrack API Server
FastAPI backend for the nutrition tracking dashboard.
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date, timedelta
import uvicorn
import os
from database import get_db, init_db, calculate_bmr, calculate_tdee, calculate_daily_goals, calculate_gamification

# ── Initialize ───────────────────────────────────────────────────────
app = FastAPI(title="NutriTrack API", version="1.0.0")

# Serve static files
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.on_event("startup")
def startup():
    init_db()

# ── Pydantic Models ─────────────────────────────────────────────────
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

# ── Helper ───────────────────────────────────────────────────────────
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

# ── Dashboard ────────────────────────────────────────────────────────
@app.get("/")
def serve_dashboard():
    return FileResponse(os.path.join(STATIC_DIR, "dashboard.html"))

# ── Profile Endpoints ────────────────────────────────────────────────
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
    # Check if profile exists
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

# ── Food Endpoints ───────────────────────────────────────────────────
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
    conn.close()
    return {"entry": row_to_dict(row), "message": f"Logged: {entry.name} ({entry.calories} kcal)"}

@app.get("/api/food")
def get_food(date: Optional[str] = None):
    conn = get_db()
    if date:
        start, end = get_date_range(date)
        rows = conn.execute(
            "SELECT * FROM food_entries WHERE logged_at BETWEEN ? AND ? ORDER BY logged_at", (start, end)
        ).fetchall()
    else:
        # Default to today
        today = datetime.now().date().isoformat()
        start, end = get_date_range(today)
        rows = conn.execute(
            "SELECT * FROM food_entries WHERE logged_at BETWEEN ? AND ? ORDER BY logged_at", (start, end)
        ).fetchall()
    conn.close()
    return {"entries": rows_to_list(rows), "count": len(rows)}

@app.get("/api/food/range")
def get_food_range(start: str, end: str):
    conn = get_db()
    s = datetime.combine(date.fromisoformat(start), datetime.min.time()).isoformat()
    e = datetime.combine(date.fromisoformat(end), datetime.max.time()).isoformat()
    rows = conn.execute(
        "SELECT * FROM food_entries WHERE logged_at BETWEEN ? AND ? ORDER BY logged_at", (s, e)
    ).fetchall()
    conn.close()
    return {"entries": rows_to_list(rows), "count": len(rows)}

@app.delete("/api/food/{entry_id}")
def delete_food(entry_id: int):
    conn = get_db()
    conn.execute("DELETE FROM food_entries WHERE id=?", (entry_id,))
    conn.commit()
    conn.close()
    return {"message": f"Food entry {entry_id} deleted."}

# ── Weight Endpoints ─────────────────────────────────────────────────
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

@app.get("/api/weight")
def get_weight(limit: int = 90):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM weight_logs ORDER BY measured_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return {"entries": rows_to_list(rows), "count": len(rows)}

# ── Activity Endpoints ───────────────────────────────────────────────
@app.post("/api/activity")
def log_activity(entry: ActivityEntry):
    conn = get_db()
    performed_at = entry.performed_at or datetime.now().isoformat()
    
    conn.execute("""
        INSERT INTO sport_activities (activity_type, duration_minutes, calories_burned, intensity, notes, performed_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (entry.activity_type, entry.duration_minutes, entry.calories_burned, entry.intensity, entry.notes, performed_at))
    conn.commit()
    
    last_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    row = conn.execute("SELECT * FROM sport_activities WHERE id=?", (last_id,)).fetchone()
    conn.close()
    return {"entry": row_to_dict(row), "message": f"Activity logged: {entry.activity_type} ({entry.calories_burned} kcal burned)"}

@app.get("/api/activity")
def get_activity(date: Optional[str] = None):
    conn = get_db()
    if date:
        start, end = get_date_range(date)
        rows = conn.execute(
            "SELECT * FROM sport_activities WHERE performed_at BETWEEN ? AND ? ORDER BY performed_at", (start, end)
        ).fetchall()
    else:
        today = datetime.now().date().isoformat()
        start, end = get_date_range(today)
        rows = conn.execute(
            "SELECT * FROM sport_activities WHERE performed_at BETWEEN ? AND ? ORDER BY performed_at", (start, end)
        ).fetchall()
    conn.close()
    return {"entries": rows_to_list(rows), "count": len(rows)}

@app.get("/api/activity/range")
def get_activity_range(start: str, end: str):
    conn = get_db()
    s = datetime.combine(date.fromisoformat(start), datetime.min.time()).isoformat()
    e = datetime.combine(date.fromisoformat(end), datetime.max.time()).isoformat()
    rows = conn.execute(
        "SELECT * FROM sport_activities WHERE performed_at BETWEEN ? AND ? ORDER BY performed_at", (s, e)
    ).fetchall()
    conn.close()
    return {"entries": rows_to_list(rows), "count": len(rows)}

# ── Health Endpoints ─────────────────────────────────────────────────
@app.post("/api/health")
def log_health(entry: HealthEntry):
    conn = get_db()
    measured_at = entry.measured_at or datetime.now().isoformat()
    
    conn.execute("""
        INSERT INTO health_measurements (systolic_bp, diastolic_bp, blood_sugar, blood_oxygen, heart_rate, notes, measured_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (entry.systolic_bp, entry.diastolic_bp, entry.blood_sugar, entry.blood_oxygen, entry.heart_rate, entry.notes, measured_at))
    conn.commit()
    
    last_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    row = conn.execute("SELECT * FROM health_measurements WHERE id=?", (last_id,)).fetchone()
    conn.close()
    return {"entry": row_to_dict(row), "message": "Health measurement logged."}

@app.get("/api/health")
def get_health(limit: int = 90):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM health_measurements ORDER BY measured_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return {"entries": rows_to_list(rows), "count": len(rows)}

# ── Daily Summary ────────────────────────────────────────────────────
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

# ── Weekly Report ────────────────────────────────────────────────────
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

# ── History Endpoints (for charts) ───────────────────────────────────
@app.get("/api/history/daily-totals")
def get_daily_totals(days: int = 30):
    """Get daily calorie/macro totals for the last N days (for charts)."""
    end_d = datetime.now().date()
    start_d = end_d - timedelta(days=days - 1)
    
    conn = get_db()
    
    # Get profile for goals
    profile_row = conn.execute("SELECT * FROM user_profile ORDER BY id DESC LIMIT 1").fetchone()
    profile = row_to_dict(profile_row) if profile_row else None
    
    results = []
    for i in range(days):
        d = start_d + timedelta(days=i)
        ds = d.isoformat()
        start, end = get_date_range(ds)
        
        food = conn.execute(
            "SELECT COALESCE(SUM(calories),0) as cal, COALESCE(SUM(protein_g),0) as prot, "
            "COALESCE(SUM(carbs_g),0) as carb, COALESCE(SUM(fat_g),0) as fat "
            "FROM food_entries WHERE logged_at BETWEEN ? AND ?", (start, end)
        ).fetchone()
        
        activity = conn.execute(
            "SELECT COALESCE(SUM(calories_burned),0) as burned "
            "FROM sport_activities WHERE performed_at BETWEEN ? AND ?", (start, end)
        ).fetchone()
        
        goals = calculate_daily_goals(profile, activity["burned"]) if profile else None
        
        results.append({
            "date": ds,
            "calories": round(food["cal"], 1),
            "protein_g": round(food["prot"], 1),
            "carbs_g": round(food["carb"], 1),
            "fat_g": round(food["fat"], 1),
            "activity_calories": round(activity["burned"], 1),
            "calorie_goal": goals["calorie_goal"] if goals else None,
            "protein_goal_g": goals["protein_goal_g"] if goals else None,
            "carbs_goal_g": goals["carbs_goal_g"] if goals else None,
            "fat_goal_g": goals["fat_goal_g"] if goals else None,
        })
        
    conn.close()
    return {"daily_totals": results}

# ── Gamification ────────────────────────────────────────────────────
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
    # (Today doesn't add to streak until it's over, but we show current status)
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
        
        # If no food logged, streak breaks (unless we allow skip days? For now, break)
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
