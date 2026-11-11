#!/usr/bin/env python3
"""An independent check of UNATE-20261111-001's parity gadget (research/PARITY-NEEDS-20261111-001/preregistration.md, ticket A).

Fresh code: reads only gadget.json (the rotation system and the signs) and uses no library of the learning line. It rebuilds the incidence
from the rotation system, traces the faces of the map, computes the Euler characteristic and genus, checks that every face is odd (a
Kasteleyn law), enumerates the states satisfying every line, and reads the interface. Then it runs the canonical K1-K3 test
(tools/knotlab, forgetting reading) on every line's relation and on the gadget's relation on its four interface points with the other
points as witnesses.

    PYTHONPATH=tools .venv/bin/python3 -B referee.py"""
import itertools
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from knotlab.knots import check_knot  # noqa: E402
from knotlab.relations import Relation  # noqa: E402

g = json.loads((HERE / "gadget.json").read_text())
rot = g["rotation"]
partner = g["partner"]
signs = g["signs_as_built"]
out = {}

# incidence: line Li's darts in rotation order, each to the point owning its partner dart
lines = []
for i in range(8):
    pts = [partner[d].split(".")[0] for d in rot["L%d" % i]]
    lines.append([int(p[1:]) for p in pts])
deg = [sum(row.count(p) for row in lines) for p in range(8)]
out["every line on three distinct points"] = all(len(set(r)) == 3 for r in lines)
out["every point on three lines"] = deg == [3] * 8
out["lines rebuilt from the rotation"] = lines
out["lines as built (UNATE)"] = g["lines_as_built"]
out["incidence agrees with the build"] = lines == g["lines_as_built"]

# faces of the map: phi(d) = next dart around the vertex of partner(d)
nxt = {}
for v, ds in rot.items():
    for j, d in enumerate(ds):
        nxt[d] = ds[(j + 1) % 3]
darts = [d for ds in rot.values() for d in ds]
seen, faces = set(), []
for d0 in darts:
    if d0 in seen:
        continue
    face, d = [], d0
    while d not in seen:
        seen.add(d)
        face.append(d)
        d = nxt[partner[d]]
    faces.append(face)
V, E, F = 16, 24, len(faces)
chi = V - E + F
out["faces"] = F
out["Euler characteristic"] = chi
out["genus"] = (2 - chi) // 2

# Kasteleyn: at every face, the number of agreeing corners is odd in every state; its parity is the sum over the face's line corners of
# 1 + s(side before) + s(side after), the state cancelling
odd = []
for face in faces:
    par = 0
    for d in face:
        a = partner[d]
        v = a.split(".")[0]
        if v.startswith("L"):
            i = int(v[1:])
            j = rot[v].index(a)
            j2 = (j + 1) % 3
            par += 1 + signs[i][j] + signs[i][j2]
    odd.append(par % 2 == 1)
out["every face odd (Kasteleyn law)"] = all(odd)

# states satisfying every line (NAE on literals x ^ s)
sols = []
for x in itertools.product((0, 1), repeat=8):
    if all(not ((x[p] ^ s0) == (x[q] ^ s1) == (x[r] ^ s2)) for (p, q, r), (s0, s1, s2) in zip(lines, signs)):
        sols.append(x)
ins, o = g["interface"]["inputs"], g["interface"]["output"]
proj = sorted({tuple(x[p] for p in ins) + (x[o],) for x in sols})
out["satisfying states"] = len(sols)
out["interface relation (inputs, output)"] = proj
out["output is the parity of the inputs at every input pattern"] = (len(proj) == 8 and all(r[3] == (r[0] ^ r[1] ^ r[2]) for r in proj))

# the canonical K1-K3 test
def lit(p, s):
    return ("~P%d" % p) if s else ("P%d" % p)
def cnf_of(rows):
    cl = []
    for (p, q, r), (s0, s1, s2) in rows:
        cl.append(" ".join([lit(p, s0), lit(q, s1), lit(r, s2)]))
        cl.append(" ".join([lit(p, 1 - s0), lit(q, 1 - s1), lit(r, 1 - s2)]))
    return cl
line_knots = []
for (p, q, r), sg in zip(lines, signs):
    rel = Relation.from_cnf(cnf_of([((p, q, r), sg)]), ["P%d" % p, "P%d" % q, "P%d" % r], [])
    rep = check_knot(rel, ["P%d" % p, "P%d" % q], "P%d" % r)
    line_knots.append(rep.is_knot)
out["every line is a knot by K1-K3"] = all(line_knots)
names = ["P%d" % p for p in ins] + ["P%d" % o]
wit = ["P%d" % p for p in range(8) if p not in ins + [o]]
rel = Relation.from_cnf(cnf_of(list(zip(lines, signs))), names, wit)
rep = check_knot(rel, names[:3], names[3])
out["interface relation, other points as witnesses: K1 binding, K2 loss on erasure, K3 coexistence"] = [rep.binding, rep.loss_on_erasure, rep.coexistence]
out["interface relation is a knot by K1-K3"] = rep.is_knot
print(json.dumps(out, indent=1, default=str))
ok = all(out[k] for k in ("every line on three distinct points", "every point on three lines", "incidence agrees with the build",
                          "every face odd (Kasteleyn law)", "output is the parity of the inputs at every input pattern",
                          "every line is a knot by K1-K3", "interface relation is a knot by K1-K3")) and out["genus"] == 4
(HERE / "referee.json").write_text(json.dumps({"passed": ok, "checks": out}, indent=1, default=str) + "\n")
print("REFEREE PASSED" if ok else "REFEREE FAILED")
