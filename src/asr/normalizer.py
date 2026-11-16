"""Script normalization (Devanagari/Kannada/Roman Hinglish) and exact WER/CER alignment."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Dict, List, Tuple


# High-frequency clinical & Hinglish Devanagari word-level overrides (handles schwa deletion & English loanwords)
DEVANAGARI_LEXICAL_MAP: Dict[str, str] = {
    "डॉक्टर": "doctor",
    "डाक्टर": "doctor",
    "साहब": "sahab",
    "जी": "ji",
    "नमस्ते": "namaste",
    "मुझे": "mujhe",
    "मुझको": "mujhe",
    "मेरा": "mera",
    "मेरी": "meri",
    "मेरे": "mere",
    "पिताजी": "pitaji",
    "माताजी": "mataji",
    "मम्मी": "mummy",
    "पापा": "papa",
    "को": "ko",
    "से": "se",
    "में": "mein",
    "मे": "mein",
    "पर": "par",
    "लेकिन": "lekin",
    "और": "aur",
    "या": "ya",
    "तो": "toh",
    "भी": "bhi",
    "अभी": "abhi",
    "अब": "ab",
    "है": "hai",
    "हैं": "hai",
    "था": "tha",
    "थी": "thi",
    "थे": "the",
    "हूँ": "hoon",
    "हूं": "hoon",
    "रहा": "raha",
    "रही": "rahi",
    "रहे": "rahe",
    "रहीहूँ": "rahi hoon",
    "नहीं": "nahi",
    "नही": "nahi",
    "ना": "na",
    "मत": "mat",
    "बिना": "bina",
    "कोई": "koi",
    "बुखार": "bukhar",
    "खांसी": "khansi",
    "खाँसी": "khansi",
    "जुकाम": "zukam",
    "ज़ुकाम": "zukam",
    "सर्दी": "sardi",
    "गले": "gale",
    "गला": "gala",
    "खराश": "kharash",
    "दर्द": "dard",
    "सिर": "sir",
    "सर": "sir",
    "सिरदर्द": "sir dard",
    "चक्कर": "chakkar",
    "उल्टी": "ulti",
    "मतली": "matli",
    "जीमचलाना": "ji machlana",
    "गैस": "gas",
    "पेट": "pet",
    "जलन": "jalan",
    "खट्टी": "khatti",
    "डकार": "dakar",
    "दस्त": "dast",
    "कब्ज": "qabz",
    "कब्ज़": "qabz",
    "सीने": "seene",
    "छाती": "chhati",
    "सांस": "saans",
    "साँस": "saans",
    "फूलना": "phoolna",
    "फूलती": "phoolti",
    "कमजोरी": "kamzori",
    "कमज़ोरी": "kamzori",
    "थकान": "thakan",
    "बदन": "badan",
    "टूट": "toot",
    "जोड़ों": "jodon",
    "घुटने": "ghutne",
    "कंधे": "kandhe",
    "पैर": "paer",
    "पैरों": "paeron",
    "हाथ": "haath",
    "बाएं": "baayein",
    "बायें": "baayein",
    "बाएँ": "baayein",
    "दाएं": "daayein",
    "दायें": "daayein",
    "दाएँ": "daayein",
    "झनझनाहट": "jhanjhanahat",
    "सुन्नपन": "sunnapan",
    "सूजन": "sujan",
    "दाने": "daane",
    "खुजली": "khujli",
    "शुगर": "sugar",
    "बीपी": "bp",
    "दवा": "dawa",
    "दवाई": "dawai",
    "गोली": "goli",
    "गोलियां": "goliyan",
    "गोलियाँ": "goliyan",
    "टैबलेट": "tablet",
    "सुबह": "subah",
    "शाम": "shaam",
    "रात": "raat",
    "खाली": "khaali",
    "खाना": "khana",
    "खाने": "khane",
    "बाद": "baad",
    "पहले": "pehle",
    "एक": "ek",
    "दो": "do",
    "तीन": "teen",
    "चार": "chaar",
    "पांच": "paanch",
    "पाँच": "paanch",
    "छह": "chhah",
    "सात": "saat",
    "आठ": "aath",
    "दस": "das",
    "पंद्रह": "pandrah",
    "आधी": "aadhi",
    "आधा": "aadha",
    "सवा": "sawa",
    "डेढ़": "dedh",
    "डेढ": "dedh",
    "ढाई": "dhai",
    "पौने": "paune",
    "साढ़े": "saadhe",
    "साढे": "saadhe",
    "दिन": "din",
    "दिनों": "dino",
    "हफ्ते": "hafte",
    "हफ़्ते": "hafte",
    "महीने": "mahine",
    "महीना": "mahina",
    "साल": "saal",
    "पैरासिटामोल": "paracetamol",
    "पेरासिटामोल": "paracetamol",
    "मेटफॉर्मिन": "metformin",
    "मेटफार्मिन": "metformin",
    "अम्लोडिपिन": "amlodipine",
    "एम्लोडिपिन": "amlodipine",
    "एज़िथ्रोमाइसिन": "azithromycin",
    "एजिथ्रोमाइसिन": "azithromycin",
    "अमोक्सिसिलिन": "amoxicillin",
    "पैंटोप्राज़ोल": "pantoprazole",
    "पैंटोप्राजोल": "pantoprazole",
    "ओमेप्राज़ोल": "omeprazole",
    "सेट्रिज़िन": "cetirizine",
    "सेट्रीजीन": "cetirizine",
    "ग्लिमेपिराइड": "glimepiride",
    "टेलमीसार्टन": "telmisartan",
    "अटोरवास्टेटिन": "atorvastatin",
    "एंटीबायोटिक": "antibiotic",
    "इंसुलिन": "insulin",
}

KANNADA_LEXICAL_MAP: Dict[str, str] = {
    "ಡಾಕ್ಟರ್": "doctor",
    "ನನಗೆ": "nanage",
    "ಮೂರು": "mooru",
    "ಎರಡು": "eradu",
    "ಒಂದು": "ondu",
    "ದಿನದಿಂದ": "dinadinda",
    "ದಿನಗಳಿಂದ": "dinagalinda",
    "ತಿಂಗಳಿಂದ": "tingalinda",
    "ಜ್ವರ": "jvara",
    "ಕೆಮ್ಮು": "kemmu",
    "ಶೀತ": "sheeta",
    "ತಲೆನೋವು": "talenovu",
    "ನೋವು": "novu",
    "ಹೊಟ್ಟೆ": "hotte",
    "ಉಬ್ಬರ": "ubbara",
    "ಗ್ಯಾಸ್": "gas",
    "ಎದೆ": "ede",
    "ಉರಿ": "uri",
    "ತಲೆಸುತ್ತು": "talesuttu",
    "ವಾಂತಿ": "vaanti",
    "ಭೇದಿ": "bhedi",
    "ಸಕ್ಕರೆ": "sakkare",
    "ಕಾಯಿಲೆ": "kaayile",
    "ಬಿಪಿ": "bp",
    "ಮಾತ್ರೆ": "maatre",
    "ಅರ್ಧ": "ardha",
    "ಒಂದೂವರೆ": "onduvare",
    "ಎರಡೂವರೆ": "eraduvaare",
    "ಇದೆ": "ide",
    "ಇಲ್ಲ": "illa",
    "ಬೇಡ": "beda",
    "ಆದರೆ": "aadare",
    "ಮತ್ತು": "mattu",
    "ಪ್ಯಾರಾಸಿಟಮಾಲ್": "paracetamol",
    "ಮೆಟ್‌ಫಾರ್ಮಿನ್": "metformin",
    "ಮೆಟ್ಫಾರ್ಮಿನ್": "metformin",
    "ಆಂಟಿಬಯೋಟಿಕ್": "antibiotic",
}

# Phonetic spelling canonicalization for Romanized Hinglish variants
ROMAN_SPELLING_CANONICAL: Dict[str, str] = {
    "nahin": "nahi",
    "nahee": "nahi",
    "nhi": "nahi",
    "bukhaar": "bukhar",
    "bukaar": "bukhar",
    "khaansi": "khansi",
    "khasi": "khansi",
    "zukaam": "zukam",
    "jukam": "zukam",
    "jukaam": "zukam",
    "sar": "sir",
    "dawaai": "dawai",
    "dawai": "dawa",
    "davai": "dawa",
    "dava": "dawa",
    "golee": "goli",
    "subha": "subah",
    "sham": "shaam",
    "khali": "khaali",
    "saadey": "saadhe",
    "sadhe": "saadhe",
    "sade": "saadhe",
    "ded": "dedh",
    "derh": "dedh",
    "dhaai": "dhai",
    "pauney": "paune",
    "pone": "paune",
    "savva": "sawa",
    "aadha": "aadhi",
    "adha": "aadhi",
    "adhi": "aadhi",
    "bayein": "baayein",
    "baye": "baayein",
    "baaye": "baayein",
    "dayein": "daayein",
    "daye": "daayein",
    "daaye": "daayein",
    "me": "mein",
    "mai": "mein",
    "main": "mein",
    "hun": "hoon",
    "hu": "hoon",
    "hain": "hai",
    "he": "hai",
    "dr": "doctor",
    "saheb": "sahab",
    "sahib": "sahab",
    "1": "ek",
    "2": "do",
    "3": "teen",
    "4": "chaar",
    "5": "paanch",
    "6": "chhah",
    "7": "saat",
    "8": "aath",
    "10": "das",
    "15": "pandrah",
}

# Basic character-level Devanagari fallback transliteration table
_DEV_CONSONANTS: Dict[str, str] = {
    "क": "k", "ख": "kh", "ग": "g", "घ": "gh", "ङ": "ng",
    "च": "ch", "छ": "chh", "ज": "j", "झ": "jh", "ञ": "ny",
    "ट": "t", "ठ": "th", "ड": "d", "ढ": "dh", "ण": "n",
    "त": "t", "थ": "th", "द": "d", "ध": "dh", "न": "n",
    "प": "p", "फ": "ph", "ब": "b", "भ": "bh", "म": "m",
    "य": "y", "र": "r", "ल": "l", "व": "v",
    "श": "sh", "ष": "sh", "स": "s", "ह": "h",
    "क़": "q", "ख़": "kh", "ग़": "gh", "ज़": "z", "ड़": "d", "ढ़": "dh", "फ़": "f",
}

_DEV_VOWELS_INDEP: Dict[str, str] = {
    "अ": "a", "आ": "aa", "इ": "i", "ई": "ee", "उ": "u", "ऊ": "oo",
    "ए": "e", "ऐ": "ai", "ओ": "o", "औ": "au", "ऋ": "ri",
}

_DEV_MATRAS: Dict[str, str] = {
    "ा": "a", "ि": "i", "ी": "i", "ु": "u", "ू": "oo",
    "े": "e", "ै": "ai", "ो": "o", "ौ": "au", "ृ": "ri",
}

_DEV_DIGITS: Dict[str, str] = {
    "०": "0", "१": "1", "२": "2", "३": "3", "४": "4",
    "५": "5", "६": "6", "७": "7", "८": "8", "९": "9",
}


def transliterate_devanagari_token(token: str) -> str:
    """Transliterate a Devanagari word into approximate Romanized Hinglish."""
    if token in DEVANAGARI_LEXICAL_MAP:
        return DEVANAGARI_LEXICAL_MAP[token]
    if token in KANNADA_LEXICAL_MAP:
        return KANNADA_LEXICAL_MAP[token]

    # Normalize nukta combinations (NFC)
    tok = unicodedata.normalize("NFC", token)
    if tok in DEVANAGARI_LEXICAL_MAP:
        return DEVANAGARI_LEXICAL_MAP[tok]

    if not any("\u0900" <= ch <= "\u097f" for ch in tok):
        return tok

    out: List[str] = []
    n = len(tok)
    i = 0
    while i < n:
        ch = tok[i]
        if ch in _DEV_DIGITS:
            out.append(_DEV_DIGITS[ch])
            i += 1
        elif ch in _DEV_VOWELS_INDEP:
            out.append(_DEV_VOWELS_INDEP[ch])
            i += 1
        elif ch in ("ं", "ँ"):
            out.append("n")
            i += 1
        elif ch == "ः":
            out.append("h")
            i += 1
        elif ch == "्" or ch == "़":
            i += 1
        elif ch in _DEV_CONSONANTS:
            # Check nukta组合 if decomposed
            if i + 1 < n and tok[i + 1] == "़":
                comb = ch + "़"
                base = _DEV_CONSONANTS.get(comb, _DEV_CONSONANTS[ch])
                i += 1
            else:
                base = _DEV_CONSONANTS[ch]
            out.append(base)
            if i + 1 < n:
                nxt = tok[i + 1]
                if nxt == "्":
                    i += 2
                    continue
                if nxt in _DEV_MATRAS:
                    out.append(_DEV_MATRAS[nxt])
                    i += 2
                    continue
                # Inherent schwa except word-final consonant
                out.append("a")
            i += 1
        else:
            out.append(ch)
            i += 1
    return "".join(out)


def normalize_hinglish_text(text: str, canonicalize_spelling: bool = True) -> str:
    """Convert mixed Devanagari/Kannada/Roman Hinglish text into clean lowercase Romanized tokens."""
    if not text:
        return ""
    cleaned = unicodedata.normalize("NFC", text)
    # Strip punctuation including Devanagari danda (।)
    cleaned = re.sub(r"[।॥,.;:!?\"'()\[\]{}<>/\\—–\-]+", " ", cleaned)
    raw_tokens = cleaned.lower().split()
    norm_tokens: List[str] = []
    for tok in raw_tokens:
        rom = transliterate_devanagari_token(tok)
        for sub in rom.split():
            if canonicalize_spelling:
                sub = ROMAN_SPELLING_CANONICAL.get(sub, sub)
            if sub:
                norm_tokens.append(sub)
    return " ".join(norm_tokens)


@dataclass
class ErrorAlignment:
    """Exact edit-distance breakdown per Lecture 9 Slide 9: WER = (S + D + I) / N."""

    substitutions: int
    deletions: int
    insertions: int
    ref_length: int

    @property
    def error_rate(self) -> float:
        if self.ref_length == 0:
            return 0.0 if (self.substitutions + self.deletions + self.insertions) == 0 else 1.0
        return (self.substitutions + self.deletions + self.insertions) / self.ref_length


def _sequence_alignment(ref: List[str], hyp: List[str]) -> ErrorAlignment:
    """Compute minimum edit distance with exact (S, D, I) backtrace."""
    n, m = len(ref), len(hyp)
    # dp[i][j] = (cost, S, D, I)
    dp: List[List[Tuple[int, int, int, int]]] = [
        [(0, 0, 0, 0) for _ in range(m + 1)] for _ in range(n + 1)
    ]
    for i in range(1, n + 1):
        dp[i][0] = (i, 0, i, 0)
    for j in range(1, m + 1):
        dp[0][j] = (j, 0, 0, j)

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if ref[i - 1] == hyp[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                sub = (dp[i - 1][j - 1][0] + 1, dp[i - 1][j - 1][1] + 1, dp[i - 1][j - 1][2], dp[i - 1][j - 1][3])
                dele = (dp[i - 1][j][0] + 1, dp[i - 1][j][1], dp[i - 1][j][2] + 1, dp[i - 1][j][3])
                ins = (dp[i][j - 1][0] + 1, dp[i][j - 1][1], dp[i][j - 1][2], dp[i][j - 1][3] + 1)
                dp[i][j] = min(sub, dele, ins, key=lambda x: x[0])

    _, s, d, ins_c = dp[n][m]
    return ErrorAlignment(substitutions=s, deletions=d, insertions=ins_c, ref_length=n)


def compute_wer(reference: str, hypothesis: str, normalize_script: bool = True) -> ErrorAlignment:
    """Compute Word Error Rate (with optional Indic->Roman Hinglish script canonicalization)."""
    if normalize_script:
        ref_norm = normalize_hinglish_text(reference, canonicalize_spelling=True)
        hyp_norm = normalize_hinglish_text(hypothesis, canonicalize_spelling=True)
    else:
        ref_norm = re.sub(r"[।॥,.;:!?\"'()\[\]\-]+", " ", reference.lower())
        hyp_norm = re.sub(r"[।॥,.;:!?\"'()\[\]\-]+", " ", hypothesis.lower())
    return _sequence_alignment(ref_norm.split(), hyp_norm.split())


def compute_cer(reference: str, hypothesis: str, normalize_script: bool = True) -> ErrorAlignment:
    """Compute Character Error Rate."""
    if normalize_script:
        ref_norm = normalize_hinglish_text(reference, canonicalize_spelling=True).replace(" ", "")
        hyp_norm = normalize_hinglish_text(hypothesis, canonicalize_spelling=True).replace(" ", "")
    else:
        ref_norm = re.sub(r"\s+", "", reference.lower())
        hyp_norm = re.sub(r"\s+", "", hypothesis.lower())
    return _sequence_alignment(list(ref_norm), list(hyp_norm))
