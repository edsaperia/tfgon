"""Round 2 mark directions (E to H): away from four-equal-colours-round-a-centre.

Run: python3 design/tools/marks2.py  -> writes design/marks/e-*.svg ... h-*.svg
Plain shapes and strokes on a 100 x 100 box. E uses mix-blend-mode: multiply inside
an isolated group, so overlaps mix with each other only, whatever the background.
"""
import pathlib
PINK, YELLOW, GREEN, BLUE, INK, LIGHT = "#D33A63", "#FFC845", "#34CFA0", "#2B7FC2", "#1E2A36", "#F4F6F8"
OUT = pathlib.Path(__file__).resolve().parent.parent / "marks"

def wrap(label, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" role="img" aria-label="TFGON mark: {label}">\n{body}</svg>\n'

def line(x1, y1, x2, y2, c, w, extra=""):
    return f'    <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="{w}" stroke-linecap="round"{extra}/>\n'

# E. Crossing strokes: unequal bars that cross, blended so new tones appear where they meet.
def crossing(scale=1.0):
    w = lambda n: round(n * scale, 1)
    b = '  <g style="isolation:isolate">\n'
    m = ' style="mix-blend-mode:multiply"'
    b += line(24, 76, 72, 26, PINK, w(22), m)      # the dominant stroke
    b += line(28, 38, 80, 60, BLUE, w(16), m)
    b += line(32, 58, 58, 82, YELLOW, w(14), m)
    b += line(58, 18, 78, 32, GREEN, w(10), m)
    return b + "  </g>\n"

# F. Converging threads: four lines start apart and run together into one cable.
def threads(width=6.5, small=False):
    if small:
        starts = [(8, 18), (8, 44), (8, 66), (8, 88)]; end_x, mid = 92, 50
    else:
        starts = [(8, 14), (14, 40), (6, 64), (18, 90)]; end_x, mid = 94, 56
    gap = width + 1.2
    cols = [PINK, YELLOW, GREEN, BLUE]
    b = ""
    for i, ((x, y), c) in enumerate(zip(starts, cols)):
        yy = mid + (i - 1.5) * gap
        b += (f'  <path d="M{x} {y} C{x + 34} {y} 40 {yy} 66 {yy} L{end_x} {yy}" fill="none" '
              f'stroke="{c}" stroke-width="{width}" stroke-linecap="round"/>\n')
    return b

# G. Letter mark: lowercase t, f, g in ink, one crossbar in four unequal colour lengths linking them.
def letters(ink, small=False):
    sw = 13 if small else 10
    b = f'  <g fill="none" stroke="{ink}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">\n'
    b += '    <path d="M22 16 V64 Q22 78 36 78"/>\n'                 # t
    b += '    <path d="M50 82 V36 Q50 18 68 20"/>\n'                 # f
    b += '    <circle cx="80" cy="54" r="11"/>\n'                    # g bowl
    b += '    <path d="M91 46 V84 Q91 96 76 95"/>\n'                 # g tail
    b += '  </g>\n'
    # crossbar: pink dominant, then short yellow, green, blue — the link between letters
    y, h = 38, (12 if small else 9)
    segs = [(8, 44, PINK), (44, 56, YELLOW), (56, 64, GREEN), (64, 72, BLUE)]
    for x0, x1, c in segs:
        b += f'  <rect x="{x0}" y="{y - h/2}" width="{x1 - x0}" height="{h}" fill="{c}"/>\n'
    return b

# H. Constellation: uneven nodes, one dominant, joined by ink lines; no symmetry.
def constellation(ink, small=False):
    if small:
        nodes = [(30, 34, 22, PINK), (76, 26, 13, YELLOW), (70, 76, 16, BLUE)]
        links = [(0, 1), (0, 2)]; lw = 8
    else:
        nodes = [(30, 34, 17, PINK), (76, 20, 8, YELLOW), (80, 66, 11, BLUE), (38, 82, 7, GREEN), (60, 48, 4.5, ink)]
        links = [(0, 4), (1, 4), (2, 4), (0, 3), (3, 2)]; lw = 3.5
    b = ""
    for a, c in links:
        b += f'  <line x1="{nodes[a][0]}" y1="{nodes[a][1]}" x2="{nodes[c][0]}" y2="{nodes[c][1]}" stroke="{ink}" stroke-width="{lw}" stroke-linecap="round"/>\n'
    for x, y, r, c in nodes:
        b += f'  <circle cx="{x}" cy="{y}" r="{r}" fill="{c}"/>\n'
    return b

def write(name, txt): (OUT / name).write_text(txt)

if __name__ == "__main__":
    write("e-crossing-strokes.svg", wrap("crossing strokes", crossing()))
    write("e-crossing-strokes-small.svg", wrap("crossing strokes, small", crossing(1.3)))
    write("f-threads.svg", wrap("converging threads", threads()))
    write("f-threads-small.svg", wrap("converging threads, small", threads(width=11, small=True)))
    write("g-letters.svg", wrap("tfg letters", letters(INK)))
    write("g-letters-on-dark.svg", wrap("tfg letters, for dark backgrounds", letters(LIGHT)))
    write("g-letters-small.svg", wrap("tfg letters, small", letters(INK, small=True)))
    write("g-letters-small-on-dark.svg", wrap("tfg letters, small, for dark backgrounds", letters(LIGHT, small=True)))
    write("h-constellation.svg", wrap("constellation", constellation(INK)))
    write("h-constellation-on-dark.svg", wrap("constellation, for dark backgrounds", constellation(LIGHT)))
    write("h-constellation-small.svg", wrap("constellation, small", constellation(INK, small=True)))
    write("h-constellation-small-on-dark.svg", wrap("constellation, small, for dark backgrounds", constellation(LIGHT, small=True)))
    print("ok")
