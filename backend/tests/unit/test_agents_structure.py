from backend.agents.root_agent import get_root_agent_config, get_sub_agents

def test_root_agent_config():
    root = get_root_agent_config()
    assert root.name == "LeanBulkCoachAgent"
    assert "orchestrate" in root.purpose.lower()

def test_sub_agents_exist():
    subs = get_sub_agents()
    assert len(subs) == 5
    
    names = [sub.name for sub in subs]
    assert "IntakeAgent" in names
    assert "NutritionAgent" in names
    assert "TrainingAgent" in names
    assert "ProgressAgent" in names
    assert "SafetyAgent" in names
    
    # Check uniqueness
    assert len(set(names)) == 5
    
    # Root references them
    root = get_root_agent_config()
    assert all(name in root.metadata["sub_agents"] for name in names)

def test_safety_agent_override_capability():
    subs = get_sub_agents()
    safety = next(s for s in subs if s.name == "SafetyAgent")
    
    assert safety.metadata.get("is_safety_agent") is True
    assert "safety_override" in safety.metadata.get("capabilities", [])
    assert "override" in safety.instruction.lower()

def test_nutrition_agent_no_guessing():
    subs = get_sub_agents()
    nutrition = next(s for s in subs if s.name == "NutritionAgent")
    
    # Instruction must prohibit estimating calories without tools
    assert "do not estimate" in nutrition.instruction.lower()
    assert "tools" in nutrition.instruction.lower()
