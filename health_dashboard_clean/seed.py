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
