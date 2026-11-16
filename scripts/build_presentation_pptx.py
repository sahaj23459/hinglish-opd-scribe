"""Build Group 20's 5-minute Mid-Semester PowerPoint presentation (.pptx) with speaker notes & geometry audit."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Tuple

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt


ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / "results" / "figures"
OUT_PPTX = ROOT / "Group20_Hinglish_OPD_Scribe_MidSem.pptx"

# Color Palette (Executive Clinical Navy, Cobalt, Emerald Teal, Alert Red)
C_NAVY_DARK = RGBColor(11, 31, 58)      # #0B1F3A (Hero bg)
C_INK = RGBColor(15, 23, 42)            # #0F172A (Primary text)
C_SLATE = RGBColor(71, 85, 105)         # #475569 (Secondary text)
C_MUTED = RGBColor(100, 116, 139)       # #64748B (Footer / captions)
C_BG_LIGHT = RGBColor(248, 250, 252)    # #F8FAFC (Slide canvas)
C_WHITE = RGBColor(255, 255, 255)
C_BORDER = RGBColor(203, 213, 225)      # #CBD5E1
C_ROW_ALT = RGBColor(241, 245, 249)     # #F1F5F9

C_BLUE = RGBColor(29, 78, 216)          # #1D4ED8
C_BLUE_SOFT = RGBColor(219, 234, 254)   # #DBEAFE
C_SKY = RGBColor(56, 189, 248)          # #38BDF8
C_SKY_TEXT = RGBColor(186, 230, 253)    # #BAE6FD

C_TEAL = RGBColor(13, 148, 136)         # #0D9488
C_TEAL_SOFT = RGBColor(204, 251, 241)   # #CCFBF1

C_RED = RGBColor(220, 38, 38)           # #DC2626
C_RED_SOFT = RGBColor(254, 226, 226)    # #FEE2E2

C_AMBER = RGBColor(217, 119, 6)         # #D97706
C_AMBER_SOFT = RGBColor(254, 243, 199)  # #FEF3C7

C_PURPLE = RGBColor(109, 40, 217)       # #6D28D9
C_PURPLE_SOFT = RGBColor(237, 233, 254) # #EDE9FE

FONT_MAIN = "Calibri"
FONT_MONO = "Consolas"


def set_slide_bg(slide, color: RGBColor) -> None:
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_rect(
    slide,
    x: float,
    y: float,
    w: float,
    h: float,
    fill_color: RGBColor,
    border_color: Optional[RGBColor] = None,
    border_pt: float = 1.0,
    rounded: bool = False,
):
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE
    shp = slide.shapes.add_shape(shape_type, Inches(x), Inches(y), Inches(w), Inches(h))
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill_color
    if border_color is not None:
        shp.line.color.rgb = border_color
        shp.line.width = Pt(border_pt)
    else:
        shp.line.fill.background()
    if rounded and hasattr(shp, "adjustments") and len(shp.adjustments) > 0:
        shp.adjustments[0] = 0.04
    return shp


def add_accent_card(
    slide,
    x: float,
    y: float,
    w: float,
    h: float,
    accent_color: RGBColor,
    fill_color: RGBColor = C_WHITE,
    border_color: RGBColor = C_BORDER,
) -> None:
    """Draw a clean Lecture-9-inspired white card with a crisp left vertical color bar."""
    add_rect(slide, x, y, w, h, fill_color=fill_color, border_color=border_color, border_pt=0.9, rounded=False)
    add_rect(slide, x, y, 0.08, h, fill_color=accent_color, border_color=None)


def add_textbox(
    slide,
    x: float,
    y: float,
    w: float,
    h: float,
    paragraphs: List[Tuple[str, float, bool, RGBColor, PP_ALIGN]],
    font_name: str = FONT_MAIN,
    space_after_pt: float = 4.0,
    valign: MSO_ANCHOR = MSO_ANCHOR.TOP,
):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = valign
    tf.margin_left = Inches(0.05)
    tf.margin_right = Inches(0.05)
    tf.margin_top = Inches(0.03)
    tf.margin_bottom = Inches(0.03)

    for idx, (txt, size_pt, is_bold, color, align) in enumerate(paragraphs):
        p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        p.text = txt
        p.alignment = align
        p.space_after = Pt(space_after_pt)
        p.font.name = font_name
        p.font.size = Pt(size_pt)
        p.font.bold = is_bold
        p.font.color.rgb = color
    return tb


def add_header_and_footer(
    slide,
    title: str,
    subtitle: str,
    rubric_badge: str,
    badge_bg: RGBColor,
    badge_fg: RGBColor,
    slide_label: str,
) -> None:
    set_slide_bg(slide, C_BG_LIGHT)
    # Top thin brand bar
    add_rect(slide, 0.0, 0.0, 13.333, 0.09, fill_color=C_BLUE)

    # Title & subtitle (guaranteed single-line title + single-line subtitle)
    add_textbox(
        slide,
        0.55,
        0.16,
        9.02,
        0.90,
        [
            (title, 20.5, True, C_INK, PP_ALIGN.LEFT),
            (subtitle, 11.2, False, C_SLATE, PP_ALIGN.LEFT),
        ],
        space_after_pt=2.0,
    )

    # Top-right rubric pill
    pill = add_rect(slide, 9.68, 0.24, 3.10, 0.38, fill_color=badge_bg, border_color=badge_fg, border_pt=1.0, rounded=True)
    tf = pill.text_frame
    tf.word_wrap = False
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.text = rubric_badge
    p.alignment = PP_ALIGN.CENTER
    p.font.name = FONT_MAIN
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = badge_fg

    # Divider line under header
    add_rect(slide, 0.55, 1.12, 12.23, 0.015, fill_color=C_BORDER)

    # Bottom footer line + metadata
    add_rect(slide, 0.55, 7.06, 12.23, 0.012, fill_color=C_BORDER)
    add_textbox(
        slide,
        0.55,
        7.10,
        8.5,
        0.30,
        [("Group 20 · Hinglish OPD Scribe · Computing for Medicine (Monsoon 2026)", 10.0, False, C_MUTED, PP_ALIGN.LEFT)],
        space_after_pt=0.0,
    )
    add_textbox(
        slide,
        9.50,
        7.10,
        3.28,
        0.30,
        [(slide_label, 10.0, True, C_SLATE, PP_ALIGN.RIGHT)],
        space_after_pt=0.0,
    )


def add_picture_fit(slide, img_path: Path, x: float, y: float, max_w: float, max_h: float) -> None:
    """Insert image centered inside bounding box while strictly preserving aspect ratio."""
    with Image.open(img_path) as im:
        iw, ih = im.size
    aspect = iw / float(ih)
    box_aspect = max_w / float(max_h)
    if aspect >= box_aspect:
        w = max_w
        h = max_w / aspect
    else:
        h = max_h
        w = max_h * aspect
    px = x + (max_w - w) / 2.0
    py = y + (max_h - h) / 2.0
    slide.shapes.add_picture(str(img_path), Inches(px), Inches(py), width=Inches(w), height=Inches(h))


def style_table_cell(
    cell,
    text: str,
    font_size: float = 11.0,
    bold: bool = False,
    fg: RGBColor = C_INK,
    bg: Optional[RGBColor] = None,
    align: PP_ALIGN = PP_ALIGN.LEFT,
    font_name: str = FONT_MAIN,
) -> None:
    if bg is not None:
        cell.fill.solid()
        cell.fill.fore_color.rgb = bg
    cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    cell.margin_left = Inches(0.08)
    cell.margin_right = Inches(0.08)
    cell.margin_top = Inches(0.04)
    cell.margin_bottom = Inches(0.04)
    tf = cell.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.alignment = align
    p.font.name = font_name
    p.font.size = Pt(font_size)
    p.font.bold = bold
    p.font.color.rgb = fg


def set_notes(slide, text: str) -> None:
    notes_slide = slide.notes_slide
    notes_slide.notes_text_frame.text = text


def build_deck() -> Path:
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.500)
    blank = prs.slide_layouts[6]

    # =========================================================================
    # SLIDE 1: HERO TITLE SLIDE (0:00 - 0:20)
    # =========================================================================
    s1 = prs.slides.add_slide(blank)
    set_slide_bg(s1, C_NAVY_DARK)
    add_rect(s1, 0.0, 0.0, 13.333, 0.10, fill_color=C_SKY)

    pill1 = add_rect(s1, 0.65, 0.52, 6.25, 0.38, fill_color=RGBColor(20, 50, 90), border_color=C_SKY, border_pt=1.0, rounded=True)
    style_table_cell(pill1, "COMPUTING FOR MEDICINE (MONSOON 2026)  ·  GROUP 20  ·  VOICESCRIBE TRACK", 10.5, True, C_SKY_TEXT, align=PP_ALIGN.CENTER)

    add_textbox(
        s1,
        0.65,
        1.10,
        12.0,
        1.85,
        [
            ("Hinglish OPD Scribe", 38.0, True, C_WHITE, PP_ALIGN.LEFT),
            (
                "Turning Noisy Hindi–English Consults into SNOMED-Coded, Longitudinal HL7 FHIR R4 Notes —\nEvaluated by Clinical Severity Instead of Plain Word Error Rate",
                16.5,
                False,
                C_SKY_TEXT,
                PP_ALIGN.LEFT,
            ),
        ],
        space_after_pt=10.0,
    )

    # 4 Key Metric Cards
    kpis = [
        ("106 + 14", "Verified SNOMED Codes", "Hinglish + Kannada Plugin", C_SKY),
        ("320 Runs", "77 Multi-Noise WAVs", "Clean, +10dB, +3dB, Overlap", C_TEAL),
        ("0.0%", "Hallucinated Codes", "Constrained Hybrid Linker", RGBColor(52, 211, 153)),
        ("$0 GPU · 0% PHI", "Safe & Bounded Compute", "Synthetic · Local Apple M4", RGBColor(251, 191, 36)),
    ]
    for idx, (big, mid, sub, col) in enumerate(kpis):
        cx = 0.65 + idx * 3.05
        add_rect(s1, cx, 3.18, 2.88, 1.44, fill_color=RGBColor(18, 43, 77), border_color=col, border_pt=1.2, rounded=True)
        add_textbox(
            s1,
            cx + 0.12,
            3.26,
            2.64,
            1.30,
            [
                (big, 20.0, True, col, PP_ALIGN.LEFT),
                (mid, 11.8, True, C_WHITE, PP_ALIGN.LEFT),
                (sub, 10.2, False, RGBColor(148, 163, 184), PP_ALIGN.LEFT),
            ],
            space_after_pt=2.0,
        )

    # Team Roster Panel
    add_rect(s1, 0.65, 4.82, 12.03, 2.22, fill_color=RGBColor(15, 36, 66), border_color=RGBColor(51, 65, 85), border_pt=1.0, rounded=True)
    add_textbox(
        s1,
        0.85,
        4.92,
        11.6,
        0.34,
        [("GROUP 20 TEAM ROSTER (INDIVIDUALLY GRADED WORKSTREAMS)", 11.0, True, C_SKY, PP_ALIGN.LEFT)],
    )
    roster_cols = [
        [
            "1. Shivansh Singh (2023509) · Multi-ASR",
            "2. Tanish Goel (2023546) · Norm & Overlap",
            "3. Dheeraj Arora (2023195) · SNOMED Lexicon",
        ],
        [
            "4. Arnav Gupta (2023125) · Hybrid Linker",
            "5. Adarsh · Negation & Fractional Dose NLP",
            "6. Prakhar · Architecture & Severity Metric",
        ],
        [
            "7. Sahaj Gupta (2023459) · FHIR R4 & Notes",
            "8. Rishita Dhankhar (2023438) · Longitudinal",
            "9. Musaf Khan (2023331) · Audio & Privacy",
        ],
    ]
    for c_i, lines in enumerate(roster_cols):
        add_textbox(
            s1,
            0.85 + c_i * 3.92,
            5.32,
            3.84,
            1.60,
            [(ln, 10.8, False, C_WHITE, PP_ALIGN.LEFT) for ln in lines],
            space_after_pt=5.0,
        )

    set_notes(
        s1,
        "[0:00 - 0:20 | 20s] Good afternoon Professor and TAs. We are Group 20 presenting Hinglish OPD Scribe—an open-source clinical speech experiment that converts noisy Hindi-English OPD consults into SNOMED-coded, longitudinal HL7 FHIR R4 notes, evaluated on clinical risk rather than plain Word Error Rate.",
    )

    # =========================================================================
    # SLIDE 2: BACKGROUND (0:20 - 1:05) -> 10 MARKS
    # =========================================================================
    s2 = prs.slides.add_slide(blank)
    add_header_and_footer(
        s2,
        "Background: Why Indian OPDs Break Plain WER",
        "Noisy Hinglish code-switching + free-text notes create silent clinical safety failures",
        "RUBRIC: BACKGROUND (10 MARKS)",
        C_BLUE_SOFT,
        C_BLUE,
        "Slide 2 / 9",
    )

    bg_cards = [
        (
            "1. Acoustic & Linguistic Reality of Indian OPDs",
            "• 2–4 minute crowded consults with 3-party speech (Doctor, Patient, Attendant) and ambient babble.\n"
            "• Patients speak colloquial Hinglish idioms ('pet mein gas banti hai', 'chakkar aana') and fractional Hindi doses ('dedh goli' = 1.5, 'dhai' = 2.5).",
            C_BLUE,
        ),
        (
            "2. Interoperability Gap (Free Text vs. ABDM HL7 FHIR R4)",
            "• Unstructured notes bury chronic progression across visits.\n"
            "• Mapping consults to SNOMED-coded FHIR R4 (Condition, Observation, MedicationStatement) enables longitudinal tracking without invented codes.",
            C_TEAL,
        ),
        (
            "3. Hinglish First, Karnataka-Ready Architecture",
            "• 'Multilingual is not a translate button' (Lecture 9): auditing clinical negations and idioms requires native-speaker verification.\n"
            "• We validate natively in Hinglish while isolating language strings into a swappable lexicon plugin for Kannada (kn-IN).",
            C_PURPLE,
        ),
    ]
    for idx, (ctitle, cbody, ccol) in enumerate(bg_cards):
        cy = 1.30 + idx * 1.88
        add_accent_card(s2, 0.55, cy, 5.80, 1.72, ccol)
        add_textbox(
            s2,
            0.74,
            cy + 0.10,
            5.50,
            1.52,
            [
                (ctitle, 14.0, True, C_INK, PP_ALIGN.LEFT),
                (cbody, 11.8, False, C_SLATE, PP_ALIGN.LEFT),
            ],
            space_after_pt=4.0,
        )

    # Right side: Why Plain WER Fails in Medicine
    add_accent_card(s2, 6.58, 1.30, 6.20, 5.48, C_RED)
    add_textbox(
        s2,
        6.78,
        1.36,
        5.85,
        0.96,
        [
            ("Why Plain WER Is Clinically Blind", 14.0, True, C_RED, PP_ALIGN.LEFT),
            ("WER = (S + D + I) / N weights a lethal negation drop identically to a filler.", 11.0, False, C_SLATE, PP_ALIGN.LEFT),
        ],
        space_after_pt=2.0,
    )

    tbl_s2 = s2.shapes.add_table(4, 4, Inches(6.78), Inches(2.38), Inches(5.82), Inches(3.12)).table
    col_w2 = [2.15, 0.85, 1.67, 1.15]
    for i, w in enumerate(col_w2):
        tbl_s2.columns[i].width = Inches(w)

    headers2 = ["Hinglish Transcript Edit", "Plain WER", "Clinical Effect", "Risk Tier"]
    for c_i, h in enumerate(headers2):
        style_table_cell(tbl_s2.cell(0, c_i), h, 11.0, True, C_WHITE, C_NAVY_DARK, PP_ALIGN.CENTER if c_i in (1, 3) else PP_ALIGN.LEFT)

    rows2 = [
        ('"sir mein dard [nahi] hai"\n(1 word deleted)', "7.1%", "Flips refuted headache to active condition", "CRITICAL\n(w = 5.0)", C_RED_SOFT, C_RED),
        ('"Metformin dedh → dhai goli"\n(1.5 vs 2.5 tab)', "8.3%", "67% medication overdose recorded in FHIR", "CRITICAL\n(w = 5.0)", C_RED_SOFT, C_RED),
        ('"mahhsus / subahle" (OPD-T10)\n(orthographic/filler)', "25.0%", "All SNOMED codes, negations & doses intact", "IGNORED\n(w = 0.0)", C_TEAL_SOFT, C_TEAL),
    ]
    for r_i, (c0, c1, c2, c3, badge_bg, badge_fg) in enumerate(rows2, start=1):
        row_bg = C_WHITE if r_i % 2 == 1 else C_ROW_ALT
        style_table_cell(tbl_s2.cell(r_i, 0), c0, 10.8, True, C_INK, row_bg)
        style_table_cell(tbl_s2.cell(r_i, 1), c1, 11.5, True, C_INK, row_bg, PP_ALIGN.CENTER)
        style_table_cell(tbl_s2.cell(r_i, 2), c2, 10.8, False, C_SLATE, row_bg)
        style_table_cell(tbl_s2.cell(r_i, 3), c3, 10.5, True, badge_fg, badge_bg, PP_ALIGN.CENTER)

    add_rect(s2, 6.78, 5.66, 5.82, 0.92, fill_color=C_AMBER_SOFT, border_color=C_AMBER, border_pt=1.0, rounded=True)
    add_textbox(
        s2,
        6.92,
        5.74,
        5.55,
        0.76,
        [
            (
                "Key Gap: No open benchmark evaluates Hinglish-to-FHIR scribes using clinical risk weights + SNOMED taxonomic distance under controlled OPD noise and overlap.",
                11.5,
                True,
                RGBColor(146, 64, 14),
                PP_ALIGN.LEFT,
            )
        ],
    )

    set_notes(
        s2,
        "[0:20 - 1:05 | 45s] In Indian OPDs, consults last 2-4 minutes amid crowd noise, 3-party speech, and Hinglish idioms like 'gas banti hai' or 'dedh goli'. Standard WER treats every word equally: dropping 'nahi' gives just 7% WER yet flips a negated symptom to active, whereas harmless spelling variants in OPD-T10 produce 25% WER with zero clinical error. We start in Hinglish so our team can natively audit clinical negations, while keeping the core pipeline 100% plug-and-play for Kannada.",
    )

    # =========================================================================
    # SLIDE 3: FALSIFIABLE HYPOTHESIS (1:05 - 1:45) -> 10 MARKS
    # =========================================================================
    s3 = prs.slides.add_slide(blank)
    add_header_and_footer(
        s3,
        "Falsifiable Hypothesis & Severity Evaluation Design",
        "Explicit H₁ claim, H₀ falsification boundary, and error-isolation experimental controls",
        "RUBRIC: HYPOTHESIS (10 MARKS)",
        C_TEAL_SOFT,
        C_TEAL,
        "Slide 3 / 9",
    )

    # Top Hypothesis Card
    add_accent_card(s3, 0.55, 1.28, 12.23, 1.92, C_BLUE, fill_color=C_WHITE)
    add_textbox(
        s3,
        0.76,
        1.36,
        11.85,
        1.78,
        [
            (
                "Primary Falsifiable Hypothesis (H₁):",
                14.0,
                True,
                C_BLUE,
                PP_ALIGN.LEFT,
            ),
            (
                "Across candidate ASR models evaluated on a locked held-out Hinglish OPD benchmark spanning clean, noisy (+10 dB, +3 dB SNR), and overlapping speech, model rankings under our Clinical Severity Score (CSS / CCER) diverge significantly from plain WER (Spearman ρ < 0.90 with pairwise rank inversions); furthermore, constraining concept linking to Lexicon + Subword TF-IDF SNOMED Retrieval reduces hallucinated SNOMED codes to 0.0% vs. unconstrained coding.",
                12.0,
                False,
                C_INK,
                PP_ALIGN.LEFT,
            ),
            (
                "Null / Falsification Criterion (H₀):  Falsified if WER and CSS preserve rank order (Spearman ρ ≥ 0.90 across model-noise cells) OR if lexicon-constrained retrieval drops SNOMED concept recall below 70%.",
                11.5,
                True,
                C_RED,
                PP_ALIGN.LEFT,
            ),
        ],
        space_after_pt=4.0,
    )

    # Bottom Left: Severity Rubric Table
    add_textbox(s3, 0.55, 3.34, 6.35, 0.34, [("Clinical Severity Metric (CSS) — Risk Weights", 14.0, True, C_INK, PP_ALIGN.LEFT)])
    tbl_s3 = s3.shapes.add_table(5, 3, Inches(0.55), Inches(3.70), Inches(6.35), Inches(3.12)).table
    for i, w in enumerate([1.35, 2.35, 2.65]):
        tbl_s3.columns[i].width = Inches(w)
    for c_i, h in enumerate(["Severity (Wt)", "Error Category", "Hinglish OPD Example"]):
        style_table_cell(tbl_s3.cell(0, c_i), h, 11.0, True, C_WHITE, C_NAVY_DARK)

    sev_rows = [
        ("CRITICAL (5.0)", "Negation / Dose / Subject flip", '"dard nahi"→"dard"; dedh(1.5) vs dhai(2.5); pitaji→patient', C_RED_SOFT, C_RED),
        ("HIGH (3.0)", "Time / Laterality / Far SNOMED", '"3 din" vs "3 mahine"; left vs right; invented code', C_AMBER_SOFT, C_AMBER),
        ("LOW (1.0)", "SNOMED sibling substitution", "Near-neighbour in same sub-branch (dist ≤ 2)", C_BLUE_SOFT, C_BLUE),
        ("IGNORED (0.0)", "Filler / Script / Orthography", '"doctor sahab", Devanagari vs Roman spelling', C_ROW_ALT, C_SLATE),
    ]
    for r_i, (s_lbl, cat, ex, s_bg, s_fg) in enumerate(sev_rows, start=1):
        rbg = C_WHITE if r_i % 2 == 1 else C_ROW_ALT
        style_table_cell(tbl_s3.cell(r_i, 0), s_lbl, 10.5, True, s_fg, s_bg, PP_ALIGN.CENTER)
        style_table_cell(tbl_s3.cell(r_i, 1), cat, 10.8, True, C_INK, rbg)
        style_table_cell(tbl_s3.cell(r_i, 2), ex, 10.5, False, C_SLATE, rbg)

    # Bottom Right: Experimental Controls
    add_accent_card(s3, 7.12, 3.38, 5.66, 3.44, C_TEAL)
    add_textbox(
        s3,
        7.32,
        3.48,
        5.32,
        3.24,
        [
            ("Three Scientific Controls Built Into Benchmark", 14.5, True, C_TEAL, PP_ALIGN.LEFT),
            (
                "1. Identical Locked Held-Out Test Split:\n"
                "All 5 ASR arms × 4 acoustic conditions (320 runs) are evaluated on the exact same 16 held-out consults (66 gold clinical items) — never across mismatched splits.",
                11.5,
                False,
                C_INK,
                PP_ALIGN.LEFT,
            ),
            (
                "2. Script Canonicalization (Raw WER vs. nWER):\n"
                "Devanagari/Kannada→Roman Hinglish normalizer isolates script-switching artifacts from true phonetic/lexical recognition failures.",
                11.5,
                False,
                C_INK,
                PP_ALIGN.LEFT,
            ),
            (
                "3. Oracle Transcript vs. Noisy ASR Ablation:\n"
                "Running SNOMED linking on Gold Transcripts (Oracle) vs. ASR outputs cleanly separates NLP linking accuracy from acoustic errors.",
                11.5,
                False,
                C_INK,
                PP_ALIGN.LEFT,
            ),
        ],
        space_after_pt=6.0,
    )

    set_notes(
        s3,
        "[1:05 - 1:45 | 40s] Our falsifiable hypothesis H1 states that ranking ASR models by Clinical Severity Score diverges from plain WER with Spearman rho below 0.90, and that retrieval-constrained SNOMED linking eliminates code hallucinations. H0 falsifies our claim if rho >= 0.90 or if recall drops below 70%. We enforce three strict controls: a locked test split, Devanagari-to-Roman script normalization, and an Oracle-vs-ASR ablation.",
    )

    # =========================================================================
    # SLIDE 4: DATASET, ACOUSTIC AUGMENTATION & PRIVACY (1:45 - 2:25) -> 10 MARKS
    # =========================================================================
    s4 = prs.slides.add_slide(blank)
    add_header_and_footer(
        s4,
        "Dataset: Synthetic OPD Benchmark & Privacy Gate",
        "0% real patient PHI · 3 OPD domains · 106 verified SNOMED codes · controlled SNR & overlap",
        "RUBRIC: DATASET (10 MARKS)",
        C_PURPLE_SOFT,
        C_PURPLE,
        "Slide 4 / 9",
    )

    domains = [
        (
            "Domain 1: Acute Febrile & AMR",
            "• Viral fever/URI, chills, dengue checks\n• Explicit antibiotic stewardship ('viral mein antibiotic / Azithromycin mat lijiye')",
            C_BLUE,
        ),
        (
            "Domain 2: Cardiometabolic Care",
            "• Type 2 Diabetes, HTN, neuropathy\n• Hindi fractional tablet doses (aadhi 0.5, sawa 1.25, dedh 1.5, dhai 2.5)",
            C_TEAL,
        ),
        (
            "Domain 3: GI & Musculoskeletal",
            "• Colloquial idioms ('gas banti hai', 'khatti dakar')\n• Laterality (baayein/daayein) & family history ('pitaji ko')",
            C_PURPLE,
        ),
    ]
    for idx, (dtitle, dbody, dcol) in enumerate(domains):
        dx = 0.55 + idx * 4.14
        add_accent_card(s4, dx, 1.28, 3.95, 1.62, dcol)
        add_textbox(
            s4,
            dx + 0.18,
            1.36,
            3.65,
            1.44,
            [
                (dtitle, 13.5, True, C_INK, PP_ALIGN.LEFT),
                (dbody, 11.3, False, C_SLATE, PP_ALIGN.LEFT),
            ],
            space_after_pt=4.0,
        )

    # Dataset Split Table
    add_textbox(s4, 0.55, 3.06, 6.30, 0.34, [("Pilot Dataset v1.0 Inventory (77 WAVs, 16 kHz, seed=42)", 14.0, True, C_INK, PP_ALIGN.LEFT)])
    tbl_s4 = s4.shapes.add_table(5, 4, Inches(0.55), Inches(3.42), Inches(6.30), Inches(3.38)).table
    for i, w in enumerate([1.65, 1.15, 1.25, 2.25]):
        tbl_s4.columns[i].width = Inches(w)
    for c_i, h in enumerate(["Split", "Consults", "Audio WAVs", "Acoustic / Clinical Purpose"]):
        style_table_cell(tbl_s4.cell(0, c_i), h, 10.8, True, C_WHITE, C_NAVY_DARK)

    d_rows = [
        ("Dev Calibration", "8", "8 (Clean)", "Clause negation & lexicon tuning"),
        ("Locked Held-Out Test", "16 (66 items)", "64 (16 × 4)", "Clean, +10 dB, +3 dB crowd & 28% overlap"),
        ("Longitudinal Memory", "3 × 3 visits", "9 FHIR visits", "Synthea-style progression & dose changes"),
        ("Kannada Portability", "5 (kn-IN)", "5 (Clean)", "Zero-code-change lexicon swap check"),
    ]
    for r_i, (c0, c1, c2, c3) in enumerate(d_rows, start=1):
        rbg = C_WHITE if r_i % 2 == 1 else C_ROW_ALT
        style_table_cell(tbl_s4.cell(r_i, 0), c0, 10.8, True, C_INK, rbg)
        style_table_cell(tbl_s4.cell(r_i, 1), c1, 10.8, False, C_INK, rbg, PP_ALIGN.CENTER)
        style_table_cell(tbl_s4.cell(r_i, 2), c2, 10.8, True, C_BLUE, rbg, PP_ALIGN.CENTER)
        style_table_cell(tbl_s4.cell(r_i, 3), c3, 10.5, False, C_SLATE, rbg)

    # Privacy & Acoustic Engineering Box
    add_accent_card(s4, 7.05, 3.08, 5.73, 3.72, C_AMBER)
    add_textbox(
        s4,
        7.25,
        3.18,
        5.38,
        3.50,
        [
            ("Privacy Safeguards & Controlled OPD Acoustics", 14.5, True, C_INK, PP_ALIGN.LEFT),
            (
                "• Strict Safe Boundary (0% Real PHI): 100% synthetic patient personas documented via formal Gebru Datasheet (data/DATASHEET.md) + SHA-256 manifest.",
                11.5,
                False,
                C_SLATE,
                PP_ALIGN.LEFT,
            ),
            (
                "• Consent Gate & PHI Redactor (src/privacy/): Spoken consent verifier + append-only audit log + regex/context scrubber for Aadhaar, ABHA, phone, UHID, and names.",
                11.5,
                False,
                C_SLATE,
                PP_ALIGN.LEFT,
            ),
            (
                "• Controlled OPD Noise & Overlap Synthesis: Neural Indian voices (hi-IN / en-IN / kn-IN) mixed deterministically with waiting-room babble + ceiling-fan hum (+10 dB, +3 dB) and exact overlap timestamps.",
                11.5,
                False,
                C_SLATE,
                PP_ALIGN.LEFT,
            ),
            (
                "• Weeks 5–8 Scaling: Expanding to 100–150 consented human volunteer role-played consults (10% doctor-friend reviewed).",
                11.5,
                True,
                C_BLUE,
                PP_ALIGN.LEFT,
            ),
        ],
        space_after_pt=5.0,
    )

    set_notes(
        s4,
        "[1:45 - 2:25 | 40s] We use zero real patient data. We locked three clinical domains—Acute Fever/AMR, Cardiometabolic chronic care, and GI/Musculoskeletal pain—covering 106 verified SNOMED codes. Our pilot dataset contains 77 16kHz WAVs across clean, +10dB, +3dB clinic babble, and 28% speaker overlap, guarded by a SHA-256 voice-consent gate and Hinglish PHI redactor, scaling to 100+ human volunteer recordings next.",
    )

    # =========================================================================
    # SLIDE 5: PROPOSED APPROACH & WORKING PROTOTYPE (2:25 - 3:05)
    # =========================================================================
    s5 = prs.slides.add_slide(blank)
    add_header_and_footer(
        s5,
        "Proposed Approach: 5-Stage Pipeline & Prototype",
        "Zero-hallucination SNOMED retrieval, clause-scoped Hindi modifiers, FHIR R4 & longitudinal deltas",
        "PROPOSED APPROACH & PROTOTYPE",
        C_BLUE_SOFT,
        C_BLUE,
        "Slide 5 / 9",
    )

    stages = [
        ("Stage 1: ASR & Norm", "Faster-Whisper / AWS\n+ Devanagari→Roman\n+ Overlap Detector", C_BLUE),
        ("Stage 2: SNOMED Link", "Lexicon + Char TF-IDF\nConstrained Selection\n(0% Invented Codes)", C_TEAL),
        ("Stage 3: Modifiers", "Clause Negation ('nahi')\nFractional Dose ('dedh')\nLaterality & Family Hx", C_PURPLE),
        ("Stage 4: Safe Note", "Span-Cited English Note\n+ Doctor One-Tap\nConfirmation Queue", C_AMBER),
        ("Stage 5: FHIR + Memory", "Valid HL7 FHIR R4\n+ Longitudinal Multi-\nVisit Delta Summary", RGBColor(5, 150, 105)),
    ]
    for idx, (st_title, st_desc, st_col) in enumerate(stages):
        sx = 0.55 + idx * 2.48
        add_rect(s5, sx, 1.30, 2.30, 1.50, fill_color=C_WHITE, border_color=st_col, border_pt=1.5, rounded=True)
        add_rect(s5, sx, 1.30, 2.30, 0.34, fill_color=st_col, rounded=False)
        add_textbox(s5, sx + 0.06, 1.32, 2.18, 0.30, [(st_title, 11.2, True, C_WHITE, PP_ALIGN.CENTER)], space_after_pt=0.0)
        add_textbox(s5, sx + 0.08, 1.70, 2.14, 1.05, [(st_desc, 10.5, False, C_INK, PP_ALIGN.CENTER)], space_after_pt=2.0)
        if idx < 4:
            arr = s5.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(sx + 2.32), Inches(1.92), Inches(0.14), Inches(0.24))
            arr.fill.solid()
            arr.fill.fore_color.rgb = C_SLATE
            arr.line.fill.background()

    # Left: Real Execution Trace (OPD-T01 @ +10 dB)
    add_accent_card(s5, 0.55, 3.02, 6.08, 3.82, C_BLUE)
    add_textbox(
        s5,
        0.74,
        3.08,
        5.75,
        1.14,
        [
            ("Live Trace: OPD-T01.wav (+10 dB Noise · 3.36s on M4)", 13.2, True, C_BLUE, PP_ALIGN.LEFT),
            (
                'ASR: "Doctor sahab, mujhe teen din se bukhar hai, par sir mein dard nahi hai, Paracetamol dedh goli, Subah, Shyam lijiye, Viral mein antibiotic mat lijiye."',
                10.4,
                False,
                C_SLATE,
                PP_ALIGN.LEFT,
            ),
        ],
        space_after_pt=2.0,
    )
    add_rect(s5, 0.74, 4.26, 5.70, 2.44, fill_color=C_NAVY_DARK, rounded=True)
    add_textbox(
        s5,
        0.86,
        4.32,
        5.48,
        2.32,
        [
            ("Emitted Valid FHIR R4 Bundle (7 Resources, CSS = 0.00):", 10.6, True, C_SKY, PP_ALIGN.LEFT),
            ("• Condition [386661006] Fever       | confirmed | dur: 3.0 d", 9.8, False, C_WHITE, PP_ALIGN.LEFT),
            ("• Condition [25064002]  Headache    | REFUTED   | 'sir mein dard'", 9.8, False, RGBColor(252, 165, 165), PP_ALIGN.LEFT),
            ("• MedStmt   [387517004] Paracetamol | active    | dose: 1.5 tab", 9.8, False, RGBColor(134, 239, 172), PP_ALIGN.LEFT),
            ("• MedStmt   [255631004] Antibiotic  | NOT-TAKEN | AMR kept", 9.8, False, RGBColor(253, 224, 71), PP_ALIGN.LEFT),
            ("  Homophone 'Shyam' raises WER, yet Clinical Severity = 0.0!", 9.8, True, C_SKY_TEXT, PP_ALIGN.LEFT),
        ],
        font_name=FONT_MONO,
        space_after_pt=3.5,
    )

    # Right: Longitudinal Memory & Clinician UI
    add_accent_card(s5, 6.82, 3.02, 5.96, 3.82, C_TEAL)
    add_textbox(
        s5,
        7.02,
        3.12,
        5.62,
        3.62,
        [
            ("Longitudinal FHIR Memory & Clinician Safety Controls", 13.8, True, C_TEAL, PP_ALIGN.LEFT),
            (
                "• Verified Multi-Visit Trajectory (SYN-PAT-001, Visits 1 → 2 → 3):\n"
                "  – [RESOLVED] Polyuria (28442001) negated in V2 (active in V1)\n"
                "  – [PROGRESSION_ALERT] New Peripheral Neuropathy (302226006) linked to prior T2DM history\n"
                "  – [MEDICATION_CHANGED] Metformin titrated 1.0 → 1.5 → 2.0 tab",
                11.2,
                False,
                C_INK,
                PP_ALIGN.LEFT,
            ),
            (
                "• One-Tap Clinician Confirmation Queue:\n"
                "  Ambiguous idioms ('chakkar aana', 'gas banti hai') emit FHIR verificationStatus='provisional' until doctor taps Confirm.",
                11.2,
                False,
                C_INK,
                PP_ALIGN.LEFT,
            ),
            (
                "• Runnable Today: Standalone Clinician UI (demo/interactive_demo.html) + CLI (scripts/run_single_consult_demo.py) + 10/10 passing pytest tests.",
                11.2,
                True,
                C_BLUE,
                PP_ALIGN.LEFT,
            ),
        ],
        space_after_pt=6.0,
    )

    set_notes(
        s5,
        "[2:25 - 3:05 | 40s] Our working 5-stage prototype is fully runnable today. On OPD-T01 at +10dB noise, Whisper transcribes 'shaam' as 'Shyam'—incurring a WER penalty—yet our pipeline extracts Fever for 3 days, refuted Headache, Paracetamol 1.5 tablets, and not-taken Antibiotic into a valid 7-resource FHIR R4 bundle with zero clinical errors, plus multi-visit progression alerts across sequential visits.",
    )

    # =========================================================================
    # SLIDE 6: CURRENT PROGRESS & 320-RUN BENCHMARK RESULTS (3:05 - 3:50)
    # =========================================================================
    s6 = prs.slides.add_slide(blank)
    add_header_and_footer(
        s6,
        "Current Progress: 320-Run Benchmark Confirms H₁",
        "Plain WER misranks clinical safety (ρ = 0.30 raw; ρ = 0.808 normalized, 33 cell inversions)",
        "CURRENT PROGRESS & RESULTS",
        C_TEAL_SOFT,
        C_TEAL,
        "Slide 6 / 9",
    )

    add_rect(s6, 0.55, 1.28, 6.75, 5.52, fill_color=C_WHITE, border_color=C_BORDER, border_pt=1.0, rounded=True)
    add_picture_fit(s6, FIG_DIR / "fig1_wer_vs_critical_clinical_error.png", 0.65, 1.38, 6.55, 4.15)
    add_textbox(
        s6,
        0.72,
        5.60,
        6.42,
        1.12,
        [
            (
                "Rank Inversion Proof: Raw WER ranks Whisper-Tiny (93.0%, #2) ahead of Whisper-Small Unprompted (102.9%, #4) solely due to Devanagari script output—yet Whisper-Tiny has the WORST Clinical Severity Score (3.555, #5). Across all 320 consult runs, Spearman ρ = 0.612 (12,440 pairwise consult inversions).",
                10.8,
                True,
                C_INK,
                PP_ALIGN.LEFT,
            )
        ],
    )

    # Right summary table + Oracle result
    tbl_s6 = s6.shapes.add_table(6, 5, Inches(7.48), Inches(1.28), Inches(5.30), Inches(3.32)).table
    for i, w in enumerate([1.82, 0.85, 0.88, 0.88, 0.87]):
        tbl_s6.columns[i].width = Inches(w)
    for c_i, h in enumerate(["ASR Arm (64 runs ea.)", "nWER", "SNOMED F1", "CSS ↓", "p95 (s)"]):
        style_table_cell(tbl_s6.cell(0, c_i), h, 10.2, True, C_WHITE, C_NAVY_DARK, PP_ALIGN.CENTER if c_i > 0 else PP_ALIGN.LEFT)

    b_rows = [
        ("Whisper-Tiny (Auto)", "87.3%", "30.8%", "3.56", "10.0s", False),
        ("Whisper-Base (EN)", "114.7%", "19.0%", "3.51", "7.8s", False),
        ("Whisper-Base (Auto)", "95.9%", "21.5%", "3.51", "17.0s", False),
        ("Whisper-Small (Auto)", "50.0%", "55.8%", "2.99", "20.3s", False),
        ("Small + Hinglish Lex", "32.3%", "79.8%", "1.68", "16.5s*", True),
    ]
    for r_i, (m_n, nw, f1s, css, p95, hi) in enumerate(b_rows, start=1):
        rbg = C_TEAL_SOFT if hi else (C_WHITE if r_i % 2 == 1 else C_ROW_ALT)
        fg = C_TEAL if hi else C_INK
        style_table_cell(tbl_s6.cell(r_i, 0), m_n, 10.0, hi, fg, rbg)
        style_table_cell(tbl_s6.cell(r_i, 1), nw, 10.2, hi, C_INK, rbg, PP_ALIGN.CENTER)
        style_table_cell(tbl_s6.cell(r_i, 2), f1s, 10.2, True, fg, rbg, PP_ALIGN.CENTER)
        style_table_cell(tbl_s6.cell(r_i, 3), css, 10.2, True, C_RED if not hi else C_TEAL, rbg, PP_ALIGN.CENTER)
        style_table_cell(tbl_s6.cell(r_i, 4), p95, 10.0, False, C_SLATE, rbg, PP_ALIGN.CENTER)

    add_accent_card(s6, 7.48, 4.76, 5.30, 2.04, C_BLUE)
    add_textbox(
        s6,
        7.66,
        4.85,
        5.00,
        1.88,
        [
            ("Key Takeaways & Oracle Ablation", 13.5, True, C_BLUE, PP_ALIGN.LEFT),
            ("• Clinical Lexicon Prompting jumps SNOMED F1 from 55.8% → 79.8% (85.7% clean) and cuts CSS from 2.99 → 1.68 (*p95 = 4.8s at +10 dB).", 10.8, False, C_INK, PP_ALIGN.LEFT),
            ("• Oracle Transcript Ablation: Constrained linker hits 100.0% SNOMED F1 with 0 hallucinated codes (vs. 25% consult hallucination & 87.5% CCER in unconstrained baseline).", 10.8, False, C_INK, PP_ALIGN.LEFT),
        ],
        space_after_pt=4.0,
    )

    set_notes(
        s6,
        "[3:05 - 3:50 | 45s] We executed 320 real Faster-Whisper runs on Apple M4. First, H1 is confirmed: raw WER ranks Whisper-Tiny #2 above Whisper-Small #4 due to script mismatch, even though Tiny has the worst Clinical Severity Score at 3.56. Even with normalized WER, rho is 0.808 across the 20 model-noise cells with 33 rank inversions. Second, conditioning Whisper-Small with our Hinglish clinical lexicon raises SNOMED F1 to 79.8%, while our constrained linker achieves 100% F1 and zero hallucinated codes on Oracle transcripts.",
    )

    # =========================================================================
    # SLIDE 7: FAILURE CASES & KANNADA PORTABILITY (3:50 - 4:15)
    # =========================================================================
    s7 = prs.slides.add_slide(blank)
    add_header_and_footer(
        s7,
        "Where It Fails: Error Modes & Kannada Check",
        "Reporting negative results transparently (Lecture 9 Slides 11, 15 & 17)",
        "FAILURE ANALYSIS & FAIRNESS",
        C_RED_SOFT,
        C_RED,
        "Slide 7 / 9",
    )

    add_rect(s7, 0.55, 1.28, 6.45, 5.52, fill_color=C_WHITE, border_color=C_BORDER, border_pt=1.0, rounded=True)
    add_picture_fit(s7, FIG_DIR / "fig2_acoustic_noise_and_overlap_ablation.png", 0.63, 1.38, 6.28, 4.10)
    add_textbox(
        s7,
        0.72,
        5.56,
        6.12,
        1.15,
        [
            (
                "Overlap vs. Crowd Noise Inversion: On Whisper-Small (+Clinical), Speaker Overlap has LOWER nWER (32.9%) than +3 dB Crowd Noise (44.3%), yet HIGHER Critical Error Rate (93.8% vs. 62.5%) because turn interruptions selectively corrupt clause-final negations ('nahi' / 'mat lijiye')!",
                10.6,
                True,
                C_RED,
                PP_ALIGN.LEFT,
            )
        ],
    )

    fail_cards = [
        (
            "Failure 1 — Overlap Negation Flip (OPD-T01, CSS = 4.50)",
            'Ref: "...par sir mein dard nahi hai..." → ASR: "...पर सिर में दरने रहा है..."\nDoctor turn overlap destroys "dard nahi hai", flipping Headache from refuted to confirmed.',
            C_RED,
        ),
        (
            "Failure 2 — Phonetic Drug Splitting in Unprompted ASR",
            'Unprompted Whisper splits English drugs into Devanagari syllables ("आजत्रमाइसन" for Azithromycin, "आन्टो प्रजोल" for Pantoprazole) — nWER = 27%, critical drug missed.',
            C_AMBER,
        ),
        (
            "Failure 3 — Kannada Portability Test (KN-OPD-01..05)",
            "Swapping ONLY kannada_snomed_lexicon.json (0 code changes) gives 100% SNOMED F1 on Oracle Kannada text, but Whisper-Small collapses on Kannada audio (0% F1) — proving need for IndicConformer/Parrotlet + native reviewers.",
            C_PURPLE,
        ),
    ]
    for idx, (ftitle, fbody, fcol) in enumerate(fail_cards):
        fy = 1.28 + idx * 1.88
        add_accent_card(s7, 7.18, fy, 5.60, 1.74, fcol)
        add_textbox(
            s7,
            7.36,
            fy + 0.08,
            5.30,
            1.58,
            [
                (ftitle, 13.0, True, C_INK, PP_ALIGN.LEFT),
                (fbody, 11.0, False, C_SLATE, PP_ALIGN.LEFT),
            ],
            space_after_pt=3.0,
        )

    set_notes(
        s7,
        "[3:50 - 4:15 | 25s] Following Lecture 9's rule to show where our system fails: speaker overlap causes a striking inversion—lower WER than +3dB noise, yet 93.8% Critical Error Rate because interruptions wipe out Hindi post-positional 'nahi'. Second, swapping only our Kannada lexicon achieves 100% F1 on Kannada text with zero code changes, but Whisper-Small fails completely on Kannada audio—motivating IndicConformer or Parrotlet next.",
    )

    # =========================================================================
    # SLIDE 8: FEASIBILITY, CLOUD COST & ROADMAP (4:15 - 4:40) -> 10 MARKS
    # =========================================================================
    s8 = prs.slides.add_slide(blank)
    add_header_and_footer(
        s8,
        "Feasibility, Cloud Cost & Weeks 5–8 Roadmap",
        "Zero cloud GPUs · NRCES SNOMED compliance · < $20 Mumbai AWS budget · clear endsem plan",
        "RUBRIC: FEASIBILITY (10 MARKS)",
        C_AMBER_SOFT,
        C_AMBER,
        "Slide 8 / 9",
    )

    # Col 1: Technical & Licensing Feasibility
    add_accent_card(s8, 0.55, 1.30, 3.92, 5.50, C_TEAL)
    add_textbox(
        s8,
        0.74,
        1.42,
        3.62,
        5.25,
        [
            ("1. Technical & Legal Feasibility", 14.5, True, C_TEAL, PP_ALIGN.LEFT),
            (
                "• SNOMED CT Licensing:\nIndia holds national NRCES membership; scoping to 106–200 common OPD/IPS codes runs 100% locally with zero paid terminology APIs.",
                11.3,
                False,
                C_INK,
                PP_ALIGN.LEFT,
            ),
            (
                "• Reproducibility Ready:\nIndependent repo + README + 10/10 passing pytest tests + SHA-256 dataset manifest + 25 valid FHIR R4 bundles already generated.",
                11.3,
                False,
                C_INK,
                PP_ALIGN.LEFT,
            ),
            (
                "• Controlled Scope:\nCore ASR→SNOMED→FHIR→Severity harness is complete; W5–8 focuses strictly on human volunteer audio & diarization.",
                11.3,
                False,
                C_INK,
                PP_ALIGN.LEFT,
            ),
        ],
        space_after_pt=8.0,
    )

    # Col 2: AWS Cost Governance
    add_accent_card(s8, 4.68, 1.30, 4.02, 5.50, C_BLUE)
    add_textbox(
        s8,
        4.87,
        1.42,
        3.70,
        1.70,
        [
            ("2. Cloud Cost Governance", 14.5, True, C_BLUE, PP_ALIGN.LEFT),
            (
                "• Strict GPU Rule: 0 AWS GPU instances & 0 public endpoints created.\n• Midsem Cloud Spend: $0.00 (Apple M4 int8).",
                11.3,
                False,
                C_INK,
                PP_ALIGN.LEFT,
            ),
        ],
        space_after_pt=5.0,
    )
    tbl_s8 = s8.shapes.add_table(4, 3, Inches(4.86), Inches(3.15), Inches(3.66), Inches(2.25)).table
    for i, w in enumerate([1.56, 1.15, 0.95]):
        tbl_s8.columns[i].width = Inches(w)
    for c_i, h in enumerate(["Scenario", "Audio / Ops", "Total USD"]):
        style_table_cell(tbl_s8.cell(0, c_i), h, 10.2, True, C_WHITE, C_NAVY_DARK)
    c_rows = [
        ("Midsem Pilot (Actual)", "77 WAVs (M4)", "$0.00"),
        ("Endsem 150 Consults", "300m (1x AWS)", "$7.28"),
        ("Endsem 200 Consults", "400m (2x AWS)", "$19.38"),
    ]
    for r_i, (s_n, op, usd) in enumerate(c_rows, start=1):
        rbg = C_TEAL_SOFT if r_i == 1 else (C_WHITE if r_i == 2 else C_ROW_ALT)
        style_table_cell(tbl_s8.cell(r_i, 0), s_n, 10.0, True, C_INK, rbg)
        style_table_cell(tbl_s8.cell(r_i, 1), op, 10.0, False, C_SLATE, rbg)
        style_table_cell(tbl_s8.cell(r_i, 2), usd, 10.5, True, C_TEAL if r_i == 1 else C_BLUE, rbg, PP_ALIGN.RIGHT)

    add_textbox(
        s8,
        4.87,
        5.55,
        3.68,
        1.10,
        [
            ("Region locked to ap-south-1 (Mumbai) in code with project tags, budget alerts & 14-day S3 auto-delete.", 10.5, False, C_SLATE, PP_ALIGN.LEFT)
        ],
    )

    # Col 3: Weeks 5-8 Roadmap
    add_accent_card(s8, 8.91, 1.30, 3.87, 5.50, C_PURPLE)
    add_textbox(
        s8,
        9.10,
        1.42,
        3.55,
        5.25,
        [
            ("3. Weeks 5–8 Execution Plan", 14.5, True, C_PURPLE, PP_ALIGN.LEFT),
            ("• Week 5 (Human Role-Play Data):\nRecord 100–150 consented volunteer Hinglish consults; 10% clinician-friend realism review.", 11.2, False, C_INK, PP_ALIGN.LEFT),
            ("• Week 6 (Models & Diarization):\nBenchmark AWS Transcribe (hi-IN/en-IN) + IndicConformer/Parrotlet; add pyannote diarization for overlap.", 11.2, False, C_INK, PP_ALIGN.LEFT),
            ("• Week 7 (Kannada & Calibration):\nExpand to 200 SNOMED codes; test Indic ASR on Kannada plugin with native speaker checks.", 11.2, False, C_INK, PP_ALIGN.LEFT),
            ("• Week 8 (Tournament & Cleanup):\nFinal reproducible demo, AWS teardown receipt & workshop paper draft.", 11.2, False, C_INK, PP_ALIGN.LEFT),
        ],
        space_after_pt=7.0,
    )

    set_notes(
        s8,
        "[4:15 - 4:40 | 25s] On feasibility: SNOMED CT is covered under India's NRCES license with a local 106-to-200 concept subset. We spent zero cloud dollars and used zero GPU instances by running int8 inference locally on Apple M4. Even two full passes of AWS Transcribe in Mumbai ap-south-1 for 200 human consults is strictly bounded under $20, leading cleanly into our Week 5-8 roadmap.",
    )

    # =========================================================================
    # SLIDE 9: INDIVIDUAL CONTRIBUTIONS (4:40 - 5:00) -> MANDATORY INDIVIDUAL MARKS
    # =========================================================================
    s9 = prs.slides.add_slide(blank)
    add_header_and_footer(
        s9,
        "Individual Contributions — Group 20 (9 Members)",
        "Non-overlapping module ownership across midsem benchmark and Weeks 5–8 deliverables",
        "INDIVIDUAL GRADING SLIDE",
        C_BLUE_SOFT,
        C_BLUE,
        "Slide 9 / 9",
    )

    tbl_s9 = s9.shapes.add_table(10, 5, Inches(0.55), Inches(1.26), Inches(12.23), Inches(5.62)).table
    for i, w in enumerate([1.85, 1.05, 2.35, 3.78, 3.20]):
        tbl_s9.columns[i].width = Inches(w)

    h9 = ["Team Member", "Roll No.", "Module Owned", "Completed Mid-Term Contribution", "Weeks 5–8 End-Term Deliverable"]
    for c_i, h in enumerate(h9):
        style_table_cell(tbl_s9.cell(0, c_i), h, 10.5, True, C_WHITE, C_NAVY_DARK, PP_ALIGN.CENTER if c_i == 1 else PP_ALIGN.LEFT)

    members = [
        ("1. Shivansh Singh", "2023509", "Multi-Model ASR Engine", "Built Faster-Whisper runner (whisper_engine.py); profiled latency/RTF across 320 runs", "Benchmark AWS Transcribe & IndicConformer on 150 human consults"),
        ("2. Tanish Goel", "2023546", "Script Normalizer & Overlap", "Built Devanagari/Kannada→Roman normalizer (nWER/CER) & spectral overlap detector", "Integrate neural diarization (pyannote/NeMo) for 3-party overlap"),
        ("3. Dheeraj Arora", "2023195", "SNOMED CT Lexicons", "Curated 106-concept Hinglish SNOMED lexicon + 14-concept Kannada plugin across 3 domains", "Expand ontology to 200 SNOMED codes with clinician synonym review"),
        ("4. Arnav Gupta", "2023125", "Constrained Hybrid Linker", "Built char TF-IDF + RapidFuzz retriever (0% hallucinated codes) & 1-tap confirm gate", "Add Bedrock Haiku constrained reranker & confidence calibration"),
        ("5. Adarsh", "—", "Clinical Attribute NLP", "Built clause-scoped Hindi negation, fractional doses (dedh/dhai/sawa), duration & family Hx", "Adversarial negation/dose red-teaming & multi-drug regimen rules"),
        ("6. Prakhar", "—", "Architecture & Severity Metric", "Authored proposal; built Clinical Severity Scorer (CSS/CCER) & Spearman divergence tests", "Clinician risk-weight validation & workshop benchmark paper draft"),
        ("7. Sahaj Gupta", "2023459", "HL7 FHIR R4 & Safe Notes", "Built ABDM FHIR R4 serializer, schema validator (25/25 valid) & interactive Clinician UI", "ABDM profile conformance checks & end-to-end live tournament demo"),
        ("8. Rishita Dhankhar", "2023438", "Longitudinal FHIR Memory", "Built SNOMED-indexed multi-visit store & 3×3 Synthea change-summary engine", "Evaluate longitudinal progression alerts across 15 multi-visit cases"),
        ("9. Musaf Khan", "2023331", "Audio, Privacy & Cloud Ops", "Built 77-WAV SNR/overlap mixer, SHA-256 consent gate, PHI redactor, Datasheet & AWS guard", "Coordinate 100–150 consented volunteer recordings & AWS teardown"),
    ]
    for r_i, (m_name, roll, mod, done, nxt) in enumerate(members, start=1):
        rbg = C_WHITE if r_i % 2 == 1 else C_ROW_ALT
        style_table_cell(tbl_s9.cell(r_i, 0), m_name, 10.0, True, C_INK, rbg)
        style_table_cell(tbl_s9.cell(r_i, 1), roll, 10.0, False, C_SLATE, rbg, PP_ALIGN.CENTER, font_name=FONT_MONO)
        style_table_cell(tbl_s9.cell(r_i, 2), mod, 10.0, True, C_BLUE, rbg)
        style_table_cell(tbl_s9.cell(r_i, 3), done, 9.8, False, C_INK, rbg)
        style_table_cell(tbl_s9.cell(r_i, 4), nxt, 9.8, False, C_SLATE, rbg)

    set_notes(
        s9,
        "[4:40 - 5:00 | 20s] Finally, every member of Group 20 owns an independent, verifiable module in our repository—spanning multi-model ASR, script normalization, SNOMED lexicons, constrained linking, Hindi negation/fractional doses, severity scoring, FHIR R4 generation, longitudinal memory, and privacy/audio engineering. Thank you—we welcome your questions and can run our live demo.",
    )

    # =========================================================================
    # SLIDE 10: BACKUP APPENDIX A1 — ORACLE ABLATION & PARETO LATENCY CHART
    # =========================================================================
    s10 = prs.slides.add_slide(blank)
    add_header_and_footer(
        s10,
        "Backup A1: Oracle Ablation & Latency Pareto",
        "Supplementary empirical evidence for Q&A (isolating NLP linking from ASR latency)",
        "APPENDIX / Q&A BACKUP",
        C_ROW_ALT,
        C_SLATE,
        "Backup A1",
    )
    add_rect(s10, 0.55, 1.30, 12.23, 5.50, fill_color=C_WHITE, border_color=C_BORDER, border_pt=1.0, rounded=True)
    add_picture_fit(s10, FIG_DIR / "fig3_oracle_ablation_and_latency_pareto.png", 0.70, 1.42, 11.93, 5.25)
    set_notes(s10, "[Q&A Backup] Shows Oracle transcript ablation (left: 100% SNOMED F1, 0% hallucination) and p95 Apple M4 latency vs Clinical Severity Score (right).")

    # =========================================================================
    # SLIDE 11: BACKUP APPENDIX A2 — LONGITUDINAL MULTI-VISIT DELTAS
    # =========================================================================
    s11 = prs.slides.add_slide(blank)
    add_header_and_footer(
        s11,
        "Backup A2: Longitudinal FHIR Visit Trajectories",
        "Cross-visit SNOMED concept & medication deltas generated by longitudinal_memory.py",
        "APPENDIX / Q&A BACKUP",
        C_ROW_ALT,
        C_SLATE,
        "Backup A2",
    )
    trajs = [
        (
            "SYN-PAT-001 (54M — T2DM Progression)",
            "• V1: T2DM + Polyuria; Metformin 1.0 tab\n"
            "• V2: [RESOLVED] Polyuria; [PROGRESSION_ALERT] Hyperglycemia & Dizziness; [MED_CHANGED] Metformin 1.0 → 1.5 tab\n"
            "• V3: [PROGRESSION_ALERT] Peripheral Neuropathy (302226006) citing V1/V2; Metformin 1.5 → 2.0 tab + Started Vit B12",
            C_BLUE,
        ),
        (
            "SYN-PAT-002 (46F — HTN + NSAID Gastritis)",
            "• V1: HTN + Knee Pain; Amlodipine 1.0 + Ibuprofen 1.0\n"
            "• V2: [NEW] Bloating & Heartburn; [MED_STOPPED] Ibuprofen; [MED_CHANGED] Amlodipine 1.0 → 1.5; [NEW] Pantoprazole\n"
            "• V3: [RESOLVED] Heartburn & Bloating negated (citing V2)",
            C_TEAL,
        ),
        (
            "SYN-PAT-003 (29M — Viral URI Trajectory)",
            "• V1: Fever + Dry Cough; Paracetamol 1.0; Antibiotic refuted\n"
            "• V2: [RESOLVED] Fever; [PROGRESSION_ALERT] Productive Cough & Dyspnea; [NEW] Amoxicillin 1.0 tab\n"
            "• V3: [RESOLVED] Productive Cough & Dyspnea; [MED_STOPPED] Amoxicillin course completed",
            C_PURPLE,
        ),
    ]
    for idx, (ptitle, pbody, pcol) in enumerate(trajs):
        px = 0.55 + idx * 4.14
        add_accent_card(s11, px, 1.32, 3.95, 5.45, pcol)
        add_textbox(
            s11,
            px + 0.18,
            1.45,
            3.62,
            5.15,
            [
                (ptitle, 14.0, True, C_INK, PP_ALIGN.LEFT),
                (pbody, 11.5, False, C_SLATE, PP_ALIGN.LEFT),
            ],
            space_after_pt=8.0,
        )
    set_notes(s11, "[Q&A Backup] Detailed visit-by-visit deltas across all 3 synthetic longitudinal patients (9 valid FHIR R4 bundles).")

    prs.save(str(OUT_PPTX))
    return OUT_PPTX


def audit_deck_geometry(pptx_path: Path) -> None:
    """Verify every shape stays strictly inside slide bounds [0..13.333, 0..7.5] with zero out-of-bounds overflow."""
    prs = Presentation(str(pptx_path))
    w_in = prs.slide_width.inches
    h_in = prs.slide_height.inches
    issues: List[str] = []
    for s_idx, slide in enumerate(prs.slides, start=1):
        for shp in slide.shapes:
            left = shp.left.inches
            top = shp.top.inches
            right = left + shp.width.inches
            bottom = top + shp.height.inches
            if left < -0.05 or top < -0.05 or right > w_in + 0.05 or bottom > h_in + 0.05:
                issues.append(f"Slide {s_idx} shape '{shp.name}' out of bounds: ({left:.2f}, {top:.2f}) -> ({right:.2f}, {bottom:.2f})")
    if issues:
        raise AssertionError("Geometry audit failed:\n" + "\n".join(issues))
    print(f"Geometry audit PASSED across all {len(prs.slides)} slides: zero out-of-bounds shapes.")


if __name__ == "__main__":
    out = build_deck()
    audit_deck_geometry(out)
    print(f"Saved presentation: {out}")
