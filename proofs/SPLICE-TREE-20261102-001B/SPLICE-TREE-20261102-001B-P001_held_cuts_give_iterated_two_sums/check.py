#!/usr/bin/env python3
"""Checks for SPLICE-TREE-20261102-001B: knots that cross only held cuts are iterated 2-sums.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy). About fifteen minutes."""
import collections
import hashlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/SPLICE-TREE-20261102-001A/SPLICE-TREE-20261102-001A-P001_a_removal_opens_the_cuts_that_point_away"))
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
    ("K4 > K4 > K4", [K4, K4, K4], [(0, 0, 1, 0), (1, 0, 2, 0)], None, None),
    ("K4 > K4 < K4", [K4, K4, K4], [(0, 0, 1, 0), (2, 0, 1, 1)], None, None),
    ("K4 > Fano > K4", [K4, FANO, K4], [(0, 0, 1, 0), (1, 0, 2, 0)], None, None),
    ("Fano > K4 > Fano", [FANO, K4, FANO], [(0, 0, 1, 0), (1, 0, 2, 0)], 6, None),
    ("K4 > K4 > K4 > K4", [K4, K4, K4, K4], [(0, 0, 1, 0), (1, 0, 2, 0), (2, 0, 3, 0)], None, None),
    ("K4 star (three leaves into a K4 centre)", [K4, K4, K4, K4], [(1, 0, 0, 0), (2, 0, 0, 1), (3, 0, 0, 2)], None, None),
    ("Fano > Fano > Fano", [FANO, FANO, FANO], [(0, 0, 1, 0), (1, 0, 2, 3)], 5, "one removal per piece"),
]


def crosses(C, c, n):
    inner = c["points"] - c["ports"]
    return bool(C & inner) and bool(C - c["points"])


tally = collections.Counter()
per = {}
ok = True
for name, pieces, edges, bound, sample in FAMILIES:
    ls, ss, n, piece, cuts = T.assemble(pieces, edges)
    V = set(range(n))
    removals = range(len(ls))
    if sample:
        removals = [next(M for M, L in enumerate(ls) if all(piece[p] == k for p in L)) for k in range(len(pieces))]
    t = collections.Counter()
    for M in removals:
        line = ls[M]
        held = [c for c in cuts if not set(line) <= c["points"]]
        S = G.removal(ls, ss, n, M)
        cs = set(G.circuits(S, n, bound))
        base = {C for C in cs if not any(crosses(C, c, n) for c in cuts)}
        gen = set(base)
        changed = True
        while changed:
            changed = False
            for c in held:
                ports = c["ports"]
                K1s = [K for K in gen if K <= c["points"] and len(K & ports) == 1 and K - ports]
                K2s = [K for K in gen if K <= (V - c["points"]) | ports and len(K & ports) == 1 and K - ports]
                for K1 in K1s:
                    for K2 in K2s:
                        new = (K1 - ports) | (K2 - ports)
                        if (bound is None or len(new) <= bound) and new not in gen:
                            gen.add(new)
                            changed = True
        actual = {C for C in cs if any(crosses(C, c, n) for c in cuts) and all(c in held for c in cuts if crosses(C, c, n))}
        produced = gen - base
        good = produced == actual and gen <= cs
        ok &= good
        t["removals"] += 1
        t["circuits crossing only held cuts"] += len(actual)
        t["of which crossing two or more held cuts"] += sum(1 for C in actual if sum(1 for c in cuts if crosses(C, c, n)) >= 2)
        t["iterated 2-sums produced"] += len(produced)
        t["removals where the two sets are equal"] += good
    per[name] = dict(t)
    tally.update(t)
check("1 on seven assemblies of three and four pieces, at every removal (one per piece on the 19-point Fano chain): the circuits that "
      "cross at least one cut, all of them held, are exactly the iterated 2-sums through held hubs of circuits crossing no cut, and every "
      "iterated 2-sum produced is a circuit (all circuits up to 13 points; up to 6 elements at 16 and 5 at 19)",
      ok and tally["circuits crossing only held cuts"] > 0 and tally["of which crossing two or more held cuts"] > 0, per)

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
