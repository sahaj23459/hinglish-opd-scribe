"""Clinical Severity-Aware Evaluation Metric (CS-WER / CSS / CCER) vs Plain WER."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional, Tuple

from scipy.stats import spearmanr

from src.asr.normalizer import compute_cer, compute_wer
from src.linking.concept_linker import ConstrainedSnomedLinker, LinkedMention


SEVERITY_WEIGHTS = {
    "CRITICAL": 5.0,  # Negation flip, drug/dose swap, family-vs-patient subject flip
    "HIGH": 3.0,      # Laterality/duration unit swap, cross-organ SNOMED branch error, hallucinated code, missed primary finding
    "LOW": 1.0,       # SNOMED sibling/same-organ substitution
    "IGNORED": 0.0,   # Conversational filler / Roman spelling variant with zero clinical effect
}


@dataclass
class GoldAnnotation:
    """Ground-truth structured clinical item for a consult."""

    snomed_code: str
    preferred_term: str
    semantic_tag: str
    polarity: str = "affirmed"
    subject: str = "patient"
    dose_value: Optional[float] = None
    duration_value: Optional[float] = None
    duration_unit: Optional[str] = None
    laterality: Optional[str] = None


@dataclass
class ClinicalErrorEvent:
    """Detailed record of a single clinical error stratified by patient-safety risk."""

    error_category: str
    severity_tier: str  # CRITICAL | HIGH | LOW
    penalty_weight: float
    description: str
    gold_code: Optional[str] = None
    pred_code: Optional[str] = None


@dataclass
class ConsultEvaluationResult:
    """Combined speech (WER/CER) and clinical safety evaluation for a single OPD consult."""

    consult_id: str
    raw_wer: float
    normalized_wer: float
    normalized_cer: float
    snomed_precision: float
    snomed_recall: float
    snomed_f1: float
    critical_error_count: int
    high_error_count: int
    low_error_count: int
    hallucinated_code_count: int
    total_severity_penalty: float
    clinical_severity_score: float  # Penalty per gold clinical item (CS-WER analog)
    has_critical_error: bool
    errors: List[ClinicalErrorEvent] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def evaluate_consult_predictions(
    consult_id: str,
    reference_transcript: str,
    hypothesis_transcript: str,
    gold_items: List[GoldAnnotation],
    predicted_mentions: List[LinkedMention],
    linker: ConstrainedSnomedLinker,
) -> ConsultEvaluationResult:
    """Score both plain lexical WER/CER and Clinical Severity-Weighted errors."""
    raw_wer_obj = compute_wer(reference_transcript, hypothesis_transcript, normalize_script=False)
    norm_wer_obj = compute_wer(reference_transcript, hypothesis_transcript, normalize_script=True)
    norm_cer_obj = compute_cer(reference_transcript, hypothesis_transcript, normalize_script=True)

    errors: List[ClinicalErrorEvent] = []
    hallucinated_count = 0

    # Separate invalid/hallucinated SNOMED predictions first
    valid_preds: List[LinkedMention] = []
    for p in predicted_mentions:
        if not p.is_valid_snomed_in_lexicon or p.snomed_code not in linker.entries:
            hallucinated_count += 1
            errors.append(
                ClinicalErrorEvent(
                    error_category="HALLUCINATED_SNOMED_CODE",
                    severity_tier="HIGH",
                    penalty_weight=SEVERITY_WEIGHTS["HIGH"],
                    description=f"Invented/ungrounded SNOMED code '{p.snomed_code}' on span '{p.matched_span}'.",
                    pred_code=p.snomed_code,
                )
            )
        else:
            valid_preds.append(p)

    matched_pred_indices: set[int] = set()
    exact_code_tp = 0

    for g in gold_items:
        # 1. Look for exact SNOMED code match
        exact_idx = None
        for idx, p in enumerate(valid_preds):
            if idx not in matched_pred_indices and p.snomed_code == g.snomed_code:
                exact_idx = idx
                break

        if exact_idx is not None:
            matched_pred_indices.add(exact_idx)
            exact_code_tp += 1
            p = valid_preds[exact_idx]
            at = p.attributes

            # Check CRITICAL modifier errors on matched concept!
            if at.polarity != g.polarity:
                errors.append(
                    ClinicalErrorEvent(
                        error_category="NEGATION_FLIP",
                        severity_tier="CRITICAL",
                        penalty_weight=SEVERITY_WEIGHTS["CRITICAL"],
                        description=f"Negation flip on {g.preferred_term} ({g.snomed_code}): gold='{g.polarity}' vs pred='{at.polarity}'.",
                        gold_code=g.snomed_code,
                        pred_code=p.snomed_code,
                    )
                )
            if at.subject != g.subject:
                errors.append(
                    ClinicalErrorEvent(
                        error_category="SUBJECT_ATTRIBUTION_FLIP",
                        severity_tier="CRITICAL",
                        penalty_weight=SEVERITY_WEIGHTS["CRITICAL"],
                        description=f"Subject flip on {g.preferred_term}: gold='{g.subject}' vs pred='{at.subject}'.",
                        gold_code=g.snomed_code,
                        pred_code=p.snomed_code,
                    )
                )
            if g.dose_value is not None and at.dose_value != g.dose_value:
                errors.append(
                    ClinicalErrorEvent(
                        error_category="FRACTIONAL_DOSE_ERROR",
                        severity_tier="CRITICAL",
                        penalty_weight=SEVERITY_WEIGHTS["CRITICAL"],
                        description=f"Medication dose mismatch on {g.preferred_term}: gold={g.dose_value} vs pred={at.dose_value} tablet(s).",
                        gold_code=g.snomed_code,
                        pred_code=p.snomed_code,
                    )
                )
            if g.laterality and at.laterality != g.laterality:
                errors.append(
                    ClinicalErrorEvent(
                        error_category="LATERALITY_ERROR",
                        severity_tier="HIGH",
                        penalty_weight=SEVERITY_WEIGHTS["HIGH"],
                        description=f"Laterality mismatch on {g.preferred_term}: gold='{g.laterality}' vs pred='{at.laterality}'.",
                        gold_code=g.snomed_code,
                        pred_code=p.snomed_code,
                    )
                )
            if g.duration_unit and (at.duration_unit != g.duration_unit or at.duration_value != g.duration_value):
                errors.append(
                    ClinicalErrorEvent(
                        error_category="TEMPORAL_DURATION_ERROR",
                        severity_tier="HIGH",
                        penalty_weight=SEVERITY_WEIGHTS["HIGH"],
                        description=f"Duration mismatch on {g.preferred_term}: gold={g.duration_value}{g.duration_unit} vs pred={at.duration_value}{at.duration_unit}.",
                        gold_code=g.snomed_code,
                        pred_code=p.snomed_code,
                    )
                )
        else:
            # 2. Check if substituted with a near/far SNOMED concept
            best_sub_idx = None
            best_dist = 99
            for idx, p in enumerate(valid_preds):
                if idx in matched_pred_indices:
                    continue
                dist = linker.snomed_hierarchy_distance(g.snomed_code, p.snomed_code)
                if dist < best_dist:
                    best_dist = dist
                    best_sub_idx = idx

            if best_sub_idx is not None and best_dist <= 2:
                matched_pred_indices.add(best_sub_idx)
                p = valid_preds[best_sub_idx]
                errors.append(
                    ClinicalErrorEvent(
                        error_category="SNOMED_SIBLING_SUBSTITUTION",
                        severity_tier="LOW",
                        penalty_weight=SEVERITY_WEIGHTS["LOW"],
                        description=f"Near-neighbour SNOMED substitution: gold={g.preferred_term} ({g.snomed_code}) vs pred={p.preferred_term} ({p.snomed_code}), dist={best_dist}.",
                        gold_code=g.snomed_code,
                        pred_code=p.snomed_code,
                    )
                )
            elif g.semantic_tag == "medication":
                errors.append(
                    ClinicalErrorEvent(
                        error_category="MISSED_OR_SWAPPED_MEDICATION",
                        severity_tier="CRITICAL",
                        penalty_weight=SEVERITY_WEIGHTS["CRITICAL"],
                        description=f"Missed/swapped medication {g.preferred_term} ({g.snomed_code}).",
                        gold_code=g.snomed_code,
                    )
                )
            else:
                errors.append(
                    ClinicalErrorEvent(
                        error_category="MISSED_CLINICAL_CONCEPT",
                        severity_tier="HIGH",
                        penalty_weight=SEVERITY_WEIGHTS["HIGH"],
                        description=f"Missed clinical concept {g.preferred_term} ({g.snomed_code}, polarity={g.polarity}).",
                        gold_code=g.snomed_code,
                    )
                )

    # 3. Remaining unmatched valid predictions -> False-positive / far-branch clinical additions
    for idx, p in enumerate(valid_preds):
        if idx not in matched_pred_indices:
            tier = "CRITICAL" if p.semantic_tag == "medication" else "HIGH"
            errors.append(
                ClinicalErrorEvent(
                    error_category="UNSUPPORTED_FALSE_POSITIVE_CONCEPT",
                    severity_tier=tier,
                    penalty_weight=SEVERITY_WEIGHTS[tier],
                    description=f"Spurious concept linked: {p.preferred_term} ({p.snomed_code}) from '{p.matched_span}'.",
                    pred_code=p.snomed_code,
                )
            )

    n_gold = max(1, len(gold_items))
    n_pred_total = len(predicted_mentions)
    precision = exact_code_tp / n_pred_total if n_pred_total > 0 else (1.0 if len(gold_items) == 0 else 0.0)
    recall = exact_code_tp / len(gold_items) if len(gold_items) > 0 else 1.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

    crit_c = sum(1 for e in errors if e.severity_tier == "CRITICAL")
    high_c = sum(1 for e in errors if e.severity_tier == "HIGH")
    low_c = sum(1 for e in errors if e.severity_tier == "LOW")
    total_pen = sum(e.penalty_weight for e in errors)
    css = total_pen / n_gold

    return ConsultEvaluationResult(
        consult_id=consult_id,
        raw_wer=round(raw_wer_obj.error_rate, 4),
        normalized_wer=round(norm_wer_obj.error_rate, 4),
        normalized_cer=round(norm_cer_obj.error_rate, 4),
        snomed_precision=round(precision, 4),
        snomed_recall=round(recall, 4),
        snomed_f1=round(f1, 4),
        critical_error_count=crit_c,
        high_error_count=high_c,
        low_error_count=low_c,
        hallucinated_code_count=hallucinated_count,
        total_severity_penalty=round(total_pen, 3),
        clinical_severity_score=round(css, 4),
        has_critical_error=(crit_c > 0),
        errors=errors,
    )


def compute_rank_divergence_stats(
    arm_summaries: List[Tuple[str, float, float]],
) -> Dict[str, object]:
    """Test Hypothesis H1: Do model/condition rankings diverge between plain WER and Clinical Severity Score?

    Args:
        arm_summaries: List of (arm_label, mean_wer, mean_clinical_severity_score).
    """
    if len(arm_summaries) < 3:
        return {"spearman_rho": 1.0, "p_value": 1.0, "pairwise_rank_inversions": 0}

    wers = [x[1] for x in arm_summaries]
    sev_scores = [x[2] for x in arm_summaries]
    rho, p_val = spearmanr(wers, sev_scores)

    inversions: List[Dict[str, object]] = []
    n = len(arm_summaries)
    for i in range(n):
        for j in range(i + 1, n):
            name_i, w_i, s_i = arm_summaries[i]
            name_j, w_j, s_j = arm_summaries[j]
            if (w_i < w_j and s_i > s_j) or (w_i > w_j and s_i < s_j):
                inversions.append(
                    {
                        "pair": f"{name_i} vs {name_j}",
                        "wer_pair": (round(w_i, 4), round(w_j, 4)),
                        "severity_pair": (round(s_i, 4), round(s_j, 4)),
                    }
                )

    wer_ranked = [x[0] for x in sorted(arm_summaries, key=lambda t: t[1])]
    sev_ranked = [x[0] for x in sorted(arm_summaries, key=lambda t: t[2])]

    return {
        "spearman_rho": round(float(rho), 4),
        "p_value": round(float(p_val), 4),
        "hypothesis_supported_rho_lt_0_90": bool(float(rho) < 0.90 or len(inversions) > 0),
        "pairwise_rank_inversion_count": len(inversions),
        "inversions": inversions,
        "ranking_by_plain_wer": wer_ranked,
        "ranking_by_clinical_severity": sev_ranked,
    }
