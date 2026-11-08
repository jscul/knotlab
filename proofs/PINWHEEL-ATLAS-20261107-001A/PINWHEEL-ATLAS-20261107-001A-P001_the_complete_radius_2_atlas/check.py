"""Check for PINWHEEL-ATLAS-20261107-001A: the complete radius-2 atlas of the pinwheel law.

1. The collar search from one triangle closes: every key's five images are in the set (193 keys).
2. Exactly 108 keys are complete (the collar covers a neighbourhood of its tile).
3. For every complete key, in its 4-fold cut every dart whose tail lies in the central tile's descendants is farther than 3 from the
   edge of the cut collar, so its radius-2 code is computed there.
4. The resulting atlas has 1,168 radius-2 codes and no code with two oriented labels; at radius 1 it has 198 codes, 9 of them with two
   labels.
5. The atlas equals the codes of the interior darts of the geometric level-7 patch, at radius 1 and 2, labels included.
The complete collars come in mirror pairs (the partial ones need not: they sit on one fixed triangle's boundary).
Controls: at 2 cuts the edge test fails; a search stopped at level 3 misses keys; shuffled labels conflict.
Writes result.json and atlas.json (each radius-2 code with its label)."""
from __future__ import annotations
import json, random, sys, time
from collections import defaultdict
from pathlib import Path
from fractions import Fraction as Fr

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import atlas_lib as A

def atlas(keys, j, radii=(1, 2)):
    out = {r: defaultdict(set) for r in radii}
    short = {r: 0 for r in radii}
    for k in keys:
        h, tiles = k
        alltiles, desc = A.descend(list(tiles), A.BASE, j)
        pts = {p for t in alltiles for p in t}
        from functools import reduce
        import math
        den = reduce(lambda a, b: a * b // math.gcd(a, b), {x.denominator for p in pts for x in p}, 1)
        conv = {p: (int(p[0] * den), int(p[1] * den)) for p in pts}
        M = A.build_map([tuple(conv[p] for p in t) for t in alltiles], h)
        db = A.bfs_dist(M["rot"], list(M["boundary"]))
        tails = {M["vid"][conv[p]] for t in desc for p in t}
        for (u, v), lab in M["dlab"].items():
            if u not in tails:
                continue
            for r in radii:
                if db.get(u, 0) <= r + 1 or db.get(v, 0) <= r + 1:
                    short[r] += 1
                    continue
                out[r][A.code(M["rot"], u, v, r)].add(lab)
    return out, short

def enc_lab(lab):
    left, right, al = lab
    f = lambda s: None if s is None else [s[0], str(s[1]), str(s[2])]
    return [f(left), f(right), al]

def main():
    t0 = time.time()
    checks, controls, census = {}, {}, {}
    first = A.closure()
    keys = set(first)
    closed = all(k2 in keys for k in keys for k2 in A.phi(k))
    lv = defaultdict(int)
    for k, l in first.items():
        lv[l] += 1
    census["collars"] = len(keys)
    census["first_level"] = dict(sorted(lv.items()))
    checks["closure_closed"] = closed and len(keys) == 193
    comp = sorted((k for k in keys if A.complete(k)), key=lambda k: (k[0], sorted(k[1])))
    cset = set(comp)
    # partial collars sit on the boundary of one fixed triangle, so only the complete ones need come in mirror pairs
    checks["complete_collars_mirror_symmetric"] = all((-h, X) in cset for h, X in comp)
    census["partial_collars_without_mirror"] = sum(1 for h, X in keys if (-h, X) not in keys)
    census["complete_collars"] = len(comp)
    checks["complete_collars_108"] = len(comp) == 108
    at, short = atlas(comp, 4)
    census["darts_near_edge_j4"] = short
    checks["edge_test_j4"] = short[1] == 0 and short[2] == 0
    conf = {r: sum(1 for s in at[r].values() if len(s) > 1) for r in at}
    census["codes"] = {r: len(at[r]) for r in at}
    census["conflicting_codes"] = conf
    checks["radius2_label_is_a_function"] = conf[2] == 0 and len(at[2]) == 1168
    checks["radius1_is_not_enough"] = conf[1] == 9 and len(at[1]) == 198
    geo = {r: A.patch_codes(A.pinwheel_patch(7), r) for r in (1, 2)}
    checks["equals_level7_patch"] = all({c: frozenset(s) for c, s in geo[r].items()} == {c: frozenset(s) for c, s in at[r].items()}
                                        for r in (1, 2))
    # controls
    at2, short2 = atlas(comp, 2, radii=(2,))
    controls["two cuts leave darts near the edge"] = short2[2] > 0 and len(at2[2]) < 1168
    trunc = A.closure(max_level=3)
    controls["search stopped at level 3 misses keys"] = len(trunc) < len(keys)
    rng = random.Random(20261107)
    M = A.build_map(A.pinwheel_patch(5), 1)
    db = A.bfs_dist(M["rot"], list(M["boundary"]))
    darts = [(u, v) for (u, v) in M["dlab"] if db.get(u, 0) > 3 and db.get(v, 0) > 3]
    perm = [M["dlab"][d] for d in darts]; rng.shuffle(perm)
    g = defaultdict(set)
    for d, lab in zip(darts, perm):
        g[A.code(M["rot"], d[0], d[1], 2)].add(lab)
    controls["shuffled labels conflict"] = sum(1 for s in g.values() if len(s) > 1) > 0
    data = {"about": "Every radius-2 rooted code of a pinwheel tiling's planar map, with the oriented label of its dart: (left tile's side, "
            "interval start, interval end), (right tile's side, start, end), whether the two sides run the same way. Codes as in "
            "PINWHEEL-NATIVE-20261107-001B: per discovered vertex, its degree and its neighbours' discovery numbers in counterclockwise "
            "order from the vertex it was entered from (-1: beyond radius 2).",
            "radius": 2,
            "atlas": [[[[d, list(row)] for d, row in c], enc_lab(next(iter(s)))] for c, s in sorted(at[2].items())]}
    (HERE / "atlas.json").write_text(json.dumps(data, separators=(",", ":")) + "\n")
    res = {"status": "passed" if all(checks.values()) and all(controls.values()) else "failed",
           "failures": [k for k, v in {**checks, **controls}.items() if not v],
           "checks": checks, "controls": controls, "census": census, "runtime_seconds": round(time.time() - t0, 1)}
    (HERE / "result.json").write_text(json.dumps(res, indent=1, default=str) + "\n")
    print(json.dumps(res, indent=1, default=str))
    return 0 if res["status"] == "passed" else 1

if __name__ == "__main__":
    sys.exit(main())
