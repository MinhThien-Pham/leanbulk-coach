from pydantic import BaseModel, Field
from typing import Optional

class HealthResponse(BaseModel):
    status: str
    live_llm_calls: bool
    service: str
    version: str

class CalorieTargetRequest(BaseModel):
    weight_kg: float
    height_cm: float
    age: int
    sex: str
    activity_level: str = "moderately_active"
    goal: str = "lean_bulk"

class CalorieTargetResponse(BaseModel):
    bmr: int
    tdee: int
    activity_level: str
    target_kcal: int
    adjustment_kcal: int
    goal: str
    clamped: bool

class ProteinTargetRequest(BaseModel):
    weight_kg: float
    goal: str = "lean_bulk"

class ProteinTargetResponse(BaseModel):
    protein_g: int
    protein_per_lb: float
    goal: str
    clamped: bool

class MealSuggestionRequest(BaseModel):
    target_kcal: int
    target_protein_g: int
    dietary_preferences: list[str] = Field(default_factory=list)
    available_equipment: list[str] = Field(default_factory=list)
    n_suggestions: int = 5

class MealSuggestionResponse(BaseModel):
    suggestions: list[dict]
    fallback_used: bool

class SummaryRequest(BaseModel):
    profile_context: dict = Field(default_factory=dict)
    latest_body_context: dict = Field(default_factory=dict)
    body_history_context: list[dict] = Field(default_factory=list)
    latest_nutrition_context: dict = Field(default_factory=dict)
    recent_workout_context: list[dict] = Field(default_factory=list)
    recent_meal_context: list[dict] = Field(default_factory=list)
    open_safety_context: list[dict] = Field(default_factory=list)
    progress_summary_context: dict = Field(default_factory=dict)

class SummaryResponse(BaseModel):
    user_name: Optional[str] = None
    goal: Optional[str] = None
    current_weight_kg: Optional[float] = None
    latest_waist_cm: Optional[float] = None
    calorie_target_kcal: Optional[int] = None
    protein_target_g: Optional[int] = None
    progress_status: str
    safety_status: str
    training_status: str
    nutrition_status: str
    next_actions: list[str]

class CreateUserProfileRequest(BaseModel):
    display_name: Optional[str] = None
    sex: str
    age: int
    height_cm: float
    goal: str = "lean_bulk"
    target_weight_kg: Optional[float] = None

class UserProfileResponse(BaseModel):
    id: int
    display_name: Optional[str] = None
    sex: str
    age: int
    height_cm: float
    goal: str
    target_weight_kg: Optional[float] = None

class BodyMetricLogRequest(BaseModel):
    user_id: int
    weight_kg: float
    waist_cm: Optional[float] = None
    notes: Optional[str] = None

class WorkoutSetLogRequest(BaseModel):
    user_id: int
    exercise_name: str
    reps: int
    weight_kg: Optional[float] = None
    rir: Optional[float] = None
    muscle_group: Optional[str] = None
    set_number: Optional[int] = None
    notes: Optional[str] = None

class NutritionTargetLogRequest(BaseModel):
    user_id: int
    target_kcal: int
    protein_g: int
    carbs_g: Optional[int] = None
    fat_g: Optional[int] = None
    goal: str = "lean_bulk"

class MealLogRequest(BaseModel):
    user_id: int
    meal_name: str
    kcal: int
    protein_g: int
    carbs_g: Optional[int] = None
    fat_g: Optional[int] = None
    notes: Optional[str] = None

class SafetyFlagRequest(BaseModel):
    user_id: int
    flag_type: str
    severity: str
    message: str

class EvalCaseSummary(BaseModel):
    id: str
    category: str
    description: str

class EvalListResponse(BaseModel):
    total: int
    cases: list[EvalCaseSummary]

class EvalSuiteResponse(BaseModel):
    total: int
    passed: int
    failed: int
    score: float
    results: list[dict]

class EvalReportSummary(BaseModel):
    total: int
    passed: int
    failed: int
    score: float

class EvalReportResponse(BaseModel):
    report: str
    summary: EvalReportSummary
