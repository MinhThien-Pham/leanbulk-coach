# Security & Guardrails — LeanBulk Coach

**Version**: 1.0  
**Status**: Active

---

> [!IMPORTANT]
> **Medical Disclaimer**: LeanBulk Coach is a fitness coaching assistant and is NOT a medical application.
> It cannot and will not provide medical diagnoses, treat injuries, or replace professional medical advice.
> This disclaimer must appear in every agent response. See "Mandatory Disclaimer" section below.

---

## Guardrail Architecture (5 Layers)

```
Request from user
      │
      ▼
┌─────────────────────────────────────────────────┐
│  Layer 1: Pydantic v2 Schema Validation          │
│  • Range checks on all numeric inputs            │
│  • Enum validation for categorical inputs        │
│  • Required field enforcement                    │
│  • Rejects malformed requests before any logic   │
└─────────────────────────────────────────────────┘
      │ (passes validation)
      ▼
┌─────────────────────────────────────────────────┐
│  Layer 2: Guardrail Middleware (FastAPI)          │
│  • Pre-request text scan (notes field)           │
│  • Flags extreme calorie requests immediately    │
│  • Adds safety context to agent invocation       │
└─────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────┐
│  Layer 3: safety_tools.py (Deterministic)        │
│  • check_pain_flag() — runs before training      │
│  • check_rate_of_change() — runs before decision │
│  • check_calorie_adjustment() — before targets   │
│  • check_training_volume() — before programming  │
│  These are ALWAYS called, cannot be skipped.     │
└─────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────┐
│  Layer 4: LLM System Prompt Guardrails           │
│  • Injected into root agent system prompt        │
│  • Instructs model to refuse medical diagnoses   │
│  • Prohibits extreme recommendations             │
│  • Requires disclaimer in every response         │
└─────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────┐
│  Layer 5: Post-Output Validation                 │
│  • Checks final JSON for required fields         │
│  • Verifies disclaimer is present                │
│  • Verifies calorie target within bounds         │
│  • Verifies no forbidden content in coach_msg    │
└─────────────────────────────────────────────────┘
      │
      ▼
   Response to user
```

---

## Specific Guardrail Rules

### Nutrition Safety

| Rule | Threshold | Response |
|---|---|---|
| Calorie floor | < 1400 kcal/day | Hard block; clamp to 1400 |
| Calorie ceiling | > 6000 kcal/day | Hard block; clamp to 6000 |
| Max deficit | > 500 kcal/day | Block + redirect to 200–300 kcal deficit |
| Max surplus | > 600 kcal/day | Block + redirect to 200–300 kcal surplus |

### Rate of Change Safety

| Rule | Threshold | Response |
|---|---|---|
| Rapid weight gain | > 0.45 kg/week during bulk | Warning + reduce surplus |
| Rapid weight loss | > 0.9 kg/week during cut | Warning + reduce deficit |
| Waist creep | > 0.5 cm/week | Warning + consider mini-cut |
| Sustained waist creep | > 0.5 cm/week × 2 weeks | Strong warning + trigger MINI_CUT decision |

### Training Safety

| Rule | Threshold | Response |
|---|---|---|
| Beginner training cap | > 4 days/week | Cap at 4, explain recovery importance |
| Intermediate cap | > 5 days/week | Cap at 5 |
| Pain flag | Any pain/injury keyword | Block training advice, redirect to healthcare provider |
| Medical request | Any diagnosis-seeking pattern | Hard refuse + disclaimer |
| Extreme fatigue | Energy ≤ 2/5 + sleep < 6h | Trigger DELOAD evaluation |

### Medical / Diagnosis Guardrails

**Trigger keywords** (any of these in user notes → immediate flag):
- pain, painful, hurts, hurting, sharp, stabbing
- torn, tear, hernia, strain, sprain, fracture, broken, dislocated
- swelling, bruise, popped, snap, grinding, clicking

**Medical request patterns** (regex):
- `do i have`, `am i sick`, `diagnose`, `medical condition`
- `what is wrong with`, `symptoms mean`

**Response when triggered**:
1. Set `decision = GUARDRAIL_TRIGGERED`
2. Set `safety_warning` to the standard medical disclaimer (see below)
3. Do NOT provide any exercise or nutrition advice for the affected area
4. Recommend consulting a healthcare professional

---

## Mandatory Medical Disclaimer

The following text MUST appear in every agent response, in the `medical_disclaimer` field:

> "⚠️ Important: LeanBulk Coach provides general fitness guidance only and is not a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare professional before making significant changes to your diet or exercise program, especially if you have any pre-existing health conditions or injuries."

---

## API Key Security

| Item | Rule |
|---|---|
| `GEMINI_API_KEY` | In `.env` only. Never in source code, logs, or version control. |
| `API_KEY` (backend) | In `.env` only. Single shared key for local demo. |
| `.env` | Listed in `.gitignore`. Never committed. |
| `.env.example` | Committed with placeholder values only. |
| Logging | Log level `INFO` by default. Never log API key values. |
| Model name | From `GEMINI_MODEL` env var. Never hardcoded. |

---

## Input Validation Bounds (Pydantic Schema)

```python
age: int          # range 16–75
height_cm: float  # range 100–250
weight_kg: float  # range 35–250
waist_cm: float   # range 50–200
training_days: int  # range 1–6
avg_calories: int   # range 0–10000
avg_protein_g: int  # range 0–500
avg_sleep_h: float  # range 0–14
energy_level: int   # range 1–5
```

---

## Forbidden Outputs

The agent MUST NEVER output:
- A specific diagnosis (e.g., "you have a hernia")
- A recommendation to train through acute pain
- A calorie target below 1400 kcal/day
- A weekly weight loss goal > 1 kg/week
- A recommendation to take specific medications or supplements (beyond protein powder)
- Claims that a specific diet will cure a medical condition

---

## Testing Guardrails

All guardrail scenarios have dedicated eval cases (see `specs/EVAL_PLAN.md`):
- **Case 2**: Extreme cut request → blocked
- **Case 5**: Medical/injury question → hard refuse

Unit tests in `backend/tests/unit/test_safety_tools.py` cover:
- All pain keywords
- All medical regex patterns
- Calorie adjustment clamping
- Rate of change thresholds
- Training volume caps

---

## Limitations and Disclosures

The following limitations are by design and must be documented in the README:

1. This tool is not approved for use by individuals with eating disorders, diagnosed health conditions, or who are under medical supervision for weight management.
2. Calorie and macro targets are estimates based on population averages. Individual metabolic response varies.
3. The agent cannot verify self-reported data and relies on honest user input.
4. No emergency escalation is provided. If you are experiencing a medical emergency, call emergency services immediately.
