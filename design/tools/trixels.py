"""Trixel versions of I7 (Ed, 2026-11-28: "let's try trixels instead of pixels").

Run: python3 design/tools/trixels.py  -> writes design/marks/shapes/t-*.svg
A: each of I7's squares split into two right triangles (keeps the shape exactly).
B: an equilateral triangle grid (alternating up and down triangles) laid over I7's shape:
   a triangle is in if its centre falls inside one of I7's squares. Diagonal coasts appear by themselves.
Colours: I7's neon set, spread evenly, and no two triangles that share an edge are alike.
"""
import math, pathlib, random
from pixelcaricature import parse, NEON, INK
from i7 import SHAPE
OUT = pathlib.Path(__file__).resolve().parent.parent / "marks" / "shapes"
PAL = list(NEON.values())

def colour(cells, neighbours, seed, radius_fn):
    rng = random.Random(seed); placed = {}
    for cell in cells:
        near = [placed[o] for o in placed if radius_fn(o, cell)]
        touching = {placed.get(n) for n in neighbours(cell)}
        opts = [p for p in PAL if p not in touching] or PAL
        rng.shuffle(opts)
        placed[cell] = min(opts, key=near.count)
    return placed

def wrap(box_w, box_h, polys, label, pad):
    W, H = box_w + 2 * pad, box_h + 2 * pad
    S = max(W, H)
    ox, oy = (S - box_w) / 2, (S - box_h) / 2
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {S:.3f} {S:.3f}" role="img" aria-label="TFGON mark: {label}">',
           f'  <rect width="{S:.3f}" height="{S:.3f}" rx="{S * 0.12:.3f}" fill="{INK}"/>']
    for pts, col in polys:
        # a hairline stroke in the same colour hides the anti-aliasing seams between triangles
        p = " ".join(f"{x + ox:.3f},{y + oy:.3f}" for x, y in pts)
        out.append(f'  <polygon points="{p}" fill="{col}" stroke="{col}" stroke-width="0.02" stroke-linejoin="round"/>')
    out.append("</svg>")
    return "\n".join(out) + "\n"

def split_squares(seed=9, diag="/"):
    g = parse(SHAPE); cells = []
    for r, row in enumerate(g):
        for c, ch in enumerate(row):
            if ch == "#": cells += [(r, c, 0), (r, c, 1)]   # 0 = upper-left half, 1 = lower-right half (for "/")
    sq = {(r, c) for r, c, _ in cells}
    def nb(cell):
        r, c, h = cell
        if h == 0: return [(r, c, 1), (r - 1, c, 1), (r, c - 1, 1)]
        return [(r, c, 0), (r + 1, c, 0), (r, c + 1, 0)]
    placed = colour(cells, nb, seed, lambda a, b: abs(a[0] - b[0]) <= 1 and abs(a[1] - b[1]) <= 1)
    polys = []
    for (r, c, h), col in placed.items():
        pts = [(c, r), (c + 1, r), (c, r + 1)] if h == 0 else [(c + 1, r), (c + 1, r + 1), (c, r + 1)]
        polys.append((pts, col))
    cols = max(len(r) for r in g)
    return wrap(cols, len(g), polys, "trixels A, split squares", 1)

def equilateral(side=1.0, seed=9):
    g = parse(SHAPE)
    inside = lambda x, y: 0 <= int(y) < len(g) and 0 <= int(x) < len(g[int(y)]) and g[int(y)][int(x)] == "#"
    h = side * math.sqrt(3) / 2
    rows = math.ceil(len(g) / h) + 1; cols = math.ceil(max(len(r) for r in g) / (side / 2)) + 2
    tris = {}
    for r in range(rows):
        for c in range(-1, cols):
            up = (r + c) % 2 == 0
            x0 = c * side / 2
            pts = [(x0, (r + 1) * h), (x0 + side / 2, r * h), (x0 + side, (r + 1) * h)] if up else \
                  [(x0, r * h), (x0 + side, r * h), (x0 + side / 2, (r + 1) * h)]
            cx = sum(p[0] for p in pts) / 3; cy = sum(p[1] for p in pts) / 3
            if inside(cx, cy): tris[(r, c)] = (pts, up)
    def nb(cell):
        r, c = cell; up = tris[cell][1]
        return [(r, c - 1), (r, c + 1), (r + 1, c) if up else (r - 1, c)]
    order = sorted(tris)
    placed = colour(order, nb, seed, lambda a, b: abs(a[0] - b[0]) <= 1 and abs(a[1] - b[1]) <= 2)
    xs = [p[0] for pts, _ in tris.values() for p in pts]; ys = [p[1] for pts, _ in tris.values() for p in pts]
    mx, my = min(xs), min(ys)
    polys = [([(x - mx, y - my) for x, y in tris[k][0]], col) for k, col in placed.items()]
    return wrap(max(xs) - mx, max(ys) - my, polys, f"trixels B, equilateral, side {side}", 1)

if __name__ == "__main__":
    (OUT / "t-a-split.svg").write_text(split_squares())
    for s in (1.0, 0.75):
        (OUT / f"t-b-equilateral-{str(s).replace('.', '')}.svg").write_text(equilateral(s))
    print("ok")
