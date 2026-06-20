import React, { useEffect, useState } from 'react';
import { dataCollectionAPI } from '../services/api';
import toast from 'react-hot-toast';
import { Github, Linkedin, Upload, User, FileText, Loader2, CheckCircle, AlertTriangle } from 'lucide-react';

export default function DataCollectionPage() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [githubUrl, setGithubUrl] = useState('');
  const [linkedinUrl, setLinkedinUrl] = useState('');
  const [analyzing, setAnalyzing] = useState(null);
  const [resumeFile, setResumeFile] = useState(null);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const res = await dataCollectionAPI.getProfile();
      setProfile(res.data);
    } catch {
      // Profile not yet built
      setProfile(null);
    } finally {
      setLoading(false);
    }
  };

  const handleGithubAnalysis = async () => {
    if (!githubUrl.trim()) return toast.error('Enter a GitHub profile URL');
    setAnalyzing('github');
    try {
      const res = await dataCollectionAPI.analyzeGithub(githubUrl);
      toast.success('GitHub profile analyzed!');
      setProfile((prev) => ({ ...prev, github: res.data }));
      setGithubUrl('');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'GitHub analysis failed');
    } finally {
      setAnalyzing(null);
    }
  };

  const handleLinkedinLink = async () => {
    if (!linkedinUrl.trim()) return toast.error('Enter a LinkedIn profile URL');
    setAnalyzing('linkedin');
    try {
      await dataCollectionAPI.analyzeLinkedin(linkedinUrl);
      toast.success('LinkedIn profile linked!');
      setLinkedinUrl('');
      loadProfile();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'LinkedIn linking failed');
    } finally {
      setAnalyzing(null);
    }
  };

  const handleResumeUpload = async () => {
    if (!resumeFile) return toast.error('Select a resume file');
    setAnalyzing('resume');
    try {
      const res = await dataCollectionAPI.uploadResume(resumeFile);
      toast.success('Resume analyzed!');
      setProfile((prev) => ({ ...prev, resume: res.data }));
      setResumeFile(null);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Resume upload failed');
    } finally {
      setAnalyzing(null);
    }
  };

  const handleBuildFullProfile = async () => {
    setAnalyzing('full');
    try {
      const res = await dataCollectionAPI.buildFullProfile({});
      toast.success('Full profile built!');
      setProfile(res.data);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Profile build failed');
    } finally {
      setAnalyzing(null);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <span className="inline-block w-10 h-10 border-3 border-primary-200 border-t-primary-600 rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="mb-8 slide-up">
        <div className="flex items-center gap-3 mb-1">
          <div className="w-12 h-12 rounded-xl gradient-bg flex items-center justify-center shadow-sm">
            <User className="text-white" size={22} />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Candidate Profile</h1>
            <p className="text-gray-500 mt-1">Build your profile for personalized interview questions</p>
          </div>
        </div>
      </div>

      <div className="grid gap-6">
        {/* GitHub Analysis */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
          <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Github size={20} /> GitHub Profile Analysis
          </h3>
          <div className="flex gap-3">
            <input
              type="url"
              value={githubUrl}
              onChange={(e) => setGithubUrl(e.target.value)}
              placeholder="https://github.com/username"
              className="flex-1 px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-200 focus:border-primary-400 outline-none transition text-sm"
            />
            <button
              onClick={handleGithubAnalysis}
              disabled={analyzing === 'github'}
              className="gradient-bg text-white px-5 py-2.5 rounded-xl font-medium text-sm hover:opacity-90 transition disabled:opacity-50 flex items-center gap-2"
            >
              {analyzing === 'github' ? <Loader2 size={16} className="animate-spin" /> : <Github size={16} />}
              Analyze
            </button>
          </div>
          {profile?.github && (
            <div className="mt-4 bg-gray-50 rounded-xl p-4">
              <div className="grid grid-cols-3 gap-3 mb-3">
                <div className="text-center">
                  <div className="text-lg font-bold text-gray-900">{profile.github.public_repos || 0}</div>
                  <div className="text-xs text-gray-500">Repositories</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold text-gray-900">{profile.github.primary_languages?.length || 0}</div>
                  <div className="text-xs text-gray-500">Languages</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold text-gray-900">{profile.github.contribution_score || 0}</div>
                  <div className="text-xs text-gray-500">Score</div>
                </div>
              </div>
              {profile.github.primary_languages && (
                <div className="flex flex-wrap gap-1.5">
                  {profile.github.primary_languages.map((lang) => (
                    <span key={lang} className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">{lang}</span>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* LinkedIn Link */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
          <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Linkedin size={20} /> LinkedIn Profile
          </h3>
          <div className="flex gap-3">
            <input
              type="url"
              value={linkedinUrl}
              onChange={(e) => setLinkedinUrl(e.target.value)}
              placeholder="https://linkedin.com/in/username"
              className="flex-1 px-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-200 focus:border-primary-400 outline-none transition text-sm"
            />
            <button
              onClick={handleLinkedinLink}
              disabled={analyzing === 'linkedin'}
              className="gradient-bg text-white px-5 py-2.5 rounded-xl font-medium text-sm hover:opacity-90 transition disabled:opacity-50 flex items-center gap-2"
            >
              {analyzing === 'linkedin' ? <Loader2 size={16} className="animate-spin" /> : <Linkedin size={16} />}
              Link
            </button>
          </div>
        </div>

        {/* Resume Upload */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
          <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <FileText size={20} /> Resume Upload
          </h3>
          <div className="flex gap-3 items-center">
            <label className="flex-1 cursor-pointer">
              <div className="border-2 border-dashed border-gray-200 rounded-xl px-4 py-4 text-center hover:border-primary-300 transition">
                <Upload size={20} className="mx-auto text-gray-400 mb-1" />
                <p className="text-sm text-gray-500">
                  {resumeFile ? resumeFile.name : 'Click to select PDF or DOCX'}
                </p>
              </div>
              <input
                type="file"
                accept=".pdf,.docx"
                className="hidden"
                onChange={(e) => setResumeFile(e.target.files[0])}
              />
            </label>
            <button
              onClick={handleResumeUpload}
              disabled={!resumeFile || analyzing === 'resume'}
              className="gradient-bg text-white px-5 py-2.5 rounded-xl font-medium text-sm hover:opacity-90 transition disabled:opacity-50 flex items-center gap-2"
            >
              {analyzing === 'resume' ? <Loader2 size={16} className="animate-spin" /> : <Upload size={16} />}
              Upload
            </button>
          </div>
          {profile?.resume && (
            <div className="mt-4 bg-gray-50 rounded-xl p-4">
              <p className="text-sm text-gray-700 mb-2 font-medium">Extracted Skills:</p>
              <div className="flex flex-wrap gap-1.5">
                {(profile.resume.skills || []).map((skill) => (
                  <span key={skill} className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">{skill}</span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Build Full Profile */}
        <div className="bg-gradient-to-r from-primary-50 to-purple-50 rounded-2xl border border-primary-100 p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-gray-900 mb-1">Build Complete Profile</h3>
              <p className="text-sm text-gray-500">Combine GitHub, LinkedIn, and resume data into a comprehensive candidate profile with knowledge graph</p>
            </div>
            <button
              onClick={handleBuildFullProfile}
              disabled={analyzing === 'full'}
              className="gradient-bg text-white px-6 py-3 rounded-xl font-semibold hover:opacity-90 transition disabled:opacity-50 flex items-center gap-2 flex-shrink-0"
            >
              {analyzing === 'full' ? <Loader2 size={16} className="animate-spin" /> : <CheckCircle size={16} />}
              Build Profile
            </button>
          </div>
        </div>

        {/* Profile Summary */}
        {profile?.knowledge_graph && (
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
            <h3 className="font-semibold text-gray-900 mb-3">Profile Summary</h3>
            <div className="grid grid-cols-2 gap-4">
              {profile.knowledge_graph.central_skills && (
                <div>
                  <p className="text-xs font-medium text-gray-500 uppercase mb-2">Core Skills</p>
                  <div className="flex flex-wrap gap-1.5">
                    {profile.knowledge_graph.central_skills.map((s) => (
                      <span key={s} className="text-xs bg-primary-100 text-primary-700 px-2 py-0.5 rounded-full">{s}</span>
                    ))}
                  </div>
                </div>
              )}
              {profile.knowledge_graph.skill_clusters && (
                <div>
                  <p className="text-xs font-medium text-gray-500 uppercase mb-2">Skill Clusters</p>
                  <div className="flex flex-wrap gap-1.5">
                    {Object.keys(profile.knowledge_graph.skill_clusters).map((c) => (
                      <span key={c} className="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded-full">{c}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
