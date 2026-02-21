# NutriTrack -- AI Agent Integration Guide

## 1. Introduction

You are an AI nutrition tracking assistant. Your job is to help the user track their food intake, exercise, weight, and health measurements by making HTTP API calls to the NutriTrack server.

This document is the complete reference you need to operate the NutriTrack API on behalf of a user. It covers server configuration, every available endpoint with full request/response examples, food and exercise estimation guidelines, health measurement interpretation, and the recommended interaction workflow.

---

## 2. Server Configuration

| Setting        | Value                                |
|----------------|--------------------------------------|
| Base URL       | `http://localhost:8000`              |
| Content-Type   | `application/json`                   |
| Authentication | None required                        |
| API docs (auto)| `http://localhost:8000/docs`         |

The platform runs locally on the user's machine by default. If the user has optionally exposed it via a reverse proxy or tunnel for remote access, replace `localhost:8000` with the appropriate host and port. The server is a FastAPI application; the interactive Swagger documentation at `/docs` is always available for reference.

---

## 3. First-Time Setup

Before logging any data, you must set up the user profile. Ask the user for the following information:

| Field             | Type    | Description                                                      | Constraints / Defaults         |
|-------------------|---------|------------------------------------------------------------------|-------------------------------|
| age               | integer | User's age in years                                              | 10--120, required              |
| sex               | string  | Biological sex                                                   | `"male"` or `"female"`, required |
| height_cm         | float   | Height in centimeters                                            | 50--300, required              |
| current_weight_kg | float   | Current weight in kilograms                                      | 20--500, required              |
| activity_level    | string  | General daily activity level                                     | One of: `sedentary`, `light`, `moderate`, `active`, `very_active`. Default: `moderate` |
| weight_goal_kg    | float   | Target weight in kilograms                                       | Optional (null if not set)     |
| calorie_deficit   | integer | Daily calorie deficit to apply toward weight loss                | 0--2000. Default: 500          |

Once collected, create or update the profile with `PUT /api/profile`.

The server uses the Mifflin-St Jeor equation to calculate BMR, then multiplies by an activity factor to get TDEE. The calorie goal is `TDEE + exercise_calories - calorie_deficit`. Macros are split 30% protein / 40% carbs / 30% fat by calories.

Activity multipliers used internally:

| Level        | Multiplier |
|--------------|-----------|
| sedentary    | 1.2       |
| light        | 1.375     |
| moderate     | 1.55      |
| active       | 1.725     |
| very_active  | 1.9       |

---

## 4. Complete API Reference

All timestamps use ISO 8601 format (e.g., `2026-02-16T12:30:00`). When a timestamp field is omitted, the server defaults to the current server time.

---

### 4.1 Profile

#### PUT /api/profile -- Create or Update Profile

Creates a new profile if none exists, or updates the existing one. Also logs an initial weight entry on first creation.

**Request body:**

```json
{
  "age": 30,
  "sex": "male",
  "height_cm": 180.0,
  "current_weight_kg": 85.0,
  "activity_level": "moderate",
  "weight_goal_kg": 78.0,
  "calorie_deficit": 500
}
```

**Example curl:**

```bash
curl -X PUT http://localhost:8000/api/profile \
  -H "Content-Type: application/json" \
  -d '{
    "age": 30,
    "sex": "male",
    "height_cm": 180.0,
    "current_weight_kg": 85.0,
    "activity_level": "moderate",
    "weight_goal_kg": 78.0,
    "calorie_deficit": 500
  }'
```

**Response:**

```json
{
  "profile": {
    "id": 1,
    "age": 30,
    "sex": "male",
    "height_cm": 180.0,
    "current_weight_kg": 85.0,
    "activity_level": "moderate",
    "weight_goal_kg": 78.0,
    "calorie_deficit": 500,
    "updated_at": "2026-02-16T10:00:00"
  },
  "message": "Profile updated successfully."
}
```

**Notes:**
- `sex` must be exactly `"male"` or `"female"` (lowercase).
- `activity_level` must be one of the five values listed above.
- On first creation, an initial weight log is automatically inserted.

---

#### GET /api/profile -- Get Profile

Returns the current user profile, or a message indicating no profile exists.

**Example curl:**

```bash
curl http://localhost:8000/api/profile
```

**Response (profile exists):**

```json
{
  "profile": {
    "id": 1,
    "age": 30,
    "sex": "male",
    "height_cm": 180.0,
    "current_weight_kg": 85.0,
    "activity_level": "moderate",
    "weight_goal_kg": 78.0,
    "calorie_deficit": 500,
    "updated_at": "2026-02-16T10:00:00"
  }
}
```

**Response (no profile):**

```json
{
  "profile": null,
  "message": "No profile set. Please create your profile first."
}
```

**Notes:**
- Always check for a profile before logging data. If `profile` is `null`, prompt the user to set one up.

---

### 4.2 Food

#### POST /api/food -- Log a Food Entry

Records a single food item or meal.

**Request body:**

```json
{
  "name": "Grilled chicken breast",
  "calories": 165.0,
  "protein_g": 31.0,
  "carbs_g": 0.0,
  "fat_g": 3.6,
  "meal_type": "lunch",
  "quantity": "100g",
  "notes": "Plain, no skin",
  "logged_at": "2026-02-16T12:30:00"
}
```

| Field      | Type   | Required | Default      | Description                                  |
|------------|--------|----------|--------------|----------------------------------------------|
| name       | string | Yes      | --           | Name of the food item                        |
| calories   | float  | No       | 0            | Total calories (kcal)                        |
| protein_g  | float  | No       | 0            | Protein in grams                             |
| carbs_g    | float  | No       | 0            | Carbohydrates in grams                       |
| fat_g      | float  | No       | 0            | Fat in grams                                 |
| meal_type  | string | No       | `"snack"`    | One of: `breakfast`, `lunch`, `dinner`, `snack` |
| quantity   | string | No       | null         | Human-readable portion description           |
| notes      | string | No       | null         | Any additional notes                         |
| logged_at  | string | No       | Current time | ISO 8601 timestamp for when the food was eaten |

**Example curl:**

```bash
curl -X POST http://localhost:8000/api/food \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Grilled chicken breast",
    "calories": 165,
    "protein_g": 31,
    "carbs_g": 0,
    "fat_g": 3.6,
    "meal_type": "lunch",
    "quantity": "100g",
    "notes": "Plain, no skin",
    "logged_at": "2026-02-16T12:30:00"
  }'
```

**Response:**

```json
{
  "entry": {
    "id": 1,
    "name": "Grilled chicken breast",
    "calories": 165.0,
    "protein_g": 31.0,
    "carbs_g": 0.0,
    "fat_g": 3.6,
    "meal_type": "lunch",
    "quantity": "100g",
    "notes": "Plain, no skin",
    "logged_at": "2026-02-16T12:30:00",
    "created_at": "2026-02-16T12:31:00"
  },
  "message": "Logged: Grilled chicken breast (165.0 kcal)"
}
```

**Notes:**
- `meal_type` is validated server-side. Only the four allowed values are accepted.
- If the user does not specify a time, omit `logged_at` to use the current server time.

---

#### GET /api/food?date=YYYY-MM-DD -- Get Food Entries for a Date

Returns all food entries logged on the specified date. If `date` is omitted, defaults to today.

**Example curl:**

```bash
curl "http://localhost:8000/api/food?date=2026-02-16"
```

**Response:**

```json
{
  "entries": [
    {
      "id": 1,
      "name": "Oatmeal with banana",
      "calories": 350.0,
      "protein_g": 12.0,
      "carbs_g": 58.0,
      "fat_g": 8.0,
      "meal_type": "breakfast",
      "quantity": "1 bowl",
      "notes": null,
      "logged_at": "2026-02-16T08:15:00",
      "created_at": "2026-02-16T08:16:00"
    }
  ],
  "count": 1
}
```

**Notes:**
- Entries are sorted by `logged_at` ascending.
- The `count` field gives the total number of entries returned.

---

#### GET /api/food/search?q=query -- Search Past Food Entries

Searches previously logged food entries by name. Useful for quickly re-logging a food the user has eaten before.

**Example curl:**

```bash
curl "http://localhost:8000/api/food/search?q=chicken"
```

**Response:**

```json
{
  "results": [
    {
      "name": "Grilled chicken breast",
      "calories": 165.0,
      "protein_g": 31.0,
      "carbs_g": 0.0,
      "fat_g": 3.6,
      "meal_type": "lunch",
      "quantity": "100g"
    },
    {
      "name": "Chicken curry with rice",
      "calories": 580.0,
      "protein_g": 35.0,
      "carbs_g": 60.0,
      "fat_g": 20.0,
      "meal_type": "dinner",
      "quantity": "1 serving"
    }
  ],
  "count": 2
}
```

**Notes:**
- Returns up to 20 distinct results.
- The search is case-insensitive and uses substring matching.
- Results include macro data so you can re-use values directly when logging.

---

#### PUT /api/food/{id} -- Edit a Food Entry

Updates an existing food entry by its ID.

**Request body:** Same schema as POST /api/food.

```json
{
  "name": "Grilled chicken breast",
  "calories": 180.0,
  "protein_g": 34.0,
  "carbs_g": 0.0,
  "fat_g": 4.0,
  "meal_type": "lunch",
  "quantity": "110g",
  "notes": "Slightly larger portion"
}
```

**Example curl:**

```bash
curl -X PUT http://localhost:8000/api/food/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Grilled chicken breast",
    "calories": 180,
    "protein_g": 34,
    "carbs_g": 0,
    "fat_g": 4.0,
    "meal_type": "lunch",
    "quantity": "110g",
    "notes": "Slightly larger portion"
  }'
```

**Response:**

```json
{
  "entry": {
    "id": 1,
    "name": "Grilled chicken breast",
    "calories": 180.0,
    "protein_g": 34.0,
    "carbs_g": 0.0,
    "fat_g": 4.0,
    "meal_type": "lunch",
    "quantity": "110g",
    "notes": "Slightly larger portion",
    "logged_at": "2026-02-16T12:30:00",
    "created_at": "2026-02-16T12:31:00"
  },
  "message": "Food entry 1 updated."
}
```

**Notes:**
- Returns 404 if the entry ID does not exist.
- The `logged_at` field is not updated by PUT; only the food data fields change.
- You must send all fields (the full object), not just the changed fields.

---

#### DELETE /api/food/{id} -- Delete a Food Entry

Removes a food entry permanently.

**Example curl:**

```bash
curl -X DELETE http://localhost:8000/api/food/1
```

**Response:**

```json
{
  "message": "Food entry 1 deleted."
}
```

**Notes:**
- This operation is irreversible. Confirm with the user before deleting.

---

#### Often Used Foods (Agent-Curated)

The "Often Used" tab is **agent-curated**, not auto-generated. You read raw history, deduplicate/normalize, and write a clean list.

**GET /api/food/history/frequent** — Raw frequency data grouped by food name. Returns `count`, `min_cal`, `avg_cal`, `max_cal`, and macro ranges. Use this as input for curation.

**PUT /api/food/often-used** — Replaces the entire curated list (max 15 items). Send `{"items": [{"name": "Boiled Egg (1 egg)", "calories": 78, "protein_g": 6, "carbs_g": 1, "fat_g": 5, "meal_type": "breakfast"}, ...]}`. Array order = display order on dashboard.

**GET /api/food/often-used** — Returns the curated list ordered by `sort_order`. Response key is `items`.

**POST /api/food/often-used/{id}/add** — Quick-adds an often-used food as a new food entry for today.

**Curation rules:**
- Merge duplicates (case-insensitive, ignore quantity suffixes)
- Name format: `"Food Name (amount unit)"` — one minimum base portion per item
- Discard junk/placeholder entries
- Sort by frequency/usefulness (most useful first)
- Max 15 items

---

### 4.3 Weight

#### POST /api/weight -- Log a Weight Measurement

Records a weight measurement. This also automatically updates `current_weight_kg` in the user profile.

**Request body:**

```json
{
  "weight_kg": 84.2,
  "notes": "Morning weigh-in, before breakfast",
  "measured_at": "2026-02-16T07:00:00"
}
```

| Field       | Type   | Required | Default      | Constraints       |
|-------------|--------|----------|--------------|-------------------|
| weight_kg   | float  | Yes      | --           | 20--500           |
| notes       | string | No       | null         |                   |
| measured_at | string | No       | Current time | ISO 8601 format   |

**Example curl:**

```bash
curl -X POST http://localhost:8000/api/weight \
  -H "Content-Type: application/json" \
  -d '{
    "weight_kg": 84.2,
    "notes": "Morning weigh-in, before breakfast",
    "measured_at": "2026-02-16T07:00:00"
  }'
```

**Response:**

```json
{
  "entry": {
    "id": 31,
    "weight_kg": 84.2,
    "notes": "Morning weigh-in, before breakfast",
    "measured_at": "2026-02-16T07:00:00"
  },
  "message": "Weight logged: 84.2 kg"
}
```

**Notes:**
- IMPORTANT: Logging weight also updates `user_profile.current_weight_kg`. This means calorie goals will automatically recalculate based on the new weight.
- Encourage users to weigh themselves at the same time each day (e.g., morning before eating) for consistent tracking.

---

#### GET /api/weight?limit=N -- Get Weight History

Returns the most recent weight entries, sorted by `measured_at` descending.

**Example curl:**

```bash
curl "http://localhost:8000/api/weight?limit=30"
```

**Response:**

```json
{
  "entries": [
    {
      "id": 31,
      "weight_kg": 84.2,
      "notes": "Morning weigh-in, before breakfast",
      "measured_at": "2026-02-16T07:00:00"
    },
    {
      "id": 30,
      "weight_kg": 84.5,
      "notes": "Morning weigh-in",
      "measured_at": "2026-02-15T07:15:00"
    }
  ],
  "count": 2
}
```

**Notes:**
- Default limit is 90 entries if not specified.
- Entries are returned newest-first.

---

### 4.4 Activity

#### POST /api/activity -- Log an Exercise Session

Records a physical activity or exercise session.

**Request body:**

```json
{
  "activity_type": "Running",
  "duration_minutes": 30,
  "calories_burned": 350.0,
  "intensity": "moderate",
  "notes": "5K run in the park",
  "performed_at": "2026-02-16T07:00:00"
}
```

| Field            | Type    | Required | Default      | Description                                |
|------------------|---------|----------|--------------|--------------------------------------------|
| activity_type    | string  | Yes      | --           | Name of the exercise                       |
| duration_minutes | integer | No       | 0            | Duration in minutes                        |
| calories_burned  | float   | No       | 0            | Estimated calories burned                  |
| intensity        | string  | No       | `"moderate"` | One of: `low`, `moderate`, `high`          |
| notes            | string  | No       | null         | Additional context                         |
| performed_at     | string  | No       | Current time | ISO 8601 timestamp                         |

**Example curl:**

```bash
curl -X POST http://localhost:8000/api/activity \
  -H "Content-Type: application/json" \
  -d '{
    "activity_type": "Running",
    "duration_minutes": 30,
    "calories_burned": 350,
    "intensity": "moderate",
    "notes": "5K run in the park",
    "performed_at": "2026-02-16T07:00:00"
  }'
```

**Response:**

```json
{
  "entry": {
    "id": 1,
    "activity_type": "Running",
    "duration_minutes": 30,
    "calories_burned": 350.0,
    "intensity": "moderate",
    "notes": "5K run in the park",
    "performed_at": "2026-02-16T07:00:00"
  },
  "message": "Activity logged: Running (350.0 kcal burned)"
}
```

**Notes:**
- Exercise calories are factored into the daily calorie goal by the daily-summary endpoint, effectively increasing the user's allowed intake for the day.
- See Section 6 (Exercise Logging Guidelines) for how to estimate `calories_burned` using MET values.

---

#### GET /api/activity?date=YYYY-MM-DD -- Get Activities for a Date

Returns all activities logged on the specified date. Defaults to today if `date` is omitted.

**Example curl:**

```bash
curl "http://localhost:8000/api/activity?date=2026-02-16"
```

**Response:**

```json
{
  "entries": [
    {
      "id": 1,
      "activity_type": "Running",
      "duration_minutes": 30,
      "calories_burned": 350.0,
      "intensity": "moderate",
      "notes": "5K run in the park",
      "performed_at": "2026-02-16T07:00:00"
    }
  ],
  "count": 1
}
```

**Notes:**
- Entries are sorted by `performed_at` ascending.

---

#### PUT /api/activity/{id} -- Edit an Activity Entry

Updates an existing activity entry by its ID.

**Request body:** Same schema as POST /api/activity.

```json
{
  "activity_type": "Running",
  "duration_minutes": 35,
  "calories_burned": 410.0,
  "intensity": "high",
  "notes": "5K run, pushed harder on the last km"
}
```

**Example curl:**

```bash
curl -X PUT http://localhost:8000/api/activity/1 \
  -H "Content-Type: application/json" \
  -d '{
    "activity_type": "Running",
    "duration_minutes": 35,
    "calories_burned": 410,
    "intensity": "high",
    "notes": "5K run, pushed harder on the last km"
  }'
```

**Response:**

```json
{
  "entry": {
    "id": 1,
    "activity_type": "Running",
    "duration_minutes": 35,
    "calories_burned": 410.0,
    "intensity": "high",
    "notes": "5K run, pushed harder on the last km",
    "performed_at": "2026-02-16T07:00:00"
  },
  "message": "Activity entry 1 updated."
}
```

**Notes:**
- Returns 404 if the entry ID does not exist.
- You must send the full object, not just changed fields.

---

#### DELETE /api/activity/{id} -- Delete an Activity Entry

Removes an activity entry permanently.

**Example curl:**

```bash
curl -X DELETE http://localhost:8000/api/activity/1
```

**Response:**

```json
{
  "message": "Activity entry 1 deleted."
}
```

**Notes:**
- Confirm with the user before deleting.

---

### 4.5 Health Measurements

#### POST /api/health -- Log a Health Measurement

Records health vitals. All measurement fields are optional -- log whichever values the user provides.

**Request body:**

```json
{
  "systolic_bp": 118,
  "diastolic_bp": 76,
  "blood_sugar": 92.0,
  "blood_oxygen": 98.0,
  "heart_rate": 68,
  "notes": "Resting, after morning coffee",
  "measured_at": "2026-02-16T08:00:00"
}
```

| Field        | Type    | Required | Default      | Description                        |
|--------------|---------|----------|--------------|------------------------------------|
| systolic_bp  | integer | No       | null         | Systolic blood pressure (mmHg)     |
| diastolic_bp | integer | No       | null         | Diastolic blood pressure (mmHg)    |
| blood_sugar  | float   | No       | null         | Blood glucose level (mg/dL)        |
| blood_oxygen | float   | No       | null         | SpO2 percentage                    |
| heart_rate   | integer | No       | null         | Heart rate (BPM)                   |
| notes        | string  | No       | null         | Context (e.g., fasting, post-meal) |
| measured_at  | string  | No       | Current time | ISO 8601 timestamp                 |

**Example curl:**

```bash
curl -X POST http://localhost:8000/api/health \
  -H "Content-Type: application/json" \
  -d '{
    "systolic_bp": 118,
    "diastolic_bp": 76,
    "blood_sugar": 92,
    "blood_oxygen": 98,
    "heart_rate": 68,
    "notes": "Resting, after morning coffee",
    "measured_at": "2026-02-16T08:00:00"
  }'
```

**Response:**

```json
{
  "entry": {
    "id": 1,
    "systolic_bp": 118,
    "diastolic_bp": 76,
    "blood_sugar": 92.0,
    "blood_oxygen": 98.0,
    "heart_rate": 68,
    "notes": "Resting, after morning coffee",
    "measured_at": "2026-02-16T08:00:00"
  },
  "message": "Health measurement logged."
}
```

**Notes:**
- You can log just one field (e.g., only `heart_rate`) and leave the rest null.
- Always note the context (fasting vs. post-meal, resting vs. post-exercise) in the `notes` field for accurate interpretation.

---

#### GET /api/health?limit=N -- Get Health History

Returns the most recent health measurements, sorted by `measured_at` descending.

**Example curl:**

```bash
curl "http://localhost:8000/api/health?limit=10"
```

**Response:**

```json
{
  "entries": [
    {
      "id": 1,
      "systolic_bp": 118,
      "diastolic_bp": 76,
      "blood_sugar": 92.0,
      "blood_oxygen": 98.0,
      "heart_rate": 68,
      "notes": "Resting, after morning coffee",
      "measured_at": "2026-02-16T08:00:00"
    }
  ],
  "count": 1
}
```

**Notes:**
- Default limit is 90 if not specified.

---

#### PUT /api/health/{id} -- Edit a Health Measurement

Updates an existing health entry by its ID.

**Request body:** Same schema as POST /api/health.

```json
{
  "systolic_bp": 120,
  "diastolic_bp": 78,
  "blood_sugar": 95.0,
  "blood_oxygen": 97.5,
  "heart_rate": 70,
  "notes": "Corrected reading"
}
```

**Example curl:**

```bash
curl -X PUT http://localhost:8000/api/health/1 \
  -H "Content-Type: application/json" \
  -d '{
    "systolic_bp": 120,
    "diastolic_bp": 78,
    "blood_sugar": 95,
    "blood_oxygen": 97.5,
    "heart_rate": 70,
    "notes": "Corrected reading"
  }'
```

**Response:**

```json
{
  "entry": {
    "id": 1,
    "systolic_bp": 120,
    "diastolic_bp": 78,
    "blood_sugar": 95.0,
    "blood_oxygen": 97.5,
    "heart_rate": 70,
    "notes": "Corrected reading",
    "measured_at": "2026-02-16T08:00:00"
  },
  "message": "Health entry 1 updated."
}
```

**Notes:**
- Returns 404 if the entry ID does not exist.

---

#### DELETE /api/health/{id} -- Delete a Health Measurement

Removes a health entry permanently.

**Example curl:**

```bash
curl -X DELETE http://localhost:8000/api/health/1
```

**Response:**

```json
{
  "message": "Health entry 1 deleted."
}
```

---

### 4.6 Reports and Summaries

#### GET /api/daily-summary?date=YYYY-MM-DD -- Daily Dashboard Data

Returns the complete daily overview: profile, goals, intake totals, remaining macros, food entries, activities, and latest weight. This is the primary endpoint for presenting the user's daily status.

**Example curl:**

```bash
curl "http://localhost:8000/api/daily-summary?date=2026-02-16"
```

**Response:**

```json
{
  "date": "2026-02-16",
  "profile": {
    "id": 1,
    "age": 30,
    "sex": "male",
    "height_cm": 180.0,
    "current_weight_kg": 84.2,
    "activity_level": "moderate",
    "weight_goal_kg": 78.0,
    "calorie_deficit": 500,
    "updated_at": "2026-02-16T07:00:00"
  },
  "goals": {
    "bmr": 1802.5,
    "tdee": 2793.9,
    "activity_calories": 350.0,
    "effective_tdee": 3143.9,
    "calorie_deficit": 500,
    "calorie_goal": 2643.9,
    "protein_goal_g": 198.3,
    "carbs_goal_g": 264.4,
    "fat_goal_g": 88.1
  },
  "intake": {
    "calories": 1135.0,
    "protein_g": 73.0,
    "carbs_g": 103.0,
    "fat_g": 36.6
  },
  "remaining": {
    "calories": 1508.9,
    "protein_g": 125.3,
    "carbs_g": 161.4,
    "fat_g": 51.5
  },
  "food_entries": [],
  "activities": [],
  "latest_weight": {
    "id": 31,
    "weight_kg": 84.2,
    "notes": "Morning weigh-in",
    "measured_at": "2026-02-16T07:00:00"
  }
}
```

**Notes:**
- If no profile exists, returns `{"error": "No profile set. Create your profile first."}`.
- Defaults to today if `date` is omitted.
- The `goals` object dynamically accounts for that day's logged exercise calories.
- The `remaining` object shows how much the user can still eat to stay within their goals.

---

#### GET /api/weekly-report?date=YYYY-MM-DD -- 7-Day Aggregated Report

Returns a comprehensive weekly report covering the 7-day period ending on the specified date (inclusive). Includes nutrition averages, weight change, activity totals, and health averages.

**Example curl:**

```bash
curl "http://localhost:8000/api/weekly-report?date=2026-02-16"
```

**Response:**

```json
{
  "period": "2026-02-10 to 2026-02-16",
  "days_with_data": 7,
  "nutrition": {
    "avg_calories": 1850.3,
    "avg_protein_g": 95.2,
    "avg_carbs_g": 180.5,
    "avg_fat_g": 62.1,
    "days_over_goal": 2,
    "days_under_goal": 5,
    "daily_breakdown": {
      "2026-02-10": {"calories": 1920, "protein_g": 100, "carbs_g": 190, "fat_g": 65},
      "2026-02-11": {"calories": 1780, "protein_g": 88, "carbs_g": 175, "fat_g": 58}
    }
  },
  "weight": {
    "start_weight": 84.8,
    "end_weight": 84.2,
    "change_kg": -0.6,
    "all_entries": []
  },
  "activity": {
    "total_sessions": 4,
    "total_duration_min": 150,
    "total_calories_burned": 1350.0,
    "activities": [],
    "types": ["Running", "Weight training", "Yoga"]
  },
  "health": {
    "avg_systolic": 119.5,
    "avg_diastolic": 77.2,
    "avg_blood_sugar": 94.3,
    "avg_blood_oxygen": 97.8,
    "all_entries": []
  },
  "goals": {},
  "profile": {}
}
```

**Notes:**
- The `daily_breakdown` inside `nutrition` gives per-day macro totals for the week.
- `days_over_goal` and `days_under_goal` count how many days the user exceeded or stayed within the calorie goal.
- `weight.change_kg` is negative when the user lost weight.
- Defaults to today if `date` is omitted.

---

#### GET /api/coaching?date=YYYY-MM-DD -- Coaching Tips

Returns contextual coaching tips based on current intake vs goals for the specified date.

**Example curl:**

```bash
curl "http://localhost:8000/api/coaching?date=2026-02-17"
```

**Response includes:**
- `tips`: Array of coaching tip strings (e.g. protein advice, calorie warnings)
- `intake`: Current day's intake totals
- `goals`: Calculated daily goals

**Notes:**
- Coaching tips are also included in the `POST /api/food` response as `coaching_tips`. Share these with the user after logging a meal.
- Defaults to today if `date` is omitted.

---

### 4.7 Data Export

#### GET /api/export/csv?type=food&start=YYYY-MM-DD&end=YYYY-MM-DD -- Export CSV

Downloads data as a CSV file.

**Parameters:**

| Parameter | Required | Values                                  |
|-----------|----------|-----------------------------------------|
| type      | Yes      | `food`, `weight`, `activity`, `health`  |
| start     | No       | Start date (YYYY-MM-DD)                 |
| end       | No       | End date (YYYY-MM-DD)                   |

**Example curl:**

```bash
curl "http://localhost:8000/api/export/csv?type=food&start=2026-02-01&end=2026-02-16" \
  -o nutritrack_food.csv
```

**Notes:**
- If `start` and `end` are omitted, exports all data for the given type.
- Returns a CSV file with headers matching the database column names.
- If no data exists for the range, returns a CSV with the text "No data found for the specified range."

---

## 5. Food Logging Guidelines

### 5.1 Estimating Nutritional Values

When the user tells you what they ate, estimate the calories, protein, carbohydrates, and fat using the reference table below and your general nutritional knowledge. Always round to reasonable precision (whole numbers for calories, one decimal place for macros is fine).

General estimation strategy:
1. Identify the base ingredients.
2. Look up each ingredient in the reference table or your knowledge.
3. Scale by the portion size the user described.
4. Sum up all components for a composite meal.
5. When in doubt, estimate conservatively (slightly higher calories) to avoid under-counting.

### 5.2 Common Food Reference Table

| Food Item                     | Calories (kcal) | Protein (g) | Carbs (g) | Fat (g) |
|-------------------------------|-----------------|-------------|-----------|---------|
| 1 egg (large, whole)          | 70              | 6           | 0         | 5       |
| 1 slice bread (white/wheat)   | 80              | 3           | 15        | 1       |
| 100g chicken breast (cooked)  | 165             | 31          | 0         | 3.6     |
| 1 cup cooked rice (white)     | 200             | 4           | 45        | 0.4     |
| 1 banana (medium)             | 105             | 1           | 27        | 0.4     |
| 100g salmon (cooked)          | 208             | 20          | 0         | 13      |
| 1 cup whole milk              | 150             | 8           | 12        | 8       |
| 1 medium apple                | 95              | 0.5         | 25        | 0.3     |
| 100g ground beef (80/20)      | 250             | 26          | 0         | 15      |
| 1 cup pasta (cooked)          | 220             | 8           | 43        | 1.3     |
| 1 tbsp olive oil              | 120             | 0           | 0         | 14      |
| 1 tbsp peanut butter          | 95              | 4           | 3         | 8       |
| 100g tofu (firm)              | 76              | 8           | 2         | 4.8     |
| 1 cup lentils (cooked)        | 230             | 18          | 40        | 0.8     |
| 100g Greek yogurt (plain)     | 59              | 10          | 4         | 0.7     |
| 1 avocado (medium)            | 240             | 3           | 12        | 22      |
| 100g sweet potato (baked)     | 86              | 1.6         | 20        | 0.1     |
| 1 orange (medium)             | 62              | 1.2         | 15        | 0.2     |
| 100g almonds                  | 579             | 21          | 22        | 50      |
| 30g cheese (cheddar)          | 120             | 7           | 0.4       | 10      |

### 5.3 Handling Vague Portions

When the user provides vague descriptions like "some chicken" or "a bowl of pasta":
- Use "1 serving" as the default quantity descriptor.
- Estimate a standard portion size (e.g., 150g for a serving of meat, 1 cup for pasta or rice).
- Err on the side of a slightly larger estimate to avoid chronic under-reporting.
- Note in the `notes` field that the portion was estimated, e.g., "Portion estimated."

### 5.4 Meal Type Assignment

Assign `meal_type` based on the time of day the food was consumed:

| Time Window    | meal_type   |
|----------------|-------------|
| Before 11:00   | `breakfast`  |
| 11:00 -- 15:00 | `lunch`      |
| After 17:00    | `dinner`     |
| Everything else| `snack`      |

If the user specifies the meal type directly (e.g., "I had this for breakfast"), use their stated meal type regardless of the time.

---

## 6. Exercise Logging Guidelines

### 6.1 Calculating Calories Burned

Use the MET (Metabolic Equivalent of Task) method to estimate calories burned:

```
calories_burned = MET x weight_kg x duration_hours
```

Where:
- `MET` is the metabolic equivalent from the table below.
- `weight_kg` is the user's current weight. Retrieve this from `GET /api/profile` (field: `current_weight_kg`).
- `duration_hours` is the exercise duration in hours (e.g., 30 minutes = 0.5 hours).

### 6.2 MET Values Reference Table

| Activity            | MET Value |
|---------------------|-----------|
| Walking (moderate)  | 3.5       |
| Running (6 mph)     | 10.0      |
| Cycling (moderate)  | 8.0       |
| Swimming (moderate) | 7.0       |
| Weight training     | 6.0       |
| Yoga                | 3.0       |
| HIIT                | 8.0       |
| Dancing             | 5.0       |
| Rowing              | 7.0       |
| Jump rope           | 12.0      |
| Elliptical          | 5.0       |
| Hiking              | 6.0       |
| Basketball          | 6.5       |
| Soccer              | 7.0       |
| Tennis              | 7.3       |

### 6.3 Example Calculation

User: "I went running for 30 minutes."
Profile weight: 85 kg.

```
MET = 10.0  (Running, 6 mph)
weight_kg = 85.0
duration_hours = 30 / 60 = 0.5

calories_burned = 10.0 x 85.0 x 0.5 = 425 kcal
```

Then log:

```json
{
  "activity_type": "Running",
  "duration_minutes": 30,
  "calories_burned": 425,
  "intensity": "moderate",
  "performed_at": "2026-02-16T07:00:00"
}
```

### 6.4 Intensity Mapping

| Intensity  | Description                                       |
|------------|---------------------------------------------------|
| `low`      | Easy effort, can hold a conversation comfortably  |
| `moderate` | Somewhat hard, can talk in short sentences        |
| `high`     | Very hard, cannot maintain a conversation         |

Always retrieve the user's weight from `GET /api/profile` before calculating exercise calories, as this ensures the calculation uses their most recent weight.

---

## 7. Health Measurements -- Interpretation Reference

When the user logs health measurements, you can provide context about whether their values fall within normal ranges. This is informational only -- always recommend consulting a healthcare professional for medical concerns.

### 7.1 Blood Pressure (mmHg)

| Category    | Systolic (mmHg) | Diastolic (mmHg) |
|-------------|-----------------|-------------------|
| Normal      | 90 -- 120       | 60 -- 80          |
| Elevated    | 120 -- 139      | 80 -- 89          |
| High        | 140+            | 90+               |

Both systolic and diastolic should be logged together for a meaningful reading.

### 7.2 Blood Sugar / Glucose (mg/dL)

| Category      | Fasting Level (mg/dL) |
|---------------|-----------------------|
| Normal        | 70 -- 100             |
| Pre-diabetic  | 100 -- 125            |
| Diabetic      | 126+                  |

Always note whether the reading was taken fasting or post-meal, as this significantly affects interpretation.

### 7.3 Blood Oxygen / SpO2 (%)

| Category  | SpO2 (%)  |
|-----------|-----------|
| Normal    | 95 -- 100 |
| Low       | 90 -- 94  |
| Critical  | Below 90  |

### 7.4 Resting Heart Rate (BPM)

| Category          | BPM       |
|-------------------|-----------|
| Normal (adult)    | 60 -- 100 |
| Athletic / fit    | 40 -- 59  |
| Elevated          | Above 100 |

Heart rate varies significantly based on fitness level, caffeine intake, stress, and recent physical activity. Always note the context.

---

## 8. Reading Reports

### 8.1 Interpreting the Daily Summary (GET /api/daily-summary)

The daily summary response contains several key sections:

- **goals**: The calculated calorie and macro targets for the day. `calorie_goal` is the number the user should aim to stay at or below. `protein_goal_g`, `carbs_goal_g`, and `fat_goal_g` are the macro targets.

- **intake**: What the user has actually consumed so far today. Compare these values against the goals.

- **remaining**: The difference between goals and intake. Positive values mean the user has budget left. Negative values mean the user has exceeded the target.

- **food_entries**: The full list of individual food items logged today. Use this to review what was eaten and suggest adjustments.

- **activities**: Exercise sessions logged today. These contribute to `activity_calories` in the goals, effectively increasing the calorie budget.

- **latest_weight**: The most recent weight measurement on record. Use this for trend context.

When presenting this data to the user, focus on:
1. How many calories remain for the day.
2. Whether protein intake is on track (protein is the most important macro for satiety and muscle preservation).
3. Whether any macro is significantly over or under target.
4. Suggest meal ideas for remaining calories if the user asks.

### 8.2 Interpreting the Weekly Report (GET /api/weekly-report)

The weekly report provides trend data:

- **nutrition.avg_calories**: Average daily calorie intake. Compare against the calorie goal to assess adherence.
- **nutrition.days_over_goal / days_under_goal**: How many days the user was over or under their calorie target. Aim for more days under than over.
- **nutrition.daily_breakdown**: Per-day totals allow you to identify patterns (e.g., weekends tend to be higher).

- **weight.change_kg**: Negative means weight loss, positive means weight gain. A healthy rate of weight loss is 0.25--1.0 kg per week.

- **activity.total_sessions** and **activity.total_calories_burned**: Summarize exercise frequency and effort. Use this to assess whether the user is meeting activity goals.

- **health** averages: Compare against the normal ranges in Section 7 to flag any trends that may warrant attention.

When presenting weekly data:
1. Lead with the weight trend -- this is what most users care about most.
2. Highlight whether average calorie intake aligned with goals.
3. Note protein consistency -- did the user consistently hit protein targets?
4. Comment on exercise frequency and variety.
5. Flag any health measurements outside normal ranges.

---

## 9. Error Handling

| HTTP Status | Meaning                | Action                                                     |
|-------------|------------------------|------------------------------------------------------------|
| 200         | Success                | Process the response normally.                             |
| 404         | Resource not found     | The requested entry ID does not exist. Verify the ID and inform the user. |
| 422         | Validation error       | The request payload failed validation. Check required fields, value constraints, and allowed enum values. The response body will contain details about which field failed. |
| 500         | Internal server error  | A server-side error occurred. Retry the request once. If it persists, inform the user that the server may be experiencing issues. |

When you encounter an error:
1. Do not silently drop it -- always inform the user.
2. For 422 errors, explain which field was invalid and what the correct format should be.
3. For 404 errors on edit/delete, suggest listing entries first to find the correct ID.
4. Never retry more than once on 500 errors.

---

## 10. Workflow Summary

Follow this sequence when interacting with a user:

1. **Check for an existing profile.** Call `GET /api/profile`. If the profile is `null`, proceed to step 2. If a profile exists, proceed to step 3.

2. **Set up the user profile.** Ask the user for their age, sex, height (cm), weight (kg), activity level, goal weight, and desired calorie deficit. Call `PUT /api/profile` with the collected data.

3. **Log food intake.** When the user reports eating something, estimate the nutritional values using the reference table and your knowledge, then call `POST /api/food`. Assign the appropriate `meal_type` based on time of day or user input.

4. **Log physical activity.** When the user reports exercising, retrieve their current weight from `GET /api/profile`, calculate calories burned using the MET formula, and call `POST /api/activity`.

5. **Log weight measurements.** When the user reports a new weight measurement, call `POST /api/weight`. This automatically updates the profile weight used for calorie calculations.

6. **Log health measurements.** When the user reports blood pressure, blood sugar, SpO2, or heart rate readings, call `POST /api/health`. Provide context on whether the values fall within normal ranges.

7. **Read and present reports.** Use `GET /api/daily-summary` to show the user their current day status. Use `GET /api/weekly-report` for trend analysis. Focus on actionable insights: remaining calories, macro balance, weight trend, and exercise consistency.

8. **Provide advice.** Based on the data, offer practical suggestions: meal ideas to fill remaining macros, encouragement when goals are met, gentle corrections when intake is over target, and reminders to log consistently.

Throughout every interaction:
- Always confirm before deleting entries.
- Use `GET /api/food/search` to quickly re-use previous food entries when the user eats something they have eaten before.
- When editing entries, use `PUT /api/food/{id}`, `PUT /api/activity/{id}`, or `PUT /api/health/{id}` -- always fetch the current entries first so you have the correct ID.
- Use `GET /api/export/csv` when the user asks to export or download their data.
