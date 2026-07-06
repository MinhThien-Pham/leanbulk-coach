import React, { useState } from 'react';
import { buildSummary } from '../api/client';

export default function SummaryPanel() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const runEmptySummary = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await buildSummary({});
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const runExampleSummary = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await buildSummary({
        profile_context: { goal: "lean_bulk", current_weight_kg: 75.0 },
        latest_nutrition_context: { target_kcal: 2500, protein_g: 150 },
        progress_summary_context: { weight_trend: "gaining_fast", waist_trend: "increasing" },
        open_safety_context: [{ flag_type: "waist_creep", severity: "high", message: "Waist expanding too fast" }]
      });
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2>Coaching Summary</h2>
      <div className="button-group">
        <button onClick={runEmptySummary} disabled={loading}>
          Build Empty Intake Summary
        </button>
        <button onClick={runExampleSummary} disabled={loading}>
          Build Example Summary
        </button>
      </div>
      
      {error && <p className="error">Error: {error}</p>}
      
      {result && (
        <div className="result-block">
          <h3>Generated Summary</h3>
          <ul>
            <li><strong>Progress Status:</strong> {result.progress_status}</li>
            <li><strong>Safety Status:</strong> {result.safety_status}</li>
            <li><strong>Training Status:</strong> {result.training_status}</li>
            <li><strong>Nutrition Status:</strong> {result.nutrition_status}</li>
          </ul>
          <h4>Next Actions</h4>
          <ul>
            {result.next_actions?.map((action, i) => (
              <li key={i}>{action}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
