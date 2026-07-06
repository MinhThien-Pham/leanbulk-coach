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
