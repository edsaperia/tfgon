"""Concept I5: a caricature of the UK in big pixel squares, near-equal colour values, on a dark tile.

Run: python3 design/tools/pixelcaricature.py
The shapes are drawn by hand below ('#' = a square): exaggerated, not map-accurate.
Edit the grids directly to change the shape.
"""
import pathlib, random
OUT = pathlib.Path(__file__).resolve().parent.parent / "marks"
INK = "#1E2A36"
# Near-equal value: each retuned colour moved towards one lightness, keeping its hue (see equal_value.py).
COLOURS = {"pink": "#FF6285", "yellow": "#E1AB00", "green": "#06B98C", "blue": "#009FF9"}  # L* 63, 73, 67, 63, at the most saturated sRGB allows

FULL = """
.....##....
....####...
...####....
....###....
.....##....
##....##...
##....###..
......####.
.....#####.
...#######.
...#######.
.....######
...#####...
..##.......
"""
SMALL = """
...##..
..###..
#..##..
#...##.
...####
..####.
.##....
"""

def parse(s): return [list(r) for r in s.strip("\n").split("\n")]

# I6's own shape (Ed, 2026-11-27: "simpler and more angular"): straight runs and clean diagonal steps.
FULL6 = """
..###....
..###....
...##....
...###...
#...###..
#...####.
...#####.
..######.
.##......
"""
SMALL6 = """
..##....
..##....
...##...
#..###..
#..####.
..##....
"""

# I6: "almost neon" (Ed, 2026-11-27). Brighter and fully saturated; values spread again (L* 57 to 90).
NEON = {"pink": "#FF2E88", "yellow": "#FFE41F", "green": "#22F2A0", "blue": "#1EBEFF"}

def colour_squares(g, radius, seed, colours=None):
    rng = random.Random(seed); pal = list((colours or COLOURS).values()); placed = {}
    for r, row in enumerate(g):
        for c, ch in enumerate(row):
            if ch != "#": continue
            near = [v for (rr, cc), v in placed.items() if abs(rr - r) <= radius and abs(cc - c) <= radius]
            touching = {placed.get((r, c - 1)), placed.get((r - 1, c)), placed.get((r - 1, c - 1)), placed.get((r - 1, c + 1))}
            opts = [p for p in pal if p not in touching] or pal
            rng.shuffle(opts)
            placed[(r, c)] = min(opts, key=near.count)
    return placed

def svg(g, unit, box, gap, radius, seed, label, tile=True, colours=None):
    rows, cols = len(g), max(len(r) for r in g)
    ox, oy = (box - cols * unit) / 2, (box - rows * unit) / 2
    placed = colour_squares(g, radius, seed, colours)
    s = unit - gap
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {box} {box}" shape-rendering="crispEdges" role="img" aria-label="TFGON mark: {label}">']
    if tile: parts.append(f'  <rect width="{box}" height="{box}" rx="{box * 0.12:g}" fill="{INK}"/>')
    for (r, c), col in placed.items():
        parts.append(f'  <rect x="{ox + c * unit + gap / 2:g}" y="{oy + r * unit + gap / 2:g}" width="{s:g}" height="{s:g}" fill="{col}"/>')
    parts.append("</svg>")
    counts = {k: list(placed.values()).count(v) for k, v in (colours or COLOURS).items()}
    return "\n".join(parts) + "\n", counts

if __name__ == "__main__":
    full, n1 = svg(parse(FULL), 1, 16, 0.14, 1, 5, "pixel caricature on a dark tile")
    small, n2 = svg(parse(SMALL), 2, 16, 0, 1, 5, "pixel caricature on a dark tile, small")  # 2 px squares at 16 px
    (OUT / "i5-pixel-caricature.svg").write_text(full)
    (OUT / "i5-pixel-caricature-small.svg").write_text(small)
    print("counts full", n1, "small", n2)
    full6, _ = svg(parse(FULL6), 1, 11, 0.14, 1, 5, "pixel caricature, neon, on a dark tile", colours=NEON)
    small6, _ = svg(parse(SMALL6), 2, 16, 0, 1, 5, "pixel caricature, neon, on a dark tile, small", colours=NEON)
    (OUT / "i6-pixel-neon.svg").write_text(full6)
    (OUT / "i6-pixel-neon-small.svg").write_text(small6)
