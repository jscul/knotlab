"""GROW-HANDLE-20261110-001 stress test, one size past ticket A (K_2 to K_4): K_5, every line orbit, placements d = 0 to 5, both
chiralities, every bijection that gives a torus. Reads H1 (two completions, one class), H2 (the grown law the only unsatisfiable class, the
atom acting as the replaced line in it and transparent in the others), whether the extended state is least and where its violated line
sits, and the cheapest resolving walk into each other class. Writes stress_test.json beside this file."""
import importlib.util
import itertools
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if os.environ.get("PYTHONHASHSEED") != "0":
    os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
sys.path.insert(0, str(ROOT / "proofs/GROW-HANDLE-20261110-001A/GROW-HANDLE-20261110-001A-P001_a_fano_atom_grown_at_the_dissonance"))
import grow_lib as G  # noqa: E402
spec = importlib.util.spec_from_file_location("steer_lib", ROOT / "proofs/RESIGN-STEER-20261107-001A/RESIGN-STEER-20261107-001A-P001_re_signing_splits_the_dissonance_and_carries_it_anywhere/steer_lib.py")
L = importlib.util.module_from_spec(spec)
spec.loader.exec_module(L)
SL = G.SL
fano = SL.torus(7, 2, 1)
P = next(t for t in range(fano.nt) if fano.colour[t] == 0)
S = SL.octahedral_sphere(5)
sph = L.Sphere(S, "K_5")
KA, s0 = sph.K, sph.s0
reps, orbit = G.line_orbits(S)
rows, ok = [], True
for l0 in reps:
    x = sph.flat_state(KA.lines.index(l0))
    dist = G.line_distance(S, l0)
    for d in range(6):
        l = l0 if d == 0 else min(t for t, dd in dist.items() if dd == d)
        for chir in (0, 1):
            for sg in itertools.permutations(range(3)):
                g = G.Growth(S, s0, l, fano, P, sg, chir)
                if g.chi != 0:
                    continue
                T = G.GrownTorus(g.G, "K_5+atom", g.completions[0])
                li = KA.lines.index(l)
                own = [p for p in itertools.product((0, 1), repeat=3)
                       if not (p[0] ^ s0[3 * li] == p[1] ^ s0[3 * li + 1] == p[2] ^ s0[3 * li + 2])]
                rel = {lab: g.atom_relation(s) for lab, s in T.classes.items()}
                h1 = len(g.completions) == 2 and len({T.label(c) for c in g.completions}) == 1
                h2 = (T.forced == [T.natural] and sorted(map(tuple, rel[T.natural])) == own
                      and all(len(r) == 8 for lab, r in rel.items() if lab != T.natural))
                s_nat = T.classes[T.natural]
                xg, vmin, ties = g.extend(s_nat, x, KA)
                viol = T.tally(s_nat, xg)[0]
                cost = None
                if vmin == 1:
                    best = []
                    for kk in range(3):
                        s2, f, dg, ll, w0 = T.split(s_nat, xg, kk)
                        for c in T.classes:
                            if c != T.natural:
                                M, cst = T.cheapest_matching(f, c)
                                moves, left = T.realize(f, dg, M)
                                sf, local = T.replay(s2, xg, moves)
                                v2, _, D2, E2 = T.tally(sf, xg)
                                good = not left and local and not v2 and E2 == 0 and not D2
                                ok &= good
                                best.append(1 + len(moves))
                    cost = min(best)
                ok &= h1 and h2 and vmin == 1
                rows.append({"l0": l0, "distance": d, "chirality": chir, "sigma": sg, "H1": h1, "H2": h2, "extension violates": vmin,
                             "violated line in": "atom" if viol and viol[0] in g.atom_lines else "old", "cheapest walk": cost})
    print("line", l0, flush=True)
by = {}
for r in rows:
    by.setdefault(r["distance"], []).append(r["cheapest walk"])
summary = {d: (min(v), max(v), round(sum(v) / len(v), 2)) for d, v in sorted(by.items())}
out = {"sphere": "K_5", "orbits": len(reps), "grown tori": len(rows), "all hold": bool(ok),
       "at the dissonance, violated line in the atom": all(r["violated line in"] == "atom" for r in rows if r["distance"] == 0),
       "cheapest walk (min, max, mean) by distance": summary, "rows": rows}
(HERE / "stress_test.json").write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps({k: v for k, v in out.items() if k != "rows"}))
