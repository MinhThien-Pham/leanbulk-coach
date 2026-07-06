"""
meal_tools.py — Deterministic meal suggestion tools for LeanBulk Coach.

All functions are pure (no I/O, no LLM calls, no side effects).
Suggests simple, high-protein meals that help fill a remaining macro gap.
"""

from typing import Optional

# ---------------------------------------------------------------------------
# Meal Library
# ---------------------------------------------------------------------------
# Each meal: name, kcal, protein_g, tags (dietary/equipment/meal type),
#            equipment needed, description.
# Tags used for filtering: dietary restrictions + equipment.

MEAL_LIBRARY: list[dict] = [
    {
        "name": "Greek Yogurt Protein Bowl",
        "kcal": 380,
        "protein_g": 35,
        "tags": ["no_cook", "dairy", "high_protein", "breakfast", "vegetarian", "snack"],
        "equipment": ["none"],
        "description": "200g Greek yogurt, 30g whey protein mixed in, mixed berries, 1 tbsp honey, 30g low-sugar granola.",
    },
    {
        "name": "Chicken Rice Bowl",
        "kcal": 550,
        "protein_g": 45,
        "tags": ["poultry", "high_protein", "lunch", "dinner", "meal_prep"],
        "equipment": ["stove", "oven", "microwave"],
        "description": "175g chicken breast, 150g cooked white rice, mixed vegetables, soy sauce, sesame oil.",
    },
    {
        "name": "Egg and Oat Breakfast",
        "kcal": 420,
        "protein_g": 28,
        "tags": ["eggs", "vegetarian", "breakfast", "budget"],
        "equipment": ["stove", "microwave"],
        "description": "3 whole eggs scrambled, 80g oats made with 250ml milk, 1 banana.",
    },
    {
        "name": "Tuna Pasta",
        "kcal": 480,
        "protein_g": 38,
        "tags": ["fish", "high_protein", "lunch", "dinner", "budget"],
        "equipment": ["stove"],
        "description": "1 can tuna (in water), 100g dry pasta, olive oil, cherry tomatoes, dried herbs.",
    },
    {
        "name": "Cottage Cheese and Fruit",
        "kcal": 300,
        "protein_g": 25,
        "tags": ["no_cook", "dairy", "vegetarian", "snack", "high_protein"],
        "equipment": ["none"],
        "description": "200g low-fat cottage cheese, mixed fruit, 1 tbsp nut butter.",
    },
    {
        "name": "Ground Turkey Stir Fry",
        "kcal": 520,
        "protein_g": 42,
        "tags": ["poultry", "high_protein", "dinner", "lunch", "meal_prep"],
        "equipment": ["stove"],
        "description": "200g ground turkey, mixed bell peppers and broccoli, 100g cooked rice, light teriyaki sauce.",
    },
    {
        "name": "Protein Smoothie",
        "kcal": 350,
        "protein_g": 30,
        "tags": ["no_cook", "dairy", "vegetarian", "breakfast", "snack", "high_protein"],
        "equipment": ["blender"],
        "description": "1 scoop whey protein, 1 banana, 250ml semi-skimmed milk, 1 tbsp peanut butter, ice.",
    },
    {
        "name": "Salmon with Sweet Potato",
        "kcal": 580,
        "protein_g": 44,
        "tags": ["fish", "high_protein", "dinner"],
        "equipment": ["oven", "stove"],
        "description": "175g salmon fillet, 200g sweet potato, asparagus, olive oil, lemon.",
    },
    {
        "name": "Lentil and Vegetable Curry",
        "kcal": 450,
        "protein_g": 22,
        "tags": ["vegan", "vegetarian", "budget", "dinner", "lunch"],
        "equipment": ["stove"],
        "description": "200g red lentils, mixed vegetables, 1 can coconut milk, curry spices, 100g cooked rice.",
    },
    {
        "name": "Ham and Cheese Omelette",
        "kcal": 390,
        "protein_g": 32,
        "tags": ["eggs", "breakfast", "lunch", "quick", "pork", "meat"],
        "equipment": ["stove"],
        "description": "4 whole eggs, 50g sliced ham, 30g cheddar cheese, handful spinach, salt and pepper.",
    },
    {
        "name": "Beef and Vegetable Stir Fry",
        "kcal": 530,
        "protein_g": 40,
        "tags": ["beef", "high_protein", "dinner", "lunch"],
        "equipment": ["stove"],
        "description": "175g lean beef strips, mixed vegetables, 100g cooked rice, soy sauce, garlic.",
    },
    {
        "name": "Canned Sardines on Toast",
        "kcal": 340,
        "protein_g": 28,
        "tags": ["fish", "budget", "no_cook", "lunch", "snack"],
        "equipment": ["none", "toaster"],
        "description": "1 tin sardines in olive oil, 2 slices wholegrain toast, sliced tomato, black pepper.",
    },
    {
        "name": "Tofu and Vegetable Scramble",
        "kcal": 380,
        "protein_g": 24,
        "tags": ["vegan", "vegetarian", "breakfast", "lunch", "dairy_free"],
        "equipment": ["stove"],
        "description": "200g firm tofu crumbled, mixed vegetables, nutritional yeast, turmeric, soy sauce.",
    },
    {
        "name": "Protein Overnight Oats",
        "kcal": 420,
        "protein_g": 32,
        "tags": ["vegetarian", "dairy", "breakfast", "meal_prep", "no_cook"],
        "equipment": ["none"],
        "description": "80g rolled oats, 200ml milk, 1 scoop whey protein, 1 tbsp chia seeds, mixed berries. Prep overnight.",
    },
    {
        "name": "Edamame and Rice Bowl",
        "kcal": 460,
        "protein_g": 26,
        "tags": ["vegan", "vegetarian", "dairy_free", "lunch", "dinner"],
        "equipment": ["stove", "microwave"],
        "description": "200g edamame (shelled), 150g cooked brown rice, sliced avocado, soy sauce, sesame seeds.",
    },
]


# ---------------------------------------------------------------------------
# Dietary exclusion mapping
# ---------------------------------------------------------------------------

# Note: Specific meat-type tags like 'pork' are intentionally kept alongside the 
# general 'meat' tag. This is because exclusion filters check for exact tags and 
# lack hierarchical awareness (e.g., 'no_pork' strictly relies on the 'pork' tag).
PREFERENCE_EXCLUSIONS: dict[str, set[str]] = {
    "vegetarian": {"poultry", "fish", "beef", "pork", "meat"},
    "vegan": {"poultry", "fish", "beef", "pork", "meat", "dairy", "eggs"},
    "dairy_free": {"dairy"},
    "no_fish": {"fish"},
    "no_pork": {"pork"},
}


# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------

def suggest_meals(
    remaining_kcal: float,
    remaining_protein_g: float,
    dietary_preferences: Optional[list[str]] = None,
    equipment_available: Optional[list[str]] = None,
    n_suggestions: int = 3,
) -> dict:
    """Suggest N meals that help fill a remaining daily calorie/protein gap.

    Filters by dietary preferences and available cooking equipment.
    Ranks by proximity to the remaining targets using a simple scoring
    function that prioritises protein match and penalises large overshoots.

    Args:
        remaining_kcal: Remaining daily calorie budget to fill (kcal).
        remaining_protein_g: Remaining daily protein target to fill (g).
        dietary_preferences: List of preference strings from the user profile.
            Supported: 'vegetarian', 'vegan', 'dairy_free', 'no_fish', 'no_pork'.
            Pass None or empty list for no restrictions.
        equipment_available: List of available cooking equipment.
            Supported values: 'stove', 'oven', 'microwave', 'blender', 'toaster',
            'none' (for no-cook options).
            Pass None to assume all equipment available.
        n_suggestions: Number of meal suggestions to return (default 3).

    Returns:
        dict with keys:
            - suggestions (list[dict]): Top N meal dicts from MEAL_LIBRARY.
            - total_suggested_kcal (int): Sum of all suggested meals' kcal.
            - total_suggested_protein_g (int): Sum of all suggested meals' protein.
            - remaining_kcal (float): Input remaining calories (for context).
            - remaining_protein_g (float): Input remaining protein (for context).
            - n_returned (int): Actual number of suggestions returned.
            - fallback_used (bool): True if filters were relaxed due to no matches.
    """
    preferences = [p.strip().lower() for p in (dietary_preferences or [])]
    # If no equipment specified, assume a fully-equipped kitchen
    equipment = (
        {e.strip().lower() for e in equipment_available}
        if equipment_available is not None
        else {"stove", "oven", "microwave", "blender", "toaster", "none"}
    )

    # Build set of excluded tags from dietary preferences
    excluded_tags: set[str] = set()
    for pref in preferences:
        excluded_tags.update(PREFERENCE_EXCLUSIONS.get(pref, set()))

    def has_suitable_equipment(meal: dict) -> bool:
        """Return True if any of the meal's equipment requirements are available."""
        return any(e in equipment for e in meal["equipment"])

    def meets_dietary_requirements(meal: dict) -> bool:
        """Return True if the meal has no excluded tags."""
        return not any(tag in excluded_tags for tag in meal["tags"])

    # Filter candidates
    candidates = [
        m for m in MEAL_LIBRARY
        if has_suitable_equipment(m) and meets_dietary_requirements(m)
    ]

    fallback_used = False
    if not candidates:
        # Relax all filters and use full library
        candidates = list(MEAL_LIBRARY)
        fallback_used = True

    def score(meal: dict) -> float:
        """Lower score = better match to remaining targets."""
        kcal_diff = abs(meal["kcal"] - remaining_kcal)
        protein_diff = abs(meal["protein_g"] - remaining_protein_g)
        # Heavily penalise meals that overshoot calories by > 50%
        overshoot_penalty = 0.0
        if remaining_kcal > 0 and meal["kcal"] > remaining_kcal * 1.5:
            overshoot_penalty = 800.0
        # Protein is more important for this context — weight it more
        return kcal_diff + protein_diff * 2.5 + overshoot_penalty

    ranked = sorted(candidates, key=score)
    suggestions = ranked[:n_suggestions]

    return {
        "suggestions": suggestions,
        "total_suggested_kcal": sum(m["kcal"] for m in suggestions),
        "total_suggested_protein_g": sum(m["protein_g"] for m in suggestions),
        "remaining_kcal": remaining_kcal,
        "remaining_protein_g": remaining_protein_g,
        "n_returned": len(suggestions),
        "fallback_used": fallback_used,
    }
