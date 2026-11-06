#!/usr/bin/env python3
"""Checks for SPLICE-TREE-20261102-001A: a removal opens exactly the cuts that point away from it.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy)."""
import collections
import hashlib
import itertools
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import tree_lib as T  # noqa: E402

G = T.G
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
status = {p: json.loads((ROOT / p).read_text()).get("status") for p in manifest["parent_bindings"]
          if p.endswith(".json") and p.startswith("proofs/")}
check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
      {"mismatched": bad, "statuses": status})

SP = {idx: (H, s, n) for idx, n, H, s in G.census_spaces(ROOT)}
K4, FANO = SP[1], SP[21]
FAMILIES = [
    ("K4 > K4 > K4", [K4, K4, K4], [(0, 0, 1, 0), (1, 0, 2, 0)]),
    ("K4 > K4 < K4", [K4, K4, K4], [(0, 0, 1, 0), (2, 0, 1, 1)]),
    ("K4 > Fano > K4", [K4, FANO, K4], [(0, 0, 1, 0), (1, 0, 2, 0)]),
    ("Fano > K4 > Fano", [FANO, K4, FANO], [(0, 0, 1, 0), (1, 0, 2, 0)]),
    ("K4 > K4 > K4 > K4", [K4, K4, K4, K4], [(0, 0, 1, 0), (1, 0, 2, 0), (2, 0, 3, 0)]),
    ("K4 star (three leaves into a K4 centre)", [K4, K4, K4, K4], [(1, 0, 0, 0), (2, 0, 0, 1), (3, 0, 0, 2)]),
]
SPACES = []
info1, ok1 = {}, True
for name, pieces, edges in FAMILIES:
    ls, ss, n, piece, cuts = T.assemble(pieces, edges)
    glob = G.fails_globally(ls, ss, n)
    shapes = [T.cut_shape(ls, n, c["points"]) for c in cuts]
    simple = all(sh == (3, 3, 3, 1) for sh in shapes)
    ok1 &= glob and simple
    info1[name] = {"points": n, "fails globally": glob, "cuts simple (3 edges, 3 ports, 3 slots, one more point than lines)": simple}
    SPACES.append((name, ls, ss, n, cuts))
check("1 six assemblies of three and four pieces (chains in both orientations, a chain of four, a star; K4^(3) and Fano pieces, 10 to "
      "16 points) are knot spaces failing globally, and every one of their cuts is a simple 3-edge cut of the whole space", ok1, info1)

# ------------------------------------------------------------------------------------------------ 2. which cuts a removal opens
tally2 = collections.Counter()
ok2 = True
for name, ls, ss, n, cuts in SPACES:
    for M, line in enumerate(ls):
        S = G.removal(ls, ss, n, M)
        for c in cuts:
            pts, ports = c["points"], sorted(c["ports"])
            opened = set(line) <= pts
            if not opened:
                tied = all(len({(t[a], t[b]) for t in S}) == 2 for a, b in itertools.combinations(ports, 2))
                ok2 &= tied
                tally2["held cuts with tied ports"] += tied
                tally2["held"] += 1
            else:
                Pl, Ps, port_t, tw, pmap = T.closing_signs(ls, ss, n, pts, ports)
                Mi = Pl.index(tuple(pmap[p] for p in line))
                SP_ = G.removal(Pl + [port_t], Ps + [tw], len(pts), Mi)
                I_formula = {tuple(t[q] ^ tw[j] for j, q in enumerate(port_t)) for t in SP_}
                I_actual = {tuple(t[p] ^ tw[j] for j, p in enumerate(ports)) for t in S}
                ok2 &= I_formula == I_actual
                tally2["opened"] += 1
                tally2["opened cuts matching the interface formula"] += I_formula == I_actual
                tally2["opened interface of %d patterns" % len(I_actual)] += 1
check("2 at every removal and every cut: a cut whose point side does not contain the removed line is held (its ports tied), and a cut "
      "whose point side contains it is opened, with port patterns exactly those the near contraction allows on its closing line "
      "without the removed line", ok2 and tally2["held"] > 0 and tally2["opened"] > 0, dict(tally2))

# ------------------------------------------------------------------------------------------------ 3. what stays fixed beyond a held cut
tally3 = collections.Counter()
ok3 = True
for name, ls, ss, n, cuts in SPACES:
    for c in cuts:
        pts = sorted(c["points"])
        inside = [k for k, L in enumerate(ls) if set(L) <= set(pts)]
        pmap = {p: k for k, p in enumerate(pts)}
        own = G.circuits(G.removal([tuple(pmap[p] for p in ls[k]) for k in inside] + [(0, 0, 0)],
                                   [ss[k] for k in inside] + [[0, 1, 0]], len(pts), len(inside)), len(pts))
        own = {frozenset(pts[i] for i in C) for C in own}
        for M, line in enumerate(ls):
            if set(line) <= set(pts):
                continue
            S = G.removal(ls, ss, n, M)
            proj = [tuple(t[p] for p in pts) for t in S]
            seen = {frozenset(pts[i] for i in C) for C in G.circuits(sorted(set(proj)), len(pts))}
            ok3 &= seen == own
            tally3["held (cut, removal) pairs"] += 1
            tally3["far side keeps exactly its own system's circuits"] += seen == own
check("3 beyond every held cut nothing depends on the removed line: the circuits of the solutions inside the far point side are exactly "
      "the circuits of that side's own system (its contraction without the closing line), for every removal off it",
      ok3 and tally3["held (cut, removal) pairs"] > 0, dict(tally3))

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
