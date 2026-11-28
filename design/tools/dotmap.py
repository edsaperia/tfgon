"""Builds the dot-map mark (concept D) from a rough outline of the UK.

Run: python3 design/tools/dotmap.py  -> writes design/marks/d-dot-map*.svg
The outline is a hand-traced, deliberately coarse polygon (longitude, latitude).
"""
import math, pathlib
GB = [(-5.0,58.6),(-3.0,58.65),(-3.05,58.4),(-4.0,57.9),(-3.8,57.6),(-2.0,57.7),(-1.8,57.5),(-2.1,57.1),(-2.5,56.6),
(-2.8,56.3),(-3.2,56.05),(-2.0,55.9),(-1.6,55.6),(-1.4,55.0),(-1.2,54.6),(-0.4,54.3),(0.1,53.6),(0.3,53.1),(1.3,52.95),
(1.75,52.6),(1.6,52.1),(1.0,51.8),(0.5,51.5),(1.4,51.35),(1.0,51.0),(0.2,50.75),(-1.0,50.8),(-2.0,50.6),(-3.5,50.6),
(-4.2,50.35),(-5.7,50.05),(-4.5,50.9),(-4.2,51.2),(-3.0,51.2),(-2.7,51.5),(-3.2,51.4),(-4.2,51.55),(-5.2,51.7),(-4.5,52.2),
(-4.1,52.5),(-4.6,52.8),(-4.6,53.3),(-3.1,53.3),(-3.0,53.6),(-3.1,54.1),(-3.6,54.5),(-3.1,54.95),(-4.4,54.8),(-5.1,54.85),
(-4.9,55.4),(-4.9,55.9),(-5.6,55.4),(-5.6,56.3),(-6.2,56.7),(-5.7,57.0),(-5.8,57.6),(-5.1,58.3)]
NI = [(-5.4,54.25),(-5.5,54.65),(-5.9,55.1),(-6.3,55.2),(-7.3,55.2),(-7.6,54.9),(-8.1,54.5),(-7.8,54.2),(-7.0,54.1),(-6.3,54.1)]
# Highlighted dots: rough places, one per colour. Not a claim about who is where.
HI = [((-3.2,55.95),"#34CFA0"),((-2.2,53.48),"#FFC845"),((-3.4,51.6),"#D33A63"),((-0.1,51.5),"#2B7FC2")]
STEP = 0.27  # degrees of latitude between dot rows
K = math.cos(math.radians(54.5))

def inside(pt, poly):
    x, y = pt; c = False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1: c = not c
    return c

def dots():
    out = []
    lat = 58.55
    while lat > 50.0:
        lon = -8.0
        while lon < 1.9:
            if inside((lon, lat), GB) or inside((lon, lat), NI): out.append((lon, lat))
            lon += STEP / K
        lat -= STEP
    return out

def svg(bg=None, base="#1E2A36"):
    ds = dots()
    xs = [d[0] * K for d in ds]; ys = [-d[1] for d in ds]
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    s = 88 / (maxy - miny)
    w = (maxx - minx) * s
    ox, oy = (100 - w) / 2, 6
    P = lambda lon, lat: ((lon * K - minx) * s + ox, (-lat - miny) * s + oy)
    r = STEP * s * 0.34
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" role="img" aria-label="TFGON mark: dot map">']
    if bg: parts.append(f'  <rect width="100" height="100" fill="{bg}"/>')
    parts.append(f'  <g fill="{base}">')
    for lon, lat in ds:
        x, y = P(lon, lat); parts.append(f'    <circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}"/>')
    parts.append('  </g>')
    for (lon, lat), col in HI:
        x, y = P(lon, lat); parts.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="{r*2.6:.2f}" fill="{col}"/>')
    parts.append('</svg>')
    return "\n".join(parts) + "\n", len(ds)

if __name__ == "__main__":
    d = pathlib.Path(__file__).resolve().parent.parent / "marks"; d.mkdir(exist_ok=True)
    txt, n = svg(); (d / "d-dot-map.svg").write_text(txt)
    (d / "d-dot-map-on-dark.svg").write_text(svg(base="#C9D3DD")[0])
    print(n, "dots")
