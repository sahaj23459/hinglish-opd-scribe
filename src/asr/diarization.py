"""Lightweight acoustic VAD, speaker turn change & overlap detector for noisy OPD consults."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

from src.asr.whisper_engine import load_wav_16k_mono


@dataclass
class AcousticSegment:
    """Detected speech segment with spectral energy & overlap confidence."""

    start_sec: float
    end_sec: float
    speaker_cluster: str
    rms_db: float
    spectral_centroid_hz: float
    suspected_overlap: bool


def analyze_turns_and_overlap(
    wav_path: Path,
    frame_ms: int = 30,
    energy_margin_db: float = 8.5,
) -> Dict[str, object]:
    """Segment speech activity, cluster 2-3 speaker pitch/spectral profiles, and flag overlap bursts.

    Uses short-time RMS energy, spectral centroid variance, and spectral flatness
    to flag frames likely containing simultaneous multi-speaker speech (doctor + patient/attendant).
    """
    samples, duration_sec = load_wav_16k_mono(wav_path)
    sr = 16000
    if len(samples) == 0:
        return {"duration_sec": 0.0, "segments": [], "overlap_ratio_est": 0.0}

    frame_len = int(sr * frame_ms / 1000)
    n_frames = len(samples) // frame_len
    if n_frames == 0:
        return {"duration_sec": duration_sec, "segments": [], "overlap_ratio_est": 0.0}

    framed = samples[: n_frames * frame_len].reshape(n_frames, frame_len)
    rms = np.sqrt(np.mean(framed**2, axis=1) + 1e-10)
    rms_db = 20.0 * np.log10(rms)

    noise_floor_db = float(np.percentile(rms_db, 15))
    vad_mask = rms_db > (noise_floor_db + energy_margin_db)

    # Compute FFT magnitude per frame for spectral centroid & harmonic spread
    window = np.hanning(frame_len).astype(np.float32)
    mag = np.abs(np.fft.rfft(framed * window, axis=1)) + 1e-9
    freqs = np.fft.rfftfreq(frame_len, d=1.0 / sr)
    centroids = np.sum(mag * freqs, axis=1) / np.sum(mag, axis=1)
    bandwidth = np.sqrt(
        np.sum(mag * ((freqs[None, :] - centroids[:, None]) ** 2), axis=1) / np.sum(mag, axis=1)
    )

    # Group contiguous active frames (bridging short <180ms pauses)
    gap_bridge = max(1, int(180 / frame_ms))
    smoothed = vad_mask.copy()
    i = 0
    while i < n_frames:
        if not smoothed[i]:
            j = i
            while j < n_frames and not smoothed[j]:
                j += 1
            if i > 0 and j < n_frames and (j - i) <= gap_bridge:
                smoothed[i:j] = True
            i = j
        else:
            i += 1

    active_centroids = centroids[smoothed] if np.any(smoothed) else np.array([1200.0])
    median_centroid = float(np.median(active_centroids))
    high_bw_thresh = float(np.percentile(bandwidth[smoothed], 78)) if np.any(smoothed) else 2000.0
    high_rms_thresh = float(np.percentile(rms_db[smoothed], 75)) if np.any(smoothed) else -20.0

    segments: List[AcousticSegment] = []
    overlap_frames = 0
    active_frame_count = int(np.sum(smoothed))

    idx = 0
    while idx < n_frames:
        if not smoothed[idx]:
            idx += 1
            continue
        end_idx = idx
        while end_idx < n_frames and smoothed[end_idx]:
            end_idx += 1
        if (end_idx - idx) >= 4:  # >= 120ms speech
            seg_c = float(np.mean(centroids[idx:end_idx]))
            seg_rms = float(np.mean(rms_db[idx:end_idx]))
            seg_bw = float(np.mean(bandwidth[idx:end_idx]))
            is_overlap = bool(seg_bw > high_bw_thresh and seg_rms > high_rms_thresh)
            if is_overlap:
                overlap_frames += (end_idx - idx)
            speaker = "SPEAKER_A_LOW" if seg_c <= median_centroid else "SPEAKER_B_HIGH"
            segments.append(
                AcousticSegment(
                    start_sec=round(idx * frame_ms / 1000.0, 3),
                    end_sec=round(end_idx * frame_ms / 1000.0, 3),
                    speaker_cluster=speaker,
                    rms_db=round(seg_rms, 2),
                    spectral_centroid_hz=round(seg_c, 1),
                    suspected_overlap=is_overlap,
                )
            )
        idx = end_idx

    overlap_ratio = overlap_frames / max(active_frame_count, 1)
    return {
        "duration_sec": round(duration_sec, 3),
        "noise_floor_db": round(noise_floor_db, 2),
        "num_detected_turns": len(segments),
        "overlap_ratio_est": round(float(overlap_ratio), 4),
        "segments": segments,
    }


def compute_overlap_detection_f1(
    predicted_segments: List[AcousticSegment],
    ground_truth_overlaps: List[Tuple[float, float]],
    duration_sec: float,
    grid_sec: float = 0.05,
) -> Dict[str, float]:
    """Evaluate frame-level overlap detection accuracy against exact synthetic mix timestamps."""
    n_bins = max(1, int(duration_sec / grid_sec))
    pred_mask = np.zeros(n_bins, dtype=bool)
    gt_mask = np.zeros(n_bins, dtype=bool)

    for seg in predicted_segments:
        if seg.suspected_overlap:
            s = max(0, int(seg.start_sec / grid_sec))
            e = min(n_bins, int(seg.end_sec / grid_sec))
            pred_mask[s:e] = True

    for start, end in ground_truth_overlaps:
        s = max(0, int(start / grid_sec))
        e = min(n_bins, int(end / grid_sec))
        gt_mask[s:e] = True

    tp = int(np.sum(pred_mask & gt_mask))
    fp = int(np.sum(pred_mask & ~gt_mask))
    fn = int(np.sum(~pred_mask & gt_mask))
    precision = tp / (tp + fp) if (tp + fp) > 0 else (1.0 if fn == 0 else 0.0)
    recall = tp / (tp + fn) if (tp + fn) > 0 else 1.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
    }
