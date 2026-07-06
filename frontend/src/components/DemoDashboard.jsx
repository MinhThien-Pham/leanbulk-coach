import React, { useState } from 'react';
import { getLocalDemo } from '../api/client';

export default function DemoDashboard() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const runDemo = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getLocalDemo();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const summary = result?.summary || {};
  const profile = result?.profile || {};
  const latestBody = result?.contexts?.latest_body_context || {};
  const latestNutrition = result?.contexts?.latest_nutrition_context || {};

  return (
    <div className="card">
      <h2>Local Demo Flow</h2>
      <button onClick={runDemo} disabled={loading}>
        {loading ? 'Running...' : 'Run Local Demo Flow'}
      </button>
      
      {error && <p className="error">Error: {error}</p>}
      
      {result && (
        <div className="result-block">
          <h3>Summary Results</h3>
          <ul>
            <li><strong>Name:</strong> {summary.user_name || profile.display_name || 'N/A'}</li>
            <li><strong>Current Weight:</strong> {summary.current_weight_kg || latestBody.weight_kg || 'N/A'} kg</li>
            <li><strong>Calorie Target:</strong> {summary.calorie_target_kcal || latestNutrition.target_kcal || 'N/A'} kcal</li>
            <li><strong>Protein Target:</strong> {summary.protein_target_g || latestNutrition.protein_g || 'N/A'} g</li>
            <li><strong>Live LLM Calls:</strong> {result.metadata?.live_llm_calls ? 'Yes' : 'No'}</li>
          </ul>
          <h4>Next Actions</h4>
          <ul>
            {summary.next_actions?.map((action, i) => (
              <li key={i}>{action}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
