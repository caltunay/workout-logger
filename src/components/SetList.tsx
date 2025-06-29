import React, { useState, useEffect } from 'react';
import { api } from '../utils/api';
import { ExerciseSet, WorkoutSession } from '../types';
import { formatDisplayTime } from '../utils/helpers';

interface SetListProps {
  session: WorkoutSession | null;
  userId: string;
  accessToken: string;
  refreshTrigger: number;
}

const SetList: React.FC<SetListProps> = ({ session, userId, accessToken, refreshTrigger }) => {
  const [sets, setSets] = useState<ExerciseSet[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const loadSets = async () => {
    if (!session) {
      setSets([]);
      return;
    }

    setIsLoading(true);
    try {
      const response = await api.getSessionSets(session.id, userId, accessToken);
      if (response.success && response.data) {
        setSets(response.data);
      }
    } catch (error) {
      console.error('Error loading sets:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadSets();
  }, [session, refreshTrigger]);

  const duplicateSet = async (setId: number) => {
    try {
      const response = await api.duplicateSet(setId, userId, accessToken);
      if (response.success) {
        loadSets(); // Refresh the list
      } else {
        alert(response.detail || 'Failed to duplicate set');
      }
    } catch (error) {
      alert('Error duplicating set');
    }
  };

  const editSet = async (setId: number, currentReps: number, currentWeight: number) => {
    const newReps = prompt('Enter new reps:', currentReps.toString());
    if (newReps === null) return;

    const newWeight = prompt('Enter new weight:', currentWeight.toString());
    if (newWeight === null) return;

    const reps = parseInt(newReps);
    const weight = parseFloat(newWeight);

    if (isNaN(reps) || isNaN(weight) || reps <= 0 || weight <= 0) {
      alert('Please enter valid positive numbers');
      return;
    }

    try {
      const response = await api.editSet(setId, reps, weight, userId, accessToken);
      if (response.success) {
        loadSets(); // Refresh the list
      } else {
        alert(response.detail || 'Failed to edit set');
      }
    } catch (error) {
      alert('Error editing set');
    }
  };

  const removeSet = async (setId: number) => {
    if (!confirm('Are you sure you want to remove this set?')) {
      return;
    }

    try {
      const response = await api.removeSet(setId, userId, accessToken);
      if (response.success) {
        loadSets(); // Refresh the list
      } else {
        alert(response.detail || 'Failed to remove set');
      }
    } catch (error) {
      alert('Error removing set');
    }
  };

  const groupedSets = sets.reduce((groups, set) => {
    const exerciseName = set.exercise_name;
    if (!groups[exerciseName]) {
      groups[exerciseName] = [];
    }
    groups[exerciseName].push(set);
    return groups;
  }, {} as Record<string, ExerciseSet[]>);

  if (!session) {
    return (
      <div className="card p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Exercise Sets</h2>
        <div className="text-center py-8">
          <p className="text-gray-500">Select a session to view sets</p>
        </div>
      </div>
    );
  }

  return (
    <div className="card p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">
        {session.name} - Sets
      </h2>

      {isLoading ? (
        <div className="text-center py-8">
          <p className="text-gray-500">Loading sets...</p>
        </div>
      ) : sets.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-gray-500">No sets added yet</p>
          <p className="text-sm text-gray-400 mt-2">Add your first exercise set above</p>
        </div>
      ) : (
        <div className="space-y-6">
          {Object.entries(groupedSets).map(([exerciseName, exerciseSets]) => (
            <div key={exerciseName}>
              <h3 className="font-medium text-gray-900 mb-3 pb-2 border-b border-gray-200">
                {exerciseName}
              </h3>
              
              <div className="space-y-2">
                {exerciseSets.map((set, index) => (
                  <div
                    key={set.id}
                    className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:border-gray-300 transition-colors"
                  >
                    <div className="flex items-center space-x-4">
                      <span className="text-sm font-medium text-gray-500 w-8">
                        #{index + 1}
                      </span>
                      <div className="flex items-center space-x-6">
                        <div className="text-center">
                          <p className="text-lg font-semibold text-gray-900">{set.reps}</p>
                          <p className="text-xs text-gray-500">reps</p>
                        </div>
                        <div className="text-center">
                          <p className="text-lg font-semibold text-gray-900">
                            {set.weight} {set.is_kg ? 'kg' : 'lbs'}
                          </p>
                          <p className="text-xs text-gray-500">weight</p>
                        </div>
                        <div className="text-center">
                          <p className="text-sm text-gray-500">
                            {formatDisplayTime(set.created_at)}
                          </p>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => duplicateSet(set.id)}
                        className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-50 rounded"
                        title="Duplicate set"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                        </svg>
                      </button>
                      
                      <button
                        onClick={() => editSet(set.id, set.reps, set.weight)}
                        className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-50 rounded"
                        title="Edit set"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                      </button>
                      
                      <button
                        onClick={() => removeSet(set.id)}
                        className="p-2 text-red-400 hover:text-red-600 hover:bg-red-50 rounded"
                        title="Remove set"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SetList;
