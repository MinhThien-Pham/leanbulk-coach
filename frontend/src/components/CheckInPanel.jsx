import React, { useState, useEffect } from 'react';
import { 
  listProfiles, 
  logBodyMetric, 
  logWorkoutSet, 
  logMeal, 
  logSafetyFlag, 
  getUserContext, 
  buildSummary 
} from '../api/client';

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

export default function CheckInPanel({ selectedUserId, onCheckInComplete }) {
  const [profiles, setProfiles] = useState([]);
  const [userId, setUserId] = useState(selectedUserId || '');
  const [weight, setWeight] = useState(75.5);
  const [waist, setWaist] = useState(80.5);
  const [kcal, setKcal] = useState(2500);
  const [protein, setProtein] = useState(150);
  
  // Workouts and sets
  const [exercise, setExercise] = useState('Squat');
  const [reps, setReps] = useState(5);
  const [liftWeight, setLiftWeight] = useState(60);
  const [rir, setRir] = useState(2);
  const [workoutSets, setWorkoutSets] = useState([]);

  const [sleep, setSleep] = useState(7.5);
  const [energy, setEnergy] = useState(4);
  const [notes, setNotes] = useState('');

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [coachResponse, setCoachResponse] = useState(null);

  useEffect(() => {
    listProfiles()
      .then(setProfiles)
      .catch(err => console.error("Failed to load profiles", err));
  }, []);

  useEffect(() => {
    if (selectedUserId) {
      setUserId(selectedUserId);
    }
  }, [selectedUserId]);

  const addSetToLog = () => {
    setWorkoutSets([
      ...workoutSets,
      { exercise_name: exercise, reps: parseInt(reps), weight_kg: parseFloat(liftWeight), rir: parseFloat(rir) }
    ]);
  };

  const clearWorkoutSets = () => setWorkoutSets([]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!userId) {
      setError("Please select or enter a User ID.");
      return;
    }
    setLoading(true);
    setError(null);
    setCoachResponse(null);

    try {
      const uId = parseInt(userId);

      // 1. Log weight and waist
      await logBodyMetric({
        user_id: uId,
        weight_kg: parseFloat(weight),
        waist_cm: waist ? parseFloat(waist) : undefined,
        notes: notes || "Weekly check-in log."
      });

      // 2. Log nutrition intake as a meal log
      await logMeal({
        user_id: uId,
        meal_name: "Average Daily Intake",
        kcal: parseInt(kcal),
        protein_g: parseInt(protein),
        notes: `Weekly average: Sleep ${sleep}h, Energy ${energy}/5`
      });

      // 3. Log all workout sets
      for (const set of workoutSets) {
        await logWorkoutSet({
          user_id: uId,
          ...set
        });
      }

      // 4. Client-side scanning for pain/soreness keywords to trigger a safety flag
      const keywords = ["pain", "hurt", "injury", "hernia", "sprain", "soreness", "damage", "ache"];
      const lowerNotes = notes.toLowerCase();
      const triggeredWord = keywords.find(word => lowerNotes.includes(word));
      
      if (triggeredWord) {
        await logSafetyFlag({
          user_id: uId,
          flag_type: "pain_flag",
          severity: "high",
          message: `User reported pain/injury symptoms containing: '${triggeredWord}'. Notes: "${notes}"`
        });
      }

      // 5. Fetch updated context and build a deterministic coaching summary.
      const context = await getUserContext(uId);
      const summaryResult = await buildSummary(context);
      setCoachResponse(summaryResult);

      if (onCheckInComplete) {
        onCheckInComplete(uId);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2>Weekly Check-In & Coaching Call</h2>
      {error && <p className="error">Error: {error}</p>}

      {coachResponse ? (
        <div className="result-block coach-speech-bubble">
          <h3>Coach Summary for {coachResponse.user_name}</h3>
          <div className="badge-container">
            <span className={`badge ${coachResponse.safety_status === 'attention_needed' ? 'badge-danger' : 'badge-success'}`}>
              Safety Status: {formatEnumLabel(coachResponse.safety_status)}
            </span>
          </div>
          
          <div className="summary-section">
            <p><strong>Goal:</strong> {formatEnumLabel(coachResponse.goal)}</p>
            <p><strong>Calorie Target:</strong> {coachResponse.calorie_target_kcal} kcal</p>
            <p><strong>Protein Target:</strong> {coachResponse.protein_target_g} g</p>
            <p><strong>Progress Trend:</strong> {formatEnumLabel(coachResponse.progress_status)}</p>
            <p><strong>Nutrition Target Status:</strong> {formatEnumLabel(coachResponse.nutrition_status)}</p>
            <p><strong>Training Activity:</strong> {formatEnumLabel(coachResponse.training_status)}</p>
          </div>

          <h4>Next Actions:</h4>
          <ul>
            {coachResponse.next_actions?.map((act, i) => (
              <li key={i}><strong>{act}</strong></li>
            ))}
          </ul>

          <button onClick={() => setCoachResponse(null)}>Submit Another Check-In</button>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="checkin-form">
          <div className="form-grid">
            <label>
              Select User Profile:
              <select value={userId} onChange={e => setUserId(e.target.value)} required>
                <option value="">-- Choose User --</option>
                {profiles.map(p => (
                  <option key={p.id} value={p.id}>
                    {p.display_name || `User #${p.id}`} (Goal: {formatEnumLabel(p.goal)})
                  </option>
                ))}
              </select>
            </label>
            
            <label>
              Manual User ID (if not listed):
              <input type="number" value={userId} onChange={e => setUserId(e.target.value)} />
            </label>

            <label>
              Current Weight (kg):
              <input type="number" step="0.1" value={weight} onChange={e => setWeight(parseFloat(e.target.value))} required />
            </label>

            <label>
              Current Waist (cm):
              <input type="number" step="0.1" value={waist} onChange={e => setWaist(parseFloat(e.target.value))} required />
            </label>

            <label>
              Avg Daily Calories Consumed:
              <input type="number" value={kcal} onChange={e => setKcal(parseInt(e.target.value))} required />
            </label>

            <label>
              Avg Daily Protein Consumed (g):
              <input type="number" value={protein} onChange={e => setProtein(parseInt(e.target.value))} required />
            </label>

            <label>
              Sleep Average Per Night (hrs):
              <input type="number" step="0.1" value={sleep} onChange={e => setSleep(parseFloat(e.target.value))} required />
            </label>

            <label>
              Energy & Recovery (1-5):
              <select value={energy} onChange={e => setEnergy(parseInt(e.target.value))}>
                <option value="1">1 - Extremely Fatigued</option>
                <option value="2">2 - Poor recovery</option>
                <option value="3">3 - Normal</option>
                <option value="4">4 - Good</option>
                <option value="5">5 - Excellent energy</option>
              </select>
            </label>
          </div>

          <div className="form-section workout-section-builder">
            <h4>Log Key Lifts / Workouts Completed:</h4>
            <div className="workout-builder-row">
              <label>Exercise: 
                <input type="text" value={exercise} onChange={e => setExercise(e.target.value)} />
              </label>
              <label>Reps: 
                <input type="number" value={reps} onChange={e => setReps(e.target.value)} />
              </label>
              <label>Weight (kg): 
                <input type="number" value={liftWeight} onChange={e => setLiftWeight(e.target.value)} />
              </label>
              <label>RIR: 
                <input type="number" step="0.5" value={rir} onChange={e => setRir(e.target.value)} />
              </label>
              <button type="button" onClick={addSetToLog} className="btn-secondary">Add Set</button>
            </div>

            {workoutSets.length > 0 && (
              <div className="added-sets-list">
                <h5>Sets to log this check-in:</h5>
                <ul>
                  {workoutSets.map((set, idx) => (
                    <li key={idx}>
                      {set.exercise_name} - {set.weight_kg}kg x {set.reps} reps (RIR: {set.rir})
                    </li>
                  ))}
                </ul>
                <button type="button" onClick={clearWorkoutSets} className="btn-danger-text">Clear sets</button>
              </div>
            )}
          </div>

          <label className="text-area-label">
            Check-In Notes & physical sensations:
            <textarea 
              value={notes} 
              onChange={e => setNotes(e.target.value)} 
              placeholder="e.g. Felt strong. Joint soreness in knees. (Type 'pain' or 'injury' to trigger a guardrail flag demo)" 
            />
          </label>

          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? 'Submitting & Analyzing Metrics...' : 'Submit Weekly Check-In'}
          </button>
        </form>
      )}
    </div>
  );
}
