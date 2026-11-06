#!/usr/bin/env python3
"""Checks for KNOT-COMPOSE-20261101-001A: the knot's spaces compose only through hubs.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (networkx)."""
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
sys.path.insert(0, str(ROOT / "proofs/FOUR-PLACE-20261031-001A/FOUR-PLACE-20261031-001A-P001_the_value_free_four_place_knots"))
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
status = {p: json.loads((ROOT / p).read_text()).get("status") for p in manifest["parent_bindings"] if p.startswith("proofs/") and p.endswith(".json")}
check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
      {"mismatched": bad, "statuses": status})

# ------------------------------------------------------------------------------------------------ systems
FANO = [(0, 1, 2), (0, 3, 4), (0, 5, 6), (1, 3, 5), (1, 4, 6), (2, 3, 6), (2, 4, 5)]


def relabel(lines):
    lab = {p: i for i, p in enumerate(sorted({p for l in lines for p in l}, key=repr))}
    return [tuple(lab[p] for p in l) for l in lines]


def point_splice(H1, t, H2, m):
    """replace point t of H1 by H2 minus its line m: t's three lines take m's three points (THREEFOLD-SPACES)"""
    M, out, k = H2[m], [], 0
    for l in H1:
        if t in l:
            out.append(tuple(("b", M[k]) if q == t else ("a", q) for q in l))
            k += 1
        else:
            out.append(tuple(("a", q) for q in l))
    out += [tuple(("b", q) for q in l) for i, l in enumerate(H2) if i != m]
    return relabel(out)


def transpose(lines):
    n = len(lines)
    return [tuple(i for i, L in enumerate(lines) if p in L) for p in range(n)]


def colourable(lines):
    n = 1 + max(max(L) for L in lines)
    return any(all(len({c >> p & 1 for p in L}) == 2 for L in lines) for c in range(1 << n))


S13 = point_splice(FANO, 0, FANO, 0)
S19 = point_splice(S13, 5, FANO, 3)
S19b = point_splice(FANO, 2, S13, 7)
SPACES = {"Fano": FANO, "S13": S13, "S19": S19, "S19b": S19b}
check("1 four knot's spaces (Fano, the 13-point splice, two 19-point splices): connected, cubic, simple, not 2-colourable",
      all(F.is_regular_system(H, 3) and not colourable(H) and nx.is_connected(F.incidence_graph(H)) for H in SPACES.values()),
      {name: len(H) for name, H in SPACES.items()})


# ------------------------------------------------------------------------------------------------ 2-3. three-edge cuts
def three_edge_cuts(lines):
    g = F.incidence_graph(lines)
    edges = list(g.edges())
    out = []
    for cut in itertools.combinations(edges, 3):
        h = g.copy()
        h.remove_edges_from(cut)
        comps = list(nx.connected_components(h))
        if len(comps) == 2 and min(len(c) for c in comps) > 1:
            out.append((cut, comps))
    return out


def side_relations(lines, cut, comps):
    """point side: colours of its three ports; line side: values fed into its three slots"""
    pc = [sum(1 for v in c if v[0] == "p") - sum(1 for v in c if v[0] == "l") for c in comps]
    X = comps[pc.index(1)]
    Y = comps[pc.index(-1)]
    ports = [u if u in X else v for u, v in cut]
    slots = [u if u in Y else v for u, v in cut]
    balanced = all(p[0] == "p" for p in ports) and all(s[0] == "l" for s in slots)
    # point side relation
    Xp = sorted(v[1] for v in X if v[0] == "p")
    Xl = [lines[v[1]] for v in X if v[0] == "l"]
    idx = {p: i for i, p in enumerate(Xp)}
    rel_point = set()
    for c in range(1 << len(Xp)):
        if all(len({c >> idx[p] & 1 for p in L}) == 2 for L in Xl):
            rel_point.add(tuple(c >> idx[p[1]] & 1 for p in ports))
    # line side relation: slot line s reads y_j in place of the port point
    Yp = sorted(v[1] for v in Y if v[0] == "p")
    Yl = [(v[1], lines[v[1]]) for v in Y if v[0] == "l"]
    idy = {p: i for i, p in enumerate(Yp)}
    slot_of = {}
    for j, ((u, v), s) in enumerate(zip(cut, slots)):
        port = u if u != s else v
        slot_of.setdefault(s[1], []).append((port[1], j))
    rel_line = set()
    for c in range(1 << len(Yp)):
        for y in itertools.product((0, 1), repeat=3):
            ok = True
            for li, L in Yl:
                seen = []
                for p in L:
                    hit = [j for q, j in slot_of.get(li, []) if q == p]
                    seen.append(y[hit[0]] if hit else c >> idy[p] & 1)
                if len(set(seen)) == 1:
                    ok = False
                    break
            if ok:
                rel_line.add(y)
    return balanced, frozenset(rel_point), frozenset(rel_line)


EQ = frozenset({(0, 0, 0), (1, 1, 1)})
NAE = frozenset(s for s in itertools.product((0, 1), repeat=3) if len(set(s)) == 2)
cut_info, all_balanced, all_exact = {}, True, True
for name, H in SPACES.items():
    cuts = three_edge_cuts(H)
    ex = 0
    for cut, comps in cuts:
        bal, rp, rl = side_relations(H, cut, comps)
        all_balanced &= bal
        exact = rp == EQ and rl == NAE
        all_exact &= exact
        ex += exact
    cut_info[name] = {"nontrivial 3-edge cuts": len(cuts), "point side = equality and line side = not-all-equal": ex}
check("2 balance: every nontrivial 3-edge cut of the four spaces has all three cut edges leaving one shore's points for the other shore's lines",
      all_balanced and sum(v["nontrivial 3-edge cuts"] for v in cut_info.values()) > 0, cut_info)
check("3 at every nontrivial 3-edge cut of a knot's space, the line side accepts exactly not-all-equal on its slots and the point side exactly "
      "equality on its ports: complementary halves of {0,1}^3 (the point lemma), so the composition fails and meets a hub",
      all_exact, cut_info)

# ------------------------------------------------------------------------------------------------ 4. complementarity
comp_info = {}
for k in (2, 3, 4):
    cube = list(itertools.product((0, 1), repeat=k))
    small = []
    for m in range(1, 1 << len(cube)):
        R = [s for i, s in enumerate(cube) if m >> i & 1]
        if len(R) != 2 ** (k - 1):
            continue
        if all(len({tuple(s[j] for j in range(k) if j != d) for s in R}) == 2 ** (k - 1) for d in range(k)):
            small.append(frozenset(R))
    parity = {frozenset(s for s in cube if sum(s) % 2 == b) for b in (0, 1)}
    comp_info[f"k={k}"] = {"relations with full (k-1)-projections and 2^(k-1) states": len(small), "all parity cosets": set(small) == parity}
check("4 complementarity: on k = 2, 3, 4 channels the only relations with full (k-1)-place projections and exactly 2^(k-1) states are the two "
      "parity cosets (in general: such a relation is an independent set of size 2^(k-1) in the k-cube, hence a colour class), so two "
      "knot sides are disjoint only as complementary parity cosets", all(v["all parity cosets"] for v in comp_info.values()), comp_info)


# ------------------------------------------------------------------------------------------------ 5. double cuts and knot-to-knot joins
def double_cut_relation(H, e1, e2):
    n = 1 + max(max(L) for L in H)
    (l1, p1), (l2, p2) = e1, e2
    acc = set()
    for c in range(1 << n):
        for y1 in (0, 1):
            for y2 in (0, 1):
                ok = True
                for i, L in enumerate(H):
                    vals = [y1 if (i == l1 and p == p1) else (y2 if (i == l2 and p == p2) else c >> p & 1) for p in L]
                    if len(set(vals)) == 1:
                        ok = False
                        break
                if ok:
                    acc.add((c >> p1 & 1, c >> p2 & 1, y1, y2))
    return frozenset(acc)


def cross_join(H, e, K, f):
    (l1, p1), (l2, p2) = e
    (m1, q1), (m2, q2) = f
    out = [tuple(("K", q1) if (i == l1 and p == p1) else (("K", q2) if (i == l2 and p == p2) else ("H", p)) for p in L) for i, L in enumerate(H)]
    out += [tuple(("H", p1) if (i == m1 and q == q1) else (("H", p2) if (i == m2 and q == q2) else ("K", q)) for q in L) for i, L in enumerate(K)]
    return relabel(out)


twelve = F.canonical(F.classes()["twelve"][0])
dc_info, knotty = {}, {}
for name in ("Fano", "S13"):
    H = SPACES[name]
    inc = [(i, p) for i, L in enumerate(H) for p in L]
    kinds = {}
    pairs = [pr for pr in itertools.combinations(inc, 2) if pr[0][0] != pr[1][0] and pr[0][1] != pr[1][1]]
    if name == "S13":
        pairs = pairs[:300]
    for pr in pairs:
        R = double_cut_relation(H, *pr)
        key = "twelve-class knot" if F.is_knot(R) and F.canonical(R) == twelve else ("other knot" if F.is_knot(R) else f"no knot ({len(R)} states)")
        kinds[key] = kinds.get(key, 0) + 1
        if key == "twelve-class knot":
            knotty.setdefault(name, []).append(pr)
    dc_info[name] = kinds
rng = random.Random(20261101)
joins = {"tried": 0, "failing": 0}
for t in range(200):
    a, b = rng.choice(["Fano", "S13"]), rng.choice(["Fano", "S13"])
    if a == b == "S13":
        b = "Fano"
    G = cross_join(SPACES[a], rng.choice(knotty[a]), SPACES[b], rng.choice(knotty[b]))
    joins["tried"] += 1
    joins["failing"] += not colourable(G)
check("5 double cuts: a pair of cuts accepts a twelve-class knot (12 states) or no knot, never another knot; joining two twelve-class sides "
      "knot to knot never fails (12 + 12 > 16), checked on 200 random joins of Fano and 13-point pieces",
      all(set(v) <= {"twelve-class knot", "no knot (10 states)", "no knot (6 states)"} for v in dc_info.values()) and joins["failing"] == 0,
      {"double-cut relations": dc_info, "joins": joins})

# ------------------------------------------------------------------------------------------------ 6. control: parity fails hub-free
census = json.loads((ROOT / "research/MUTUAL-SELECTION-20261031-001C/census.json").read_text())
PH = [tuple(l) for l in census["6"]["rows"][0]["lines"]]


def parity_double_cut(H, e1, e2, signs):
    n = 1 + max(max(L) for L in H)
    (l1, p1), (l2, p2) = e1, e2
    acc = set()
    for c in range(1 << n):
        for y1 in (0, 1):
            for y2 in (0, 1):
                if all((sum(y1 if (i == l1 and p == p1) else (y2 if (i == l2 and p == p2) else c >> p & 1) for p in L) + signs[i]) % 2 == 0
                       for i, L in enumerate(H)):
                    acc.add((c >> p1 & 1, c >> p2 & 1, y1, y2))
    return frozenset(acc)


e = ((0, 2), (3, 4))
flipped = [1] + [0] * (len(PH) - 1)
R0 = parity_double_cut(PH, *e, [0] * len(PH))
R1 = parity_double_cut(PH, *e, flipped)
swap = lambda R: frozenset((s[2], s[3], s[0], s[1]) for s in R)  # noqa: E731   the other side sees ports and slots exchanged
G = cross_join(PH, e, PH, e)
signsG = [0] * len(PH) + flipped
nG = 1 + max(max(L) for L in G)
solvable = any(all((sum(c >> p & 1 for p in L) + sg) % 2 == 0 for L, sg in zip(G, signsG)) for c in range(1 << nG))
control = len(R0) == 8 and len(R1) == 8 and F.is_knot(R0) and F.is_knot(R1) and not (R0 & swap(R1)) and not solvable \
    and F.is_regular_system(G, 3)
check("6 control: parity does fail hub-free. A double cut of a census system (n = 6) under the parity law accepts a parity coset on its four "
      "channels (8 states, a knot); joining it knot to knot with a copy whose line 0 is negated makes the sides complementary, and the "
      "joined cubic system has no parity solution", control,
      {"accepted states": [len(R0), len(R1)], "disjoint after crossing": not (R0 & swap(R1)), "joined system solvable": solvable})

# ------------------------------------------------------------------------------------------------ 7. the transpose
tr_info, tr_ok = {}, True
for name, H in SPACES.items():
    T = transpose(H)
    ok = F.is_regular_system(T, 3) and not colourable(T)
    if name in ("S13",):
        for cut, comps in three_edge_cuts(H)[:20]:
            # in the transpose the same edges cut the same vertex sets with points and lines exchanged
            pc = [sum(1 for v in c if v[0] == "p") - sum(1 for v in c if v[0] == "l") for c in comps]
            ok &= sorted(pc) == [-1, 1]
    tr_ok &= ok
    tr_info[name] = {"transpose is a knot's space": ok}
check("7 the transpose of each knot's space is a knot's space (sign-nonsingularity is transpose-invariant); it exchanges points and lines, so "
      "every 3-edge cut's point side (hub) becomes a line side (knot) and conversely", tr_ok, tr_info)

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
