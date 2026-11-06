#!/usr/bin/env python3
"""Checks for HANDLE-LOCALITY-20261103-001B: where creation happens.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy, networkx). About half an hour."""
import collections
import hashlib
import itertools
import json
import sys
import time
from pathlib import Path

import networkx as nx
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "proofs/HANDLE-EMERGENCE-20261102-001A/HANDLE-EMERGENCE-20261102-001A-P001_a_planar_removed_side_creates_nothing"))
sys.path.insert(0, str(ROOT / "proofs/SPLICE-TREE-20261102-001C/SPLICE-TREE-20261102-001C-P001_opened_cuts_interact"))
import planar_lib as PL  # noqa: E402
import elim_lib as E  # noqa: E402
import join_lib as J  # noqa: E402

G = PL.G
T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:900], round(time.time() - T0, 1), "s", flush=True)
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

# ------------------------------------------------------------------------------------------------ 1. the join-based method
info1 = collections.Counter()
ok1 = True
for nidx in (6, 14, 21, 58):
    HS, sS, nS = SP[nidx]
    for fidx in (1, 6):
        HF, sF, nF = SP[fidx]
        for L in range(len(HS)):
            ls, ss, n, side, ports = G.splice(HS, sS, nS, L, HF, sF, nF, 0)
            n_rest1 = len(HS) - 1
            lines, signs, far, AF = J.far_side(G, HS, sS, nS, L, HF, sF, nF)
            same = [tuple(x) for x in ls[n_rest1:]] == [tuple(x) for x in lines] and [list(x) for x in ss[n_rest1:]] == [list(x) for x in signs]
            ok1 &= same
            info1["far sides equal to the splice's (twist chosen from the far side alone)"] += same
            for Mg in range(n_rest1):
                M = Mg if Mg < L else Mg + 1
                AN = np.array(G.removal(HS, sS, nS, M), dtype=np.int8)
                if len({tuple(int(b) for b in r) for r in AN[:, list(HS[L])]}) != 6:
                    continue
                cj = set(J.circuits(AN, list(range(nS)), AF, far, list(HS[L]), 4))
                T = np.array(G.removal(ls, ss, n, Mg), dtype=np.int8)
                cb = {frozenset(E.bits(m)) for m in E.circuits(T, n, 4)}
                ok1 &= cj == cb
                info1["splices with every circuit up to four points equal to brute force"] += cj == cb
                info1["splices compared"] += 1
check("1 the join-based method: on census 6, 14, the Fano plane and census 58 spliced into K4^(3) and census 6 at every line, the far side "
      "built with the twist chosen from the far side alone equals the splice's, and at every removal with six port patterns the circuits "
      "up to four points found from the two sides by the join lemma equal those of the whole splice", ok1 and info1["splices compared"] > 0,
      dict(info1))


# ------------------------------------------------------------------------------------------------ 2. the creation map
def lab(space, name):
    H, s, n = space
    return (H, s, n, [name] * len(H), [name] * n)


def far_plane_point(S, avoid):
    """the point of the plane piece farthest from the named pieces in the incidence graph (lowest label on ties)"""
    H, s, n, ll, pl = S
    g = nx.Graph()
    g.add_edges_from((("p", q), ("l", k)) for k, L in enumerate(H) for q in L)
    d = nx.multi_source_dijkstra_path_length(g, [("p", q) for q in range(n) if pl[q] in avoid])
    return max((q for q in range(n) if pl[q] == "plane"), key=lambda q: (d[("p", q)], -q))


def creation_map(S, FARS, maxsize, info, tag, only_plane_L=False, only_handle_M=False):
    """new crossing knots at every (removal, gluing line) with six patterns; returns the list of records"""
    HS, sS, nS, llab, plab = S
    g = nx.Graph()
    g.add_edges_from((("p", q), ("l", k)) for k, L in enumerate(HS) for q in L)
    atoms = sorted(set(llab) - {"plane"})
    dist = {a: nx.multi_source_dijkstra_path_length(g, [("p", q) for q in range(nS) if plab[q] == a] +
                                                    [("l", k) for k in range(len(HS)) if llab[k] == a]) for a in atoms}
    src_ = (ROOT / "proofs/PLANAR-COMPOSE-20261102-001A/PLANAR-COMPOSE-20261102-001A-P001_the_hub_reaches_the_ports_on_a_plane_side/check.py").read_text()
    scope = {}
    exec(src_[src_.index("def tied_to("):src_.index("def odd_index(")], scope)
    records = []
    for M in range(len(HS)):
        if only_handle_M and llab[M] == "plane":
            continue
        AN = np.array(G.removal(HS, sS, nS, M), dtype=np.int8)
        hub = scope["tied_to"](AN, HS[M][0], nS)
        for L in range(len(HS)):
            if L == M or (only_plane_L and llab[L] != "plane"):
                continue
            X = list(HS[L])
            if len({tuple(int(b) for b in r) for r in AN[:, X]}) != 6:
                continue
            for fname, F in FARS:
                newraw, rep, far, AF = J.new_knots(E, G, AN, HS, sS, nS, L, F, maxsize)
                dM = dist[llab[M]][("l", L)] if llab[M] != "plane" else None
                records.append((M, L, fname, len(newraw), dM))
                info["%s: gluing line in %s, removal in %s, far side %s: %s" % (
                    tag, "a handle" if llab[L] != "plane" else "the plane piece", "a handle" if llab[M] != "plane" else "the plane piece",
                    fname, "creates" if newraw else "no new knot")] += 1
                for m in newraw:
                    pts = E.bits(m)
                    U = [q for q in pts if q < nS]
                    pinned = False
                    if len(U) == 2:
                        for u in itertools.product((0, 1), repeat=2):
                            rows = AN[(AN[:, U[0]] == u[0]) & (AN[:, U[1]] == u[1])]
                            pinned |= len({tuple(int(b) for b in r) for r in rows[:, X]}) == 1
                    info["%s: new knots, gluing line in %s: %d near + %d far points, %s, %s" % (
                        tag, "a handle" if llab[L] != "plane" else "the plane piece", len(U), len(pts) - len(U),
                        "pinned" if pinned else "not pinned", "through the hub" if any(q in hub for q in U) else "off the hub")] += 1
                if newraw and llab[L] == "plane":
                    info["%s: creating plane gluing lines at distance %d from the opened handle" % (tag, dM)] += 1
    return records, llab


FARS = [("K4^(3)", SP[1]), ("census 6", SP[6]), ("the Fano plane", SP[21]), ("census 58", SP[58])]
FANO = SP[21]
NEAR = []
for seed in (0, 1):
    Hp = lab(PL.to_space(PL.grow(10, seed)), "plane")
    NEAR.append(("handle at a point, seed %d" % seed, "point", J.splice_pieces(G, lab(FANO, "handle A"), Hp, 0, 0)))
    NEAR.append(("handle at a line, seed %d" % seed, "line", J.splice_pieces(G, Hp, lab(FANO, "handle A"), 0, 0)))
for seed in (0, 1):
    Hp = lab(PL.to_space(PL.grow(10, seed)), "plane")
    S1 = J.splice_pieces(G, lab(FANO, "handle A"), Hp, 0, 0)
    NEAR.append(("two handles at points, seed %d" % seed, "point", J.splice_pieces(G, lab(FANO, "handle B"), S1, 0, far_plane_point(S1, ("handle A",)))))
info2 = collections.Counter()
ok2 = True
for name, attach, S in NEAR:
    records, llab = creation_map(S, FARS, 3, info2, name.split(",")[0])
    for (M, L, fname, k, dM) in records:
        if llab[L] == "plane" and llab[M] == "plane":
            ok2 &= k == 0                                  # neither line on a handle: nothing new
        if llab[L] == "plane" and attach == "line":
            ok2 &= k == 0                                  # a handle attached at a line never creates outside itself
check("2 the creation map: six near sides of 16 and 22 points (the Fano plane spliced into a 10-point plane space at a point or at a line, "
      "both seeds, and two Fano planes at two points), spliced at every gluing line with six patterns into K4^(3), census 6, the Fano plane "
      "and census 58, new crossing knots exact up to three points: no new knot when neither the gluing line nor the removed line lies on a "
      "handle; no new knot at a plane gluing line when the handle is attached at a line; creation at plane gluing lines otherwise only with "
      "the removal inside a handle attached at a point", ok2 and sum(info2.values()) > 0, dict(info2))

# ------------------------------------------------------------------------------------------------ 3. the reach of an opened handle
info3 = collections.Counter()
reach = collections.Counter()
for size, seed in ((12, 0), (12, 1), (14, 0)):
    Hp = lab(PL.to_space(PL.grow(size, seed)), "plane")
    S = J.splice_pieces(G, lab(FANO, "handle A"), Hp, 0, 0)
    records, llab = creation_map(S, FARS[:3], 3, info3, "handle at a point, plane %d/%d" % (size, seed), only_plane_L=True, only_handle_M=True)
    for (M, L, fname, k, dM) in records:
        reach[(dM, k > 0)] += 1
far_reach = max(d for (d, c) in reach if c)
check("3 the reach of an opened handle: with the Fano plane attached at a point of plane spaces of 12 and 14 points and the removal inside "
      "it, plane gluing lines create at distance 1, 3 and 5 from the handle (in the incidence graph), so the effect is not confined to the "
      "lines through the cut", far_reach >= 5 and all((d, True) in reach for d in (1, 3, 5)),
      dict(info3, **{"reach: plane gluing lines at distance %d, %s" % (d, "creating" if c else "not creating"): v for (d, c), v in reach.items()}))

# ------------------------------------------------------------------------------------------------ 4. up to four points
info4 = collections.Counter()
ok4 = True
for name, attach, S in NEAR[:4]:
    records, llab = creation_map(S, FARS[:2], 4, info4, name.split(",")[0])
    for (M, L, fname, k, dM) in records:
        if llab[L] == "plane" and (llab[M] == "plane" or attach == "line"):
            ok4 &= k == 0
check("4 up to four points: on the four one-handle near sides with far sides K4^(3) and census 6, new crossing knots exact up to four "
      "points obey the same two prohibitions", ok4 and sum(info4.values()) > 0, dict(info4))

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
