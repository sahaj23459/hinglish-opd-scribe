"""Privacy, voice consent verification, audit logging, and Hinglish PHI redaction."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple


CONSENT_AFFIRMATIVE_CUES = (
    "haan",
    "han",
    "yes",
    "consent",
    "manzoor",
    "theek hai",
    "thik hai",
    "sammatti",
    "record kar sakte",
    "i agree",
    "अनुमति",
    "हाँ",
    "ठीक है",
    "ಸಮ್ಮತಿ",
    "ಹೌದು",
)

CONSENT_NEGATIVE_CUES = (
    "nahi",
    "naa",
    "mat karo",
    "no consent",
    "do not record",
    "mana hai",
    "नहीं",
    "मना",
    "ಬೇಡ",
)


@dataclass
class ConsentRecord:
    """Immutable audit record for volunteer/patient audio recording consent."""

    session_id: str
    participant_role: str
    consent_granted: bool
    verification_method: str
    audio_sha256: str
    storage_region: str = "ap-south-1"
    synthetic_data_only: bool = True
    timestamp_utc: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    notes: str = ""


class ConsentGateError(PermissionError):
    """Raised when audio processing is attempted without verified consent."""


def compute_file_sha256(path: Path) -> str:
    """Return hex SHA-256 digest of a file on disk."""
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_voice_consent_utterance(consent_transcript: str) -> bool:
    """Verify spoken consent utterance in Hinglish, Hindi, English, or Kannada.

    Any explicit refusal token immediately rejects consent even if affirmative
    words co-occur (e.g., 'haan par record mat karo' -> False).
    """
    text = consent_transcript.strip().lower()
    if not text:
        return False
    for neg in CONSENT_NEGATIVE_CUES:
        if re.search(rf"(?<!\w){re.escape(neg)}(?!\w)", text):
            return False
    for pos in CONSENT_AFFIRMATIVE_CUES:
        if re.search(rf"(?<!\w){re.escape(pos)}(?!\w)", text):
            return True
    return False


def enforce_consent_gate(record: ConsentRecord, audit_log_path: Optional[Path] = None) -> None:
    """Append consent check to append-only JSONL audit log and block if unconsented."""
    if audit_log_path is not None:
        audit_log_path.parent.mkdir(parents=True, exist_ok=True)
        with audit_log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")
    if not record.consent_granted:
        raise ConsentGateError(
            f"Processing blocked for session '{record.session_id}': voice/signed consent not granted."
        )


# Patterns targeting Indian OPD Protected Health Information (PHI)
_PHI_PATTERNS: List[Tuple[str, re.Pattern[str]]] = [
    # Aadhaar-style 12-digit numbers (4-4-4 space/hyphen separated)
    ("REDACTED_AADHAAR", re.compile(r"\b[2-9]\d{3}[\s-]?\d{4}[\s-]?\d{4}\b")),
    # ABHA IDs (14 digits: XX-XXXX-XXXX-XXXX or numeric)
    ("REDACTED_ABHA", re.compile(r"\b\d{2}-\d{4}-\d{4}-\d{4}\b")),
    # Indian mobile numbers (+91 / 0 prefix + 10 digits starting 6-9)
    ("REDACTED_PHONE", re.compile(r"(?:\+91[\s-]?|0)?\b[6-9]\d{9}\b")),
    # Hospital UHID / MRN codes
    ("REDACTED_UHID", re.compile(r"\b(?:UHID|MRN|OPD)[-\s:#]*\d{4,10}\b", re.IGNORECASE)),
    # Email addresses
    ("REDACTED_EMAIL", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
    # Self-introduced names in Hinglish / Hindi ("mera naam Rahul Sharma hai", "my name is ...")
    (
        "REDACTED_NAME",
        re.compile(
            r"(?<=\bmera naam\s)([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})(?=\s+hai\b|\b)"
            r"|(?<=\bmy name is\s)([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})"
            r"|(?<=\bpatient name\s)([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})",
            re.IGNORECASE,
        ),
    ),
    # Residential address cues ("sector 14 Rohini mein rehta hoon" / PIN codes)
    ("REDACTED_PINCODE", re.compile(r"\b[1-8]\d{5}\b")),
]


def redact_hinglish_phi(text: str) -> Tuple[str, Dict[str, int]]:
    """Redact Indian PHI spans from Hinglish/English transcripts before storage or LLM calls.

    Returns:
        Tuple of (redacted_text, counts_by_category).
    """
    redacted = text
    counts: Dict[str, int] = {}
    for tag, pattern in _PHI_PATTERNS:
        matches = list(pattern.finditer(redacted))
        if matches:
            counts[tag] = counts.get(tag, 0) + len(matches)
            redacted = pattern.sub(f"[{tag}]", redacted)
    return redacted, counts
