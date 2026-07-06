from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

def now_utc():
    return datetime.now(timezone.utc)

class UserProfile(Base):
    __tablename__ = 'user_profiles'
    
    id = Column(Integer, primary_key=True)
    display_name = Column(String, nullable=True)
    sex = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    height_cm = Column(Float, nullable=False)
    goal = Column(String, nullable=False, default="lean_bulk")
    target_weight_kg = Column(Float, nullable=True)
    created_at = Column(DateTime, default=now_utc)
    updated_at = Column(DateTime, default=now_utc, onupdate=now_utc)
    
    # Relationships
    body_metrics = relationship("BodyMetricLog", back_populates="user")
    workout_sets = relationship("WorkoutSetLog", back_populates="user")
    nutrition_targets = relationship("NutritionTargetLog", back_populates="user")
    meal_logs = relationship("MealLog", back_populates="user")
    safety_flags = relationship("SafetyFlagLog", back_populates="user")

class BodyMetricLog(Base):
    __tablename__ = 'body_metric_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user_profiles.id'), nullable=False)
    logged_at = Column(DateTime, default=now_utc, nullable=False)
    weight_kg = Column(Float, nullable=False)
    waist_cm = Column(Float, nullable=True)
    notes = Column(String, nullable=True)
    
    user = relationship("UserProfile", back_populates="body_metrics")

class WorkoutSetLog(Base):
    __tablename__ = 'workout_set_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user_profiles.id'), nullable=False)
    logged_at = Column(DateTime, default=now_utc, nullable=False)
    exercise_name = Column(String, nullable=False)
    muscle_group = Column(String, nullable=True)
    weight_kg = Column(Float, nullable=True)
    reps = Column(Integer, nullable=False)
    rir = Column(Float, nullable=True)
    set_number = Column(Integer, nullable=True)
    notes = Column(String, nullable=True)
    
    user = relationship("UserProfile", back_populates="workout_sets")

class NutritionTargetLog(Base):
    __tablename__ = 'nutrition_target_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user_profiles.id'), nullable=False)
    logged_at = Column(DateTime, default=now_utc, nullable=False)
    target_kcal = Column(Integer, nullable=False)
    protein_g = Column(Integer, nullable=False)
    carbs_g = Column(Integer, nullable=True)
    fat_g = Column(Integer, nullable=True)
    goal = Column(String, nullable=False)
    
    user = relationship("UserProfile", back_populates="nutrition_targets")

class MealLog(Base):
    __tablename__ = 'meal_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user_profiles.id'), nullable=False)
    logged_at = Column(DateTime, default=now_utc, nullable=False)
    meal_name = Column(String, nullable=False)
    kcal = Column(Integer, nullable=False)
    protein_g = Column(Integer, nullable=False)
    carbs_g = Column(Integer, nullable=True)
    fat_g = Column(Integer, nullable=True)
    notes = Column(String, nullable=True)
    
    user = relationship("UserProfile", back_populates="meal_logs")

class SafetyFlagLog(Base):
    __tablename__ = 'safety_flag_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user_profiles.id'), nullable=False)
    logged_at = Column(DateTime, default=now_utc, nullable=False)
    flag_type = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    message = Column(String, nullable=False)
    resolved = Column(Boolean, default=False, nullable=False)
    
    user = relationship("UserProfile", back_populates="safety_flags")
