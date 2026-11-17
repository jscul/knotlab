"""Referee R1 for DISTANCE-ORDER-20261117-001 (own code, nothing imported from the study).

  .venv/bin/python -B referee_order.py > referee_order.json

1. Census of every not-all-equal relation at n = 3..6 (the referee's relation enumeration from DISTANCE-INFO's referee): the
   table-only decoder of statement 3(b) (all counts 2^(n-1) means full; else N = largest triple sum / 2, and the relation is cut
   out by the triples whose counts sum to 2N), checked to rebuild every relation; strict betweenness; P1 (built from unit steps);
   gap graphs that are paths; distinct tau-with-N tables.
2. Knot trees: 300 random ones on up to 13 distinctions, all states by brute force: correlation (-1/3)^s at s steps apart, 0 with
   no row, and the close-time corollary (the knots are the triples pairwise one step apart).
3. The thread (n = 30) and the knot chain (15 knots): exact pair counts by the referee's own transfer matrices; strict
   betweenness triples; tau against steps apart.
4. The weave W(L), L = 6, 9, 12: the correlation of v(0,0) with every distinction by a float transfer matrix (order checks only),
   tau against steps apart, and two weaker readings of "outward from a start, nothing skipped":
     W-path: every v has a one-step neighbour (sharing a knot) strictly nearer to v(0,0) in tau (a strictly monotone path of
             unit steps back to the start);
     W-ord:  every v other than the nearest has some w nearer to both v(0,0) and v than they are to each other (ordinal
             betweenness, the weakest notion of "something lies between").
"""
from __future__ import annotations

import itertools
import json
import math
import random
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "DISTANCE-INFO-20261117-001/referee-R1"))
import referee_census as RC  # noqa: E402  (the referee's own relation enumeration)


def tables(n, rel):
    """N and the disagreement counts of every relation row (uint64 words)."""
    R, W = rel.shape
    bits = RC.state_bits(n)
    pairs = list(itertools.combinations(range(n), 2))
    cnt = np.zeros((R, len(pairs)), np.int64)
    for pi, (u, v) in enumerate(pairs):
        mw = RC.to_words(bits[u] != bits[v])
        for w in range(W):
            cnt[:, pi] += np.bitwise_count(rel[:, w] & mw[w]).astype(np.int64)
    N = sum(np.bitwise_count(rel[:, w]).astype(np.int64) for w in range(W))
    return N, cnt, pairs


def decode(n, d, pairs):
    """Statement 3(b)'s decoder from the table alone; returns the set of states."""
    D = {p: int(x) for p, x in zip(pairs, d)}
    g = lambda u, v: D[(min(u, v), max(u, v))]
    if all(x == 1 << (n - 1) for x in D.values()):
        return set(range(1 << n))
    sums = {t: g(t[0], t[1]) + g(t[1], t[2]) + g(t[0], t[2]) for t in itertools.combinations(range(n), 3)}
    M = max(sums.values())
    knots = [t for t, s_ in sums.items() if s_ == M]
    return {s for s in range(1 << n) if all(len({(s >> a) & 1 for a in t}) == 2 for t in knots)}


def census():
    out = {}
    for n in (3, 4, 5, 6):
        if n == 3:
            rel = np.array([[0xFF], [0x7E]], np.uint64)  # no knot; one knot
        else:
            rel = RC.all_relations(n)
            rel = np.unique(rel[np.any(rel != 0, axis=1)], axis=0)
        N, cnt, pairs = tables(n, rel)
        decoded_ok = 0
        between = p1 = p1_nonconst = gap_path = 0
        tau_tables = set()
        for i in range(len(rel)):
            states = {s for s in range(1 << n) if (int(rel[i][s // 64]) >> (s % 64)) & 1}
            decoded_ok += decode(n, cnt[i], pairs) == states
            D = [[0] * n for _ in range(n)]
            for (u, v), x in zip(pairs, cnt[i]):
                D[u][v] = D[v][u] = int(x)
            has_b = any(D[a][c] > 0 and D[c][b] > 0 and D[a][b] == D[a][c] + D[c][b]
                        for a, b in itertools.combinations(range(n), 2) for c in range(n) if c not in (a, b))
            between += has_b
            pos = [D[u][v] for u, v in pairs if D[u][v] > 0]
            if pos:
                unit = min(pos)
                ok = all(D[u][v] % unit == 0 for u, v in pairs)
                if ok:
                    for u in range(n):
                        for v in range(n):
                            if u != v and D[u][v] > unit and not any(D[u][w] == unit and D[w][v] == D[u][v] - unit
                                                                     for w in range(n)):
                                ok = False
                p1 += ok
                p1_nonconst += ok and len(set(pos)) > 1
            gaps = [(u, v) for u, v in pairs if D[u][v] > 0 and not any(
                D[u][w] > 0 and D[w][v] > 0 and D[u][v] == D[u][w] + D[w][v] for w in range(n) if w not in (u, v))]
            deg = [0] * n
            for u, v in gaps:
                deg[u] += 1
                deg[v] += 1
            gap_path += len(gaps) == n - 1 and max(deg) <= 2 and min(deg) >= 1
            tau_tables.add((int(N[i]),) + tuple(abs(int(N[i]) - 2 * int(x)) for x in cnt[i]))
        out[n] = {"relations": int(len(rel)), "decoded_from_table_alone": int(decoded_ok), "with_strict_betweenness": between,
                  "p1": p1, "p1_nonconstant": p1_nonconst, "gap_graph_path": gap_path, "distinct_tau_tables_with_N": len(tau_tables)}
    return out


def knot_trees(trials=300, seed=7):
    rng = random.Random(seed)
    bad_corr = bad_cor = 0
    for _ in range(trials):
        k = rng.randint(1, 5)
        knots, used = [], []
        nxt = 0
        for _ in range(k):
            if used and rng.random() < 0.85:
                x = rng.choice(used)
                t = (x, nxt, nxt + 1)
            else:
                t = (nxt, nxt + 1, nxt + 2)
                nxt += 1
            nxt += 2
            knots.append(t)
            used = sorted(set(used) | set(t))
        n = nxt
        states = [s for s in range(1 << n) if all(len({(s >> a) & 1 for a in t}) == 2 for t in knots)]
        N = len(states)
        adj = {u: set() for u in range(n)}
        for t in knots:
            for a, b in itertools.combinations(t, 2):
                adj[a].add(b)
                adj[b].add(a)
        for u in range(n):
            dist = {u: 0}
            fr = [u]
            while fr:
                nf = []
                for x in fr:
                    for y in adj[x]:
                        if y not in dist:
                            dist[y] = dist[x] + 1
                            nf.append(y)
                fr = nf
            for v in range(u + 1, n):
                c = Fraction(sum(1 if ((s >> u) & 1) == ((s >> v) & 1) else -1 for s in states), N)
                want = Fraction(-1, 3) ** dist[v] if v in dist else Fraction(0)
                bad_corr += c != want
        tri = {t for t in itertools.combinations(range(n), 3) if all(b in adj[a] for a, b in itertools.combinations(t, 2))}
        bad_cor += tri != {tuple(sorted(t)) for t in knots}
    return {"trees": trials, "pairs_with_wrong_correlation": bad_corr, "trees_where_corollary_fails": bad_cor}


def line_counts(n, knots):
    """Exact pair counts for a pattern on 0..n-1 whose knots each span at most 3 consecutive indices, by a transfer over
    windows of two consecutive values; returns N and d[(u, v)]."""
    kn = {}
    for t in knots:
        kn.setdefault(max(t), []).append(t)

    def run(pins):
        table = {(): 1}
        for x in range(n):
            nt = {}
            for key, c in table.items():
                for b in ((pins[x],) if x in pins else (0, 1)):
                    k2 = key + (b,)
                    full = k2
                    ok = True
                    for t in kn.get(x, []):
                        vals = {full[len(full) - 1 - (x - a)] for a in t}
                        if len(vals) == 1:
                            ok = False
                    if ok:
                        nt[k2[-2:]] = nt.get(k2[-2:], 0) + c
            table = nt
        return sum(table.values())
    N = run({})
    d = {}
    for u, v in itertools.combinations(range(n), 2):
        d[(u, v)] = run({u: 0, v: 1}) + run({u: 1, v: 0})
    return N, d


def steps_matrix(n, knots):
    adj = {u: set() for u in range(n)}
    for t in knots:
        for a, b in itertools.combinations(t, 2):
            adj[a].add(b)
            adj[b].add(a)
    S = {}
    for u in range(n):
        dist = {u: 0}
        fr = [u]
        while fr:
            nf = []
            for x in fr:
                for y in adj[x]:
                    if y not in dist:
                        dist[y] = dist[x] + 1
                        nf.append(y)
            fr = nf
        S[u] = dist
    return S


def line_bases():
    out = {}
    for name, n, knots in (("thread n=30", 30, [(i, i + 1, i + 2) for i in range(28)]),
                           ("chain 15 knots", 31, [(2 * i, 2 * i + 1, 2 * i + 2) for i in range(15)])):
        N, d = line_counts(n, knots)
        g = lambda u, v: 0 if u == v else d[(min(u, v), max(u, v))]
        bt = sum(1 for a, b in itertools.combinations(range(n), 2) for c in range(n)
                 if c not in (a, b) and g(a, c) > 0 and g(c, b) > 0 and g(a, b) == g(a, c) + g(c, b))
        S = steps_matrix(n, knots)
        dev = max(abs(-math.log(abs(1 - 2 * g(u, v) / N), 3) - S[u][v]) for u, v in itertools.combinations(range(n), 2))
        out[name] = {"N": N, "strict_betweenness_triples": bt, "max_abs_tau_minus_steps": dev}
    return out


def weave(L):
    R = 1 << L
    a = np.arange(R)
    bit = lambda x, i: (x >> (i % L)) & 1
    T = np.ones((R, R), dtype=bool)
    for i in range(L):
        ai, ai1 = bit(a, i)[:, None], bit(a, i + 1)[:, None]
        bi, bi1 = bit(a, i)[None, :], bit(a, i + 1)[None, :]
        T &= ~((ai == ai1) & (ai1 == bi))
        T &= ~((ai1 == bi) & (bi == bi1))
    T = T.astype(np.float64)
    P = [np.eye(R)]
    for _ in range(L):
        P.append(P[-1] @ T)
    N = np.trace(P[L])
    spin = 1.0 - 2.0 * ((a[:, None] >> np.arange(L)[None, :]) & 1)
    corr = {}
    for r in range(L):
        M = spin[:, 0][:, None] * P[r]
        col = (M * P[L - r].T).sum(axis=0)
        for c in range(L):
            corr[(c, r)] = float((col * spin[:, c]).sum() / N)
    tau = {k: (0.0 if k == (0, 0) else -math.log(abs(v), 3)) for k, v in corr.items()}

    def steps(c, r):
        best = None
        for x in (c - L, c, c + L):
            for y in (r - L, r, r + L):
                s = abs(x) + abs(y) if x * y >= 0 else max(abs(x), abs(y))
                best = s if best is None else min(best, s)
        return best
    nbr = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)]
    keys = [k for k in tau if k != (0, 0)]
    w_path_fail = [k for k in keys if not any(tau[((k[0] + dx) % L, (k[1] + dy) % L)] < tau[k] - 1e-9 for dx, dy in nbr)]
    nearest = min(tau[k] for k in keys)
    w_ord_fail = []
    for k in keys:
        if tau[k] <= nearest + 1e-12:
            continue
        ok = False
        for w in keys:
            if w == k:
                continue
            dvw = ((k[0] - w[0]) % L, (k[1] - w[1]) % L)
            if dvw == (0, 0):
                continue
            if tau[w] < tau[k] - 1e-9 and tau[dvw] < tau[k] - 1e-9:
                ok = True
                break
        if not ok:
            w_ord_fail.append(k)
    by_steps = {}
    for k in keys:
        by_steps.setdefault(steps(*k), []).append(tau[k])
    return {"one_step_rate": (1 - corr[(1, 0)]) / 2, "tau_range_by_steps": {s: [min(v), max(v)] for s, v in sorted(by_steps.items())},
            "W_path_failures": len(w_path_fail), "W_path_failure_examples": w_path_fail[:6], "W_ord_failures": len(w_ord_fail),
            "distinctions": len(keys)}


def main():
    out = {"census": census(), "knot_trees": knot_trees(), "line_bases": line_bases(),
           "weave": {L: weave(L) for L in (6, 9, 12)}}
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
