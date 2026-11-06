#!/usr/bin/env python3
"""Producer for FREEZING-KNOTS-20261020-001A-E001 (exploratory; see contract.json).

At planted q-colourings of random d-regular graphs, measure the fraction of
vertices, and of star knots on q neighbours of a vertex, that a change inside
the ball of radius L can recolour. Compare with exact values of the
frozen-branch recursion on the d-regular tree. At small n, test whether the
star relation over all colourings of the graph is still the knot.

Writes, under artifacts/FREEZING-KNOTS-20261020-001A/<this folder>/:
- result.json;
- raw_rows.jsonl;
- balls.json.gz: stored balls with verdicts, for the checker;
- relation.json.gz: small graphs, stars, realizable triples and witnesses;
- run_output.txt.

    python3 -B run.py
"""

from __future__ import annotations

import gzip
import json
import random
import sys
import time
from collections import Counter, defaultdict
from itertools import combinations, product
from math import comb, sqrt
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / "FREEZING-KNOTS-20261020-001A" / HERE.name
SEED = 20261020
LOG = []


def log(msg):
    line = f"[{time.time() - START:.0f}s] {msg}"
    LOG.append(line)
    print(line, flush=True)


# ------------------------------------------------------------------ planted graphs

def planted(n, d, q, rng):
    """A balanced q-colouring and a simple d-regular graph whose edges all join different colours."""
    colour = [v % q for v in range(n)]
    rng.shuffle(colour)
    while True:
        stubs = {c: [] for c in range(q)}
        for v in range(n):
            stubs[colour[v]].extend([v] * d)
        for c in stubs:
            rng.shuffle(stubs[c])
        edges, ok, total = [], True, n * d
        while total:
            r = rng.randrange(total)
            for c1 in range(q):
                if r < len(stubs[c1]):
                    break
                r -= len(stubs[c1])
            u = stubs[c1].pop()
            others = [c for c in range(q) if c != c1 and stubs[c]]
            if not others:
                ok = False
                break
            c2 = rng.choices(others, [len(stubs[c]) for c in others])[0]
            edges.append((u, stubs[c2].pop()))
            total -= 2
        if ok:
            break

    def key(a, b):
        return (a, b) if a < b else (b, a)

    cnt = Counter(key(a, b) for a, b in edges)
    present = set(cnt)
    bad = [i for i, (a, b) in enumerate(edges) if cnt[key(a, b)] > 1]
    while bad:
        i = bad.pop()
        a, b = edges[i]
        if cnt[key(a, b)] <= 1:
            continue
        j = rng.randrange(len(edges))
        x, y = edges[j]
        if rng.random() < 0.5:
            x, y = y, x
        if (len({a, b, x, y}) < 4 or colour[a] == colour[y] or colour[x] == colour[b]
                or key(a, y) in present or key(x, b) in present):
            bad.append(i)
            continue
        for e in (key(a, b), key(x, y)):
            cnt[e] -= 1
            if cnt[e] == 0:
                present.discard(e)
        edges[i], edges[j] = (a, y), (x, b)
        for e in (key(a, y), key(x, b)):
            cnt[e] += 1
            present.add(e)
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    for v in range(n):
        adj[v].sort()
        assert len(adj[v]) == d and len(set(adj[v])) == d
    assert all(colour[a] != colour[b] for a, b in edges)
    return colour, adj


# ------------------------------------------------------------------ balls

def ball(v, radius, adj):
    dist = {v: 0}
    layers = [[v]]
    for k in range(1, radius + 1):
        nxt = []
        for u in layers[-1]:
            for w in adj[u]:
                if w not in dist:
                    dist[w] = k
                    nxt.append(w)
        layers.append(nxt)
    return dist, layers


def tree_like(dist, layers, L, adj):
    for k in range(1, L + 2):
        for u in layers[k]:
            if sum(1 for w in adj[u] if dist.get(w) == k - 1) != 1:
                return False
    for k in range(L + 1):
        for u in layers[k]:
            if any(dist.get(w) == k for w in adj[u]):
                return False
    return True


def frozen_dp(v, L, colour, adj, q):
    """None if the radius-(L+1) ball is not a tree; else whether v is forced inside B_L(v) by the colours at distance L+1."""
    dist, layers = ball(v, L + 1, adj)
    if not tree_like(dist, layers, L, adj):
        return None
    allowed = {u: 1 << colour[u] for u in layers[L + 1]}
    for k in range(L, -1, -1):
        for u in layers[k]:
            kids = [allowed[w] for w in adj[u] if dist.get(w) == k + 1]
            allowed[u] = sum(1 << c for c in range(q) if all(m != 1 << c for m in kids))
    return allowed[v] == 1 << colour[v]


def ball_record(v, L, colour, adj):
    dist, layers = ball(v, L + 1, adj)
    verts = [u for layer in layers for u in layer]
    index = {u: k for k, u in enumerate(verts)}
    edges = sorted({(min(index[u], index[w]), max(index[u], index[w])) for u in verts for w in adj[u] if w in index})
    return {"L": L, "dist": [dist[u] for u in verts], "colour": [colour[u] for u in verts], "edges": edges}


def search_native(rec, q, cap_nodes=2_000_000):
    """Exhaustive search on a stored ball: can the centre take another colour with distance L+1 fixed?"""
    n = len(rec["dist"])
    nbrs = [[] for _ in range(n)]
    for a, b in rec["edges"]:
        nbrs[a].append(b)
        nbrs[b].append(a)
    L = rec["L"]
    free = [u for u in range(n) if rec["dist"][u] <= L]
    fixed = {u: rec["colour"][u] for u in range(n) if rec["dist"][u] == L + 1}
    domains = {}
    for u in free:
        dom = set(range(q)) - {fixed[w] for w in nbrs[u] if w in fixed}
        if u == 0:
            dom.discard(rec["colour"][0])
        domains[u] = frozenset(dom)
    if any(not d for d in domains.values()):
        return False
    nodes = 0

    def rec_search(doms):
        nonlocal nodes
        nodes += 1
        if nodes > cap_nodes:
            raise RuntimeError("search cap")
        if not doms:
            return True
        u = min(doms, key=lambda x: (len(doms[x]), x))
        for c in sorted(doms[u]):
            new, ok = {}, True
            for w, dm in doms.items():
                if w == u:
                    continue
                if c in dm and w in nbrs[u]:
                    dm = dm - {c}
                    if not dm:
                        ok = False
                        break
                new[w] = dm
            if ok and rec_search(new):
                return True
        return False

    return rec_search(domains)


# ------------------------------------------------------------------ tree values

def coverage(p, need, k, total):
    """P(k children, each forced w.p. p with a uniform colour among `total`, cover `need` given colours)."""
    return sum((-1) ** j * comb(need, j) * (1 - j * p / total) ** k for j in range(need + 1))


def p_sequence(q, d, L):
    ps = [1.0]
    for _ in range(L):
        ps.append(coverage(ps[-1], q - 1, d - 1, q - 1))
    return ps


def psi(q, d, p):
    return coverage(p, q - 1, d, q - 1)


def star_exact(q, d, L):
    """Exact probability that the star knot on z's first q neighbours is native at radius L on the broadcast tree.

    Fix z's colour 0. A star member a_i (colour c_i) is frozen at radius L iff the colours of its outer children
    forced at depth L, together with 0 when z is forced in its branch away from a_i, cover every colour but c_i.
    z is forced there iff the neighbours a_j (j != i) whose outer children forced at depth L-2 cover every colour
    but c_j carry all colours other than 0 (for L = 1 the a_j are fixed, so they always count)."""
    ps = p_sequence(q, d, L)
    pL = ps[L]
    pL2 = ps[L - 2] if L >= 2 else None
    own = 1
    dist = {(0, 0): 1.0}
    for _ in range(d - 1):
        new = defaultdict(float)
        for (X, Y), pr in dist.items():
            for c in range(q):
                if c == own:
                    continue
                pc = pr / (q - 1)
                opts = [(pL, 1, 1), (pL2 - pL, 0, 1), (1 - pL2, 0, 0)] if L >= 2 else [(pL, 1, 0), (1 - pL, 0, 0)]
                for w, fx, fy in opts:
                    if w > 0:
                        new[(X | (1 << c) if fx else X, Y | (1 << c) if fy else Y)] += pc * w
        dist = new
    others = ((1 << q) - 1) & ~(1 << own)
    need_g = others & ~1
    feat = defaultdict(float)
    for (X, Y), pr in dist.items():
        feat[((X & others) == others, (X & need_g) == need_g, L == 1 or (Y & others) == others)] += pr
    p_o = sum(pr for (f, g, o), pr in feat.items() if o)
    cover_ns = {0: 1.0}
    for _ in range(d - q):
        new = defaultdict(float)
        for C, pr in cover_ns.items():
            for c in range(1, q):
                new[C | (1 << c)] += pr / (q - 1) * p_o
                new[C] += pr / (q - 1) * (1 - p_o)
        cover_ns = new
    target = ((1 << q) - 1) & ~1
    members = [(c, f, g, o, pr / (q - 1)) for c in range(1, q) for (f, g, o), pr in feat.items() if pr > 0]
    total = 0.0
    for combo in product(members, repeat=q):
        weight = 1.0
        for m in combo:
            weight *= m[4]
        if weight == 0:
            continue
        o_mask = [sum(1 << cj for j, (cj, fj, gj, oj, _) in enumerate(combo) if oj and j != i) for i in range(q)]
        for C, pc in cover_ns.items():
            if all(not (fi or (gi and ((C | o_mask[i]) & target) == target))
                   for i, (ci, fi, gi, oi, _) in enumerate(combo)):
                total += weight * pc
    return total


def tree_limit(q, d, iters=20000):
    p = 1.0
    for _ in range(iters):
        p = coverage(p, q - 1, d - 1, q - 1)
    p = max(p, 0.0)
    mu = coverage(p, q - 2, d - 1, q - 1)
    zeta = coverage(p, q - 1, d - q, q - 1) if d - q >= q - 1 else 0.0
    star = (1 - p) ** q * (1 - zeta) + (1 - mu) ** q * zeta
    return {"p_star": p, "frozen_vertex": psi(q, d, p), "mu": mu, "zeta": zeta, "star_native": star,
            "p_first": [round(x, 6) for x in p_sequence(q, d, 6)]}


# ------------------------------------------------------------------ the relation over all colourings

def colourings_solver(n, nbrs, fixed, cap=1, store=False):
    """Count proper 3-colourings agreeing with fixed (up to cap); returns (count, first witness)."""
    domains = {}
    for u in range(n):
        if u in fixed:
            continue
        dom = {0, 1, 2} - {fixed[w] for w in nbrs[u] if w in fixed}
        if not dom:
            return 0, None
        domains[u] = frozenset(dom)
    for u in fixed:
        if any(w in fixed and fixed[w] == fixed[u] for w in nbrs[u]):
            return 0, None
    count, witness = 0, None

    def rec(doms, assign):
        nonlocal count, witness
        if count >= cap:
            return
        if not doms:
            count += 1
            if witness is None:
                witness = dict(assign)
            return
        u = min(doms, key=lambda x: (len(doms[x]), x))
        for c in sorted(doms[u]):
            new, ok = {}, True
            for w, dm in doms.items():
                if w == u:
                    continue
                if c in dm and w in nbrs[u]:
                    dm = dm - {c}
                    if not dm:
                        ok = False
                        break
                new[w] = dm
            if ok:
                assign[u] = c
                rec(new, assign)
                del assign[u]
            if count >= cap:
                return

    rec(domains, dict(fixed))
    return count, witness


def relation_study(rng):
    rows, store = [], []
    not_distinct = {t for t in product(range(3), repeat=3) if len(set(t)) < 3}
    for d in (3, 4, 5, 6, 7):
        for n in (24, 36):
            for g in range(4):
                colour, adj = planted(n, d, 3, rng)
                nbrs = [set(a) for a in adj]
                count, _ = colourings_solver(n, nbrs, {}, cap=3000)
                stars = []
                for z in range(n):
                    trip = next((t for t in combinations(adj[z], 3)
                                 if all(b not in nbrs[a] for a, b in combinations(t, 2))), None)
                    if trip:
                        stars.append((z, trip))
                    if len(stars) == 6:
                        break
                graph_rec = {"d": d, "n": n, "g": g, "colour": colour, "adj": adj, "colourings_capped": count, "stars": []}
                for z, (a, b, c) in stars:
                    realized, witnesses = [], {}
                    for t in product(range(3), repeat=3):
                        cnt, wit = colourings_solver(n, nbrs, {a: t[0], b: t[1], c: t[2]})
                        if cnt:
                            assert all(wit[u] != wit[w] for u in range(n) for w in adj[u])
                            realized.append(t)
                            witnesses["".join(map(str, t))] = [wit[u] for u in range(n)]
                    is_knot = set(realized) == not_distinct
                    rows.append({"kind": "relation", "d": d, "n": n, "g": g, "z": z, "star": [a, b, c],
                                 "realized": len(realized), "is_knot": is_knot, "colourings_capped": count})
                    graph_rec["stars"].append({"z": z, "star": [a, b, c], "realized": ["".join(map(str, t)) for t in realized],
                                               "witnesses": witnesses})
                store.append(graph_rec)
            log(f"relation d={d} n={n} done")
    return rows, store


# ------------------------------------------------------------------ run

def main():
    global START
    START = time.time()
    rng = random.Random(SEED)
    OUT.mkdir(parents=True, exist_ok=True)
    rows, balls = [], []
    local = {}
    roster = [(3, d, 240000, (1, 2, 3) if d <= 6 else (1, 2)) for d in (3, 4, 5, 6, 7)]
    roster += [(4, d, 60000, (1,)) for d in (9, 10, 11)]
    for q, d, n, Ls in roster:
        colour, adj = planted(n, d, q, rng)
        log(f"planted q={q} d={d} n={n}")
        centres = [rng.randrange(n) for _ in range(4000)]
        for L in Ls:
            vf = vt = sn = st = 0
            for z in centres:
                f = frozen_dp(z, L, colour, adj, q)
                if f is not None:
                    vt += 1
                    vf += f
                members = adj[z][:q]
                verdicts = [frozen_dp(a, L, colour, adj, q) for a in members]
                if all(x is not None for x in verdicts):
                    st += 1
                    sn += not any(verdicts)
            pl = p_sequence(q, d, L)[L]
            row = {"kind": "local", "q": q, "d": d, "n": n, "L": L, "centres": len(centres),
                   "vertex_tree_like": vt, "vertex_frozen": vf, "frozen_fraction": vf / vt if vt else None,
                   "psi": psi(q, d, pl), "wrong_formula": coverage(pl, q - 1, d - 1, q - 1),
                   "star_tree_like": st, "star_native": sn, "native_fraction": sn / st if st else None,
                   "star_exact": star_exact(q, d, L)}
            rows.append(row)
            local[f"q{q}_d{d}_L{L}"] = row
            log(f"  L={L}: frozen {row['frozen_fraction']:.4f} vs psi {row['psi']:.4f} ({vt}); "
                f"star native {row['native_fraction']} vs exact {row['star_exact']:.4f} ({st})")
            if L <= 2:
                keep = 300 if (q, d, L) == (3, 4, 2) else 100 if (q, d, L) == (4, 9, 1) else 40
                for z in centres:
                    if keep == 0:
                        break
                    f = frozen_dp(z, L, colour, adj, q)
                    if f is None:
                        continue
                    rec = ball_record(z, L, colour, adj)
                    rec.update({"q": q, "d": d, "verdict_frozen": f})
                    balls.append(rec)
                    keep -= 1
    tree = {}
    for q, ds in ((3, range(3, 9)), (4, range(6, 13)), (5, range(10, 18))):
        for d in ds:
            tree[f"q{q}_d{d}"] = {"q": q, "d": d, **tree_limit(q, d)}
    log("tree limits done")
    rel_rows, rel_store = relation_study(rng)
    rows += rel_rows

    c1 = {"checked": 0, "agree": 0}
    for rec in balls:
        if (rec["q"], rec["d"], rec["L"]) in ((3, 4, 2), (4, 9, 1)):
            native = search_native(rec, rec["q"])
            c1["checked"] += 1
            c1["agree"] += native == (not rec["verdict_frozen"])
    log(f"C1 exhaustive search agreement {c1}")

    def tol(v, n):
        return max(0.03, 3 * sqrt(max(v * (1 - v), 1e-12) / max(n, 1)))

    p1 = all(abs(r["frozen_fraction"] - r["psi"]) <= tol(r["psi"], r["vertex_tree_like"]) for r in local.values())
    p2 = all(abs(r["native_fraction"] - r["star_exact"]) <= tol(r["star_exact"], r["star_tree_like"])
             for r in local.values() if r["star_tree_like"] >= 100)
    wrong_fails = [k for k, r in local.items()
                   if abs(r["frozen_fraction"] - r["wrong_formula"]) > tol(r["wrong_formula"], r["vertex_tree_like"])]
    thresholds = {}
    for q in (3, 4, 5):
        ds = sorted(v["d"] for v in tree.values() if v["q"] == q)
        frozen_ds = [d for d in ds if tree[f"q{q}_d{d}"]["p_star"] > 1e-6]
        thresholds[q] = min(frozen_ds) if frozen_ds else None
    p3 = (thresholds == {3: 6, 4: 10, 5: 15}
          and all((v["p_star"] > 0.8 and v["star_native"] < 1e-3) if v["d"] >= thresholds[v["q"]]
                  else (v["p_star"] < 1e-6 and abs(v["star_native"] - 1) < 1e-9) for v in tree.values()))
    rel = defaultdict(lambda: [0, 0])
    for r in rel_rows:
        rel[(r["d"], r["n"])][0] += 1
        rel[(r["d"], r["n"])][1] += r["is_knot"]
    rel_frac = {f"d{d}_n{n}": c[1] / c[0] for (d, n), c in sorted(rel.items()) if c[0]}
    p4 = all(rel_frac[f"d3_n{n}"] >= 0.8 and rel_frac[f"d7_n{n}"] <= 0.5 for n in (24, 36))
    result = {
        "experiment_id": "FREEZING-KNOTS-20261020-001A-E001", "evidence_stage": "exploratory",
        "local": local, "tree": tree, "thresholds": {str(k): v for k, v in thresholds.items()},
        "relation_knot_fraction": rel_frac,
        "relation_sizes": {f"d{d}_n{n}": sorted(Counter(r["realized"] for r in rel_rows if r["d"] == d and r["n"] == n).items())
                           for d in (3, 4, 5, 6, 7) for n in (24, 36)},
        "predictions": {"P1": p1, "P2": p2, "P3": p3, "P4": p4},
        "controls": {"C1_exhaustive_agreement": c1, "C2_wrong_formula_rejected_at": wrong_fails,
                     "C2_rejected": bool(wrong_fails) and p1, "C3_witnesses_verified": True},
        "signal": p1 and p2 and p3,
        "wall_seconds": round(time.time() - START, 1),
    }
    (OUT / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    with (OUT / "raw_rows.jsonl").open("w") as fh:
        for r in rows:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
    with gzip.open(OUT / "balls.json.gz", "wt") as fh:
        json.dump(balls, fh)
    with gzip.open(OUT / "relation.json.gz", "wt") as fh:
        json.dump(rel_store, fh)
    log(f"predictions {result['predictions']} signal {result['signal']}")
    (OUT / "run_output.txt").write_text("\n".join(LOG) + "\n")


if __name__ == "__main__":
    sys.exit(main())
