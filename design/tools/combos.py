"""Combinations of minimal 10.3 (attached tail) and 10.5 (Scotland 2x2), with small tweaks
(Ed, 2026-11-28: ".3 and .5 are close"; then "take away the red block in the top left").

Run: python3 design/tools/combos.py  -> writes design/marks/shapes/c-a.svg ... c-f.svg
"""
import pathlib
from pixelcaricature import parse, svg, NEON
OUT = pathlib.Path(__file__).resolve().parent.parent / "marks" / "shapes"

COMBOS = [
("a", "10.3 + 10.5", """
..#..
.##..
..#..
#.##.
..###
.##..
"""),
("b", "+ taller Northern Ireland", """
..#..
.##..
..#..
#.##.
#.###
.##..
"""),
("c", "no waist", """
..#..
.##..
#.##.
..###
.##..
"""),
("d", "longer attached tail", """
...#..
..##..
...#..
#..##.
...###
..##..
.##...
"""),
("e", "wider sea", """
...#..
..##..
...#..
#..##.
...###
..##..
"""),
("f", "wide south", """
..#...
.##...
..#...
#.##..
..####
.##...
"""),
]

if __name__ == "__main__":
    for key, name, grid in COMBOS:
        g = parse(grid)
        box = max(len(g), max(len(r) for r in g)) + 2
        txt, _ = svg(g, 1, box, 0.14, 1, 5, f"combination {key}: {name}", colours=NEON)
        (OUT / f"c-{key}.svg").write_text(txt)
        print(f"c-{key} {name}: {sum(r.count('#') for r in g)} squares")
