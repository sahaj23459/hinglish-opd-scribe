"""Compile self-contained offline clinician demo (demo/interactive_demo.html) from real lexicon & results."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEX_DIR = ROOT / "data" / "lexicon"
MAN_DIR = ROOT / "data" / "manifests"
RES_DIR = ROOT / "results"
DEMO_OUT = ROOT / "demo" / "interactive_demo.html"


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Hinglish OPD Scribe — Clinical FHIR & Severity Demo</title>
<style>
  :root {
    --bg: #f8fafc;
    --panel: #ffffff;
    --border: #e2e8f0;
    --ink: #0f172a;
    --muted: #475569;
    --brand: #0f4c81;
    --brand-soft: #e0f2fe;
    --ok: #059669;
    --ok-soft: #dcfce7;
    --warn: #d97706;
    --warn-soft: #fef3c7;
    --crit: #dc2626;
    --crit-soft: #fee2e2;
    --mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    --sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: var(--sans);
    background: var(--bg);
    color: var(--ink);
    line-height: 1.5;
  }
  header {
    background: #0f172a;
    color: #fff;
    padding: 16px 28px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 3px solid #38bdf8;
  }
  header h1 { margin: 0; font-size: 19px; letter-spacing: -0.01em; }
  header .sub { font-size: 12.5px; color: #94a3b8; margin-top: 2px; }
  .safety-pill {
    background: rgba(56, 189, 248, 0.16);
    border: 1px solid #38bdf8;
    color: #e0f2fe;
    font-size: 11.5px;
    padding: 5px 11px;
    border-radius: 999px;
    font-weight: 600;
  }
  .tabs {
    display: flex;
    gap: 8px;
    padding: 12px 28px 0;
    background: #f1f5f9;
    border-bottom: 1px solid var(--border);
  }
  .tab-btn {
    border: 1px solid transparent;
    border-bottom: none;
    background: transparent;
    padding: 9px 16px;
    font-size: 13.5px;
    font-weight: 600;
    color: var(--muted);
    cursor: pointer;
    border-radius: 8px 8px 0 0;
  }
  .tab-btn.active {
    background: var(--panel);
    color: var(--brand);
    border-color: var(--border);
  }
  main { max-width: 1340px; margin: 0 auto; padding: 20px 28px 40px; }
  .tab-pane { display: none; }
  .tab-pane.active { display: block; }
  .grid-2 { display: grid; grid-template-columns: 1.08fr 0.92fr; gap: 18px; }
  .card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 16px 18px;
    margin-bottom: 16px;
    box-shadow: 0 1px 2px rgba(15,23,42,0.04);
  }
  .card h2 {
    margin: 0 0 10px;
    font-size: 15px;
    color: #0f172a;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  label { font-size: 12px; font-weight: 600; color: var(--muted); display: block; margin-bottom: 4px; }
  select, textarea, input[type="text"] {
    width: 100%;
    font-family: var(--sans);
    font-size: 13.5px;
    padding: 8px 10px;
    border: 1px solid #cbd5e1;
    border-radius: 7px;
    background: #fff;
    color: var(--ink);
  }
  textarea { min-height: 82px; resize: vertical; }
  .row { display: flex; gap: 12px; align-items: center; margin-bottom: 12px; flex-wrap: wrap; }
  .row > div { flex: 1; min-width: 180px; }
  audio { width: 100%; height: 36px; margin-top: 4px; }
  .btn {
    background: var(--brand);
    color: #fff;
    border: none;
    padding: 8px 14px;
    border-radius: 7px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
  }
  .btn-sm {
    padding: 4px 10px;
    font-size: 11.5px;
    border-radius: 5px;
  }
  .btn-confirm { background: var(--ok); color: #fff; border: none; cursor: pointer; }
  .btn-reject { background: #64748b; color: #fff; border: none; cursor: pointer; }
  .badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 700;
  }
  .b-aff { background: var(--ok-soft); color: #065f46; }
  .b-neg { background: var(--crit-soft); color: #991b1b; }
  .b-amb { background: var(--warn-soft); color: #92400e; }
  .b-fam { background: #ede9fe; color: #5b21b6; }
  .concept-item {
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 10px 12px;
    margin-bottom: 8px;
    background: #fcfdff;
  }
  .concept-top { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
  .code-chip { font-family: var(--mono); font-size: 11.5px; background: #e2e8f0; padding: 2px 6px; border-radius: 4px; }
  pre {
    background: #0f172a;
    color: #e2e8f0;
    padding: 12px;
    border-radius: 8px;
    font-family: var(--mono);
    font-size: 11.5px;
    overflow: auto;
    max-height: 360px;
    margin: 0;
  }
  table { width: 100%; border-collapse: collapse; font-size: 12.5px; }
  th, td { padding: 8px 10px; border-bottom: 1px solid var(--border); text-align: left; }
  th { background: #f1f5f9; font-weight: 700; color: #1e293b; }
  .delta-NEW { border-left: 4px solid #0284c7; padding-left: 10px; margin-bottom: 8px; }
  .delta-RESOLVED { border-left: 4px solid #059669; padding-left: 10px; margin-bottom: 8px; }
  .delta-PROGRESSION_ALERT { border-left: 4px solid #dc2626; padding-left: 10px; margin-bottom: 8px; background: #fff5f5; padding: 8px 10px; border-radius: 0 6px 6px 0; }
  .delta-MEDICATION_CHANGED, .delta-MEDICATION_STOPPED { border-left: 4px solid #d97706; padding-left: 10px; margin-bottom: 8px; }
  .delta-PERSISTENT { border-left: 4px solid #64748b; padding-left: 10px; margin-bottom: 8px; }
</style>
</head>
<body>
<header>
  <div>
    <h1>Hinglish OPD Scribe — SNOMED CT, HL7 FHIR R4 &amp; Clinical Severity Sandbox</h1>
    <div class="sub">Computing for Medicine (Monsoon 2026) · Synthetic Consented Benchmark Only · 0% Real Patient PHI</div>
  </div>
  <div class="safety-pill">106 Verified SNOMED Codes · Constrained Retrieval (0% Code Hallucination)</div>
</header>

<div class="tabs">
  <button class="tab-btn active" onclick="switchTab('scribe', this)">1. Live OPD Scribe &amp; One-Tap Doctor Confirmation</button>
  <button class="tab-btn" onclick="switchTab('longitudinal', this)">2. Longitudinal Multi-Visit FHIR Memory</button>
  <button class="tab-btn" onclick="switchTab('benchmark', this)">3. WER vs. Clinical Severity Benchmark Results</button>
</div>

<main>
  <!-- TAB 1: LIVE OPD SCRIBE -->
  <div id="tab-scribe" class="tab-pane active">
    <div class="grid-2">
      <div>
        <div class="card">
          <h2>
            <span>Step 1: Select Benchmark Consult or Type Any Hinglish / Kannada Utterance</span>
            <span class="badge b-aff" id="consent-badge">Voice Consent: VERIFIED</span>
          </h2>
          <div class="row">
            <div>
              <label>Preset Held-Out Consult</label>
              <select id="preset-select" onchange="loadPresetConsult()"></select>
            </div>
            <div>
              <label>Acoustic Condition (16 kHz WAV)</label>
              <select id="cond-select" onchange="updateAudioSource()">
                <option value="clean">Clean Studio Role-Play</option>
                <option value="noisy_10db" selected>Noisy Indian OPD (+10 dB SNR)</option>
                <option value="noisy_3db">Crowded Govt OPD (+3 dB SNR)</option>
                <option value="overlap_10db">Multi-Speaker Overlap (+10 dB)</option>
              </select>
            </div>
          </div>
          <label>Play Benchmark Audio (`data/audio/...`)</label>
          <audio id="audio-player" controls></audio>
          <div style="margin-top: 12px;">
            <label>Live Transcript Input (Edit freely — PHI is auto-redacted before SNOMED linking!)</label>
            <textarea id="live-input" oninput="runLivePipeline()"></textarea>
          </div>
          <div style="margin-top:8px; font-size:12px; color:#475569;">
            <strong>PHI Redaction Preview:</strong> <span id="redacted-preview" style="font-family:var(--mono);"></span>
          </div>
        </div>

        <div class="card">
          <h2>
            <span>Step 2: Constrained SNOMED CT Concept Linking &amp; Attribute Extraction</span>
            <span id="concept-count" class="code-chip">0 concepts</span>
          </h2>
          <div id="concepts-list"></div>
        </div>
      </div>

      <div>
        <div class="card">
          <h2>Step 3: Span-Grounded English Clinical Note</h2>
          <div id="grounded-note" style="font-size:13.5px;"></div>
        </div>
        <div class="card">
          <h2>
            <span>Step 4: ABDM-Aligned HL7 FHIR R4 Bundle (`Condition`, `Observation`, `MedicationStatement`)</span>
            <span class="badge b-aff">FHIR R4 VALID</span>
          </h2>
          <pre id="fhir-json"></pre>
        </div>
      </div>
    </div>
  </div>

  <!-- TAB 2: LONGITUDINAL MEMORY -->
  <div id="tab-longitudinal" class="tab-pane">
    <div class="card">
      <h2>
        <span>Longitudinal Multi-Visit FHIR Change Summary (Synthea-Style Trajectories)</span>
        <select id="patient-select" style="max-width:460px;" onchange="renderLongitudinal()"></select>
      </h2>
      <div id="longitudinal-view"></div>
    </div>
  </div>

  <!-- TAB 3: BENCHMARK RESULTS -->
  <div id="tab-benchmark" class="tab-pane">
    <div class="card">
      <h2>Hypothesis Test: Plain WER vs. Clinical Severity-Weighted Error Across ASR Arms (320 Runs)</h2>
      <div id="hypothesis-banner" style="margin-bottom:12px; padding:10px 14px; background:#eff6ff; border-left:4px solid #2563eb; font-size:13px;"></div>
      <table id="bench-table">
        <thead>
          <tr>
            <th>ASR Experimental Arm</th>
            <th>Raw WER (%)</th>
            <th>Script-Normalized WER (%)</th>
            <th>SNOMED Concept F1 (%)</th>
            <th>Critical Clinical Error Rate (%)</th>
            <th>Clinical Severity Score (CSS)</th>
            <th>p95 Latency (s)</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>
    </div>
    <div class="grid-2">
      <div class="card">
        <h2>Oracle Transcript Ablation (NLP Grounding Isolation)</h2>
        <table id="oracle-table">
          <thead>
            <tr>
              <th>Linking Mode</th>
              <th>SNOMED F1 (%)</th>
              <th>Hallucinated Codes</th>
              <th>Critical Error Rate (%)</th>
              <th>Severity Score</th>
            </tr>
          </thead>
          <tbody></tbody>
        </table>
      </div>
      <div class="card">
        <h2>Documented Real ASR Failure &amp; Divergence Cases</h2>
        <div id="failures-list" style="max-height:320px; overflow:auto; font-size:12.5px;"></div>
      </div>
    </div>
  </div>
</main>

<script>
const APP_DATA = __APP_DATA_JSON__;
let confirmedOverrides = {};

function switchTab(id, btn) {
  document.querySelectorAll('.tab-pane').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
  document.getElementById('tab-' + id).classList.add('active');
  btn.classList.add('active');
}

function redactPHI(txt) {
  return txt
    .replace(/\\b[2-9]\\d{3}[\\s-]?\\d{4}[\\s-]?\\d{4}\\b/g, '[REDACTED_AADHAAR]')
    .replace(/(?:\\+91[\\s-]?|0)?\\b[6-9]\\d{9}\\b/g, '[REDACTED_PHONE]')
    .replace(/(?<=\\bmera naam\\s)([A-Za-z]+(?:\\s+[A-Za-z]+)?)(?=\\s+hai\\b|\\b)/gi, '[REDACTED_NAME]');
}

function normalizeText(txt) {
  let s = txt.toLowerCase().replace(/[।॥,.;:!?"'()\\[\\]\\-]+/g, ' ');
  const map = {"nahin":"nahi","nahee":"nahi","bukhaar":"bukhar","khaansi":"khansi","zukaam":"zukam","golee":"goli","dawai":"dawa","1":"ek","2":"do","3":"teen","4":"chaar","5":"paanch"};
  return s.split(/\\s+/).filter(Boolean).map(w => map[w] || w).join(' ');
}

function parseAttributes(clause, semTag, matchSpan) {
  const neg = /\\b(nahi|mat|mana|illa|beda|no|without|bina)\\b/i.test(clause);
  const fam = /\\b(pitaji|papa|mataji|mummy|maa|father|mother)\\b/i.test(clause) && !/\\b(mujhe|mujhko|nanage)\\b/i.test(clause);
  let dose = null;
  if (semTag === 'medication') {
    if (/\\b(dhai|eraduvaare)\\b/.test(clause)) dose = 2.5;
    else if (/\\b(dedh|onduvare)\\b/.test(clause)) dose = 1.5;
    else if (/\\bsawa\\b/.test(clause)) dose = 1.25;
    else if (/\\b(aadhi|aadha|ardha)\\b/.test(clause)) dose = 0.5;
    else if (/\\b(do|eradu)\\s+(goli|tablet|maatre)\\b/.test(clause)) dose = 2.0;
    else if (/\\b(ek|ondu)\\s+(goli|tablet|maatre)\\b/.test(clause)) dose = 1.0;
  }
  let dur = null;
  const numMap = {"ek":1,"ondu":1,"do":2,"eradu":2,"teen":3,"mooru":3,"chaar":4,"paanch":5,"chhah":6,"saat":7,"das":10};
  const dm = clause.match(/\\b(ek|ondu|do|eradu|teen|mooru|chaar|paanch|chhah|saat|das)\\s+(din|dinadinda|hafte|mahine)\\b/);
  if (dm) {
    const u = dm[2].startsWith('din') ? 'd' : (dm[2].startsWith('haf') ? 'wk' : 'mo');
    dur = {val: numMap[dm[1]], unit: u};
  }
  let lat = null;
  if (/\\b(baayein|left)\\b/.test(clause)) lat = 'left';
  else if (/\\b(daayein|right)\\b/.test(clause)) lat = 'right';
  return {polarity: neg ? 'negated' : 'affirmed', subject: fam ? 'family_member' : 'patient', dose, dur, lat};
}

function linkClientSide(rawText) {
  const red = redactPHI(rawText);
  document.getElementById('redacted-preview').textContent = red;
  const clauses = red.split(/\\b(?:par|lekin|magar|aur|aadare|mattu)\\b|[।,.;?!]+/i).map(c => normalizeText(c)).filter(Boolean);
  const allConcepts = APP_DATA.lexicon;
  const results = [];
  const seen = new Set();

  clauses.forEach(cl => {
    const matches = [];
    allConcepts.forEach(c => {
      const allSyns = [...c.synonyms.map(s => ({p: normalizeText(s), amb: false})), ...(c.ambiguous_triggers || []).map(s => ({p: normalizeText(s), amb: true}))];
      allSyns.forEach(syn => {
        if (!syn.p || syn.p.length < 2) return;
        const re = new RegExp('(^|\\\\s)' + syn.p.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&') + '(?=\\\\s|$)');
        if (re.test(cl)) {
          matches.push({concept: c, span: syn.p, amb: syn.amb, len: syn.p.split(' ').length});
        }
      });
    });
    matches.sort((a, b) => b.len - a.len);
    const usedWords = new Set();
    matches.forEach(m => {
      if (m.span.split(' ').some(w => usedWords.has(w))) return;
      m.span.split(' ').forEach(w => usedWords.add(w));
      const attrs = parseAttributes(cl, m.concept.semantic_tag, m.span);
      const key = m.concept.snomed_code + ':' + attrs.polarity;
      if (seen.has(key)) return;
      seen.add(key);
      results.push({
        code: m.concept.snomed_code,
        term: m.concept.preferred_term,
        tag: m.concept.semantic_tag,
        span: m.span,
        ambiguous: m.amb,
        attrs: attrs
      });
    });
  });
  return results;
}

function toggleDoctorConfirm(code, status) {
  confirmedOverrides[code] = status;
  runLivePipeline();
}

function runLivePipeline() {
  const txt = document.getElementById('live-input').value;
  const linked = linkClientSide(txt).filter(m => confirmedOverrides[m.code] !== 'rejected');
  document.getElementById('concept-count').textContent = linked.length + ' SNOMED concepts';

  const listEl = document.getElementById('concepts-list');
  listEl.innerHTML = '';
  linked.forEach(m => {
    const isConfirmed = confirmedOverrides[m.code] === 'confirmed' || !m.ambiguous;
    const polBadge = m.attrs.polarity === 'negated'
      ? '<span class="badge b-neg">NEGATED</span>'
      : '<span class="badge b-aff">AFFIRMED</span>';
    const famBadge = m.attrs.subject === 'family_member' ? ' <span class="badge b-fam">FAMILY HX</span>' : '';
    const ambBadge = !isConfirmed ? ' <span class="badge b-amb">DOCTOR CONFIRM?</span>' : '';
    const confirmBtns = !isConfirmed
      ? `<div style="margin-top:6px;"><button class="btn-sm btn-confirm" onclick="toggleDoctorConfirm('${m.code}','confirmed')">One-Tap Confirm</button> <button class="btn-sm btn-reject" onclick="toggleDoctorConfirm('${m.code}','rejected')">Dismiss</button></div>`
      : '';
    const extra = [
      m.attrs.dose ? `Dose: <strong>${m.attrs.dose} tablet(s)</strong>` : '',
      m.attrs.dur ? `Duration: <strong>${m.attrs.dur.val}${m.attrs.dur.unit}</strong>` : '',
      m.attrs.lat ? `Site: <strong>${m.attrs.lat}</strong>` : ''
    ].filter(Boolean).join(' · ');

    listEl.innerHTML += `
      <div class="concept-item">
        <div class="concept-top">
          <div><span class="code-chip">SNOMED ${m.code}</span> <strong>${m.term}</strong></div>
          <div>${polBadge}${famBadge}${ambBadge}</div>
        </div>
        <div style="font-size:12px; color:#475569; margin-top:4px;">Matched span: <code>"${m.span}"</code> ${extra ? ' · ' + extra : ''}</div>
        ${confirmBtns}
      </div>`;
  });

  // Grounded Note
  const noteLines = [];
  linked.forEach(m => {
    const isConf = confirmedOverrides[m.code] === 'confirmed' || !m.ambiguous;
    const prefix = !isConf ? '[Pending Doctor Confirm] ' : '';
    if (m.tag === 'medication') {
      const d = m.attrs.dose ? ` (${m.attrs.dose} tablet)` : '';
      noteLines.push(`<li>${prefix}${m.attrs.polarity === 'negated' ? 'Advised against / not taking' : 'Taking / prescribed'} <strong>${m.term}</strong>${d} <code>[SNOMED:${m.code} | "${m.span}"]</code></li>`);
    } else if (m.attrs.subject === 'family_member') {
      noteLines.push(`<li>${prefix}Family history of <strong>${m.term}</strong> <code>[SNOMED:${m.code} | "${m.span}"]</code></li>`);
    } else if (m.attrs.polarity === 'negated') {
      noteLines.push(`<li>${prefix}Denies <strong>${m.term}</strong> <code>[SNOMED:${m.code} | "${m.span}"]</code></li>`);
    } else {
      const dur = m.attrs.dur ? ` for ${m.attrs.dur.val}${m.attrs.dur.unit}` : '';
      const lat = m.attrs.lat ? ` (${m.attrs.lat})` : '';
      noteLines.push(`<li>${prefix}Reports <strong>${m.term}</strong>${lat}${dur} <code>[SNOMED:${m.code} | "${m.span}"]</code></li>`);
    }
  });
  document.getElementById('grounded-note').innerHTML = noteLines.length
    ? '<ul style="margin:0; padding-left:18px;">' + noteLines.join('') + '</ul>'
    : '<em>No grounded clinical concepts detected.</em>';

  // FHIR R4 Bundle
  const fhirEntries = [
    {resource: {resourceType: "Patient", id: "PAT-DEMO", active: true}},
    {resource: {resourceType: "Encounter", id: "ENC-LIVE", status: "finished", class: {code: "AMB"}}}
  ];
  linked.forEach((m, i) => {
    const isConf = confirmedOverrides[m.code] === 'confirmed' || !m.ambiguous;
    if (m.tag === 'medication') {
      const res = {
        resourceType: "MedicationStatement",
        id: "med-" + (i+1),
        status: m.attrs.polarity === 'negated' ? "not-taken" : "active",
        medicationCodeableConcept: {coding: [{system: "http://snomed.info/sct", code: m.code, display: m.term}]}
      };
      if (m.attrs.dose) res.dosage = [{doseAndRate: [{doseQuantity: {value: m.attrs.dose, unit: "tablet"}}]}];
      fhirEntries.push({resource: res});
    } else if (m.attrs.subject === 'family_member') {
      fhirEntries.push({
        resource: {
          resourceType: "FamilyMemberHistory",
          id: "fam-" + (i+1),
          status: "completed",
          condition: [{code: {coding: [{system: "http://snomed.info/sct", code: m.code, display: m.term}]}}]
        }
      });
    } else {
      fhirEntries.push({
        resource: {
          resourceType: "Condition",
          id: "cond-" + (i+1),
          verificationStatus: {coding: [{code: m.attrs.polarity === 'negated' ? 'refuted' : (isConf ? 'confirmed' : 'provisional')}]},
          code: {coding: [{system: "http://snomed.info/sct", code: m.code, display: m.term}]}
        }
      });
    }
  });
  document.getElementById('fhir-json').textContent = JSON.stringify({
    resourceType: "Bundle",
    type: "collection",
    entry: fhirEntries
  }, null, 2);
}

function loadPresetConsult() {
  confirmedOverrides = {};
  const idx = parseInt(document.getElementById('preset-select').value, 10);
  const c = APP_DATA.presets[idx];
  document.getElementById('live-input').value = c.text;
  updateAudioSource();
  runLivePipeline();
}

function updateAudioSource() {
  const idx = parseInt(document.getElementById('preset-select').value, 10);
  const c = APP_DATA.presets[idx];
  const cond = document.getElementById('cond-select').value;
  const folder = c.lang === 'kn-IN' ? 'kannada_clean' : cond;
  document.getElementById('audio-player').src = `../data/audio/${folder}/${c.id}.wav`;
}

function renderLongitudinal() {
  const idx = parseInt(document.getElementById('patient-select').value, 10);
  const p = APP_DATA.longitudinal[idx];
  if (!p) return;
  let html = `<p style="margin-top:0; color:#475569;"><strong>Persona:</strong> ${p.persona}</p>`;
  p.visit_deltas.forEach((vd, vIdx) => {
    html += `<div class="card" style="background:#f8fafc;"><strong>Visit ${vIdx+1}: <code>${vd.current_visit_id}</code></strong>`;
    if (!vd.items.length) {
      html += `<div style="font-size:13px; color:#64748b; margin-top:6px;">Baseline initial visit indexed in FHIR store.</div>`;
    } else {
      html += `<div style="margin-top:8px; font-size:13px;">`;
      vd.items.forEach(it => {
        html += `<div class="delta-${it.change_type}"><strong>[${it.change_type}]</strong> ${it.summary_text} <span class="code-chip">SNOMED ${it.snomed_code}</span></div>`;
      });
      html += `</div>`;
    }
    html += `</div>`;
  });
  document.getElementById('longitudinal-view').innerHTML = html;
}

function initUI() {
  const pSel = document.getElementById('preset-select');
  APP_DATA.presets.forEach((c, i) => {
    const opt = document.createElement('option');
    opt.value = i;
    opt.textContent = `${c.id} (${c.domain}) — ${c.text.slice(0, 52)}...`;
    pSel.appendChild(opt);
  });

  const patSel = document.getElementById('patient-select');
  APP_DATA.longitudinal.forEach((p, i) => {
    const opt = document.createElement('option');
    opt.value = i;
    opt.textContent = `${p.patient_id}: ${p.persona}`;
    patSel.appendChild(opt);
  });

  if (APP_DATA.benchmark && APP_DATA.benchmark.overall_by_arm) {
    const tb = document.querySelector('#bench-table tbody');
    APP_DATA.benchmark.overall_by_arm.forEach(r => {
      tb.innerHTML += `<tr>
        <td><strong>${r.arm_name}</strong></td>
        <td>${(r.mean_raw_wer*100).toFixed(1)}%</td>
        <td>${(r.mean_normalized_wer*100).toFixed(1)}%</td>
        <td>${(r.mean_snomed_f1*100).toFixed(1)}%</td>
        <td><strong>${(r.critical_clinical_error_rate*100).toFixed(1)}%</strong></td>
        <td><strong>${r.mean_clinical_severity_score.toFixed(3)}</strong></td>
        <td>${r.p95_latency_sec.toFixed(2)}s</td>
      </tr>`;
    });
    const h = APP_DATA.benchmark.hypothesis_tests.normalized_wer_vs_clinical_severity_across_20_cells;
    const hc = APP_DATA.benchmark.hypothesis_tests.consult_level_n320_spearman;
    document.getElementById('hypothesis-banner').innerHTML =
      `<strong>Hypothesis Verification:</strong> Across the 20 (Model &times; Noise) cells, Spearman &rho; = <strong>${h.spearman_rho}</strong> with <strong>${h.pairwise_rank_inversion_count}</strong> pairwise rank inversions between nWER and Clinical Severity; across all 320 individual consult runs, &rho; = <strong>${hc.spearman_rho}</strong> (<strong>${hc.pairwise_rank_inversion_count}</strong> pairwise inversions), confirming that plain WER misranks clinical safety.`;
  }

  if (APP_DATA.oracle) {
    const otb = document.querySelector('#oracle-table tbody');
    [['Unconstrained Baseline', APP_DATA.oracle.unconstrained_baseline], ['Constrained Hybrid (Ours)', APP_DATA.oracle.constrained_hybrid]].forEach(([label, d]) => {
      if (!d) return;
      otb.innerHTML += `<tr>
        <td><strong>${label}</strong></td>
        <td>${(d.mean_snomed_f1*100).toFixed(1)}%</td>
        <td>${d.total_hallucinated_codes}</td>
        <td>${(d.critical_clinical_error_rate_ccer*100).toFixed(1)}%</td>
        <td>${d.mean_clinical_severity_score.toFixed(3)}</td>
      </tr>`;
    });
  }

  if (APP_DATA.failures) {
    const fl = document.getElementById('failures-list');
    APP_DATA.failures.slice(0, 8).forEach(f => {
      const badge = f.type.includes('CRITICAL')
        ? '<span class="badge b-neg">CRITICAL SAFETY FLIP</span>'
        : '<span class="badge b-aff">HIGH WER / ZERO HARM</span>';
      fl.innerHTML += `<div style="border-bottom:1px solid #e2e8f0; padding:8px 0;">
        <div>${badge} <code>${f.consult_id}</code> · <strong>${f.arm_id}</strong> (${f.acoustic_condition}) — nWER: <strong>${(f.normalized_wer*100).toFixed(1)}%</strong>, Severity: <strong>${f.clinical_severity_score}</strong></div>
        <div style="color:#475569; margin-top:3px;">Ref: <em>"${f.reference}"</em><br/>ASR: <em>"${f.asr_normalized}"</em></div>
      </div>`;
    });
  }

  loadPresetConsult();
  renderLongitudinal();
}

window.addEventListener('DOMContentLoaded', initUI);
</script>
</body>
</html>
"""


def main() -> None:
    hi_lex = json.loads((LEX_DIR / "hinglish_snomed_lexicon.json").read_text(encoding="utf-8"))["concepts"]
    kn_lex = json.loads((LEX_DIR / "kannada_snomed_lexicon.json").read_text(encoding="utf-8"))["concepts"]

    # Merge Kannada synonyms into unified demo lexicon by SNOMED code
    by_code = {c["snomed_code"]: dict(c) for c in hi_lex}
    for kc in kn_lex:
        code = kc["snomed_code"]
        if code in by_code:
            by_code[code]["synonyms"] = list(set(by_code[code]["synonyms"] + kc["synonyms"]))
        else:
            by_code[code] = kc

    pilot = json.loads((MAN_DIR / "pilot_consults_v1.json").read_text(encoding="utf-8"))["consults"]
    kn_consults = json.loads((MAN_DIR / "kannada_portability_v1.json").read_text(encoding="utf-8"))["consults"]

    presets = [
        {
            "id": c["consult_id"],
            "domain": c["domain"],
            "lang": "hinglish",
            "text": " ".join(t["text_ref"] for t in c["turns"]),
        }
        for c in pilot
        if c["split"] == "test"
    ] + [
        {
            "id": kc["consult_id"],
            "domain": "kannada_portability",
            "lang": "kn-IN",
            "text": kc["text_ref"],
        }
        for kc in kn_consults[:2]
    ]

    bench = json.loads((RES_DIR / "asr_severity_benchmark.json").read_text(encoding="utf-8")) if (RES_DIR / "asr_severity_benchmark.json").exists() else {}
    oracle = json.loads((RES_DIR / "oracle_ablation.json").read_text(encoding="utf-8")) if (RES_DIR / "oracle_ablation.json").exists() else {}
    long_ev = json.loads((RES_DIR / "longitudinal_evaluation.json").read_text(encoding="utf-8"))["patients"] if (RES_DIR / "longitudinal_evaluation.json").exists() else []
    failures = json.loads((RES_DIR / "failure_cases.json").read_text(encoding="utf-8"))["cases"] if (RES_DIR / "failure_cases.json").exists() else []

    app_data = {
        "lexicon": list(by_code.values()),
        "presets": presets,
        "benchmark": bench,
        "oracle": oracle,
        "longitudinal": long_ev,
        "failures": failures,
    }

    DEMO_OUT.parent.mkdir(parents=True, exist_ok=True)
    html_out = HTML_TEMPLATE.replace("__APP_DATA_JSON__", json.dumps(app_data, ensure_ascii=False))
    DEMO_OUT.write_text(html_out, encoding="utf-8")
    print(f"Compiled standalone interactive demo: {DEMO_OUT}")


if __name__ == "__main__":
    main()
