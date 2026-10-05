"""Generate placeholder SWFs for assets that were never recovered.

The client cannot start without a tank, its dirt overlay, a gravel and the gift
prop, and none of the originals survived. These stubs follow the formats the
client expects (see docs/ASSET_FORMATS.md):
  - tank background: any MovieClip, centred on the origin;
  - dirt / gravel / gift: a named child ("dirt", "gravel", "decor") linked to an
    AS3 class, because the client clones art with `new child.constructor()`.

The SWFs are written by hand (no Flash/Flex toolchain needed), including a
minimal ABC block declaring `class X extends flash.display.MovieClip`.

Usage: python tools/make_stub_swf.py [assets_dir]   (default: ./assets)
"""
import struct
import sys
import zlib
from pathlib import Path

TWIP = 20


class Bits:
    def __init__(self):
        self.out = bytearray()
        self.acc = 0
        self.n = 0

    def write(self, value, nbits):
        for i in range(nbits - 1, -1, -1):
            self.acc = (self.acc << 1) | ((value >> i) & 1)
            self.n += 1
            if self.n == 8:
                self.out.append(self.acc)
                self.acc = self.n = 0

    def write_signed(self, value, nbits):
        self.write(value & ((1 << nbits) - 1), nbits)

    def flush(self):
        if self.n:
            self.out.append(self.acc << (8 - self.n))
            self.acc = self.n = 0
        return bytes(self.out)


def nbits_signed(*vals):
    n = 1
    for v in vals:
        need = (abs(v) if v >= 0 else abs(v) - 1).bit_length() + 1
        n = max(n, need)
    return n


def rect(xmin, xmax, ymin, ymax):
    b = Bits()
    n = nbits_signed(xmin, xmax, ymin, ymax)
    b.write(n, 5)
    for v in (xmin, xmax, ymin, ymax):
        b.write_signed(v, n)
    return b.flush()


def tag(code, body=b""):
    if len(body) < 0x3F:
        return struct.pack("<H", (code << 6) | len(body)) + body
    return struct.pack("<HI", (code << 6) | 0x3F, len(body)) + body


def define_shape_rect(char_id, x, y, w, h, rgb):
    """DefineShape with a single solid filled rectangle (coords in pixels)."""
    x0, y0, x1, y1 = x * TWIP, y * TWIP, (x + w) * TWIP, (y + h) * TWIP
    body = struct.pack("<H", char_id) + rect(x0, x1, y0, y1)
    body += bytes([1, 0x00]) + bytes(rgb)  # 1 fill style: solid RGB
    body += bytes([0])  # 0 line styles
    b = Bits()
    b.write(1, 4)  # NumFillBits
    b.write(0, 4)  # NumLineBits
    # StyleChangeRecord: MoveTo + FillStyle0
    b.write(0, 1)
    b.write(0b00011, 5)  # flags: StateFillStyle0 | StateMoveTo
    n = nbits_signed(x0, y0)
    b.write(n, 5)
    b.write_signed(x0, n)
    b.write_signed(y0, n)
    b.write(1, 1)  # FillStyle0 = 1
    for dx, dy in ((x1 - x0, 0), (0, y1 - y0), (x0 - x1, 0), (0, y0 - y1)):
        b.write(1, 1)  # edge
        b.write(1, 1)  # straight
        n = nbits_signed(dx, dy)
        b.write(n - 2, 4)
        if dx and dy:
            b.write(1, 1)
            b.write_signed(dx, n)
            b.write_signed(dy, n)
        else:
            b.write(0, 1)
            b.write(1 if dy else 0, 1)  # vertical?
            b.write_signed(dy if dy else dx, n)
    b.write(0, 6)  # EndShapeRecord
    body += b.flush()
    return tag(2, body)


def place(depth, char_id, name=None):
    flags = 0x02 | (0x20 if name else 0)
    body = bytes([flags]) + struct.pack("<HH", depth, char_id)
    if name:
        body += name.encode() + b"\0"
    return tag(26, body)


def sprite(char_id, *children):
    """DefineSprite placing the given character ids at increasing depths."""
    inner = b"".join(place(i + 1, c) for i, c in enumerate(children))
    return tag(39, struct.pack("<HH", char_id, 1) + inner + tag(1) + tag(0))


def u30(v):
    out = bytearray()
    while True:
        b = v & 0x7F
        v >>= 7
        if v:
            out.append(b | 0x80)
        else:
            out.append(b)
            return bytes(out)


def abc_string(s):
    raw = s.encode()
    return u30(len(raw)) + raw


def movieclip_subclass_abc(class_name):
    """ABC bytecode for: package { public class <class_name> extends flash.display.MovieClip {} }

    The client instantiates art via `child.constructor`; without a linked class that is a
    bare MovieClip with no graphics (and a 0x0 BitmapData crash), so stubs need real classes.
    """
    strings = ["", class_name, "flash.display", "MovieClip"]  # indices 1..4
    pool = u30(1) + u30(1) + u30(1)  # no ints / uints / doubles
    pool += u30(len(strings) + 1) + b"".join(abc_string(x) for x in strings)
    pool += u30(3) + bytes([0x16]) + u30(1) + bytes([0x16]) + u30(3)  # ns1: "", ns2: flash.display
    pool += u30(1)  # no ns sets
    pool += u30(3) + bytes([0x07]) + u30(1) + u30(2) + bytes([0x07]) + u30(2) + u30(4)  # mn1: Foo, mn2: MovieClip
    methods = u30(3) + b"".join(u30(0) + u30(0) + u30(0) + bytes([0]) for _ in range(3))
    metadata = u30(0)
    instance = u30(1) + u30(2) + bytes([0x00]) + u30(0) + u30(1) + u30(0)  # name, super, dynamic, iinit=m1
    classes = u30(1) + instance + u30(2) + u30(0)  # cinit = m2
    scripts = u30(1) + u30(0) + u30(1) + u30(1) + bytes([0x04]) + u30(1) + u30(0)  # init=m0, trait Class slot1

    def body(method, code, max_stack):
        return (u30(method) + u30(max_stack) + u30(1) + u30(0) + u30(1)
                + u30(len(code)) + code + u30(0) + u30(0))

    script_init = bytes([0xD0, 0x30, 0xD0, 0x60]) + u30(2) + bytes([0x58]) + u30(0) + bytes([0x68]) + u30(1) + bytes([0x47])
    iinit = bytes([0xD0, 0x30, 0xD0, 0x49]) + u30(0) + bytes([0x47])
    cinit = bytes([0xD0, 0x30, 0x47])
    bodies = u30(3) + body(0, script_init, 2) + body(1, iinit, 1) + body(2, cinit, 1)
    return struct.pack("<HH", 16, 46) + pool + methods + metadata + classes + scripts + bodies


def linked_sprite(char_id, class_name, *children):
    """A DefineSprite plus the DoABC + SymbolClass tags linking it to a MovieClip subclass."""
    nul = bytes(1)
    abc = tag(82, struct.pack("<I", 1) + nul + movieclip_subclass_abc(class_name))
    symbol = tag(76, struct.pack("<HH", 1, char_id) + class_name.encode() + nul)
    return sprite(char_id, *children) + abc + symbol


def frame_label(name):
    return tag(43, name.encode() + bytes(1))


def remove(depth):
    return tag(28, struct.pack("<H", depth))


def labelled_sprite(char_id, frames):
    """Multi-frame DefineSprite: frames is a list of (label, shape_id) shown one per frame."""
    inner = b""
    for i, (label, shape_id) in enumerate(frames):
        if i:
            inner += remove(1)
        inner += frame_label(label) + place(1, shape_id) + tag(1)
    return tag(39, struct.pack("<HH", char_id, len(frames)) + inner + tag(0))


def swf(width, height, tags, bg=(0, 0, 0)):
    body = rect(0, width * TWIP, 0, height * TWIP) + struct.pack("<HH", 24 << 8, 1)
    body += tag(69, struct.pack("<I", 0x08))  # FileAttributes: ActionScript 3
    body += tag(9, bytes(bg))
    body += b"".join(tags) + tag(1) + tag(0)
    raw = struct.pack("<I", 8 + len(body))
    return b"CWS" + bytes([10]) + raw + zlib.compress(body)


ART = Path(__file__).resolve().parent / "stub_art"
WATER_TOP, WATER_BOTTOM = (0x8f, 0xdc, 0xf0), (0x1f, 0x7c, 0xbf)
SAND_TINT = (0xf0, 0xd9, 0x9c)


def lossless_bitmap(bitmap_id, img):
    """DefineBitsLossless2: 32-bit premultiplied ARGB."""
    img = img.convert("RGBA")
    w, h = img.size
    px = bytearray()
    for r, g, b, a in img.getdata():
        px += bytes([a, r * a // 255, g * a // 255, b * a // 255])
    return tag(36, struct.pack("<HBHH", bitmap_id, 5, w, h) + zlib.compress(bytes(px)))


def bitmap_shape(shape_id, bitmap_id, x, y, w, h):
    """DefineShape showing a bitmap 1:1 with its top-left corner at (x, y) pixels."""
    x0, y0, x1, y1 = x * TWIP, y * TWIP, (x + w) * TWIP, (y + h) * TWIP
    body = struct.pack("<H", shape_id) + rect(x0, x1, y0, y1)
    body += bytes([1, 0x41]) + struct.pack("<H", bitmap_id)
    m = Bits()
    m.write(1, 1)
    scale = TWIP << 16
    n = nbits_signed(scale)
    m.write(n, 5)
    m.write_signed(scale, n)
    m.write_signed(scale, n)
    m.write(0, 1)
    n = nbits_signed(x0, y0)
    m.write(n, 5)
    m.write_signed(x0, n)
    m.write_signed(y0, n)
    body += m.flush() + bytes([0])
    b = Bits()
    b.write(1, 4)
    b.write(0, 4)
    b.write(0, 1)
    b.write(0b00011, 5)
    n = nbits_signed(x0, y0)
    b.write(n, 5)
    b.write_signed(x0, n)
    b.write_signed(y0, n)
    b.write(1, 1)
    for dx, dy in ((x1 - x0, 0), (0, y1 - y0), (x0 - x1, 0), (0, y0 - y1)):
        b.write(1, 1)
        b.write(1, 1)
        n = nbits_signed(dx, dy)
        b.write(n - 2, 4)
        b.write(0, 1)
        b.write(1 if dy else 0, 1)
        b.write_signed(dy if dy else dx, n)
    b.write(0, 6)
    return tag(2, body + b.flush())


def tint(img, color):
    """Colourise a greyscale image (Fish with Attitude ships its "locked" art in grey)."""
    from PIL import ImageOps
    grey = ImageOps.grayscale(img)
    coloured = ImageOps.colorize(grey, black=tuple(c // 3 for c in color), white=color).convert("RGBA")
    coloured.putalpha(img.convert("RGBA").getchannel("A"))
    return coloured


def tank_background(w, h):
    from PIL import Image
    water = Image.new("RGBA", (w, h))
    for y in range(h):
        t = y / (h - 1)
        water.paste(tuple(round(a + (b - a) * t) for a, b in zip(WATER_TOP, WATER_BOTTOM)) + (255,), (0, y, w, y + 1))
    # Keep only the frame's light edges, drawn as faint glass highlights over the water
    frame = Image.open(ART / "fwa_tank_frame.png").convert("L").resize((w, h), Image.LANCZOS)
    edges = frame.point(lambda v: 110 if v > 200 else 0)
    water.paste(Image.new("RGBA", (w, h), (255, 255, 255, 255)), (0, 0), edges)
    return water


def tank_stub(w, h):
    # FishTank centres this clip (x = width/2), so draw around the origin
    return swf(w, h, [
        lossless_bitmap(1, tank_background(w, h)),
        bitmap_shape(2, 1, -w // 2, -h // 2, w, h),
        place(1, 2),
    ])


def dirt_stub(w, h):
    # 1px shape so the dirt overlay has non-empty bounds
    return swf(w, h, [
        define_shape_rect(1, 0, 0, 1, 1, (0x55, 0x44, 0x22)),
        linked_sprite(2, "StubDirt", 1),
        place(1, 2, "dirt"),
    ])


def gravel_art(w):
    from PIL import Image
    sand = Image.open(ART / "fwa_sand.png")
    sand = sand.resize((w, round(sand.height * w / sand.width)), Image.LANCZOS)
    return tint(sand, SAND_TINT)


def gravel_stub(w, class_name):
    # Gravel.setMCByTankId expects the loaded root to expose a "gravel" child.
    sand = gravel_art(w)
    return swf(w, sand.height, [
        lossless_bitmap(1, sand),
        bitmap_shape(2, 1, 0, 0, sand.width, sand.height),
        linked_sprite(3, class_name, 2),
        place(1, 3, "gravel"),
    ])


def decor_stub(w, h, rgb, class_name):
    # Prop/decor art: the client clones `loadedRoot.decor`.
    return swf(w, h, [
        define_shape_rect(1, 0, 0, w, h, rgb),
        linked_sprite(2, class_name, 1),
        place(1, 2, "decor"),
    ])


def chest_stub(w, h):
    # ChestSprite loops between start_<state> and stop_<state> frame labels
    full, empty, dirty = 1, 2, 3
    frames = []
    for state, shape in (("full", full), ("empty", empty), ("win", full), ("dirty", dirty)):
        frames += [(f"start_{state}", shape), (f"stop_{state}", shape)]
    sprite_id = 4
    abc = tag(82, struct.pack("<I", 1) + bytes(1) + movieclip_subclass_abc("StubChest"))
    symbol = tag(76, struct.pack("<HH", 1, sprite_id) + b"StubChest" + bytes(1))
    return swf(w, h, [
        define_shape_rect(full, -w // 2, -h, w, h, (0xf2, 0xc2, 0x2e)),
        define_shape_rect(empty, -w // 2, -h, w, h, (0x8a, 0x5a, 0x2b)),
        define_shape_rect(dirty, -w // 2, -h, w, h, (0x55, 0x55, 0x44)),
        labelled_sprite(sprite_id, frames), abc, symbol,
        place(1, sprite_id, "chest"),
    ])


LOADING_SIZE = (596, 392)


def loading_image():
    # Shown by the preloader in its frame (img_to_load); the logo covers the top centre
    from PIL import Image
    img = Image.open(ART / "fwa_loading.png").convert("RGB")
    w, h = LOADING_SIZE
    scaled = img.resize((round(img.width * h / img.height), h), Image.LANCZOS)
    left = (scaled.width - w) // 2
    return scaled.crop((left, 0, left + w, h))


def main(assets):
    tank_dir = assets / "swf" / "tank"
    prop_dir = assets / "swf" / "prop"
    tank_dir.mkdir(parents=True, exist_ok=True)
    prop_dir.mkdir(parents=True, exist_ok=True)
    w, h = 760, 520
    (tank_dir / "Tank_Stub.swf").write_bytes(tank_stub(w, h))
    (tank_dir / "Tank_Stub_Dirt.swf").write_bytes(dirt_stub(w, h))
    # Gravel.getTankScaledGravelUrl appends a size suffix to art_url
    for suffix in ("50", "100", "150", "Small", "Medium", "Large"):
        (tank_dir / f"Gravel_Stub{suffix}.swf").write_bytes(gravel_stub(w, f"StubGravel{suffix}"))
    chest_dir = assets / "swf" / "chest"
    chest_dir.mkdir(parents=True, exist_ok=True)
    (chest_dir / "Chest_Stub.swf").write_bytes(chest_stub(60, 45))
    img_dir = assets / "img"
    img_dir.mkdir(parents=True, exist_ok=True)
    loading_image().save(img_dir / "loading.png")
    (prop_dir / "Prop_Gift.swf").write_bytes(decor_stub(40, 40, (0xe0, 0x30, 0x40), "StubGift"))
    print(f"stubs written to {assets / 'swf'}")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "assets")
