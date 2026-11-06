#!/usr/bin/env python3
"""Checks for HUB-GLUE-20261102-001B: through a held hub, emergence composes as a 2-sum.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy)."""
import collections
import hashlib
import itertools
import json
import math
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/HUB-GLUE-20261102-001A/HUB-GLUE-20261102-001A-P001_selection_leaves_a_hub_and_pieces_glue"))
import glue_lib as G  # noqa: E402

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


def constrained(S, Y):
    return len({tuple(t[v] for v in Y) for t in S}) < math.prod(len({t[v] for t in S}) for v in Y)


# ------------------------------------------------------------------------------------------------ 1-2. every splice, every removal off the point side
SPACES = G.census_spaces(ROOT)
tally = collections.Counter()
ok_tied = ok_comp = ok_sum = True
mismatch = []
for i1, n1, H1, s1 in SPACES:
    for i2, n2, H2, s2 in SPACES:
        if n1 + n2 - 1 > 13:
            continue
        ls, ss, n, side, ports = G.splice(H1, s1, n1, 0, H2, s2, n2, 0)
        P = {v for v in range(n) if side[v] == 0}
        Q = set(range(n)) - P
        interior = P - ports
        bound = None if n <= 11 else 7                    # circuits up to 7 elements on the largest spaces
        for M, line in enumerate(ls):
            if set(line) <= P:
                continue                                  # on the point side: the hub opens (ticket C)
            S = G.removal(ls, ss, n, M)
            tally["removals off the point side"] += 1
            pp = sorted(ports)
            tied = all(len({(t[a], t[b]) for t in S}) == 2 for a, b in itertools.combinations(pp, 2))
            ok_tied &= tied
            Sset = set(S)
            ok_comp &= all(tuple(1 - v for v in t) in Sset for t in S)
            cs = G.circuits(S, n, bound)
            p0 = pp[0]
            sideP = [C for C in cs if C <= P and p0 in C and not (C - {p0}) & ports]   # through the hub, one port only
            # circuits of the (Q + ports)-part through the hub: through any port, moved onto p0 (ports are tied)
            sideQ = set()
            for C in cs:
                if C <= Q | ports and C & ports and C & Q:
                    if len(C & ports) == 1:
                        sideQ.add((C - ports) | {p0})
            predicted = {frozenset((K1 - {p0}) | (K2 - {p0})) for K1 in sideP for K2 in sideQ
                         if K1 - {p0} and K2 - {p0} and (bound is None or len(K1) + len(K2) - 2 <= bound)}
            crossing = {C for C in cs if C & interior and C & Q}
            tally["crossing circuits"] += len(crossing)
            tally["crossing circuits that contain a port"] += sum(1 for C in crossing if C & ports)
            if crossing != predicted:
                ok_sum = False
                if len(mismatch) < 3:
                    mismatch.append({"splice": (i1, i2), "removed": line, "missing": [sorted(c) for c in list(predicted - crossing)[:3]],
                                     "extra": [sorted(c) for c in list(crossing - predicted)[:3]]})
            tally["2-sums predicted"] += len(predicted)
check("1 every splice of two census knot spaces up to 13 points (at their first line and point), at every removal off the point side: "
      "the three ports are tied (two joint values for every pair), and the solutions are closed under complementing every value",
      ok_tied and ok_comp and tally["removals off the point side"] > 0, {"removals off the point side": tally["removals off the point side"]})
check("2 at every such removal, the circuits meeting both the point side's interior and the line side are exactly the 2-sums "
      "(K1 - p) u (K2 - p) of a circuit through the hub on each side, ties included, and none contains a port (all circuits on spaces "
      "up to 11 points, circuits up to 7 elements on 12 and 13)", ok_sum and tally["crossing circuits"] > 0 and
      tally["crossing circuits that contain a port"] == 0, {**{k: v for k, v in tally.items()}, "mismatches": mismatch})

# ------------------------------------------------------------------------------------------------ 3. the control: without complement symmetry the elimination fails
# A on (x1, x2, h) = OR, B on (h, y1, y2) = OR: each is a circuit through h, deficient only at h = 0
A_ = {t for t in itertools.product((0, 1), repeat=3) if any(t)}
B_ = {t for t in itertools.product((0, 1), repeat=3) if any(t)}
R = {(a[0], a[1], b[1], b[2]) for a in A_ for b in B_ if a[2] == b[0]}
or_circuit = (not constrained(sorted(A_), [0, 1])) and constrained(sorted(A_), [0, 1, 2])
free_elim = not constrained(sorted(R), [0, 1, 2, 3])
NAE = {t for t in itertools.product((0, 1), repeat=3) if len(set(t)) > 1}
R2 = {(a[0], a[1], b[1], b[2]) for a in NAE for b in NAE if a[2] == b[0]}
sym_elim = constrained(sorted(R2), [0, 1, 2, 3])
check("3 the control: joining two OR circuits along a bit (each deficient at one value of the bit only) eliminates to a free set, while "
      "joining two knot circuits (not-all-equal, deficient at both values) eliminates to a constrained one: complement symmetry is "
      "what makes the held hub compose", or_circuit and free_elim and sym_elim,
      {"OR is a circuit through the bit": or_circuit, "OR elimination is free": free_elim, "knot elimination is constrained": sym_elim})

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
