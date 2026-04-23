import React, { useState } from 'react';
import Button from '@components/Button';
import { useAuth } from '@/context/AuthContext';
import usersService from '@services/users';

const SettingsPage = () => {
  const { user, refreshUser } = useAuth();
  const [name, setName] = useState(user?.name || user?.full_name || '');
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const save = async (event) => {
    event.preventDefault();
    setIsSaving(true);
    setMessage('');
    setError('');
    try {
      await usersService.updateProfile({ full_name: name });
      await refreshUser();
      setMessage('Profile updated.');
    } catch {
      setError('Unable to update settings right now.');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="font-heading font-bold text-3xl mb-2">Settings</h1>
        <p className="text-secondary-600">Manage your account profile and preferences.</p>
      </div>

      <form onSubmit={save} className="bg-white border border-secondary-200 rounded-xl p-6 space-y-4">
        <div>
          <label className="text-sm font-medium text-secondary-700">Email</label>
          <input
            value={user?.email || ''}
            disabled
            className="mt-1 w-full px-4 py-3 border border-secondary-300 rounded-lg bg-secondary-100"
          />
        </div>
        <div>
          <label className="text-sm font-medium text-secondary-700">Full Name</label>
          <input
            value={name}
            onChange={(event) => setName(event.target.value)}
            className="mt-1 w-full px-4 py-3 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
        {message && <p className="text-sm text-success-dark">{message}</p>}
        {error && <p className="text-sm text-error-DEFAULT">{error}</p>}
        <Button type="submit" disabled={isSaving}>
          {isSaving ? 'Saving...' : 'Save Settings'}
        </Button>
      </form>
    </div>
  );
};

export default SettingsPage;

