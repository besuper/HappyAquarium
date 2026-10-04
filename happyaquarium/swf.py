import zlib
from functools import lru_cache
from pathlib import Path

# Transport.CDN_URL in main_deploy_preloaded.swf. The client uses it directly (instead of
# the cdn_url flashvar) for swf/dialogs.xml and for the sound effects.
ORIGINAL_CDN = b"https://happy-aquarium-fb.101xp.com/"
# Same byte length, so the ABC constant pool needs no rebuilding. Root-relative, so the
# client works on any host/port; the extra slashes are collapsed by the app.
LOCAL_CDN = b"/assets/".ljust(len(ORIGINAL_CDN), b"/")

# MPEG-1 Layer III, 128 kbps, 44.1 kHz, mono frames of digital silence.
_SILENT_FRAME = bytes([0xFF, 0xFB, 0x90, 0xC4]) + bytes(413)
SILENT_MP3 = _SILENT_FRAME * 20


@lru_cache(maxsize=4)
def patched_main_swf(path: Path, mtime: float) -> bytes:
    """main_deploy_preloaded.swf with the hardcoded 101XP CDN pointed at /assets/."""
    data = path.read_bytes()
    if data[:3] != b"CWS":
        raise ValueError(f"{path.name}: expected a zlib-compressed (CWS) SWF")
    body = zlib.decompress(data[8:])
    if ORIGINAL_CDN in body:
        body = body.replace(ORIGINAL_CDN, LOCAL_CDN)
    return data[:8] + zlib.compress(body)
