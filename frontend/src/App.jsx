import React, { useState } from 'react';
import StatusCard from './components/StatusCard';
import DemoDashboard from './components/DemoDashboard';
import ToolPanel from './components/ToolPanel';
import SummaryPanel from './components/SummaryPanel';
import EvalPanel from './components/EvalPanel';
import OnboardingPanel from './components/OnboardingPanel';
import CheckInPanel from './components/CheckInPanel';
import DashboardPanel from './components/DashboardPanel';
import MealHelperPanel from './components/MealHelperPanel';
import './styles.css';

function App() {
  const [activeTab, setActiveTab] = useState('onboarding');
  const [currentUserId, setCurrentUserId] = useState('');

  const handleProfileCreated = (userId) => {
    setCurrentUserId(userId);
    setActiveTab('dashboard');
  };

  const handleCheckInComplete = (userId) => {
    setCurrentUserId(userId);
    setActiveTab('dashboard');
  };

  return (
    <div className="container">
      <header>
        <h1>LeanBulk Coach</h1>
        <p>Deterministic Coaching & Adaptive Safety Guardrails</p>
      </header>

      <div className="tab-navigation">
        <button 
          className={`tab-btn ${activeTab === 'onboarding' ? 'active' : ''}`} 
          onClick={() => setActiveTab('onboarding')}
        >
          Onboarding
        </button>
        <button 
          className={`tab-btn ${activeTab === 'checkin' ? 'active' : ''}`} 
          onClick={() => setActiveTab('checkin')}
        >
          Check-In
        </button>
        <button 
          className={`tab-btn ${activeTab === 'dashboard' ? 'active' : ''}`} 
          onClick={() => setActiveTab('dashboard')}
        >
          Dashboard
        </button>
        <button 
          className={`tab-btn ${activeTab === 'mealhelper' ? 'active' : ''}`} 
          onClick={() => setActiveTab('mealhelper')}
        >
          Meal Helper
        </button>
        <button 
          className={`tab-btn ${activeTab === 'dev' ? 'active' : ''}`} 
          onClick={() => setActiveTab('dev')}
        >
          Dev Panel
        </button>
      </div>
      
      <main>
        {activeTab === 'onboarding' && (
          <OnboardingPanel onProfileCreated={handleProfileCreated} />
        )}
        
        {activeTab === 'checkin' && (
          <CheckInPanel 
            selectedUserId={currentUserId} 
            onCheckInComplete={handleCheckInComplete} 
          />
        )}
        
        {activeTab === 'dashboard' && (
          <DashboardPanel initialUserId={currentUserId} />
        )}
        
        {activeTab === 'mealhelper' && (
          <MealHelperPanel initialUserId={currentUserId} />
        )}

        {activeTab === 'dev' && (
          <div className="dev-tab-content">
            <StatusCard />
            <DemoDashboard />
            <ToolPanel />
            <SummaryPanel />
            <EvalPanel />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
