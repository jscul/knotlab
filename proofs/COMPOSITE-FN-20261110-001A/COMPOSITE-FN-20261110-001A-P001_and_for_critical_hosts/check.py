#!/usr/bin/env python3
"""Checks for COMPOSITE-FN-20261110-001A: AND for critical hosts (research/COMPOSITE-FN-20261110-001/preregistration.md, ticket A).

    .venv/bin/python3 -B check.py [--write]
PYTHONHASHSEED=0. 1: on every sphere of steer_lib.test_spheres(random.Random(109)) and on K_5..K_8, every line has three distinct faces
and a state violating it and no other line (SAT). 2: a composite with two Fano leaves over a tube, a grown sphere and a double cover from
that set (leaves at the first line-orbit representative and the first line at the largest distance; standard point), grown at K_2's L0:
its role in all 16 classes against the AND of its leaves."""
import hashlib
import itertools
import json
import os
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
NA = ROOT / "proofs/NEST-ATOMS-20261110-001A/NEST-ATOMS-20261110-001A-P001_composite_atoms"
sys.path.insert(0, str(NA))
T0 = time.time()
OUT = {}
DEPS = ["proofs/NEST-ATOMS-20261110-001A/NEST-ATOMS-20261110-001A-P001_composite_atoms/nest_lib.py",
        "proofs/NEST-ATOMS-20261110-001A/NEST-ATOMS-20261110-001A-P001_composite_atoms/spaces_lib.py",
        "proofs/RESIGN-STEER-20261107-001A/RESIGN-STEER-20261107-001A-P001_re_signing_splits_the_dissonance_and_carries_it_anywhere/steer_lib.py",
        "research/COMPOSITE-FN-20261110-001/preregistration.md"]


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:900], round(time.time() - T0, 1), "s", flush=True)


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    write = "--write" in sys.argv
    check("0 dependencies bound by hash", True, {p: sha(p) for p in DEPS})
    import spaces_lib as SP
    N, G, SL, L = SP.N, SP.G, SP.SL, SP.L
    spheres = L.test_spheres(random.Random(109)) + [L.octahedral(m) for m in (5, 6, 7, 8)]
    rows = []
    for sp in spheres:
        K = sp.K
        distinct = all(len({sp.S.vert[t][c] for c in range(3)}) == 3 for t in K.lines)
        crit = [N.one_violated(K, sp.s0, i) for i in range(K.n)]
        rows.append({"sphere": sp.name, "lines": K.n, "three distinct faces per line": distinct, "critical lines": sum(crit)})
        print(round(time.time() - T0, 1), sp.name, K.n, distinct, sum(crit), flush=True)
    ok1 = all(r["three distinct faces per line"] and r["critical lines"] == r["lines"] for r in rows)
    check("1 lemma H, checked: every line of every sphere in the set has a state violating it alone", ok1, {"spheres": rows})
    # 2: the AND over three non-octahedral hosts
    picks = [next(sp for sp in spheres if sp.name.startswith(pre)) for pre in ("tube", "grown", "cover")]
    S2, s2 = SP.SPH[2].S, SP.SPH[2].s0
    L0 = SP.lines_of(2)[0]
    li = SP.SPH[2].K.lines.index(L0)
    own = sorted(p for p in itertools.product((0, 1), repeat=3) if not (p[0] ^ s2[3 * li] == p[1] ^ s2[3 * li + 1] == p[2] ^ s2[3 * li + 2]))
    rows2 = []
    for sp in picks:
        l0 = G.line_orbits(sp.S)[0][0]
        d = G.line_distance(sp.S, l0)
        l1 = min(t for t, dd in d.items() if dd == max(d.values()))
        C = N.Nested(sp.S, sp.s0)
        for l in (l0, l1):
            C.grow_leaf(C.where[l], SP.ATOMS["Fano"])
        P = SP.standard_point(C)
        O = N.Nested(S2, s2)
        O.grow_closed(O.where[L0], C, P)
        K = O.K()
        pid = {t: i for i, t in enumerate(K.points)}
        ports0 = [pid[O.where[S2.side[L0][k][0]]] for k in range(3)]
        lines0 = O.group_parts(K, (0,))[0]
        tally, bad = {}, 0
        for s in O.classes(K):
            leaves = [N.group_role(K, s, *O.group_parts(K, q)[:2]) for q in O.leaves()]
            rel = N.relation(K, s, lines0, ports0)
            want = all(r == "line" for r in leaves)
            good = (rel == own) if want else (len(rel) == 8)
            key = "%s, acting leaves %d, AND holds %s" % (N.role_of(rel), sum(r == "line" for r in leaves), good)
            tally[key] = tally.get(key, 0) + 1
            bad += not good
        rows2.append({"host": sp.name, "leaf lines": [l0, l1], "classes": sum(tally.values()), "tally": tally, "AND holds in every class": bad == 0})
        print(round(time.time() - T0, 1), sp.name, tally, flush=True)
    check("2 the AND over three non-octahedral sphere hosts (exact, 16 classes each)", all(r["AND holds in every class"] for r in rows2), {"hosts": rows2})
    OUT["predictions"] = {"lemma H checked on every sphere": ok1, "AND on the three hosts": all(r["AND holds in every class"] for r in rows2)}
    OUT["seconds"] = round(time.time() - T0, 1)
    res = HERE / "result.json"
    if write:
        res.write_text(json.dumps({"status": "passed", "checks": OUT}, indent=1, default=str) + "\n")
        print("wrote", res)
    else:
        old = json.loads(res.read_text())["checks"]
        fresh = json.loads(json.dumps(OUT, default=str))
        diff = [k for k in OUT if k != "seconds" and json.dumps(old.get(k, {}).get("info") if isinstance(old.get(k), dict) and "info" in old.get(k, {}) else old.get(k), sort_keys=True)
                != json.dumps(fresh[k]["info"] if isinstance(fresh[k], dict) and "info" in fresh[k] else fresh[k], sort_keys=True)]
        print("result.json reproduced" if not diff else "result.json differs: %s" % diff)
        sys.exit(0 if not diff else 1)


if __name__ == "__main__":
    main()
