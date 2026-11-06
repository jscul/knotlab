#!/usr/bin/env python3
"""Checks for FOUR-PLACE-20261031-001A: the value-free four-place knots.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (networkx)."""
import hashlib
import itertools
import json
import sys
import time
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import four_lib as F  # noqa: E402

T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:600], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        print(json.dumps(info, default=str, indent=1))
        sys.exit(1)


def bits(R):
    return "".join("1" if s in R else "0" for s in F.H4)       # truth table over 0000, 0001, ..., 1111


# ------------------------------------------------------------------------------------------------ 0. bindings
manifest = json.loads((HERE / "manifest.json").read_text())
bad = {p: d for p, d in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != d}
check("0 dependency artifacts bound by hash", not bad, {"parents": len(manifest["parent_bindings"]), "mismatched": bad})

# ------------------------------------------------------------------------------------------------ 1. the catalogue
CL = F.classes()
vf = F.value_free_knots()
# independent count: every subset of {0,1}^4 that is complement-invariant is a union of the 8 antipodal pairs (2^8 - 2 candidates)
brute = 0
for m in range(1, 1 << 16):
    R = frozenset(s for i, s in enumerate(F.H4) if m >> i & 1)
    brute += F.complement(R) == R and F.is_knot(R)
info = {name: {"states": len(mem[0]), "relations": len(mem), "a representative (truth table)": bits(mem[0]),
               "symmetric members": sum(all(F.permute(R, p) == R for p in itertools.permutations(range(4))) for R in mem)}
        for name, mem in CL.items()}
check("1 the value-free four-place knots: 30 relations in four classes (parity 8 states x 2, not-exactly-two 10 x 8, twelve 12 x 12, "
      "not-all-equal 14 x 8), confirmed by brute force over all 2^16 relations",
      len(vf) == 30 and brute == 30 and [(len(m[0]), len(m)) for m in CL.values()] == [(8, 2), (10, 8), (12, 12), (14, 8)]
      and all(F.is_knot(R) and F.complement(R) == R for R in vf), info)

# ------------------------------------------------------------------------------------------------ 2. no pinning
pin_bad, pieces_seen = [], 0
for name, mem in CL.items():
    for k in (3, 4):
        for lines in F.structures(k):
            for rel in F.accepted_relations(lines, k, mem):
                pieces_seen += 1
                if F.complement(rel) != rel or any(len({s[j] for s in rel}) == 1 for j in range(4)):
                    pin_bad.append((name, lines, sorted(rel)))
check("2 a complement-invariant law cannot pin: every accepted relation of every piece with three or four internal points, in every "
      "class, is complement-invariant, so no port is ever forced to a value", not pin_bad,
      {"distinct (piece, accepted relation) pairs checked": pieces_seen, "violations": pin_bad[:2]})

# ------------------------------------------------------------------------------------------------ 3. Schaefer
sch = {name: F.schaefer_classes(mem) for name, mem in CL.items()}
check("3 Schaefer: parity is affine; the other three classes are closed under none of the six tractable polymorphisms",
      sch == {"parity": ["affine (minority)"], "not-exactly-two": [], "twelve": [], "not-all-equal": []}, sch)

# ------------------------------------------------------------------------------------------------ 4. plain failures
plain = {name: [bits(R) for R in mem if F.ZERO not in R and F.ONE not in R] for name, mem in CL.items()}
check("4 on plain systems only relations excluding both constant colourings can fail: eight of them (odd parity, three of not-exactly-two "
      "= odd parity plus one balanced pair, three of twelve = odd parity plus two balanced pairs, not-all-equal)",
      {k: len(v) for k, v in plain.items()} == {"parity": 1, "not-exactly-two": 3, "twelve": 3, "not-all-equal": 1}, plain)

# ------------------------------------------------------------------------------------------------ 5. the systems
census = json.loads((ROOT / "research/MUTUAL-SELECTION-20261031-001C/census.json").read_text())
SYS = {n: F.systems(n, census) for n in (4, 5, 6, 7)}
graphs = {n: [F.incidence_graph(L) for L in S] for n, S in SYS.items()}
distinct = all(not nx.is_isomorphic(a, b) for S in graphs.values() for a, b in itertools.combinations(S, 2))
check("5 every 4-regular 4-uniform system with n <= 7 points, up to isomorphism: 1, 1, 4, 14 (complements in K_{n,n} of the (n-4)-regular "
      "bipartite graphs: cycle covers for n = 6, the 14 cubic bipartite graphs on 7 + 7 vertices for n = 7); all regular and simple, "
      "pairwise non-isomorphic", [len(SYS[n]) for n in (4, 5, 6, 7)] == [1, 1, 4, 14] and distinct
      and all(F.is_regular_system(L) for S in SYS.values() for L in S),
      {"counts": {n: len(S) for n, S in SYS.items()}, "connected": {n: sum(nx.is_connected(g) for g in G) for n, G in graphs.items()}})

# ------------------------------------------------------------------------------------------------ 6. the failure census
table, failing_systems = {}, {name: {n: 0 for n in SYS} for name in CL}
for n, S in SYS.items():
    for i, lines in enumerate(S):
        row = {}
        for name, mem in CL.items():
            if name == "twelve" and n == 7:
                f, tot = F.failing_count(lines, mem, stop_at_first=True)
                row[name] = "fails (one failure exhibited)" if f else "no failure (all 12^7 signings solvable)"
            else:
                f, tot = F.failing_count(lines, mem)
                row[name] = f"{f}/{tot}"
            failing_systems[name][n] += f > 0
        table[f"n={n} #{i}"] = row
counts = {n: len(S) for n, S in SYS.items()}
check("6 failure census over every signing (one member relation per line) of every 4-regular 4-uniform system with n <= 7: not-all-equal "
      "never fails; parity and not-exactly-two fail on every system; twelve fails on every system with n <= 6 and on 11 of the 14 "
      "with n = 7", failing_systems["parity"] == counts and failing_systems["not-exactly-two"] == counts
      and failing_systems["not-all-equal"] == {n: 0 for n in SYS} and failing_systems["twelve"] == {4: 1, 5: 1, 6: 4, 7: 11},
      {"systems with a failing signing": failing_systems, "table": table})

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
