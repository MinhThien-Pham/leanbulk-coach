import React, { useState, useEffect } from 'react';
import { listProfiles, getLatestNutritionTarget, suggestMeals, getMealLogs } from '../api/client';

export default function MealHelperPanel({ initialUserId }) {
  const [profiles, setProfiles] = useState([]);
  const [userId, setUserId] = useState(initialUserId || '');
  const [targets, setTargets] = useState({ calorie_target: 2500, protein_target: 150 });
  
  // Consumed & Remaining Macros
  const [consumedKcal, setConsumedKcal] = useState(1800);
  const [consumedProtein, setConsumedProtein] = useState(110);
  const [remainingKcal, setRemainingKcal] = useState(700);
  const [remainingProtein, setRemainingProtein] = useState(40);

  const [equipment, setEquipment] = useState(['stove', 'microwave']);
  const [dietaryPrefs, setDietaryPrefs] = useState([]);
  const [nSuggestions, setNSuggestions] = useState(3);
  
  const [suggestions, setSuggestions] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    listProfiles()
      .then(list => {
        setProfiles(list);
        if (list.length > 0 && !userId) {
          setUserId(list[0].id);
          loadTargetAndLogs(list[0].id);
        }
      })
      .catch(err => console.error(err));
  }, []);

  useEffect(() => {
    if (initialUserId) {
      setUserId(initialUserId);
      loadTargetAndLogs(initialUserId);
    }
  }, [initialUserId]);

  const loadTargetAndLogs = async (uid) => {
    if (!uid) return;
    try {
      const uId = parseInt(uid);
      // Fetch latest target
      const target = await getLatestNutritionTarget(uId).catch(() => null);
      if (target) {
        setTargets({
          calorie_target: target.target_kcal,
          protein_target: target.protein_g
        });
      }

      // Fetch today's meal logs to calculate consumed
      const meals = await getMealLogs(uId).catch(() => []);
      const todayStr = new Date().toDateString();
      const todaysMeals = meals.filter(m => new Date(m.logged_at).toDateString() === todayStr);
      
      const sumKcal = todaysMeals.reduce((acc, x) => acc + x.kcal, 0);
      const sumProtein = todaysMeals.reduce((acc, x) => acc + x.protein_g, 0);
      
      setConsumedKcal(sumKcal);
      setConsumedProtein(sumProtein);

      // Compute remaining
      const remKcal = Math.max((target?.target_kcal || 2500) - sumKcal, 0);
      const remProt = Math.max((target?.protein_g || 150) - sumProtein, 0);
      setRemainingKcal(remKcal);
      setRemainingProtein(remProt);
    } catch (err) {
      console.error(err);
    }
  };

  const calculateRemaining = () => {
    const rKcal = Math.max(targets.calorie_target - consumedKcal, 0);
    const rProt = Math.max(targets.protein_target - consumedProtein, 0);
    setRemainingKcal(rKcal);
    setRemainingProtein(rProt);
  };

  const handleGetSuggestions = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuggestions(null);

    try {
      const payload = {
        target_kcal: parseInt(remainingKcal),
        target_protein_g: parseInt(remainingProtein),
        dietary_preferences: dietaryPrefs,
        available_equipment: equipment,
        n_suggestions: parseInt(nSuggestions),
      };

      const res = await suggestMeals(payload);
      setSuggestions(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const toggleEquipment = (item) => {
    if (equipment.includes(item)) {
      setEquipment(equipment.filter(x => x !== item));
    } else {
      setEquipment([...equipment, item]);
    }
  };

  const toggleDietary = (item) => {
    if (dietaryPrefs.includes(item)) {
      setDietaryPrefs(dietaryPrefs.filter(x => x !== item));
    } else {
      setDietaryPrefs([...dietaryPrefs, item]);
    }
  };

  return (
    <div className="card meal-helper-panel">
      <h2>Meal Suggestion Helper</h2>

      <div className="profile-selector-row">
        <label>
          Load Target for Profile:
          <select value={userId} onChange={e => {
            setUserId(e.target.value);
            loadTargetAndLogs(e.target.value);
          }}>
            <option value="">-- Choose Profile --</option>
            {profiles.map(p => (
              <option key={p.id} value={p.id}>
                {p.display_name || `User #${p.id}`}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="macro-calculator-section">
        <h4>Calculate Remaining Macros for Today</h4>
        <div className="macro-inputs-grid">
          <label>Target Daily Calories:
            <input type="number" value={targets.calorie_target} onChange={e => setTargets({...targets, calorie_target: parseInt(e.target.value)})} onBlur={calculateRemaining} />
          </label>
          <label>Target Daily Protein (g):
            <input type="number" value={targets.protein_target} onChange={e => setTargets({...targets, protein_target: parseInt(e.target.value)})} onBlur={calculateRemaining} />
          </label>
          <label>Consumed Calories Today:
            <input type="number" value={consumedKcal} onChange={e => setConsumedKcal(parseInt(e.target.value))} onBlur={calculateRemaining} />
          </label>
          <label>Consumed Protein Today (g):
            <input type="number" value={consumedProtein} onChange={e => setConsumedProtein(parseInt(e.target.value))} onBlur={calculateRemaining} />
          </label>
        </div>
        
        <div className="macro-remaining-banner">
          <span>Remaining Calories Needed: <strong>{remainingKcal} kcal</strong></span>
          <span>Remaining Protein Needed: <strong>{remainingProtein} g</strong></span>
        </div>
      </div>

      <form onSubmit={handleGetSuggestions}>
        <div className="form-grid">
          <label>Remaining Kcal Gap:
            <input type="number" value={remainingKcal} onChange={e => setRemainingKcal(parseInt(e.target.value))} required />
          </label>
          <label>Remaining Protein Gap (g):
            <input type="number" value={remainingProtein} onChange={e => setRemainingProtein(parseInt(e.target.value))} required />
          </label>
          <label>Number of suggestions:
            <input type="number" min="1" max="10" value={nSuggestions} onChange={e => setNSuggestions(parseInt(e.target.value))} />
          </label>
        </div>

        <div className="form-section">
          <h4>Kitchen Equipment Available:</h4>
          <div className="checkbox-group">
            {['stove', 'microwave', 'oven', 'blender', 'air_fryer', 'no_equipment'].map(eq => (
              <label key={eq} className="checkbox-label">
                <input type="checkbox" checked={equipment.includes(eq)} onChange={() => toggleEquipment(eq)} />
                {eq.replace('_', ' ')}
              </label>
            ))}
          </div>
        </div>

        <div className="form-section">
          <h4>Dietary Limitations:</h4>
          <div className="checkbox-group">
            {['vegetarian', 'vegan', 'dairy_free', 'no_fish', 'no_restrictions'].map(diet => (
              <label key={diet} className="checkbox-label">
                <input type="checkbox" checked={dietaryPrefs.includes(diet)} onChange={() => toggleDietary(diet)} />
                {diet.replace('_', ' ')}
              </label>
            ))}
          </div>
        </div>

        <button type="submit" disabled={loading} className="btn-primary">
          {loading ? 'Consulting meal generator...' : 'Get Meal Suggestions'}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      {suggestions && (
        <div className="result-block suggestions-block">
          <h3>Suggested Meals ({suggestions.suggestions?.length || 0})</h3>
          {suggestions.fallback_used && <p className="warning-banner">Warning: Showing backup fallback suggestions due to macro/diet constraints.</p>}
          <div className="suggestions-list">
            {suggestions.suggestions?.map((meal, idx) => (
              <div key={idx} className="suggestion-item">
                <h5>{meal.name}</h5>
                <div className="suggestion-macros">
                  <span>{meal.kcal} kcal</span>
                  <span>{meal.protein_g ?? meal.protein}g P</span>
                </div>
                {(meal.description || meal.recipe) && <p className="suggestion-recipe"><strong>Description:</strong> {meal.description || meal.recipe}</p>}
                {meal.equipment && <p className="suggestion-meta"><strong>Equipment:</strong> {meal.equipment.join(', ')}</p>}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
