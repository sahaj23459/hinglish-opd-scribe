"""Decode neural speech stems offline & build deterministic Clean, Noisy (10dB, 3dB) & Overlap WAVs."""

from __future__ import annotations

import json
import sys
import wave
from pathlib import Path
from typing import Dict, List, Tuple

import av
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.privacy.consent_and_redaction import ConsentRecord, compute_file_sha256, enforce_consent_gate


MANIFEST_DIR = ROOT / "data" / "manifests"
STEMS_DIR = ROOT / "data" / "audio" / "stems"
AUDIO_OUT_DIR = ROOT / "data" / "audio"
TARGET_SR = 16000


def decode_audio_to_16k_mono(path: Path) -> np.ndarray:
    """Decode MP3/WAV to 16 kHz float32 mono numpy array via PyAV resampler."""
    container = av.open(str(path))
    resampler = av.AudioResampler(format="s16", layout="mono", rate=TARGET_SR)
    chunks: List[np.ndarray] = []
    for frame in container.decode(audio=0):
        resampled_frames = resampler.resample(frame)
        if not isinstance(resampled_frames, list):
            resampled_frames = [resampled_frames]
        for rf in resampled_frames:
            if rf is not None:
                arr = rf.to_ndarray().reshape(-1).astype(np.float32) / 32768.0
                chunks.append(arr)
    container.close()
    if not chunks:
        return np.zeros(0, dtype=np.float32)
    pcm = np.concatenate(chunks)
    # Trim leading/trailing near-silence
    non_silent = np.where(np.abs(pcm) > 0.006)[0]
    if len(non_silent) > 0:
        s = max(0, int(non_silent[0]) - int(0.05 * TARGET_SR))
        e = min(len(pcm), int(non_silent[-1]) + int(0.08 * TARGET_SR))
        pcm = pcm[s:e]
    return pcm


def save_wav_16k(path: Path, samples: np.ndarray) -> float:
    """Write normalized float32 [-1, 1] array as 16-bit PCM 16 kHz mono WAV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    peak = float(np.max(np.abs(samples))) if len(samples) > 0 else 0.0
    if peak > 0.96:
        samples = samples * (0.94 / peak)
    pcm16 = np.clip(samples * 32767.0, -32768, 32767).astype(np.int16)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(TARGET_SR)
        wf.writeframes(pcm16.tobytes())
    return round(len(pcm16) / float(TARGET_SR), 3)


def build_opd_noise_bed(length: int, babble_pool: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Synthesize realistic Indian OPD ambient soundscape: waiting-room babble + ceiling fan hum + transients."""
    t = np.arange(length, dtype=np.float32) / float(TARGET_SR)
    # 1. Ceiling fan / AC low-frequency hum + pink-ish room tone
    hum = 0.25 * np.sin(2 * np.pi * 100.0 * t) + 0.15 * np.sin(2 * np.pi * 50.0 * t)
    white = rng.standard_normal(length).astype(np.float32)
    # Simple moving-average lowpass for warm room rumble
    kernel = np.ones(12, dtype=np.float32) / 12.0
    room = np.convolve(white, kernel, mode="same")

    # 2. Multi-talker background waiting-room babble drawn from non-clinical stems
    babble = np.zeros(length, dtype=np.float32)
    if len(babble_pool) > TARGET_SR:
        for _ in range(3):
            offset = int(rng.integers(0, max(1, len(babble_pool) - 1)))
            tiled = np.tile(babble_pool, (length // len(babble_pool)) + 2)
            babble += 0.45 * tiled[offset : offset + length]

    # 3. Intermittent clinic chair/door impulse clicks
    impulses = np.zeros(length, dtype=np.float32)
    n_clicks = max(1, length // (3 * TARGET_SR))
    for _ in range(n_clicks):
        pos = int(rng.integers(0, max(1, length - 800)))
        decay = np.exp(-np.linspace(0, 8, 800)).astype(np.float32)
        impulses[pos : pos + 800] += 0.5 * rng.standard_normal(800).astype(np.float32) * decay

    bed = 0.25 * hum + 0.45 * room + 0.70 * babble + 0.15 * impulses
    return bed.astype(np.float32)


def mix_at_snr_db(clean: np.ndarray, noise: np.ndarray, snr_db: float) -> np.ndarray:
    """Mix noise into clean signal at an exact target Signal-to-Noise Ratio (dB)."""
    sig_power = float(np.mean(clean**2)) + 1e-10
    noise_power = float(np.mean(noise**2)) + 1e-10
    target_noise_power = sig_power / (10.0 ** (snr_db / 10.0))
    scale = np.sqrt(target_noise_power / noise_power)
    return (clean + float(scale) * noise).astype(np.float32)


def stitch_clean_turns(turn_arrays: List[np.ndarray], pause_sec: float = 0.28) -> Tuple[np.ndarray, List[Tuple[float, float]]]:
    """Concatenate multi-speaker turns with natural inter-turn pause and return turn timestamps."""
    pause = np.zeros(int(pause_sec * TARGET_SR), dtype=np.float32)
    pieces: List[np.ndarray] = []
    spans: List[Tuple[float, float]] = []
    cursor = 0
    for idx, arr in enumerate(turn_arrays):
        if idx > 0:
            pieces.append(pause)
            cursor += len(pause)
        start_s = cursor / float(TARGET_SR)
        pieces.append(arr)
        cursor += len(arr)
        end_s = cursor / float(TARGET_SR)
        spans.append((round(start_s, 3), round(end_s, 3)))
    return (np.concatenate(pieces) if pieces else np.zeros(0, dtype=np.float32)), spans


def stitch_overlapping_turns(
    turn_arrays: List[np.ndarray], overlap_fraction: float = 0.28
) -> Tuple[np.ndarray, List[Tuple[float, float]]]:
    """Create realistic OPD interruption/overlap audio and return exact overlap intervals."""
    if not turn_arrays:
        return np.zeros(0, dtype=np.float32), []
    if len(turn_arrays) == 1:
        return turn_arrays[0].copy(), []

    total_len = sum(len(a) for a in turn_arrays)
    canvas = np.zeros(total_len, dtype=np.float32)
    overlaps: List[Tuple[float, float]] = []

    cursor = 0
    for idx, arr in enumerate(turn_arrays):
        if idx == 0:
            canvas[0 : len(arr)] += arr
            cursor = len(arr)
        else:
            prev_len = len(turn_arrays[idx - 1])
            ov_samples = min(int(prev_len * overlap_fraction), int(0.9 * TARGET_SR), len(arr) // 2)
            start = max(0, cursor - ov_samples)
            if ov_samples > 0:
                overlaps.append((round(start / float(TARGET_SR), 3), round(cursor / float(TARGET_SR), 3)))
            canvas[start : start + len(arr)] += arr
            cursor = max(cursor, start + len(arr))

    return canvas[:cursor], overlaps


def main() -> None:
    rng = np.random.default_rng(42)
    audit_log = MANIFEST_DIR / "consent_audit.jsonl"
    if audit_log.exists():
        audit_log.unlink()

    # Load background babble pool
    bg_chunks: List[np.ndarray] = []
    for bg_idx in range(1, 5):
        bg_mp3 = STEMS_DIR / f"bg_0{bg_idx}.mp3"
        if bg_mp3.exists():
            bg_chunks.append(decode_audio_to_16k_mono(bg_mp3))
    babble_pool = np.concatenate(bg_chunks) if bg_chunks else np.zeros(TARGET_SR * 4, dtype=np.float32)

    pilot = json.loads((MANIFEST_DIR / "pilot_consults_v1.json").read_text(encoding="utf-8"))["consults"]
    kn_list = json.loads((MANIFEST_DIR / "kannada_portability_v1.json").read_text(encoding="utf-8"))["consults"]

    manifest_records: List[Dict[str, object]] = []

    for c in pilot:
        cid = c["consult_id"]
        split = c["split"]
        turn_arrays = [
            decode_audio_to_16k_mono(STEMS_DIR / f"{cid}_turn{i:02d}.mp3")
            for i in range(len(c["turns"]))
        ]
        ref_full = " ".join(t["text_ref"] for t in c["turns"])

        # 1. Clean WAV (for both dev and test)
        clean_pcm, turn_spans = stitch_clean_turns(turn_arrays)
        clean_wav = AUDIO_OUT_DIR / "clean" / f"{cid}.wav"
        dur_clean = save_wav_16k(clean_wav, clean_pcm)
        sha_clean = compute_file_sha256(clean_wav)
        enforce_consent_gate(
            ConsentRecord(
                session_id=f"{cid}-clean",
                participant_role="synthetic_neural_roleplay",
                consent_granted=True,
                verification_method="synthetic_manifest_signed",
                audio_sha256=sha_clean,
            ),
            audit_log,
        )
        manifest_records.append(
            {
                "consult_id": cid,
                "split": split,
                "language": "hinglish",
                "domain": c["domain"],
                "acoustic_condition": "clean",
                "snr_db": None,
                "wav_path": str(clean_wav.relative_to(ROOT)),
                "duration_sec": dur_clean,
                "sha256": sha_clean,
                "turn_spans": turn_spans,
                "overlap_spans": [],
                "reference_transcript": ref_full,
            }
        )

        # For locked held-out test split, generate exact SNR +10dB, +3dB, and Overlapping OPD audio!
        if split == "test":
            noise_10 = build_opd_noise_bed(len(clean_pcm), babble_pool, rng)
            pcm_10 = mix_at_snr_db(clean_pcm, noise_10, snr_db=10.0)
            wav_10 = AUDIO_OUT_DIR / "noisy_10db" / f"{cid}.wav"
            dur_10 = save_wav_16k(wav_10, pcm_10)
            manifest_records.append(
                {
                    "consult_id": cid,
                    "split": split,
                    "language": "hinglish",
                    "domain": c["domain"],
                    "acoustic_condition": "noisy_10db",
                    "snr_db": 10.0,
                    "wav_path": str(wav_10.relative_to(ROOT)),
                    "duration_sec": dur_10,
                    "sha256": compute_file_sha256(wav_10),
                    "turn_spans": turn_spans,
                    "overlap_spans": [],
                    "reference_transcript": ref_full,
                }
            )

            noise_3 = build_opd_noise_bed(len(clean_pcm), babble_pool, rng)
            pcm_3 = mix_at_snr_db(clean_pcm, noise_3, snr_db=3.0)
            wav_3 = AUDIO_OUT_DIR / "noisy_3db" / f"{cid}.wav"
            dur_3 = save_wav_16k(wav_3, pcm_3)
            manifest_records.append(
                {
                    "consult_id": cid,
                    "split": split,
                    "language": "hinglish",
                    "domain": c["domain"],
                    "acoustic_condition": "noisy_3db",
                    "snr_db": 3.0,
                    "wav_path": str(wav_3.relative_to(ROOT)),
                    "duration_sec": dur_3,
                    "sha256": compute_file_sha256(wav_3),
                    "turn_spans": turn_spans,
                    "overlap_spans": [],
                    "reference_transcript": ref_full,
                }
            )

            ov_clean, ov_spans = stitch_overlapping_turns(turn_arrays, overlap_fraction=0.28)
            ov_noise = build_opd_noise_bed(len(ov_clean), babble_pool, rng)
            pcm_ov = mix_at_snr_db(ov_clean, ov_noise, snr_db=10.0)
            wav_ov = AUDIO_OUT_DIR / "overlap_10db" / f"{cid}.wav"
            dur_ov = save_wav_16k(wav_ov, pcm_ov)
            manifest_records.append(
                {
                    "consult_id": cid,
                    "split": split,
                    "language": "hinglish",
                    "domain": c["domain"],
                    "acoustic_condition": "overlap_10db",
                    "snr_db": 10.0,
                    "wav_path": str(wav_ov.relative_to(ROOT)),
                    "duration_sec": dur_ov,
                    "sha256": compute_file_sha256(wav_ov),
                    "turn_spans": [],
                    "overlap_spans": ov_spans,
                    "reference_transcript": ref_full,
                }
            )

    # Kannada Portability WAVs
    for kc in kn_list:
        cid = kc["consult_id"]
        kn_pcm = decode_audio_to_16k_mono(STEMS_DIR / f"{cid}_turn00.mp3")
        kn_wav = AUDIO_OUT_DIR / "kannada_clean" / f"{cid}.wav"
        dur_kn = save_wav_16k(kn_wav, kn_pcm)
        sha_kn = compute_file_sha256(kn_wav)
        enforce_consent_gate(
            ConsentRecord(
                session_id=f"{cid}-clean",
                participant_role="synthetic_neural_kannada",
                consent_granted=True,
                verification_method="synthetic_manifest_signed",
                audio_sha256=sha_kn,
            ),
            audit_log,
        )
        manifest_records.append(
            {
                "consult_id": cid,
                "split": "kannada_portability",
                "language": "kn-IN",
                "domain": "portability",
                "acoustic_condition": "clean",
                "snr_db": None,
                "wav_path": str(kn_wav.relative_to(ROOT)),
                "duration_sec": dur_kn,
                "sha256": sha_kn,
                "turn_spans": [(0.0, dur_kn)],
                "overlap_spans": [],
                "reference_transcript": kc["text_ref"],
            }
        )

    total_sec = sum(float(r["duration_sec"]) for r in manifest_records)
    manifest_out = {
        "dataset_name": "Hinglish-OPD-Scribe-Midsem-Pilot-v1",
        "phi_status": "ZERO_REAL_PATIENT_DATA_100_PERCENT_SYNTHETIC_CONSENTED",
        "sample_rate_hz": TARGET_SR,
        "random_seed": 42,
        "total_audio_files": len(manifest_records),
        "total_duration_sec": round(total_sec, 2),
        "records": manifest_records,
    }
    (MANIFEST_DIR / "dataset_manifest.json").write_text(
        json.dumps(manifest_out, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Built {len(manifest_records)} WAV files ({total_sec:.1f}s total audio) + SHA-256 dataset_manifest.json")


if __name__ == "__main__":
    main()
