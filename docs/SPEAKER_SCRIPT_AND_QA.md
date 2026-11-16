# Group 20 — 5-Minute Speaker Script & Q&A Defense Sheet

**Deck:** `Group20_Hinglish_OPD_Scribe_MidSem.pptx` (`9` Main Slides = `4m 55s` + `2` Backup Slides for Q&A)  
**Interactive Demo:** Open `demo/interactive_demo.html` in any browser (zero server setup needed).

---

## 1. Timed Speaker Script (`0:00 – 5:00`)

> **Tip:** Assign **2 speakers** (e.g., Speaker 1: Slides 1–5 in `2m 55s`; Speaker 2: Slides 6–9 in `2m 00s`) so mic handoffs don't eat into your 5-minute limit. All 9 members are credited on Slides 1 & 9 and can answer Q&A for their owned module.

* **Slide 1 — Title (`0:00–0:20`, 20s):**  
  "Good afternoon Professor and TAs. We are Group 20 presenting **Hinglish OPD Scribe**—a reproducible clinical speech experiment that turns noisy Hindi–English consults into SNOMED-coded, longitudinal HL7 FHIR R4 notes, evaluated on **clinical severity** rather than plain Word Error Rate."
* **Slide 2 — Background (`0:20–1:05`, 45s):**  
  "Indian OPDs involve 2–4 minute crowded, 3-party consults full of Hinglish idioms ('gas banti hai') and fractional doses ('dedh goli'). Plain `WER` is clinically blind: dropping 'nahi' in 'sir mein dard nahi hai' gives `7%` `WER` with critical harm; swapping 'dedh' (`1.5`) vs 'dhai' (`2.5`) gives `8%` `WER` with a `67%` overdose; whereas harmless spelling shifts in `OPD-T10` gave `25%` `WER` with **zero** clinical error. Per Lecture 9, we validate natively in Hinglish first while isolating language strings into a plug-and-play Kannada lexicon."
* **Slide 3 — Hypothesis (`1:05–1:45`, 40s):**  
  "Our falsifiable hypothesis `H₁` states that ranking ASR models by Clinical Severity (`CSS`) diverges from plain `WER` (`Spearman ρ < 0.90` with rank inversions), and that Lexicon + TF-IDF Constrained Linking reduces hallucinated SNOMED codes to `0.0%`. `H₀` falsifies this if `ρ ≥ 0.90` or recall `< 70%`. We enforce an identical locked test split, Devanagari-to-Roman normalization (`nWER`), and an Oracle-vs-ASR ablation."
* **Slide 4 — Dataset & Privacy (`1:45–2:25`, 40s):**  
  "We use **zero real patient PHI**. Our `v1.0` benchmark covers `3` OPD domains (`106` verified SNOMED codes) across `77` deterministic `16 kHz` WAVs (`seed=42`: clean, `+10 dB`, `+3 dB` clinic babble, and `28%` turn overlap), guarded by a SHA-256 voice-consent gate and PHI redactor, scaling to `100–150` volunteer human role-plays in Weeks 5–8."
* **Slide 5 — Proposed Pipeline & Prototype (`2:25–3:05`, 40s):**  
  "All 5 stages run today. On `OPD-T01.wav` at `+10 dB` noise (`3.36s` on Apple M4), Whisper hears 'shaam' as 'Shyam'—raising `WER`—yet our pipeline emits a valid 7-resource FHIR R4 bundle with Fever (`3d`), **refuted** Headache, Paracetamol **`1.5` tablets**, and **not-taken** Antibiotic (`CSS = 0.0`), plus multi-visit progression alerts and One-Tap Doctor Confirmation."
* **Slide 6 — Current Progress: 320-Run Benchmark (`3:05–3:50`, 45s):**  
  "Across `320` Faster-Whisper runs, **`H₁` is confirmed**: raw `WER` misranks `Whisper-Tiny` `#2` above `Whisper-Small` `#4` (`ρ = 0.30`) due to script mismatch despite `Tiny` having the worst clinical safety (`CSS = 3.56`). Even with normalized `nWER`, `ρ = 0.808` across `20` model-noise cells (`33` inversions). Clinical lexicon prompting lifts SNOMED `F1` from `55.8%` to **`79.8%`**, and Oracle linking hits **`100%` `F1` with `0` hallucinated codes**."
* **Slide 7 — Failure Analysis & Kannada Check (`3:50–4:15`, 25s):**  
  "Where it fails: Speaker Overlap has *lower* `nWER` (`32.9%`) than `+3 dB` noise (`44.3%`) yet **higher Critical Error Rate (`93.8%` vs `62.5%`)** because turn interruptions wipe out clause-final Hindi 'nahi'. Second, swapping `kannada_snomed_lexicon.json` (`0` code changes) hits `100%` `F1` on Kannada text, but `Whisper-Small` gets `0%` `F1` on Kannada audio—motivating IndicConformer/Parrotlet next."
* **Slide 8 — Feasibility, Cost & W5–8 Plan (`4:15–4:40`, 25s):**  
  "SNOMED CT is covered under India's NRCES license; we spent `\$0.00` cloud compute with `0` unapproved GPUs on local Apple M4; and `150–200` consults on AWS Transcribe in Mumbai (`ap-south-1`) is bounded at `\$7.28–\$19.38`."
* **Slide 9 — Individual Contributions (`4:40–5:00`, 20s):**  
  "Every member of Group 20 owns a distinct, tested module in our repo—from multi-ASR and normalization to SNOMED lexicons, constrained linking, Hindi negation/doses, severity scoring, FHIR R4, longitudinal memory, and privacy/audio ops. Thank you!"

---

## 2. Q&A Quick Answers

1. **Why Hinglish first instead of Kannada?** Native-speaker clinical negation auditing (Lecture 9 Slide 7); core FHIR/severity code is 100% language-agnostic (`100%` Oracle Kannada `F1` with `0` code changes).
2. **ASR error vs. NLP linker error?** See **Backup Slide A1**: Oracle transcripts achieve `100%` SNOMED `F1` and `0` invented codes (`CSS = 0.078`), isolating `>95%` of cascaded errors to acoustic corruption.
3. **Why is Overlap deadlier than +3 dB noise despite lower WER?** Hindi places `'nahi'` / `'mat lijiye'` at the **end** of the clause—right where turn-taking interruptions overlap!
4. **Cloud GPU / Cost compliance?** `0` EC2 GPUs, `0` public endpoints, `\$0.00` midsem spend; AWS Mumbai (`ap-south-1`) capped `< \$20` with auto-delete lifecycle.
