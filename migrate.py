import sqlite3
import re
from datetime import datetime

# Paths
OLD_DB_PATH = "/home/taner/.openclaw/workspace/My_Nutrition_Tracker/nutrition.db"
NEW_DB_PATH = "/home/taner/.openclaw/workspace/health_dashboard/nutritrack.db"

def get_meal_type(timestamp_str):
    try:
        # Timestamp format in old db: "YYYY-MM-DD HH:MM:SS"
        dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        hour = dt.hour
        if 4 <= hour < 11: return "breakfast"
        elif 11 <= hour < 16: return "lunch"
        elif 16 <= hour < 22: return "dinner"
        return "snack"
    except:
        return "snack"

def extract_duration(text):
    # Look for patterns like "30 mins", "20 min", "1 hour"
    match = re.search(r'(\d+)\s*(min|minute)', text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return 30 # Default estimate if not found

def migrate():
    print(f"Migrating from {OLD_DB_PATH} to {NEW_DB_PATH}...")
    
    try:
        old_conn = sqlite3.connect(OLD_DB_PATH)
        new_conn = sqlite3.connect(NEW_DB_PATH)
        
        old_c = old_conn.cursor()
        new_c = new_conn.cursor()
        
        # 1. Migrate Profile
        print("Migrating Profile...")
        old_c.execute("SELECT age, gender, height_cm, weight_kg, activity_level FROM users LIMIT 1")
        user = old_c.fetchone()
        
        if user:
            age, gender, height, weight, activity = user
            sex = "male" if gender and "male" in gender.lower() else "female"
            # Map activity string if necessary (old seems to match new: "Lightly Active" -> needs mapping)
            act_map = {
                "Sedentary": "sedentary",
                "Lightly Active": "light",
                "Moderately Active": "moderate",
                "Very Active": "active",
                "Extra Active": "very_active"
            }
            activity_slug = act_map.get(activity, "moderate")
            
            # Check if profile exists
            new_c.execute("SELECT id FROM user_profile LIMIT 1")
            if new_c.fetchone():
                new_c.execute("""
                    UPDATE user_profile 
                    SET age=?, sex=?, height_cm=?, current_weight_kg=?, activity_level=?
                """, (age, sex, height, weight, activity_slug))
            else:
                new_c.execute("""
                    INSERT INTO user_profile (age, sex, height_cm, current_weight_kg, activity_level)
                    VALUES (?, ?, ?, ?, ?)
                """, (age, sex, height, weight, activity_slug))
            
            # Also log current weight to history
            new_c.execute("INSERT INTO weight_logs (weight_kg, notes) VALUES (?, 'Migrated from old tracker')", (weight,))
            print("✅ Profile migrated.")
        else:
            print("⚠️ No profile found in old DB.")

        # 2. Migrate Logs
        print("Migrating Logs...")
        old_c.execute("SELECT timestamp, food_item_name, calories, protein, carbs, fats, entry_type FROM logs")
        logs = old_c.fetchall()
        
        food_count = 0
        activity_count = 0
        
        for row in logs:
            ts, name, cal, prot, carb, fat, etype = row
            
            if etype == 'Food':
                meal = get_meal_type(ts)
                new_c.execute("""
                    INSERT INTO food_entries (name, calories, protein_g, carbs_g, fat_g, meal_type, logged_at, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 'Migrated entry')
                """, (name, cal, prot, carb, fat, meal, ts))
                food_count += 1
                
            elif etype == 'Exercise':
                duration = extract_duration(name)
                new_c.execute("""
                    INSERT INTO sport_activities (activity_type, duration_minutes, calories_burned, performed_at, notes)
                    VALUES (?, ?, ?, ?, 'Migrated entry')
                """, (name, duration, cal, ts))
                activity_count += 1
        
        new_conn.commit()
        print(f"✅ Migrated {food_count} food entries.")
        print(f"✅ Migrated {activity_count} activity entries.")
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
    finally:
        if 'old_conn' in locals(): old_conn.close()
        if 'new_conn' in locals(): new_conn.close()

if __name__ == "__main__":
    migrate()
