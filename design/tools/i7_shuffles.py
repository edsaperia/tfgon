"""Colour shuffles of I7 (Ed, 2026-11-28: "show me different shuffles of the colours").

Run: python3 design/tools/i7_shuffles.py  -> writes design/marks/shapes/i7-shuffle-01.svg ... -12.svg
Same shape and rules as I7 (no two touching squares alike, near-equal shares); only the seed changes.
Duplicate colourings are skipped. Each file records its seed.
"""
import pathlib
from pixelcaricature import parse, svg, colour_squares, NEON
from i7 import SHAPE
OUT = pathlib.Path(__file__).resolve().parent.parent / "marks" / "shapes"

if __name__ == "__main__":
    g = parse(SHAPE); seen = set(); found = []
    seed = 0
    while len(found) < 12:
        seed += 1
        key = tuple(sorted(colour_squares(g, 1, seed, NEON).items()))
        if key in seen: continue
        seen.add(key); found.append(seed)
    for i, sd in enumerate(found, 1):
        full, _ = svg(g, 1, 8, 0, 1, sd, f"I7 colour shuffle {i} (seed {sd})", colours=NEON)
        small, _ = svg(g, 2, 16, 0, 1, sd, f"I7 colour shuffle {i} (seed {sd}), small", colours=NEON)
        (OUT / f"i7-shuffle-{i:02d}.svg").write_text(full)
        (OUT / f"i7-shuffle-{i:02d}-small.svg").write_text(small)
    print("seeds:", found)
