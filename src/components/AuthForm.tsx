import React, { useState } from 'react';
import { api } from '../utils/api';

interface AuthFormProps {
  onLogin: (user: { user_id: string; access_token: string }) => void;
}

const AuthForm: React.FC<AuthFormProps> = ({ onLogin }) => {
  const [view, setView] = useState<'login' | 'signup' | 'forgot'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage('');

    try {
      let response;
      
      if (view === 'login') {
        response = await api.login(email, password);
        if (response.success && response.user_id && response.access_token) {
          onLogin({ user_id: response.user_id, access_token: response.access_token });
        } else {
          setMessage('Login failed. Please check your credentials.');
        }
      } else if (view === 'signup') {
        response = await api.signup(email, password);
        if (response.success) {
          setMessage('Account created! Please check your email for verification.');
          setView('login');
        } else {
          setMessage(response.detail || 'Signup failed. Please try again.');
        }
      } else if (view === 'forgot') {
        response = await api.forgotPassword(email);
        if (response.success) {
          setMessage('Password reset email sent! Check your inbox.');
          setView('login');
        } else {
          setMessage(response.detail || 'Failed to send reset email.');
        }
      }
    } catch (error) {
      setMessage('An error occurred. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleTestMode = () => {
    // Use a mock user for testing (using proper UUID format)
    onLogin({ 
      user_id: '123e4567-e89b-12d3-a456-426614174000', 
      access_token: 'test-token-456'
    });
  };

  const getTitle = () => {
    switch (view) {
      case 'signup': return 'Create Account';
      case 'forgot': return 'Reset Password';
      default: return 'Welcome Back';
    }
  };

  const getButtonText = () => {
    switch (view) {
      case 'signup': return 'Create Account';
      case 'forgot': return 'Send Reset Email';
      default: return 'Sign In';
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="card w-full max-w-md p-8">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">{getTitle()}</h1>
          <p className="text-gray-600">Track your workouts with precision</p>
        </div>

        {message && (
          <div className={`mb-6 p-3 rounded-lg text-sm ${
            message.includes('success') || message.includes('sent') || message.includes('created')
              ? 'bg-green-50 text-green-700 border border-green-200'
              : 'bg-red-50 text-red-700 border border-red-200'
          }`}>
            {message}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="input"
              placeholder="Enter your email"
              required
            />
          </div>

          {view !== 'forgot' && (
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="input"
                placeholder="Enter your password"
                required
              />
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading}
            className="btn btn-primary w-full py-3"
          >
            {isLoading ? 'Loading...' : getButtonText()}
          </button>
        </form>

        <div className="mt-6 text-center space-y-2">
          {view === 'login' && (
            <>
              <button
                onClick={() => setView('forgot')}
                className="text-gray-600 hover:text-gray-900 text-sm"
              >
                Forgot your password?
              </button>
              <div className="text-gray-500">·</div>
              <button
                onClick={() => setView('signup')}
                className="text-gray-600 hover:text-gray-900 text-sm"
              >
                Create new account
              </button>
              <div className="text-gray-500">·</div>
              <button
                onClick={handleTestMode}
                className="text-blue-600 hover:text-blue-800 text-sm font-medium"
              >
                Test Mode (Demo)
              </button>
            </>
          )}
          
          {view !== 'login' && (
            <button
              onClick={() => setView('login')}
              className="text-gray-600 hover:text-gray-900 text-sm"
            >
              Back to sign in
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default AuthForm;
