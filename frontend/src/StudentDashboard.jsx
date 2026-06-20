import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { mockAPI } from '../services/api';
import { Play, History, Trophy, TrendingUp, Sparkles, ArrowRight, BookOpen } from 'lucide-react';

export default function StudentDashboard() {
  const { user } = useAuth();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    mockAPI.history().then((r) => setHistory(r.data)).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const completed = history.filter((h) => h.status === 'completed');
  const avgScore = completed.length
    ? Math.round(completed.reduce((a, b) => a + (b.technical_score || 0), 0) / completed.length)
    : 0;

  const scoreColor = avgScore >= 75 ? 'text-green-600' : avgScore >= 50 ? 'text-yellow-600' : 'text-red-500';

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Greeting */}
      <div className="mb-8 slide-up">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-2xl">👋</span>
          <h1 className="text-3xl font-bold text-gray-900">Welcome back, {user?.name}!</h1>
        </div>
        <p className="text-gray-500 mt-1 ml-10">Ready for your next practice session?</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mb-10">
        {[
          { icon: History, color: 'blue', label: 'Total Sessions', value: history.length },
          { icon: Trophy, color: 'green', label: 'Completed', value: completed.length },
          { icon: TrendingUp, color: 'purple', label: 'Avg Score', value: `${avgScore}%`, special: true },
        ].map((stat, i) => (
          <div key={i} className="bg-white rounded-2xl shadow-sm p-6 border border-gray-100 card-hover">
            <div className="flex items-center space-x-4">
              <div className={`w-12 h-12 rounded-xl bg-${stat.color}-100 flex items-center justify-center`}>
                <stat.icon className={`text-${stat.color}-600`} size={22} />
              </div>
              <div>
                <p className="text-sm text-gray-500 font-medium">{stat.label}</p>
                <p className={`text-2xl font-bold ${stat.special ? scoreColor : 'text-gray-900'}`}>{stat.value}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Start Practice CTA */}
      <div className="relative overflow-hidden bg-gradient-to-r from-primary-500 via-primary-600 to-purple-600 rounded-2xl p-8 text-white mb-10 shadow-lg">
        <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full -translate-y-1/2 translate-x-1/4" />
        <div className="absolute bottom-0 left-1/3 w-40 h-40 bg-white/5 rounded-full translate-y-1/2" />
        <div className="flex flex-col sm:flex-row items-center justify-between relative z-10">
          <div className="flex items-start gap-4">
            <div className="w-14 h-14 bg-white/20 backdrop-blur rounded-2xl flex items-center justify-center flex-shrink-0">
              <Sparkles size={26} />
            </div>
            <div>
              <h2 className="text-2xl font-bold mb-1">Start a Mock Interview</h2>
              <p className="text-purple-100">Practice with AI-generated questions tailored to your target role and difficulty.</p>
            </div>
          </div>
          <Link
            to="/mock-interview"
            className="mt-5 sm:mt-0 bg-white text-primary-600 px-7 py-3.5 rounded-xl font-semibold flex items-center gap-2 hover:bg-gray-50 transition-all shadow-md hover:shadow-lg flex-shrink-0"
          >
            <Play size={18} />
            <span>Start Practice</span>
          </Link>
        </div>
      </div>

      {/* History */}
      <div>
        <div className="flex items-center gap-2 mb-5">
          <BookOpen size={20} className="text-gray-400" />
          <h2 className="text-xl font-bold text-gray-900">Interview History</h2>
        </div>
        {loading ? (
          <div className="flex justify-center py-12">
            <span className="inline-block w-8 h-8 border-3 border-primary-200 border-t-primary-600 rounded-full animate-spin" />
          </div>
        ) : history.length === 0 ? (
          <div className="bg-white/80 backdrop-blur rounded-2xl p-12 text-center border border-gray-100">
            <div className="w-16 h-16 bg-gray-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <History size={28} className="text-gray-300" />
            </div>
            <p className="text-gray-500 mb-1 font-medium">No interviews yet</p>
            <p className="text-gray-400 text-sm">Start your first practice session to see your progress here.</p>
          </div>
        ) : (
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="bg-gray-50/80">
                    <th className="px-6 py-3.5 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Role</th>
                    <th className="px-6 py-3.5 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Round</th>
                    <th className="px-6 py-3.5 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Questions</th>
                    <th className="px-6 py-3.5 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Status</th>
                    <th className="px-6 py-3.5 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Date</th>
                    <th className="px-6 py-3.5"></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {history.map((h) => (
                    <tr key={h.session_id} className="hover:bg-primary-50/30 transition-colors">
                      <td className="px-6 py-4 text-sm font-semibold text-gray-900">{h.job_role}</td>
                      <td className="px-6 py-4">
                        <span className={`text-xs px-2.5 py-1 rounded-full font-medium capitalize ${
                          h.current_round === 'HR' ? 'bg-purple-50 text-purple-600'
                            : 'bg-blue-50 text-blue-600'
                        }`}>
                          {h.current_round}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-gray-500">{h.questions_answered} answered</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${
                          h.status === 'completed'
                            ? 'bg-green-100 text-green-700'
                            : 'bg-yellow-100 text-yellow-700'
                        }`}>
                          {h.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500">
                        {new Date(h.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4">
                        {h.status === 'completed' && (
                          <Link to={`/report/${h.session_id}`} className="text-primary-600 text-sm font-semibold hover:text-primary-700 flex items-center gap-1 transition">
                            Report <ArrowRight size={14} />
                          </Link>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
