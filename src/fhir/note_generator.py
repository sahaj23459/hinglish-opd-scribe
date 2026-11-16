"""Span-grounded English clinical note generator with strict hallucination blocking."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, List

from src.linking.concept_linker import LinkedMention


@dataclass
class GroundedSentence:
    """Single structured clinical statement linked to transcript span & SNOMED CT code."""

    section: str  # Subjective | Medications | FamilyHistory | ClinicianReviewQueue
    english_text: str
    snomed_code: str
    matched_span: str
    span_start: int
    span_end: int
    polarity: str
    needs_confirmation: bool


@dataclass
class StructuredGroundedNote:
    """Complete clinician-facing note with 100% span provenance and flagged unsupported checks."""

    consult_id: str
    subjective_findings: List[GroundedSentence] = field(default_factory=list)
    negated_pertinent_findings: List[GroundedSentence] = field(default_factory=list)
    medication_statements: List[GroundedSentence] = field(default_factory=list)
    family_history: List[GroundedSentence] = field(default_factory=list)
    clinician_confirmation_queue: List[GroundedSentence] = field(default_factory=list)
    blocked_unsupported_claims: List[str] = field(default_factory=list)

    def render_markdown(self) -> str:
        lines: List[str] = [f"### Structured Clinical Note (`{self.consult_id}`)"]
        if self.subjective_findings:
            lines.append("**Active Complaints & Findings:**")
            for s in self.subjective_findings:
                lines.append(
                    f"- {s.english_text} *(SNOMED `{s.snomed_code}`, span `{s.span_start}:{s.span_end}`: \"{s.matched_span}\")*"
                )
        if self.negated_pertinent_findings:
            lines.append("\n**Pertinent Negatives:**")
            for s in self.negated_pertinent_findings:
                lines.append(
                    f"- {s.english_text} *(SNOMED `{s.snomed_code}`, span `{s.span_start}:{s.span_end}`: \"{s.matched_span}\")*"
                )
        if self.medication_statements:
            lines.append("\n**Medications Reported / Discussed:**")
            for s in self.medication_statements:
                lines.append(
                    f"- {s.english_text} *(SNOMED `{s.snomed_code}`, span `{s.span_start}:{s.span_end}`: \"{s.matched_span}\")*"
                )
        if self.family_history:
            lines.append("\n**Family History:**")
            for s in self.family_history:
                lines.append(
                    f"- {s.english_text} *(SNOMED `{s.snomed_code}`, span `{s.span_start}:{s.span_end}`: \"{s.matched_span}\")*"
                )
        if self.clinician_confirmation_queue:
            lines.append("\n**Doctor One-Tap Confirmation Required (Low-Confidence / Ambiguous Idiom):**")
            for s in self.clinician_confirmation_queue:
                lines.append(f"- [CONFIRM?] {s.english_text} *(from \"{s.matched_span}\")*")
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


_UNIT_LABELS = {"d": "days", "wk": "weeks", "mo": "months", "yr": "years"}


def generate_grounded_note(
    consult_id: str,
    mentions: List[LinkedMention],
    candidate_freeform_claims: List[str] | None = None,
) -> StructuredGroundedNote:
    """Generate span-grounded English clinical note; block any claim without valid SNOMED + span."""
    note = StructuredGroundedNote(consult_id=consult_id)

    for m in mentions:
        if not m.is_valid_snomed_in_lexicon or not m.matched_span.strip():
            note.blocked_unsupported_claims.append(
                f"Blocked unverified concept '{m.preferred_term}' (code={m.snomed_code})"
            )
            continue

        at = m.attributes
        mods: List[str] = []
        if at.laterality:
            mods.append(f"{at.laterality}-sided")
        if at.duration_value is not None and at.duration_unit:
            dur_num = int(at.duration_value) if float(at.duration_value).is_integer() else at.duration_value
            mods.append(f"for {dur_num} {_UNIT_LABELS.get(at.duration_unit, at.duration_unit)}")

        mod_str = f" ({', '.join(mods)})" if mods else ""

        if m.semantic_tag == "medication":
            dose_parts: List[str] = []
            if at.strength_mg is not None:
                dose_parts.append(f"{int(at.strength_mg)} mg")
            if at.dose_value is not None:
                d_str = str(int(at.dose_value)) if float(at.dose_value).is_integer() else str(at.dose_value)
                dose_parts.append(f"{d_str} {at.dose_unit or 'tablet'}(s)")
            if at.frequency_code:
                dose_parts.append(at.frequency_code)
            dose_desc = f" — {', '.join(dose_parts)}" if dose_parts else ""
            if at.polarity == "negated":
                eng = f"Advised against / not taking {m.preferred_term}{dose_desc}"
            else:
                eng = f"Taking / prescribed {m.preferred_term}{dose_desc}{mod_str}"
            sent = GroundedSentence(
                section="Medications",
                english_text=eng,
                snomed_code=m.snomed_code,
                matched_span=m.matched_span,
                span_start=m.span_start,
                span_end=m.span_end,
                polarity=at.polarity,
                needs_confirmation=m.needs_doctor_confirmation,
            )
            note.medication_statements.append(sent)
        elif at.subject == "family_member":
            eng = f"Family history of {m.preferred_term}{mod_str}"
            sent = GroundedSentence(
                section="FamilyHistory",
                english_text=eng,
                snomed_code=m.snomed_code,
                matched_span=m.matched_span,
                span_start=m.span_start,
                span_end=m.span_end,
                polarity=at.polarity,
                needs_confirmation=m.needs_doctor_confirmation,
            )
            note.family_history.append(sent)
        elif at.polarity == "negated":
            eng = f"Denies {m.preferred_term}{mod_str}"
            sent = GroundedSentence(
                section="Subjective",
                english_text=eng,
                snomed_code=m.snomed_code,
                matched_span=m.matched_span,
                span_start=m.span_start,
                span_end=m.span_end,
                polarity="negated",
                needs_confirmation=m.needs_doctor_confirmation,
            )
            note.negated_pertinent_findings.append(sent)
        else:
            eng = f"Reports {m.preferred_term}{mod_str}"
            sent = GroundedSentence(
                section="Subjective",
                english_text=eng,
                snomed_code=m.snomed_code,
                matched_span=m.matched_span,
                span_start=m.span_start,
                span_end=m.span_end,
                polarity="affirmed",
                needs_confirmation=m.needs_doctor_confirmation,
            )
            note.subjective_findings.append(sent)

        if m.needs_doctor_confirmation:
            note.clinician_confirmation_queue.append(sent)

    # Check any optional external LLM candidate sentences for unsupported clinical claims
    if candidate_freeform_claims:
        grounded_terms = {m.preferred_term.lower() for m in mentions if m.is_valid_snomed_in_lexicon}
        for claim in candidate_freeform_claims:
            if not any(term in claim.lower() for term in grounded_terms):
                note.blocked_unsupported_claims.append(claim)

    return note
