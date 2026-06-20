import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Brain, Video, BarChart3, Mail, Shield, Zap, ArrowRight, Sparkles, Users, CheckCircle } from 'lucide-react';

const features = [
  { icon: Brain, title: 'AI-Powered Questions', desc: 'Dynamic question generation using advanced AI with adaptive difficulty that adjusts to your skill level.', color: 'from-violet-500 to-purple-600' },
  { icon: Video, title: 'Live Video Interviews', desc: 'WebRTC-powered real-time video sessions with camera analysis for confidence detection.', color: 'from-blue-500 to-cyan-500' },
  { icon: BarChart3, title: 'Smart Evaluation', desc: 'NLP semantic analysis, keyword matching, and multi-dimensional scoring with detailed feedback.', color: 'from-emerald-500 to-teal-500' },
  { icon: Mail, title: 'Bulk Invitations', desc: 'Generate unique interview links and send automated email invites to candidates at scale.', color: 'from-orange-500 to-amber-500' },
  { icon: Shield, title: 'Secure & Private', desc: 'JWT authentication, token-based access, bcrypt hashing, and role-based permissions.', color: 'from-slate-600 to-gray-700' },
  { icon: Zap, title: '100% Free & Open', desc: 'Built entirely with free, open-source tools. No paid APIs. Self-host anywhere.', color: 'from-pink-500 to-rose-500' },
];

const stats = [
  { value: '100%', label: 'Free & Open Source' },
  { value: 'AI', label: 'Powered by Groq' },
  { value: '2', label: 'Interview Rounds' },
  { value: 'PDF', label: 'Detailed Reports' },
];

export default function Landing() {
  const { user } = useAuth();

  return (
    <div className="overflow-hidden">
      {/* Hero */}
      <section className="relative min-h-[90vh] flex items-center">
        {/* Background */}
        <div className="absolute inset-0 gradient-bg" />
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmZmZmYiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PHBhdGggZD0iTTM2IDM0djItSDI0di0yaDEyek0zNiAyNHYySDI0di0yaDEyeiIvPjwvZz48L2c+PC9zdmc+')] opacity-30" />
        
        {/* Floating decorative elements */}
        <div className="absolute top-20 left-10 w-72 h-72 bg-white/5 rounded-full blur-3xl float" />
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-purple-300/10 rounded-full blur-3xl float" style={{ animationDelay: '2s' }} />

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 text-center">
          <div className="slide-up">
            <div className="inline-flex items-center gap-2 bg-white/10 backdrop-blur-sm border border-white/20 rounded-full px-4 py-2 mb-8">
              <Sparkles size={16} className="text-yellow-300" />
              <span className="text-white/90 text-sm font-medium">AI-Powered Interview Platform</span>
            </div>
            
            <h1 className="text-4xl sm:text-5xl lg:text-7xl font-black mb-6 leading-[1.1] text-white tracking-tight">
              Ace Your Next<br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-yellow-200 via-pink-200 to-cyan-200">
                Interview with AI
              </span>
            </h1>
            
            <p className="text-lg sm:text-xl text-purple-100/90 max-w-2xl mx-auto mb-12 leading-relaxed">
              Practice with an AI interviewer that adapts to your skill level. 
              Companies can conduct real interviews with automated evaluation and detailed reports.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              {!user ? (
                <>
                  <Link to="/register" className="group bg-white text-gray-900 px-8 py-4 rounded-2xl font-bold text-lg hover:bg-gray-50 transition-all shadow-xl shadow-black/10 flex items-center justify-center gap-2">
                    Get Started Free
                    <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" />
                  </Link>
                  <Link to="/login" className="border-2 border-white/30 text-white px-8 py-4 rounded-2xl font-semibold text-lg hover:bg-white/10 backdrop-blur-sm transition-all">
                    Sign In
                  </Link>
                </>
              ) : (
                <Link
                  to={user.role === 'hr' ? '/hr' : '/dashboard'}
                  className="group bg-white text-gray-900 px-8 py-4 rounded-2xl font-bold text-lg hover:bg-gray-50 transition-all shadow-xl flex items-center justify-center gap-2"
                >
                  Go to Dashboard
                  <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" />
                </Link>
              )}
            </div>
          </div>

          {/* Stats bar */}
          <div className="mt-20 grid grid-cols-2 sm:grid-cols-4 gap-4 max-w-3xl mx-auto fade-in" style={{ animationDelay: '0.4s' }}>
            {stats.map((s, i) => (
              <div key={i} className="glass rounded-2xl p-4 text-center">
                <div className="text-2xl font-bold text-white">{s.value}</div>
                <div className="text-xs text-white/60 mt-1">{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-24 bg-white relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <span className="text-sm font-semibold text-primary-600 uppercase tracking-wider">Features</span>
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mt-3 mb-4">
              Everything You Need
            </h2>
            <p className="text-gray-500 max-w-2xl mx-auto text-lg">
              A complete platform for AI-driven interview preparation and corporate recruitment.
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((f, i) => (
              <div key={i} className="group p-7 rounded-2xl border border-gray-100 bg-white card-hover">
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${f.color} flex items-center justify-center mb-5 group-hover:scale-110 transition-transform`}>
                  <f.icon className="text-white" size={22} />
                </div>
                <h3 className="text-lg font-bold text-gray-900 mb-2">{f.title}</h3>
                <p className="text-gray-500 text-sm leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-24 bg-gradient-to-b from-gray-50 to-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <span className="text-sm font-semibold text-primary-600 uppercase tracking-wider">How it works</span>
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mt-3">Simple 4-Step Process</h2>
          </div>
          <div className="grid md:grid-cols-2 gap-12 lg:gap-20">
            {/* Students */}
            <div className="bg-white rounded-3xl p-8 shadow-sm border border-gray-100 card-hover">
              <div className="flex items-center gap-3 mb-8">
                <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center">
                  <Users className="text-white" size={22} />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-gray-900">For Students</h3>
                  <p className="text-sm text-gray-500">Practice & improve</p>
                </div>
              </div>
              <div className="space-y-5">
                {[
                  { step: 'Sign up and select your target role & difficulty', icon: '🎯' },
                  { step: 'AI generates dynamic, role-specific questions', icon: '🤖' },
                  { step: 'Answer via voice with camera for confidence analysis', icon: '🎤' },
                  { step: 'Get detailed PDF report with scores & improvement tips', icon: '📊' },
                ].map((item, i) => (
                  <div key={i} className="flex items-start gap-4">
                    <div className="flex-shrink-0 w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center text-lg">
                      {item.icon}
                    </div>
                    <div className="pt-2">
                      <p className="text-gray-700 text-sm font-medium">{item.step}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            {/* HR */}
            <div className="bg-white rounded-3xl p-8 shadow-sm border border-gray-100 card-hover">
              <div className="flex items-center gap-3 mb-8">
                <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center">
                  <BarChart3 className="text-white" size={22} />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-gray-900">For Companies</h3>
                  <p className="text-sm text-gray-500">Recruit efficiently</p>
                </div>
              </div>
              <div className="space-y-5">
                {[
                  { step: 'Create session with job role, JD & schedule', icon: '📋' },
                  { step: 'Send bulk email invitations to candidates', icon: '📧' },
                  { step: 'Candidates join via unique links for AI interview', icon: '🔗' },
                  { step: 'View scores, rankings & download evaluation reports', icon: '🏆' },
                ].map((item, i) => (
                  <div key={i} className="flex items-start gap-4">
                    <div className="flex-shrink-0 w-10 h-10 rounded-xl bg-purple-50 flex items-center justify-center text-lg">
                      {item.icon}
                    </div>
                    <div className="pt-2">
                      <p className="text-gray-700 text-sm font-medium">{item.step}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 relative">
        <div className="absolute inset-0 gradient-bg" />
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmZmZmYiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PHBhdGggZD0iTTM2IDM0djItSDI0di0yaDEyek0zNiAyNHYySDI0di0yaDEyeiIvPjwvZz48L2c+PC9zdmc+')] opacity-30" />
        <div className="relative max-w-4xl mx-auto px-4 text-center">
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-6">
            Ready to ace your next interview?
          </h2>
          <p className="text-lg text-purple-100/90 mb-10 max-w-2xl mx-auto">
            Join thousands of candidates using AI to prepare smarter, not harder.
          </p>
          {!user && (
            <Link
              to="/register"
              className="group inline-flex items-center gap-2 bg-white text-gray-900 px-10 py-4 rounded-2xl font-bold text-lg hover:bg-gray-50 transition-all shadow-xl shadow-black/10"
            >
              Start Practicing Free
              <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" />
            </Link>
          )}
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-950 text-gray-400 py-14">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg gradient-bg flex items-center justify-center">
                <span className="text-white font-bold text-xs">AI</span>
              </div>
              <span className="font-bold text-white">InterviewAI</span>
            </div>
            <p className="text-sm text-center">Built with React, FastAPI, Groq & WebRTC — 100% Open Source</p>
            <div className="flex items-center gap-1 text-xs">
              <CheckCircle size={14} className="text-green-500" />
              <span>Free forever</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
