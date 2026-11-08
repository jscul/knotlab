"""Writes figure.tex: the rhombus lattice (thick) and its once-cut tiling (thin), for the note."""
from fractions import Fraction as F
from replay import cut

rh = [((0, 0), (0, 2), (1, 0)), ((0, 0), (0, 2), (-1, 0)), ((0, 0), (0, -2), (1, 0)), ((0, 0), (0, -2), (-1, 0))]
tiles = []
for i in range(-3, 4):
    for j in range(-3, 4):
        vx, vy = i + j, 2 * i - 2 * j
        for t in rh:
            tiles.append(tuple((F(p[0] + vx), F(p[1] + vy)) for p in t))
box = (-2, -2.5, 2, 2.5)
inside = lambda t: all(box[0] <= float(p[0]) <= box[2] and box[1] <= float(p[1]) <= box[3] for p in t)
lines = [r"\begin{tikzpicture}[scale=0.95]"]
for t in tiles:
    if not inside(t):
        continue
    for c in cut(t):
        pts = " -- ".join(f"({float(p[0]):.3f},{float(p[1]):.3f})" for p in c)
        lines.append(rf"\draw[gray!70, line width=0.3pt, fill=gray!8] {pts} -- cycle;")
for t in tiles:
    if not inside(t):
        continue
    pts = " -- ".join(f"({float(p[0]):.3f},{float(p[1]):.3f})" for p in t)
    lines.append(rf"\draw[black, line width=0.9pt] {pts} -- cycle;")
lines.append(r"\end{tikzpicture}")
open("figure.tex", "w").write("\n".join(lines) + "\n")
print(len(lines))
