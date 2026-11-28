"""I7: the chosen minimal pixel UK (Ed, 2026-11-28): shape a without Scotland's top-left square,
Northern Ireland as three squares (two stacked, one to the east at the top), moved down one row.
Neon colours on the dark tile.

Run: python3 design/tools/i7.py  -> writes design/marks/i7-pixel-minimal.svg and -small.svg
The small version uses 2 px squares with no gaps, so it is pixel-exact at 16 px.
"""
import pathlib
from pixelcaricature import parse, svg, NEON
OUT = pathlib.Path(__file__).resolve().parent.parent / "marks"

SHAPE = """
...#..
..##..
...#..
##.##.
#..###
..##..
"""

if __name__ == "__main__":
    g = parse(SHAPE)
    full, n = svg(g, 1, 8, 0, 1, 5, "minimal pixel UK, neon, on a dark tile", colours=NEON)
    small, _ = svg(g, 2, 16, 0, 1, 5, "minimal pixel UK, neon, on a dark tile, small", colours=NEON)
    (OUT / "i7-pixel-minimal.svg").write_text(full)
    (OUT / "i7-pixel-minimal-small.svg").write_text(small)
    print("squares:", sum(r.count("#") for r in g), n)
