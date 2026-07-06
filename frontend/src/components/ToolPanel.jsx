import React, { useState } from 'react';
import { calculateCalories, calculateProtein, suggestMeals } from '../api/client';

export default function ToolPanel() {
  const [calorieForm, setCalorieForm] = useState({
    weight_kg: 75,
    height_cm: 180,
    age: 25,
    sex: "male",
    activity_level: "moderately_active",
    goal: "lean_bulk",
  });
  const [calorieResult, setCalorieResult] = useState(null);

  const [proteinForm, setProteinForm] = useState({
    weight_kg: 75,
    goal: "lean_bulk",
  });
  const [proteinResult, setProteinResult] = useState(null);

  const [mealsForm, setMealsForm] = useState({
    target_kcal: 600,
    target_protein_g: 40,
    dietary_preferences: "",
  });
  const [mealsResult, setMealsResult] = useState(null);

  const handleCalorieSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await calculateCalories(calorieForm);
      setCalorieResult(res);
    } catch (err) {
      alert("Error: " + err.message);
    }
  };

  const handleProteinSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await calculateProtein(proteinForm);
      setProteinResult(res);
    } catch (err) {
      alert("Error: " + err.message);
    }
  };

  const handleMealsSubmit = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        ...mealsForm,
        dietary_preferences: mealsForm.dietary_preferences ? mealsForm.dietary_preferences.split(',').map(s => s.trim()) : [],
      };
      const res = await suggestMeals(payload);
      setMealsResult(res);
    } catch (err) {
      alert("Error: " + err.message);
    }
  };

  return (
    <div className="card tool-panel">
      <h2>Deterministic Tools</h2>
      
      <div className="tool-section">
        <h3>Calorie Target</h3>
        <form onSubmit={handleCalorieSubmit}>
          <label>Weight (kg): <input type="number" value={calorieForm.weight_kg} onChange={e => setCalorieForm({...calorieForm, weight_kg: parseFloat(e.target.value)})} /></label>
          <label>Height (cm): <input type="number" value={calorieForm.height_cm} onChange={e => setCalorieForm({...calorieForm, height_cm: parseFloat(e.target.value)})} /></label>
          <label>Age: <input type="number" value={calorieForm.age} onChange={e => setCalorieForm({...calorieForm, age: parseInt(e.target.value)})} /></label>
          <label>Sex: 
            <select value={calorieForm.sex} onChange={e => setCalorieForm({...calorieForm, sex: e.target.value})}>
              <option value="male">Male</option>
              <option value="female">Female</option>
            </select>
          </label>
          <button type="submit">Calculate Calories</button>
        </form>
        {calorieResult && <pre>{JSON.stringify(calorieResult, null, 2)}</pre>}
      </div>

      <div className="tool-section">
        <h3>Protein Target</h3>
        <form onSubmit={handleProteinSubmit}>
          <label>Weight (kg): <input type="number" value={proteinForm.weight_kg} onChange={e => setProteinForm({...proteinForm, weight_kg: parseFloat(e.target.value)})} /></label>
          <button type="submit">Calculate Protein</button>
        </form>
        {proteinResult && <pre>{JSON.stringify(proteinResult, null, 2)}</pre>}
      </div>

      <div className="tool-section">
        <h3>Meal Suggestions</h3>
        <form onSubmit={handleMealsSubmit}>
          <label>Target Kcal: <input type="number" value={mealsForm.target_kcal} onChange={e => setMealsForm({...mealsForm, target_kcal: parseInt(e.target.value)})} /></label>
          <label>Target Protein (g): <input type="number" value={mealsForm.target_protein_g} onChange={e => setMealsForm({...mealsForm, target_protein_g: parseInt(e.target.value)})} /></label>
          <label>Dietary Preferences (comma-separated): <input type="text" value={mealsForm.dietary_preferences} onChange={e => setMealsForm({...mealsForm, dietary_preferences: e.target.value})} /></label>
          <button type="submit">Suggest Meals</button>
        </form>
        {mealsResult && <pre>{JSON.stringify(mealsResult, null, 2)}</pre>}
      </div>
    </div>
  );
}
