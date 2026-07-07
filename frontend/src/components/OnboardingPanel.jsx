import React, { useState } from 'react';
import { createProfile, calculateCalories, calculateProtein, logNutritionTarget, logBodyMetric } from '../api/client';

const formatEnumLabel = (val) => {
  if (!val) return '';
  const key = String(val).toLowerCase();
  const mapping = {
    'attention_needed': 'Attention Needed',
    'clear': 'Clear',
    'lean_bulk': 'Lean Bulk',
    'pain_flag': 'Pain Flag',
    'medium': 'Medium',
    'high': 'High',
    'low': 'Low',
    'maintain': 'Maintain',
    'mini_cut': 'Mini Cut'
  };
  return mapping[key] || val;
};

export default function OnboardingPanel({ onProfileCreated }) {
  const [form, setForm] = useState({
    display_name: '',
    sex: 'male',
    age: 25,
    height_cm: 180,
    weight_kg: 75,
    waist_cm: 80,
    goal: 'lean_bulk',
    target_weight_kg: '',
  });

  const [loading, setLoading] = useState(false);
  const [successData, setSuccessData] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccessData(null);

    // Frontend validation
    if (form.age < 16 || form.age > 75) {
      setError("Age must be between 16 and 75.");
      setLoading(false);
      return;
    }
    if (form.height_cm < 100 || form.height_cm > 250) {
      setError("Height must be between 100 and 250 cm.");
      setLoading(false);
      return;
    }
    if (form.weight_kg < 35 || form.weight_kg > 250) {
      setError("Weight must be between 35 and 250 kg.");
      setLoading(false);
      return;
    }
    if (form.waist_cm && (form.waist_cm < 50 || form.waist_cm > 200)) {
      setError("Waist must be between 50 and 200 cm.");
      setLoading(false);
      return;
    }

    try {
      // 1. Compute starting targets using tools first
      const kcalData = await calculateCalories({
        weight_kg: form.weight_kg,
        height_cm: form.height_cm,
        age: form.age,
        sex: form.sex,
        goal: form.goal,
        activity_level: "moderately_active",
      });

      const proteinData = await calculateProtein({
        weight_kg: form.weight_kg,
        goal: form.goal,
      });

      // 2. Create Profile only after calorie/protein calculation succeeds
      const payload = {
        display_name: form.display_name || undefined,
        sex: form.sex,
        age: parseInt(form.age),
        height_cm: parseFloat(form.height_cm),
        goal: form.goal,
        target_weight_kg: form.target_weight_kg ? parseFloat(form.target_weight_kg) : undefined,
      };

      const profile = await createProfile(payload);

      // 3. Save targets to nutrition log
      await logNutritionTarget({
        user_id: profile.id,
        target_kcal: kcalData.target_kcal,
        protein_g: proteinData.protein_g,
        goal: form.goal,
      });

      // 4. Save starting body metric (weight/waist)
      try {
        await logBodyMetric({
          user_id: profile.id,
          weight_kg: form.weight_kg,
          waist_cm: form.waist_cm ? parseFloat(form.waist_cm) : undefined,
          notes: "Initial specs during onboarding."
        });
      } catch (err) {
        console.error("Failed to store initial body log", err);
      }

      setSuccessData({
        profile,
        target_kcal: kcalData.target_kcal,
        protein_g: proteinData.protein_g,
      });

      if (onProfileCreated) {
        onProfileCreated(profile.id);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2>User Intake & Onboarding</h2>
      {error && <p className="error">Error: {error}</p>}
      
      {successData ? (
        <div className="result-block">
          <h3>Success: Profile Successfully Created!</h3>
          <p>Welcome, <strong>{successData.profile.display_name || `User #${successData.profile.id}`}</strong>!</p>
          <ul>
            <li><strong>User ID:</strong> {successData.profile.id} (Save this to check in!)</li>
            <li><strong>Goal:</strong> {formatEnumLabel(successData.profile.goal)}</li>
            <li><strong>Starting Calorie Target:</strong> {successData.target_kcal} kcal/day</li>
            <li><strong>Starting Protein Target:</strong> {successData.protein_g} g/day</li>
          </ul>
          <button onClick={() => setSuccessData(null)}>Create Another Profile</button>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="onboarding-form">
          <div className="form-grid">
            <label>
              Display Name:
              <input type="text" placeholder="e.g. John Doe" value={form.display_name} onChange={e => setForm({...form, display_name: e.target.value})} required />
            </label>
            <label>
              Sex:
              <select value={form.sex} onChange={e => setForm({...form, sex: e.target.value})}>
                <option value="male">Male</option>
                <option value="female">Female</option>
              </select>
            </label>
            <label>
              Age (16-75):
              <input type="number" min="16" max="75" value={form.age} onChange={e => setForm({...form, age: parseInt(e.target.value)})} required />
            </label>
            <label>
              Height (cm):
              <input type="number" min="100" max="250" value={form.height_cm} onChange={e => setForm({...form, height_cm: parseFloat(e.target.value)})} required />
            </label>
            <label>
              Current Weight (kg):
              <input type="number" step="0.1" min="35" max="250" value={form.weight_kg} onChange={e => setForm({...form, weight_kg: parseFloat(e.target.value)})} required />
            </label>
            <label>
              Current Waist (cm, optional):
              <input type="number" step="0.1" min="50" max="200" value={form.waist_cm} onChange={e => setForm({...form, waist_cm: e.target.value ? parseFloat(e.target.value) : ''})} />
            </label>
            <label>
              Primary Goal:
              <select value={form.goal} onChange={e => setForm({...form, goal: e.target.value})}>
                <option value="lean_bulk">Lean Bulk (Recommended for skinny-fat beginners)</option>
                <option value="maintain">Maintain</option>
                <option value="mini_cut">Mini Cut</option>
              </select>
            </label>
            <label>
              Target Weight (kg, optional):
              <input type="number" step="0.1" value={form.target_weight_kg} onChange={e => setForm({...form, target_weight_kg: e.target.value})} />
            </label>
          </div>

          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? 'Calculating Targets & Creating Profile...' : 'Complete Onboarding'}
          </button>
        </form>
      )}
    </div>
  );
}
