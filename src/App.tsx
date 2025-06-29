import React, { useState } from 'react';
import { useAuth } from './hooks/useAuth';
import AuthForm from './components/AuthForm';
import SessionSelector from './components/SessionSelector';
import ExerciseForm from './components/ExerciseForm';
import SetList from './components/SetList';
import { WorkoutSession } from './types';

const App: React.FC = () => {
  const { user, isLoading, login, logout, isAuthenticated } = useAuth();
  const [currentSession, setCurrentSession] = useState<WorkoutSession | null>(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleSetAdded = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <AuthForm onLogin={login} />;
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">Workout Tracker</h1>
            <button
              onClick={logout}
              className="btn btn-secondary"
            >
              Sign Out
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 py-8 space-y-8">
        <SessionSelector
          userId={user!.user_id}
          accessToken={user!.access_token}
          currentSession={currentSession}
          onSessionSelect={setCurrentSession}
        />

        <ExerciseForm
          sessionId={currentSession?.id || null}
          userId={user!.user_id}
          accessToken={user!.access_token}
          onSetAdded={handleSetAdded}
        />

        <SetList
          session={currentSession}
          userId={user!.user_id}
          accessToken={user!.access_token}
          refreshTrigger={refreshTrigger}
        />
      </div>
    </div>
  );
};

export default App;
