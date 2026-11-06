#!/usr/bin/env python3
"""Checks for NATIVE-PATHS-20261101-001C: the twist criterion, and knot meets knot only pairwise.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (networkx, pysat)."""
import collections
import hashlib
import itertools
import json
import random
import sys
import time
from pathlib import Path

from pysat.solvers import Minisat22

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/NATIVE-PATHS-20261101-001A/NATIVE-PATHS-20261101-001A-P001_two_kinds_of_interface"))
import paths_lib as P  # noqa: E402

T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:600], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        print(json.dumps(info, default=str, indent=1))
        sys.exit(1)


# ------------------------------------------------------------------------------------------------ 0. bindings
manifest = json.loads((HERE / "manifest.json").read_text())
bad = {p: d for p, d in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != d}
status = {p: json.loads((ROOT / p).read_text()).get("status") for p in manifest["parent_bindings"] if p.endswith(".json")}
check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
      {"mismatched": bad, "statuses": status})


def incidences(H):
    return [(i, p) for i, L in enumerate(H) for p in L]


def colourable_twisted(H, t):
    """is H, with every incidence (line, point) in t reading its point's colour exchanged, 2-colourable under not-all-equal?"""
    clauses = []
    for i, L in enumerate(H):
        lits = [-(p + 1) if (i, p) in t else (p + 1) for p in L]
        clauses += [lits, [-x for x in lits]]
    with Minisat22(bootstrap_with=clauses) as S:
        return S.solve()


def is_cocycle(H, t):
    """is t = d(S) for a set S of vertices of the incidence graph? (potentials x_u + x_v = [uv in t] over GF(2), by search)"""
    adj = collections.defaultdict(list)
    for i, p in incidences(H):
        b = 1 if (i, p) in t else 0
        adj[("l", i)].append((("p", p), b))
        adj[("p", p)].append((("l", i), b))
    pot = {}
    for root in adj:
        if root in pot:
            continue
        pot[root] = 0
        stack = [root]
        while stack:
            u = stack.pop()
            for v, b in adj[u]:
                if v not in pot:
                    pot[v] = pot[u] ^ b
                    stack.append(v)
                elif pot[v] != pot[u] ^ b:
                    return False
    return True


def edge_of(e):
    a, b = e
    line, point = (a, b) if a[0] == "l" else (b, a)
    return (line[1], point[1])


def is_knot(R, k):
    """K1-K3 on k channels: non-empty, constrained, and every (k-1)-place projection full"""
    if not R or len(R) == 2 ** k:
        return False
    return all(len({s[:j] + s[j + 1:] for s in R}) == 2 ** (k - 1) for j in range(k))


SP = P.spaces()
CUTS = {name: {k: P.nontrivial_cuts(H, k) for k in (2, 3)} for name, H in SP.items()}
SMALL = ("Fano", "chain of 2", "chain of 3", "cycle of 3 blocks")
for name in SMALL:
    CUTS[name][4] = P.nontrivial_cuts(SP[name], 4)

# ------------------------------------------------------------------------------------------------ 1. criterion on cut twists
ok1, info1 = True, {}
for name, H in SP.items():
    tally = collections.Counter()
    for k in (2, 3):
        for cut, _ in CUTS[name][k]:
            F = [edge_of(e) for e in cut]
            for r in range(len(F) + 1):
                for sub in itertools.combinations(F, r):
                    t = set(sub)
                    fails, coc = not colourable_twisted(H, t), is_cocycle(H, t)
                    ok1 &= fails == coc
                    tally["cocycle" if coc else "not a cocycle"] += 1
    info1[name] = dict(tally)
check("1 the twist criterion on every twist pattern of every nontrivial 2- and 3-edge cut of the ten knot's spaces: the space stays "
      "non-colourable exactly when the twisted set is a cocycle", ok1, info1)

# ------------------------------------------------------------------------------------------------ 2. criterion on random sets
rng = random.Random(20261101)
ok2, info2 = True, {}
for name, H in SP.items():
    inc = incidences(H)
    verts = [("l", i) for i in range(len(H))] + [("p", p) for p in sorted({p for L in H for p in L})]
    tally = collections.Counter()
    for _ in range(60):
        t = set(rng.sample(inc, rng.randint(1, len(inc) - 1)))
        fails, coc = not colourable_twisted(H, t), is_cocycle(H, t)
        ok2 &= fails == coc
        tally["random set: " + ("cocycle" if coc else "not a cocycle")] += 1
    for _ in range(60):
        S = {v for v in verts if rng.random() < 0.5}
        t = {(i, p) for i, p in inc if (("l", i) in S) != (("p", p) in S)}
        fails, coc = not colourable_twisted(H, t), is_cocycle(H, t)
        ok2 &= fails and coc
        tally["random d(S): non-colourable" if fails else "random d(S): colourable"] += 1
    info2[name] = dict(tally)
check("2 the twist criterion on random incidence sets (60 per space) and random cocycles d(S) (60 per space): a random set keeps the "
      "space non-colourable exactly when it is a cocycle, and every d(S) does", ok2, info2)

# ------------------------------------------------------------------------------------------------ 3. knot meets knot only pairwise
ok3, info3 = True, {}
for name, H in SP.items():
    tally = collections.Counter()
    for k, cuts in CUTS[name].items():
        for cut, comps in cuts:
            rels = [P.accepted(H, *P.shore_data(H, cut, S)) for S in comps]
            both = all(is_knot(R, k) for R in rels)
            ok3 &= both == (k == 2)
            tally["%d-edge: %s" % (k, "both sides knots" if both else "sides %s" % "/".join(str(len(R)) for R in sorted(rels, key=len)))] += 1
    info3[name] = dict(tally)
check("3 knot meets knot only pairwise: across every nontrivial 2-edge cut both sides accept knots (two-place parity), and across "
      "every nontrivial 3-edge cut of the ten spaces and 4-edge cut of Fano, the chains of 2 and 3 and the 3-cycle they never both do",
      ok3, info3)

# ------------------------------------------------------------------------------------------------ 4. controls
G = [(5, 2, 3), (0, 2, 3), (0, 1, 3), (0, 1, 2), (1, 6, 7), (4, 6, 7), (4, 5, 7), (4, 5, 6)]   # colourable, from A's control
lines4, conn4, ports4 = P.C.cycle_of_blocks(4)
junction = (conn4[0], ports4[1][2])
ctrl = {"colourable K4^(3) pair: the empty twist (a cocycle) leaves it colourable": colourable_twisted(G, set()),
        "even cycle of 4 Fano blocks: colourable untwisted": colourable_twisted(lines4, set()),
        "even cycle of 4 Fano blocks: one twisted junction (not a cocycle) makes it non-colourable":
            (not colourable_twisted(lines4, {junction})) and not is_cocycle(lines4, {junction})}
check("4 controls: off the knot's spaces the criterion fails both ways (a colourable system stays colourable under a cocycle twist, and "
      "the colourable even cycle of Fano blocks becomes non-colourable under a non-cocycle twist)", all(ctrl.values()), ctrl)

OUT["seconds"] = round(time.time() - T0, 1)
print("ALL OK", OUT["seconds"], "s")
result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"], "proof": manifest["proof"],
          "status": "passed", "claim": manifest["claim"], "checks": {k: v for k, v in OUT.items() if k != "seconds"}}
text = json.dumps(result, indent=1, sort_keys=True, default=str) + "\n"
if "--write" in sys.argv:
    (HERE / "result.json").write_text(text)
elif not (HERE / "result.json").exists() or json.loads((HERE / "result.json").read_text()) != json.loads(text):
    print("result.json does not match a fresh run; rerun with --write after review")
    sys.exit(1)
