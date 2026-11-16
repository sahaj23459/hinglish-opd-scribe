# Hinglish OPD Scribe: SNOMED-Coded, FHIR-Formatted Clinical Scribe & Severity Benchmark

**Course:** Computing for Medicine (Monsoon Semester 2026) — VoiceScribe Track  
**Experimental Boundary:** 100% Consented Synthetic Role-Play Data (`0%` Real Patient PHI) · Research Sandbox Only (Not for Clinical Deployment)

---

## 1. Overview & Scientific Hypothesis

Standard Automatic Speech Recognition (ASR) benchmarks rank models by **Word Error Rate (`WER`)**, treating every token substitution or deletion equally. In high-volume, code-switched **Hindi–English (Hinglish) Indian OPDs**, dropping a single post-positional negation (*"sir mein dard **nahi** hai"* → *"sir mein dard hai"*) or mishearing a Hindi fractional dosage (*"dedh goli"* = `1.5` vs *"dhai goli"* = `2.5`) incurs a tiny `WER` penalty while creating **critical clinical risk**. Conversely, harmless script switches (Devanagari vs. Romanized Hinglish) or dropped conversational fillers inflate `WER` with zero clinical harm.

### Primary Falsifiable Hypothesis (`H₁`)
> Across candidate ASR models evaluated on a locked held-out Hinglish OPD benchmark spanning clean, noisy (`+10 dB`, `+3 dB` SNR), and overlapping speech, **model rankings under a Clinical Severity-Weighted Error Score (`CSS` / `CCER`) diverge significantly from rankings under plain `WER`**; furthermore, constraining clinical concept linking to a curated **Lexicon + Subword TF-IDF SNOMED CT Retriever** reduces hallucinated/invalid SNOMED codes to **`0.0%`** compared to unconstrained coding.

---

## 2. System Architecture (5 Stages + Longitudinal FHIR Layer)

1. **Privacy, Voice Consent & Hinglish PHI Redaction (`src/privacy/`):** Verifies spoken/signed consent (`consent_audit.jsonl` with SHA-256 audio hashes) and redacts Aadhaar, ABHA, Indian phone numbers, UHIDs, PIN codes, and self-introduced names prior to NLP.
2. **Multi-Model ASR, Script Canonicalization & Acoustic Overlap Analysis (`src/asr/`):** Evaluates Faster-Whisper (`tiny`, `base`, `small`, English-forced vs. multilingual auto vs. Hinglish clinical-lexicon prompted) with Devanagari/Kannada-to-Roman canonicalization (`normalizer.py`), turn/overlap spectral detector (`diarization.py`), and `ap-south-1` budget-guarded AWS Transcribe adapter (`aws_transcribe_adapter.py`).
3. **Constrained SNOMED CT Concept Linking & Attribute Extraction (`src/linking/`):**
   - `106` verified SNOMED CT concepts across **Acute Febrile Illness & AMR**, **Cardiometabolic Care (T2DM/HTN)**, **GI & Musculoskeletal Pain**, and **OPD Medications**, plus a swappable **Kannada Lexicon Plugin (`kannada_snomed_lexicon.json`)** proving zero-core-code-change Karnataka portability.
   - Extracts clause-scoped Hindi/Kannada negation, fractional tablet doses (*aadhi* `0.5`, *sawa* `1.25`, *dedh* `1.5`, *dhai* `2.5`, *saadhe teen* `3.5`), duration, anatomical laterality, and family-member subject attribution (*"pitaji ko"*).
   - Routes low-confidence/ambiguous idioms (*"gas banti hai"*, *"chakkar aana"*) to a **Doctor One-Tap Confirmation Queue**.
4. **Span-Grounded SOAP Note & HL7 FHIR R4 Bundle Serializer (`src/fhir/`):** Emits ABDM-aligned HL7 FHIR R4 `Bundle` (`Patient`, `Encounter`, `Condition`, `Observation`, `MedicationStatement`, `FamilyMemberHistory`) where every clinical claim cites its exact transcript span.
5. **Longitudinal Multi-Visit Memory & Clinical Severity Scorer (`src/fhir/longitudinal_memory.py`, `src/eval/severity_metric.py`):** Tracks `NEW`, `RESOLVED`, `PERSISTENT`, `PROGRESSION_ALERT`, and `MEDICATION_CHANGED` across sequential FHIR visits, and evaluates transcripts by clinical risk (`CRITICAL = 5`, `HIGH = 3`, `LOW = 1`, `IGNORED = 0`).

---

## 3. Reproducible Quickstart

```bash
# 1. Create virtual environment & install pinned dependencies
python3 -m venv --system-site-packages .venv
.venv/bin/pip install -r requirements.txt

# 2. Run automated unit & integration tests (10 tests covering negation, doses, FHIR R4, PHI, severity)
.venv/bin/python -m pytest tests/test_pipeline.py -v

# 3. Rebuild lexicons & consult manifests (deterministic)
.venv/bin/python scripts/build_lexicon_and_manifests.py

# 4. (If regenerating audio/models from scratch) Fetch neural stems, build noisy WAVs & cache ASR models
.venv/bin/python scripts/fetch_tts_stems.py
.venv/bin/python scripts/build_noisy_wavs_and_manifest.py
.venv/bin/python scripts/prefetch_whisper_models.py

# 5. Run full 320-consult ASR + Oracle Ablation + Longitudinal + Kannada Benchmark & generate figures
.venv/bin/python scripts/run_experiments.py
.venv/bin/python scripts/generate_plots_and_report.py
.venv/bin/python scripts/build_interactive_demo_html.py

# 6. Run live single-consult CLI demo on any WAV file
.venv/bin/python scripts/run_single_consult_demo.py --wav data/audio/noisy_10db/OPD-T01.wav
```

Open `demo/interactive_demo.html` in any browser for the **offline interactive Clinician One-Tap Confirmation, FHIR R4 & Longitudinal Visit Explorer**.

---

## 4. Cloud Cost Governance & Academic Integrity Disclosure

* **Cloud Compute Spend (`Mid-Semester`):** `\$0.00` (all `320` ASR consult runs + `5` Kannada runs executed locally on Apple Silicon `M4` in `int8` precision; `0` AWS EC2 GPU instances or public endpoints created).
* **Projected End-Semester AWS Spend (`ap-south-1` Mumbai):** Bounded between `\$7.22` (`150` consults × `2 min`, 1 pass) and `\$19.38` (`200` consults × `2 min`, 2 passes + constrained candidate reranking), enforced via tags and teardown rules in `results/cloud_cost_governance.json`.
* **AI-Assisted Engineering Disclosure (per Lecture 9 Slide 15):** Codebase scaffolding, deterministic DSP augmentation scripts, unit tests, and evaluation harnesses were developed with AI-assisted coding tools (Google Antigravity) and verified against automated `pytest` assertions, HL7 FHIR R4 structural checks, and locked test-split audio evaluations.
