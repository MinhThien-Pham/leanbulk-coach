---
name: lean-bulk-coaching
description: >
  Teaches the LeanBulk Coaching workflow for skinny-fat beginners.
  Triggers when the agent is handling a fitness coaching task involving
  body composition decisions, lean bulk vs cut decisions, weekly check-in
  analysis, training progression, or meal suggestions for beginners.
---

# Lean Bulk Coaching Skill

This skill defines the complete repeatable coaching workflow for LeanBulk Coach.
The agent MUST follow this workflow for every weekly check-in session.

## Scope

This skill applies to skinny-fat beginners (0–12 months consistent training) who are
making weekly decisions about their body composition strategy.

**Not in scope**: Medical advice, injury treatment, advanced periodization, sport-specific programming.

---

## Coaching Philosophy

Skinny-fat beginners occupy a unique body composition zone: normal BMI but high body fat
percentage and low muscle mass simultaneously. Generic "just bulk" or "just cut" advice
fails them because:

- Bulking without monitoring leads to excess fat gain and frustration.
- Aggressive cutting depletes the limited muscle they have.
- The goal is **gradual body recomposition**: slow, conservative lean bulk phases
  punctuated by brief mini-cuts when fat accumulation is detected.

Key principles:
1. **Data > feelings**: weekly weight average and waist measurement are the primary signals.
2. **Conservative adjustments**: ±200–300 kcal from TDEE, never extreme.
3. **Safety first**: guardrail tools always run before any decision or training advice.
4. **Encourage consistency**: adherence to the plan matters more than perfection.

---

## The 4-Decision Taxonomy

Every coaching session must produce exactly one of these decisions:

### LEAN_BULK_CONTINUE
**Meaning**: Current lean bulk is working. Stay the course.  
**Trigger conditions** (ALL must be met):
- Weekly weight gain ≤ 0.45 kg
- Waist stable or decreasing (delta ≤ +0.2 cm)
- Overall adherence ≥ 70%
- No pain or safety flags
- Strength progressing or stable

**Calorie adjustment**: ±0 (maintain current target)  
**Protein adjustment**: Maintain current target  

---

### LEAN_BULK_START
**Meaning**: New user or returning from maintenance. Begin a lean bulk phase.  
**Trigger conditions**:
- First check-in OR returning from deload/maintenance
- No acute pain or injury flags
- Waist within acceptable range for the user

**Calorie adjustment**: TDEE + 200–250 kcal (conservative beginner surplus)  
**Protein target**: 0.82g per lb bodyweight  

---

### MAINTAIN
**Meaning**: Hold current weight. No surplus or deficit.  
**Trigger conditions** (any):
- Signals are ambiguous (some positive, some negative)
- Adherence is low (< 70%) — fix compliance before adding more food
- Sleep is consistently < 6.5h — sleep is prerequisite for body composition change
- User is stressed, travelling, or recovering from illness
- Weight is stable and waist is stable — user may not be ready for a phase change

**Calorie adjustment**: ±0 from TDEE (or very small nudge of ±50 kcal)  

---

### MINI_CUT
**Meaning**: Brief fat-loss phase (4–8 weeks max) to reduce waist before resuming bulk.  
**Trigger conditions** (any):
- Waist increasing > 0.5 cm/week sustained for ≥ 1 week
- Weight gaining > 0.45 kg/week despite correct food intake (excess fat signal)
- Calorie adherence is very high but waist is creeping
- User explicitly requests a brief cut (validate it's appropriate)

**Calorie adjustment**: TDEE - 250–300 kcal (never > -500 kcal/day)  
**Duration**: 4–8 weeks, then re-evaluate  

---

### DELOAD
**Meaning**: Reduce training volume and intensity for 1 week to allow recovery.  
**Trigger conditions** (any combination):
- Average sleep < 6h for the check-in week
- Energy/recovery level ≤ 2/5 (self-reported)
- Workouts completed < 50% of planned for 2+ consecutive weeks
- Strength stalled or declining for 2+ consecutive weeks
- Joint soreness or fatigue mentioned in notes (after `check_pain_flag()` confirms non-injury)
- Illness or travel reported

**Training adjustment**: 50% of normal volume, same frequency, light weights, focus on form  
**Calorie adjustment**: Maintain TDEE (do not cut during deload)  

---

## Step-by-Step Coaching Workflow

Every weekly check-in MUST follow this exact pipeline:

```
Step 1: HYDRATE USER PROFILE
  → Call IntakeAgent (or MCP db_query_tool to load profile)
  → Compute/verify TDEE using calorie_tools.calc_tdee()
  → Compute/verify protein target using protein_tools.calc_protein_target()

Step 2: ANALYSE TRENDS
  → Call trend_tools.weight_trend(current_week, previous_week)
  → Call trend_tools.waist_trend(current_waist, previous_waist)
  → Call trend_tools.adherence_score(actual vs targets)
  → Call MCP db_query_tool for previous week's data if not in session

Step 3: SAFETY CHECKS (MANDATORY — cannot be skipped)
  → Call safety_tools.check_pain_flag(user_notes)
      IF pain_detected OR medical_request_detected:
          → Set decision = GUARDRAIL_TRIGGERED
          → Include medical disclaimer
          → STOP. Do not proceed to Step 4 or 5.
  → Call safety_tools.check_rate_of_change(weight_delta, waist_delta, goal)
  → Call safety_tools.check_calorie_adjustment(requested_adjustment, goal)

Step 4: DECISION
  → Call MCP rules_lookup_tool(scenario) to fetch relevant coaching rules
  → Apply the 4-decision taxonomy (above) using all tool outputs
  → Compute new calorie target with calorie_tools.calc_calorie_target()
  → Set protein target with protein_tools.calc_protein_target()

Step 5: TRAINING (parallel with Step 5b)
  → If DELOAD: call progression_tools.suggest_weekly_progression(deload_mode=True)
  → If other: call progression_tools.suggest_weekly_progression(deload_mode=False)

Step 5b: MEAL SUGGESTION (parallel with Step 5a)
  → Call meal_tools.suggest_meals() with remaining macro gap + preferences

Step 6: ASSEMBLE RESPONSE
  → Combine all tool outputs into structured coach response
  → Write coach_message (warm, encouraging, ≤3 sentences, LLM-generated)
  → Append medical_disclaimer (mandatory, fixed text — see SECURITY_GUARDRAILS.md)
  → Persist decision to database
```

---

## Output Format

Every coaching response MUST contain these fields:

```json
{
  "current_status": "string — plain English summary of this week's data",
  "decision": "LEAN_BULK_CONTINUE | LEAN_BULK_START | MAINTAIN | MINI_CUT | DELOAD | GUARDRAIL_TRIGGERED",
  "decision_reasoning": "string — 1-3 sentences explaining the decision",
  "calorie_target": 2900,
  "protein_target": 160,
  "training_recommendation": "string — progression note or deload protocol",
  "meal_suggestions": [...],
  "safety_warning": "string — empty if no flag, populated if guardrail triggered",
  "coach_message": "string — warm 2-3 sentence motivating message",
  "medical_disclaimer": "⚠️ Important: LeanBulk Coach provides general fitness guidance only..."
}
```

---

## Tone Guidelines for Coach Messages

- **Warm and encouraging**, never clinical or robotic.
- **Evidence-based and honest**: if things aren't going well, say so kindly.
- **Action-oriented**: always end with a clear, specific next step.
- **Never**: use medical language, diagnose, shame, or create urgency/fear.
- **Length**: 2–3 sentences maximum. No bullet points in the coach message.

Examples:
- ✅ "Great consistency this week — your weight trend is right on target. Keep hitting those protein goals and let's push the squat up to 62.5kg next session. See you next check-in!"
- ✅ "Your waist has crept up a little, so let's dial back the calories slightly this week. This is completely normal — it's just your body's signal to adjust. Stay consistent with training and you'll be back on track."
- ❌ "You need to lose weight. Cut your calories by 1000 immediately." (Never say this)

---

## References

- [Skinny-Fat Protocols](references/skinny_fat_protocols.md) — Evidence base for thresholds and decision logic
- [Guardrail Rules](references/guardrail_rules.md) — Complete list of safety blocks and triggers
