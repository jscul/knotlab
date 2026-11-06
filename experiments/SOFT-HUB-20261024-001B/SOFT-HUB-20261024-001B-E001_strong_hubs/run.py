#!/usr/bin/env python3
"""Producer of SOFT-HUB-20261024-001B-E001 (searching for strong hubs among gadgets of an open knot).

Gadgets are connected native networks of one knot with pins, free legs (summed) and three terminals, self-loops allowed; F(x) is
computed by bucket elimination (floats while annealing, exact Python integers for every reported gadget). Parts:
- anneal: for each size and seed, 30,000 moves maximizing the largest over the four axes of log(min(F(u), F(u-bar)) / off-axis max);
  the best gadget is re-evaluated exactly;
- sample: 100,000 random gadgets with 1 to 16 knots, evaluated exactly, in 100 chunks;
- pairs: 3,000 random small gadgets, every pair classified by its difference components (standard library), in 30 chunks;
- compose: triangles, dressings and hubs of hubs built from the 12 best annealed gadgets.
Rows are appended to rows.jsonl as parts finish; result.json is written at the end by summarize().

    .venv/bin/python -B run.py            run everything (skips parts already in rows.jsonl)
"""

from __future__ import annotations

import itertools
import json
import math
import random
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts/SOFT-HUB-20261024-001B/SOFT-HUB-20261024-001B-E001_strong_hubs"
CUBE = list(itertools.product((0, 1), repeat=3))
AXES = [(0, 0, 0), (0, 0, 1), (0, 1, 0), (1, 0, 0)]
OPEN = "000,011,101"
NOLONE1 = "001,010,100"
NAE = "000,111"
SIZES = [8, 12, 16, 20, 24, 32, 40]
SEEDS = 48
STEPS = 30000
SQRT3 = math.sqrt(3)


def relation(label):
    ex = {tuple(int(c) for c in w) for w in label.split(",")}
    return frozenset(t for t in CUBE if t not in ex)


def tensor(R, exact=False):
    T = np.zeros((2, 2, 2), dtype=object if exact else float)
    if exact:
        T[...] = 0
    for t in R:
        T[t] = 1
    return T


def comp(x):
    return tuple(1 - b for b in x)


def xor(x, y):
    return tuple(a ^ b for a, b in zip(x, y))


def unit(i):
    return tuple(int(j == i) for j in range(3))


# ---------------------------------------------------------------- gadgets

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


def renumber(a):
    ids, out = {}, {}
    for s in sorted(a):
        k = a[s]
        if k[0] == "E":
            ids.setdefault(k[1], len(ids))
            out[s] = ("E", ids[k[1]])
        else:
            out[s] = k
    return out


def random_gadget(rng, n, p_pin=0.75):
    slots = [(v, p) for v in range(n) for p in range(3)]
    for _ in range(2000):
        rng.shuffle(slots)
        a = {slots[k]: ("T", k) for k in range(3)}
        rest = slots[3:]
        m = len(rest)
        npf = rng.randint(0, max(0, m - 2 * (n - 1)))
        if (m - npf) % 2:
            npf += 1
        if npf > m:
            continue
        for s in rest[:npf]:
            a[s] = ("P", rng.randint(0, 1)) if rng.random() < p_pin else ("F",)
        pr = rest[npf:]
        for i in range(0, len(pr), 2):
            a[pr[i]] = a[pr[i + 1]] = ("E", i // 2)
        if connected(n, a):
            return renumber(a)
    return None


def mutate(rng, n, a):
    b = dict(a)
    slots = list(b)
    move = rng.random()
    if move < 0.45:
        s1, s2 = rng.sample(slots, 2)
        b[s1], b[s2] = b[s2], b[s1]
    elif move < 0.6:
        cand = [s for s in slots if b[s][0] in "PF"]
        if not cand:
            return None
        s = rng.choice(cand)
        b[s] = ("P", rng.randint(0, 1)) if rng.random() < 0.75 else ("F",)
    elif move < 0.8:
        cand = [s for s in slots if b[s][0] in "PF"]
        if len(cand) >= 2 and rng.random() < 0.5:
            s1, s2 = rng.sample(cand, 2)
            e = max([k[1] for k in b.values() if k[0] == "E"], default=-1) + 1
            b[s1] = b[s2] = ("E", e)
        else:
            edges = sorted({k[1] for k in b.values() if k[0] == "E"})
            if not edges:
                return None
            e = rng.choice(edges)
            for s in slots:
                if b[s] == ("E", e):
                    b[s] = ("P", rng.randint(0, 1)) if rng.random() < 0.75 else ("F",)
    else:
        v = rng.randrange(n)
        perm = rng.choice(list(itertools.permutations(range(3))))
        old = [b[(v, p)] for p in range(3)]
        for p in range(3):
            b[(v, p)] = old[perm[p]]
    if not connected(n, b):
        return None
    return renumber(b)


def evaluate(T, n, a):
    """F as a 2x2x2 array (dtype of T) by bucket elimination; edge e -> variable e, terminal k -> 1000 + k"""
    factors = []
    for v in range(n):
        A = T
        kinds = [a[(v, p)] for p in range(3)]
        for p in (2, 1, 0):
            k = kinds[p]
            if k[0] == "P":
                A = np.take(A, k[1], axis=p)
            elif k[0] == "F":
                A = A.sum(axis=p)
        vs = [k[1] if k[0] == "E" else 1000 + k[1] for k in kinds if k[0] in "ET"]
        if len(set(vs)) < len(vs):
            uniq = sorted(set(vs), key=vs.index)
            idx = {x: i for i, x in enumerate(uniq)}
            A = np.einsum(A, [idx[x] for x in vs], list(range(len(uniq))))
            vs = uniq
        factors.append((A, vs))
    keep = (1000, 1001, 1002)
    elim = sorted({x for _, vs in factors for x in vs if x not in keep})
    while elim:
        best = None
        for x in elim:
            size = len({y for _, vs in factors if x in vs for y in vs}) - 1
            if best is None or size < best[0]:
                best = (size, x)
        x = best[1]
        inv = [f for f in factors if x in f[1]]
        rest = [f for f in factors if x not in f[1]]
        allv = sorted({y for _, vs in inv for y in vs})
        lab = {y: i for i, y in enumerate(allv)}
        outv = [y for y in allv if y != x]
        args = []
        for A, vs in inv:
            args += [A, [lab[y] for y in vs]]
        rest.append((np.einsum(*args, [lab[y] for y in outv]), outv))
        factors = rest
        elim.remove(x)
    allv = sorted({y for _, vs in factors for y in vs})
    lab = {y: i for i, y in enumerate(allv)}
    args = []
    for A, vs in factors:
        args += [A, [lab[y] for y in vs]]
    return np.einsum(*args, [lab[y] for y in keep])


def as_dict(F):
    return {x: F[x] for x in CUBE}


def ratios(F):
    out = {}
    for u in AXES:
        off = max(F[x] for x in CUBE if x not in (u, comp(u)))
        m = min(F[u], F[comp(u)])
        out[u] = 0.0 if m == 0 else (float(m) / float(off) if off > 0 else float("inf"))
    return out


def split_sum(F, u):
    return sum(F[xor(u, unit(i))] * F[xor(comp(u), unit(i))] for i in range(3))


def violations(F):
    """axes where F(u)F(u-bar) > s_u (exact integers)"""
    return [u for u in AXES if F[u] * F[comp(u)] > split_sum(F, u)]


def soft(F):
    best = -1e9
    tot = float(F.sum())
    for u in AXES:
        off = max(float(F[x]) for x in CUBE if x not in (u, comp(u)))
        m = min(float(F[u]), float(F[comp(u)]))
        if off > 0:
            best = max(best, math.log((m + 1e-9 * tot) / off))
        else:
            best = max(best, 50.0)
    return best


def gadget_json(n, a):
    return [[list(a[(v, p)]) for p in range(3)] for v in range(n)]


def gadget_from_json(g):
    return len(g), {(v, p): tuple(g[v][p]) for v in range(len(g)) for p in range(3)}


def describe(R, n, a):
    F = as_dict(evaluate(tensor(R, exact=True), n, a))
    r = ratios(F)
    return {"F": [int(F[x]) for x in CUBE], "ratio": {"".join(map(str, u)): r[u] for u in AXES},
            "max_ratio": max(r.values()), "violations": ["".join(map(str, u)) for u in violations(F)],
            "dichotomy_fail": [("".join(map(str, u))) for u in violations(F) if r[u] > 1]}


def anneal(job):
    label, n, seed, steps = job
    rng = random.Random(seed)
    R = relation(label)
    T = tensor(R)
    a = random_gadget(rng, n)
    F = evaluate(T, n, a)
    s = soft(F)
    best = (s, a)
    for i in range(steps):
        temp = 0.3 * (1 - i / steps) + 0.005
        b = mutate(rng, n, a)
        if b is None:
            continue
        G = evaluate(T, n, b)
        t = soft(G)
        if t >= s or rng.random() < math.exp((t - s) / temp):
            a, F, s = b, G, t
            if s > best[0]:
                best = (s, a)
    a = best[1]
    return {"part": "anneal", "knot": label, "n": n, "seed": seed, "gadget": gadget_json(n, a), **describe(R, n, a)}


def sample_chunk(job):
    label, chunk, count, seed = job
    rng = random.Random(seed)
    R = relation(label)
    T = tensor(R, exact=True)
    best_ratio, best = 0.0, None
    viol = 0
    fails = []
    over = []
    for _ in range(count):
        n = rng.randint(1, 16)
        a = random_gadget(rng, n)
        if a is None:
            continue
        F = as_dict(evaluate(T, n, a))
        r = ratios(F)
        v = violations(F)
        viol += len(v)
        for u in v:
            if r[u] > 1:
                fails.append({"gadget": gadget_json(n, a), "axis": "".join(map(str, u))})
        m = max(r.values())
        if m > SQRT3:
            over.append({"gadget": gadget_json(n, a), "ratio": m})
        if m > best_ratio:
            best_ratio, best = m, gadget_json(n, a)
    return {"part": "sample", "knot": label, "chunk": chunk, "count": count, "best_ratio": best_ratio, "best_gadget": best,
            "violating_axes": viol, "dichotomy_failures": fails, "above_sqrt3": over}


# ---------------------------------------------------------------- pairs (standard library)

def item(a, s):
    k = a[s]
    return ("E", k[1]) if k[0] == "E" else ("T", k[1]) if k[0] == "T" else ("F", s)


def local(a, conf, v):
    return tuple(conf[item(a, (v, p))] if a[(v, p)][0] != "P" else a[(v, p)][1] for p in range(3))


def configurations(R, n, a):
    items = sorted({item(a, s) for s in a if a[s][0] != "P"})
    by = {x: [] for x in CUBE}
    for vals in itertools.product((0, 1), repeat=len(items)):
        conf = dict(zip(items, vals))
        if all(local(a, conf, v) in R for v in range(n)):
            by[tuple(conf[("T", k)] for k in range(3))].append(conf)
    return by


def component_of_terminal1(n, a, diff):
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
    root = find(("T", 0))
    return {z for z in diff if find(z) == root}


def pairs_chunk(job):
    label, chunk, count, seed = job
    rng = random.Random(seed)
    R = relation(label)
    cases = 0
    lemma_ok = True
    worst = 0.0
    worst_case = None
    fails = []
    gadgets = 0
    while gadgets < count:
        n = rng.randint(1, 7)
        a = random_gadget(rng, n)
        if a is None or len({item(a, s) for s in a if a[s][0] != "P"}) > 15:
            continue
        gadgets += 1
        by = configurations(R, n, a)
        F = {x: len(by[x]) for x in CUBE}
        for u in AXES:
            if F[u] * F[comp(u)] > 6000:
                continue
            cases += 1
            sep = link = 0
            for s in by[u]:
                for t in by[comp(u)]:
                    diff = {z for z in s if s[z] != t[z]}
                    c1 = component_of_terminal1(n, a, diff)
                    if {z[1] for z in c1 if z[0] == "T"} == {0, 1, 2}:
                        link += 1
                    else:
                        sep += 1
            lemma_ok &= sep + link == F[u] * F[comp(u)] and sep <= split_sum(F, u)
            M = max(F[x] for x in CUBE if x not in (u, comp(u)))
            if link > M * M:
                fails.append({"gadget": gadget_json(n, a), "axis": "".join(map(str, u)), "linked": link, "M": M})
            if M > 0 and link / (M * M) > worst:
                worst = link / (M * M)
                worst_case = {"gadget": gadget_json(n, a), "axis": "".join(map(str, u)), "linked": link, "M": M,
                              "F": [F[x] for x in CUBE]}
    return {"part": "pairs", "knot": label, "chunk": chunk, "gadgets": gadgets, "axis_cases": cases, "lemma2_ok": lemma_ok,
            "max_linked_over_M2": worst, "worst_case": worst_case, "P3_failures": fails}


# ---------------------------------------------------------------- compositions

def compose(best_rows):
    R = relation(OPEN)
    T = tensor(R, exact=True)
    hubs = []
    for r in best_rows:
        n, a = gadget_from_json(r["gadget"])
        hubs.append(evaluate(T, n, a))
    base = max(max(ratios(as_dict(F)).values()) for F in hubs)
    units = [np.array([1, 0], dtype=object), np.array([0, 1], dtype=object), np.array([1, 1], dtype=object)]
    wires = [np.array([[1, 0], [0, 1]], dtype=object)]
    for F in hubs + [T]:
        for p in itertools.permutations(range(3)):
            G = np.transpose(F, p)
            for u in units:
                wires.append(np.einsum("abc,c->ab", G, u))
    perms = lambda F: [np.transpose(F, p) for p in itertools.permutations(range(3))]
    best = {"triangle": 0.0, "dressed": 0.0, "hub_of_hubs": 0.0}
    H = hubs[:6]
    for A in H:
        for B in H:
            for C in H:
                for a_ in perms(A):
                    for b_ in perms(B):
                        for c_ in perms(C):
                            Tri = np.einsum("xab,ybc,zca->xyz", a_, b_, c_)
                            best["triangle"] = max(best["triangle"], max(ratios(as_dict(Tri)).values()))
    rng = random.Random(20261027)
    for C in hubs:
        for c_ in perms(C):
            for _ in range(200):
                w1, w2, w3 = rng.choice(wires), rng.choice(wires), rng.choice(wires)
                D = np.einsum("abc,ax,by,cz->xyz", c_, w1, w2, w3)
                best["dressed"] = max(best["dressed"], max(ratios(as_dict(D)).values()))
    for C in hubs[:4]:
        for A in hubs[:4]:
            for a_ in perms(A):
                G = np.einsum("pqr,pxa,qyb,rzc->xyzabc", C, a_, a_, a_)
                for close in hubs[:4]:
                    K = np.einsum("xyzabc,abc->xyz", G, close)
                    best["hub_of_hubs"] = max(best["hub_of_hubs"], max(ratios(as_dict(K)).values()))
    return {"part": "compose", "knot": OPEN, "base_best": base, "best": best, "wires": len(wires)}


# ---------------------------------------------------------------- driver

def jobs():
    out = [("anneal", (OPEN, n, 1000 * n + s, STEPS)) for n in SIZES for s in range(SEEDS)]
    rng = random.Random(20261025)
    out += [("sample", (OPEN, c, 1000, rng.randrange(1 << 60))) for c in range(100)]
    rng = random.Random(20261026)
    out += [("pairs", (OPEN, c, 100, rng.randrange(1 << 60))) for c in range(30)]
    return out


def run_job(job):
    kind, args = job
    return {"anneal": anneal, "sample": sample_chunk, "pairs": pairs_chunk}[kind](args)


def key(r):
    if r["part"] == "anneal":
        return ("anneal", r["n"], r["seed"])
    if r["part"] in ("sample", "pairs"):
        return (r["part"], r["chunk"])
    return ("compose",)


def summarize(rows):
    ann = [r for r in rows if r["part"] == "anneal"]
    sam = [r for r in rows if r["part"] == "sample"]
    pai = [r for r in rows if r["part"] == "pairs"]
    com = [r for r in rows if r["part"] == "compose"]
    by_size = {}
    for r in ann:
        d = by_size.setdefault(r["n"], {"best": 0.0, "above_1": 0, "above_1.2": 0, "above_1.5": 0, "seeds": 0})
        d["best"] = max(d["best"], r["max_ratio"])
        d["above_1"] += r["max_ratio"] > 1
        d["above_1.2"] += r["max_ratio"] > 1.2
        d["above_1.5"] += r["max_ratio"] > 1.5
        d["seeds"] += 1
    best_ann = max((r["max_ratio"] for r in ann), default=0.0)
    best_sam = max((r["best_ratio"] for r in sam), default=0.0)
    P1 = best_ann <= SQRT3 and best_sam <= SQRT3 and not any(r["above_sqrt3"] for r in sam)
    P2 = not any(r["dichotomy_fail"] for r in ann) and not any(r["dichotomy_failures"] for r in sam)
    P3 = not any(r["P3_failures"] for r in pai)
    P4 = bool(com) and all(v <= com[0]["base_best"] + 1e-12 for v in com[0]["best"].values())
    top = sorted(ann, key=lambda r: -r["max_ratio"])[:5]
    summary = {"P1_bounded_ratio": P1, "P2_dichotomy": P2, "P3_linked_pairs": P3, "P4_no_amplification": P4,
               "best_ratio_annealing": best_ann, "best_ratio_sampling": best_sam,
               "sampled_gadgets": sum(r["count"] for r in sam),
               "violating_axes_sampled": sum(r["violating_axes"] for r in sam),
               "violating_axes_annealed": sum(len(r["violations"]) for r in ann),
               "pairs_axis_cases": sum(r["axis_cases"] for r in pai), "pairs_gadgets": sum(r["gadgets"] for r in pai),
               "lemma2_holds_on_pairs": all(r["lemma2_ok"] for r in pai),
               "max_linked_over_M2": max((r["max_linked_over_M2"] for r in pai), default=0.0),
               "compositions": com[0] if com else None}
    table = {"by_size": {str(k): v for k, v in sorted(by_size.items())},
             "top_gadgets": [{"n": r["n"], "seed": r["seed"], "max_ratio": r["max_ratio"], "F": r["F"], "gadget": r["gadget"]}
                             for r in top],
             "worst_linked_case": max((r for r in pai), key=lambda r: r["max_linked_over_M2"])["worst_case"] if pai else None}
    return table, summary


def verdict_of(controls, summary):
    if not controls or not all(controls.values()) or not summary["lemma2_holds_on_pairs"]:   # control (iv) is computed with the pairs
        return "invalid"
    ok = all(summary[k] for k in ("P1_bounded_ratio", "P2_dichotomy", "P3_linked_pairs", "P4_no_amplification"))
    return "supported" if ok else "refuted"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    rows_path = OUT / "rows.jsonl"
    done = set()
    if rows_path.exists():
        for line in rows_path.read_text().splitlines():
            done.add(key(json.loads(line)))
    todo = [j for j in jobs() if key({"part": j[0], "n": j[1][1], "seed": j[1][2], "chunk": j[1][1]}) not in done]
    todo.sort(key=lambda j: -(j[1][1] if j[0] == "anneal" else 0))
    t0 = time.time()
    with Pool(24) as pool, rows_path.open("a") as fh:
        for row in pool.imap_unordered(run_job, todo):
            fh.write(json.dumps(row, sort_keys=True) + "\n")
            fh.flush()
    rows = [json.loads(line) for line in rows_path.read_text().splitlines()]
    if ("compose",) not in {key(r) for r in rows}:
        ann = sorted([r for r in rows if r["part"] == "anneal"], key=lambda r: -r["max_ratio"])[:12]
        row = compose(ann)
        with rows_path.open("a") as fh:
            fh.write(json.dumps(row, sort_keys=True) + "\n")
        rows.append(row)
    table, summary = summarize(rows)
    controls = json.loads((OUT / "controls.json").read_text()) if (OUT / "controls.json").exists() else {}
    verdict = verdict_of(controls, summary)
    result = {"schema_version": 1, "experiment_id": "SOFT-HUB-20261024-001B-E001", "ticket": "SOFT-HUB-20261024-001B",
              "evidence_stage": "confirmatory", "verdict": verdict, "summary": summary, "controls": controls,
              "table": table, "rows": len(rows), "wall_seconds_this_run": round(time.time() - t0, 1)}
    (OUT / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"verdict": verdict, "summary": {k: v for k, v in summary.items() if k != "compositions"},
                      "compositions": summary["compositions"]}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
