"""Writes the hand-editable SVGs for concepts A to C, and the small (16 px) versions.

Run: python3 design/tools/marks.py  (dotmap.py writes concept D's full mark)
Each SVG is plain shapes on a 100 x 100 box. Edit the files directly if you like;
this script only saves typing.
"""
import math, pathlib
PINK, YELLOW, GREEN, BLUE, INK, LIGHT = "#D33A63", "#FFC845", "#34CFA0", "#2B7FC2", "#1E2A36", "#F4F6F8"
OUT = pathlib.Path(__file__).resolve().parent.parent / "marks"

def wrap(label, body, bg=None):
    bgr = f'  <rect width="100" height="100" fill="{bg}"/>\n' if bg else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" role="img" aria-label="TFGON mark: {label}">\n{bgr}{body}</svg>\n'

# A. Four strokes, refreshed: rounded bars in a pinwheel, each overlapping the next.
def pinwheel(thick=18, length=60, tilt=-10, inset=16):
    bar = f'x="{inset}" y="{inset}" width="{length}" height="{thick}" rx="{thick/2}"'
    cols = [GREEN, BLUE, YELLOW, PINK]
    b = f'  <defs><clipPath id="a-corner"><rect x="0" y="0" width="{inset+thick+4}" height="{inset+thick+4}"/></clipPath></defs>\n'
    b += f'  <g transform="rotate({tilt} 50 50)">\n'
    for i, c in enumerate(cols):
        b += f'    <rect {bar} fill="{c}" transform="rotate({90*i} 50 50)"/>\n'
    b += f'    <rect {bar} fill="{cols[0]}" clip-path="url(#a-corner)"/>\n  </g>\n'
    return b

# B. Four leaves meeting at one point.
def leaves(gap=3.5, reach=12):
    cols = [PINK, GREEN, BLUE, YELLOW]
    b = ""
    for i, c in enumerate(cols):
        g = gap
        b += (f'  <path d="M{50-g} {50-g} Q{50-g} {reach} {reach} {reach} Q{reach} {50-g} {50-g} {50-g} Z" '
              f'fill="{c}" transform="rotate({90*i} 50 50)"/>\n')
    return b

def arc(cx, cy, r, a0, a1):
    p = lambda a: (cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
    (x0, y0), (x1, y1) = p(a0), p(a1)
    return f"M{x0:.2f} {y0:.2f} A{r} {r} 0 0 1 {x1:.2f} {y1:.2f}"

def ring(cx, cy, r, w, gapdeg=10):
    cols = [PINK, YELLOW, BLUE, GREEN]  # clockwise from the top-right
    return "".join(f'  <path d="{arc(cx, cy, r, -90 + 90*i + gapdeg/2, -90 + 90*(i+1) - gapdeg/2)}" fill="none" stroke="{c}" stroke-width="{w}"/>\n'
                   for i, c in enumerate(cols))

# C. One map pin, its head a ring of four communities.
def pin(body):
    b = f'  <path d="M50 96 C38 80 18 64 18 40 A32 32 0 1 1 82 40 C82 64 62 80 50 96 Z" fill="{body}"/>\n'
    return b + ring(50, 40, 18, 11, gapdeg=14)

def write(name, txt): (OUT / name).write_text(txt)

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    write("a-four-strokes.svg", wrap("four strokes", pinwheel()))
    write("a-four-strokes-small.svg", wrap("four strokes, small", pinwheel(thick=26, length=64, tilt=0, inset=10)))
    write("b-four-leaves.svg", wrap("four leaves", leaves()))
    write("b-four-leaves-small.svg", wrap("four leaves, small", leaves(gap=5, reach=6)))
    write("c-map-pin.svg", wrap("map pin", pin(INK)))
    write("c-map-pin-on-dark.svg", wrap("map pin, for dark backgrounds", pin(LIGHT)))
    write("c-map-pin-small.svg", wrap("map pin, small", ring(50, 50, 33, 26, gapdeg=16)))
    # D small: the map cannot survive 16 px, so four dots keep its places and colours.
    dots = [(44, 17, GREEN), (66, 42, YELLOW), (28, 70, PINK), (70, 82, BLUE)]
    write("d-dot-map-small.svg", wrap("dot map, small", "".join(f'  <circle cx="{x}" cy="{y}" r="16" fill="{c}"/>\n' for x, y, c in dots)))
    print("ok")
