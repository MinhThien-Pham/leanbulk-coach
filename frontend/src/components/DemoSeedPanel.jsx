import React, { useState } from 'react';
import { createDemoProfile } from '../api/client';

export default function DemoSeedPanel({ onDemoCreated }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [demoResult, setDemoResult] = useState(null);

  const handleCreateDemo = async () => {
    setLoading(true);
    setError(null);
    setDemoResult(null);
    try {
      const data = await createDemoProfile();
      setDemoResult(data);
      if (onDemoCreated && data.profile) {
        onDemoCreated(data.profile.id);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card demo-seed-panel">
      <h2>Reviewer Quickstart</h2>
      <p>Create a sample local user with body, workout, meal, nutrition, and safety data so reviewers can explore the dashboard immediately.</p>
      
      <button 
        onClick={handleCreateDemo} 
        disabled={loading} 
        className="btn-secondary"
        style={{ width: '100%', padding: '0.75rem', marginBottom: '1rem' }}
      >
        {loading ? 'Seeding Demo Data...' : 'Create Demo User'}
      </button>

      {error && <p className="error">Error: {error}</p>}

      {demoResult && (
        <div className="result-block">
          <h3>Success: Demo user created and loaded.</h3>
          <p style={{ fontSize: '0.9rem', marginBottom: '1rem', color: 'var(--text-secondary)' }}>
            Open the Dashboard to review seeded progress, meals, and safety flags.
          </p>
          <ul>
            <li><strong>Profile ID:</strong> {demoResult.profile.id}</li>
            <li><strong>Display Name:</strong> {demoResult.profile.display_name}</li>
            <li><strong>Body Metrics Logged:</strong> {demoResult.created.body_logs} entries</li>
            <li><strong>Workouts Logged:</strong> {demoResult.created.workout_logs} sets</li>
            <li><strong>Meals Logged:</strong> {demoResult.created.meal_logs} meals</li>
            <li><strong>Safety Flags Active:</strong> {demoResult.created.safety_flags} flag</li>
          </ul>
          
          <h4>Next Actions from Summary:</h4>
          <ul>
            {demoResult.summary?.next_actions?.map((action, i) => (
              <li key={i}>{action}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
