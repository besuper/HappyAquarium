import zlib
from functools import lru_cache
from pathlib import Path

ORIGINAL_CDN = b"https://happy-aquarium-fb.101xp.com/"
LOCAL_CDN = b"/assets/".ljust(len(ORIGINAL_CDN), b"/")

# MPEG-1 Layer III, 128 kbps, 44.1 kHz, mono frames of digital silence.
_SILENT_FRAME = bytes([0xFF, 0xFB, 0x90, 0xC4]) + bytes(413)
SILENT_MP3 = _SILENT_FRAME * 20


@lru_cache(maxsize=4)
def patched_main_swf(path: Path, mtime: float) -> bytes:
    data = path.read_bytes()
    if data[:3] != b"CWS":
        raise ValueError(f"{path.name}: expected a zlib-compressed (CWS) SWF")
    body = zlib.decompress(data[8:])
    if ORIGINAL_CDN in body:
        body = body.replace(ORIGINAL_CDN, LOCAL_CDN)
    return data[:8] + zlib.compress(body)
