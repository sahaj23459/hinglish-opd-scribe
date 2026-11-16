"""Clause-aware Hinglish/Kannada negation, fractional dosage, duration, laterality & subject extraction."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional, Tuple

from src.asr.normalizer import normalize_hinglish_text


CLAUSE_BOUNDARY_RE = re.compile(
    r"\b(?:par|lekin|magar|jabki|aur|halanki|but|however|although|aadare|mattu)\b"
    r"|(?:(?<=\bhai)|(?<=\btha)|(?<=\bthi)|(?<=\bthe)|(?<=\bhoon)|(?<=\bhua)|(?<=\bhui))\s+(?=(?:mujhe|mujhko|mera|meri|mere|nanage|ab|abhi|kal|aaj|doctor|paracetamol|metformin|amlodipine|cetirizine|amoxicillin|pantoprazole|omeprazole|ibuprofen|ondansetron|glimepiride|metoprolol|salbutamol|ors|urine|bhaap)\b)"
    r"|(?:(?<=\blijiye)|(?<=\blein)|(?<=\bdijiye)|(?<=\brakhein)|(?<=\billa)|(?<=\bbeda)|(?<=\bide))\s+"
    r"|[।,.;?!]+",
    re.IGNORECASE,
)

POST_NEGATION_RE = re.compile(
    r"\b(?:nahi|nahee|nahin|mat|mana|illa|beda|never|absent|normal\s+hai|theek\s+hai|kam\s+ho\s+gaya\s+ab\s+nahi)\b",
    re.IGNORECASE,
)

PRE_NEGATION_RE = re.compile(
    r"\b(?:no|without|denies|denied|ruled\s+out|bina|koi\s+bhi\s+nahi|na\s+toh|na)\b",
    re.IGNORECASE,
)

FAMILY_SUBJECT_RE = re.compile(
    r"\b(?:pitaji|papa|father|mataji|mummy|maa|mother|bhai|behen|dada|dadi|nana|nani|family)\s*(?:ko|mein|ka|ki|had|has)?\b",
    re.IGNORECASE,
)

PATIENT_SELF_OVERRIDE_RE = re.compile(
    r"\b(?:mujhe|mujhko|nanage)\b|\b(?:mera|meri|mere)\s+(?!(?:pitaji|papa|father|mataji|mummy|maa|mother|bhai|behen|dada|dadi|nana|nani|family)\b)",
    re.IGNORECASE,
)

# Hindi/Kannada cardinal numerals
CARDINAL_NUMBERS: Dict[str, float] = {
    "ek": 1.0, "ondu": 1.0, "one": 1.0, "1": 1.0,
    "do": 2.0, "eradu": 2.0, "two": 2.0, "2": 2.0,
    "teen": 3.0, "mooru": 3.0, "three": 3.0, "3": 3.0,
    "chaar": 4.0, "char": 4.0, "four": 4.0, "4": 4.0,
    "paanch": 5.0, "panch": 5.0, "five": 5.0, "5": 5.0,
    "chhah": 6.0, "chhe": 6.0, "six": 6.0, "6": 6.0,
    "saat": 7.0, "seven": 7.0, "7": 7.0,
    "aath": 8.0, "eight": 8.0, "8": 8.0,
    "das": 10.0, "ten": 10.0, "10": 10.0,
    "pandrah": 15.0, "fifteen": 15.0, "15": 15.0,
}

DOSE_UNIT_WORDS = r"(?:goli|goliyan|tablet|tablets|tab|capsule|cap|maatre|spoon|chammach|ml)"


@dataclass
class ExtractedAttributes:
    """Clinical modifiers attached to a linked SNOMED CT concept mention."""

    polarity: str = "affirmed"  # affirmed | negated
    subject: str = "patient"  # patient | family_member
    dose_value: Optional[float] = None
    dose_unit: Optional[str] = None
    strength_mg: Optional[float] = None
    frequency_code: Optional[str] = None  # QD | BID | TID | PRN
    duration_value: Optional[float] = None
    duration_unit: Optional[str] = None  # d | wk | mo | yr
    laterality: Optional[str] = None  # left | right | bilateral
    clause_text: str = ""

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def split_into_clauses(normalized_text: str) -> List[Tuple[int, int, str]]:
    """Split normalized Hinglish sentence into local semantic clauses with character offsets."""
    clauses: List[Tuple[int, int, str]] = []
    last_idx = 0
    for match in CLAUSE_BOUNDARY_RE.finditer(normalized_text):
        seg = normalized_text[last_idx : match.start()].strip()
        if seg:
            clauses.append((last_idx, match.start(), seg))
        last_idx = match.end()
    tail = normalized_text[last_idx:].strip()
    if tail:
        clauses.append((last_idx, len(normalized_text), tail))
    if not clauses and normalized_text.strip():
        clauses.append((0, len(normalized_text), normalized_text.strip()))
    return clauses


def find_enclosing_clause(normalized_text: str, span_start: int, span_end: int) -> str:
    """Return the local clause containing `[span_start, span_end]`."""
    clauses = split_into_clauses(normalized_text)
    mid = (span_start + span_end) // 2
    for c_start, c_end, c_text in clauses:
        if c_start <= mid <= c_end:
            return c_text
    return normalized_text


def parse_fractional_hindi_number(clause: str) -> Tuple[Optional[float], Optional[str]]:
    """Parse Hindi/Kannada fractional and cardinal medication doses (e.g. 'dedh goli' -> 1.5 tablet)."""
    c = clause.lower()

    # Explicit compound fractions first: "saadhe teen" (3.5), "paune do" (1.75), "sawa do" (2.25)
    m_saadhe = re.search(rf"\bsaadhe\s+(\w+)\s*{DOSE_UNIT_WORDS}?\b", c)
    if m_saadhe and m_saadhe.group(1) in CARDINAL_NUMBERS:
        return CARDINAL_NUMBERS[m_saadhe.group(1)] + 0.5, "tablet"

    m_paune = re.search(rf"\bpaune\s+(\w+)\s*{DOSE_UNIT_WORDS}?\b", c)
    if m_paune and m_paune.group(1) in CARDINAL_NUMBERS:
        return max(0.25, CARDINAL_NUMBERS[m_paune.group(1)] - 0.25), "tablet"

    m_sawa = re.search(rf"\bsawa\s+(\w+)\s*{DOSE_UNIT_WORDS}?\b", c)
    if m_sawa and m_sawa.group(1) in CARDINAL_NUMBERS:
        return CARDINAL_NUMBERS[m_sawa.group(1)] + 0.25, "tablet"

    # Standalone fractional words near tablet/goli/maatre or standalone in medication clause
    standalone_fractions: List[Tuple[str, float]] = [
        (r"\b(?:dhai|eraduvaare|2\.5)\b", 2.5),
        (r"\b(?:dedh|onduvare|1\.5)\b", 1.5),
        (r"\bsawa\b", 1.25),
        (r"\bpaune\b", 0.75),
        (r"\b(?:aadhi|aadha|ardha|half|0\.5)\b", 0.5),
    ]
    for pat, val in standalone_fractions:
        if re.search(rf"{pat}(?:\s+{DOSE_UNIT_WORDS})?", c):
            # Avoid confusing "dedh mahine" / "dhai din" duration with tablet dose!
            if not re.search(rf"{pat}\s+(?:din|dino|hafte|mahine|mahina|saal|ghante)\b", c):
                return val, "tablet"

    # Cardinal number directly preceding dose unit ("do goli", "ek tablet", "ondu maatre")
    m_card = re.search(rf"\b(\w+)\s+({DOSE_UNIT_WORDS})\b", c)
    if m_card and m_card.group(1) in CARDINAL_NUMBERS:
        unit_raw = m_card.group(2)
        unit = "ml" if unit_raw == "ml" else "tablet"
        return CARDINAL_NUMBERS[m_card.group(1)], unit

    return None, None


def parse_strength_mg(clause: str) -> Optional[float]:
    """Extract milligram strength if spoken (e.g. '500 mg', '650mg')."""
    m = re.search(r"\b(\d{2,4})\s*mg\b", clause.lower())
    if m:
        return float(m.group(1))
    return None


def parse_duration(clause: str) -> Tuple[Optional[float], Optional[str]]:
    """Extract symptom or medication duration ('teen din se' -> (3.0, 'd'), 'teen mahine' -> (3.0, 'mo'))."""
    c = clause.lower()
    unit_map = {
        "din": "d", "dino": "d", "day": "d", "days": "d", "dinadinda": "d", "dinagalinda": "d",
        "hafte": "wk", "hafta": "wk", "week": "wk", "weeks": "wk",
        "mahine": "mo", "mahina": "mo", "month": "mo", "months": "mo", "tingalinda": "mo",
        "saal": "yr", "year": "yr", "years": "yr",
    }
    # Fractional duration ("dedh mahine", "dhai din")
    frac_dur = {"aadhi": 0.5, "dedh": 1.5, "dhai": 2.5}
    for f_word, f_val in frac_dur.items():
        m_f = re.search(
            r"\b" + f_word + r"\s+(din|dino|day|days|hafte|hafta|mahine|mahina|saal)\b",
            c,
        )
        if m_f:
            return f_val, unit_map[m_f.group(1)]

    m = re.search(
        r"\b(\w+)\s+(din|dino|day|days|dinadinda|dinagalinda|hafte|hafta|week|weeks|mahine|mahina|month|months|tingalinda|saal|year|years)\b",
        c,
    )
    if m:
        num_tok, u_tok = m.group(1), m.group(2)
        if num_tok in CARDINAL_NUMBERS:
            return CARDINAL_NUMBERS[num_tok], unit_map[u_tok]
        if num_tok.isdigit():
            return float(num_tok), unit_map[u_tok]
    return None, None


def parse_frequency(clause: str) -> Optional[str]:
    """Extract dosing frequency code (BID, TID, QD, PRN)."""
    c = clause.lower()
    if re.search(r"\b(?:subah\s+shaam|do\s+baar|twice|bd|bid)\b", c):
        return "BID"
    if re.search(r"\b(?:teen\s+baar|subah\s+dopahar\s+shaam|thrice|tds|tid)\b", c):
        return "TID"
    if re.search(r"\b(?:zaroorat|jab\s+bukhar|jab\s+dard|sos|prn)\b", c):
        return "PRN"
    if re.search(r"\b(?:roz\s+ek|subah\s+khaali\s+pet|raat\s+ko|daily|od|once)\b", c):
        return "QD"
    return None


def parse_laterality(clause: str) -> Optional[str]:
    """Extract anatomical laterality ('baayein' -> left, 'daayein' -> right, 'dono' -> bilateral)."""
    c = clause.lower()
    if re.search(r"\b(?:baayein|left)\b", c):
        return "left"
    if re.search(r"\b(?:daayein|right)\b", c):
        return "right"
    if re.search(r"\b(?:dono|both|bilateral)\b", c):
        return "bilateral"
    return None


def detect_polarity_in_clause(clause: str, concept_match_text: str) -> str:
    """Detect whether a clinical mention inside a local clause is affirmed or negated."""
    c = clause.lower()
    pos = c.find(concept_match_text.lower())
    if pos >= 0:
        before = c[max(0, pos - 24) : pos]
        after = c[pos + len(concept_match_text) : min(len(c), pos + len(concept_match_text) + 38)]
        if PRE_NEGATION_RE.search(before) or POST_NEGATION_RE.search(after):
            return "negated"
        return "affirmed"

    if POST_NEGATION_RE.search(c) or PRE_NEGATION_RE.search(c):
        return "negated"
    return "affirmed"


def detect_subject_in_clause(clause: str) -> str:
    """Determine if symptom/condition applies to patient or family member ('pitaji ko')."""
    if FAMILY_SUBJECT_RE.search(clause) and not PATIENT_SELF_OVERRIDE_RE.search(clause):
        return "family_member"
    return "patient"


def extract_attributes_for_mention(
    raw_or_norm_text: str,
    span_start: int,
    span_end: int,
    matched_phrase: str,
    semantic_tag: str = "finding",
) -> ExtractedAttributes:
    """Extract negation, subject, dose, duration, frequency, and laterality for a concept mention."""
    norm_text = normalize_hinglish_text(raw_or_norm_text)
    clause = find_enclosing_clause(norm_text, span_start, span_end)

    polarity = detect_polarity_in_clause(clause, matched_phrase)
    subject = detect_subject_in_clause(clause)
    dose_val, dose_unit = (None, None)
    strength_mg = None
    freq = None
    if semantic_tag == "medication":
        dose_val, dose_unit = parse_fractional_hindi_number(clause)
        strength_mg = parse_strength_mg(clause)
        freq = parse_frequency(clause)

    dur_val, dur_unit = parse_duration(clause)
    lat = parse_laterality(clause)

    return ExtractedAttributes(
        polarity=polarity,
        subject=subject,
        dose_value=dose_val,
        dose_unit=dose_unit,
        strength_mg=strength_mg,
        frequency_code=freq,
        duration_value=dur_val,
        duration_unit=dur_unit,
        laterality=lat,
        clause_text=clause,
    )
