"""Equal-value versions of the four brights, for the pixel mosaic (Ed, 2026-11-27: "make the value of the colours more equal").

Run: python3 design/tools/equal_value.py
For each retuned colour, keep its hue (CIE LCh) and move it to one shared lightness L*,
with the strongest chroma that stays inside sRGB. Prints old and new L* and hex.
"""
import math
from palette_check import lab, contrast

def lab_to_hex(L, a, b):
    fy = (L + 16) / 116; fx = fy + a / 500; fz = fy - b / 200
    finv = lambda t: t ** 3 if t ** 3 > 216 / 24389 else (116 * t - 16) / (24389 / 27)
    X, Y, Z = finv(fx) * 0.95047, finv(fy), finv(fz) * 1.08883
    r = 3.2406 * X - 1.5372 * Y - 0.4986 * Z
    g = -0.9689 * X + 1.8758 * Y + 0.0415 * Z
    bb = 0.0557 * X - 0.2040 * Y + 1.0570 * Z
    out = []
    for c in (r, g, bb):
        if c < -1e-4 or c > 1 + 1e-4: return None
        c = min(1, max(0, c))
        out.append(12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055)
    return "#" + "".join(f"{round(c * 255):02X}" for c in out)

def equalise(hexes, L):
    res = {}
    for name, hx in hexes.items():
        _, a, b = lab(hx); h = math.atan2(b, a)
        best = None
        for C in [x / 2 for x in range(0, 300)]:
            hx2 = lab_to_hex(L, C * math.cos(h), C * math.sin(h))
            if hx2: best = hx2
            else: break
        res[name] = best
    return res

RETUNED = {"pink": "#D33A63", "yellow": "#FFC845", "green": "#34CFA0", "blue": "#2B7FC2"}
TARGET_L = 64

if __name__ == "__main__":
    new = equalise(RETUNED, TARGET_L)
    for k in RETUNED:
        print(f"{k:7} {RETUNED[k]} L*={lab(RETUNED[k])[0]:5.1f}  ->  {new[k]} L*={lab(new[k])[0]:5.1f}  vs ink {contrast(new[k], '#1E2A36'):.2f}:1")
