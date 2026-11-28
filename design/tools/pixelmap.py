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


# I2 and I3: every land square is coloured (Ed, 2026-11-27: "the whole country made of the colourful pixels").
SEATS = [(-3.3, 55.9, GREEN), (-2.3, 53.5, YELLOW), (-3.6, 51.8, PINK), (-0.2, 51.6, BLUE)]

def coloured(n, mode, label):
    import random
    g, to_rc = grid(n)
    cols = len(g[0])
    used = [c for c in range(cols) if any(g[r][c] for r in range(n))]
    c0, c1 = min(used), max(used); off = (n - (c1 - c0 + 1)) // 2
    seats = [(to_rc(lon, lat), col) for lon, lat, col in SEATS]
    rng = random.Random(7)  # fixed seed: the same mosaic every run
    palette = [PINK] * 4 + [BLUE] * 3 + [GREEN] * 2 + [YELLOW] * 2  # pink leads, not four equal shares
    rects, prev_row = [], {}
    for r in range(n):
        row = {}
        for c in range(c0, c1 + 1):
            if not g[r][c]: continue
            if mode == "regions":   # nearest community: the map split into each one's patch
                col = min(seats, key=lambda s: (s[0][0] - r) ** 2 + (s[0][1] - c) ** 2)[1]
            else:                   # mosaic: random, but never the same as the square to the left or above
                avoid = {row.get(c - 1), prev_row.get(c)}
                col = rng.choice([p for p in palette if p not in avoid])
            row[c] = col
            rects.append(f'  <rect x="{c - c0 + off}" y="{r}" width="1" height="1" fill="{col}"/>')
        prev_row = row
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {n} {n}" shape-rendering="crispEdges" role="img" aria-label="TFGON mark: {label}">\n' + "\n".join(rects) + "\n</svg>\n"

def write_coloured():
    for mode, slug in [("regions", "i2-pixel-regions"), ("mosaic", "i3-pixel-mosaic")]:
        (OUT / f"{slug}.svg").write_text(coloured(24, mode, f"pixel {mode}"))
        (OUT / f"{slug}-small.svg").write_text(coloured(16, mode, f"pixel {mode}, small"))

if __name__ == "__main__":
    write_coloured()


# I4: the mosaic with larger squares, colours spread evenly, on a dark tile (Ed, 2026-11-27).
def even_mosaic(rows, box, label, gap=0.0, radius=2, seed=3):
    """Map on `rows` squares, centred in a `box` x `box` dark tile.
    Each square takes the colour least used among squares already placed within `radius`
    (ties broken by a fixed-seed shuffle), so all four colours spread evenly, in equal shares,
    and no two touching squares match."""
    import random
    rng = random.Random(seed)
    g, _ = grid(rows)
    cols = len(g[0])
    used = [c for c in range(cols) if any(g[r][c] for r in range(rows))]
    c0, c1 = min(used), max(used)
    ox = (box - (c1 - c0 + 1)) / 2; oy = (box - rows) / 2
    placed = {}
    pal = [PINK, YELLOW, GREEN, BLUE]
    for r in range(rows):
        for c in range(c0, c1 + 1):
            if not g[r][c]: continue
            near = [placed[(rr, cc)] for (rr, cc) in placed if abs(rr - r) <= radius and abs(cc - c) <= radius]
            touching = {placed.get((r, c - 1)), placed.get((r - 1, c)), placed.get((r - 1, c - 1)), placed.get((r - 1, c + 1))}
            opts = [p for p in pal if p not in touching] or pal
            rng.shuffle(opts)
            placed[(r, c)] = min(opts, key=lambda p: near.count(p))
    s = 1 - gap
    rects = [f'  <rect x="{c - c0 + ox + gap/2:g}" y="{r + oy + gap/2:g}" width="{s:g}" height="{s:g}" fill="{col}"/>' for (r, c), col in placed.items()]
    tile = f'  <rect width="{box}" height="{box}" rx="{box * 0.12:g}" fill="{INK}"/>'
    counts = {p: list(placed.values()).count(p) for p in pal}
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {box} {box}" shape-rendering="crispEdges" role="img" aria-label="TFGON mark: {label}">\n{tile}\n' + "\n".join(rects) + "\n</svg>\n", counts)

if __name__ == "__main__":
    full, n1 = even_mosaic(16, 19, "even pixel mosaic on a dark tile", gap=0.12)
    small, n2 = even_mosaic(14, 16, "even pixel mosaic on a dark tile, small")
    (OUT / "i4-pixel-mosaic-tile.svg").write_text(full)
    (OUT / "i4-pixel-mosaic-tile-small.svg").write_text(small)
    print("I4 colour counts, full:", n1, "small:", n2)
