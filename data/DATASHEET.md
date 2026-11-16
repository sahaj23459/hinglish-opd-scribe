# Datasheet for Dataset: Hinglish-OPD-Scribe Mid-Semester Pilot (`v1.0`)

Following *Datasheets for Datasets* (Gebru et al., 2021) and the healthcare safety boundaries of **Computing for Medicine (Monsoon 2026, Lecture 9)**, this document records the provenance, composition, privacy guarantees, and known limitations of the benchmark in `data/`.

---

## 1. Motivation

* **Purpose:** Evaluate Automatic Speech Recognition (ASR), constrained SNOMED CT clinical concept linking, attribute extraction (Hindi post-positional negation, fractional dosages such as *dedh* = 1.5 and *dhai* = 2.5, duration, laterality, family subject attribution), HL7 FHIR R4 serialization, and **Clinical Severity-Weighted Error Scoring** under realistic Indian Outpatient Department (OPD) code-switching and noise conditions.
* **Creators:** Hinglish OPD Scribe Team — Computing for Medicine (Course Project, Prof. Tavpritesh Sethi).
* **Funding / Compute:** Executed locally on Apple Silicon (`M4`) with `\$0.00` cloud GPU spend; AWS cloud budget capped strictly below `\$20` in `ap-south-1` (Mumbai).

---

## 2. Ethical & Privacy Boundary (`0%` Real Patient PHI)

* **Zero Real Patient Data:** No recordings, clinical notes, or identifiers from real patients or hospital OPDs are included.
* **Synthetic Profiles:** All clinical scenarios are scripted from synthetic outpatient personas spanning three high-burden Indian primary-care domains:
  1. **Acute Febrile Illness, URI & Antimicrobial Stewardship (AMR)** (e.g., viral fever/cough where antibiotics such as Azithromycin or Ciprofloxacin are explicitly counselled against).
  2. **Cardiometabolic Chronic Care** (Type 2 Diabetes Mellitus, Hypertension, Peripheral Neuropathy, fractional tablet titrations).
  3. **Gastrointestinal & Musculoskeletal Primary Care** (colloquial somatic idioms such as *"pet mein gas banti hai"*, *"khatti dakar"*, laterality *"baayein kandhe mein dard"*).
* **Consent & PHI Redaction Pipeline:** Every audio record in `data/manifests/dataset_manifest.json` passes through `src/privacy/consent_and_redaction.py`, logging a SHA-256 audio digest to `data/manifests/consent_audit.jsonl` and stripping Aadhaar, ABHA, phone numbers, UHIDs, PIN codes, and self-introduced names prior to downstream NLP.

---

## 3. Composition & Splits

| Subset | Split Tag | Dialogues / Visits | Audio Files (`16 kHz` Mono WAV) | Description |
| :--- | :--- | :---: | :---: | :--- |
| **Hinglish Dev Split** | `dev` | 8 consults | 8 (`clean`) | Used for lexicon calibration, clause-boundary rules, and prompt tuning. |
| **Hinglish Locked Test Split** | `test` | 16 consults (66 gold clinical items) | 64 (`16 x 4` acoustic conditions) | **Locked held-out evaluation split** tested identically across all ASR models and SNRs (`clean`, `noisy_10db`, `noisy_3db`, `overlap_10db`). |
| **Longitudinal Trajectories** | `longitudinal` | 3 patients x 3 visits (9 encounters) | Text + FHIR bundles | Synthea-style multi-visit trajectories testing `NEW`, `RESOLVED`, `PROGRESSION_ALERT`, and `MEDICATION_CHANGED`. |
| **Kannada Portability Set** | `kannada_portability` | 5 consults | 5 (`clean`) | Verifies zero-core-code-change Karnataka portability by swapping only `kannada_snomed_lexicon.json`. |

**Total Audio Inventory (`v1.0` Pilot):** `77` `.wav` files (`484.1` seconds, `16 kHz` 16-bit PCM mono), deterministically synthesized (`seed = 42`) with neural Indian voices (`hi-IN-SwaraNeural`, `hi-IN-MadhurNeural`, `en-IN-PrabhatNeural`, `en-IN-NeerjaNeural`, `kn-IN-SapnaNeural`, `kn-IN-GaganNeural`) and controlled clinic babble + fan hum + turn-overlap mixing.

---

## 4. Known Limitations & End-Semester Scaling Plan

1. **Synthetic Neural Prosody vs. Spontaneous Human Speech:** Neural TTS voices pronounce drug names and Hindi numerals more consistently than fatigued or elderly OPD patients, though acoustic noise (`+3 dB` clinic babble) and `28%` turn overlap induce realistic ASR degradation and critical negation/dose errors.
2. **Weeks 5–8 Human Role-Play Expansion:** Using the exact manifest schema and consent gate established here, the team is expanding to **100–150 consented human volunteer role-played Hinglish consults** (with 10% clinician-friend realism review) for the final submission.
3. **Clinical Deployment Disclaimer:** Research sandbox benchmark only — **not approved for clinical deployment or autonomous medical advice**.
