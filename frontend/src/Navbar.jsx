import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LogOut, User, Menu, X, Sparkles, Settings, Database } from 'lucide-react';

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [open, setOpen] = React.useState(false);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const isActive = (path) => location.pathname === path;
  const navLinkClass = (path) =>
    `px-3 py-2 rounded-lg text-sm font-medium transition-all ${
      isActive(path)
        ? 'text-primary-700 bg-primary-50'
        : 'text-gray-600 hover:text-primary-600 hover:bg-gray-50'
    }`;

  return (
    <nav className="bg-white/80 backdrop-blur-lg shadow-sm border-b border-gray-100 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link to="/" className="flex items-center space-x-2.5 group">
              <div className="w-9 h-9 rounded-xl gradient-bg flex items-center justify-center shadow-sm group-hover:shadow-md transition-shadow pulse-glow">
                <Sparkles className="text-white" size={18} />
              </div>
              <span className="font-extrabold text-xl text-gray-900 hidden sm:block tracking-tight">
                Interview<span className="gradient-text">AI</span>
              </span>
            </Link>
          </div>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center space-x-1">
            {!user ? (
              <>
                <Link to="/login" className={navLinkClass('/login')}>
                  Login
                </Link>
                <Link to="/register" className="gradient-bg text-white px-5 py-2 rounded-xl text-sm font-semibold hover:opacity-90 transition-all shadow-sm ml-2">
                  Get Started
                </Link>
              </>
            ) : (
              <>
                {user.role === 'student' && (
                  <>
                    <Link to="/dashboard" className={navLinkClass('/dashboard')}>
                      Dashboard
                    </Link>
                    <Link to="/mock-interview" className={navLinkClass('/mock-interview')}>
                      Practice
                    </Link>
                    <Link to="/profile-builder" className={navLinkClass('/profile-builder')}>
                      Profile Builder
                    </Link>
                  </>
                )}
                {(user.role === 'hr' || user.role === 'admin') && (
                  <>
                    <Link to="/hr" className={navLinkClass('/hr')}>
                      Dashboard
                    </Link>
                    <Link to="/hr/create-session" className={navLinkClass('/hr/create-session')}>
                      New Session
                    </Link>
                  </>
                )}
                <div className="flex items-center space-x-3 ml-4 pl-4 border-l border-gray-200">
                  <div className="flex items-center space-x-2">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-400 to-purple-500 flex items-center justify-center">
                      <span className="text-white text-xs font-bold">{user.name?.charAt(0).toUpperCase()}</span>
                    </div>
                    <div className="hidden lg:block">
                      <span className="text-sm font-medium text-gray-700">{user.name}</span>
                      <span className="text-xs bg-primary-50 text-primary-700 px-2 py-0.5 rounded-full capitalize ml-2">{user.role}</span>
                    </div>
                  </div>
                  <Link to="/profile" className="p-2 text-gray-400 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-all" title="Account Settings">
                    <Settings size={18} />
                  </Link>
                  <button onClick={handleLogout} className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-all" title="Logout">
                    <LogOut size={18} />
                  </button>
                </div>
              </>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center">
            <button onClick={() => setOpen(!open)} className="p-2 text-gray-500 hover:bg-gray-100 rounded-lg transition">
              {open ? <X size={22} /> : <Menu size={22} />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Nav */}
      {open && (
        <div className="md:hidden bg-white/95 backdrop-blur-lg border-t border-gray-100 fade-in">
          <div className="px-3 pt-3 pb-4 space-y-1">
            {!user ? (
              <>
                <Link to="/login" onClick={() => setOpen(false)} className="block px-4 py-3 text-gray-700 hover:bg-gray-50 rounded-xl font-medium">Login</Link>
                <Link to="/register" onClick={() => setOpen(false)} className="block px-4 py-3 gradient-bg text-white rounded-xl font-medium text-center">Get Started</Link>
              </>
            ) : (
              <>
                <div className="flex items-center gap-3 px-4 py-3 mb-2">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-400 to-purple-500 flex items-center justify-center">
                    <span className="text-white font-bold">{user.name?.charAt(0).toUpperCase()}</span>
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">{user.name}</p>
                    <p className="text-xs text-gray-500 capitalize">{user.role}</p>
                  </div>
                </div>
                {user.role === 'student' && (
                  <>
                    <Link to="/dashboard" onClick={() => setOpen(false)} className="block px-4 py-3 text-gray-700 hover:bg-gray-50 rounded-xl">Dashboard</Link>
                    <Link to="/mock-interview" onClick={() => setOpen(false)} className="block px-4 py-3 text-gray-700 hover:bg-gray-50 rounded-xl">Practice</Link>
                    <Link to="/profile-builder" onClick={() => setOpen(false)} className="block px-4 py-3 text-gray-700 hover:bg-gray-50 rounded-xl">Profile Builder</Link>
                  </>
                )}
                {(user.role === 'hr' || user.role === 'admin') && (
                  <>
                    <Link to="/hr" onClick={() => setOpen(false)} className="block px-4 py-3 text-gray-700 hover:bg-gray-50 rounded-xl">Dashboard</Link>
                    <Link to="/hr/create-session" onClick={() => setOpen(false)} className="block px-4 py-3 text-gray-700 hover:bg-gray-50 rounded-xl">New Session</Link>
                  </>
                )}
                <Link to="/profile" onClick={() => setOpen(false)} className="block px-4 py-3 text-gray-700 hover:bg-gray-50 rounded-xl">Account Settings</Link>
                <button onClick={() => { handleLogout(); setOpen(false); }} className="block w-full text-left px-4 py-3 text-red-600 hover:bg-red-50 rounded-xl font-medium">
                  Logout
                </button>
              </>
            )}
          </div>
        </div>
      )}
    </nav>
  );
}
