import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { interviewAPI } from '../services/api';
import toast from 'react-hot-toast';
import { ArrowLeft, TrendingUp, Users, Award, AlertTriangle, BarChart3, Target } from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
  PieChart, Pie, Cell, LineChart, Line,
} from 'recharts';

const COLORS = ['#ef4444', '#f59e0b', '#3b82f6', '#8b5cf6', '#10b981'];

export default function HRAnalytics() {
  const [data, setData] = useState(null);
  const [paperData, setPaperData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      interviewAPI.getDashboardAnalytics(),
      interviewAPI.getPaperMetrics()
    ])
      .then(([r1, r2]) => {
        setData(r1.data);
        setPaperData(r2.data);
      })
      .catch(() => toast.error('Failed to load analytics'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <span className="inline-block w-10 h-10 border-3 border-primary-200 border-t-primary-600 rounded-full animate-spin" />
      </div>
    );
  }

  if (!data || data.total_sessions === 0) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-8">
        <Link to="/hr" className="inline-flex items-center gap-2 text-gray-500 hover:text-gray-700 mb-6">
          <ArrowLeft size={16} /> Back to Dashboard
        </Link>
        <div className="text-center py-20 text-gray-500">
          <BarChart3 size={48} className="mx-auto mb-4 text-gray-300" />
          <p className="font-medium">No interview data yet</p>
          <p className="text-sm mt-1">Complete some interviews to see analytics here.</p>
        </div>
      </div>
    );
  }

  const getScoreColor = (score) => {
    if (score >= 70) return 'text-green-600';
    if (score >= 40) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-8 slide-up">
        <div>
          <Link to="/hr" className="inline-flex items-center gap-2 text-gray-500 hover:text-gray-700 text-sm mb-2">
            <ArrowLeft size={14} /> Back to Dashboard
          </Link>
          <h1 className="text-3xl font-bold text-gray-900">Interview Analytics</h1>
          <p className="text-gray-500 mt-1">Aggregate performance across all your sessions</p>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
        {[
          { icon: Users, color: 'blue', label: 'Sessions', value: data.total_sessions },
          { icon: Users, color: 'indigo', label: 'Candidates', value: data.total_candidates },
          { icon: Award, color: 'green', label: 'Completed', value: data.completed_interviews },
          { icon: TrendingUp, color: 'purple', label: 'Avg Score', value: `${Math.round(data.avg_overall_score)}%` },
          { icon: Target, color: 'blue', label: 'Tech Avg', value: `${Math.round(data.avg_technical_score)}%` },
          { icon: Award, color: 'emerald', label: 'Pass Rate', value: `${Math.round(data.pass_rate)}%` },
        ].map((stat, i) => (
          <div key={i} className="bg-white rounded-2xl shadow-sm p-5 border border-gray-100 card-hover">
            <div className="flex items-center gap-3">
              <div className={`w-10 h-10 rounded-xl bg-${stat.color}-100 flex items-center justify-center`}>
                <stat.icon className={`text-${stat.color}-600`} size={18} />
              </div>
              <div>
                <p className="text-xs text-gray-500 font-medium">{stat.label}</p>
                <p className="text-xl font-bold text-gray-900">{stat.value}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid md:grid-cols-2 gap-6 mb-8">
        {/* Score Distribution */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
          <h3 className="font-bold text-gray-900 mb-4">Score Distribution</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={data.score_distribution}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="range" tick={{ fontSize: 12 }} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#667eea" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Top Failing Skills */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
          <h3 className="font-bold text-gray-900 mb-4">Top Failing Skills</h3>
          {data.top_failing_skills.length === 0 ? (
            <p className="text-gray-400 text-sm text-center py-10">No significant skill gaps detected</p>
          ) : (
            <div className="space-y-4">
              {data.top_failing_skills.map((s, i) => {
                const maxCount = data.top_failing_skills[0]?.fail_count || 1;
                const pct = (s.fail_count / maxCount) * 100;
                return (
                  <div key={i}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="font-medium text-gray-700">{s.skill}</span>
                      <span className="text-red-600 font-semibold">{s.fail_count} fails</span>
                    </div>
                    <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div className="h-full bg-red-400 rounded-full" style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6 mb-8">
        {/* Monthly Trend */}
        {data.monthly_trend.length > 0 && (
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
            <h3 className="font-bold text-gray-900 mb-4">Monthly Trend</h3>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={data.monthly_trend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" tick={{ fontSize: 11 }} />
                <YAxis yAxisId="left" orientation="left" domain={[0, 100]} />
                <YAxis yAxisId="right" orientation="right" />
                <Tooltip />
                <Legend />
                <Line yAxisId="left" type="monotone" dataKey="avg_score" stroke="#667eea" strokeWidth={2} name="Avg Score" dot={{ r: 4 }} />
                <Line yAxisId="right" type="monotone" dataKey="interviews" stroke="#10b981" strokeWidth={2} name="Interviews" dot={{ r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Role Breakdown */}
        {data.role_breakdown.length > 0 && (
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
            <h3 className="font-bold text-gray-900 mb-4">Performance by Role</h3>
            <div className="space-y-3">
              {data.role_breakdown.map((role, i) => (
                <div key={i} className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
                  <div>
                    <p className="font-semibold text-gray-800 text-sm">{role.role}</p>
                    <p className="text-xs text-gray-500">{role.count} candidates</p>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <p className={`text-sm font-bold ${getScoreColor(role.avg_score)}`}>
                        {Math.round(role.avg_score)}%
                      </p>
                      <p className="text-[10px] text-gray-400">avg score</p>
                    </div>
                    <div className="text-right">
                      <p className={`text-sm font-bold ${getScoreColor(role.pass_rate)}`}>
                        {Math.round(role.pass_rate)}%
                      </p>
                      <p className="text-[10px] text-gray-400">pass rate</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Research Paper Metrics Section */}
      {paperData && paperData.status === "success" && (
        <div className="mt-8">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Research Paper Metrics</h2>
            <button 
              onClick={() => {
                const blob = new Blob([JSON.stringify(paperData.data, null, 2)], {type: 'application/json'});
                const link = document.createElement('a');
                link.href = URL.createObjectURL(blob);
                link.download = `research_metrics_${new Date().toISOString().split('T')[0]}.json`;
                link.click();
              }}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 transition"
            >
              Export JSON for Paper
            </button>
          </div>
          
          <div className="grid md:grid-cols-3 gap-6">
            {/* Accuracy & Quality */}
            <div className="bg-gradient-to-br from-indigo-50 to-white rounded-2xl shadow-sm border border-indigo-100 p-6">
              <h3 className="font-bold text-indigo-900 mb-4 flex items-center gap-2"><Award size={18}/> Evaluation Accuracy</h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center border-b border-indigo-50 pb-2">
                  <span className="text-sm text-gray-600">Scoring Consistency</span>
                  <span className="font-bold text-indigo-700">{paperData.data.Accuracy_and_Quality.Scoring_Consistency}%</span>
                </div>
                <div className="flex justify-between items-center border-b border-indigo-50 pb-2">
                  <span className="text-sm text-gray-600">Avg Overall Score</span>
                  <span className="font-bold text-indigo-700">{paperData.data.Accuracy_and_Quality.Average_Overall_Score}%</span>
                </div>
              </div>
            </div>

            {/* Performance & Latency */}
            <div className="bg-gradient-to-br from-blue-50 to-white rounded-2xl shadow-sm border border-blue-100 p-6">
              <h3 className="font-bold text-blue-900 mb-4 flex items-center gap-2"><TrendingUp size={18}/> System Performance</h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center border-b border-blue-50 pb-2">
                  <span className="text-sm text-gray-600">Avg Response Latency</span>
                  <span className="font-bold text-blue-700">{paperData.data.Performance_and_Latency.Average_Response_Latency_Ms} ms</span>
                </div>
                <div className="flex justify-between items-center border-b border-blue-50 pb-2">
                  <span className="text-sm text-gray-600">Phase 1 Instant Eval</span>
                  <span className="font-bold text-blue-700">{paperData.data.Performance_and_Latency.Phase_1_Instant_Eval_Ms} ms</span>
                </div>
                <div className="flex justify-between items-center border-b border-blue-50 pb-2">
                  <span className="text-sm text-gray-600">Concurrent Tests Run</span>
                  <span className="font-bold text-blue-700">{paperData.data.Performance_and_Latency.Concurrent_Candidates_Tested}</span>
                </div>
              </div>
            </div>

            {/* RL & Advanced Features */}
            <div className="bg-gradient-to-br from-emerald-50 to-white rounded-2xl shadow-sm border border-emerald-100 p-6">
              <h3 className="font-bold text-emerald-900 mb-4 flex items-center gap-2"><Target size={18}/> Advanced Features</h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center border-b border-emerald-50 pb-2">
                  <span className="text-sm text-gray-600">Total RL Adaptations</span>
                  <span className="font-bold text-emerald-700">{paperData.data.RL_and_Features.Total_RL_Difficulty_Adaptations} drops/bumps</span>
                </div>
                <div className="flex justify-between items-center border-b border-emerald-50 pb-2">
                  <span className="text-sm text-gray-600">Proctoring Violations</span>
                  <span className="font-bold text-emerald-700">{paperData.data.RL_and_Features.Proctoring_Violations_Detected} flagged</span>
                </div>
                <div className="flex justify-between items-center border-b border-emerald-50 pb-2">
                  <span className="text-sm text-gray-600">XAI Explainability</span>
                  <span className="font-bold text-emerald-700">Active</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
