import React, { useState, useEffect } from 'react';
import { api } from '../utils/api';
import { WorkoutSession } from '../types';
import { formatDateTime, formatDisplayDate, formatDisplayTime } from '../utils/helpers';

interface SessionSelectorProps {
  userId: string;
  accessToken: string;
  currentSession: WorkoutSession | null;
  onSessionSelect: (session: WorkoutSession) => void;
}

const SessionSelector: React.FC<SessionSelectorProps> = ({
  userId,
  accessToken,
  currentSession,
  onSessionSelect
}) => {
  const [workoutDate, setWorkoutDate] = useState(() => {
    const now = new Date();
    return formatDateTime(now);
  });
  const [sessions, setSessions] = useState<WorkoutSession[]>([]);
  const [allSessions, setAllSessions] = useState<WorkoutSession[]>([]);
  const [showAllSessions, setShowAllSessions] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const loadSessionsForDate = async (date: string) => {
    try {
      const response = await api.getSessionsByDate(userId, accessToken, date.split('T')[0]);
      if (response.success && response.data) {
        setSessions(response.data);
      }
    } catch (error) {
      console.error('Error loading sessions:', error);
    }
  };

  const loadAllSessions = async () => {
    try {
      const response = await api.getAllSessions(userId, accessToken);
      if (response.success && response.data) {
        setAllSessions(response.data);
      }
    } catch (error) {
      console.error('Error loading all sessions:', error);
    }
  };

  useEffect(() => {
    loadSessionsForDate(workoutDate);
  }, [workoutDate, userId, accessToken]);

  const handleDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setWorkoutDate(e.target.value);
  };

  const createSession = async () => {
    setIsLoading(true);
    try {
      const response = await api.createSession(userId, accessToken, workoutDate);
      if (response.success && response.data) {
        const newSession = response.data;
        setSessions(prev => [...prev, newSession]);
        onSessionSelect(newSession);
      } else {
        alert(response.detail || 'Failed to create session');
      }
    } catch (error) {
      alert('Error creating session');
    } finally {
      setIsLoading(false);
    }
  };

  const handleShowAllSessions = () => {
    setShowAllSessions(true);
    loadAllSessions();
  };

  const renameSession = async (sessionId: number, currentName: string) => {
    const newName = prompt('Enter new session name:', currentName);
    if (!newName || newName === currentName) return;

    try {
      const response = await api.renameSession(sessionId, newName, userId, accessToken);
      if (response.success) {
        setSessions(prev => prev.map(s => 
          s.id === sessionId ? { ...s, name: newName } : s
        ));
        setAllSessions(prev => prev.map(s => 
          s.id === sessionId ? { ...s, name: newName } : s
        ));
        if (currentSession?.id === sessionId) {
          onSessionSelect({ ...currentSession, name: newName });
        }
      } else {
        alert(response.detail || 'Failed to rename session');
      }
    } catch (error) {
      alert('Error renaming session');
    }
  };

  return (
    <>
      <div className="card p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Workout Session</h2>
        
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <label htmlFor="workout-date" className="block text-sm font-medium text-gray-700 mb-1">
                Select Date & Time
              </label>
              <input
                id="workout-date"
                type="datetime-local"
                value={workoutDate}
                onChange={handleDateChange}
                className="input"
              />
            </div>
            
            <div className="flex gap-2">
              <button
                onClick={createSession}
                disabled={isLoading}
                className="btn btn-primary whitespace-nowrap"
              >
                {isLoading ? 'Creating...' : 'New Session'}
              </button>
              
              <button
                onClick={handleShowAllSessions}
                className="btn btn-secondary whitespace-nowrap"
              >
                View All
              </button>
            </div>
          </div>

          {sessions.length > 0 && (
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-2">
                Sessions for {formatDisplayDate(workoutDate)}
              </h3>
              <div className="space-y-2">
                {sessions.map((session) => (
                  <div
                    key={session.id}
                    className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                      currentSession?.id === session.id
                        ? 'border-gray-900 bg-gray-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => onSessionSelect(session)}
                  >
                    <div className="flex justify-between items-center">
                      <div>
                        <p className="font-medium text-gray-900">{session.name}</p>
                        <p className="text-sm text-gray-500">
                          {formatDisplayTime(session.created_at)}
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        {session.set_count !== undefined && (
                          <span className="text-sm text-gray-500">
                            {session.set_count} sets
                          </span>
                        )}
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            renameSession(session.id, session.name);
                          }}
                          className="text-gray-400 hover:text-gray-600 p-1"
                          title="Rename session"
                        >
                          ✏️
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {currentSession && (
            <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-sm text-green-800">
                <strong>Active Session:</strong> {currentSession.name}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* All Sessions Modal */}
      {showAllSessions && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg w-full max-w-2xl max-h-96 overflow-hidden">
            <div className="flex justify-between items-center p-6 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">All Workout Sessions</h2>
              <button
                onClick={() => setShowAllSessions(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div className="p-6 overflow-y-auto max-h-80">
              {allSessions.length > 0 ? (
                <div className="space-y-3">
                  {allSessions.map((session) => (
                    <div
                      key={session.id}
                      className="p-3 border border-gray-200 rounded-lg hover:border-gray-300 cursor-pointer"
                      onClick={() => {
                        onSessionSelect(session);
                        setShowAllSessions(false);
                      }}
                    >
                      <div className="flex justify-between items-center">
                        <div>
                          <p className="font-medium text-gray-900">{session.name}</p>
                          <p className="text-sm text-gray-500">
                            {formatDisplayDate(session.created_at)} at {formatDisplayTime(session.created_at)}
                          </p>
                        </div>
                        {session.set_count !== undefined && (
                          <span className="text-sm text-gray-500">
                            {session.set_count} sets
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <p className="text-gray-500">No sessions found</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default SessionSelector;
