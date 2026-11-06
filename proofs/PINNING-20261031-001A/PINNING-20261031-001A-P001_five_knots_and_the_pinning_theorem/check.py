#!/usr/bin/env python3
"""Checks for PINNING-20261031-001A: five knots and the pinning theorem.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (pysat, networkx)."""
import hashlib
import itertools
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import pin_lib as P  # noqa: E402

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
check("0 dependency artifacts bound by hash", not bad, {"parents": len(manifest["parent_bindings"]), "mismatched": bad})

KNOTS = P.all_knots()
CLASSES = sorted({P.canonical(R) for R in KNOTS}, key=lambda c: (len(c), sorted(c)))
LAW = {P.name_of(c): c for c in CLASSES}

# ------------------------------------------------------------------------------------------------ 1. five classes
info = {P.name_of(c): {"canonical states": sorted(c), "relations in the class": len(P.orbit(c))} for c in CLASSES}
check("1 the three-place knots (34 relations) form exactly five classes under flips and permutations", len(KNOTS) == 34 and len(CLASSES) == 5
      and set(LAW) == {"parity", "Fibonacci (no-lone)", "not-all-equal", "x or (y != z)", "clause"}, info)

# ------------------------------------------------------------------------------------------------ 2. plain systems
excl = [sorted(R) for R in KNOTS if (0, 0, 0) not in R and (1, 1, 1) not in R]
nae = frozenset(s for s in P.CUBE if 0 < sum(s) < 3)
check("2 plain systems: not-all-equal is the only knot relation excluding both constant colourings, so every other knot is satisfied by a "
      "constant on every plain system", excl == [sorted(nae)], {"knot relations excluding 000 and 111": excl})

# ------------------------------------------------------------------------------------------------ 3. no preferred value
inv = [sorted(R) for R in KNOTS if P.complement_invariant(R)]
check("3 the knot relations unchanged by flipping every colour are exactly the four signed not-all-equal relations",
      len(inv) == 4 and all(P.canonical(frozenset(map(tuple, R))) == LAW["not-all-equal"] for R in inv), {"relations": inv})

# ------------------------------------------------------------------------------------------------ 4. Schaefer status
info = {name: P.schaefer_classes(P.orbit(c)) for name, c in LAW.items()}
check("4 Schaefer: only the parity law is tractable with unbounded occurrences (affine); the other four signed laws are NP-complete",
      info == {"parity": ["affine (closed under a+b+c)"], "Fibonacci (no-lone)": [], "not-all-equal": [], "x or (y != z)": [], "clause": []},
      info)

# ------------------------------------------------------------------------------------------------ 5. the pinning theorem on the Fibonacci law
V = P.orbit(LAW["Fibonacci (no-lone)"])
pin = P.find_piece(V, lambda acc: acc in set(P.faces().values()))
full = P.find_piece(V, lambda acc: len(acc) == 8)
key = next(k for k, F in P.faces().items() if F == pin["accepted"])
link = next((R,) + P.pinned_binary(R) for R in sorted(V, key=sorted) if P.pinned_binary(R))
rng = random.Random(20261031)
agree, unsat, biggest = 0, 0, 0
for t in range(60):
    n, m = rng.randint(3, 7), rng.randint(2, 11)
    cons = [(tuple(rng.sample(range(n), 3)), rng.choice(sorted(V, key=sorted))) for _ in range(m)]
    B = P.to_cubic(n, cons, (pin, key), full, link)
    a, b = P.solvable_direct(n, cons), P.sat(B.lines)
    simple = len({frozenset(l) for l, R in B.lines}) == len(B.lines)
    agree += (a == b) and all(d == 3 for d in B.deg.values()) and simple
    unsat += not a
    biggest = max(biggest, len(B.lines))
check("5 the pinning theorem's reduction (generic code) on the Fibonacci law: unbounded instances become simple cubic systems with the same "
      "solvability", agree == 60 and unsat > 0,
      {"pinning piece": {"internal points": pin["k"], "lines": [list(map(str, l)) for l in pin["lines"]], "face (port, value)": key},
       "full piece internal points": full["k"], "link (coordinate, value, kind)": list(P.pinned_binary(link[0])),
       "instances": 60, "agree, cubic and simple": agree, "unsolvable sources": unsat, "largest system (lines)": biggest})

# ------------------------------------------------------------------------------------------------ 6. the clause cannot pin
C = P.orbit(LAW["clause"])
full_c = P.find_piece(C, lambda acc: len(acc) == 8)
pin_c = P.find_piece(C, lambda acc: acc in set(P.faces().values()))


def random_cubic(n, rng):
    while True:
        slots = [p for p in range(n) for _ in range(3)]
        rng.shuffle(slots)
        lines = [tuple(slots[3 * i:3 * i + 3]) for i in range(n)]
        if all(len(set(l)) == 3 for l in lines):
            return lines


tovey = 0
for t in range(300):
    n = rng.randint(4, 30)
    lines = random_cubic(n, rng)
    tovey += P.sat([(l, rng.choice(sorted(C, key=sorted))) for l in lines])
check("6 the clause cannot pin: a pinning piece and its sign-flipped copy, glued at the pinned port and padded with full pieces, would be "
      "an unsatisfiable cubic clause system, against Tovey's theorem (checked: random cubic clause systems are all satisfiable; a full "
      "clause piece exists; no pinning piece with up to four internal points)", full_c is not None and pin_c is None and tovey == 300,
      {"full clause piece internal points": full_c["k"] if full_c else None, "pinning piece found (k <= 4)": pin_c is not None,
       "random cubic clause systems satisfiable": f"{tovey}/300"})

# ------------------------------------------------------------------------------------------------ 7. not-all-equal cannot pin
N = P.orbit(LAW["not-all-equal"])
pin_n = P.find_piece(N, lambda acc: acc in set(P.faces().values()))
flip_closed = P.find_piece(N, lambda acc: P.flip(acc, (1, 1, 1)) != acc)
check("7 not-all-equal cannot pin: every accepted set of its pieces is closed under flipping every port (none found otherwise, k <= 4)",
      pin_n is None and flip_closed is None, {"pinning piece found": pin_n is not None, "accepted set not flip-closed found": flip_closed is not None})

# ------------------------------------------------------------------------------------------------ 8. controls
one = frozenset(s for s in P.CUBE if sum(s) == 1)
bad_link = (frozenset(s for s in P.CUBE if s != (0, 0, 0)), 0, 0, "equality")    # a clause line through a 0: not an equality
disagree = 0
for t in range(40):
    n, m = rng.randint(3, 6), rng.randint(3, 10)
    cons = [(tuple(rng.sample(range(n), 3)), rng.choice(sorted(V, key=sorted))) for _ in range(m)]
    Bb = P.to_cubic(n, cons, (pin, key), full, bad_link)
    disagree += P.solvable_direct(n, cons) != P.sat(Bb.lines)
controls = {"exactly-one (not a knot) also excludes both constants: the knot hypothesis matters in 2":
                (0, 0, 0) not in one and (1, 1, 1) not in one and not P.is_knot(one),
            "the parity law can pin (affine pieces include faces), yet stays polynomial":
                P.find_piece(P.orbit(LAW["parity"]), lambda acc: acc in set(P.faces().values()), kmax=4) is not None,
            "with a link that is not an equality (a clause line) the copies decouple and solvability is lost on some instances":
                disagree > 0, "disagreements (of 40)": disagree}
check("8 controls", all(v for k, v in controls.items() if not k.startswith("disagreements")), controls)

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
