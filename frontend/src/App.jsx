import React from 'react';
import StatusCard from './components/StatusCard';
import DemoDashboard from './components/DemoDashboard';
import ToolPanel from './components/ToolPanel';
import SummaryPanel from './components/SummaryPanel';
import EvalPanel from './components/EvalPanel';
import './styles.css';

function App() {
  return (
    <div className="container">
      <header>
        <h1>LeanBulk Coach</h1>
        <p>Deterministic Coaching Demo UI</p>
      </header>
      
      <main>
        <StatusCard />
        <DemoDashboard />
        <ToolPanel />
        <SummaryPanel />
        <EvalPanel />
      </main>
    </div>
  );
}

export default App;
