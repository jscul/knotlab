#!/usr/bin/env python3
"""Checks for PINNING-20261031-001B: x or (y != z) pins, so it is NP-complete on cubic systems.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Uses ticket A's library (bound by hash). Run with the repository's .venv (pysat, networkx)."""
import hashlib
import itertools
import json
import random
import sys
import time
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
A_DIR = ROOT / "proofs/PINNING-20261031-001A/PINNING-20261031-001A-P001_five_knots_and_the_pinning_theorem"
sys.path.insert(0, str(A_DIR))
import pin_lib as P  # noqa: E402

T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:600], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        print(json.dumps(info, default=str, indent=1))
        sys.exit(1)


def describe(R):
    return "".join("1" if s in R else "0" for s in P.CUBE)     # truth table over 000, 001, ..., 111


# ------------------------------------------------------------------------------------------------ 0. bindings
manifest = json.loads((HERE / "manifest.json").read_text())
bad = {p: d for p, d in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != d}
check("0 dependency artifacts bound by hash", not bad, {"parents": len(manifest["parent_bindings"]), "mismatched": bad})

XYZ = frozenset(s for s in P.CUBE if s[0] == 1 or s[1] != s[2])
V = sorted(P.orbit(XYZ), key=sorted)
check("1 the law x or (y != z): a knot, 12 relations under flips and permutations, Schaefer: none of the tractable classes",
      P.is_knot(XYZ) and len(V) == 12 and P.schaefer_classes(V) == [] and P.name_of(XYZ) == "x or (y != z)",
      {"relation (truth table over 000..111)": describe(XYZ), "class size": len(V)})

# ------------------------------------------------------------------------------------------------ 2. the pieces
pin = P.find_piece(V, lambda acc: acc in set(P.faces().values()))
key = next(k for k, F in P.faces().items() if F == pin["accepted"])
full = P.find_piece(V, lambda acc: len(acc) == 8)
link_R = XYZ
link = (link_R,) + P.pinned_binary(link_R)
check("2 the pieces: a pinning piece (four internal points, five lines, the same skeleton as the Fibonacci and parity pieces), the link "
      "x = 0 giving y != z, and a full piece; each re-verified by enumeration",
      pin["k"] == 4 and P.accepted(pin["lines"], pin["rels"], pin["k"]) == pin["accepted"]
      and P.accepted(full["lines"], full["rels"], full["k"]) == frozenset(P.CUBE) and link[1:] == (0, 0, "disequality"),
      {"pinning piece": {"lines": [list(map(str, l)) for l in pin["lines"]], "relations": [describe(R) for R in pin["rels"]],
                         "pins (port, value)": ["abc"[key[0]], key[1]]},
       "full piece": {"lines": [list(map(str, l)) for l in full["lines"]], "relations": [describe(R) for R in full["rels"]]},
       "link": list(link[1:])})

# ------------------------------------------------------------------------------------------------ 3. the reduction
rng = random.Random(20261031)
agree, unsat, biggest = 0, 0, 0
for t in range(80):
    n, m = rng.randint(3, 7), rng.randint(2, 12)
    cons = [(tuple(rng.sample(range(n), 3)), rng.choice(V)) for _ in range(m)]
    B = P.to_cubic(n, cons, (pin, key), full, link)
    a, b = P.solvable_direct(n, cons), P.sat(B.lines)
    simple = len({frozenset(l) for l, R in B.lines}) == len(B.lines)
    agree += (a == b) and all(d == 3 for d in B.deg.values()) and simple
    unsat += not a
    biggest = max(biggest, len(B.lines))
check("3 the pinning theorem's reduction: instances of x or (y != z) with any number of occurrences become simple cubic systems with the "
      "same solvability", agree == 80 and unsat > 0,
      {"instances": 80, "agree, cubic and simple": agree, "unsolvable sources": unsat, "largest cubic system (lines)": biggest})

# ------------------------------------------------------------------------------------------------ 4. census of failures
def graphs(n, count, rng):
    reps = []
    tries = 0
    while len(reps) < count and tries < 20000:
        tries += 1
        slots = [p for p in range(n) for _ in range(3)]
        rng.shuffle(slots)
        lines = [tuple(slots[3 * i:3 * i + 3]) for i in range(n)]
        if not all(len(set(l)) == 3 for l in lines):
            continue
        g = nx.Graph([(('l', i), ('p', p)) for i, l in enumerate(lines) for p in l])
        if g.number_of_edges() != 3 * n or not nx.is_connected(g) or any(nx.is_isomorphic(g, h) for h, _ in reps):
            continue
        reps.append((g, lines))
    return reps


A006823 = {4: 1, 5: 2}
census = {}
for n in (4, 5):
    for gi, (g, lines) in enumerate(graphs(n, A006823[n], rng)):
        fails = 0
        for choice in itertools.product(range(len(V)), repeat=n):
            if not P.sat([(l, V[c]) for l, c in zip(lines, choice)]):
                fails += 1
        census[f"n = {n}, graph {gi}"] = {"relation assignments": len(V) ** n, "unsolvable": fails}
sampled = {}
for n in (6, 8, 10):
    for g, lines in graphs(n, 3, rng):
        fails = sum(1 for t in range(400) if not P.sat([(l, rng.choice(V)) for l in lines]))
        sampled.setdefault(f"n = {n}", []).append(f"{fails}/400")
# an explicit failing system: two pinning pieces with opposite pins glued at the pinned port, padded with full pieces
Bx = P.Builder()
p = Bx.point('pinned')
ports1 = [Bx.point('d'), Bx.point('d'), Bx.point('d')]
ports1[key[0]] = p
Bx.piece(pin, ports1)
flipped = dict(pin)
pi = key[0]
port_name = "abc"[pi]
flipped["rels"] = [P.flip(R, tuple(1 if l[j] == port_name else 0 for j in range(3))) for l, R in zip(pin["lines"], pin["rels"])]
ports2 = [Bx.point('d'), Bx.point('d'), Bx.point('d')]
ports2[pi] = p
Bx.piece(flipped, ports2)
demand = {q: 3 - d for q, d in Bx.deg.items() if d < 3}
total = sum(demand.values())
while max(demand.values()) > total // 3 or total % 3:
    q = Bx.point('pad')
    demand[q] = 3
    total += 3
while demand:
    trio = sorted(demand, key=lambda q: (-demand[q], repr(q)))[:3]
    Bx.piece(full, trio)
    for q in trio:
        demand[q] -= 1
        if not demand[q]:
            del demand[q]
explicit = {"lines": len(Bx.lines), "points": len(Bx.deg), "cubic": all(d == 3 for d in Bx.deg.values()),
            "simple": len({frozenset(l) for l, R in Bx.lines}) == len(Bx.lines), "solvable": P.sat(Bx.lines)}
check("4 failures: none on small cubic systems (exhaustive n = 4, 5; sampled n = 6, 8, 10), but an explicit failing cubic system exists "
      "(two pinning pieces with opposite pins glued at the pinned port, padded with full pieces), besides the unsolvable systems of check 3",
      explicit["cubic"] and explicit["simple"] and not explicit["solvable"] and not any(v["unsolvable"] for v in census.values()),
      {"exhaustive": census, "sampled (random relation per line)": sampled, "explicit failing system": explicit})

# ------------------------------------------------------------------------------------------------ 5. controls
wrong = (link_R, 0, 0, "equality")       # treat the disequality as an equality: copies anti-correlate
disagree = 0
for t in range(40):
    n, m = rng.randint(3, 6), rng.randint(3, 10)
    cons = [(tuple(rng.sample(range(n), 3)), rng.choice(V)) for _ in range(m)]
    disagree += P.solvable_direct(n, cons) != P.sat(P.to_cubic(n, cons, (pin, key), full, wrong).lines)
controls = {"misreading the disequality link as an equality breaks the reduction": disagree > 0, "disagreements (of 40)": disagree,
            "the flip of x or (y != z) is a different relation (it prefers a value)": not P.complement_invariant(XYZ)}
check("5 controls", all(v for k, v in controls.items() if not k.startswith("disagreements")), controls)

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
