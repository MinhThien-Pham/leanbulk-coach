import React, { useState } from 'react';
import { listEvals, runEvals, getEvalReport } from '../api/client';

export default function EvalPanel() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [listResult, setListResult] = useState(null);
  const [suiteResult, setSuiteResult] = useState(null);
  const [reportResult, setReportResult] = useState(null);

  const handleList = async () => {
    setLoading(true); setError(null); setSuiteResult(null); setReportResult(null);
    try {
      const data = await listEvals();
      setListResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleRun = async () => {
    setLoading(true); setError(null); setListResult(null); setReportResult(null);
    try {
      const data = await runEvals();
      setSuiteResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleReport = async () => {
    setLoading(true); setError(null); setListResult(null); setSuiteResult(null);
    try {
      const data = await getEvalReport();
      setReportResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2>Evaluation Suite</h2>
      <div className="button-group">
        <button onClick={handleList} disabled={loading}>List Eval Cases</button>
        <button onClick={handleRun} disabled={loading}>Run Eval Suite</button>
        <button onClick={handleReport} disabled={loading}>Show Eval Report</button>
      </div>

      {loading && <p>Loading evaluations...</p>}
      {error && <p className="error">Error: {error}</p>}

      {listResult && (
        <div className="result-block">
          <h3>Total Cases: {listResult.total}</h3>
          <ul>
            {listResult.cases.map(c => (
              <li key={c.id}><strong>{c.id}</strong> ({c.category}): {c.description}</li>
            ))}
          </ul>
        </div>
      )}

      {suiteResult && (
        <div className="result-block">
          <h3>Suite Result</h3>
          <p>Total: {suiteResult.total} | Passed: {suiteResult.passed} | Failed: {suiteResult.failed} | Score: {(suiteResult.score * 100).toFixed(1)}%</p>
          <pre>{JSON.stringify(suiteResult.results.map(r => ({id: r.case_id, passed: r.passed})), null, 2)}</pre>
        </div>
      )}

      {reportResult && (
        <div className="result-block">
          <h3>Evaluation Report</h3>
          <p>Total: {reportResult.summary.total} | Passed: {reportResult.summary.passed} | Failed: {reportResult.summary.failed}</p>
          <pre>{reportResult.report}</pre>
        </div>
      )}
    </div>
  );
}
