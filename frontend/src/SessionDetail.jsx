import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { interviewAPI, candidateAPI } from '../services/api';
import toast from 'react-hot-toast';
import { Mail, Users, Copy, Loader2, Eye, Calendar, Clock, Send, LogOut } from 'lucide-react';

export default function SessionDetail() {
  const { sessionId } = useParams();
  const [session, setSession] = useState(null);
  const [candidates, setCandidates] = useState([]);
  const [emailInput, setEmailInput] = useState('');
  const [loading, setLoading] = useState(true);
  const [inviting, setInviting] = useState(false);
  const [publicUrl, setPublicUrl] = useState(window.location.origin);
  const [showEndConfirm, setShowEndConfirm] = useState(false);
  const [endingSession, setEndingSession] = useState(false);

  const load = async () => {
    try {
      const [sRes, cRes, urlRes] = await Promise.all([
        interviewAPI.getSession(sessionId),
        interviewAPI.listCandidates(sessionId),
        candidateAPI.getPublicUrl(),
      ]);
      setSession(sRes.data);
      setCandidates(cRes.data);
      if (urlRes.data.public_url) setPublicUrl(urlRes.data.public_url);
    } catch {
      toast.error('Failed to load session');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [sessionId]);

  const handleInvite = async () => {
    const emails = emailInput
      .split(/[\n,;]+/)
      .map((e) => e.trim())
      .filter((e) => e && e.includes('@'));

    if (emails.length === 0) {
      toast.error('Enter valid email addresses');
      return;
    }

    setInviting(true);
    try {
      await interviewAPI.inviteCandidates(sessionId, emails);
      toast.success(`${emails.length} candidate(s) invited!`);
      setEmailInput('');
      load();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to send invites');
    } finally {
      setInviting(false);
    }
  };

  const copyLink = (token) => {
    const link = `${publicUrl}/interview/${token}`;
    navigator.clipboard.writeText(link);
    toast.success('Link copied!');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <span className="inline-block w-10 h-10 border-3 border-primary-200 border-t-primary-600 rounded-full animate-spin" />
      </div>
    );
  }

  if (!session) {
    return <div className="text-center py-20 text-gray-500">Session not found.</div>;
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      {/* End Session Confirmation Modal */}
      {showEndConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-2xl border border-gray-200 p-8 max-w-md w-full mx-4">
            <div className="text-center">
              <div className="w-14 h-14 rounded-full bg-red-100 flex items-center justify-center mx-auto mb-4">
                <LogOut className="text-red-600" size={28} />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">End Session?</h3>
              <p className="text-gray-500 text-sm mb-6">
                This will end the session and force-complete all in-progress candidate interviews. This cannot be undone.
              </p>
              <div className="flex gap-3">
                <button
                  onClick={() => setShowEndConfirm(false)}
                  className="flex-1 px-4 py-2.5 rounded-xl border-2 border-gray-200 text-gray-700 font-semibold hover:bg-gray-50 transition"
                  disabled={endingSession}
                >
                  Cancel
                </button>
                <button
                  onClick={async () => {
                    setEndingSession(true);
                    try {
                      await interviewAPI.endSession(sessionId);
                      toast.success('Session ended successfully');
                      setShowEndConfirm(false);
                      load();
                    } catch (err) {
                      toast.error('Failed to end session');
                    } finally {
                      setEndingSession(false);
                    }
                  }}
                  disabled={endingSession}
                  className="flex-1 px-4 py-2.5 rounded-xl bg-red-600 text-white font-semibold hover:bg-red-700 transition flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {endingSession ? <Loader2 size={16} className="animate-spin" /> : <LogOut size={16} />}
                  {endingSession ? 'Ending...' : 'End Session'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Session info */}
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-sm border border-gray-100 p-6 mb-8 slide-up">
        <div className="flex flex-col sm:flex-row justify-between items-start">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{session.job_role}</h1>
            {session.company_name && <p className="text-gray-500 mt-0.5">{session.company_name}</p>}
            <div className="flex flex-wrap gap-4 mt-3 text-sm text-gray-500">
              <span className="flex items-center gap-1.5"><Calendar size={14} className="text-gray-400" />{new Date(session.scheduled_time).toLocaleString()}</span>
              <span className="flex items-center gap-1.5"><Clock size={14} className="text-gray-400" />{session.duration_minutes} min</span>
              <span className="flex items-center gap-1.5"><Users size={14} className="text-gray-400" />{session.candidate_count} candidates</span>
            </div>
          </div>
          <div className="mt-4 sm:mt-0 flex items-center gap-3">
            {session.status !== 'completed' && (
              <button
                onClick={() => setShowEndConfirm(true)}
                className="flex items-center gap-2 px-5 py-3 rounded-xl font-semibold bg-red-50 text-red-600 hover:bg-red-100 transition-all"
              >
                <LogOut size={18} />
                <span>End Session</span>
              </button>
            )}
            <Link
              to={`/hr/live/${sessionId}`}
              className="gradient-bg text-white px-6 py-3 rounded-xl font-semibold flex items-center gap-2 hover:opacity-90 transition-all shadow-md"
            >
              <Eye size={18} />
              <span>Monitor Interviews</span>
            </Link>
          </div>
        </div>
      </div>

      {/* Invite section */}
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-sm border border-gray-100 p-6 mb-8">
        <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-primary-100 flex items-center justify-center">
            <Mail size={16} className="text-primary-600" />
          </div>
          <span>Invite Candidates</span>
        </h2>
        <p className="text-sm text-gray-500 mb-3">
          Enter candidate email addresses (one per line, or comma-separated). Each candidate will receive a unique link to an AI-conducted interview.
        </p>
        <textarea
          value={emailInput}
          onChange={(e) => setEmailInput(e.target.value)}
          rows={4}
          placeholder="candidate1@example.com&#10;candidate2@example.com&#10;candidate3@example.com"
          className="w-full px-4 py-3 bg-gray-50/80 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none resize-none font-mono text-sm transition-all"
        />
        <button
          onClick={handleInvite}
          disabled={inviting || !emailInput.trim()}
          className="mt-3 gradient-bg text-white px-6 py-2.5 rounded-xl font-semibold flex items-center gap-2 hover:opacity-90 disabled:opacity-50 shadow-sm transition-all"
        >
          {inviting ? <span className="inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : <Send size={16} />}
          <span>{inviting ? 'Sending...' : 'Send Invitations'}</span>
        </button>
      </div>

      {/* Candidate list */}
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-sm border border-gray-100 p-6">
        <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-green-100 flex items-center justify-center">
            <Users size={16} className="text-green-600" />
          </div>
          <span>Candidates ({candidates.length})</span>
        </h2>
        {candidates.length === 0 ? (
          <div className="text-center py-8">
            <div className="w-14 h-14 bg-gray-100 rounded-xl flex items-center justify-center mx-auto mb-3">
              <Users size={24} className="text-gray-300" />
            </div>
            <p className="text-gray-400 text-sm">No candidates invited yet.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-50/80">
                  <th className="px-4 py-3.5 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Email</th>
                  <th className="px-4 py-3.5 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="px-4 py-3.5 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Link</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {candidates.map((c) => (
                  <tr key={c.id} className="hover:bg-primary-50/30 transition-colors">
                    <td className="px-4 py-3.5 text-sm font-medium text-gray-900">{c.email}</td>
                    <td className="px-4 py-3.5">
                      <span className={`text-xs px-2.5 py-1 rounded-full font-semibold ${
                        c.status === 'joined' ? 'bg-green-100 text-green-700'
                          : c.status === 'completed' ? 'bg-blue-100 text-blue-700'
                          : 'bg-amber-100 text-amber-700'
                      }`}>
                        {c.status}
                      </span>
                    </td>
                    <td className="px-4 py-3.5">
                      <button
                        onClick={() => copyLink(c.unique_token)}
                        className="text-primary-600 hover:text-primary-700 flex items-center gap-1.5 text-sm font-medium transition"
                      >
                        <Copy size={14} />
                        <span>Copy Link</span>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
