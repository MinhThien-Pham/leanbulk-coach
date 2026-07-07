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

function TrendLineChart({ logs, valueKey, title, unit }) {
  if (!logs || logs.length === 0) {
    return (
      <div className="custom-chart-wrapper">
        <h4>{title}</h4>
        <p className="no-data">No logs recorded yet.</p>
      </div>
    );
  }

  // Sort and limit to last 7 logs
  const sorted = [...logs].sort((a, b) => new Date(a.logged_at) - new Date(b.logged_at)).slice(-7);
  
  const values = sorted.map(log => log[valueKey]);
  let minVal = Math.min(...values);
  let maxVal = Math.max(...values);
  
  // padding / normalization
  if (minVal === maxVal) {
    minVal -= 1;
    maxVal += 1;
  } else {
    const diff = maxVal - minVal;
    const pad = diff * 0.15 > 0.1 ? diff * 0.15 : 0.2;
    minVal -= pad;
    maxVal += pad;
  }
  const range = maxVal - minVal;

  // SVG dimensions
  const width = 360;
  const height = 180;
  const paddingLeft = 40;
  const paddingRight = 20;
  const paddingTop = 30;
  const paddingBottom = 40;

  const chartWidth = width - paddingLeft - paddingRight;
  const chartHeight = height - paddingTop - paddingBottom;

  const getCoords = (index, value) => {
    const x = paddingLeft + (sorted.length > 1 ? (index / (sorted.length - 1)) * chartWidth : chartWidth / 2);
    const y = paddingTop + chartHeight - ((value - minVal) / range) * chartHeight;
    return { x, y };
  };

  const points = sorted.map((log, i) => getCoords(i, log[valueKey]));
  const polylinePointsStr = points.map(p => `${p.x},${p.y}`).join(' ');

  return (
    <div className="custom-chart-wrapper" style={{ minWidth: '320px' }}>
      <h4 style={{ margin: '0 0 1rem 0', color: '#475569' }}>{title}</h4>
      <div style={{ position: 'relative', width: '100%', height: `${height}px` }}>
        <svg width="100%" height="100%" viewBox={`0 0 ${width} ${height}`}>
          {/* Background Grid Lines (Horizontal) */}
          {[0, 0.25, 0.5, 0.75, 1].map((ratio, idx) => {
            const y = paddingTop + chartHeight * ratio;
            const val = maxVal - range * ratio;
            return (
              <g key={idx}>
                <line 
                  x1={paddingLeft} 
                  y1={y} 
                  x2={width - paddingRight} 
                  y2={y} 
                  stroke="#e2e8f0" 
                  strokeDasharray="4 4" 
                />
                <text 
                  x={paddingLeft - 8} 
                  y={y + 4} 
                  fill="#64748b" 
                  fontSize="10" 
                  textAnchor="end"
                >
                  {val.toFixed(1)}
                </text>
              </g>
            );
          })}

          {/* Connecting Line */}
          {points.length > 1 && (
            <polyline
              fill="none"
              stroke="#2563eb"
              strokeWidth="3"
              points={polylinePointsStr}
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          )}

          {/* Data points (dots & labels) */}
          {sorted.map((log, i) => {
            const { x, y } = points[i];
            const val = log[valueKey];
            const dateLabel = formatDate(log.logged_at, true) || `Day ${i + 1}`;
            return (
              <g key={i}>
                <circle
                  cx={x}
                  cy={y}
                  r="5"
                  fill="#2563eb"
                  stroke="#ffffff"
                  strokeWidth="2"
                />
                <text
                  x={x}
                  y={y - 10}
                  fill="#0f172a"
                  fontSize="10"
                  fontWeight="bold"
                  textAnchor="middle"
                >
                  {val.toFixed(1)}
                </text>
                <text
                  x={x}
                  y={height - 12}
                  fill="#64748b"
                  fontSize="10"
                  textAnchor="middle"
                >
                  {dateLabel}
                </text>
              </g>
            );
          })}
        </svg>
      </div>
    </div>
  );
}

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

  // Custom Chart Renderers using plain React + SVG TrendLineChart
  const renderWeightChart = () => {
    return (
      <TrendLineChart 
        logs={bodyLogs} 
        valueKey="weight_kg" 
        title="Weight Trend (kg)" 
        unit="kg" 
      />
    );
  };

  const renderWaistChart = () => {
    const validLogs = bodyLogs.filter(x => x.waist_cm !== null);
    return (
      <TrendLineChart 
        logs={validLogs} 
        valueKey="waist_cm" 
        title="Waist Circumference Trend (cm)" 
        unit="cm" 
      />
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
