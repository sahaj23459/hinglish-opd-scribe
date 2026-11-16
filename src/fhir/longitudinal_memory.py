"""Longitudinal multi-visit FHIR memory & SNOMED hierarchy change-summary engine."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional

from src.linking.concept_linker import ConstrainedSnomedLinker


@dataclass
class LongitudinalDeltaItem:
    """Single clinician-facing change item citing prior & current visit IDs."""

    change_type: str  # NEW | RESOLVED | PERSISTENT | PROGRESSION_ALERT | MEDICATION_CHANGED | MEDICATION_STOPPED
    snomed_code: str
    preferred_term: str
    summary_text: str
    cited_visits: List[str]
    organ_branch: str


@dataclass
class LongitudinalChangeSummary:
    """Clinician decision-support delta summary comparing Visit t against Visits 1..t-1."""

    patient_id: str
    current_visit_id: str
    prior_visit_ids: List[str]
    items: List[LongitudinalDeltaItem] = field(default_factory=list)
    disclaimer: str = "Clinician-facing longitudinal summary from prior FHIR visits; not direct patient advice."

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


class PatientLongitudinalStore:
    """Stores sequential HL7 FHIR R4 bundles per patient and computes cross-visit trajectories."""

    def __init__(self, linker: ConstrainedSnomedLinker) -> None:
        self.linker = linker
        self._visits_by_patient: Dict[str, List[Dict[str, object]]] = {}

    def add_visit_bundle(self, patient_id: str, consult_id: str, visit_date: str, bundle: Dict[str, object]) -> None:
        self._visits_by_patient.setdefault(patient_id, []).append(
            {
                "consult_id": consult_id,
                "visit_date": visit_date,
                "bundle": bundle,
            }
        )

    @staticmethod
    def _extract_bundle_snapshot(bundle: Dict[str, object]) -> Dict[str, Dict[str, object]]:
        """Extract conditions (confirmed vs refuted) and medications with doses from a FHIR bundle."""
        conds: Dict[str, Dict[str, object]] = {}
        meds: Dict[str, Dict[str, object]] = {}

        for ent in bundle.get("entry", []):  # type: ignore[union-attr]
            res = ent.get("resource", {})
            rtype = res.get("resourceType")
            if rtype == "Condition":
                coding = res.get("code", {}).get("coding", [{}])[0]
                code = str(coding.get("code", ""))
                disp = str(coding.get("display", ""))
                ver = res.get("verificationStatus", {}).get("coding", [{}])[0].get("code", "confirmed")
                if code:
                    conds[code] = {"display": disp, "verification": ver}
            elif rtype == "MedicationStatement":
                coding = res.get("medicationCodeableConcept", {}).get("coding", [{}])[0]
                code = str(coding.get("code", ""))
                disp = str(coding.get("display", ""))
                status = str(res.get("status", "active"))
                dose_val: Optional[float] = None
                dosages = res.get("dosage", [])
                if dosages:
                    dr = dosages[0].get("doseAndRate", [])
                    if dr:
                        dose_val = dr[0].get("doseQuantity", {}).get("value")
                if code:
                    meds[code] = {"display": disp, "status": status, "dose_value": dose_val}

        return {"conditions": conds, "medications": meds}

    def summarize_changes_at_latest_visit(self, patient_id: str) -> LongitudinalChangeSummary:
        """Compare latest visit against all prior visits for a patient."""
        history = self._visits_by_patient.get(patient_id, [])
        if not history:
            return LongitudinalChangeSummary(patient_id=patient_id, current_visit_id="", prior_visit_ids=[])

        curr = history[-1]
        priors = history[:-1]
        summary = LongitudinalChangeSummary(
            patient_id=patient_id,
            current_visit_id=str(curr["consult_id"]),
            prior_visit_ids=[str(p["consult_id"]) for p in priors],
        )
        if not priors:
            return summary

        curr_snap = self._extract_bundle_snapshot(curr["bundle"])  # type: ignore[arg-type]
        prior_cond_history: Dict[str, List[Tuple[str, str]]] = {}
        prior_med_history: Dict[str, List[Tuple[str, str, Optional[float]]]] = {}

        for p in priors:
            p_id = str(p["consult_id"])
            p_snap = self._extract_bundle_snapshot(p["bundle"])  # type: ignore[arg-type]
            for c_code, c_info in p_snap["conditions"].items():
                prior_cond_history.setdefault(c_code, []).append((p_id, str(c_info["verification"])))
            for m_code, m_info in p_snap["medications"].items():
                prior_med_history.setdefault(m_code, []).append(
                    (p_id, str(m_info["status"]), m_info.get("dose_value"))  # type: ignore[arg-type]
                )

        # 1. Analyze Conditions (NEW, PERSISTENT, RESOLVED, PROGRESSION_ALERT)
        for c_code, c_info in curr_snap["conditions"].items():
            ent = self.linker.entries.get(c_code)
            branch = ent.organ_branch if ent else "general"
            disp = str(c_info["display"])
            curr_ver = str(c_info["verification"])

            prior_active_visits = [
                vid for vid, ver in prior_cond_history.get(c_code, []) if ver in ("confirmed", "provisional")
            ]

            if curr_ver == "refuted" and prior_active_visits:
                summary.items.append(
                    LongitudinalDeltaItem(
                        change_type="RESOLVED",
                        snomed_code=c_code,
                        preferred_term=disp,
                        summary_text=f"{disp} now negated/resolved (previously active in {', '.join(prior_active_visits)}).",
                        cited_visits=prior_active_visits + [str(curr["consult_id"])],
                        organ_branch=branch,
                    )
                )
            elif curr_ver in ("confirmed", "provisional"):
                if prior_active_visits:
                    summary.items.append(
                        LongitudinalDeltaItem(
                            change_type="PERSISTENT",
                            snomed_code=c_code,
                            preferred_term=disp,
                            summary_text=f"Persistent/recurring {disp} across {len(prior_active_visits) + 1} visits ({', '.join(prior_active_visits)} -> {curr['consult_id']}).",
                            cited_visits=prior_active_visits + [str(curr["consult_id"])],
                            organ_branch=branch,
                        )
                    )
                else:
                    # Check if related to an earlier chronic disorder (e.g., Diabetes -> Neuropathy/Dizziness)
                    related_priors: List[str] = []
                    for old_code, old_records in prior_cond_history.items():
                        if any(v in ("confirmed", "provisional") for _, v in old_records):
                            dist = self.linker.snomed_hierarchy_distance(c_code, old_code)
                            old_ent = self.linker.entries.get(old_code)
                            if dist <= 2 or (
                                old_ent
                                and ent
                                and old_ent.clinical_domain == ent.clinical_domain
                                and old_ent.semantic_tag == "disorder"
                            ):
                                old_vids = [vid for vid, v in old_records if v in ("confirmed", "provisional")]
                                related_priors.extend(old_vids)

                    if related_priors:
                        uniq = sorted(set(related_priors))
                        summary.items.append(
                            LongitudinalDeltaItem(
                                change_type="PROGRESSION_ALERT",
                                snomed_code=c_code,
                                preferred_term=disp,
                                summary_text=f"New complication/related finding {disp} linked to prior domain history in {', '.join(uniq)}.",
                                cited_visits=uniq + [str(curr["consult_id"])],
                                organ_branch=branch,
                            )
                        )
                    else:
                        summary.items.append(
                            LongitudinalDeltaItem(
                                change_type="NEW",
                                snomed_code=c_code,
                                preferred_term=disp,
                                summary_text=f"Newly reported {disp} at {curr['consult_id']}.",
                                cited_visits=[str(curr["consult_id"])],
                                organ_branch=branch,
                            )
                        )

        # 2. Analyze Medication Changes (Dose titration, newly started, stopped)
        for m_code, m_info in curr_snap["medications"].items():
            disp = str(m_info["display"])
            curr_status = str(m_info["status"])
            curr_dose = m_info.get("dose_value")
            prior_meds = prior_med_history.get(m_code, [])

            if not prior_meds and curr_status == "active":
                summary.items.append(
                    LongitudinalDeltaItem(
                        change_type="NEW",
                        snomed_code=m_code,
                        preferred_term=disp,
                        summary_text=f"Started {disp} ({curr_dose or 'unspecified'} tab) at {curr['consult_id']}.",
                        cited_visits=[str(curr["consult_id"])],
                        organ_branch="drug",
                    )
                )
            elif prior_meds:
                last_vid, last_status, last_dose = prior_meds[-1]
                if curr_status == "not-taken" and last_status == "active":
                    summary.items.append(
                        LongitudinalDeltaItem(
                            change_type="MEDICATION_STOPPED",
                            snomed_code=m_code,
                            preferred_term=disp,
                            summary_text=f"{disp} stopped / adherence gap (was active in {last_vid}).",
                            cited_visits=[last_vid, str(curr["consult_id"])],
                            organ_branch="drug",
                        )
                    )
                elif curr_dose != last_dose and curr_dose is not None and last_dose is not None:
                    summary.items.append(
                        LongitudinalDeltaItem(
                            change_type="MEDICATION_CHANGED",
                            snomed_code=m_code,
                            preferred_term=disp,
                            summary_text=f"{disp} dose changed from {last_dose} -> {curr_dose} tablet(s) ({last_vid} -> {curr['consult_id']}).",
                            cited_visits=[last_vid, str(curr["consult_id"])],
                            organ_branch="drug",
                        )
                    )

        return summary
