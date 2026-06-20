import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { interviewAPI } from "../services/api";
import {
  ArrowLeft,
  Trophy,
  AlertTriangle,
  Eye,
  Users,
  Monitor,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import {
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

const COLORS = [
  "#6366f1",
  "#f59e0b",
  "#10b981",
  "#ef4444",
  "#8b5cf6",
  "#ec4899",
  "#14b8a6",
  "#f97316",
];

const DIMENSION_LABELS = {
  content: "Content",
  keyword: "Keywords",
  depth: "Depth",
  communication: "Communication",
  confidence: "Confidence",
  overall: "Overall",
};

export default function CandidateComparison() {
  const { sessionId } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sortField, setSortField] = useState("overall");
  const [sortAsc, setSortAsc] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await interviewAPI.getCandidateComparison(sessionId);
        setData(res.data);
      } catch (err) {
        setError(err.response?.data?.detail || "Failed to load comparison data");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [sessionId]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="bg-red-50 text-red-600 p-6 rounded-2xl max-w-md text-center">
          <AlertTriangle className="mx-auto mb-3" size={32} />
          <p className="font-semibold">{error}</p>
          <Link to="/hr" className="mt-4 inline-block text-indigo-600 hover:underline">
            Back to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  const candidates = data?.candidates || [];

  const sorted = [...candidates].sort((a, b) => {
    let valA, valB;
    if (sortField === "name") {
      valA = a.candidate_name.toLowerCase();
      valB = b.candidate_name.toLowerCase();
      return sortAsc ? valA.localeCompare(valB) : valB.localeCompare(valA);
    }
    if (sortField === "technical") {
      valA = a.technical_score;
      valB = b.technical_score;
    } else if (sortField === "hr") {
      valA = a.hr_score;
      valB = b.hr_score;
    } else if (sortField === "integrity") {
      valA = a.integrity_score;
      valB = b.integrity_score;
    } else {
      valA = a.dimension_scores?.[sortField] || 0;
      valB = b.dimension_scores?.[sortField] || 0;
    }
    return sortAsc ? valA - valB : valB - valA;
  });

  const handleSort = (field) => {
    if (sortField === field) {
      setSortAsc(!sortAsc);
    } else {
      setSortField(field);
      setSortAsc(false);
    }
  };

  const SortIcon = ({ field }) => {
    if (sortField !== field) return null;
    return sortAsc ? <ChevronUp size={14} className="inline ml-0.5" /> : <ChevronDown size={14} className="inline ml-0.5" />;
  };

  const scoreColor = (score) => {
    if (score >= 80) return "text-green-600";
    if (score >= 60) return "text-yellow-600";
    return "text-red-600";
  };

  const scoreBg = (score) => {
    if (score >= 80) return "bg-green-50";
    if (score >= 60) return "bg-yellow-50";
    return "bg-red-50";
  };

  // Radar chart data for top candidates (max 6)
  const radarCandidates = sorted.slice(0, 6);
  const radarDimensions = ["content", "keyword", "depth", "communication", "confidence"];
  const radarData = radarDimensions.map((dim) => {
    const entry = { dimension: DIMENSION_LABELS[dim] };
    radarCandidates.forEach((c, i) => {
      entry[`c${i}`] = c.dimension_scores?.[dim] || 0;
    });
    return entry;
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-indigo-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <Link
            to={`/hr/session/${sessionId}`}
            className="p-2 hover:bg-white rounded-xl transition-all"
          >
            <ArrowLeft size={20} />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-800">
              Candidate Comparison
            </h1>
            <p className="text-gray-500 text-sm">
              {data?.job_role || "Session"} &middot; {candidates.length} candidate{candidates.length !== 1 ? "s" : ""}
            </p>
          </div>
        </div>

        {candidates.length === 0 ? (
          <div className="bg-white rounded-2xl shadow-sm p-12 text-center text-gray-400">
            <Users className="mx-auto mb-3" size={40} />
            <p className="text-lg font-medium">No completed candidates yet</p>
            <p className="text-sm mt-1">
              Candidates will appear here after they complete the interview.
            </p>
          </div>
        ) : (
          <>
            {/* Radar Chart */}
            {radarCandidates.length >= 2 && (
              <div className="bg-white rounded-2xl shadow-sm p-6 mb-6">
                <h2 className="text-lg font-semibold text-gray-700 mb-4">
                  Skill Dimensions Overlay
                </h2>
                <ResponsiveContainer width="100%" height={350}>
                  <RadarChart data={radarData}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="dimension" tick={{ fontSize: 12 }} />
                    <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fontSize: 10 }} />
                    {radarCandidates.map((c, i) => (
                      <Radar
                        key={c.candidate_token}
                        name={c.candidate_name}
                        dataKey={`c${i}`}
                        stroke={COLORS[i]}
                        fill={COLORS[i]}
                        fillOpacity={0.1}
                        strokeWidth={2}
                      />
                    ))}
                    <Tooltip />
                  </RadarChart>
                </ResponsiveContainer>
                <div className="flex flex-wrap gap-4 mt-3 justify-center">
                  {radarCandidates.map((c, i) => (
                    <div key={c.candidate_token} className="flex items-center gap-1.5 text-sm text-gray-600">
                      <span
                        className="w-3 h-3 rounded-full inline-block"
                        style={{ backgroundColor: COLORS[i] }}
                      />
                      {c.candidate_name}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Comparison Table */}
            <div className="bg-white rounded-2xl shadow-sm overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="bg-gray-50 text-gray-500 text-xs uppercase tracking-wider">
                      <th className="text-left px-4 py-3 font-semibold">#</th>
                      <th
                        className="text-left px-4 py-3 font-semibold cursor-pointer hover:text-gray-700"
                        onClick={() => handleSort("name")}
                      >
                        Candidate <SortIcon field="name" />
                      </th>
                      <th
                        className="text-center px-3 py-3 font-semibold cursor-pointer hover:text-gray-700"
                        onClick={() => handleSort("overall")}
                      >
                        Overall <SortIcon field="overall" />
                      </th>
                      <th
                        className="text-center px-3 py-3 font-semibold cursor-pointer hover:text-gray-700"
                        onClick={() => handleSort("technical")}
                      >
                        Tech <SortIcon field="technical" />
                      </th>
                      <th
                        className="text-center px-3 py-3 font-semibold cursor-pointer hover:text-gray-700"
                        onClick={() => handleSort("hr")}
                      >
                        HR <SortIcon field="hr" />
                      </th>
                      {radarDimensions.map((dim) => (
                        <th
                          key={dim}
                          className="text-center px-3 py-3 font-semibold cursor-pointer hover:text-gray-700"
                          onClick={() => handleSort(dim)}
                        >
                          {DIMENSION_LABELS[dim]} <SortIcon field={dim} />
                        </th>
                      ))}
                      <th
                        className="text-center px-3 py-3 font-semibold cursor-pointer hover:text-gray-700"
                        onClick={() => handleSort("integrity")}
                      >
                        Integrity <SortIcon field="integrity" />
                      </th>
                      <th className="text-center px-3 py-3 font-semibold">
                        Proctoring
                      </th>
                      <th className="text-center px-3 py-3 font-semibold">
                        Round
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {sorted.map((c, idx) => (
                      <tr
                        key={c.candidate_token}
                        className={`hover:bg-gray-50 transition-colors ${idx === 0 ? "bg-indigo-50/30" : ""}`}
                      >
                        <td className="px-4 py-3">
                          {idx === 0 ? (
                            <Trophy size={16} className="text-yellow-500" />
                          ) : (
                            <span className="text-gray-400 font-medium">{idx + 1}</span>
                          )}
                        </td>
                        <td className="px-4 py-3">
                          <div className="font-medium text-gray-800">
                            {c.candidate_name}
                          </div>
                          <div className="text-xs text-gray-400">{c.candidate_email}</div>
                        </td>
                        <td className="text-center px-3 py-3">
                          <span
                            className={`inline-block px-2.5 py-1 rounded-lg font-bold text-sm ${scoreColor(c.dimension_scores?.overall || 0)} ${scoreBg(c.dimension_scores?.overall || 0)}`}
                          >
                            {c.dimension_scores?.overall || 0}
                          </span>
                        </td>
                        <td className={`text-center px-3 py-3 font-semibold ${scoreColor(c.technical_score)}`}>
                          {c.technical_score}
                        </td>
                        <td className={`text-center px-3 py-3 font-semibold ${scoreColor(c.hr_score)}`}>
                          {c.hr_score || "—"}
                        </td>
                        {radarDimensions.map((dim) => (
                          <td
                            key={dim}
                            className={`text-center px-3 py-3 ${scoreColor(c.dimension_scores?.[dim] || 0)}`}
                          >
                            {c.dimension_scores?.[dim] || 0}
                          </td>
                        ))}
                        <td className="text-center px-3 py-3">
                          <span
                            className={`inline-block px-2.5 py-1 rounded-lg font-bold text-sm ${scoreColor(c.integrity_score)} ${scoreBg(c.integrity_score)}`}
                          >
                            {c.integrity_score}
                          </span>
                        </td>
                        <td className="text-center px-3 py-3">
                          <div className="flex items-center justify-center gap-2 text-xs text-gray-500">
                            <span className="flex items-center gap-0.5" title="Gaze violations">
                              <Eye size={12} />{c.proctoring?.gaze_violations || 0}
                            </span>
                            <span className="flex items-center gap-0.5" title="Multi-person alerts">
                              <Users size={12} />{c.proctoring?.multi_person_alerts || 0}
                            </span>
                            <span className="flex items-center gap-0.5" title="Tab switches">
                              <Monitor size={12} />{c.proctoring?.tab_switches || 0}
                            </span>
                          </div>
                        </td>
                        <td className="text-center px-3 py-3">
                          <span
                            className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                              c.current_round === "HR"
                                ? "bg-purple-100 text-purple-700"
                                : c.termination_reason
                                ? "bg-red-100 text-red-700"
                                : "bg-blue-100 text-blue-700"
                            }`}
                          >
                            {c.termination_reason
                              ? "Terminated"
                              : c.current_round}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
