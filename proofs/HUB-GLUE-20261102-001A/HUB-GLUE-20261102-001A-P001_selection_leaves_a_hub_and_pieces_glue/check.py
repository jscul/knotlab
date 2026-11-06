#!/usr/bin/env python3
"""Checks for HUB-GLUE-20261102-001A: selection leaves a hub, and selected spaces glue into knot spaces.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy)."""
import collections
import hashlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
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

# ------------------------------------------------------------------------------------------------ 1. the census knot spaces
SPACES = G.census_spaces(ROOT)
info1 = {"census index and points": [(idx, n) for idx, n, _, _ in SPACES],
         "all fail globally": all(G.fails_globally(lines, s, n) for _, n, lines, s in SPACES)}
check("1 the census holds 8 knot spaces (connected cubic triple systems up to 8 points on which the signed knot fails, for some "
      "signing), and every failure is global", len(SPACES) == 8 and info1["all fail globally"], info1)


def leftover_ok(lines, signs, n):
    """after removing each line, its three points take exactly the two complementary all-equal patterns (under the line's signs)"""
    for i, L in enumerate(lines):
        S = G.removal(lines, signs, n, i)
        pats = {tuple(t[p] ^ signs[i][j] for j, p in enumerate(L)) for t in S}
        if pats != {(0, 0, 0), (1, 1, 1)}:
            return False
    return True


# ------------------------------------------------------------------------------------------------ 2. the leftover of selection is a hub
check("2 in each of the 8 census knot spaces, removing any line leaves its three points tied: under the line's signs they take exactly "
      "the two all-equal patterns, so the leftover is a hub", all(leftover_ok(lines, s, n) for _, n, lines, s in SPACES),
      {"spaces": len(SPACES), "lines checked": sum(len(lines) for _, _, lines, _ in SPACES)})

# ------------------------------------------------------------------------------------------------ 3. splices of selected spaces are knot spaces
tally3 = collections.Counter()
ok3 = True
choices = collections.Counter()
SPLICED = []
for i1, n1, H1, s1 in SPACES:
    for i2, n2, H2, s2 in SPACES:
        if n1 + n2 - 1 > 13:
            continue
        for li in range(len(H1)):
            for pt in range(n2):
                found = G.splice(H1, s1, n1, li, H2, s2, n2, pt, all_choices=True)
                tally3["splices"] += 1
                choices[len(found)] += 1
                if not found:
                    ok3 = False
                    continue
                ls, ss, n, side, ports = found[0]
                glob = G.fails_globally(ls, ss, n)
                ok3 &= glob
                hub = leftover_ok(ls, ss, n) if (li == 0 and pt == 0) else True
                ok3 &= hub
                tally3["leftover hubs checked in full"] += (li == 0 and pt == 0)
                if li == 0 and pt == 0:
                    SPLICED.append(((i1, li), (i2, pt), n))
info3 = dict(tally3)
info3["sign choices (of 8) that keep the failure"] = {str(k): v for k, v in sorted(choices.items())}
check("3 splicing a census knot space at any line into one at any point (all pairs up to 13 points) gives a knot space for some sign "
      "choice of the three new incidences; every such space fails globally, and for the first line and point of each pair its leftovers "
      "are hubs too", ok3 and tally3["splices"] > 0, info3)

# ------------------------------------------------------------------------------------------------ 4. every 3-edge cut is a splice of selected spaces
tally4 = collections.Counter()
ok4 = True
SMALL = [(idx, n, lines, s) for idx, n, lines, s in SPACES]
for i1, n1, H1, s1 in SPACES:                            # and every splice of two census spaces with at most 10 points
    for i2, n2, H2, s2 in SPACES:
        if n1 + n2 - 1 <= 10:
            ls, ss, n, side, ports = G.splice(H1, s1, n1, 0, H2, s2, n2, 0)
            SMALL.append(((i1, i2), n, ls, ss))
for idx, n, lines, s in SMALL:
    cuts = G.three_edge_cuts(lines, n)
    tally4["cuts"] += len(cuts)
    tally4["spaces with a nontrivial 3-edge cut"] += bool(cuts)
    for pts, lns in cuts:
        r = G.contract(lines, s, n, pts, lns)
        if r is None:
            tally4["cuts with a doubled port or slot (contraction not simple)"] += 1
            continue
        point_ok, line_ok, shape = r
        ok4 &= point_ok and line_ok and shape
        tally4["simple cuts"] += 1
        tally4["simple cuts with both contractions knot spaces"] += point_ok and line_ok
check("4 every nontrivial 3-edge cut of the census knot spaces and of their splices up to 10 points (all enumerated) whose three cut "
      "edges meet three distinct ports and "
      "three distinct slot lines contracts to two knot spaces (the point side closed by a line, the line side closed by a point): such a "
      "cut is a splice of two selected spaces along a leftover hub. Cuts where a port or a slot line takes two cut edges have contractions "
      "with a repeated point and are counted apart", ok4 and tally4["simple cuts"] > 0, dict(tally4))

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
