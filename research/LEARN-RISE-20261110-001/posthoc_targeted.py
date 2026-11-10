"""LEARN-RISE-20261110-001, post hoc (not pre-registered; the frozen breadth-first search stopped at its cap everywhere): a targeted search
for the same question. For each start, a target is chosen first: a class in which atom 0 acts as its line and atom 1 is transparent, and a
floor state of that law with the unit inside atom 0, found by SAT. Then a best-first search over the same moves (state flips and learning
steps at A26 sites, W <= floor + 2) expands the configuration closest to the target in Hamming distance (law bits plus state bits), and
stops at the first floor configuration with the unit inside atom 0, or after 300,000 configurations. Writes posthoc_targeted.json."""
import heapq
import importlib.util
import itertools
import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if os.environ.get("PYTHONHASHSEED") != "0":
    os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})


def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


C = load("rise_check", "proofs/LEARN-RISE-20261110-001A/LEARN-RISE-20261110-001A-P001_swapping_the_atoms_roles/check.py")
LL = load("layers_lib", "proofs/ATOM-LAYERS-20261110-001A/ATOM-LAYERS-20261110-001A-P001_where_a_dissonance_sits_among_atoms/layers_lib.py")
LH = load("law_holds", "proofs/LAW-HOLDS-20261110-001A/LAW-HOLDS-20261110-001A-P001_host_faces_by_sign_class/check.py")
L = load("steer_lib", "proofs/RESIGN-STEER-20261107-001A/RESIGN-STEER-20261107-001A-P001_re_signing_splits_the_dissonance_and_carries_it_anywhere/steer_lib.py")
ST, SL = LL.ST, LL.SL
T0 = time.time()


def floor_model(K, s, v):
    from pysat.card import CardEnc, EncType
    from pysat.solvers import Solver
    cl, top, g = list(K.clauses(s)), K.n, {}
    for w in range(K.V):
        for (i, c) in K.corners_at[w]:
            top += 1
            g[(i, c)] = top
            a, b = LH.lit(K, s, i, (c + 1) % 3), LH.lit(K, s, i, (c + 2) % 3)
            cl += [[-top, -a, b], [-top, a, -b], [top, a, b], [top, -a, -b]]
    for w in range(K.V):
        gs = [g[(i, c)] for (i, c) in K.corners_at[w]]
        enc = (CardEnc.atleast if w == v else CardEnc.atmost)(lits=gs, bound=2 if w == v else 1, top_id=top, encoding=EncType.seqcounter)
        top = max(top, enc.nv)
        cl += enc.clauses
    with Solver(name="cadical153", bootstrap_with=cl) as so:
        if not so.solve():
            return None
        m = so.get_model()
    return [int(m[p] > 0) for p in range(K.n)]


rows = []
for kk, orbits in ((2, None), (3, 1)):
    S = SL.octahedral_sphere(kk)
    sph = L.Sphere(S, f"K_{kk}")
    reps, _ = ST.G.line_orbits(S)
    for l0 in reps[:orbits] if orbits else reps:
        dist = ST.G.line_distance(S, l0)
        at = {d: min(t for t, dd in dist.items() if dd == d) for d in (1, 2, 3)}
        x0 = sph.flat_state(sph.K.lines.index(l0))
        for d in (1, 2, 3):
            Y = LL.Layered(S, sph.s0, x0)
            Y.grow(l0)
            Y.grow(at[d])
            Y.learn(4)
            K = Y.K()
            P = C.Space(K, Y.S)
            levels = [Y.face_level(v) for v in range(K.V)]
            floor2 = abs(K.chi)
            target = None
            for a in itertools.product((0, 1), repeat=4):
                s = list(Y.s)
                for ai, z in zip(a, K.classes()):
                    if ai:
                        s = [u ^ w for u, w in zip(s, z)]
                if [LH.atom_role(K, Y, s, j) for j in (0, 1)] != ["line", "transparent"]:
                    continue
                for v in range(K.V):
                    if levels[v] == "atom 0" and K.d[v] >= 3:
                        xm = floor_model(K, s, v)
                        if xm is not None:
                            target = (sum(b << e for e, b in enumerate(s)), sum(b << p for p, b in enumerate(xm)))
                            break
                if target:
                    break
            s0i = sum(b << e for e, b in enumerate(Y.s))
            x0i = sum(b << p for p, b in enumerate(Y.x))

            def h(s, x):
                return bin(s ^ target[0]).count("1") + bin(x ^ target[1]).count("1")
            start = (s0i, x0i)
            prev, heap, found = {start: None}, [(h(*start), 0, start)], None
            tick = 0
            while heap and len(prev) < 300000:
                _, _, (s, x) = heapq.heappop(heap)
                vi, ag, w = P.full(s, x)
                if w == floor2 and any(ag[v] == 3 and levels[v] == "atom 0" for v in range(K.V)):
                    found = (s, x)
                    break
                for kind, t, y, w2 in P.neighbours(s, x, vi, ag, w):
                    if w2 <= floor2 + 4 and (t, y) not in prev:
                        prev[(t, y)] = ((s, x), kind)
                        tick += 1
                        heapq.heappush(heap, (h(t, y), tick, (t, y)))
            row = {"sphere": f"K_{kk}", "l0": l0, "second atom at distance": d, "target found": target is not None,
                   "start distance to target": h(*start), "configurations": len(prev), "reached atom 0": found is not None}
            if found:
                kinds, node = [], found
                while prev[node] is not None:
                    node, kind = prev[node]
                    kinds.append(kind)
                s_end = [(found[0] >> e) & 1 for e in range(3 * K.n)]
                row.update({"moves": len(kinds), "learning steps": kinds.count("learn"), "flips": kinds.count("flip"),
                            "roles at the end": [LH.atom_role(K, Y, s_end, j) for j in (0, 1)]})
            rows.append(row)
            print(round(time.time() - T0, 1), row, flush=True)
(HERE / "posthoc_targeted.json").write_text(json.dumps({"rows": rows}, indent=1) + "\n")
