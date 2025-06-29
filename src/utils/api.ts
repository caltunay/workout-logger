import { ApiResponse } from '../types';

export const api = {
  // Auth endpoints
  login: async (email: string, password: string): Promise<ApiResponse> => {
    const response = await fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    return response.json();
  },

  signup: async (email: string, password: string): Promise<ApiResponse> => {
    const response = await fetch('/api/signup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    return response.json();
  },

  forgotPassword: async (email: string): Promise<ApiResponse> => {
    const response = await fetch('/api/forgot-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email })
    });
    return response.json();
  },

  // Exercise endpoints
  getExerciseSuggestions: async (query: string, limit = 10): Promise<ApiResponse> => {
    const response = await fetch(`/api/exercise-suggestions?query=${encodeURIComponent(query)}&limit=${limit}`);
    return response.json();
  },

  // Workout endpoints
  createSession: async (userId: string, accessToken: string, workoutDate: string): Promise<ApiResponse> => {
    const response = await fetch('/api/create-session', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, access_token: accessToken, workout_date: workoutDate })
    });
    return response.json();
  },

  getSessionsByDate: async (userId: string, accessToken: string, date: string): Promise<ApiResponse> => {
    const response = await fetch(`/api/sessions-by-date?user_id=${userId}&access_token=${accessToken}&date=${date}`);
    return response.json();
  },

  getCurrentSession: async (userId: string, accessToken: string): Promise<ApiResponse> => {
    const response = await fetch(`/api/current-session?user_id=${userId}&access_token=${accessToken}`);
    return response.json();
  },

  getAllSessions: async (userId: string, accessToken: string): Promise<ApiResponse> => {
    const response = await fetch(`/api/all-sessions?user_id=${userId}&access_token=${accessToken}`);
    return response.json();
  },

  getSessionSets: async (sessionId: number, userId: string, accessToken: string): Promise<ApiResponse> => {
    const response = await fetch(`/api/session-sets?session_id=${sessionId}&user_id=${userId}&access_token=${accessToken}`);
    return response.json();
  },

  addSet: async (sessionId: number, exerciseName: string, reps: number, weight: number, isKg: boolean, userId: string, accessToken: string): Promise<ApiResponse> => {
    const response = await fetch('/api/add-set', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        exercise_name: exerciseName,
        reps,
        weight,
        is_kg: isKg,
        user_id: userId,
        access_token: accessToken
      })
    });
    return response.json();
  },

  renameSession: async (sessionId: number, name: string, userId: string, accessToken: string): Promise<ApiResponse> => {
    const response = await fetch('/api/rename-session', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, name, user_id: userId, access_token: accessToken })
    });
    return response.json();
  },

  duplicateSet: async (setId: number, userId: string, accessToken: string): Promise<ApiResponse> => {
    const response = await fetch('/api/duplicate-set', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ set_id: setId, user_id: userId, access_token: accessToken })
    });
    return response.json();
  },

  editSet: async (setId: number, reps: number, weight: number, userId: string, accessToken: string): Promise<ApiResponse> => {
    const response = await fetch('/api/edit-set', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ set_id: setId, reps, weight, user_id: userId, access_token: accessToken })
    });
    return response.json();
  },

  removeSet: async (setId: number, userId: string, accessToken: string): Promise<ApiResponse> => {
    const response = await fetch('/api/remove-set', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ set_id: setId, user_id: userId, access_token: accessToken })
    });
    return response.json();
  }
};
