import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import Button from '@components/Button';
import Spinner from '@components/Spinner';
import { useAuth } from '@/context/AuthContext';

const AuthPage = () => {
  const navigate = useNavigate();
  const { isAuthenticated, isLoading, user, login, register } = useAuth();

  const [mode, setMode] = useState('login');
  const [form, setForm] = useState({
    name: '',
    email: '',
    password: '',
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const title = useMemo(
    () => (mode === 'login' ? 'Welcome back' : 'Create your account'),
    [mode]
  );

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      navigate(user?.onboarding_completed ? '/dashboard' : '/onboarding', { replace: true });
    }
  }, [isAuthenticated, isLoading, navigate, user]);

  const handleInputChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setSubmitting(true);

    try {
      if (mode === 'register') {
        await register({
          name: form.name,
          email: form.email,
          password: form.password,
        });
      } else {
        await login({
          email: form.email,
          password: form.password,
        });
      }
    } catch (submitError) {
      setError(
        submitError?.response?.data?.detail ||
          'Authentication failed. Please check your credentials and try again.'
      );
    } finally {
      setSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-secondary-50">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-secondary-100 via-white to-primary-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-white border border-secondary-200 rounded-2xl shadow-hard p-8">
        <div className="mb-6 text-center">
          <h1 className="font-heading font-bold text-3xl text-secondary-900 mb-2">{title}</h1>
          <p className="text-secondary-600 text-sm">
            {mode === 'login'
              ? 'Sign in to continue your personalized learning journey.'
              : 'Start your personalized project-based learning setup.'}
          </p>
        </div>

        <form className="space-y-4" onSubmit={handleSubmit}>
          {mode === 'register' && (
            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-1" htmlFor="name">
                Full name
              </label>
              <input
                id="name"
                name="name"
                type="text"
                value={form.name}
                onChange={handleInputChange}
                required
                className="w-full px-4 py-3 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-1" htmlFor="email">
              Email
            </label>
            <input
              id="email"
              name="email"
              type="email"
              value={form.email}
              onChange={handleInputChange}
              required
              className="w-full px-4 py-3 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-1" htmlFor="password">
              Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              value={form.password}
              onChange={handleInputChange}
              required
              minLength={8}
              className="w-full px-4 py-3 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>

          {error && <p className="text-sm text-error-DEFAULT">{error}</p>}

          <Button type="submit" className="w-full" disabled={submitting}>
            {submitting ? (
              <span className="inline-flex items-center gap-2">
                <Spinner size="sm" className="border-white/30 border-t-white" />
                Processing...
              </span>
            ) : mode === 'login' ? (
              'Sign in'
            ) : (
              'Create account'
            )}
          </Button>
        </form>

        <button
          type="button"
          className="mt-6 w-full text-sm text-primary-600 hover:text-primary-700 font-medium"
          onClick={() => {
            setMode((prev) => (prev === 'login' ? 'register' : 'login'));
            setError('');
          }}
        >
          {mode === 'login' ? 'No account yet? Create one' : 'Already have an account? Sign in'}
        </button>
      </div>
    </div>
  );
};

export default AuthPage;
