"""Referee R1 for VARIABLE-OUTPUT-READER-20261118-001H (own code, on the referee's 001F-R1 machinery: shore-enumerated bond
tables, exact twin-quotient isometries; none of the study's checkers are imported; histories and the two base pairs are read
from horizon.json and 001G's six_check.json as data).

  ../../../.venv/bin/python -B referee_h.py <part> > referee_h_<part>.json      (from this directory)

Parts:
  witness   the 51-distinction and 21-distinction swaps: legality, bonds, the marked pair's K before and after, the clipped
            tables compared on the same names at every horizon, entries changed, legal triples and the image's verdict.
  shore     the theorem's key step, one size past the study's 2 x 3 x 3 box: every nonempty downset of the 3 x 3 x 3, 2 x 4 x 4
            and 2 x 2 x 10 boxes (and 2 x 3 x 3 again), with an output omitted at every eligible site (which minimises every cut):
            the construction's legality under the referee's law, the hypotheses (only the seed ternary, every four-place junction
            unary), and the least cut around three or more sites (max-flow over every three-site path forced inside; checked
            against brute force on the small downsets).
  cycle     the four-place cycle obstruction: legality, the 15 pairs of the six distinctions, holders, and whether they form
            an equation.
  cross     the 116,997 comparisons regenerated: continuations of 001G's two base pairs by up to two serial additions that
            never consume the mark (one representative bit per holder, as the study does), the eligible ones (a high junction,
            the base verdict kept), the equal-width pairs, and at K through 5 and 6 the pairs with an isometry of the clipped
            tables carrying the mark to itself, opposite verdicts, and not the same site graph.
"""
import itertools
import json
import sys
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/VARIABLE-OUTPUT-READER-20261118-001F/referee-R1"))
sys.path.insert(0, str(ROOT / "research/VARIABLE-OUTPUT-READER-20261118-001G/referee-R1"))
import referee_f as F  # noqa: E402
import referee_g as RG  # noqa: E402

H = ROOT / "proofs/VARIABLE-OUTPUT-READER-20261118-001H/VARIABLE-OUTPUT-READER-20261118-001H-P001_high_junctions"


def part_witness():
    data = json.load(open(H / "horizon.json"))
    out = {}
    for name in ("five_place_holders", "six_place_holders"):
        d = data[name]
        J, legal, T, s = RG.replay(d["history"])
        n = 1 + max(max(S) for S in J)
        K, nb = F.bond_table(J, n)
        a, b = d["transposition"]
        sw = list(range(n))
        sw[a], sw[b] = b, a
        K2 = K[sw][:, sw]
        lt = F.legal_triples(T, J)
        mark = frozenset(d["legal_mark"])
        img = frozenset(sw[x] for x in mark)
        eq = {}
        for L in range(3, 17):
            C1, C2 = F.clip(K, L), F.clip(K2, L)
            eq[L] = int(sum(C1[x][y] == C2[x][y] for x in range(n) for y in range(x + 1, n)))
        pairs = n * (n - 1) // 2
        m = sorted(mark)
        out[name] = {"width": n, "junctions": len(J), "history legal": legal, "arities": dict(Counter(map(len, J))), "bonds": nb,
                     "legal triples": len(lt), "mark legal": mark in lt, "image of the mark legal": img in lt,
                     "image repeats a holder": len({k for x in img for k, S in enumerate(J) if x in S}) < 3,
                     "K within the mark": {f"{x},{y}": int(K[x][y]) for x, y in itertools.combinations(m, 2)},
                     "K of the swapped pair's image (the marked pair after the swap)": {f"{x},{y}": int(K2[x][y]) for x, y in itertools.combinations(m, 2)},
                     "pairs": pairs, "largest L with every pair equal": max(L for L in eq if eq[L] == pairs),
                     "pairs equal through K = L": eq, "full entries changed": pairs - int(sum(K[x][y] == K2[x][y] for x in range(n) for y in range(x + 1, n))),
                     "largest D between two members of any legal triple": max(int(K[x][y]) - 1 for t in lt for x, y in itertools.combinations(sorted(t), 2))}
    return out


# ---------------------------------------------------------------- the shore bound on coordinate downsets


def downsets(a, b, c):
    """Nonempty downsets of the a x b x c box, as plane partitions (heights in 0..c, non-increasing along both axes)."""
    cells = [(x, y) for x in range(a) for y in range(b)]
    out = []

    def go(i, h):
        if i == len(cells):
            S = frozenset((x, y, z) for (x, y), k in h.items() for z in range(k))
            if S:
                out.append(S)
            return
        x, y = cells[i]
        top = c
        if x > 0:
            top = min(top, h[(x - 1, y)])
        if y > 0:
            top = min(top, h[(x, y - 1)])
        for k in range(top + 1):
            h[(x, y)] = k
            go(i + 1, h)
        del h[(x, y)]
    go(0, {})
    return out


def build(S):
    """The coordinate construction with an output omitted at every eligible site: the site graph, by the referee's law."""
    order = sorted(S, key=lambda p: (sum(p), p))
    idx = {p: i for i, p in enumerate(order)}
    T = None
    legal = True
    for p in order:
        preds = [tuple(p[k] - (k == d) for k in range(3)) for d in range(3) if p[d] > 0]
        succ_missing = [d for d in range(3) if tuple(p[k] + (k == d) for k in range(3)) not in S]
        outputs = 3 - (1 if len(preds) == 3 and succ_missing else 0)
        if T is None:
            T = (1, (0,), (3,))
            continue
        P = tuple(sorted(idx[q] for q in preds))
        legal &= F.legal_sites(T, P) and outputs in (2, 3)
        T = F.add(T, P, outputs)
    return T, legal, order


def min_cut_three(T):
    """Least cut around a set of three or more sites (exterior outside), by max-flow with each three-site path forced in."""
    n, adj, loose = T
    G = nx.DiGraph()
    for i in range(n):
        for j in range(n):
            if adj[i] >> j & 1:
                G.add_edge(i, j, capacity=1)
        if loose[i]:
            G.add_edge(i, "ext", capacity=loose[i])
    best = None
    paths = 0
    for mid in range(n):
        nb = [j for j in range(n) if adj[mid] >> j & 1]
        for u, v in itertools.combinations(nb, 2):
            paths += 1
            H2 = G.copy()
            for x in (u, mid, v):
                H2.add_edge("src", x, capacity=10 ** 6)
            val = nx.maximum_flow_value(H2, "src", "ext")
            best = val if best is None else min(best, val)
    return best, paths


def brute_min_cut_three(T):
    n, adj, loose = T
    best = None
    for U in range(1, 1 << n):
        if bin(U).count("1") < 3:
            continue
        c = 0
        for i in range(n):
            if U >> i & 1:
                c += loose[i] + bin(adj[i] & ~U).count("1")
        best = c if best is None else min(best, c)
    return best


def _shore_one(S):
    T, legal, order = build(S)
    J, nbits = F.supports(T)
    ar = [len(Q) for Q in J]
    deg_in = [sum(1 for k in range(3) if p[k] > 0) for p in order]
    hyp1 = sum(1 for x in ar if x == 3) == 1
    hyp2 = all(deg_in[i] == 1 for i in range(len(J)) if ar[i] == 4)
    m, paths = min_cut_three(T) if T[0] >= 3 else (None, 0)
    brute = brute_min_cut_three(T) if 3 <= T[0] <= 14 else None
    omitted = sum(1 for i in range(len(J)) if deg_in[i] == 3 and ar[i] == 5)
    return {"sites": T[0], "legal": legal, "hyp1": hyp1, "hyp2": hyp2, "min": m, "brute": brute, "paths": paths,
            "omissions": omitted}


def part_shore():
    out = {}
    with Pool(20) as pool:
        for box in ((2, 3, 3), (3, 3, 3), (2, 4, 4), (2, 2, 10)):
            D = downsets(*box)
            rows = pool.map(_shore_one, D, chunksize=4)
            three = [r for r in rows if r["sites"] >= 3]
            out[f"{box[0]} x {box[1]} x {box[2]}"] = {
                "nonempty downsets": len(rows), "with three or more sites": len(three),
                "construction legal under the law": sum(r["legal"] for r in rows),
                "only the seed ternary": sum(r["hyp1"] for r in rows), "every four-place junction unary": sum(r["hyp2"] for r in rows),
                "least cut around three or more sites (histogram)": dict(sorted(Counter(r["min"] for r in three).items())),
                "downsets with a cut of six or less around three or more sites": sum(1 for r in three if r["min"] <= 6),
                "brute force checked (<= 14 sites)": sum(1 for r in three if r["brute"] is not None),
                "brute force agrees": sum(1 for r in three if r["brute"] is not None and r["brute"] == r["min"]),
                "three-site paths tried": sum(r["paths"] for r in rows),
                "largest number of omitted outputs in one downset": max(r["omissions"] for r in rows)}
            print(box, json.dumps(out[f"{box[0]} x {box[1]} x {box[2]}"]), file=sys.stderr, flush=True)
    return out


# ---------------------------------------------------------------- the four-place cycle


def part_cycle():
    # seed {0,1,2}; t unary on the seed (3 fresh); p, q unary on t (3 fresh each); w on p, q (2 fresh); b on p, q (3 fresh);
    # c on t, w (3 fresh)
    steps = [[0, 1, 2], [0, 3, 4, 5],            # t takes 0
             [3, 6, 7, 8], [4, 9, 10, 11],       # p takes tp = 3, q takes tq = 4
             [6, 9, 12, 13],                     # w takes pw = 6, qw = 9, fresh 12, 13
             [7, 10, 14, 15, 16],                # b takes pb = 7, qb = 10
             [5, 12, 17, 18, 19]]                # c takes tc = 5, wc = 12
    J, legal, T, s = RG.replay(steps)
    n = 1 + max(max(S) for S in J)
    K, nb = F.bond_table(J, n)
    names = {"tc": 5, "wc": 12, "pb": 7, "qb": 10, "tp": 3, "wq": 9}
    six = sorted(names.values())
    word = sum(1 << x for x in six)
    holders = Counter(k for k, S in enumerate(J) for x in S if x in six)
    basis = {}
    for S in J:
        r = sum(1 << x for x in S)
        while r:
            p = r.bit_length() - 1
            if p not in basis:
                basis[p] = r
                break
            r ^= basis[p]
    w = word
    while w:
        p = w.bit_length() - 1
        if p not in basis:
            break
        w ^= basis[p]
    return {"history legal": legal, "arities": [len(S) for S in J], "width": n,
            "the six": names, "their 15 pair minima K": {f"{a},{b}": int(K[names[a]][names[b]]) for a, b in itertools.combinations(names, 2)},
            "all 15 at K <= 6": all(K[x][y] <= 6 for x, y in itertools.combinations(six, 2)),
            "most of the six at one junction": max(holders.values()),
            "the six form an equation (in the cut space)": w == 0}


# ---------------------------------------------------------------- the cross comparisons

MARK = (9, 11, 13)


def next_supports(J, reserve):
    T = F.from_supports(J)
    owner = defaultdict(list)
    for k, S in enumerate(J):
        for x in S:
            owner[x].append(k)
    loose = defaultdict(list)
    for x, ks in owner.items():
        if len(ks) == 1:
            loose[ks[0]].append(x)
    nb = 1 + max(owner)
    for P in F.moves(T):
        choice = [sorted(b for b in loose[p] if b not in reserve) for p in P]
        if any(not c for c in choice):
            continue
        consumed = [c[0] for c in choice]
        for f in (2, 3):
            yield J + [consumed + list(range(nb, nb + f))]


def _measure(J):
    T = F.from_supports(J)
    n = 1 + max(max(S) for S in J)
    K, _ = F.bond_table(J, n)
    return K, T, n


def _pair(args):
    (Ka, Ta, n), (Kb, Tb, _), L = args
    iso = F.isometric(F.clip(Ka, L), F.clip(Kb, L), frozenset(MARK)) is not None
    same = nx.is_isomorphic(F.graph(Ta), F.graph(Tb), node_match=F.nm)
    return iso, same, n


def _inv(J):
    K, T, n = _measure(J)
    return (K, T, n), {L: F.invariant_marked(F.clip(K, L), frozenset(MARK)) for L in (5, 6)}


def part_cross():
    six = json.load(open(ROOT / "proofs/VARIABLE-OUTPUT-READER-20261118-001G/VARIABLE-OUTPUT-READER-20261118-001G-P001_two_three_fresh/six_check.json"))
    sides = ([], [])
    gen = {}
    for c in six["cases"]:
        for side, key in enumerate(("source", "rival")):
            base = [h["support"] for h in c[key]["history"]]
            verdict = side == 0
            tiers = [[base]]
            for depth in range(2):
                tiers.append([K2 for J in tiers[depth] for K2 in next_supports(J, MARK)])
            info = []
            for depth, tier in enumerate(tiers):
                sel = []
                for J in tier:
                    T = F.from_supports(J)
                    if max(map(len, J)) >= 5 and (frozenset(MARK) in F.legal_triples(T, J)) == verdict:
                        sel.append(J)
                sides[side].extend(sel)
                info.append({"additions": depth, "paths": len(tier), "eligible": len(sel)})
            gen[f"{c['case']}/{key}"] = info
    width = lambda J: 1 + max(max(S) for S in J)
    wl_ = Counter(map(width, sides[0]))
    wr_ = Counter(map(width, sides[1]))
    pairs_by_width = {w: wl_[w] * wr_[w] for w in sorted(set(wl_) & set(wr_))}
    out = {"generation": gen, "equal-width path pairs": pairs_by_width, "total": sum(pairs_by_width.values())}
    with Pool(20) as pool:
        invs = pool.map(_inv, sides[0] + sides[1], chunksize=4)
        left, right = invs[:len(sides[0])], invs[len(sides[0]):]
        for L in (5, 6):
            bucket = defaultdict(list)
            for j, (m, iv) in enumerate(right):
                bucket[(m[2], iv[L])].append(j)
            cand = [(i, j) for i, (m, iv) in enumerate(left) for j in bucket[(m[2], iv[L])]]
            res = pool.map(_pair, [(left[i][0], right[j][0], L) for i, j in cand], chunksize=8)
            opp = Counter()
            same = 0
            for iso, s_, n in res:
                if iso and s_:
                    same += 1
                elif iso:
                    opp[n] += 1
            out[f"K through {L}"] = {"pairs passing the invariant": len(cand),
                                     "isometric (mark to mark) and the same site graph": same,
                                     "opposing pairs (isometric, opposite verdicts, different site graphs) by width": dict(sorted(opp.items())),
                                     "opposing pairs": sum(opp.values())}
            print(L, json.dumps(out[f"K through {L}"]), file=sys.stderr, flush=True)
    return out


if __name__ == "__main__":
    part = sys.argv[1]
    print(json.dumps({"witness": part_witness, "shore": part_shore, "cycle": part_cycle, "cross": part_cross}[part](), indent=1, default=str))
