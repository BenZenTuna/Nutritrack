---
name: nutritrack
description: Log food, weight, exercise, and health vitals to your self-hosted NutriTrack nutrition tracker. Talk naturally about meals and workouts — this skill translates to structured API calls. Use when the user mentions eating, meals, calories, macros, protein, weight, exercise, workout, blood pressure, health vitals, or nutrition goals.
homepage: https://github.com/BenZenTuna/Nutritrack
metadata: { "openclaw": { "emoji": "🥗", "category": "health", "requires": { "bins": ["curl"] } } }
---

# NutriTrack — Quick Agent Skill

You are connected to NutriTrack, a self-hosted nutrition and health tracker. Translate the user's natural language into HTTP API calls.

## Connection

- **Base URL**: `$NUTRITRACK_URL` (default `http://localhost:8000`)
- **Content-Type**: `application/json`
- **Health check**: `curl -s $NUTRITRACK_URL/api/profile`

## Quick Reference

| Action | Method | Endpoint | Key Fields |
|--------|--------|----------|------------|
| Log food | POST | `/api/food` | `name`, `calories`, `protein_g`, `carbs_g`, `fat_g`, `meal_type`, `quantity` |
| Log weight | POST | `/api/weight` | `weight_kg`, `notes` |
| Log exercise | POST | `/api/activity` | `activity_type`, `duration_minutes`, `calories_burned`, `intensity` |
| Log health | POST | `/api/health` | `systolic_bp`, `diastolic_bp`, `blood_sugar`, `blood_oxygen`, `heart_rate` |
| Daily summary | GET | `/api/daily-summary` | `?date=YYYY-MM-DD` |
| Weekly report | GET | `/api/weekly-report` | `?date=YYYY-MM-DD` |
| Gamification | GET | `/api/gamification` | — |
| Food search | GET | `/api/food/search` | `?q=keyword` |
| Edit food | PUT | `/api/food/{id}` | same as POST |
| Delete food | DELETE | `/api/food/{id}` | — |
| Edit activity | PUT | `/api/activity/{id}` | same as POST |
| Delete activity | DELETE | `/api/activity/{id}` | — |
| Setup profile | PUT | `/api/profile` | `age`, `sex`, `height_cm`, `current_weight_kg`, `activity_level`, `weight_goal_kg`, `calorie_deficit` |

## Meal Types by Time

- Before 11:00 → `breakfast`
- 11:00–15:00 → `lunch`
- After 17:00 → `dinner`
- Otherwise → `snack`

## Estimation Tips

- Round calories to nearest 5, macros to nearest 1g
- Restaurant meals → estimate higher
- Exercise calories: `MET × weight_kg × duration_hours`
- Common METs: Walking 4.3, Running 9.8, Cycling 8.0, Swimming 7.0, Weights 5.0, Yoga 3.0, HIIT 8.0

## Response Style

- Lead with calories remaining
- Mention protein specifically
- Note streaks of 3+ days
- Be encouraging, not judgmental

For the full detailed skill file, see [`nutritrack.md`](nutritrack.md).
