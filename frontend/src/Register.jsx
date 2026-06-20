import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import { UserPlus, ArrowRight, GraduationCap, Building2 } from 'lucide-react';

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: '', email: '', password: '', role: 'student' });
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const user = await register(form.name, form.email, form.password, form.role);
      toast.success('Account created!');
      navigate(user.role === 'hr' || user.role === 'admin' ? '/hr' : '/dashboard');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center px-4 py-8 relative overflow-hidden">
      {/* Background decorations */}
      <div className="absolute inset-0 bg-gradient-to-br from-purple-50 via-white to-primary-50" />
      <div className="absolute top-10 -right-32 w-72 h-72 bg-purple-200/25 rounded-full blur-3xl" />
      <div className="absolute bottom-10 -left-32 w-72 h-72 bg-primary-200/25 rounded-full blur-3xl" />

      <div className="w-full max-w-md relative z-10 slide-up">
        <div className="bg-white/80 backdrop-blur-xl rounded-2xl shadow-xl border border-white/50 p-8">
          <div className="text-center mb-8">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-purple-500 to-primary-600 flex items-center justify-center mx-auto mb-4 shadow-lg">
              <UserPlus className="text-white" size={24} />
            </div>
            <h1 className="text-2xl font-bold text-gray-900">Create Account</h1>
            <p className="text-gray-500 mt-1">Start your AI-powered interview journey</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1.5">Full Name</label>
              <input
                name="name"
                value={form.name}
                onChange={handleChange}
                required
                className="w-full px-4 py-3 bg-gray-50/80 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition-all"
                placeholder="John Doe"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1.5">Email</label>
              <input
                name="email"
                type="email"
                value={form.email}
                onChange={handleChange}
                required
                className="w-full px-4 py-3 bg-gray-50/80 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition-all"
                placeholder="you@example.com"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-1.5">Password</label>
              <input
                name="password"
                type="password"
                value={form.password}
                onChange={handleChange}
                required
                minLength={6}
                className="w-full px-4 py-3 bg-gray-50/80 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition-all"
                placeholder="Min 6 characters"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">I am a</label>
              <div className="grid grid-cols-2 gap-3">
                <label
                  className={`flex flex-col items-center p-4 rounded-xl border-2 cursor-pointer transition-all ${
                    form.role === 'student'
                      ? 'border-primary-500 bg-primary-50/80 shadow-sm'
                      : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  <input type="radio" name="role" value="student" checked={form.role === 'student'} onChange={handleChange} className="hidden" />
                  <GraduationCap size={28} className={form.role === 'student' ? 'text-primary-600' : 'text-gray-400'} />
                  <span className="text-sm font-semibold mt-2">Student</span>
                  <span className="text-xs text-gray-500 mt-0.5">Practice interviews</span>
                </label>
                <label
                  className={`flex flex-col items-center p-4 rounded-xl border-2 cursor-pointer transition-all ${
                    form.role === 'hr'
                      ? 'border-purple-500 bg-purple-50/80 shadow-sm'
                      : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  <input type="radio" name="role" value="hr" checked={form.role === 'hr'} onChange={handleChange} className="hidden" />
                  <Building2 size={28} className={form.role === 'hr' ? 'text-purple-600' : 'text-gray-400'} />
                  <span className="text-sm font-semibold mt-2">HR / Recruiter</span>
                  <span className="text-xs text-gray-500 mt-0.5">Conduct interviews</span>
                </label>
              </div>
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full gradient-bg text-white py-3 rounded-xl font-semibold hover:opacity-90 transition-all disabled:opacity-50 flex items-center justify-center gap-2 shadow-md hover:shadow-lg mt-2"
            >
              {loading ? (
                <span className="inline-block w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>Create Account <ArrowRight size={18} /></>
              )}
            </button>
          </form>

          <div className="mt-6 pt-6 border-t border-gray-100">
            <p className="text-center text-sm text-gray-500">
              Already have an account?{' '}
              <Link to="/login" className="text-primary-600 font-semibold hover:text-primary-700 transition">
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
