#!/usr/bin/env python3
"""Check of SOFT-HUB-20261024-001C-P001 (standard library only, seed 20261024).

The open knot S excludes 000, 011 and 101 (centre c = 110: allowed tuples have 0, 1 or 3 places differing from c). A tree gadget is
a connected native network of S with pins, free legs and three terminals whose knots and internal edges form a tree (no cycle, no
loop). For an axis u: s_u = sum_i F(u + e_i) F(u-bar + e_i).
Checks:
- on random tree gadgets, every pair (sigma with terminals u, tau with terminals u-bar) is handled for each terminal i: separated
  pairs by exchanging the difference component of terminal 1 (Lemma 2 of SOFT-HUB-20261024-001A-P001); linked pairs by the arm map:
  walk from terminal i along the tree path towards the median of the three terminal knots, stop at the first knot where all three
  slots differ (b), and flip the walked edges on the configuration that has no defect at b. The check confirms that every knot
  before b has exactly its two path slots differing, that both images are valid with terminal values u + e_i or u-bar + e_i, that the
  arm images are injective, and that F(u)F(u-bar) <= s_u + F(u + e_i)F(u-bar) + F(u)F(u-bar + e_i);
- the stored eight-knot tree gadget has hub ratio 12/11 along the axis 001;
- the stored seven-knot gadget with a double edge has two different linked pairs with the same image under the arm map that walks
  along the difference itself (no tree to route it);
- the inequality holds on 4,000 random gadgets with up to 12 knots, trees and cyclic (exact counts by variable elimination), and on all
  annealed gadgets of SOFT-HUB-20261024-001B-E001 (their exact F values in rows.jsonl).
Controls: flipping the arm on the configuration that is full at b instead gives an invalid assignment on some pair; the planted
function [10, 1, 1, 1, 1, 1, 1, 10] violates the inequality.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
"""

from __future__ import annotations

import itertools
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
B_ROWS = ROOT / "artifacts/SOFT-HUB-20261024-001B/SOFT-HUB-20261024-001B-E001_strong_hubs/rows.jsonl"
CUBE = list(itertools.product((0, 1), repeat=3))
AXES = [(0, 0, 0), (0, 0, 1), (0, 1, 0), (1, 0, 0)]
CENTRE = (1, 1, 0)
S = frozenset(t for t in CUBE if t not in {(0, 0, 0), (0, 1, 1), (1, 0, 1)})

TREE_EXAMPLE = [[["E", 0], ["E", 1], ["P", 0]], [["F"], ["P", 1], ["E", 2]], [["E", 2], ["T", 2], ["E", 1]], [["F"], ["P", 1], ["E", 3]],
                [["E", 4], ["T", 1], ["E", 5]], [["P", 0], ["P", 1], ["E", 6]], [["E", 4], ["E", 6], ["E", 0]], [["E", 5], ["E", 3], ["T", 0]]]
CYCLIC_EXAMPLE = [[["E", 0], ["E", 1], ["E", 2]], [["E", 3], ["E", 4], ["E", 3]], [["E", 2], ["E", 5], ["P", 0]], [["T", 1], ["P", 1], ["E", 6]],
                  [["T", 2], ["E", 6], ["E", 7]], [["E", 0], ["T", 0], ["E", 1]], [["E", 5], ["E", 7], ["E", 4]]]


def comp(x):
    return tuple(1 - b for b in x)


def xor(x, y):
    return tuple(a ^ b for a, b in zip(x, y))


def unit(i):
    return tuple(int(j == i) for j in range(3))


def split_sum(F, u):
    return sum(F[xor(u, unit(i))] * F[xor(comp(u), unit(i))] for i in range(3))


def arm_rhs(F, u, i):
    return split_sum(F, u) + F[xor(u, unit(i))] * F[comp(u)] + F[u] * F[xor(comp(u), unit(i))]


def defects(t):
    return sum(1 for p in range(3) if t[p] != CENTRE[p])


def parse(g):
    return len(g), {(v, p): tuple(g[v][p]) for v in range(len(g)) for p in range(3)}


def connected(n, a):
    parent = list(range(n))

    def find(z):
        while parent[z] != z:
            parent[z] = parent[parent[z]]
            z = parent[z]
        return z
    ends = {}
    for (v, p), k in a.items():
        if k[0] == "E":
            ends.setdefault(k[1], []).append(v)
    for vs in ends.values():
        parent[find(vs[0])] = find(vs[1])
    return len({find(v) for v in range(n)}) == 1


def is_tree(n, a):
    edges = {}
    for (v, p), k in a.items():
        if k[0] == "E":
            edges.setdefault(k[1], []).append(v)
    return len(edges) == n - 1 and all(len(set(vs)) == 2 for vs in edges.values()) and connected(n, a)


def random_gadget(rng, n, tree=None):
    slots = [(v, p) for v in range(n) for p in range(3)]
    for _ in range(4000):
        rng.shuffle(slots)
        a = {slots[k]: ("T", k) for k in range(3)}
        rest = slots[3:]
        m = len(rest)
        if tree:
            nedge = n - 1
        else:
            npf = rng.randint(0, max(0, m - 2 * (n - 1)))
            if (m - npf) % 2:
                npf += 1
            nedge = (m - npf) // 2
        npf = m - 2 * nedge
        if npf < 0:
            continue
        for s in rest[:npf]:
            a[s] = ("P", rng.randint(0, 1)) if rng.random() < 0.7 else ("F",)
        pr = rest[npf:]
        for i in range(0, len(pr), 2):
            a[pr[i]] = a[pr[i + 1]] = ("E", i // 2)
        if connected(n, a) and (not tree or is_tree(n, a)):
            return a
    return None


def item(a, s):
    k = a[s]
    return ("E", k[1]) if k[0] == "E" else ("T", k[1]) if k[0] == "T" else ("F", s)


def local(a, conf, v):
    return tuple(conf[item(a, (v, p))] if a[(v, p)][0] != "P" else a[(v, p)][1] for p in range(3))


def configurations(n, a):
    items = sorted({item(a, s) for s in a if a[s][0] != "P"})
    by = {x: [] for x in CUBE}
    for vals in itertools.product((0, 1), repeat=len(items)):
        conf = dict(zip(items, vals))
        if all(local(a, conf, v) in S for v in range(n)):
            by[tuple(conf[("T", k)] for k in range(3))].append(conf)
    return by


def components(n, a, diff):
    parent = {z: z for z in diff}

    def find(z):
        while parent[z] != z:
            parent[z] = parent[parent[z]]
            z = parent[z]
        return z
    for v in range(n):
        its = [item(a, (v, p)) for p in range(3) if a[(v, p)][0] != "P" and item(a, (v, p)) in diff]
        for z in its[1:]:
            parent[find(its[0])] = find(z)
    out = {}
    for z in diff:
        out.setdefault(find(z), set()).add(z)
    return list(out.values())


def tree_route(n, a, i):
    """list of (knot, entry slot, exit slot or None) from terminal i's knot to the median of the three terminal knots"""
    adj = {v: [] for v in range(n)}
    ends = {}
    for (v, p), k in a.items():
        if k[0] == "E":
            ends.setdefault(k[1], []).append((v, p))
    for e, ((v, p), (w, q)) in ends.items():
        adj[v].append((w, p, q))
        adj[w].append((v, q, p))
    tk = {k[1]: s for s, k in a.items() if k[0] == "T"}

    def path(x, y):
        prev = {x: None}
        stack = [x]
        while stack:
            z = stack.pop()
            for w, p, q in adj[z]:
                if w not in prev:
                    prev[w] = (z, p, q)
                    stack.append(w)
        out = []
        z = y
        while prev[z] is not None:
            out.append((prev[z][0], z, prev[z][1], prev[z][2]))
            z = prev[z][0]
        return list(reversed(out))
    kn = [tk[k][0] for k in range(3)]
    # median: the knot on all three pairwise paths
    def nodes(x, y):
        return {x} | {st[1] for st in path(x, y)}
    common = nodes(kn[0], kn[1]) & nodes(kn[0], kn[2]) & nodes(kn[1], kn[2])
    assert len(common) == 1
    mu = common.pop()
    steps = path(kn[i], mu)
    route = []
    entry = tk[i][1]
    cur = kn[i]
    for (z, w, p, q) in steps:
        route.append((cur, entry, p))
        cur, entry = w, q
    route.append((cur, entry, None))
    return route


def arm_map_tree(n, a, s, t, i, route):
    """returns (side, image, ok_structure) for a linked pair"""
    diff = {z for z in s if s[z] != t[z]}
    walked = [("T", i)]
    ok = True
    for (v, entry, exit_) in route:
        dslots = [p for p in range(3) if a[(v, p)][0] != "P" and item(a, (v, p)) in diff]
        if len(dslots) == 3:
            side = "s" if defects(local(a, s, v)) == 0 else "t"
            ok &= {defects(local(a, s, v)), defects(local(a, t, v))} == {0, 3}
            img = (dict(s), dict(t))
            tgt = img[0] if side == "s" else img[1]
            for z in walked:
                tgt[z] = 1 - tgt[z]
            return side, img, ok, walked
        ok &= exit_ is not None and sorted(dslots) == sorted([entry, exit_])
        walked.append(item(a, (v, exit_)))
    return None, None, False, walked


def check_tree_gadget(n, a, by, F, stats):
    for u in AXES:
        if F[u] * F[comp(u)] == 0 or F[u] * F[comp(u)] > 5000:
            continue
        for i in range(3):
            route = tree_route(n, a, i)
            sep = link = 0
            images = set()
            for s in by[u]:
                for t in by[comp(u)]:
                    diff = {z for z in s if s[z] != t[z]}
                    c1 = next(c for c in components(n, a, diff) if ("T", 0) in c)
                    if {z[1] for z in c1 if z[0] == "T"} != {0, 1, 2}:
                        sep += 1
                        continue
                    link += 1
                    side, (s2, t2), ok, _ = arm_map_tree(n, a, s, t, i, route)
                    stats["arm structure as stated"] &= ok
                    stats["arm images valid"] &= all(local(a, s2, v) in S and local(a, t2, v) in S for v in range(n))
                    want = (xor(u, unit(i)), comp(u)) if side == "s" else (u, xor(comp(u), unit(i)))
                    stats["arm images on the stated patterns"] &= (tuple(s2[("T", k)] for k in range(3)),
                                                                     tuple(t2[("T", k)] for k in range(3))) == want
                    key = (side, tuple(sorted(s2.items())), tuple(sorted(t2.items())))
                    stats["arm images injective"] &= key not in images
                    images.add(key)
            stats["cases"] += 1
            stats["linked pairs"] += link
            stats["inequality holds"] &= F[u] * F[comp(u)] <= arm_rhs(F, u, i)


def exact_F(n, a):
    """variable elimination over dictionaries with Python integers"""
    factors = []
    for v in range(n):
        kinds = [a[(v, p)] for p in range(3)]
        vars_ = [("e", k[1]) if k[0] == "E" else ("t", k[1]) if k[0] == "T" else ("f", v, p) if k[0] == "F" else None
                 for p, k in enumerate(kinds)]
        uniq = sorted({x for x in vars_ if x is not None}, key=str)
        tab = {}
        for vals in itertools.product((0, 1), repeat=len(uniq)):
            asg = dict(zip(uniq, vals))
            if tuple(asg[x] if x is not None else kinds[p][1] for p, x in enumerate(vars_)) in S:
                tab[vals] = tab.get(vals, 0) + 1
        factors.append((uniq, tab))
    for x in sorted({x for vs, _ in factors for x in vs if x[0] != "t"}, key=str):
        inv = [f for f in factors if x in f[0]]
        rest = [f for f in factors if x not in f[0]]
        allv = sorted({y for vs, _ in inv for y in vs}, key=str)
        outv = [y for y in allv if y != x]
        tab = {}
        for vals in itertools.product((0, 1), repeat=len(allv)):
            asg = dict(zip(allv, vals))
            prod = 1
            for vs, tb in inv:
                prod *= tb.get(tuple(asg[y] for y in vs), 0)
                if not prod:
                    break
            if prod:
                k = tuple(asg[y] for y in outv)
                tab[k] = tab.get(k, 0) + prod
        rest.append((outv, tab))
        factors = rest
    F = {}
    for xx in CUBE:
        asg = {("t", k): xx[k] for k in range(3)}
        prod = 1
        for vs, tb in factors:
            prod *= tb.get(tuple(asg[y] for y in vs), 0)
        F[xx] = prod
    return F


def walk_arm(n, a, s, t):
    """arm of terminal 1 found by walking along the difference itself (no tree)"""
    where = {}
    for (v, p), k in a.items():
        if k[0] != "P":
            where.setdefault(item(a, (v, p)), []).append((v, p))
    diff = {z for z in s if s[z] != t[z]}
    cur, came = ("T", 0), None
    walked = [cur]
    for _ in range(100):
        v, p = [vp for vp in where[cur] if vp != came][0]
        dslots = [q for q in range(3) if a[(v, q)][0] != "P" and item(a, (v, q)) in diff]
        if len(dslots) == 3:
            return walked, v
        if len(dslots) != 2:
            return None
        q = [q for q in dslots if q != p][0]
        cur, came = item(a, (v, q)), (v, q)
        if cur[0] != "E":
            return None
        walked.append(cur)
    return None


def main() -> int:
    manifest = json.loads((HERE / "manifest.json").read_text())
    result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
              "proof": manifest["proof"], "claim": manifest["claim"], "foundation_contract": manifest["foundation_contract"],
              "semantic_domains": manifest["semantic_domains"], "evidence_modes": manifest["evidence_modes"],
              "thesis_alignment": manifest["thesis_alignment"], "safe_conclusions": manifest["safe_to_conclude"]}
    rng = random.Random(20261024)

    # Theorem 1 on random tree gadgets
    stats = {"tree gadgets": 0, "cases": 0, "linked pairs": 0, "arm structure as stated": True, "arm images valid": True,
             "arm images on the stated patterns": True, "arm images injective": True, "inequality holds": True}
    full_side_fails = False
    while stats["tree gadgets"] < 300:
        n = rng.randint(1, 9)
        a = random_gadget(rng, n, tree=True)
        if a is None or len({item(a, s) for s in a if a[s][0] != "P"}) > 14:
            continue
        by = configurations(n, a)
        F = {x: len(by[x]) for x in CUBE}
        stats["tree gadgets"] += 1
        check_tree_gadget(n, a, by, F, stats)
        # control (i): flip the arm on the configuration that is full at b
        if not full_side_fails:
            for u in AXES:
                for s in by[u]:
                    for t in by[comp(u)]:
                        diff = {z for z in s if s[z] != t[z]}
                        c1 = next(c for c in components(n, a, diff) if ("T", 0) in c)
                        if {z[1] for z in c1 if z[0] == "T"} != {0, 1, 2}:
                            continue
                        side, img, ok, walked = arm_map_tree(n, a, s, t, 0, tree_route(n, a, 0))
                        wrong = (dict(s), dict(t))
                        tgt = wrong[1] if side == "s" else wrong[0]
                        for z in walked:
                            tgt[z] = 1 - tgt[z]
                        if not all(local(a, wrong[0], v) in S and local(a, wrong[1], v) in S for v in range(n)):
                            full_side_fails = True
                            break
                    if full_side_fails:
                        break
                if full_side_fails:
                    break

    # Corollary 2: the stored tree gadget
    n, a = parse(TREE_EXAMPLE)
    Ft = exact_F(n, a)
    off = max(Ft[x] for x in CUBE if x not in ((0, 0, 1), (1, 1, 0)))
    tree_example = {"is a tree": is_tree(n, a), "F": [Ft[x] for x in CUBE],
                    "hub ratio along 001 is 12/11": min(Ft[(0, 0, 1)], Ft[(1, 1, 0)]) * 11 == 12 * off}

    # Proposition 3: the stored cyclic gadget collides under the walking arm map
    n, a = parse(CYCLIC_EXAMPLE)
    by = configurations(n, a)
    images = {}
    collision = None
    for u in AXES:
        for s in by[u]:
            for t in by[comp(u)]:
                diff = {z for z in s if s[z] != t[z]}
                c1 = next(c for c in components(n, a, diff) if ("T", 0) in c)
                if {z[1] for z in c1 if z[0] == "T"} != {0, 1, 2}:
                    continue
                res = walk_arm(n, a, s, t)
                if res is None:
                    continue
                walked, b = res
                side = "s" if defects(local(a, s, b)) == 0 else "t"
                img = (dict(s), dict(t))
                tgt = img[0] if side == "s" else img[1]
                for z in walked:
                    tgt[z] = 1 - tgt[z]
                key = (side, tuple(sorted(img[0].items())), tuple(sorted(img[1].items())))
                pair = (tuple(sorted(s.items())), tuple(sorted(t.items())))
                if key in images and images[key] != pair and collision is None:
                    collision = "".join(map(str, u))
                images.setdefault(key, pair)
    cyclic_example = {"has a cycle": not is_tree(n, a), "collision found on axis": collision}

    # Conjecture 4: evidence on random gadgets and on ticket B's annealed gadgets
    ev = {"random gadgets": 0, "trees among them": 0, "axis-terminal cases": 0, "failures": 0}
    while ev["random gadgets"] < 4000:
        n = rng.randint(1, 12)
        a = random_gadget(rng, n)
        if a is None:
            continue
        F = exact_F(n, a)
        ev["random gadgets"] += 1
        ev["trees among them"] += is_tree(n, a)
        for u in AXES:
            for i in range(3):
                ev["axis-terminal cases"] += 1
                ev["failures"] += F[u] * F[comp(u)] > arm_rhs(F, u, i)
    b_rows = [json.loads(line) for line in B_ROWS.read_text().splitlines()]
    ann = [r for r in b_rows if r["part"] == "anneal"]
    b_fail = 0
    b_tight = 0
    for r in ann:
        F = dict(zip(CUBE, r["F"]))
        for u in AXES:
            for i in range(3):
                b_fail += F[u] * F[comp(u)] > arm_rhs(F, u, i)
                b_tight += F[u] * F[comp(u)] == arm_rhs(F, u, i) and F[u] * F[comp(u)] > 0
    ev["ticket B annealed gadgets"] = len(ann)
    ev["ticket B failures"] = b_fail
    ev["ticket B cases with equality"] = b_tight

    planted = dict(zip(CUBE, [10, 1, 1, 1, 1, 1, 1, 10]))
    controls = {"flipping the arm on the full side gives an invalid assignment on some pair": full_side_fails,
                "the planted function violates the inequality": all(planted[(0, 0, 0)] * planted[(1, 1, 1)] > arm_rhs(planted, (0, 0, 0), i)
                                                                    for i in range(3))}
    ok = (stats["tree gadgets"] == 300 and stats["linked pairs"] > 0 and all(v is True for k, v in stats.items() if isinstance(v, bool))
          and tree_example["is a tree"] and tree_example["hub ratio along 001 is 12/11"]
          and cyclic_example["has a cycle"] and cyclic_example["collision found on axis"] is not None
          and ev["failures"] == 0 and ev["ticket B failures"] == 0 and ev["ticket B annealed gadgets"] == 336 and all(controls.values()))
    result["checks"] = {"Theorem 1 on tree gadgets": stats, "Corollary 2: tree example": tree_example,
                        "Proposition 3: cyclic example": cyclic_example, "Conjecture 4: evidence": ev}
    result["controls"] = controls
    result["status"] = "passed" if ok else "failed"
    result["failures"] = [] if ok else ["a check or control did not come out as stated in proof.md"]
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(text)
    else:
        old = (HERE / "result.json").read_text() if (HERE / "result.json").exists() else None
        print("result.json matches" if old == text else "result.json differs from a fresh run")
        ok = ok and old == text
    print(json.dumps({"status": result["status"], "checks": result["checks"], "controls": controls}, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
