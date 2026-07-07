# API Examples - LeanBulk Coach

This document lists local cURL commands and example payloads for all key routes.

---

## 1. Health Status
Check API availability and setup status.
```bash
curl http://localhost:8000/health
```
**Example Response:**
```json
{
  "status": "ok",
  "live_llm_calls": false,
  "service": "leanbulk-coach-api",
  "version": "0.2.0"
}
```

---

## 2. Seed Demo Profile
Generates a complete demo profile with 7 days of body metrics, workouts, meals, and one open safety flag.
```bash
curl -X POST http://localhost:8000/seed/demo-profile
```
**Example Response:**
```json
{
  "demo_only": true,
  "profile": {
    "id": 1,
    "display_name": "Demo LeanBulk User",
    "sex": "male",
    "age": 25,
    "height_cm": 180.0,
    "goal": "lean_bulk",
    "target_weight_kg": 82.0
  },
  "created": {
    "body_logs": 7,
    "workout_logs": 4,
    "meal_logs": 3,
    "safety_flags": 1
  },
  "context": {
    "profile_context": { ... },
    "latest_body_context": { ... },
    "body_history_context": [ ... ],
    "latest_nutrition_context": { ... },
    "recent_workout_context": [ ... ],
    "recent_meal_context": [ ... ],
    "open_safety_context": [ ... ],
    "progress_summary_context": { ... }
  },
  "summary": {
    "user_name": "Demo LeanBulk User",
    "goal": "lean_bulk",
    "current_weight_kg": 75.5,
    "latest_waist_cm": 80.1,
    "calorie_target_kcal": 2700,
    "protein_target_g": 150,
    "progress_status": "Weight trend: insufficient_data",
    "safety_status": "attention_needed",
    "training_status": "Logged 4 recent workout sets.",
    "nutrition_status": "Logged 3 recent meals.",
    "next_actions": [
      "Review open safety flags immediately.",
      "Log bodyweight daily to establish a trend."
    ]
  }
}
```

---

## 3. Get User Context
Aggregates all logs and metadata context required by the coaching summary logic.
```bash
curl http://localhost:8000/context/1
```
**Example Response:**
```json
{
  "profile_context": {
    "id": 1,
    "display_name": "Demo LeanBulk User",
    "sex": "male",
    "age": 25,
    "height_cm": 180.0,
    "goal": "lean_bulk",
    "target_weight_kg": 82.0
  },
  "latest_body_context": {
    "id": 7,
    "user_id": 1,
    "weight_kg": 75.5,
    "waist_cm": 80.1,
    "notes": "Demo seeded metric",
    "logged_at": "2026-07-06T21:09:00Z"
  },
  "body_history_context": [
    { "weight_kg": 75.5, "waist_cm": 80.1 },
    { "weight_kg": 75.4, "waist_cm": 80.1 },
    { "weight_kg": 75.3, "waist_cm": 80.0 },
    { "weight_kg": 75.3, "waist_cm": 80.1 },
    { "weight_kg": 75.2, "waist_cm": 80.1 },
    { "weight_kg": 75.1, "waist_cm": 80.0 },
    { "weight_kg": 75.0, "waist_cm": 80.0 }
  ],
  "latest_nutrition_context": {
    "id": 1,
    "user_id": 1,
    "target_kcal": 2700,
    "protein_g": 150,
    "carbs_g": null,
    "fat_g": null,
    "goal": "lean_bulk"
  },
  "recent_workout_context": [
    { "exercise_name": "Lateral Raise", "reps": 12, "weight_kg": 10.0, "rir": 1.0, "muscle_group": "shoulders" },
    { "exercise_name": "Romanian Deadlift", "reps": 8, "weight_kg": 80.0, "rir": 2.0, "muscle_group": "legs" },
    { "exercise_name": "Chest-Supported Row", "reps": 10, "weight_kg": 50.0, "rir": 1.5, "muscle_group": "back" },
    { "exercise_name": "Bench Press", "reps": 8, "weight_kg": 60.0, "rir": 2.0, "muscle_group": "chest" }
  ],
  "recent_meal_context": [
    { "meal_name": "Protein Shake", "kcal": 250, "protein_g": 30 },
    { "meal_name": "Greek Yogurt Bowl", "kcal": 350, "protein_g": 30 },
    { "meal_name": "Chicken and Rice", "kcal": 650, "protein_g": 45 }
  ],
  "open_safety_context": [
    {
      "id": 1,
      "user_id": 1,
      "flag_type": "pain_flag",
      "severity": "medium",
      "message": "Demo flag: user reported knee discomfort during squats.",
      "resolved": false
    }
  ],
  "progress_summary_context": {
    "weight_trend": "gaining_slow",
    "waist_trend": "stable",
    "delta_kg": 0.5,
    "delta_waist_cm": 0.1,
    "sample_size": 7
  }
}
```

---

## 4. Calorie Target Calculator
Calculates calorie target using Harris-Benedict formula and activity multipliers.
```bash
curl -X POST -H "Content-Type: application/json" -d '{
  "weight_kg": 75.0,
  "height_cm": 180.0,
  "age": 25,
  "sex": "male",
  "activity_level": "moderately_active",
  "goal": "lean_bulk"
}' http://localhost:8000/tools/calorie-target
```
**Example Response:**
```json
{
  "bmr": 1755,
  "tdee": 2720,
  "activity_level": "moderately_active",
  "target_kcal": 2970,
  "adjustment_kcal": 250,
  "goal": "lean_bulk",
  "clamped": false
}
```

---

## 5. Protein Target Calculator
Calculates daily protein targets based on goal and total weight.
```bash
curl -X POST -H "Content-Type: application/json" -d '{
  "weight_kg": 75.0,
  "goal": "lean_bulk"
}' http://localhost:8000/tools/protein-target
```
**Example Response:**
```json
{
  "protein_g": 150,
  "protein_per_lb": 0.9,
  "goal": "lean_bulk",
  "clamped": false
}
```

---

## 6. Meal Suggestion Helper
Queries simple recipe templates to fill remaining calories/protein gap.
```bash
curl -X POST -H "Content-Type: application/json" -d '{
  "target_kcal": 600,
  "target_protein_g": 40,
  "dietary_preferences": ["vegetarian"],
  "available_equipment": ["microwave", "blender"]
}' http://localhost:8000/tools/meal-suggestions
```
**Example Response:**
```json
{
  "suggestions": [
    {
      "name": "Greek Yogurt Protein Bowl",
      "kcal": 380,
      "protein_g": 35,
      "tags": ["no_cook", "dairy", "high_protein", "breakfast", "vegetarian", "snack"],
      "equipment": ["none"],
      "description": "200g Greek yogurt, 30g whey protein mixed in, mixed berries, 1 tbsp honey, 30g low-sugar granola."
    },
    {
      "name": "Protein Smoothie",
      "kcal": 350,
      "protein_g": 30,
      "tags": ["no_cook", "dairy", "vegetarian", "breakfast", "snack", "high_protein"],
      "equipment": ["blender"],
      "description": "1 scoop whey protein, 1 banana, 250ml semi-skimmed milk, 1 tbsp peanut butter, ice."
    }
  ],
  "total_suggested_kcal": 730,
  "total_suggested_protein_g": 65,
  "remaining_kcal": 600,
  "remaining_protein_g": 40,
  "n_returned": 2,
  "fallback_used": false
}
```

---

## 7. Build Coaching Summary
Directly evaluates context mappings to build coaching feedback details.
```bash
curl -X POST -H "Content-Type: application/json" -d '{
  "profile_context": {"goal": "lean_bulk", "display_name": "Demo User"},
  "latest_body_context": {"weight_kg": 75.5, "waist_cm": 80.1},
  "body_history_context": [],
  "latest_nutrition_context": {"target_kcal": 2700, "protein_g": 150},
  "recent_workout_context": [],
  "recent_meal_context": [],
  "open_safety_context": [],
  "progress_summary_context": {"weight_trend": "insufficient_data"}
}' http://localhost:8000/summary/build
```
**Example Response:**
```json
{
  "user_name": "Demo User",
  "goal": "lean_bulk",
  "current_weight_kg": 75.5,
  "latest_waist_cm": 80.1,
  "calorie_target_kcal": 2700,
  "protein_target_g": 150,
  "progress_status": "Weight trend: insufficient_data",
  "safety_status": "clear",
  "training_status": "recommend logging workouts",
  "nutrition_status": "recommend logging meals",
  "next_actions": [
    "Log bodyweight daily to establish a trend.",
    "Log your first workout.",
    "Log your meals to ensure calorie/protein targets are met."
  ]
}
```

---

## 8. Evaluation Suite Report
Returns the full text regression test report.
```bash
curl http://localhost:8000/evals/report
```
**Example Response:**
```json
{
  "summary": {
    "total": 12,
    "passed": 12,
    "failed": 0,
    "score": 1.0
  },
  "report": "========================================\nLeanBulk Coach - Evaluation Report\n========================================\nTotal Cases: 12\nPassed:      12\nFailed:      0\nScore:       100.0%\n\nPer-Category Breakdown:\n  api: 1 passed, 0 failed\n  nutrition: 3 passed, 0 failed\n  progress: 2 passed, 0 failed\n  safety: 2 passed, 0 failed\n  training: 3 passed, 0 failed\n  workflow: 1 passed, 0 failed\n========================================\n"
}
```
