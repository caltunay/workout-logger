import React, { useState, useEffect, useRef } from 'react';
import { api } from '../utils/api';
import { ExerciseSuggestion } from '../types';
import { debounce } from '../utils/helpers';

interface ExerciseFormProps {
  sessionId: number | null;
  userId: string;
  accessToken: string;
  onSetAdded: () => void;
}

const ExerciseForm: React.FC<ExerciseFormProps> = ({ sessionId, userId, accessToken, onSetAdded }) => {
  const [exerciseName, setExerciseName] = useState('');
  const [reps, setReps] = useState('');
  const [weight, setWeight] = useState('');
  const [suggestions, setSuggestions] = useState<ExerciseSuggestion[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  
  const exerciseInputRef = useRef<HTMLInputElement>(null);
  const suggestionsRef = useRef<HTMLDivElement>(null);

  const debouncedSearch = debounce(async (query: string) => {
    if (query.length > 1) {
      try {
        const response = await api.getExerciseSuggestions(query);
        if (response.success && response.data) {
          setSuggestions(response.data);
          setShowSuggestions(true);
          setSelectedIndex(-1);
        }
      } catch (error) {
        console.error('Error fetching suggestions:', error);
      }
    } else {
      setSuggestions([]);
      setShowSuggestions(false);
    }
  }, 300);

  useEffect(() => {
    debouncedSearch(exerciseName);
  }, [exerciseName]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        exerciseInputRef.current &&
        !exerciseInputRef.current.contains(event.target as Node) &&
        suggestionsRef.current &&
        !suggestionsRef.current.contains(event.target as Node)
      ) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!showSuggestions || suggestions.length === 0) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex(prev => (prev < suggestions.length - 1 ? prev + 1 : 0));
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(prev => (prev > 0 ? prev - 1 : suggestions.length - 1));
        break;
      case 'Enter':
        if (selectedIndex >= 0) {
          e.preventDefault();
          selectSuggestion(suggestions[selectedIndex].name);
        }
        break;
      case 'Escape':
        setShowSuggestions(false);
        setSelectedIndex(-1);
        break;
    }
  };

  const selectSuggestion = (name: string) => {
    setExerciseName(name);
    setShowSuggestions(false);
    setSelectedIndex(-1);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!sessionId) {
      alert('Please select a workout session first');
      return;
    }

    if (!exerciseName.trim() || !reps || !weight) {
      alert('Please fill in all fields');
      return;
    }

    const repsNum = parseInt(reps);
    const weightNum = parseFloat(weight);

    if (repsNum <= 0 || weightNum <= 0) {
      alert('Please enter valid positive numbers');
      return;
    }

    setIsLoading(true);

    try {
      const response = await api.addSet(sessionId, exerciseName.trim(), repsNum, weightNum, true, userId, accessToken);
      
      if (response.success) {
        setExerciseName('');
        setReps('');
        setWeight('');
        onSetAdded();
      } else {
        alert(response.detail || 'Failed to add set');
      }
    } catch (error) {
      alert('Error adding set');
    } finally {
      setIsLoading(false);
    }
  };

  if (!sessionId) {
    return (
      <div className="card p-6">
        <div className="text-center py-8">
          <p className="text-gray-500">Select a workout session to start adding exercises</p>
        </div>
      </div>
    );
  }

  return (
    <div className="card p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-6">Add Exercise Set</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="relative">
            <label htmlFor="exercise" className="block text-sm font-medium text-gray-700 mb-1">
              Exercise
            </label>
            <input
              ref={exerciseInputRef}
              id="exercise"
              type="text"
              value={exerciseName}
              onChange={(e) => setExerciseName(e.target.value)}
              onKeyDown={handleKeyDown}
              className="input"
              placeholder="Enter exercise name"
              autoComplete="off"
              required
            />
            
            {showSuggestions && suggestions.length > 0 && (
              <div
                ref={suggestionsRef}
                className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto"
              >
                {suggestions.map((suggestion, index) => (
                  <button
                    key={suggestion.name}
                    type="button"
                    onClick={() => selectSuggestion(suggestion.name)}
                    className={`w-full text-left px-3 py-2 hover:bg-gray-50 ${
                      index === selectedIndex ? 'bg-gray-100' : ''
                    }`}
                  >
                    <div className="font-medium text-gray-900">{suggestion.name}</div>
                    <div className="text-xs text-gray-500">
                      {Math.round(suggestion.similarity * 100)}% match
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>

          <div>
            <label htmlFor="reps" className="block text-sm font-medium text-gray-700 mb-1">
              Reps
            </label>
            <input
              id="reps"
              type="number"
              value={reps}
              onChange={(e) => setReps(e.target.value)}
              className="input"
              placeholder="0"
              min="1"
              required
            />
          </div>

          <div>
            <label htmlFor="weight" className="block text-sm font-medium text-gray-700 mb-1">
              Weight (kg)
            </label>
            <input
              id="weight"
              type="number"
              value={weight}
              onChange={(e) => setWeight(e.target.value)}
              className="input"
              placeholder="0"
              min="0"
              step="0.5"
              required
            />
          </div>

          <div className="flex items-end">
            <button
              type="submit"
              disabled={isLoading}
              className="btn btn-primary w-full"
            >
              {isLoading ? 'Adding...' : 'Add Set'}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
};

export default ExerciseForm;
