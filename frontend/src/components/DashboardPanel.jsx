import React, { useState, useEffect } from 'react';
import { 
  listProfiles, 
  getBodyLogs, 
  getWorkoutLogs, 
  getMealLogs, 
  getOpenSafetyFlags, 
  resolveSafetyFlag, 
  getUserContext,
  buildSummary,
  getProfile
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

const formatDate = (dateStr, short = false) => {
  if (!dateStr) return null;
  const d = new Date(dateStr);
  if (d instanceof Date && !isNaN(d.getTime())) {
    if (short) {
      return d.toLocaleDateString([], { month: 'short', day: 'numeric' });
    }
    return d.toLocaleDateString();
  }
  return null;
};

export default function DashboardPanel({ initialUserId }) {
  const [profiles, setProfiles] = useState([]);
  const [userId, setUserId] = useState(initialUserId || '');
  const [activeProfile, setActiveProfile] = useState(null);
  const [bodyLogs, setBodyLogs] = useState([]);
  const [workouts, setWorkouts] = useState([]);
  const [meals, setMeals] = useState([]);
  const [safetyFlags, setSafetyFlags] = useState([]);
  const [coachingSummary, setCoachingSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadProfiles();
  }, []);

  useEffect(() => {
    if (initialUserId) {
      setUserId(initialUserId);
      loadDashboardData(initialUserId);
    }
  }, [initialUserId]);

  const loadProfiles = async () => {
    try {
      const list = await listProfiles();
      setProfiles(list);
      if (list.length > 0 && !userId) {
        setUserId(list[0].id);
        loadDashboardData(list[0].id);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const loadDashboardData = async (uid) => {
    if (!uid) return;
    setLoading(true);
    setError(null);
    try {
      const uId = parseInt(uid);
      
      // Load all logs and context details
      const [body, wks, mls, flags, context] = await Promise.all([
        getBodyLogs(uId),
        getWorkoutLogs(uId),
        getMealLogs(uId),
        getOpenSafetyFlags(uId),
        getUserContext(uId)
      ]);

      setBodyLogs(body);
      setWorkouts(wks);
      setMeals(mls);
      setSafetyFlags(flags);

      // Build summary using loaded context
      const summary = await buildSummary(context);
      setCoachingSummary(summary);

      const profileMatch = profiles.find(p => p.id === uId);
      if (profileMatch) {
        setActiveProfile(profileMatch);
      } else {
        const prof = await getProfile(uId);
        setActiveProfile(prof);
      }
    } catch (err) {
      setError("Failed to load dashboard data: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleResolveFlag = async (flagId) => {
    try {
      await resolveSafetyFlag(flagId);
      // Reload safety flags and summary
      loadDashboardData(userId);
    } catch (err) {
      alert("Error resolving flag: " + err.message);
    }
  };

  // Custom Chart Renderers (CSS based, no library)
  const renderWeightChart = () => {
    if (bodyLogs.length === 0) return <p className="no-data">No weight logs logged yet.</p>;

    // Sort by date chronological
    const sorted = [...bodyLogs].sort((a,b) => new Date(a.logged_at) - new Date(b.logged_at));
    const weights = sorted.map(x => x.weight_kg);
    const minW = Math.min(...weights) - 2;
    const maxW = Math.max(...weights) + 2;
    const range = maxW - minW || 10;

    return (
      <div className="custom-chart-wrapper">
        <h4>Weight Trend (kg)</h4>
        <div className="bar-chart">
          {sorted.slice(-8).map((log, i) => {
            const heightPct = ((log.weight_kg - minW) / range) * 100;
            return (
              <div className="chart-bar-container" key={i}>
                <span className="bar-value">{log.weight_kg.toFixed(1)}</span>
                <div 
                  className="chart-bar weight-bar" 
                  style={{ height: `${Math.max(heightPct, 15)}%` }} 
                />
                <span className="bar-label">{formatDate(log.logged_at, true) || `Day ${i + 1}`}</span>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  const renderWaistChart = () => {
    const validLogs = bodyLogs.filter(x => x.waist_cm !== null);
    if (validLogs.length === 0) return <p className="no-data">No waist circumference logs logged yet.</p>;

    const sorted = [...validLogs].sort((a,b) => new Date(a.logged_at) - new Date(b.logged_at));
    const waists = sorted.map(x => x.waist_cm);
    const minW = Math.min(...waists) - 2;
    const maxW = Math.max(...waists) + 2;
    const range = maxW - minW || 10;

    return (
      <div className="custom-chart-wrapper">
        <h4>Waist Circumference Trend (cm)</h4>
        <div className="bar-chart">
          {sorted.slice(-8).map((log, i) => {
            const heightPct = ((log.waist_cm - minW) / range) * 100;
            return (
              <div className="chart-bar-container" key={i}>
                <span className="bar-value">{log.waist_cm.toFixed(1)}</span>
                <div 
                  className="chart-bar waist-bar" 
                  style={{ height: `${Math.max(heightPct, 15)}%` }} 
                />
                <span className="bar-label">{formatDate(log.logged_at, true) || `Day ${i + 1}`}</span>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <div className="card dashboard-panel">
      <h2>Progress Dashboard</h2>

      <div className="profile-selector-row">
        <label>
          Select Profile to View:
          <select value={userId} onChange={e => {
            setUserId(e.target.value);
            loadDashboardData(e.target.value);
          }}>
            <option value="">-- Choose Profile --</option>
            {profiles.map(p => (
              <option key={p.id} value={p.id}>
                {p.display_name || `User #${p.id}`} (Goal: {formatEnumLabel(p.goal)})
              </option>
            ))}
          </select>
        </label>
        <button onClick={() => loadDashboardData(userId)} disabled={loading || !userId} className="btn-secondary">
          Refresh Data
        </button>
      </div>

      {error && <p className="error">{error}</p>}
      {loading && <p>Loading dashboard metrics...</p>}

      {activeProfile && coachingSummary && (
        <div className="dashboard-content">
          <div className="summary-cards-grid">
            <div className="summary-status-card">
              <h4>Goal & Profile</h4>
              <p><strong>Goal:</strong> {formatEnumLabel(coachingSummary.goal)}</p>
              <p><strong>Current Weight:</strong> {coachingSummary.current_weight_kg ? `${coachingSummary.current_weight_kg} kg` : "N/A"}</p>
              <p><strong>Latest Waist:</strong> {coachingSummary.latest_waist_cm ? `${coachingSummary.latest_waist_cm} cm` : "N/A"}</p>
            </div>

            <div className="summary-status-card">
              <h4>Safety Status</h4>
              <span className={`status-pill ${coachingSummary.safety_status === 'attention_needed' ? 'status-red' : 'status-green'}`}>
                {formatEnumLabel(coachingSummary.safety_status)}
              </span>
              <p className="status-sub-text">Safety checks verify weekly rate of change constraints.</p>
            </div>

            <div className="summary-status-card">
              <h4>Current Targets</h4>
              <p><strong>Calories:</strong> {coachingSummary.calorie_target_kcal ? `${coachingSummary.calorie_target_kcal} kcal` : "N/A"}</p>
              <p><strong>Protein:</strong> {coachingSummary.protein_target_g ? `${coachingSummary.protein_target_g} g` : "N/A"}</p>
            </div>
          </div>

          <div className="next-actions-banner">
            <h4>Next Actions:</h4>
            <ul>
              {coachingSummary.next_actions?.map((act, idx) => (
                <li key={idx}><strong>{act}</strong></li>
              ))}
            </ul>
          </div>

          {/* Safety Flags Section */}
          {safetyFlags.length > 0 && (
            <div className="safety-flags-container">
              <h4>Warning: Open Safety Alert Flags ({safetyFlags.length})</h4>
              <div className="flags-list">
                {safetyFlags.map(flag => (
                  <div key={flag.id} className="flag-alert-item">
                    <div>
                      <span className="flag-severity">[{formatEnumLabel(flag.severity)}]</span>
                      <strong> {formatEnumLabel(flag.flag_type)}:</strong> {flag.message}
                    </div>
                    <button onClick={() => handleResolveFlag(flag.id)} className="btn-resolve">Resolve</button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Visual Trends Charts */}
          <div className="charts-grid">
            {renderWeightChart()}
            {renderWaistChart()}
          </div>

          {/* Detailed Lists */}
          <div className="history-lists-grid">
            <div className="history-column">
              <h4>Workout set history:</h4>
              {workouts.length === 0 ? <p className="no-data">No workouts logged yet.</p> : (
                <ul className="history-list">
                  {workouts.slice(0, 10).map((set, i) => (
                    <li key={i}>
                      <strong>{set.exercise_name}:</strong> {set.weight_kg}kg x {set.reps} reps (RIR: {set.rir})
                      {formatDate(set.logged_at) && <span className="log-date">{formatDate(set.logged_at)}</span>}
                    </li>
                  ))}
                </ul>
              )}
            </div>

            <div className="history-column">
              <h4>Meal logs:</h4>
              {meals.length === 0 ? <p className="no-data">No meals logged yet.</p> : (
                <ul className="history-list">
                  {meals.slice(0, 10).map((meal, i) => (
                    <li key={i}>
                      <strong>{meal.meal_name}:</strong> {meal.kcal} kcal, {meal.protein_g}g protein
                      {formatDate(meal.logged_at) && <span className="log-date">{formatDate(meal.logged_at)}</span>}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
