"""
Personalized Development Roadmap Generator
───────────────────────────────────────────
Component 7: Creates 4-phase personalized improvement plans

4-Phase Structure:
  Phase 1: Foundation Fix      (Weeks 1-2)  – Address critical weaknesses
  Phase 2: Skill Enhancement   (Weeks 3-4)  – Build on moderate areas
  Phase 3: Simulation          (Weeks 5-6)  – Practice with realistic scenarios
  Phase 4: Advanced Mastery    (Weeks 7-8)  – Optimize strengths + edge cases

Each phase contains:
  - Learning objectives
  - Specific tasks/exercises
  - Resource recommendations
  - Weekly milestones
  - Progress metrics
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


class DevelopmentRoadmapService:
    """Generate personalized 4-phase improvement plans from interview evaluations."""

    # Resource database
    RESOURCES = {
        "communication": [
            {"title": "TED Talks: The Power of Vulnerability", "type": "video", "url": "https://ted.com", "level": "beginner"},
            {"title": "Crucial Conversations (book)", "type": "book", "level": "intermediate"},
            {"title": "Toastmasters Local Club", "type": "practice", "level": "all"},
            {"title": "STAR Method Practice Worksheets", "type": "exercise", "level": "beginner"},
        ],
        "technical": [
            {"title": "LeetCode Easy Problems (50)", "type": "practice", "url": "https://leetcode.com", "level": "beginner"},
            {"title": "System Design Primer (GitHub)", "type": "reading", "url": "https://github.com/donnemartin/system-design-primer", "level": "intermediate"},
            {"title": "Cracking the Coding Interview", "type": "book", "level": "intermediate"},
            {"title": "Mock Technical Interviews", "type": "practice", "level": "advanced"},
        ],
        "confidence": [
            {"title": "Amy Cuddy: Power Poses", "type": "video", "level": "beginner"},
            {"title": "Visualization & Mental Rehearsal Guide", "type": "exercise", "level": "beginner"},
            {"title": "Progressive Muscle Relaxation", "type": "exercise", "level": "beginner"},
            {"title": "Mock Interview Recording & Review", "type": "practice", "level": "intermediate"},
        ],
        "emotional_regulation": [
            {"title": "Box Breathing Technique", "type": "exercise", "level": "beginner"},
            {"title": "Mindfulness-Based Stress Reduction (MBSR)", "type": "course", "level": "intermediate"},
            {"title": "Emotional Intelligence 2.0 (book)", "type": "book", "level": "intermediate"},
            {"title": "Pressure Interview Simulation", "type": "practice", "level": "advanced"},
        ],
        "problem_solving": [
            {"title": "Polya's Problem Solving Framework", "type": "reading", "level": "beginner"},
            {"title": "Case Interview Prep (McKinsey style)", "type": "practice", "level": "intermediate"},
            {"title": "Design Thinking Workshop", "type": "course", "level": "intermediate"},
            {"title": "Whiteboard Problem Walkthroughs", "type": "video", "level": "advanced"},
        ],
    }

    def __init__(self):
        pass

    def generate_roadmap(
        self,
        evaluation_summary: Dict[str, Any],
        target_role: Optional[str] = None,
        weeks_available: int = 8,
    ) -> Dict[str, Any]:
        """Generate a personalized 4-phase development roadmap.

        Args:
            evaluation_summary: {
                "overall_score": float,
                "dimension_scores": {
                    "Communication": {"score": float, "grade": str},
                    "Technical Depth": {"score": float, "grade": str},
                    "Confidence": {"score": float, "grade": str},
                    "Emotional Regulation": {"score": float, "grade": str},
                    "Problem Solving": {"score": float, "grade": str},
                },
                "improvement_suggestions": [...],
            }
            target_role: e.g. "Software Engineer", "Data Scientist"
            weeks_available: Total weeks for the plan (default: 8)
        """
        overall = evaluation_summary.get("overall_score", 50)
        dimensions = evaluation_summary.get("dimension_scores", {})
        suggestions = evaluation_summary.get("improvement_suggestions", [])

        # Classify dimensions
        weak = []    # < 50
        moderate = []  # 50-70
        strong = []  # > 70

        for dim, data in dimensions.items():
            score = data.get("score", 50) if isinstance(data, dict) else data
            if score < 50:
                weak.append({"name": dim, "score": score})
            elif score < 70:
                moderate.append({"name": dim, "score": score})
            else:
                strong.append({"name": dim, "score": score})

        # Sort weak by score ascending (worst first)
        weak.sort(key=lambda x: x["score"])
        moderate.sort(key=lambda x: x["score"])

        # Divide weeks across phases
        phase_weeks = self._allocate_weeks(weeks_available, weak, moderate)

        # Build 4 phases
        start_date = datetime.utcnow()
        roadmap = {
            "candidate_profile": {
                "overall_score": overall,
                "target_role": target_role or "General",
                "total_weeks": weeks_available,
                "start_date": start_date.isoformat(),
                "estimated_completion": (start_date + timedelta(weeks=weeks_available)).isoformat(),
            },
            "dimension_analysis": {
                "weak_areas": weak,
                "moderate_areas": moderate,
                "strong_areas": strong,
            },
            "phases": [],
            "weekly_milestones": [],
            "progress_metrics": self._define_progress_metrics(dimensions),
        }

        # Phase 1: Foundation Fix
        roadmap["phases"].append(
            self._build_phase_1(weak, suggestions, phase_weeks[0], start_date, target_role)
        )

        # Phase 2: Skill Enhancement
        phase_2_start = start_date + timedelta(weeks=phase_weeks[0])
        roadmap["phases"].append(
            self._build_phase_2(moderate, weak, suggestions, phase_weeks[1], phase_2_start, target_role)
        )

        # Phase 3: Simulation
        phase_3_start = phase_2_start + timedelta(weeks=phase_weeks[1])
        roadmap["phases"].append(
            self._build_phase_3(weak + moderate, phase_weeks[2], phase_3_start, target_role)
        )

        # Phase 4: Advanced Mastery
        phase_4_start = phase_3_start + timedelta(weeks=phase_weeks[2])
        roadmap["phases"].append(
            self._build_phase_4(strong, weak + moderate, phase_weeks[3], phase_4_start, target_role)
        )

        # Generate weekly milestones
        roadmap["weekly_milestones"] = self._generate_weekly_milestones(
            roadmap["phases"], weeks_available, start_date
        )

        return roadmap

    def _allocate_weeks(self, total: int, weak: list, moderate: list) -> List[int]:
        """Allocate weeks to each phase based on need."""
        if total <= 4:
            return [1, 1, 1, 1]

        # More weak areas = more time on Phase 1
        weak_count = len(weak)
        mod_count = len(moderate)

        if weak_count >= 3:
            return [
                max(2, total // 4 + 1),
                max(1, total // 4),
                max(1, total // 4),
                max(1, total - 3 * (total // 4) - 1),
            ]
        elif weak_count >= 1:
            return [
                max(2, total // 4),
                max(2, total // 4),
                max(2, total // 4),
                max(2, total - 3 * (total // 4)),
            ]
        else:
            # No weak areas, focus on enhancement and mastery
            return [1, max(2, total // 3), max(2, total // 3), max(2, total - 2 * (total // 3) - 1)]

    # ── Phase Builders ────────────────────────────────

    def _build_phase_1(self, weak_areas, suggestions, weeks, start, role):
        """Phase 1: Foundation Fix – Address critical weaknesses."""
        tasks = []
        resources = []

        if not weak_areas:
            tasks.append({
                "title": "Review fundamentals for target role",
                "description": "Since you have no critical weaknesses, use this time to review and reinforce foundational skills.",
                "duration": "1 week",
                "priority": "medium",
            })
        else:
            for area in weak_areas[:3]:
                dim_key = self._dim_to_resource_key(area["name"])
                area_tasks = self._generate_foundation_tasks(area["name"], area["score"], role)
                tasks.extend(area_tasks)

                if dim_key in self.RESOURCES:
                    beginner_resources = [r for r in self.RESOURCES[dim_key] if r.get("level") in ("beginner", "all")]
                    resources.extend(beginner_resources)

        # Add relevant suggestions
        high_priority = [s for s in suggestions if s.get("priority") == "high"]
        for s in high_priority[:3]:
            tasks.append({
                "title": f"Address: {s.get('category', 'General')}",
                "description": s.get("suggestion", ""),
                "duration": "1 week",
                "priority": "high",
            })

        return {
            "phase": 1,
            "name": "Foundation Fix",
            "duration_weeks": weeks,
            "start_date": start.isoformat(),
            "end_date": (start + timedelta(weeks=weeks)).isoformat(),
            "objective": "Address critical weaknesses and build foundational skills",
            "focus_areas": [a["name"] for a in weak_areas[:3]] or ["General Review"],
            "tasks": tasks,
            "resources": resources[:6],
            "daily_commitment": "45-60 minutes",
            "success_criteria": "Score improvement of 10+ points in weak areas",
        }

    def _build_phase_2(self, moderate_areas, weak_areas, suggestions, weeks, start, role):
        """Phase 2: Skill Enhancement – Build on moderate areas."""
        tasks = []
        resources = []

        target_areas = moderate_areas + [w for w in weak_areas if w["score"] >= 35]

        for area in target_areas[:4]:
            dim_key = self._dim_to_resource_key(area["name"])
            area_tasks = self._generate_enhancement_tasks(area["name"], area["score"], role)
            tasks.extend(area_tasks)

            if dim_key in self.RESOURCES:
                int_resources = [r for r in self.RESOURCES[dim_key] if r.get("level") in ("intermediate", "all")]
                resources.extend(int_resources)

        if not tasks:
            tasks.append({
                "title": "Deepen expertise across all dimensions",
                "description": "Practice intermediate-level exercises across communication, technical, and soft skills.",
                "duration": f"{weeks} weeks",
                "priority": "medium",
            })

        return {
            "phase": 2,
            "name": "Skill Enhancement",
            "duration_weeks": weeks,
            "start_date": start.isoformat(),
            "end_date": (start + timedelta(weeks=weeks)).isoformat(),
            "objective": "Elevate moderate skills to strong levels",
            "focus_areas": [a["name"] for a in target_areas[:4]] or ["All Dimensions"],
            "tasks": tasks,
            "resources": resources[:6],
            "daily_commitment": "60-90 minutes",
            "success_criteria": "All moderate areas score above 65",
        }

    def _build_phase_3(self, improvement_areas, weeks, start, role):
        """Phase 3: Simulation – Practice with realistic scenarios."""
        tasks = [
            {
                "title": "Full mock interview simulation (Technical)",
                "description": "Complete a full technical interview with timing. Record yourself and review.",
                "duration": "2 sessions/week",
                "priority": "high",
            },
            {
                "title": "Full mock interview simulation (Behavioral)",
                "description": "Practice STAR method responses for 10 common behavioral questions.",
                "duration": "2 sessions/week",
                "priority": "high",
            },
            {
                "title": "Peer practice sessions",
                "description": "Find a practice partner and alternate interviewer/interviewee roles.",
                "duration": "1 session/week",
                "priority": "medium",
            },
            {
                "title": "Video self-review",
                "description": "Record and review your mock interviews. Focus on body language, eye contact, and vocal confidence.",
                "duration": "30 min/review",
                "priority": "medium",
            },
            {
                "title": "Stress inoculation practice",
                "description": "Practice answering unexpected questions under time pressure to build resilience.",
                "duration": "2 sessions/week",
                "priority": "medium",
            },
        ]

        if role:
            tasks.append({
                "title": f"Role-specific simulation: {role}",
                "description": f"Practice questions specifically designed for {role} positions including domain-specific scenarios.",
                "duration": "2 sessions/week",
                "priority": "high",
            })

        return {
            "phase": 3,
            "name": "Simulation Practice",
            "duration_weeks": weeks,
            "start_date": start.isoformat(),
            "end_date": (start + timedelta(weeks=weeks)).isoformat(),
            "objective": "Apply skills in realistic interview simulations",
            "focus_areas": ["Full Interview Practice", "Self-Review", "Stress Management"],
            "tasks": tasks,
            "resources": [
                {"title": "AI Mock Interview Platform (this app)", "type": "practice", "level": "all"},
                {"title": "Interview Recording & Analysis", "type": "tool", "level": "all"},
            ],
            "daily_commitment": "45-60 minutes",
            "success_criteria": "Complete 8+ full mock interviews with improving scores",
        }

    def _build_phase_4(self, strong_areas, improvement_areas, weeks, start, role):
        """Phase 4: Advanced Mastery – Optimize strengths + edge cases."""
        tasks = [
            {
                "title": "Edge case preparation",
                "description": "Practice answering curveball questions, brain teasers, and unusual scenarios.",
                "duration": "3 sessions/week",
                "priority": "high",
            },
            {
                "title": "Advanced storytelling techniques",
                "description": "Master the art of weaving compelling narratives with metrics and impact.",
                "duration": "ongoing",
                "priority": "medium",
            },
            {
                "title": "Negotiation & closing skills",
                "description": "Practice salary negotiation, asking insightful questions, and leaving strong impressions.",
                "duration": "2 sessions",
                "priority": "medium",
            },
            {
                "title": "Final full-length simulation",
                "description": "Complete a comprehensive mock interview covering all rounds. Score should meet target.",
                "duration": "1 full session",
                "priority": "high",
            },
        ]

        for area in strong_areas[:2]:
            tasks.append({
                "title": f"Master-level: {area['name']}",
                "description": f"Push {area['name']} from good to exceptional with advanced techniques.",
                "duration": "ongoing",
                "priority": "low",
            })

        return {
            "phase": 4,
            "name": "Advanced Mastery",
            "duration_weeks": weeks,
            "start_date": start.isoformat(),
            "end_date": (start + timedelta(weeks=weeks)).isoformat(),
            "objective": "Achieve interview excellence and handle edge cases",
            "focus_areas": ["Edge Cases", "Advanced Techniques", "Final Preparation"],
            "tasks": tasks,
            "resources": [
                {"title": "Advanced System Design (book)", "type": "book", "level": "advanced"},
                {"title": "Executive Presence (book)", "type": "book", "level": "advanced"},
            ],
            "daily_commitment": "30-45 minutes",
            "success_criteria": "Consistent 80+ scores across all dimensions",
        }

    # ── Task Generators ───────────────────────────────

    def _generate_foundation_tasks(self, dimension: str, score: float, role: Optional[str]) -> List[Dict]:
        tasks_map = {
            "Communication": [
                {"title": "Learn STAR method framework", "description": "Study and memorize the Situation-Task-Action-Result format. Practice with 5 personal examples.", "duration": "3 days", "priority": "high"},
                {"title": "Eliminate filler words", "description": "Record yourself for 5 minutes daily. Count filler words. Practice deliberate pausing.", "duration": "1 week", "priority": "high"},
                {"title": "Structure practice", "description": "For each answer, write: 1 opening statement, 2-3 body points, 1 conclusion. Practice daily.", "duration": "1 week", "priority": "medium"},
            ],
            "Technical Depth": [
                {"title": "Core concepts review", "description": f"Review fundamental concepts for {role or 'your target role'}. Create flashcards for key terms.", "duration": "1 week", "priority": "high"},
                {"title": "Practice technical explanations", "description": "Explain 5 complex concepts to a non-technical person. Focus on clarity and examples.", "duration": "3 days", "priority": "high"},
            ],
            "Confidence": [
                {"title": "Daily affirmation practice", "description": "Write and recite 3 achievement statements each morning. Build evidence-based confidence.", "duration": "daily", "priority": "medium"},
                {"title": "Power pose routine", "description": "Practice 2-minute power poses before each practice session.", "duration": "daily", "priority": "medium"},
            ],
            "Emotional Regulation": [
                {"title": "Box breathing mastery", "description": "Practice 4-4-4-4 breathing: 3 rounds before each practice session and when feeling stressed.", "duration": "daily", "priority": "high"},
                {"title": "Cognitive reframing", "description": "When anxious, write down the thought and reframe it positively. Keep a journal.", "duration": "daily", "priority": "medium"},
            ],
            "Problem Solving": [
                {"title": "Structured thinking framework", "description": "Learn and practice: Define → Breakdown → Solve → Verify for every problem.", "duration": "1 week", "priority": "high"},
                {"title": "Think-aloud practice", "description": "Solve problems while narrating your thought process. Record and review.", "duration": "3 sessions/week", "priority": "high"},
            ],
        }
        return tasks_map.get(dimension, [{"title": f"Improve {dimension}", "description": "Focus targeted practice on this area.", "duration": "1 week", "priority": "high"}])

    def _generate_enhancement_tasks(self, dimension: str, score: float, role: Optional[str]) -> List[Dict]:
        tasks_map = {
            "Communication": [
                {"title": "Advanced vocabulary building", "description": "Learn 5 industry-specific terms per day. Use them in practice answers.", "duration": "2 weeks", "priority": "medium"},
                {"title": "Persuasive communication", "description": "Practice using data and metrics to support points. Quantify achievements.", "duration": "1 week", "priority": "medium"},
            ],
            "Technical Depth": [
                {"title": "Deep-dive projects", "description": f"Complete 2 hands-on projects relevant to {role or 'your field'}. Document learnings.", "duration": "2 weeks", "priority": "high"},
                {"title": "Architecture discussions", "description": "Practice discussing system design decisions, trade-offs, and scalability.", "duration": "1 week", "priority": "medium"},
            ],
            "Confidence": [
                {"title": "Progressive exposure", "description": "Gradually increase interview difficulty. Start with friends, then strangers, then experts.", "duration": "2 weeks", "priority": "medium"},
            ],
            "Emotional Regulation": [
                {"title": "Pressure desensitization", "description": "Practice under progressively difficult conditions: time pressure, tough questions, interruptions.", "duration": "2 weeks", "priority": "medium"},
            ],
            "Problem Solving": [
                {"title": "Case study practice", "description": "Work through 5 business case studies. Present solutions with trade-off analysis.", "duration": "2 weeks", "priority": "medium"},
            ],
        }
        return tasks_map.get(dimension, [{"title": f"Enhance {dimension}", "description": "Practice intermediate exercises.", "duration": "2 weeks", "priority": "medium"}])

    # ── Milestones ────────────────────────────────────

    def _generate_weekly_milestones(self, phases, total_weeks, start_date):
        milestones = []
        week_num = 0

        for phase in phases:
            phase_weeks = phase["duration_weeks"]
            for w in range(phase_weeks):
                week_num += 1
                if week_num > total_weeks:
                    break

                week_date = start_date + timedelta(weeks=week_num - 1)
                milestone = {
                    "week": week_num,
                    "date": week_date.isoformat(),
                    "phase": phase["name"],
                    "objectives": [],
                    "deliverables": [],
                }

                # Add relevant objectives from phase tasks
                phase_tasks = phase.get("tasks", [])
                tasks_per_week = max(1, len(phase_tasks) // max(phase_weeks, 1))
                start_idx = w * tasks_per_week
                week_tasks = phase_tasks[start_idx:start_idx + tasks_per_week]

                for t in week_tasks:
                    milestone["objectives"].append(t["title"])

                # Add deliverables based on week position
                if w == 0:
                    milestone["deliverables"].append(f"Complete {phase['name']} setup and initial assessment")
                elif w == phase_weeks - 1:
                    milestone["deliverables"].append(f"Complete {phase['name']} review and self-assessment")
                else:
                    milestone["deliverables"].append(f"Continue {phase['name']} exercises")

                milestones.append(milestone)

        return milestones

    # ── Progress Metrics ──────────────────────────────

    def _define_progress_metrics(self, dimensions):
        metrics = []
        for dim, data in dimensions.items():
            score = data.get("score", 50) if isinstance(data, dict) else data
            target = min(90, score + 20)
            metrics.append({
                "dimension": dim,
                "baseline": round(score, 1),
                "target": round(target, 1),
                "improvement_needed": round(target - score, 1),
                "tracking_method": "Mock interview scores in this dimension",
            })
        return metrics

    def compute_progress(
        self, baseline_scores: Dict[str, float], current_scores: Dict[str, float]
    ) -> Dict[str, Any]:
        """Compute progress toward roadmap targets."""
        progress = {}
        for dim in baseline_scores:
            base = baseline_scores[dim]
            current = current_scores.get(dim, base)
            target = min(90, base + 20)
            improvement = current - base
            target_improvement = target - base
            pct = (improvement / target_improvement * 100) if target_improvement > 0 else 100

            progress[dim] = {
                "baseline": round(base, 1),
                "current": round(current, 1),
                "target": round(target, 1),
                "improvement": round(improvement, 1),
                "progress_pct": round(min(100, max(0, pct)), 1),
                "on_track": pct >= 50,
            }

        overall_progress = float(
            sum(d["progress_pct"] for d in progress.values()) / max(len(progress), 1)
        )
        return {
            "dimensions": progress,
            "overall_progress_pct": round(overall_progress, 1),
            "on_track": overall_progress >= 50,
        }

    # ── Helpers ───────────────────────────────────────

    def _dim_to_resource_key(self, dimension: str) -> str:
        mapping = {
            "Communication": "communication",
            "Technical Depth": "technical",
            "Confidence": "confidence",
            "Emotional Regulation": "emotional_regulation",
            "Problem Solving": "problem_solving",
        }
        return mapping.get(dimension, "communication")


# Singleton
development_roadmap_service = DevelopmentRoadmapService()
