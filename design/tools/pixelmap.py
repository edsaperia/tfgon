"""Concept I: a pixel-art UK, built on a square grid so it is pixel-perfect at 16 px.

Run: python3 design/tools/pixelmap.py  -> writes design/marks/i-pixel-map*.svg and prints the grids
Each land square is decided by how much of it falls inside the coarse outline in dotmap.py
(supersampled), then the community squares are coloured. One SVG rect per square, crisp edges.
"""
import math, pathlib
from dotmap import GB, NI, inside, K
PINK, YELLOW, GREEN, BLUE, INK, LIGHT = "#D33A63", "#FFC845", "#34CFA0", "#2B7FC2", "#1E2A36", "#C9D3DD"
OUT = pathlib.Path(__file__).resolve().parent.parent / "marks"
# Community squares, as (lon, lat, colour, size in squares). Pink is the big one: unequal on purpose.
COMMS = [(-3.3, 55.9, GREEN, 1), (-2.3, 53.5, YELLOW, 1), (-3.6, 51.8, PINK, 2), (-0.2, 51.6, BLUE, 1)]

def grid(n, lat_top=58.75, lat_bot=49.95, cover=0.45, ss=6):
    cell = (lat_top - lat_bot) / n            # degrees of latitude per square
    cw = cell / K                             # degrees of longitude per square
    lon_l = -8.3
    cols = math.ceil((1.9 - lon_l) / cw)
    g = [[0] * cols for _ in range(n)]
    for r in range(n):
        for c in range(cols):
            hits = 0
            for i in range(ss):
                for j in range(ss):
                    lon = lon_l + (c + (j + .5) / ss) * cw; lat = lat_top - (r + (i + .5) / ss) * cell
                    hits += inside((lon, lat), GB) or inside((lon, lat), NI)
            g[r][c] = 1 if hits / ss / ss >= cover else 0
    to_rc = lambda lon, lat: (int((lat_top - lat) / cell), int((lon - lon_l) / cw))
    return g, to_rc

def svg(n, land, label, extra_fix=None):
    g, to_rc = grid(n)
    if extra_fix: extra_fix(g)
    cols = len(g[0])
    # trim empty columns and centre in an n x n box
    used = [c for c in range(cols) if any(g[r][c] for r in range(n))]
    c0, c1 = min(used), max(used)
    off = (n - (c1 - c0 + 1)) // 2
    colour = {}
    for lon, lat, col, size in COMMS:
        size += 1 if n >= 24 else 0  # bigger squares on the full-size grid
        r, c = to_rc(lon, lat)
        for dr in range(size):
            for dc in range(size):
                colour[(r - dr + (size > 1), c + dc)] = col
    rects = []
    for r in range(n):
        for c in range(c0, c1 + 1):
            if (r, c) in colour: g[r][c] = 1
            if g[r][c]:
                rects.append(f'  <rect x="{c - c0 + off}" y="{r}" width="1" height="1" fill="{colour.get((r, c), land)}"/>')
    ascii_art = "\n".join("".join(("#" if (r, c) not in colour else "o") if g[r][c] else "." for c in range(c0, c1 + 1)) for r in range(n))
    body = "\n".join(rects)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {n} {n}" shape-rendering="crispEdges" role="img" aria-label="TFGON mark: {label}">\n{body}\n</svg>\n', ascii_art)

if __name__ == "__main__":
    for n, name in [(24, "i-pixel-map"), (16, "i-pixel-map-small")]:
        txt, art = svg(n, INK, "pixel map" + (", small" if n == 16 else ""))
        (OUT / f"{name}.svg").write_text(txt)
        (OUT / f"{name}-on-dark.svg").write_text(svg(n, LIGHT, "pixel map, for dark backgrounds")[0])
        print(name); print(art)
