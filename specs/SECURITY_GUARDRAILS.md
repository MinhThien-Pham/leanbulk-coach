# Security & Guardrails — LeanBulk Coach

**Version**: 2.0  
**Status**: Active

---

> [!IMPORTANT]
> **Medical Disclaimer**: LeanBulk Coach is a fitness coaching assistant and is NOT a medical application.
> It cannot and will not provide medical diagnoses, treat injuries, or replace professional medical advice.
> This disclaimer is present in the onboarding documentation and user guidelines.

---

## Guardrail Architecture

The current MVP enforces strict safety rules through a multi-layered local deterministic architecture. No live LLM or API keys are required for this setup.

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
│  Layer 2: backend/tools/safety_tools.py          │
│  • check_pain_flag() — runs before training      │
│  • check_rate_of_change() — runs before summary  │
│  • check_calorie_adjustment() — before targets   │
│  These are ALWAYS called, cannot be skipped.     │
└─────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────┐
│  Layer 3: Local Workflows & Summaries           │
│  • Integrates calculations and active warnings  │
│  • Compiles final coach next actions            │
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
| Calorie floor | < 1400 kcal/day | Clamp to 1400 |
| Calorie ceiling | > 6000 kcal/day | Clamp to 6000 |
| Max deficit | > 500 kcal/day | Block + redirect to safety boundaries |
| Max surplus | > 600 kcal/day | Block + redirect to safety boundaries |

### Rate of Change Safety

| Rule | Threshold | Response |
|---|---|---|
| Rapid weight gain | > 0.45 kg/week during bulk | Warning + reduce surplus |
| Rapid weight loss | > 0.9 kg/week during cut | Warning + reduce deficit |
| Waist creep | > 0.5 cm/week | Warning |
| Sustained waist creep | > 0.5 cm/week × 2 weeks | Warning + recommend adjusting intake |

### Training Safety

| Rule | Threshold | Response |
|---|---|---|
| Beginner training cap | > 4 days/week | Cap at 4, explain recovery importance |
| Pain flag | Any pain/injury keyword | Block training advice, redirect to healthcare provider |
| Medical request | Any diagnosis-seeking pattern | Hard refuse + disclaimer |

### Medical / Diagnosis Guardrails

**Trigger keywords** (any of these in user notes → immediate flag):
- pain, painful, hurts, hurting, sharp, stabbing
- torn, tear, hernia, strain, sprain, fracture, broken, dislocated
- swelling, bruise, popped, snap, grinding, clicking

**Medical request patterns** (regex):
- `do i have`, `am i sick`, `diagnose`, `medical condition`
- `what is wrong with`, `symptoms mean`

**Response when triggered**:
1. Flag status is set to `attention_needed` or `pain_flag` active.
2. The dashboard displays an alert warning directing the user to seek professional medical attention.
3. No progression or training advice is advanced.

---

## Input Validation Bounds (Pydantic Schema)

```python
age: int            # range 16–75
height_cm: float    # range 100–250
weight_kg: float    # range 35–250
waist_cm: float     # range 50–200
```

---

## Forbidden Outputs

The application must never output:
- A specific diagnosis (e.g., "you have a hernia")
- A recommendation to train through acute pain
- A calorie target below 1400 kcal/day
- A weekly weight loss goal > 1 kg/week
- A recommendation to take specific medications or supplements

---

## Testing Guardrails

All guardrail scenarios are validated via deterministic evaluation cases (see `backend/evals/runner.py`):
- **Case 2**: Extreme cut request is flagged and clamped.
- **Case 5**: Medical/injury question triggers a hard block.

Unit tests in `backend/tests/unit/test_safety_tools.py` cover:
- Pain keywords
- Medical request patterns
- Calorie bounds clamping
- Rate of change thresholds
- Training volume caps
