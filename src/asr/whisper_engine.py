"""Reproducible Faster-Whisper ASR engine with latency profiling and Hinglish clinical prompting."""

from __future__ import annotations

import time
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np


HINGLISH_CLINICAL_INITIAL_PROMPT = (
    "Doctor sahab OPD consult in Romanized Hinglish: mujhe teen din se bukhar hai, "
    "sir mein dard nahi hai, khansi zukam, pet mein gas banti hai, khatti dakar, "
    "chakkar aana, sugar high hai, BP ki dawa, Paracetamol dedh goli, Metformin dhai tablet, "
    "Amlodipine aadhi goli, Azithromycin antibiotic mat lijiye, paer mein jhanjhanahat, "
    "baayein kandhe mein dard, pitaji ko diabetes thi."
)

KANNADA_CLINICAL_INITIAL_PROMPT = (
    "ಡಾಕ್ಟರ್ ನನಗೆ ಮೂರು ದಿನದಿಂದ ಜ್ವರ ಇದೆ, ಆದರೆ ತಲೆನೋವು ಇಲ್ಲ, ಕೆಮ್ಮು ಶೀತ, "
    "ಹೊಟ್ಟೆ ಉಬ್ಬರ ಗ್ಯಾಸ್, ಸಕ್ಕರೆ ಕಾಯಿಲೆ, ಬಿಪಿ ಮಾತ್ರೆ, ಪ್ಯಾರಾಸಿಟಮಾಲ್ ಒಂದೂವರೆ ಮಾತ್ರೆ, "
    "ಮೆಟ್ಫಾರ್ಮಿನ್, ಆಂಟಿಬಯೋಟಿಕ್ ಬೇಡ."
)


@dataclass
class ASRConfig:
    """Configuration for a reproducible ASR experimental arm."""

    arm_id: str
    display_name: str
    model_size: str
    language: Optional[str] = None
    task: str = "transcribe"
    initial_prompt: Optional[str] = None
    beam_size: int = 3
    vad_filter: bool = False
    estimated_cloud_usd_per_min: float = 0.0


@dataclass
class ASRResult:
    """Single-utterance or single-consult ASR output with timing telemetry."""

    arm_id: str
    audio_path: str
    raw_transcript: str
    detected_language: str
    language_probability: float
    audio_duration_sec: float
    inference_latency_sec: float
    real_time_factor: float
    estimated_cost_usd: float


def load_wav_16k_mono(wav_path: Path) -> tuple[np.ndarray, float]:
    """Load 16 kHz mono 16-bit PCM WAV directly using stdlib wave (zero external ffmpeg dependency)."""
    with wave.open(str(wav_path), "rb") as wf:
        sr = wf.getframerate()
        n_channels = wf.getnchannels()
        n_frames = wf.getnframes()
        pcm_bytes = wf.readframes(n_frames)
    samples = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32) / 32768.0
    if n_channels > 1:
        samples = samples.reshape(-1, n_channels).mean(axis=1)
    if sr != 16000 and len(samples) > 0:
        # Linear interpolation resample if needed
        duration = len(samples) / sr
        target_len = int(round(duration * 16000))
        x_old = np.linspace(0.0, duration, num=len(samples), endpoint=False)
        x_new = np.linspace(0.0, duration, num=target_len, endpoint=False)
        samples = np.interp(x_new, x_old, samples).astype(np.float32)
        sr = 16000
    duration_sec = len(samples) / float(sr) if sr > 0 else 0.0
    return samples, duration_sec


class WhisperExperimentRunner:
    """Caches loaded Faster-Whisper models on Apple Silicon CPU (int8) and runs timed evaluations."""

    def __init__(self, compute_type: str = "int8", cpu_threads: int = 8) -> None:
        self.compute_type = compute_type
        self.cpu_threads = cpu_threads
        self._models: Dict[str, object] = {}

    def _get_model(self, model_size: str):
        if model_size not in self._models:
            from faster_whisper import WhisperModel

            cache_dir = Path(__file__).resolve().parents[2] / "models" / "whisper_cache"
            cache_dir.mkdir(parents=True, exist_ok=True)
            has_local = any(cache_dir.glob(f"*whisper-{model_size}*"))
            self._models[model_size] = WhisperModel(
                model_size,
                device="cpu",
                compute_type=self.compute_type,
                cpu_threads=self.cpu_threads,
                download_root=str(cache_dir),
                local_files_only=has_local,
            )
        return self._models[model_size]

    def transcribe_file(self, wav_path: Path, config: ASRConfig) -> ASRResult:
        model = self._get_model(config.model_size)
        audio_np, duration_sec = load_wav_16k_mono(wav_path)

        t0 = time.perf_counter()
        segments_gen, info = model.transcribe(
            audio_np,
            language=config.language,
            task=config.task,
            beam_size=config.beam_size,
            initial_prompt=config.initial_prompt,
            vad_filter=config.vad_filter,
            condition_on_previous_text=False,
        )
        segments_text: List[str] = [seg.text.strip() for seg in segments_gen if seg.text.strip()]
        latency_sec = time.perf_counter() - t0

        full_text = " ".join(segments_text)
        rtf = latency_sec / max(duration_sec, 1e-3)
        cost_usd = (duration_sec / 60.0) * config.estimated_cloud_usd_per_min

        return ASRResult(
            arm_id=config.arm_id,
            audio_path=str(wav_path),
            raw_transcript=full_text,
            detected_language=getattr(info, "language", config.language or "unknown"),
            language_probability=float(getattr(info, "language_probability", 0.0)),
            audio_duration_sec=round(duration_sec, 3),
            inference_latency_sec=round(latency_sec, 4),
            real_time_factor=round(rtf, 4),
            estimated_cost_usd=round(cost_usd, 6),
        )


DEFAULT_HINGLISH_ASR_ARMS: List[ASRConfig] = [
    ASRConfig(
        arm_id="whisper_tiny_auto",
        display_name="Whisper-Tiny (Unprompted Auto)",
        model_size="tiny",
        language=None,
        initial_prompt=None,
        beam_size=2,
        estimated_cloud_usd_per_min=0.0,
    ),
    ASRConfig(
        arm_id="whisper_base_en_forced",
        display_name="Whisper-Base (English-Forced Dictation)",
        model_size="base",
        language="en",
        initial_prompt=None,
        beam_size=3,
        estimated_cloud_usd_per_min=0.0,
    ),
    ASRConfig(
        arm_id="whisper_base_auto",
        display_name="Whisper-Base (Multilingual Auto)",
        model_size="base",
        language=None,
        initial_prompt=None,
        beam_size=3,
        estimated_cloud_usd_per_min=0.0,
    ),
    ASRConfig(
        arm_id="whisper_small_auto",
        display_name="Whisper-Small (Multilingual Unprompted)",
        model_size="small",
        language="hi",
        initial_prompt=None,
        beam_size=3,
        estimated_cloud_usd_per_min=0.0,
    ),
    ASRConfig(
        arm_id="whisper_small_clinical_hinglish",
        display_name="Whisper-Small + Hinglish Clinical Lexicon Prompt",
        model_size="small",
        language="hi",
        initial_prompt=HINGLISH_CLINICAL_INITIAL_PROMPT,
        beam_size=4,
        estimated_cloud_usd_per_min=0.0,
    ),
]
