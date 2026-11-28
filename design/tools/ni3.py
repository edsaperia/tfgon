"""Combination a with a three-square Northern Ireland, in the arrangements Ed's ":-" might mean (2026-11-28).

Run: python3 design/tools/ni3.py  -> writes design/marks/shapes/n-1.svg ... n-4.svg
"""
import pathlib
from pixelcaricature import parse, svg, NEON
OUT = pathlib.Path(__file__).resolve().parent.parent / "marks" / "shapes"

NI3 = [
("1", "column of three", """
..#..
.##..
#.#..
#.##.
#.###
.##..
"""),
("2", "two stacked, one out to the east at the bottom", """
...#..
..##..
#..#..
##.##.
...###
..##..
"""),
("3", "two stacked, one out to the east at the top", """
...#..
..##..
##.#..
#..##.
...###
..##..
"""),
("4", "a bar of three across", """
....#..
...##..
....#..
###.##.
....###
...##..
"""),
]

if __name__ == "__main__":
    for key, name, grid in NI3:
        g = parse(grid)
        box = max(len(g), max(len(r) for r in g)) + 2
        txt, _ = svg(g, 1, box, 0.14, 1, 5, f"a with a three-square Northern Ireland, {name}", colours=NEON)
        (OUT / f"n-{key}.svg").write_text(txt)
        print(f"n-{key} {name}")
