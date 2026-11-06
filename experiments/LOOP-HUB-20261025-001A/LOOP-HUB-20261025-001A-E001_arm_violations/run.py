#!/usr/bin/env python3
"""Producer of LOOP-HUB-20261025-001A-E001 (searching for violations of the arm inequality on gadgets with loops).

Gadget machinery (random gadgets, moves, exact bucket elimination) is loaded unchanged from SOFT-HUB-20261024-001B-E001's run.py.
lhs = F(u)F(u-bar); rhs = s_u + F(u + e_i)F(u-bar) + F(u)F(u-bar + e_i). Parts:
- anneal: for each size and seed, 20,000 moves maximizing the largest log(lhs / rhs) over axes and terminals; the best gadget is
  re-evaluated exactly;
- chains: chains of double edges, lengths 1 to 12, 300 random place orders each;
- cores: gadgets with every non-terminal slot on an internal edge, 3 to 15 knots (odd), 2,000 each;
- pairs: 2,000 small gadgets, every pair classified (standard library); split bounds and the strengthenings.
Rows are appended to rows.jsonl as parts finish; result.json is written at the end by summarize().

    .venv/bin/python -B run.py
"""

from __future__ import annotations

import importlib.util
import itertools
import json
import math
import random
import time
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts/LOOP-HUB-20261025-001A/LOOP-HUB-20261025-001A-E001_arm_violations"
_spec = importlib.util.spec_from_file_location(
    "hub_run", ROOT / "experiments/SOFT-HUB-20261024-001B/SOFT-HUB-20261024-001B-E001_strong_hubs/run.py")
H = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(H)

CUBE, AXES = H.CUBE, H.AXES
SIZES = [4, 8, 12, 16, 20, 24, 32, 40]
SEEDS = 48
STEPS = 20000
CENTRE = (1, 1, 0)
R = H.relation(H.OPEN)


def arm_sides(F, u, i):
    ub = H.comp(u)
    lhs = F[u] * F[ub]
    rhs = H.split_sum(F, u) + F[H.xor(u, H.unit(i))] * F[ub] + F[u] * F[H.xor(ub, H.unit(i))]
    return lhs, rhs


def max_ratio(F):
    """largest lhs / rhs over axes and terminals (exact integers in, float out), with the count of equality cases"""
    best, eq = 0.0, 0
    for u in AXES:
        for i in range(3):
            lhs, rhs = arm_sides(F, u, i)
            if lhs == 0:
                continue
            eq += lhs == rhs
            best = max(best, float(lhs) / float(rhs) if rhs else float("inf"))
    return best, eq


def score(F):
    best = -30.0
    for u in AXES:
        ub = H.comp(u)
        lhs = float(F[u]) * float(F[ub])
        if lhs == 0:
            continue
        for i in range(3):
            rhs = float(H.split_sum(F, u)) + float(F[H.xor(u, H.unit(i))]) * float(F[ub]) + float(F[u]) * float(F[H.xor(ub, H.unit(i))])
            best = max(best, math.log(lhs / rhs) if rhs > 0 else 30.0)
    return best


def exact_F(n, a):
    F = H.as_dict(H.evaluate(H.tensor(R, exact=True), n, a))
    return {x: int(F[x]) for x in CUBE}


def describe(n, a):
    F = exact_F(n, a)
    r, eq = max_ratio(F)
    return {"F": [F[x] for x in CUBE], "max_lhs_over_rhs": r, "equality_cases": eq, "gadget": H.gadget_json(n, a)}


def is_tree(n, a):
    edges = {}
    for (v, p), k in a.items():
        if k[0] == "E":
            edges.setdefault(k[1], []).append(v)
    return len(edges) == n - 1 and all(len(set(vs)) == 2 for vs in edges.values()) and H.connected(n, a)


def anneal(job):
    n, seed, steps, p_pin, tree_only = job
    rng = random.Random(seed)
    T = H.tensor(R)
    a = None
    while a is None or (tree_only and not is_tree(n, a)):
        a = H.random_gadget(rng, n, p_pin)
    F = H.as_dict(H.evaluate(T, n, a))
    s = score(F)
    best = (s, a)
    for i in range(steps):
        temp = 0.2 * (1 - i / steps) + 0.003
        b = H.mutate(rng, n, a)
        if b is None or (tree_only and not is_tree(n, b)):
            continue
        G = H.as_dict(H.evaluate(T, n, b))
        t = score(G)
        if t >= s or rng.random() < math.exp((t - s) / temp):
            a, F, s = b, G, t
            if s > best[0]:
                best = (s, a)
    return {"part": "anneal" if not tree_only else "anneal_tree", "n": n, "seed": seed, "p_pin": p_pin, **describe(n, best[1])}


PERMS = list(itertools.permutations(range(3)))


def chain(L, rng):
    n = 2 * L + 1
    logical = [[None] * 3 for _ in range(n)]
    logical[0][0] = ("T", 0)
    e = 0
    for m in range(L):
        a, b = 2 * m, 2 * m + 1
        logical[a][1] = ("E", e); logical[b][0] = ("E", e); e += 1
        logical[a][2] = ("E", e); logical[b][1] = ("E", e); e += 1
        logical[b][2] = ("E", e); logical[b + 1][0] = ("E", e); e += 1
    logical[n - 1][1] = ("T", 1)
    logical[n - 1][2] = ("T", 2)
    assign = {}
    for v in range(n):
        p = rng.choice(PERMS)
        for q in range(3):
            assign[(v, p[q])] = logical[v][q]
    return n, assign


def chains_part(job):
    L, seed = job
    rng = random.Random(seed)
    best, eq, worst_g = 0.0, 0, None
    for _ in range(300):
        n, a = chain(L, rng)
        F = exact_F(n, a)
        r, e = max_ratio(F)
        eq += e
        if r > best:
            best, worst_g = r, H.gadget_json(n, a)
    return {"part": "chains", "L": L, "max_lhs_over_rhs": best, "equality_cases": eq, "worst_gadget": worst_g}


def core_gadget(rng, n):
    slots = [(v, p) for v in range(n) for p in range(3)]
    for _ in range(4000):
        rng.shuffle(slots)
        a = {slots[k]: ("T", k) for k in range(3)}
        rest = slots[3:]
        for i in range(0, len(rest), 2):
            a[rest[i]] = a[rest[i + 1]] = ("E", i // 2)
        if H.connected(n, a):
            return H.renumber(a)
    return None


def cores_part(job):
    n, seed = job
    rng = random.Random(seed)
    best, eq, worst_g, made = 0.0, 0, None, 0
    while made < 2000:
        a = core_gadget(rng, n)
        if a is None:
            continue
        made += 1
        F = exact_F(n, a)
        r, e = max_ratio(F)
        eq += e
        if r > best:
            best, worst_g = r, H.gadget_json(n, a)
    return {"part": "cores", "n": n, "max_lhs_over_rhs": best, "equality_cases": eq, "worst_gadget": worst_g}


# ---------------------------------------------------------------- pairs (standard library)

def defects(t):
    return sum(1 for p in range(3) if t[p] != CENTRE[p])


def walk(n, a, diff, term):
    """difference walk from terminal term: (items walked, first branching knot) or None"""
    where = {}
    for (v, p), k in a.items():
        if k[0] != "P":
            where.setdefault(H.item(a, (v, p)), []).append((v, p))
    cur, came = ("T", term), None
    items = [cur]
    for _ in range(400):
        v, p = [vp for vp in where[cur] if vp != came][0]
        dslots = [q for q in range(3) if a[(v, q)][0] != "P" and H.item(a, (v, q)) in diff]
        if len(dslots) == 3:
            return frozenset(items), v
        if len(dslots) != 2:
            return None
        q = [q for q in dslots if q != p][0]
        cur, came = H.item(a, (v, q)), (v, q)
        if cur[0] != "E":
            return None
        items.append(cur)
    return None


def pairs_chunk(job):
    chunk, count, seed = job
    rng = random.Random(seed)
    st = {"gadgets": 0, "axis_terminal_cases": 0, "linked": 0, "P3_fail_A": 0, "P3_fail_B": 0, "lemma2_ok": True,
          "per_partner_fail": 0, "per_partner_cases": 0, "per_image_fail": 0, "per_image_cases": 0, "minor_fail": 0, "minor_cases": 0,
          "arm_fail": 0}
    while st["gadgets"] < count:
        n = rng.randint(2, 7)
        a = H.random_gadget(rng, n, 0.3 if st["gadgets"] % 2 == 0 else 0.75)
        if a is None or len({H.item(a, s) for s in a if a[s][0] != "P"}) > 13:
            continue
        st["gadgets"] += 1
        by = H.configurations(R, n, a)
        F = {x: len(by[x]) for x in CUBE}
        keyset = {tuple(sorted(c.items())) for x in CUBE for c in by[x]}
        allconf = [c for x in CUBE for c in by[x]]
        for u in AXES:
            ub = H.comp(u)
            for i in range(3):
                j, k = [t for t in range(3) if t != i]
                # minor inequality (MI) for this axis and terminal
                def M(z, w):
                    x = [0, 0, 0]
                    x[i] = z
                    x[j], x[k] = w
                    return F[tuple(x)]
                z0, z1 = u[i], 1 - u[i]
                Aw, Ab, Pw, Qw = (u[j], u[k]), (1 - u[j], 1 - u[k]), (1 - u[j], u[k]), (u[j], 1 - u[k])
                st["minor_cases"] += 1
                st["minor_fail"] += M(z0, Aw) * M(z1, Ab) - M(z1, Aw) * M(z0, Ab) > M(z0, Pw) * M(z1, Qw) + M(z0, Qw) * M(z1, Pw)
                lhs, rhs = arm_sides(F, u, i)
                st["arm_fail"] += lhs > rhs
                if lhs == 0 or lhs > 3000:
                    continue
                st["axis_terminal_cases"] += 1
                lA = lB = sep = 0
                partner = defaultdict(int)
                images = defaultdict(int)
                for s in by[u]:
                    for t in by[ub]:
                        diff = frozenset(z for z in s if s[z] != t[z])
                        c1 = H.component_of_terminal1(n, a, set(diff))
                        if {z[1] for z in c1 if z[0] == "T"} != {0, 1, 2}:
                            sep += 1
                            continue
                        res = walk(n, a, diff, i)
                        if res is None:
                            st["lemma2_ok"] = False
                            continue
                        arm, b = res
                        images[diff ^ arm] += 1
                        if defects(H.local(a, s, b)) == 0:
                            lA += 1
                            partner[tuple(sorted(t.items()))] += 1
                        else:
                            lB += 1
                st["linked"] += lA + lB
                st["lemma2_ok"] &= sep + lA + lB == lhs and sep <= H.split_sum(F, u)
                ui, ubi = H.xor(u, H.unit(i)), H.xor(ub, H.unit(i))
                st["P3_fail_A"] += lA > F[ui] * F[ub]
                st["P3_fail_B"] += lB > F[u] * F[ubi]
                for cnt in partner.values():
                    st["per_partner_cases"] += 1
                    st["per_partner_fail"] += cnt > F[ui]
                for dp, cnt in images.items():
                    st["per_image_cases"] += 1
                    npr = 0
                    for s in allconf:
                        if s[("T", j)] != u[j] or s[("T", k)] != u[k]:
                            continue
                        t = tuple(sorted((z, (1 - v if z in dp else v)) for z, v in s.items()))
                        npr += t in keyset
                    st["per_image_fail"] += cnt > npr
    return {"part": "pairs", "chunk": chunk, **st}


# ---------------------------------------------------------------- driver

def jobs():
    out = [("anneal", (n, 1000 * n + s, STEPS, 0.3 if s % 2 == 0 else 0.75, False)) for n in SIZES for s in range(SEEDS)]
    rng = random.Random(20261028)
    out += [("chains", (L, rng.randrange(1 << 60))) for L in range(1, 13)]
    rng = random.Random(20261029)
    out += [("cores", (n, rng.randrange(1 << 60))) for n in range(3, 16, 2)]
    rng = random.Random(20261030)
    out += [("pairs", (c, 50, rng.randrange(1 << 60))) for c in range(40)]
    return out


def run_job(job):
    kind, args = job
    return {"anneal": anneal, "chains": chains_part, "cores": cores_part, "pairs": pairs_chunk}[kind](args)


def key(r):
    if r["part"] in ("anneal", "anneal_tree"):
        return (r["part"], r["n"], r["seed"])
    if r["part"] == "chains":
        return ("chains", r["L"])
    if r["part"] == "cores":
        return ("cores", r["n"])
    return ("pairs", r["chunk"])


def job_key(job):
    kind, args = job
    if kind == "anneal":
        return ("anneal", args[0], args[1])
    if kind == "chains":
        return ("chains", args[0])
    if kind == "cores":
        return ("cores", args[0])
    return ("pairs", args[0])


def summarize(rows):
    ann = [r for r in rows if r["part"] == "anneal"]
    ch = [r for r in rows if r["part"] == "chains"]
    co = [r for r in rows if r["part"] == "cores"]
    pa = [r for r in rows if r["part"] == "pairs"]
    by_size = {}
    for r in ann:
        d = by_size.setdefault(str(r["n"]), {"best": 0.0, "runs_reaching_equality": 0, "runs": 0})
        d["best"] = max(d["best"], r["max_lhs_over_rhs"])
        d["runs_reaching_equality"] += r["max_lhs_over_rhs"] == 1.0
        d["runs"] += 1
    tot = lambda key_: sum(r[key_] for r in pa)
    summary = {
        "P1_no_violation_annealing": all(r["max_lhs_over_rhs"] <= 1.0 for r in ann),
        "P2_no_violation_families": all(r["max_lhs_over_rhs"] <= 1.0 for r in ch + co),
        "P3_split_bounds": tot("P3_fail_A") == 0 and tot("P3_fail_B") == 0,
        "best_annealing": max((r["max_lhs_over_rhs"] for r in ann), default=0.0),
        "best_chains": max((r["max_lhs_over_rhs"] for r in ch), default=0.0),
        "best_cores": max((r["max_lhs_over_rhs"] for r in co), default=0.0),
        "pairs": {k_: tot(k_) for k_ in ("gadgets", "axis_terminal_cases", "linked", "P3_fail_A", "P3_fail_B", "per_partner_fail",
                                         "per_partner_cases", "per_image_fail", "per_image_cases", "minor_fail", "minor_cases",
                                         "arm_fail")},
        "lemma2_holds_on_pairs": all(r["lemma2_ok"] for r in pa)}
    table = {"annealing_by_size": dict(sorted(by_size.items(), key=lambda kv: int(kv[0]))),
             "chains": {str(r["L"]): r["max_lhs_over_rhs"] for r in sorted(ch, key=lambda r: r["L"])},
             "cores": {str(r["n"]): r["max_lhs_over_rhs"] for r in sorted(co, key=lambda r: r["n"])}}
    return table, summary


def verdict_of(controls, summary):
    if not controls or not all(controls.values()) or not summary["lemma2_holds_on_pairs"]:
        return "invalid"
    ok = summary["P1_no_violation_annealing"] and summary["P2_no_violation_families"] and summary["P3_split_bounds"]
    return "supported" if ok else "refuted"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    rows_path = OUT / "rows.jsonl"
    done = set()
    if rows_path.exists():
        for line in rows_path.read_text().splitlines():
            done.add(key(json.loads(line)))
    todo = [j for j in jobs() if job_key(j) not in done]
    todo.sort(key=lambda j: -(j[1][0] if j[0] in ("anneal", "cores") else 0))
    t0 = time.time()
    with Pool(24) as pool, rows_path.open("a") as fh:
        for row in pool.imap_unordered(run_job, todo):
            fh.write(json.dumps(row, sort_keys=True) + "\n")
            fh.flush()
    rows = [json.loads(line) for line in rows_path.read_text().splitlines()]
    table, summary = summarize(rows)
    controls = json.loads((OUT / "controls.json").read_text()) if (OUT / "controls.json").exists() else {}
    verdict = verdict_of(controls, summary)
    result = {"schema_version": 1, "experiment_id": "LOOP-HUB-20261025-001A-E001", "ticket": "LOOP-HUB-20261025-001A",
              "evidence_stage": "confirmatory", "verdict": verdict, "summary": summary, "controls": controls, "table": table,
              "rows": len(rows), "wall_seconds_this_run": round(time.time() - t0, 1)}
    (OUT / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"verdict": verdict, "summary": summary, "table": table}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
