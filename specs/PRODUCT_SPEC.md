# Product Spec — LeanBulk Coach MVP

**Version**: 1.0  
**Status**: Active  
**Audience**: Skinny-fat beginners (18–40, untrained or <1 year training)

---

## Problem Statement

Skinny-fat beginners face a uniquely confusing starting point: they have excess body fat AND lack muscle mass simultaneously. Generic fitness advice ("just bulk" or "just cut") leads to poor outcomes. They need personalized, weekly adaptive coaching that balances fat loss, muscle gain, and safety — without requiring a personal trainer.

---

## Target User

| Attribute | Details |
|---|---|
| Experience | Beginner (0–12 months consistent training) |
| Body composition | Skinny-fat (normal BMI but high body fat %, low muscle mass) |
| Primary goal | Improve body composition (lose fat, gain muscle) |
| Resources | Home gym or commercial gym, basic cooking ability |
| Tech comfort | Can use a web app, fill in a form weekly |

**Out of scope for MVP**: Intermediate/advanced athletes, competitive bodybuilders, athletes with sport-specific goals, medical patients.

---

## MVP Features

### 1. Intake Form (Onboarding)
Collected once (or updated as profile changes):

| Field | Type | Validation |
|---|---|---|
| Age | Integer | 16–75 |
| Sex | Enum | male / female / prefer_not_to_say |
| Height | Float (cm) | 100–250 |
| Weight | Float (kg) | 35–250 |
| Waist circumference | Float (cm) | 50–200 |
| Training level | Enum | beginner / intermediate / advanced |
| Primary goal | Enum | lean_bulk / mini_cut / maintain |
| Training days per week | Integer | 1–6 |
| Equipment available | Multi-select | barbell / dumbbells / cables / bodyweight / bands |
| Dietary preferences | Multi-select | vegetarian / vegan / dairy_free / no_fish / no_restrictions |
| Injury limitations | Text (optional) | Free text, triggers guardrail review |

### 2. Weekly Check-In
Submitted once per week:

| Field | Type | Notes |
|---|---|---|
| 7-day average weight | Float (kg) | User manually averages or logs daily |
| Current waist measurement | Float (cm) | Same time/conditions each week |
| Average daily calories consumed | Integer | From tracking app or estimate |
| Average daily protein consumed | Integer (g) | From tracking app or estimate |
| Workouts completed this week | Integer | Actual vs planned |
| Key lifts log | List of {exercise, weight_kg, reps} | Optional for beginners |
| Average sleep per night | Float (hours) | Self-reported |
| Energy/recovery level | Integer (1–5) | Subjective |
| Notes / flags | Text (optional) | Free text; scanned for pain/medical keywords |

### 3. Agent Output (Coach Response)
Structured response after each weekly check-in:

| Field | Description |
|---|---|
| `current_status` | Plain-English summary of this week's data |
| `decision` | One of: `LEAN_BULK_CONTINUE`, `LEAN_BULK_START`, `MAINTAIN`, `MINI_CUT`, `DELOAD` |
| `decision_reasoning` | Short explanation of why this decision was made |
| `calorie_target` | New recommended daily calorie target |
| `protein_target` | New recommended daily protein target (g) |
| `training_recommendation` | Progression note or deload protocol |
| `safety_warning` | Present only if guardrail triggered (empty string otherwise) |
| `coach_message` | Warm, motivating 2–3 sentence coach note |
| `medical_disclaimer` | Always present. Fixed text. |

### 4. Progress Dashboard
Visual overview of trends (Phase 3 frontend):
- Weight trend chart (8-week rolling)
- Waist trend chart (8-week rolling)
- Calorie + protein adherence bars (current week)
- Workout adherence (current week)
- Current decision badge

### 5. Meal Helper
Triggered after check-in or on demand:
- Input: remaining calorie/protein gap for the day + dietary preferences
- Output: 2–3 simple meal suggestions with macros
- Filtering: respects dietary preferences and available equipment

---

## The 4-Decision Taxonomy

| Decision | Trigger Conditions |
|---|---|
| **LEAN_BULK_CONTINUE** | Weight gaining ≤0.45kg/week, waist stable or decreasing, adherence ≥70%, strength progressing |
| **LEAN_BULK_START** | First check-in, beginner, waist not elevated, ready to add ∼250 kcal surplus |
| **MAINTAIN** | Weight stable, waist stable, low adherence OR high stress, borderline signals |
| **MINI_CUT** | Waist increasing >0.5cm/week OR weight gaining >0.45kg/week for 2+ weeks |
| **DELOAD** | Sleep <6h average, energy ≤2/5, workouts consistently incomplete, joint soreness reported |

---

## Non-Goals (MVP)

- No meal tracking integration (user self-reports)
- No wearable/health app sync
- No social features
- No paid subscription / billing
- No advanced periodization
- No sport-specific programming
- No Kaggle notebook runtime

---

## Future Roadmap (Post-MVP)

- Intermediate/advanced progression models
- Integration with MyFitnessPal / Cronometer export
- Photo progress tracking
- Multiple user profiles
- Export to PDF / weekly report email
