"""Twelve variations on shape 10, "Minimal" (Ed, 2026-11-28: "some variations on 10 please").

Run: python3 design/tools/minimal12.py  -> writes design/marks/shapes/m01.svg ... m12.svg
"""
import pathlib
from pixelcaricature import parse, svg, NEON
OUT = pathlib.Path(__file__).resolve().parent.parent / "marks" / "shapes"

MINIMAL = [
("Minimal (shape 10)", """
.##..
..#..
#.##.
..###
.#...
"""),
("Taller Northern Ireland", """
.##..
..#..
#.##.
#.###
.#...
"""),
("Attached tail", """
.##..
..#..
#.##.
..###
.##..
"""),
("Taller Scotland", """
..#..
.##..
..#..
#.##.
..###
.#...
"""),
("Scotland 2x2", """
.##..
.##..
..#..
#.##.
..###
.#...
"""),
("Wide south", """
.##...
..#...
#.##..
..####
.#....
"""),
("Seven squares", """
.#..
.#..
#.#.
..##
.#..
"""),
("Wider sea", """
..##..
...#..
#..##.
...###
..#...
"""),
("Island dot", """
..#..
.....
.##..
..#..
#.##.
..###
.#...
"""),
("Two-step tail", """
.##...
..#...
#.##..
..###.
.#....
#.....
"""),
("Wales nub", """
.##..
..#..
#.##.
.####
.#...
"""),
("Solid England", """
.##..
..#..
#.##.
.###.
..###
.#...
"""),
]

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for i, (name, grid) in enumerate(MINIMAL, 1):
        g = parse(grid)
        box = max(len(g), max(len(r) for r in g)) + 2
        txt, _ = svg(g, 1, box, 0.14, 1, 5, f"minimal {i}: {name}", colours=NEON)
        (OUT / f"m{i:02d}.svg").write_text(txt)
        print(f"m{i:02d} {name}: {sum(r.count('#') for r in g)} squares")
