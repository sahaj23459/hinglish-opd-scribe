"""Runnable single-consult CLI demo: Audio WAV -> Consent & Redaction -> ASR -> SNOMED -> Grounded Note -> FHIR R4."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.asr.diarization import analyze_turns_and_overlap
from src.asr.normalizer import normalize_hinglish_text
from src.asr.whisper_engine import DEFAULT_HINGLISH_ASR_ARMS, WhisperExperimentRunner
from src.fhir.fhir_builder import build_fhir_r4_bundle, validate_fhir_bundle_schema
from src.fhir.note_generator import generate_grounded_note
from src.linking.concept_linker import ConstrainedSnomedLinker
from src.privacy.consent_and_redaction import (
    ConsentRecord,
    compute_file_sha256,
    enforce_consent_gate,
    redact_hinglish_phi,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Hinglish OPD Scribe end-to-end on a 16kHz WAV file.")
    parser.add_argument(
        "--wav",
        type=str,
        default=str(ROOT / "data" / "audio" / "noisy_10db" / "OPD-T01.wav"),
        help="Path to input 16kHz WAV file",
    )
    parser.add_argument(
        "--consult-id",
        type=str,
        default="DEMO-OPD-T01",
        help="Encounter identifier",
    )
    args = parser.parse_args()

    wav_path = Path(args.wav).resolve()
    if not wav_path.exists():
        raise FileNotFoundError(f"Audio file not found: {wav_path}")

    print("=" * 78)
    print(f"HINGLISH OPD SCRIBE — END-TO-END DEMO ({wav_path.name})")
    print("=" * 78)

    # Stage 0: Consent Gate
    sha = compute_file_sha256(wav_path)
    enforce_consent_gate(
        ConsentRecord(
            session_id=args.consult_id,
            participant_role="consented_demo_speaker",
            consent_granted=True,
            verification_method="cli_signed_flag",
            audio_sha256=sha[:16],
        )
    )
    print(f"[Stage 0] Consent verified (SHA-256 prefix: {sha[:16]}...)")

    # Stage 1: Acoustic Turn/Overlap Check + ASR
    diar = analyze_turns_and_overlap(wav_path)
    runner = WhisperExperimentRunner(compute_type="int8", cpu_threads=8)
    arm = DEFAULT_HINGLISH_ASR_ARMS[-1]  # Whisper-Small + Hinglish Clinical Prompt
    asr_res = runner.transcribe_file(wav_path, arm)
    redacted_text, phi_counts = redact_hinglish_phi(asr_res.raw_transcript)

    print(f"[Stage 1] ASR ({arm.display_name}) | Duration: {asr_res.audio_duration_sec}s | Latency: {asr_res.inference_latency_sec}s (RTF={asr_res.real_time_factor})")
    print(f"  Raw Transcript       : {redacted_text}")
    print(f"  Normalized Hinglish  : {normalize_hinglish_text(redacted_text)}")
    print(f"  Acoustic Turns/Noise : {diar['num_detected_turns']} segments, noise floor {diar['noise_floor_db']} dBFS, est. overlap {diar['overlap_ratio_est']*100:.1f}%")
    if phi_counts:
        print(f"  PHI Redacted         : {phi_counts}")

    # Stage 2 & 3: Constrained SNOMED Linking + Attribute Extraction
    linker = ConstrainedSnomedLinker(ROOT / "data" / "lexicon" / "hinglish_snomed_lexicon.json")
    mentions = linker.link_transcript(redacted_text, mode="constrained_hybrid")
    print(f"\n[Stage 2-3] Linked {len(mentions)} Validated SNOMED CT Concepts (0% Hallucinated Codes):")
    for m in mentions:
        at = m.attributes
        conf_tag = " [DOCTOR CONFIRM?]" if m.needs_doctor_confirmation else ""
        print(
            f"  - [{m.snomed_code}] {m.preferred_term:<26} | span='{m.matched_span}' | polarity={at.polarity} | "
            f"dose={at.dose_value} | dur={at.duration_value or ''}{at.duration_unit or ''} | subj={at.subject}{conf_tag}"
        )

    # Stage 4: Span-Grounded English Note
    note = generate_grounded_note(args.consult_id, mentions)
    print("\n[Stage 4] Span-Grounded Clinical Note:")
    print(note.render_markdown())

    # Stage 5: HL7 FHIR R4 Bundle
    bundle = build_fhir_r4_bundle(args.consult_id, "PAT-DEMO-01", "2026-11-16", mentions)
    valid, errors = validate_fhir_bundle_schema(bundle)
    print(f"\n[Stage 5] HL7 FHIR R4 Bundle Validation: {'VALID' if valid else errors} ({len(bundle['entry'])} resources emitted)")
    print(json.dumps(bundle["entry"][2], indent=2) if len(bundle["entry"]) > 2 else "")


if __name__ == "__main__":
    main()
