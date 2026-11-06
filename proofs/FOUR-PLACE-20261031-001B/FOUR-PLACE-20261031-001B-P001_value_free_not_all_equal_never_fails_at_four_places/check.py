#!/usr/bin/env python3
"""Checks for FOUR-PLACE-20261031-001B: value-free not-all-equal never fails on k-regular k-uniform systems for k >= 4.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Uses ticket A's library (bound by hash). Run with the repository's .venv (networkx)."""
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
A_DIR = ROOT / "proofs/FOUR-PLACE-20261031-001A/FOUR-PLACE-20261031-001A-P001_the_value_free_four_place_knots"
sys.path.insert(0, str(A_DIR))
import four_lib as F  # noqa: E402

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
status = {p: json.loads((ROOT / p).read_text()).get("status") for p in manifest["parent_bindings"] if p.endswith((".json",))}
check("0 dependency artifacts bound by hash; ticket A and PINNING C Proved and passed",
      not bad and all(s in ("Proved", "passed") for s in status.values()), {"mismatched": bad, "statuses": status})


# ------------------------------------------------------------------------------------------------ helpers: signed not-all-equal
def nae_ok(lines, signs, c):
    """every line has two literals of different value; signs[i][j] = 1 negates the j-th incidence of line i"""
    return all(len({(c >> p & 1) ^ s for p, s in zip(L, sg)}) == 2 for L, sg in zip(lines, signs))


def satisfiable(lines, signs, npts):
    return any(nae_ok(lines, signs, c) for c in range(1 << npts))


def signed_matrix(lines, signs, pts):
    idx = {p: i for i, p in enumerate(pts)}
    M = [[0] * len(pts) for _ in lines]
    for r, (L, sg) in enumerate(zip(lines, signs)):
        for p, s in zip(L, sg):
            M[r][idx[p]] = -1 if s else 1
    return M


# ------------------------------------------------------------------------------------------------ 1. the signed Seymour lemma
rng = random.Random(20261031)
tested = unsat = 0
lemma_bad = []
while unsat < 150:
    npts = rng.randint(3, 6)
    k = rng.choice((2, 3, 4)) if npts >= 4 else rng.choice((2, 3))
    m = rng.randint(npts - 1, npts + 3)
    lines = [tuple(rng.sample(range(npts), k)) for _ in range(m)]
    signs = [tuple(rng.randint(0, 1) for _ in range(k)) for _ in range(m)]
    tested += 1
    if satisfiable(lines, signs, npts):
        continue
    unsat += 1
    keep = list(range(m))                                      # shrink to a minimal unsatisfiable set of lines
    changed = True
    while changed:
        changed = False
        for i in list(keep):
            rest = [j for j in keep if j != i]
            if rest and not satisfiable([lines[j] for j in rest], [signs[j] for j in rest], npts):
                keep, changed = rest, True
                break
    E = [lines[j] for j in keep]
    S = [signs[j] for j in keep]
    pts = sorted({p for L in E for p in L})
    ok = len(E) >= len(pts)
    if ok and len(E) == len(pts):
        M = signed_matrix(E, S, pts)
        per = F.permanent01([sum(1 << i for i, x in enumerate(row) if x) for row in M], len(pts))
        ok = per > 0 and abs(F.det_int(M)) == per                # sign-nonsingular pattern
    if not ok:
        lemma_bad.append((E, S))
check("1 signed Seymour lemma on 150 random unsatisfiable signed systems (lines of 2-4 points): every minimal unsatisfiable set of lines "
      "covers at most as many points as it has lines, and when equal its signed incidence pattern is sign-nonsingular (|det| = #PM)",
      not lemma_bad, {"systems drawn": tested, "unsatisfiable": unsat, "violations": lemma_bad[:1]})
pinc = json.loads((ROOT / "proofs/PINNING-20261031-001C/PINNING-20261031-001C-P001_the_knot_is_the_only_law_with_mutual_selection/result.json").read_text())
cubic = next(v for k, v in pinc["checks"].items() if k.startswith("2 "))
check("1b the lemma's cubic instance, from PINNING-20261031-001C: on all 1,380,864 signings of cubic systems with n <= 6, not-all-equal "
      "fails exactly when the signed incidence matrix is sign-nonsingular", cubic["pass"], {"PINNING C check 2": cubic["info"]})

# ------------------------------------------------------------------------------------------------ 2. no sign-nonsingular 4-regular pattern
census = json.loads((ROOT / "research/MUTUAL-SELECTION-20261031-001C/census.json").read_text())
SYS = {n: F.systems(n, census) for n in (4, 5, 6, 7)}
sns_rows, digraph_ok = {}, True
for n, S in SYS.items():
    for i, lines in enumerate(S):
        exists, per = F.sns_signing_exists(lines)
        g = F.incidence_graph(lines)
        M = nx.bipartite.maximum_matching(g, top_nodes=[("l", j) for j in range(n)])
        match = {j: M[("l", j)][1] for j in range(n)}             # line j -> its matched point
        D = nx.DiGraph()
        D.add_nodes_from(range(n))
        for j, L in enumerate(lines):
            for p in L:
                if p != match[j]:
                    D.add_edge(match[j], p)                      # arcs from the matched point to the line's other points
        degs = {(D.in_degree(v), D.out_degree(v)) for v in D}
        strong = all(nx.is_strongly_connected(D.subgraph(c)) for c in nx.weakly_connected_components(D))
        digraph_ok &= degs == {(3, 3)} and strong
        sns_rows[f"n={n} #{i}"] = {"sign-nonsingular signing": exists, "perfect matchings": per}
fano = [(0, 1, 2), (0, 3, 4), (0, 5, 6), (1, 3, 5), (1, 4, 6), (2, 3, 6), (2, 4, 5)]
fano_sns, fano_per = F.sns_signing_exists(fano)
check("2 no incidence graph of a 4-regular 4-uniform system with n <= 7 has a sign-nonsingular signing (all signings up to row and column "
      "sign changes); with a perfect matching as diagonal each digraph has in- and out-degree 3 and strong weak components (Thomassen's "
      "hypothesis); control: the Fano plane's incidence graph (cubic, the knot's space) does have one",
      not any(r["sign-nonsingular signing"] for r in sns_rows.values()) and digraph_ok and fano_sns,
      {"systems": len(sns_rows), "any sign-nonsingular": any(r["sign-nonsingular signing"] for r in sns_rows.values()),
       "Fano control": {"sign-nonsingular signing": fano_sns, "perfect matchings": fano_per}, "rows": sns_rows})

# ------------------------------------------------------------------------------------------------ 3. satisfiability, k = 4 and k = 5
a_res = json.loads((A_DIR / "result.json").read_text())["checks"]
census_a = next(v for k, v in a_res.items() if k.startswith("6 "))
k5 = {}
for n in (5, 6):
    lines = [tuple(p for p in range(n) if p != j) for j in range(n)] if n == 6 else [tuple(range(5))] * 5
    members = [frozenset(s for s in itertools.product((0, 1), repeat=5) if s != v and s != tuple(1 - x for x in v))
               for v in itertools.product((0, 1), repeat=5) if v[0] == 0]
    per_line = [[F.line_mask(L, n, R) for R in members] for L in lines]
    full = (1 << (1 << n)) - 1
    stack, fails, total = [(0, full)], 0, 0
    while stack:
        i, acc = stack.pop()
        if i == len(lines):
            total += 1
            fails += acc == 0
            continue
        for mm in per_line[i]:
            stack.append((i + 1, acc & mm))
    k5[f"n={n}"] = f"{fails}/{total}"
check("3 satisfiability: k = 4, every signing of every 4-regular 4-uniform system with n <= 7 has a solution (ticket A, check 6); k = 5, "
      "every signing of the 5-regular 5-uniform systems K5,5 (n = 5) and K6,6 minus a perfect matching (n = 6) has one",
      census_a["pass"] and k5 == {"n=5": "0/1048576", "n=6": "0/16777216"}, {"k = 5 failing/total": k5})

# ------------------------------------------------------------------------------------------------ 4. rigidity of the pieces
nae = F.classes()["not-all-equal"]
kinds, pieces = set(), 0
for k in (3, 4, 5):
    for lines in F.structures(k):
        for rel in F.accepted_relations(lines, k, nae):
            pieces += 1
            kinds.add(len(rel))
check("4 rigidity (observed): every not-all-equal piece with three to five internal points accepts a not-all-equal relation (14 states) "
      "or everything (16), never nothing, never an equality", kinds == {14, 16},
      {"(piece, accepted relation) pairs": pieces, "accepted sizes": sorted(kinds)})

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
