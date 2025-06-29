export interface User {
  user_id: string;
  access_token: string;
}

export interface WorkoutSession {
  id: number;
  name: string;
  created_at: string;
  user_id: string;
  set_count?: number;
}

export interface ExerciseSet {
  id: number;
  session_id: number;
  exercise_name: string;
  reps: number;
  weight: number;
  is_kg: boolean;
  created_at: string;
}

export interface ExerciseSuggestion {
  name: string;
  similarity: number;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  detail?: string;
  error?: string;
  message?: string;
  access_token?: string;
  user_id?: string;
}
