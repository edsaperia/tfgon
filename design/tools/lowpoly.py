"""Low-poly UK (Ed, 2026-11-28: "how about more of a low-poly style?").

Run: python3 design/tools/lowpoly.py  -> writes design/marks/shapes/lp-*.svg
A hand-drawn angular outline (exaggerated, not map-accurate) plus a few seeded interior points,
triangulated exactly (ear clipping), interior points split their triangles, then edge flips
(never on the outline) give the varied low-poly facets. Written here to avoid a dependency. Facets use I7's neon set; no two facets
sharing an edge are alike, and colours spread evenly.
"""
import math, pathlib, random
from pixelcaricature import NEON, INK
OUT = pathlib.Path(__file__).resolve().parent.parent / "marks" / "shapes"
PAL = list(NEON.values())

# Outline in a 0-10 box, clockwise from the north of Scotland. Edit freely.
GB = [(4.2, 0.3), (5.5, 0.5), (5.0, 1.8), (5.8, 2.7), (5.0, 3.7), (5.7, 4.7), (6.5, 6.0), (7.6, 7.0),
      (7.1, 8.0), (7.8, 8.6), (5.7, 9.0), (3.7, 9.2), (2.2, 9.9), (3.4, 8.4), (4.5, 8.2), (3.1, 7.6),
      (3.8, 6.7), (3.3, 6.0), (4.4, 5.8), (4.2, 4.8), (3.4, 4.4), (3.6, 3.6), (2.8, 3.0), (3.4, 2.0), (3.0, 1.0)]
NI = [(0.9, 4.0), (2.2, 3.7), (2.5, 4.8), (1.7, 5.4), (0.8, 4.9)]

def inside(p, poly):
    x, y = p; c = False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1: c = not c
    return c

def circum(a, b, c):
    ax, ay = a; bx, by = b; cx, cy = c
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if abs(d) < 1e-12: return (0, 0), float("inf")
    ux = ((ax*ax + ay*ay) * (by - cy) + (bx*bx + by*by) * (cy - ay) + (cx*cx + cy*cy) * (ay - by)) / d
    uy = ((ax*ax + ay*ay) * (cx - bx) + (bx*bx + by*by) * (ax - cx) + (cx*cx + cy*cy) * (bx - ax)) / d
    return (ux, uy), (ax - ux) ** 2 + (ay - uy) ** 2

def delaunay(pts):
    big = [(-100, -100), (100, -100), (0, 100)]
    allp = pts + big; n = len(pts)
    tris = [(n, n + 1, n + 2)]
    for i, p in enumerate(pts):
        bad = []
        for t in tris:
            (ux, uy), r2 = circum(*(allp[k] for k in t))
            if (p[0] - ux) ** 2 + (p[1] - uy) ** 2 < r2: bad.append(t)
        edges = {}
        for t in bad:
            for e in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
                k = tuple(sorted(e)); edges[k] = edges.get(k, 0) + 1
        tris = [t for t in tris if t not in bad] + [(a, b, i) for (a, b), cnt in edges.items() if cnt == 1]
    return [t for t in tris if max(t) < n]

def interior(poly, count, seed, min_d):
    rng = random.Random(seed); xs = [p[0] for p in poly]; ys = [p[1] for p in poly]; out = []
    tries = 0
    while len(out) < count and tries < 5000:
        tries += 1
        p = (rng.uniform(min(xs), max(xs)), rng.uniform(min(ys), max(ys)))
        if inside(p, poly) and all(math.dist(p, q) >= min_d for q in out + poly): out.append(p)
    return out

def ear_clip(poly):
    """Triangulate a simple polygon exactly (covers it, nothing outside)."""
    pts = list(poly)
    area = sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]))
    if area < 0: pts.reverse()          # make it counter-clockwise in maths coordinates
    cross = lambda o, a, b: (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    def in_tri(p, a, b, c):
        return cross(a, b, p) > 0 and cross(b, c, p) > 0 and cross(c, a, p) > 0
    tris = []
    while len(pts) > 3:
        for i in range(len(pts)):
            a, b, c = pts[i - 1], pts[i], pts[(i + 1) % len(pts)]
            if cross(a, b, c) <= 0: continue
            if any(in_tri(q, a, b, c) for q in pts if q not in (a, b, c)): continue
            tris.append((a, b, c)); pts.pop(i); break
        else:
            raise ValueError("ear clipping failed")
    tris.append(tuple(pts))
    return tris

def contains(t, p):
    (ax, ay), (bx, by), (cx, cy) = t
    d1 = (p[0] - bx) * (ay - by) - (ax - bx) * (p[1] - by)
    d2 = (p[0] - cx) * (by - cy) - (bx - cx) * (p[1] - cy)
    d3 = (p[0] - ax) * (cy - ay) - (cx - ax) * (p[1] - ay)
    neg = d1 < 0 or d2 < 0 or d3 < 0; pos = d1 > 0 or d2 > 0 or d3 > 0
    return not (neg and pos)

def mesh(poly, count, seed, min_d):
    """Exact triangulation of the outline, then interior points split their triangles,
    then edge flips (never on the outline) for the varied low-poly look."""
    tris = ear_clip(poly)
    for p in interior(poly, count, seed, min_d):
        for i, t in enumerate(tris):
            if contains(t, p):
                a, b, c = t; tris[i:i + 1] = [(a, b, p), (b, c, p), (c, a, p)]; break
    boundary = {frozenset(e) for e in zip(poly, poly[1:] + poly[:1])}
    for _ in range(60):                 # Lawson flips towards a Delaunay-like mesh
        flipped = False
        for i in range(len(tris)):
            for j in range(i + 1, len(tris)):
                shared = set(tris[i]) & set(tris[j])
                if len(shared) != 2 or frozenset(shared) in boundary: continue
                a, b = shared; c = (set(tris[i]) - shared).pop(); d = (set(tris[j]) - shared).pop()
                (ux, uy), r2 = circum(a, b, c)
                if (d[0] - ux) ** 2 + (d[1] - uy) ** 2 < r2 - 1e-9:
                    # flip only if the quad is convex (the new edge c-d stays inside)
                    cr = lambda o, p1, p2: (p1[0]-o[0])*(p2[1]-o[1]) - (p1[1]-o[1])*(p2[0]-o[0])
                    if (cr(c, d, a) > 0) != (cr(c, d, b) > 0) and (cr(a, b, c) > 0) != (cr(a, b, d) > 0):
                        tris[i] = (c, d, a); tris[j] = (c, d, b); flipped = True
        if not flipped: break
    return tris

def colour(tris, seed):
    rng = random.Random(seed)
    key = lambda p: (round(p[0], 4), round(p[1], 4))
    edges = {}
    for i, t in enumerate(tris):
        for p, q in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
            edges.setdefault(tuple(sorted((key(p), key(q)))), []).append(i)
    nb = {i: set() for i in range(len(tris))}
    for owners in edges.values():
        for i in owners:
            nb[i].update(j for j in owners if j != i)
    order = sorted(range(len(tris)), key=lambda i: (sum(p[1] for p in tris[i]), sum(p[0] for p in tris[i])))
    col = {}; counts = {p: 0 for p in PAL}
    for i in order:
        opts = [p for p in PAL if p not in {col.get(j) for j in nb[i]}] or PAL
        rng.shuffle(opts)
        col[i] = min(opts, key=lambda p: counts[p]); counts[col[i]] += 1
    return col

def svg(count_gb, count_ni, seed, label, min_d):
    tris = mesh(GB, count_gb, seed, min_d) + mesh(NI, count_ni, seed + 1, min_d * 0.8)
    col = colour(tris, seed)
    S, pad = 10.0, 0.6
    xs = [p[0] for t in tris for p in t]; ys = [p[1] for t in tris for p in t]
    w, h = max(xs) - min(xs), max(ys) - min(ys); scale = (S - 2 * pad) / max(w, h)
    ox = (S - w * scale) / 2 - min(xs) * scale; oy = (S - h * scale) / 2 - min(ys) * scale
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {S:g} {S:g}" role="img" aria-label="TFGON mark: {label}">',
           f'  <rect width="{S:g}" height="{S:g}" rx="{S * 0.12:g}" fill="{INK}"/>']
    for i, t in enumerate(tris):
        p = " ".join(f"{x * scale + ox:.3f},{y * scale + oy:.3f}" for x, y in t)
        out.append(f'  <polygon points="{p}" fill="{col[i]}" stroke="{col[i]}" stroke-width="0.02" stroke-linejoin="round"/>')
    out.append("</svg>")
    return "\n".join(out) + "\n", len(tris)

if __name__ == "__main__":
    for name, n_gb, n_ni, seed, d in [("coarse", 4, 0, 3, 1.4), ("medium", 10, 1, 3, 0.9), ("coarse-b", 4, 0, 11, 1.4), ("medium-b", 10, 1, 11, 0.9)]:
        txt, n = svg(n_gb, n_ni, seed, f"low-poly UK, {name}", d)
        (OUT / f"lp-{name}.svg").write_text(txt)
        print(f"lp-{name}: {n} facets")
