import React, { useState, useEffect } from 'react';
import { getHealth } from '../api/client';

export default function StatusCard() {
  const [status, setStatus] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getHealth()
      .then((data) => {
        setStatus(data);
        setError(null);
      })
      .catch((err) => {
        setError(err.message);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  return (
    <div className="card">
      <h2>Backend Status</h2>
      {loading && <p>Loading...</p>}
      {error && <p className="error">Error: {error}</p>}
      {status && (
        <ul>
          <li><strong>API Status:</strong> {status.status}</li>
          <li><strong>Service:</strong> {status.service}</li>
          <li><strong>Version:</strong> {status.version}</li>
          <li><strong>Live LLM Calls:</strong> {status.live_llm_calls ? 'Yes' : 'No'}</li>
        </ul>
      )}
    </div>
  );
}
