#!/usr/bin/env python3
"""Build optimized Ask the Moon oracle card images and a shared navy/gold card back.

Full cards: 480px wide WebP (RGBA, quality tuned ~30–50 KB).
Thumbs: ~300px tall, 5–12 KB, for the /oracle index.
Card back: same frame language as the deck, used by the face-down pick UI.
"""
from __future__ import annotations

import io
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SRC = Path("/workspace/deck/cards-web")
DEST = ROOT / "static" / "oracle"
FULL_W = 480
THUMB_H = 300
FULL_TARGET = 48 * 1024
THUMB_TARGET = 10 * 1024
THUMB_FLOOR = 5 * 1024


def encode_rgba(im: Image.Image, quality: int) -> bytes:
    buf = io.BytesIO()
    im.save(buf, "WEBP", quality=quality, method=6)
    return buf.getvalue()


def tune(im: Image.Image, target: int, qmin=55, qmax=82, floor=0) -> tuple[bytes, int]:
    lo, hi = qmin, qmax
    chosen = None
    smallest = None
    while lo <= hi:
        mid = (lo + hi) // 2
        data = encode_rgba(im, mid)
        if smallest is None or len(data) < len(smallest[0]):
            smallest = (data, mid)
        if len(data) <= target:
            chosen = (data, mid)
            lo = mid + 1
        else:
            hi = mid - 1
    if chosen is None:
        return smallest
    if floor and len(chosen[0]) < floor and chosen[1] < qmax:
        data = encode_rgba(im, qmax)
        if len(data) <= target:
            chosen = (data, qmax)
    return chosen


def make_back(size: tuple[int, int]) -> Image.Image:
    """Navy field, gold double frame, red fan from a real card, gold crescent."""
    w, h = size
    src = Image.open(SRC / "01.webp").convert("RGBA")
    # Scale source to the target size so ornaments line up.
    base = src.resize((w, h), Image.Resampling.LANCZOS)
    px = base.load()
    # Keep the ornate gold frame / red fan; fill the inner field with starry navy.
    # Sample a few inner pixels to find the text field: inside the gold border.
    inset_x, inset_y = int(w * 0.09), int(h * 0.08)
    field = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    fd = ImageDraw.Draw(field)
    # Radial navy-blue glow, darker at edges.
    for y in range(inset_y, h - inset_y):
        for x in range(inset_x, w - inset_x):
            r, g, b, a = px[x, y]
            # Keep strong gold and the red fan (high red vs green, or bright gold).
            is_red = r > g * 1.55 and r > 80 and r > b
            is_gold = r > 140 and g > 100 and b < 140 and r - b > 40 and (r + g) > 260
            # Also keep near-edge frame by skipping far-inside only when not ornament.
            if is_red or is_gold:
                continue
            # Distance from center for starfield glow
            nx = (x - w / 2) / (w * 0.45)
            ny = (y - h / 2) / (h * 0.42)
            d = math.sqrt(nx * nx + ny * ny)
            glow = max(0.0, 1 - d)
            pr = int(8 + 18 * glow)
            pg = int(12 + 36 * glow)
            pb = int(28 + 90 * glow)
            field.putpixel((x, y), (pr, pg, pb, a))
    # Soft stars
    import random
    rng = random.Random(37)
    star = ImageDraw.Draw(field)
    for _ in range(90):
        x = rng.randint(inset_x + 8, w - inset_x - 8)
        y = rng.randint(inset_y + 8, h - inset_y - 8)
        r0, g0, b0, a0 = field.getpixel((x, y))
        if a0 < 200 or (r0 > 140 and g0 > 100):
            continue
        rad = 0.6 + rng.random() * 1.4
        col = (243, 226, 168, int(80 + rng.random() * 140)) if rng.random() > 0.75 else (255, 255, 255, int(70 + rng.random() * 120))
        star.ellipse((x - rad, y - rad, x + rad, y + rad), fill=col)
    out = base.copy()
    out.alpha_composite(field)

    # Gold crescent moon in the center.
    moon = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    md = ImageDraw.Draw(moon)
    cx, cy = w / 2, h * 0.52
    rad = w * 0.16
    # Outer disc
    md.ellipse((cx - rad, cy - rad, cx + rad, cy + rad), fill=(243, 226, 168, 235))
    # Subtract inner disc for crescent
    hole = Image.new("L", (w, h), 0)
    hd = ImageDraw.Draw(hole)
    hd.ellipse((cx - rad, cy - rad, cx + rad, cy + rad), fill=255)
    hx, hy = cx + rad * 0.38, cy - rad * 0.08
    hr = rad * 0.82
    sub = Image.new("L", (w, h), 0)
    ImageDraw.Draw(sub).ellipse((hx - hr, hy - hr, hx + hr, hy + hr), fill=255)
    # crescent alpha = outer minus inner
    from PIL import ImageChops
    cres = ImageChops.subtract(hole, sub)
    # gold fill
    gold = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gold)
    gd.ellipse((cx - rad - 2, cy - rad - 2, cx + rad + 2, cy + rad + 2), fill=(212, 175, 55, 255))
    # slightly lighter inner
    glow_g = Image.new("RGBA", (w, h), (243, 226, 168, 255))
    gold = Image.composite(glow_g, gold, cres)
    gold.putalpha(cres.point(lambda v: int(v * 0.95)))
    # soft shadow
    sh = gold.split()[-1].filter(ImageFilter.GaussianBlur(6))
    shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    shadow.putalpha(sh.point(lambda v: int(v * 0.55)))
    out.alpha_composite(shadow, (3, 5))
    out.alpha_composite(gold)
    return out


def main() -> int:
    DEST.mkdir(parents=True, exist_ok=True)
    srcs = sorted(SRC.glob("*.webp"))
    if len(srcs) != 37:
        print(f"expected 37 source cards, found {len(srcs)}", file=sys.stderr)
        return 1
    full_sizes, thumb_sizes = [], []
    for src in srcs:
        n = src.stem  # 01 .. 37
        with Image.open(src) as im:
            im = im.convert("RGBA")
            w0, h0 = im.size
            w = FULL_W
            h = max(1, round(h0 * w / w0))
            full = im.resize((w, h), Image.Resampling.LANCZOS)
        data, q = tune(full, FULL_TARGET, qmin=62, qmax=84)
        (DEST / f"oracle-{n}.webp").write_bytes(data)
        full_sizes.append(len(data))
        tw = max(1, round(w0 * THUMB_H / h0))
        thumb = full.resize((tw, THUMB_H), Image.Resampling.LANCZOS) if full.size[1] != THUMB_H else full
        # resize from original for quality
        with Image.open(src) as im:
            thumb = im.convert("RGBA").resize((tw, THUMB_H), Image.Resampling.LANCZOS)
        tdata, tq = tune(thumb, THUMB_TARGET, qmin=40, qmax=80, floor=THUMB_FLOOR)
        (DEST / f"oracle-{n}-thumb.webp").write_bytes(tdata)
        thumb_sizes.append(len(tdata))
        print(f"oracle-{n}: full {w}x{h} q={q} {len(data):5d}B  thumb {tw}x{THUMB_H} q={tq} {len(tdata):5d}B")

    # Card back at full and thumb sizes (match first card).
    with Image.open(srcs[0]) as im:
        w0, h0 = im.size
    back_full = make_back((FULL_W, max(1, round(h0 * FULL_W / w0))))
    bdata, bq = tune(back_full, FULL_TARGET, qmin=62, qmax=84)
    (DEST / "card-back.webp").write_bytes(bdata)
    tw = max(1, round(w0 * THUMB_H / h0))
    back_thumb = back_full.resize((tw, THUMB_H), Image.Resampling.LANCZOS)
    tdata, tq = tune(back_thumb, THUMB_TARGET, qmin=40, qmax=80, floor=THUMB_FLOOR)
    (DEST / "card-back-thumb.webp").write_bytes(tdata)
    print(f"card-back: full {back_full.size} q={bq} {len(bdata)}B  thumb q={tq} {len(tdata)}B")
    print(
        f"\n37 full  total={sum(full_sizes)} min={min(full_sizes)} avg={sum(full_sizes)//37} max={max(full_sizes)}"
    )
    print(
        f"37 thumbs total={sum(thumb_sizes)} min={min(thumb_sizes)} avg={sum(thumb_sizes)//37} max={max(thumb_sizes)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
