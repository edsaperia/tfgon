"""Contrast and colour-blind checks for the TFGON palette drafts.

Run: python3 design/tools/palette_check.py
Contrast: WCAG 2.x relative luminance. Colour-blind simulation: Machado, Oliveira
& Fernandes (2009) matrices at full severity, applied in linear RGB. Pair
distances: CIEDE2000 on the simulated colours.
"""
import itertools, math, sys, json

PALETTES = {
    "old": {"pink": "#EF476F", "yellow": "#FFD166", "green": "#06D6A0", "blue": "#118AB2", "ink": "#393E46"},
    "new": {"pink": "#D33A63", "yellow": "#FFC845", "green": "#34CFA0", "blue": "#2B7FC2",
            "ink": "#1E2A36", "link": "#1D5E99"},
    # Ed, 2026-11-28 (19b): the mark's neon colours become the site's palette.
    "neon": {"pink": "#FF2E88", "yellow": "#FFE41F", "green": "#22F2A0", "blue": "#1EBEFF",
             "ink": "#1E2A36", "link": "#1D5E99"},
}
MACHADO = {
    "protan": [[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]],
    "deutan": [[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]],
    "tritan": [[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.303900]],
}

def rgb(h): h = h.lstrip("#"); return [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
def lin(c): return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
def unlin(c): c = min(1, max(0, c)); return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055
def lum(h): r, g, b = map(lin, rgb(h)); return 0.2126 * r + 0.7152 * g + 0.0722 * b
def contrast(a, b):
    la, lb = sorted([lum(a), lum(b)], reverse=True); return (la + 0.05) / (lb + 0.05)
def grade(r): return "AA" if r >= 4.5 else ("large/shapes" if r >= 3 else "fail")
def simulate(h, kind):
    l = [lin(c) for c in rgb(h)]; m = MACHADO[kind]
    out = [sum(m[i][j] * l[j] for j in range(3)) for i in range(3)]
    return "#" + "".join(f"{round(unlin(c) * 255):02X}" for c in out)
def lab(h):
    r, g, b = map(lin, rgb(h))
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883
    f = lambda t: t ** (1 / 3) if t > 216 / 24389 else (24389 / 27 * t + 16) / 116
    return 116 * f(y) - 16, 500 * (f(x) - f(y)), 200 * (f(y) - f(z))
def de2000(c1, c2):
    L1, a1, b1 = lab(c1); L2, a2, b2 = lab(c2)
    C1, C2 = math.hypot(a1, b1), math.hypot(a2, b2); Cb = (C1 + C2) / 2
    G = 0.5 * (1 - math.sqrt(Cb ** 7 / (Cb ** 7 + 25 ** 7)))
    a1p, a2p = a1 * (1 + G), a2 * (1 + G)
    C1p, C2p = math.hypot(a1p, b1), math.hypot(a2p, b2)
    h1p = math.degrees(math.atan2(b1, a1p)) % 360; h2p = math.degrees(math.atan2(b2, a2p)) % 360
    dLp, dCp = L2 - L1, C2p - C1p
    dhp = 0 if C1p * C2p == 0 else (h2p - h1p if abs(h2p - h1p) <= 180 else h2p - h1p - 360 if h2p > h1p else h2p - h1p + 360)
    dHp = 2 * math.sqrt(C1p * C2p) * math.sin(math.radians(dhp / 2))
    Lbp, Cbp = (L1 + L2) / 2, (C1p + C2p) / 2
    hbp = h1p + h2p if C1p * C2p == 0 else ((h1p + h2p) / 2 if abs(h1p - h2p) <= 180 else (h1p + h2p + 360) / 2 if h1p + h2p < 360 else (h1p + h2p - 360) / 2)
    T = 1 - 0.17 * math.cos(math.radians(hbp - 30)) + 0.24 * math.cos(math.radians(2 * hbp)) + 0.32 * math.cos(math.radians(3 * hbp + 6)) - 0.20 * math.cos(math.radians(4 * hbp - 63))
    Sl = 1 + 0.015 * (Lbp - 50) ** 2 / math.sqrt(20 + (Lbp - 50) ** 2); Sc = 1 + 0.045 * Cbp; Sh = 1 + 0.015 * Cbp * T
    Rt = -2 * math.sqrt(Cbp ** 7 / (Cbp ** 7 + 25 ** 7)) * math.sin(math.radians(60 * math.exp(-((hbp - 275) / 25) ** 2)))
    return math.sqrt((dLp / Sl) ** 2 + (dCp / Sc) ** 2 + (dHp / Sh) ** 2 + Rt * (dCp / Sc) * (dHp / Sh))

def report(name):
    p = PALETTES[name]; ink = p["ink"]; out = {"contrast": [], "sim": {}, "pairs": []}
    print(f"== {name}")
    for k, v in p.items():
        cw, ci = contrast(v, "#FFFFFF"), (contrast(v, ink) if k != "ink" else None)
        out["contrast"].append({"name": k, "hex": v, "white": round(cw, 2), "ink": None if ci is None else round(ci, 2)})
        print(f"  {k:7}{v}  vs white {cw:5.2f} {grade(cw):13}" + ("" if ci is None else f" vs ink {ci:5.2f} {grade(ci)}"))
    brights = ["pink", "yellow", "green", "blue"]
    for kind in ["normal"] + list(MACHADO):
        sims = {c: (p[c] if kind == "normal" else simulate(p[c], kind)) for c in brights}
        out["sim"][kind] = sims
        worst = min(((de2000(sims[a], sims[b]), a, b) for a, b in itertools.combinations(brights, 2)))
        print(f"  {kind:7} {' '.join(sims.values())}  closest pair {worst[1]}/{worst[2]} dE2000={worst[0]:.1f}")
        out["pairs"].append({"vision": kind, "closest": f"{worst[1]}/{worst[2]}", "de": round(worst[0], 1)})
    return out

if __name__ == "__main__":
    res = {n: report(n) for n in PALETTES}
    if "--json" in sys.argv: print(json.dumps(res))
