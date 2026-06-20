import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import { User, Mail, Save, Trash2, AlertTriangle, Shield } from 'lucide-react';

export default function ProfilePage() {
  const { user, updateProfile, deleteAccount } = useAuth();
  const navigate = useNavigate();

  const [name, setName] = useState(user?.name || '');
  const [email, setEmail] = useState(user?.email || '');
  const [saving, setSaving] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const handleUpdate = async (e) => {
    e.preventDefault();
    if (!name.trim() || !email.trim()) {
      toast.error('Name and email are required');
      return;
    }

    setSaving(true);
    try {
      const updates = {};
      if (name !== user.name) updates.name = name;
      if (email !== user.email) updates.email = email;

      if (Object.keys(updates).length === 0) {
        toast('No changes to save');
        setSaving(false);
        return;
      }

      await updateProfile(updates);
      toast.success('Profile updated successfully');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    setDeleting(true);
    try {
      await deleteAccount();
      toast.success('Account deleted');
      navigate('/');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to delete account');
      setDeleting(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto px-4 py-10">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Account Settings</h1>
        <p className="text-gray-500 mt-1">Manage your profile and account</p>
      </div>

      {/* Profile Info */}
      <form onSubmit={handleUpdate} className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8 mb-8">
        <div className="flex items-center gap-4 mb-8">
          <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary-400 to-purple-500 flex items-center justify-center">
            <span className="text-white text-2xl font-bold">{user?.name?.charAt(0).toUpperCase()}</span>
          </div>
          <div>
            <h2 className="text-xl font-semibold text-gray-900">{user?.name}</h2>
            <span className="text-xs bg-primary-50 text-primary-700 px-2.5 py-1 rounded-full capitalize font-medium">{user?.role}</span>
          </div>
        </div>

        <div className="space-y-5">
          <div>
            <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
              <User size={16} />
              Name
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition"
              required
              minLength={2}
            />
          </div>
          <div>
            <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
              <Mail size={16} />
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition"
              required
            />
          </div>
          <div>
            <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
              <Shield size={16} />
              Role
            </label>
            <input
              type="text"
              value={user?.role}
              disabled
              className="w-full px-4 py-3 border border-gray-100 rounded-xl bg-gray-50 text-gray-500 capitalize cursor-not-allowed"
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={saving}
          className="mt-6 w-full gradient-bg text-white py-3 rounded-xl font-semibold flex items-center justify-center gap-2 hover:opacity-90 transition disabled:opacity-50"
        >
          <Save size={18} />
          {saving ? 'Saving...' : 'Save Changes'}
        </button>
      </form>

      {/* Danger Zone */}
      <div className="bg-white rounded-2xl shadow-sm border border-red-100 p-8">
        <h3 className="text-lg font-semibold text-red-600 flex items-center gap-2 mb-2">
          <AlertTriangle size={20} />
          Danger Zone
        </h3>
        <p className="text-gray-500 text-sm mb-5">
          Once you delete your account, all your data including interview history and reports will be permanently removed. This action cannot be undone.
        </p>

        {!showDeleteConfirm ? (
          <button
            onClick={() => setShowDeleteConfirm(true)}
            className="px-5 py-2.5 bg-red-50 text-red-600 rounded-xl font-semibold hover:bg-red-100 transition flex items-center gap-2"
          >
            <Trash2 size={16} />
            Delete Account
          </button>
        ) : (
          <div className="bg-red-50 rounded-xl p-5 border border-red-200">
            <p className="text-red-700 font-medium mb-4">Are you sure? This cannot be undone.</p>
            <div className="flex gap-3">
              <button
                onClick={handleDelete}
                disabled={deleting}
                className="px-5 py-2.5 bg-red-600 text-white rounded-xl font-semibold hover:bg-red-700 transition disabled:opacity-50"
              >
                {deleting ? 'Deleting...' : 'Yes, Delete My Account'}
              </button>
              <button
                onClick={() => setShowDeleteConfirm(false)}
                className="px-5 py-2.5 bg-white text-gray-700 rounded-xl font-semibold hover:bg-gray-50 transition border border-gray-200"
              >
                Cancel
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
