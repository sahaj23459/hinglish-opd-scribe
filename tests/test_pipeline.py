"""Automated unit & integration tests for Hinglish OPD Scribe (Lecture 9 Slide 11 requirement)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.asr.aws_transcribe_adapter import build_aws_transcribe_job_payload, estimate_project_cloud_budget
from src.asr.normalizer import compute_wer, normalize_hinglish_text
from src.eval.severity_metric import GoldAnnotation, compute_rank_divergence_stats, evaluate_consult_predictions
from src.fhir.fhir_builder import build_fhir_r4_bundle, validate_fhir_bundle_schema
from src.fhir.longitudinal_memory import PatientLongitudinalStore
from src.fhir.note_generator import generate_grounded_note
from src.linking.attribute_extractor import parse_duration, parse_fractional_hindi_number
from src.linking.concept_linker import ConstrainedSnomedLinker
from src.privacy.consent_and_redaction import (
    ConsentGateError,
    ConsentRecord,
    enforce_consent_gate,
    redact_hinglish_phi,
    verify_voice_consent_utterance,
)


ROOT = Path(__file__).resolve().parents[1]
HI_LEX_PATH = ROOT / "data" / "lexicon" / "hinglish_snomed_lexicon.json"
KN_LEX_PATH = ROOT / "data" / "lexicon" / "kannada_snomed_lexicon.json"
CONSULTS_PATH = ROOT / "data" / "manifests" / "pilot_consults_v1.json"


@pytest.fixture(scope="module")
def hi_linker() -> ConstrainedSnomedLinker:
    return ConstrainedSnomedLinker(HI_LEX_PATH)


@pytest.fixture(scope="module")
def kn_linker() -> ConstrainedSnomedLinker:
    return ConstrainedSnomedLinker(KN_LEX_PATH)


def test_devanagari_and_roman_normalization() -> None:
    dev = "डॉक्टर साहब, मुझे तीन दिन से बुखार है, पर सिर में दर्द नहीं है।"
    rom = "doctor sahab mujhe 3 din se bukhaar hai par sir me dard nahin hai"
    assert normalize_hinglish_text(dev) == normalize_hinglish_text(rom)
    assert compute_wer(dev, rom, normalize_script=True).error_rate == 0.0


def test_fractional_hindi_dosages() -> None:
    assert parse_fractional_hindi_number("paracetamol dedh goli subah shaam") == (1.5, "tablet")
    assert parse_fractional_hindi_number("metformin dhai tablet mat lijiye") == (2.5, "tablet")
    assert parse_fractional_hindi_number("amlodipine aadhi goli roz") == (0.5, "tablet")
    assert parse_fractional_hindi_number("metoprolol sawa goli") == (1.25, "tablet")
    assert parse_fractional_hindi_number("paune do goli") == (1.75, "tablet")
    assert parse_fractional_hindi_number("saadhe teen tablet") == (3.5, "tablet")
    # Ensure fractional duration ("dedh mahine") does NOT falsely trigger tablet dose
    assert parse_fractional_hindi_number("dedh mahine se bukhar hai") == (None, None)
    assert parse_duration("dedh mahine se bukhar hai") == (1.5, "mo")


def test_clause_scoped_negation_and_family_subject(hi_linker: ConstrainedSnomedLinker) -> None:
    txt = "mere pitaji ko dil ki bimari thi, mujhe teen din se bukhar hai par sir mein dard nahi hai"
    mentions = hi_linker.link_transcript(txt, mode="constrained_hybrid")
    by_code = {m.snomed_code: m for m in mentions}

    assert "56265001" in by_code  # Heart disease -> family_member
    assert by_code["56265001"].attributes.subject == "family_member"

    assert "386661006" in by_code  # Fever -> affirmed, 3 days
    assert by_code["386661006"].attributes.polarity == "affirmed"
    assert by_code["386661006"].attributes.duration_value == 3.0
    assert by_code["386661006"].attributes.duration_unit == "d"

    assert "25064002" in by_code  # Headache -> negated!
    assert by_code["25064002"].attributes.polarity == "negated"


def test_zero_hallucinated_codes_and_ambiguous_confirmation(hi_linker: ConstrainedSnomedLinker) -> None:
    txt = "pet mein gas banti hai aur subah chakkar aana hota hai"
    mentions = hi_linker.link_transcript(txt, mode="constrained_hybrid")
    assert len(mentions) >= 2
    for m in mentions:
        assert m.snomed_code in hi_linker.entries
        assert m.is_valid_snomed_in_lexicon is True
    # Idiomatic 'gas banti hai' or 'chakkar aana' routes to clinician confirmation
    assert any(m.needs_doctor_confirmation for m in mentions)


def test_severity_metric_penalizes_negation_flip_more_than_filler(hi_linker: ConstrainedSnomedLinker) -> None:
    ref = "doctor sahab mujhe teen din se bukhar hai par sir mein dard nahi hai"
    gold = [
        GoldAnnotation(snomed_code="386661006", preferred_term="Fever", semantic_tag="finding", polarity="affirmed", duration_value=3.0, duration_unit="d"),
        GoldAnnotation(snomed_code="25064002", preferred_term="Headache", semantic_tag="finding", polarity="negated"),
    ]

    # Hypothesis A: Drops 1 word 'nahi' -> Low WER (~7%), CRITICAL clinical severity!
    hyp_neg_flip = "doctor sahab mujhe teen din se bukhar hai par sir mein dard hai"
    res_a = evaluate_consult_predictions(
        "TEST-A", ref, hyp_neg_flip, gold, hi_linker.link_transcript(hyp_neg_flip), hi_linker
    )

    # Hypothesis B: Drops 3 filler words -> Higher WER (~23%), ZERO clinical severity!
    hyp_filler_drop = "mujhe teen din se bukhar hai par sir mein dard nahi hai"
    res_b = evaluate_consult_predictions(
        "TEST-B", ref, hyp_filler_drop, gold, hi_linker.link_transcript(hyp_filler_drop), hi_linker
    )

    assert res_a.normalized_wer < res_b.normalized_wer
    assert res_a.clinical_severity_score > res_b.clinical_severity_score
    assert res_a.has_critical_error is True
    assert res_b.clinical_severity_score == 0.0


def test_fhir_r4_bundle_and_longitudinal_delta(hi_linker: ConstrainedSnomedLinker) -> None:
    store = PatientLongitudinalStore(hi_linker)

    v1_txt = "mujhe diabetes hai aur baar baar peshab aata hai metformin ek goli le raha hoon"
    b1 = build_fhir_r4_bundle("V1", "PAT-1", "2026-09-01", hi_linker.link_transcript(v1_txt), visit_number=1)
    ok1, errs1 = validate_fhir_bundle_schema(b1)
    assert ok1, f"FHIR validation errors: {errs1}"
    store.add_visit_bundle("PAT-1", "V1", "2026-09-01", b1)

    v2_txt = "baar baar peshab nahi hai par paer mein jhanjhanahat hai metformin dedh goli kar dijiye"
    m2 = hi_linker.link_transcript(v2_txt)
    note2 = generate_grounded_note("V2", m2, candidate_freeform_claims=["Patient has acute appendicitis"])
    assert len(note2.blocked_unsupported_claims) == 1

    b2 = build_fhir_r4_bundle("V2", "PAT-1", "2026-10-15", m2, visit_number=2)
    ok2, errs2 = validate_fhir_bundle_schema(b2)
    assert ok2, f"FHIR validation errors: {errs2}"
    store.add_visit_bundle("PAT-1", "V2", "2026-10-15", b2)

    delta = store.summarize_changes_at_latest_visit("PAT-1")
    change_types = {item.change_type for item in delta.items}
    assert "RESOLVED" in change_types          # Polyuria resolved
    assert "PROGRESSION_ALERT" in change_types  # Neuropathy linked to prior Diabetes
    assert "MEDICATION_CHANGED" in change_types # Metformin 1.0 -> 1.5 tablets


def test_kannada_zero_code_change_portability(kn_linker: ConstrainedSnomedLinker) -> None:
    kn_txt = "ಡಾಕ್ಟರ್ ನನಗೆ ಮೂರು ದಿನದಿಂದ ಜ್ವರ ಇದೆ ಆದರೆ ತಲೆನೋವು ಇಲ್ಲ ಪ್ಯಾರಾಸಿಟಮಾಲ್ ಒಂದೂವರೆ ಮಾತ್ರೆ"
    mentions = kn_linker.link_transcript(kn_txt)
    by_code = {m.snomed_code: m for m in mentions}
    assert by_code["386661006"].attributes.polarity == "affirmed"
    assert by_code["25064002"].attributes.polarity == "negated"
    assert by_code["387517004"].attributes.dose_value == 1.5


def test_privacy_consent_and_phi_redaction(tmp_path: Path) -> None:
    assert verify_voice_consent_utterance("Haan doctor sahab, record kar sakte hain") is True
    assert verify_voice_consent_utterance("Haan par record mat karo") is False

    bad_rec = ConsentRecord(
        session_id="S-001",
        participant_role="volunteer",
        consent_granted=False,
        verification_method="voice",
        audio_sha256="abc123",
    )
    with pytest.raises(ConsentGateError):
        enforce_consent_gate(bad_rec, tmp_path / "audit.jsonl")

    dirty = "Mera naam Rahul Verma hai, phone +91 9876543210, ABHA 12-3456-7890-1234, UHID-88421."
    clean, counts = redact_hinglish_phi(dirty)
    assert "Rahul Verma" not in clean
    assert "9876543210" not in clean
    assert "12-3456-7890-1234" not in clean
    assert sum(counts.values()) >= 4


def test_cloud_governance_india_residency_and_budget() -> None:
    est = estimate_project_cloud_budget(num_consults=200, avg_consult_minutes=2.0, aws_transcribe_passes=2)
    assert est.ec2_gpu_instances_used == 0
    assert est.within_budget_cap is True
    with pytest.raises(ValueError):
        build_aws_transcribe_job_payload("job1", "s3://bucket/a.wav", region="us-east-1")


def test_rank_divergence_spearman_detector() -> None:
    arms = [
        ("Model_A", 0.12, 1.80),
        ("Model_B", 0.15, 0.35),
        ("Model_C", 0.28, 2.10),
        ("Model_D", 0.31, 0.90),
    ]
    stats = compute_rank_divergence_stats(arms)
    assert stats["pairwise_rank_inversion_count"] >= 2
    assert stats["hypothesis_supported_rho_lt_0_90"] is True
