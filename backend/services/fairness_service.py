"""
Fairness Auditing Framework
────────────────────────────
Component 6: Pre- and Post-deployment fairness analysis

Pre-deployment audits:
  1. Demographic Parity  – P(positive | group) should be equal across groups
  2. Equalized Odds       – TPR and FPR should be equal across groups
  3. Calibration           – Predicted probabilities ≈ actual outcomes per group
  4. Counterfactual        – Score should not change when swapping protected attr
  5. Intersectional        – Fairness across intersections of demographics

Post-deployment monitoring:
  1. Real-time bias drift  – Track score distributions over sliding windows
  2. Statistical tests     – KS test for distribution shift
  3. Automated mitigation  – Reweighting, thresholding adjustment
"""

import math
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from collections import defaultdict

import numpy as np

try:
    from scipy import stats as scipy_stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


class FairnessService:
    """Comprehensive fairness auditing and bias mitigation framework."""

    PROTECTED_ATTRIBUTES = [
        "gender", "age_group", "ethnicity", "education_level", "native_language",
    ]

    # Thresholds
    DEMOGRAPHIC_PARITY_THRESHOLD = 0.1     # Max acceptable difference in selection rates
    EQUALIZED_ODDS_THRESHOLD = 0.1         # Max acceptable difference in TPR/FPR
    CALIBRATION_THRESHOLD = 0.15           # Max acceptable calibration error
    FOUR_FIFTHS_RULE = 0.8                 # Adverse impact ratio min (EEOC)

    def __init__(self):
        self._audit_history: List[Dict[str, Any]] = []
        self._drift_windows: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self._window_size = 100
        self._mitigation_log: List[Dict[str, Any]] = []

    # ── Pre-deployment Audits ─────────────────────────

    def audit_demographic_parity(
        self, scores: List[Dict[str, Any]], threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """Check if selection/pass rates are equal across demographic groups.

        Each record: {"score": float, "group": str, "passed": bool}
        """
        threshold = threshold or self.DEMOGRAPHIC_PARITY_THRESHOLD
        groups = defaultdict(lambda: {"total": 0, "passed": 0})

        for record in scores:
            g = record.get("group", "unknown")
            groups[g]["total"] += 1
            if record.get("passed", False):
                groups[g]["passed"] += 1

        # Compute pass rates
        pass_rates = {}
        for g, data in groups.items():
            if data["total"] > 0:
                pass_rates[g] = data["passed"] / data["total"]
            else:
                pass_rates[g] = 0

        if not pass_rates:
            return {"fair": True, "error": "No data"}

        max_rate = max(pass_rates.values())
        min_rate = min(pass_rates.values())
        disparity = max_rate - min_rate

        # Four-fifths rule (EEOC)
        four_fifths_ratios = {}
        reference_rate = max_rate
        for g, rate in pass_rates.items():
            four_fifths_ratios[g] = rate / reference_rate if reference_rate > 0 else 1.0

        four_fifths_violation = any(r < self.FOUR_FIFTHS_RULE for r in four_fifths_ratios.values())

        return {
            "metric": "demographic_parity",
            "fair": disparity <= threshold and not four_fifths_violation,
            "disparity": round(disparity, 4),
            "threshold": threshold,
            "pass_rates": {g: round(r, 4) for g, r in pass_rates.items()},
            "four_fifths_ratios": {g: round(r, 4) for g, r in four_fifths_ratios.items()},
            "four_fifths_violation": four_fifths_violation,
            "group_sizes": {g: d["total"] for g, d in groups.items()},
        }

    def audit_equalized_odds(
        self, predictions: List[Dict[str, Any]], threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """Check if TPR and FPR are equal across groups.

        Each record: {"predicted": bool, "actual": bool, "group": str}
        """
        threshold = threshold or self.EQUALIZED_ODDS_THRESHOLD
        groups = defaultdict(lambda: {"tp": 0, "fp": 0, "tn": 0, "fn": 0})

        for record in predictions:
            g = record.get("group", "unknown")
            pred = record.get("predicted", False)
            actual = record.get("actual", False)

            if pred and actual:
                groups[g]["tp"] += 1
            elif pred and not actual:
                groups[g]["fp"] += 1
            elif not pred and actual:
                groups[g]["fn"] += 1
            else:
                groups[g]["tn"] += 1

        tpr_map = {}
        fpr_map = {}
        for g, m in groups.items():
            positives = m["tp"] + m["fn"]
            negatives = m["fp"] + m["tn"]
            tpr_map[g] = m["tp"] / positives if positives > 0 else 0
            fpr_map[g] = m["fp"] / negatives if negatives > 0 else 0

        tpr_disparity = max(tpr_map.values()) - min(tpr_map.values()) if tpr_map else 0
        fpr_disparity = max(fpr_map.values()) - min(fpr_map.values()) if fpr_map else 0

        return {
            "metric": "equalized_odds",
            "fair": tpr_disparity <= threshold and fpr_disparity <= threshold,
            "tpr_disparity": round(tpr_disparity, 4),
            "fpr_disparity": round(fpr_disparity, 4),
            "threshold": threshold,
            "true_positive_rates": {g: round(r, 4) for g, r in tpr_map.items()},
            "false_positive_rates": {g: round(r, 4) for g, r in fpr_map.items()},
        }

    def audit_calibration(
        self, predictions: List[Dict[str, Any]], n_bins: int = 10
    ) -> Dict[str, Any]:
        """Check if predicted probabilities match actual outcomes per group.

        Each record: {"predicted_prob": float, "actual": bool, "group": str}
        """
        groups_data = defaultdict(list)
        for record in predictions:
            groups_data[record.get("group", "unknown")].append(record)

        group_calibration = {}
        for g, records in groups_data.items():
            bins = defaultdict(lambda: {"predicted": [], "actual": []})
            for r in records:
                bin_idx = min(int(r["predicted_prob"] * n_bins), n_bins - 1)
                bins[bin_idx]["predicted"].append(r["predicted_prob"])
                bins[bin_idx]["actual"].append(1 if r["actual"] else 0)

            errors = []
            for bin_idx, data in bins.items():
                if data["predicted"]:
                    avg_pred = np.mean(data["predicted"])
                    avg_actual = np.mean(data["actual"])
                    errors.append(abs(avg_pred - avg_actual))

            ece = float(np.mean(errors)) if errors else 0
            group_calibration[g] = {
                "expected_calibration_error": round(ece, 4),
                "num_samples": len(records),
                "well_calibrated": ece <= self.CALIBRATION_THRESHOLD,
            }

        all_ece = [v["expected_calibration_error"] for v in group_calibration.values()]
        max_ece_diff = max(all_ece) - min(all_ece) if all_ece else 0

        return {
            "metric": "calibration",
            "fair": max_ece_diff <= self.CALIBRATION_THRESHOLD,
            "max_calibration_gap": round(max_ece_diff, 4),
            "group_calibration": group_calibration,
        }

    def audit_counterfactual(
        self, scoring_function, candidate: Dict[str, Any],
        protected_attribute: str = "gender",
        counterfactual_values: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Check if score changes when swapping a protected attribute.

        scoring_function: callable taking a candidate dict → float score
        """
        original_value = candidate.get(protected_attribute, "unknown")
        original_score = scoring_function(candidate)

        if counterfactual_values is None:
            counterfactual_values = ["male", "female", "non_binary"]

        counterfactual_scores = {}
        for value in counterfactual_values:
            if value == original_value:
                counterfactual_scores[value] = original_score
                continue
            modified = candidate.copy()
            modified[protected_attribute] = value
            counterfactual_scores[value] = scoring_function(modified)

        scores = list(counterfactual_scores.values())
        max_diff = max(scores) - min(scores)

        return {
            "metric": "counterfactual_fairness",
            "fair": max_diff < 5.0,
            "max_score_difference": round(max_diff, 2),
            "original_value": original_value,
            "original_score": round(original_score, 2),
            "counterfactual_scores": {
                k: round(v, 2) for k, v in counterfactual_scores.items()
            },
        }

    def audit_intersectional(
        self, scores: List[Dict[str, Any]],
        attributes: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Check fairness across intersections of multiple demographics.

        Each record: {"score": float, "gender": str, "age_group": str, ...}
        """
        attributes = attributes or ["gender", "age_group"]
        groups = defaultdict(list)

        for record in scores:
            key_parts = [record.get(attr, "unknown") for attr in attributes]
            key = " × ".join(key_parts)
            groups[key].append(record.get("score", 50))

        group_stats = {}
        for key, values in groups.items():
            if len(values) >= 5:  # Minimum sample size
                group_stats[key] = {
                    "mean": round(float(np.mean(values)), 2),
                    "std": round(float(np.std(values)), 2),
                    "count": len(values),
                    "median": round(float(np.median(values)), 2),
                }

        if len(group_stats) < 2:
            return {"metric": "intersectional", "fair": True, "note": "Insufficient data for intersectional analysis"}

        means = [s["mean"] for s in group_stats.values()]
        max_gap = max(means) - min(means)

        # Kruskal-Wallis test if scipy available
        p_value = None
        if SCIPY_AVAILABLE and len(groups) >= 2:
            valid_groups = [v for v in groups.values() if len(v) >= 5]
            if len(valid_groups) >= 2:
                stat, p_value = scipy_stats.kruskal(*valid_groups)
                p_value = round(p_value, 4)

        return {
            "metric": "intersectional_fairness",
            "fair": max_gap < 10.0,
            "max_gap": round(max_gap, 2),
            "attributes": attributes,
            "group_statistics": group_stats,
            "statistical_test_p_value": p_value,
            "significant_difference": p_value < 0.05 if p_value is not None else None,
        }

    # ── Full Pre-deployment Audit ─────────────────────

    def run_full_audit(
        self,
        evaluation_data: List[Dict[str, Any]],
        scoring_function=None,
    ) -> Dict[str, Any]:
        """Run all pre-deployment fairness checks."""
        results = {"timestamp": datetime.utcnow().isoformat(), "audits": {}}

        # Demographic parity
        parity_data = [
            {"score": r.get("score", 50), "group": r.get("gender", "unknown"), "passed": r.get("score", 50) >= 70}
            for r in evaluation_data
        ]
        results["audits"]["demographic_parity"] = self.audit_demographic_parity(parity_data)

        # Equalized odds
        odds_data = [
            {
                "predicted": r.get("score", 50) >= 70,
                "actual": r.get("actual_outcome", r.get("score", 50) >= 70),
                "group": r.get("gender", "unknown"),
            }
            for r in evaluation_data
        ]
        results["audits"]["equalized_odds"] = self.audit_equalized_odds(odds_data)

        # Calibration
        cal_data = [
            {
                "predicted_prob": r.get("score", 50) / 100,
                "actual": r.get("actual_outcome", r.get("score", 50) >= 70),
                "group": r.get("gender", "unknown"),
            }
            for r in evaluation_data
        ]
        results["audits"]["calibration"] = self.audit_calibration(cal_data)

        # Intersectional
        results["audits"]["intersectional"] = self.audit_intersectional(evaluation_data)

        # Overall fairness verdict
        any_unfair = any(
            not audit.get("fair", True)
            for audit in results["audits"].values()
        )
        results["overall_fair"] = not any_unfair
        results["recommendation"] = (
            "All fairness checks passed." if not any_unfair
            else "Fairness violations detected. Review flagged metrics and apply mitigations."
        )

        # Store in history
        self._audit_history.append(results)

        return results

    # ── Post-deployment Monitoring ────────────────────

    def record_score(self, session_id: str, score: float, group: str, metadata: Optional[Dict] = None):
        """Record a score for real-time drift monitoring."""
        record = {
            "session_id": session_id,
            "score": score,
            "group": group,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        }
        self._drift_windows[group].append(record)

        # Trim to window size
        if len(self._drift_windows[group]) > self._window_size:
            self._drift_windows[group] = self._drift_windows[group][-self._window_size:]

    def check_drift(self, reference_group: Optional[str] = None) -> Dict[str, Any]:
        """Check for score distribution drift across groups."""
        if len(self._drift_windows) < 2:
            return {"drift_detected": False, "note": "Need at least 2 groups for drift comparison"}

        groups = list(self._drift_windows.keys())
        reference = reference_group or groups[0]
        ref_scores = [r["score"] for r in self._drift_windows.get(reference, [])]

        if len(ref_scores) < 10:
            return {"drift_detected": False, "note": "Insufficient reference data"}

        comparisons = {}
        drift_detected = False

        for g in groups:
            if g == reference:
                continue
            g_scores = [r["score"] for r in self._drift_windows.get(g, [])]
            if len(g_scores) < 10:
                comparisons[g] = {"status": "insufficient_data", "sample_size": len(g_scores)}
                continue

            mean_diff = abs(np.mean(ref_scores) - np.mean(g_scores))

            # KS test
            ks_stat = None
            ks_p = None
            if SCIPY_AVAILABLE:
                ks_stat, ks_p = scipy_stats.ks_2samp(ref_scores, g_scores)
                ks_stat = round(ks_stat, 4)
                ks_p = round(ks_p, 4)

            is_drifted = mean_diff > 10 or (ks_p is not None and ks_p < 0.05)
            if is_drifted:
                drift_detected = True

            comparisons[g] = {
                "mean_difference": round(mean_diff, 2),
                "reference_mean": round(float(np.mean(ref_scores)), 2),
                "group_mean": round(float(np.mean(g_scores)), 2),
                "ks_statistic": ks_stat,
                "ks_p_value": ks_p,
                "drift_detected": is_drifted,
                "sample_size": len(g_scores),
            }

        return {
            "drift_detected": drift_detected,
            "reference_group": reference,
            "comparisons": comparisons,
            "timestamp": datetime.utcnow().isoformat(),
        }

    # ── Mitigation Strategies ─────────────────────────

    def apply_reweighting(
        self, scores: List[Dict[str, Any]], target_attribute: str = "gender"
    ) -> List[Dict[str, Any]]:
        """Apply reweighting to balance group representation in scores."""
        groups = defaultdict(list)
        for s in scores:
            groups[s.get(target_attribute, "unknown")].append(s)

        total = len(scores)
        n_groups = len(groups)
        expected_per_group = total / n_groups if n_groups > 0 else total

        reweighted = []
        for g, records in groups.items():
            weight = expected_per_group / len(records) if records else 1.0
            for r in records:
                adjusted = r.copy()
                adjusted["fairness_weight"] = round(weight, 4)
                adjusted["adjusted_score"] = round(r.get("score", 50) * weight, 2)
                reweighted.append(adjusted)

        self._mitigation_log.append({
            "method": "reweighting",
            "attribute": target_attribute,
            "groups": {g: len(r) for g, r in groups.items()},
            "timestamp": datetime.utcnow().isoformat(),
        })

        return reweighted

    def apply_threshold_adjustment(
        self, groups_data: Dict[str, List[float]], target_rate: float = 0.5
    ) -> Dict[str, float]:
        """Compute group-specific thresholds to equalize pass rates."""
        adjusted_thresholds = {}

        for group, scores in groups_data.items():
            if not scores:
                adjusted_thresholds[group] = 70.0
                continue
            sorted_scores = sorted(scores)
            idx = int((1 - target_rate) * len(sorted_scores))
            idx = min(idx, len(sorted_scores) - 1)
            adjusted_thresholds[group] = round(sorted_scores[idx], 2)

        self._mitigation_log.append({
            "method": "threshold_adjustment",
            "target_rate": target_rate,
            "thresholds": adjusted_thresholds,
            "timestamp": datetime.utcnow().isoformat(),
        })

        return adjusted_thresholds

    # ── Reporting ─────────────────────────────────────

    def generate_fairness_report(self) -> Dict[str, Any]:
        """Generate comprehensive fairness report."""
        return {
            "audit_count": len(self._audit_history),
            "last_audit": self._audit_history[-1] if self._audit_history else None,
            "drift_status": self.check_drift(),
            "mitigation_history": self._mitigation_log[-10:],
            "monitored_groups": list(self._drift_windows.keys()),
            "total_scores_tracked": sum(
                len(v) for v in self._drift_windows.values()
            ),
            "generated_at": datetime.utcnow().isoformat(),
        }


# Singleton
fairness_service = FairnessService()
