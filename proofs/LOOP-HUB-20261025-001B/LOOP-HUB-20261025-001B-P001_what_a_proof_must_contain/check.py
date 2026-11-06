#!/usr/bin/env python3
"""Check of LOOP-HUB-20261025-001B-P001 (standard library only, seed 20261025).

The open knot S excludes 000, 011 and 101 (centre c = 110). Gadgets: connected native networks of S with pins, free legs and three
terminals. For an axis u and terminal i: lhs = F(u)F(u-bar), rhs = s_u + F(u + e_i)F(u-bar) + F(u)F(u-bar + e_i).
Checks:
- Lemma 1 on random gadgets with and without cycles: for every linked difference pattern d, the configurations compatible with d
  (sigma in Conf(u), sigma xor d in Conf) map into those compatible with d' = d xor arm(d) with terminals j, k equal to u_j, u_k, by
  sigma -> sigma xor arm(d) when sigma is empty at the first branching knot and sigma -> sigma otherwise; the images are compatible
  and the map is injective; on tree gadgets d -> d' is injective on linked patterns;
- Proposition 2: on random non-negative integer functions, rhs - lhs for the axes u and u + e_i equals (agree + cross) - minor and
  (agree + cross) + minor, and rhs - lhs = (G(A)G(Abar) + split_j + split_k - 2 lhs) / 1 exactly; on random gadgets G > 0 on all
  patterns of every pair of terminals;
- Proposition 3: the four stored gadgets (two or three knots) fail, respectively, the bound per partner solution, the bound per image
  difference pattern, saturating matchings by one-sided path flips into the two target classes, and the minor inequality; each
  satisfies the arm inequality on every axis and terminal.
Controls: reversing the side rule of Lemma 1 (flipping the configuration that is full at the branching knot) gives an incompatible
image; on random tree gadgets the path-flip matching does saturate; the planted function [10, 1, 1, 1, 1, 1, 1, 10] violates the
symmetric form.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
"""

from __future__ import annotations

import itertools
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
CUBE = list(itertools.product((0, 1), repeat=3))
AXES = [(0, 0, 0), (0, 0, 1), (0, 1, 0), (1, 0, 0)]
CENTRE = (1, 1, 0)
S = frozenset(t for t in CUBE if t not in {(0, 0, 0), (0, 1, 1), (1, 0, 1)})
WITNESSES = {
    "minor": {"gadget": [[["T", 0], ["E", 0], ["T", 2]], [["P", 0], ["T", 1], ["E", 0]]], "axis": [1, 0, 0], "i": 0},
    "image": {"gadget": [[["E", 0], ["E", 1], ["E", 2]], [["T", 1], ["T", 0], ["E", 1]], [["T", 2], ["E", 2], ["E", 0]]],
              "axis": [0, 0, 1], "i": 2},
    "matching": {"gadget": [[["E", 0], ["E", 1], ["E", 2]], [["T", 2], ["E", 1], ["T", 0]], [["T", 1], ["E", 0], ["E", 2]]],
                 "axis": [1, 0, 0], "i": 1},
    "partner": {"gadget": [[["E", 0], ["E", 1], ["T", 1]], [["E", 1], ["E", 2], ["T", 2]], [["E", 2], ["E", 0], ["T", 0]]],
                "axis": [0, 0, 0], "i": 0},
}


def comp(x):
    return tuple(1 - b for b in x)


def xor(x, y):
    return tuple(a ^ b for a, b in zip(x, y))


def unit(i):
    return tuple(int(j == i) for j in range(3))


def split_sum(F, u):
    return sum(F[xor(u, unit(i))] * F[xor(comp(u), unit(i))] for i in range(3))


def arm_sides(F, u, i):
    ub = comp(u)
    return F[u] * F[ub], split_sum(F, u) + F[xor(u, unit(i))] * F[ub] + F[u] * F[xor(ub, unit(i))]


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


def random_gadget(rng, n, p_pin, tree=False):
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
            a[s] = ("P", rng.randint(0, 1)) if rng.random() < p_pin else ("F",)
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


def terminal_component_has_all(n, a, diff):
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
    roots = {find(("T", k)) for k in range(3) if ("T", k) in diff}
    return len(roots) == 1 and all(("T", k) in diff for k in range(3))


def walk(n, a, diff, term):
    where = {}
    for (v, p), k in a.items():
        if k[0] != "P":
            where.setdefault(item(a, (v, p)), []).append((v, p))
    cur, came = ("T", term), None
    items = [cur]
    for _ in range(400):
        v, p = [vp for vp in where[cur] if vp != came][0]
        dslots = [q for q in range(3) if a[(v, q)][0] != "P" and item(a, (v, q)) in diff]
        if len(dslots) == 3:
            return frozenset(items), v
        if len(dslots) != 2:
            return None
        q = [q for q in dslots if q != p][0]
        cur, came = item(a, (v, q)), (v, q)
        if cur[0] != "E":
            return None
        items.append(cur)
    return None


def key(conf):
    return tuple(sorted(conf.items()))


def flip(conf, items):
    return {z: (1 - v if z in items else v) for z, v in conf.items()}


def lemma1_on(n, a, stats, tree):
    by = configurations(n, a)
    F = {x: len(by[x]) for x in CUBE}
    valid = {key(c) for x in CUBE for c in by[x]}
    for u in AXES:
        ub = comp(u)
        if F[u] * F[ub] == 0 or F[u] * F[ub] > 3000:
            continue
        for i in range(3):
            j, k = [t for t in range(3) if t != i]
            patterns = defaultdict(list)
            for s in by[u]:
                for t in by[ub]:
                    diff = frozenset(z for z in s if s[z] != t[z])
                    if terminal_component_has_all(n, a, diff):
                        patterns[diff].append(s)
            images_of_d = {}
            for d, sigmas in patterns.items():
                arm, b = walk(n, a, d, i)
                dp = d ^ arm
                images = set()
                for s in sigmas:
                    s2 = flip(s, arm) if defects(local(a, s, b)) == 0 else dict(s)
                    ok = key(s2) in valid and key(flip(s2, dp)) in valid and s2[("T", j)] == u[j] and s2[("T", k)] == u[k]
                    stats["images compatible"] &= ok
                    stats["injective per pattern"] &= key(s2) not in images
                    images.add(key(s2))
                    # control: the reversed side rule
                    wrong = dict(s) if defects(local(a, s, b)) == 0 else flip(s, arm)
                    if not (key(wrong) in valid and key(flip(wrong, dp)) in valid):
                        stats["reversed rule fails somewhere"] = True
                stats["patterns"] += 1
                images_of_d.setdefault(dp, []).append(d)
            if tree:
                stats["tree pattern maps injective"] &= all(len(v) == 1 for v in images_of_d.values())


def path_flip_matching(n, a, by, u, i):
    """size of a maximum matching of linked pairs into the two target classes by one-sided flips of difference paths from terminal i"""
    ub = comp(u)
    valid = {key(c) for x in CUBE for c in by[x]}
    want = {"A": xor(u, unit(i)), "B": xor(ub, unit(i))}
    where = {}
    for (v, p), k in a.items():
        if k[0] != "P":
            where.setdefault(item(a, (v, p)), []).append((v, p))
    linked, options = [], []
    for s in by[u]:
        for t in by[ub]:
            diff = frozenset(z for z in s if s[z] != t[z])
            if not terminal_component_has_all(n, a, diff):
                continue
            opts = set()

            def dfs(cur, came, path, seenk):
                for side in ("A", "B"):
                    base = flip(s if side == "A" else t, path)
                    if tuple(base[("T", kk)] for kk in range(3)) == want[side] and key(base) in valid:
                        opts.add((key(base), key(t)) if side == "A" else (key(s), key(base)))
                for (v, p) in where[cur]:
                    if (v, p) == came or v in seenk:
                        continue
                    for q in range(3):
                        if q == p or a[(v, q)][0] == "P":
                            continue
                        nxt = item(a, (v, q))
                        if nxt in diff and nxt not in path:
                            dfs(nxt, (v, q), path | {nxt}, seenk | {v})
            dfs(("T", i), None, frozenset({("T", i)}), frozenset())
            linked.append((s, t))
            options.append(sorted(opts))
    match = {}

    def aug(l, seen):
        for tg in options[l]:
            if tg in seen:
                continue
            seen.add(tg)
            if tg not in match or aug(match[tg], seen):
                match[tg] = l
                return True
        return False
    return len(linked), sum(aug(l, set()) for l in range(len(linked)))


def witness_checks():
    out = {}
    for name, w in WITNESSES.items():
        n, a = parse(w["gadget"])
        u, i = tuple(w["axis"]), w["i"]
        j, k = [t for t in range(3) if t != i]
        by = configurations(n, a)
        F = {x: len(by[x]) for x in CUBE}
        arm_holds = all(arm_sides(F, uu, ii)[0] <= arm_sides(F, uu, ii)[1] for uu in AXES for ii in range(3))
        ub = comp(u)
        if name == "minor":
            def M(z, wv):
                x = [0, 0, 0]
                x[i] = z
                x[j], x[k] = wv
                return F[tuple(x)]
            z0, z1 = u[i], 1 - u[i]
            Aw, Ab, Pw, Qw = (u[j], u[k]), (1 - u[j], 1 - u[k]), (1 - u[j], u[k]), (u[j], 1 - u[k])
            minor = M(z0, Aw) * M(z1, Ab) - M(z1, Aw) * M(z0, Ab)
            cross = M(z0, Pw) * M(z1, Qw) + M(z0, Qw) * M(z1, Pw)
            out[name] = {"knots": n, "is a tree": is_tree(n, a), "minor": minor, "cross": cross, "fails": minor > cross,
                         "arm inequality holds": arm_holds}
        elif name in ("partner", "image"):
            valid = {key(c) for x in CUBE for c in by[x]}
            allconf = [c for x in CUBE for c in by[x]]
            partner, images = defaultdict(int), defaultdict(int)
            for s in by[u]:
                for t in by[ub]:
                    diff = frozenset(z for z in s if s[z] != t[z])
                    if not terminal_component_has_all(n, a, diff):
                        continue
                    arm, b = walk(n, a, diff, i)
                    images[diff ^ arm] += 1
                    if defects(local(a, s, b)) == 0:
                        partner[key(t)] += 1
            if name == "partner":
                worst = max(partner.values(), default=0)
                out[name] = {"knots": n, "largest number of partners": worst, "F(u + e_i)": F[xor(u, unit(i))],
                             "fails": worst > F[xor(u, unit(i))], "arm inequality holds": arm_holds}
            else:
                fails = 0
                for dp, cnt in images.items():
                    npr = sum(1 for s in allconf if s[("T", j)] == u[j] and s[("T", k)] == u[k] and key(flip(s, dp)) in valid)
                    fails += cnt > npr
                out[name] = {"knots": n, "image patterns over capacity": fails, "fails": fails > 0, "arm inequality holds": arm_holds}
        else:
            nl, nm = path_flip_matching(n, a, by, u, i)
            lhs, rhs = arm_sides(F, u, i)
            out[name] = {"knots": n, "linked pairs": nl, "maximum matching": nm, "fails": nm < nl,
                         "linked pairs within the two target classes": nl <= F[xor(u, unit(i))] * F[ub] + F[u] * F[xor(ub, unit(i))],
                         "arm inequality holds": arm_holds}
    return out


def main() -> int:
    manifest = json.loads((HERE / "manifest.json").read_text())
    result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
              "proof": manifest["proof"], "claim": manifest["claim"], "foundation_contract": manifest["foundation_contract"],
              "semantic_domains": manifest["semantic_domains"], "evidence_modes": manifest["evidence_modes"],
              "thesis_alignment": manifest["thesis_alignment"], "safe_conclusions": manifest["safe_to_conclude"]}
    rng = random.Random(20261025)

    # Lemma 1
    l1 = {"gadgets": 0, "trees": 0, "patterns": 0, "images compatible": True, "injective per pattern": True,
          "tree pattern maps injective": True, "reversed rule fails somewhere": False}
    while l1["gadgets"] < 300:
        n = rng.randint(2, 7)
        tree = l1["gadgets"] % 3 == 0
        a = random_gadget(rng, n, rng.choice([0.3, 0.75]), tree=tree)
        if a is None or len({item(a, s) for s in a if a[s][0] != "P"}) > 12:
            continue
        l1["gadgets"] += 1
        l1["trees"] += is_tree(n, a)
        lemma1_on(n, a, l1, is_tree(n, a))

    # Proposition 2: algebra on random functions, positivity of G on random gadgets
    alg_ok = True
    for _ in range(20000):
        F = {x: rng.randint(0, 20) for x in CUBE}
        for u in AXES:
            for i in range(3):
                j, k = [t for t in range(3) if t != i]
                ui = xor(u, unit(i))
                l_u, r_u = arm_sides(F, u, i)
                l_v, r_v = arm_sides(F, ui, i)

                def M(z, wv):
                    x = [0, 0, 0]
                    x[i] = z
                    x[j], x[k] = wv
                    return F[tuple(x)]
                z0, z1 = u[i], 1 - u[i]
                Aw, Ab, Pw, Qw = (u[j], u[k]), (1 - u[j], 1 - u[k]), (1 - u[j], u[k]), (u[j], 1 - u[k])
                minor = M(z0, Aw) * M(z1, Ab) - M(z1, Aw) * M(z0, Ab)
                agree = M(z0, Aw) * M(z0, Ab) + M(z1, Aw) * M(z1, Ab)
                cross = M(z0, Pw) * M(z1, Qw) + M(z0, Qw) * M(z1, Pw)
                G = lambda wv: M(0, wv) + M(1, wv)
                split_jk = F[xor(u, unit(j))] * F[xor(comp(u), unit(j))] + F[xor(u, unit(k))] * F[xor(comp(u), unit(k))]
                alg_ok &= r_u - l_u == agree + cross - minor and r_v - l_v == agree + cross + minor
                alg_ok &= r_u - l_u == G(Aw) * G(Ab) + split_jk - 2 * l_u
    pos = {"gadgets": 0, "G positive on every pattern": True}
    while pos["gadgets"] < 2000:
        n = rng.randint(1, 8)
        a = random_gadget(rng, n, rng.choice([0.3, 0.75]))
        if a is None or len({item(a, s) for s in a if a[s][0] != "P"}) > 13:
            continue
        pos["gadgets"] += 1
        by = configurations(n, a)
        F = {x: len(by[x]) for x in CUBE}
        for i in range(3):
            j, k = [t for t in range(3) if t != i]
            for wv in itertools.product((0, 1), repeat=2):
                total = 0
                for z in (0, 1):
                    x = [0, 0, 0]
                    x[i] = z
                    x[j], x[k] = wv
                    total += F[tuple(x)]
                pos["G positive on every pattern"] &= total > 0

    # Proposition 3
    wit = witness_checks()

    # control: matching saturates on tree gadgets
    tree_match_ok, tree_cases = True, 0
    while tree_cases < 60:
        n = rng.randint(2, 6)
        a = random_gadget(rng, n, 0.5, tree=True)
        if a is None or len({item(a, s) for s in a if a[s][0] != "P"}) > 11:
            continue
        by = configurations(n, a)
        F = {x: len(by[x]) for x in CUBE}
        for u in AXES:
            if F[u] * F[comp(u)] == 0 or F[u] * F[comp(u)] > 400:
                continue
            nl, nm = path_flip_matching(n, a, by, u, 0)
            tree_match_ok &= nm == nl
        tree_cases += 1
    planted = dict(zip(CUBE, [10, 1, 1, 1, 1, 1, 1, 10]))
    controls = {"the reversed side rule gives an incompatible image": l1["reversed rule fails somewhere"],
                "path-flip matchings saturate on tree gadgets": tree_match_ok,
                "the planted function violates the symmetric form": arm_sides(planted, (0, 0, 0), 0)[0] > arm_sides(planted, (0, 0, 0), 0)[1]}
    ok = (l1["images compatible"] and l1["injective per pattern"] and l1["tree pattern maps injective"] and l1["trees"] > 0
          and l1["patterns"] > 0 and alg_ok and pos["G positive on every pattern"]
          and all(w["fails"] and w["arm inequality holds"] for w in wit.values())
          and wit["matching"]["linked pairs within the two target classes"] and all(controls.values()))
    result["checks"] = {"Lemma 1": l1, "Proposition 2: algebra": {"random functions": 20000, "identities hold": alg_ok},
                        "Proposition 2: positivity": pos, "Proposition 3: witnesses": wit}
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
