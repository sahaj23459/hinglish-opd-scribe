"""Prefetch Faster-Whisper CTranslate2 models (tiny, base, small) into workspace cache."""

from __future__ import annotations

from pathlib import Path
from faster_whisper import WhisperModel


ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "models" / "whisper_cache"


def main() -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    for size in ("tiny", "base", "small"):
        print(f"Fetching Faster-Whisper model: {size} ...", flush=True)
        _ = WhisperModel(size, device="cpu", compute_type="int8", download_root=str(CACHE_DIR))
        print(f"Cached: {size}", flush=True)


if __name__ == "__main__":
    main()
