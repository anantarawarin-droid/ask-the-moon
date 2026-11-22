#!/usr/bin/env python3
"""Build small /tarot/{id}-thumb.webp files for the meanings index and own-cards picker.

Displayed at 150×~259. Each thumb is at most 300px tall (~2× or slightly under),
with quality tuned so the file lands around 5–10 KB.
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "static" / "tarot"
MAX_H = 300
TARGET = 10 * 1024
FLOOR = 5 * 1024
QMIN, QMAX = 35, 85
HEIGHTS = (300, 280, 260, 240, 220, 200)


def encode(resized: Image.Image, quality: int) -> bytes:
    buf = io.BytesIO()
    resized.save(buf, "WEBP", quality=quality, method=6)
    return buf.getvalue()


def fit(im: Image.Image) -> tuple[bytes, int, int, int]:
    """Return (bytes, width, height, quality) in the 5–10 KB band if possible."""
    w0, h0 = im.size
    best_over: tuple[bytes, int, int, int] | None = None
    for height in HEIGHTS:
        width = max(1, round(w0 * height / h0))
        resized = im.resize((width, height), Image.Resampling.LANCZOS)
        lo, hi = QMIN, QMAX
        chosen: tuple[bytes, int, int, int] | None = None
        while lo <= hi:
            mid = (lo + hi) // 2
            data = encode(resized, mid)
            if len(data) <= TARGET:
                chosen = (data, width, height, mid)
                lo = mid + 1
            else:
                if best_over is None or len(data) < len(best_over[0]):
                    best_over = (data, width, height, mid)
                hi = mid - 1
        if chosen is not None:
            # Prefer a size that is not far below 5 KB when the card is simple.
            if len(chosen[0]) < FLOOR and chosen[3] < QMAX:
                data = encode(resized, QMAX)
                if len(data) <= TARGET:
                    chosen = (data, width, height, QMAX)
            return chosen
    # Busy art: smallest file we could make (lowest height, qmin).
    assert best_over is not None
    return best_over


def main() -> int:
    srcs = sorted(p for p in SRC.glob("*.webp") if not p.name.endswith("-thumb.webp"))
    if len(srcs) != 78:
        print(f"expected 78 full card images, found {len(srcs)}", file=sys.stderr)
        return 1
    sizes = []
    for src in srcs:
        dest = SRC / f"{src.stem}-thumb.webp"
        with Image.open(src) as im:
            data, w, h, q = fit(im.convert("RGB"))
        dest.write_bytes(data)
        sizes.append(len(data))
        print(f"{dest.name:24} {w}x{h}  q={q:2d}  {len(data):5d} B")
    print(
        f"\n{len(sizes)} thumbs  total={sum(sizes)}  "
        f"min={min(sizes)} avg={sum(sizes)//len(sizes)} max={max(sizes)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
