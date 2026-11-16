"""Fetch neural Indian Hindi, Indian English, and Kannada TTS turn stems via edge-tts."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Dict, List

import edge_tts


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_DIR = ROOT / "data" / "manifests"
STEMS_DIR = ROOT / "data" / "audio" / "stems"

# Non-clinical background OPD waiting-room phrases for realistic clinic babble noise synthesis
BACKGROUND_BABBLE_PHRASES = [
    ("bg_01", "hi-IN-MadhurNeural", "टोकन नंबर चौबीस कृपया कमरा नंबर तीन में आ जाइए।"),
    ("bg_02", "hi-IN-SwaraNeural", "पर्ची काउंटर किस तरफ है भाई साहब, लाइन बहुत लंबी है।"),
    ("bg_03", "en-IN-PrabhatNeural", "Please wait outside pharmacy counter number two for your slip."),
    ("bg_04", "en-IN-NeerjaNeural", "Next patient token twenty five please sit on the bench outside."),
]


async def _synth_one(sem: asyncio.Semaphore, stem_id: str, voice: str, text: str, out_path: Path) -> None:
    if out_path.exists() and out_path.stat().st_size > 500:
        return
    async with sem:
        for attempt in range(3):
            try:
                comm = edge_tts.Communicate(text=text, voice=voice, rate="+4%")
                await comm.save(str(out_path))
                if out_path.exists() and out_path.stat().st_size > 500:
                    return
            except Exception as exc:
                if attempt == 2:
                    raise RuntimeError(f"Failed TTS for {stem_id}: {exc}") from exc
                await asyncio.sleep(1.0 * (attempt + 1))


async def main_async() -> None:
    STEMS_DIR.mkdir(parents=True, exist_ok=True)
    sem = asyncio.Semaphore(6)
    tasks: List[asyncio.Task[None]] = []

    pilot = json.loads((MANIFEST_DIR / "pilot_consults_v1.json").read_text(encoding="utf-8"))["consults"]
    for c in pilot:
        cid = c["consult_id"]
        for t_idx, turn in enumerate(c["turns"]):
            stem_id = f"{cid}_turn{t_idx:02d}"
            out_mp3 = STEMS_DIR / f"{stem_id}.mp3"
            # en-IN neural voices require Latin/Romanized Hinglish; hi-IN voices read Devanagari + English
            tts_script = turn["text_ref"] if str(turn["voice"]).startswith("en-IN") else turn["text_tts"]
            tasks.append(
                asyncio.create_task(_synth_one(sem, stem_id, turn["voice"], tts_script, out_mp3))
            )

    kn_list = json.loads((MANIFEST_DIR / "kannada_portability_v1.json").read_text(encoding="utf-8"))["consults"]
    for kc in kn_list:
        cid = kc["consult_id"]
        out_mp3 = STEMS_DIR / f"{cid}_turn00.mp3"
        tasks.append(
            asyncio.create_task(_synth_one(sem, cid, kc["voice"], kc["text_tts"], out_mp3))
        )

    for bg_id, bg_voice, bg_text in BACKGROUND_BABBLE_PHRASES:
        out_mp3 = STEMS_DIR / f"{bg_id}.mp3"
        tasks.append(asyncio.create_task(_synth_one(sem, bg_id, bg_voice, bg_text, out_mp3)))

    await asyncio.gather(*tasks)
    print(f"Synthesized {len(tasks)} neural Indian speech stems in {STEMS_DIR}")


if __name__ == "__main__":
    asyncio.run(main_async())
