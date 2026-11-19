"""Referee R1 for VARIABLE-OUTPUT-READER-20261118-001I (own code, on the referee's 001F-R1 machinery and RING-READ-R1's exact
max-flow bond search; none of the study's checkers are imported; histories are read from fixtures.json and families.json as data).

  ../../../.venv/bin/python -B referee_i.py <part> [args] > referee_i_<part>.json      (from this directory)

Parts:
  fixtures      the six fixtures replayed: W's fifteen pair minima, the forced supports T, P, Q, A (common K <= 4
                neighbourhoods), the certificate word W + T + Q and its excluded pair, the space enlarged by W (first horizon
                where its table differs, entries changed), the permutations (5 8)(10 13), (7 8) and (10 11) with the horizons
                they preserve and the triple verdicts they change, and the 62 one-junction extensions of the base fixture.
  w71           the 71-distinction witness: legality, family membership (one binary two-fresh join), legal triples, the swap's
                clipped agreement (exact bonds through K = 6 by the flow-pruned search), the entries changed at K = 6, and the
                part holding the cycle and the marked holders after the ordinary bridges are removed.
  family W      the all-size theorem exhaustively at widths 15..W: every reachable type that has a history with a ternary seed,
                at most one two-parent two-fresh join and three fresh everywhere else, against every reachable rival of its
                width, at K through 6 (the theorem) and K through 5 (one below); and the same for the base fixture's class.
  conditions N  the structural conditions 1 to 3 on N random sources of the one-exception family (widths about 30 to 60):
                short shores (max-flow), an identifying pair for every five- and six-place star (exact bonds through K = 6),
                and the cactus condition on the four-place graph.
  shrink        the seven-to-six control: boundary before and after the shrinking join.
  w24           the width-24 fixture live_2_2 and the width-24 intersecting-cycle source against every reachable type of width
                24 (the referee's census), at K through 4, 5 and 6.
"""
import itertools
import json
import random
import sys
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

import networkx as nx
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/VARIABLE-OUTPUT-READER-20261118-001F/referee-R1"))
sys.path.insert(0, str(ROOT / "research/VARIABLE-OUTPUT-READER-20261118-001G/referee-R1"))
sys.path.insert(0, str(ROOT / "research/RING-READ-20261118-001/referee-R1"))
import referee_f as F  # noqa: E402
import referee_g as RG  # noqa: E402
import referee_ringread as RRD  # noqa: E402

FAM = ROOT / "proofs/VARIABLE-OUTPUT-READER-20261118-001I/VARIABLE-OUTPUT-READER-20261118-001I-P001_cycle_obstruction"


def span(rows):
    basis = {}
    for r in rows:
        while r:
            p = r.bit_length() - 1
            if p not in basis:
                basis[p] = r
                break
            r ^= basis[p]
    return basis


def in_span(basis, w):
    while w:
        p = w.bit_length() - 1
        if p not in basis:
            return False
        w ^= basis[p]
    return True


def table_rows(rows, n):
    """K table of the binary space spanned by `rows` (bitmasks), by enumerating the space (rank <= 20)."""
    basis = list(span(rows).values())
    words = [0]
    for b in basis:
        words += [w ^ b for w in words]
    words = sorted(set(words) - {0}, key=lambda w: bin(w).count("1"))
    minimal = []
    K = np.full((n, n), F.INF, dtype=np.int64)
    np.fill_diagonal(K, 0)
    for w in words:
        if any(m & w == m for m in minimal):
            continue
        minimal.append(w)
        bits = [b for b in range(n) if w >> b & 1]
        s = len(bits)
        for x, y in itertools.combinations(bits, 2):
            if K[x][y] > s:
                K[x][y] = K[y][x] = s
    return K


def agree_through(K1, K2):
    """Largest L with clip(K1, L) == clip(K2, L) entrywise on the same names."""
    best = 2
    for L in range(3, 30):
        if (F.clip(K1, L) == F.clip(K2, L)).all():
            best = L
        else:
            break
    return best


def permute(K, perm):
    n = len(K)
    p = list(range(n))
    for a, b in perm:
        p[a], p[b] = b, a
    return K[p][:, p], p


def part_fixtures():
    data = json.load(open(FAM / "fixtures.json"))
    out = {}
    W = data["false_support"]
    for case in data["cases"]:
        steps = [h["support"] for h in case["physical"]["history"]]
        J, legal, T, s = RG.replay(steps)
        n = 1 + max(max(S) for S in J)
        K, nb = F.bond_table(J, n)
        names = {h["site"]: sorted(h["support"]) for h in case["physical"]["history"]}
        lt = F.legal_triples(T, J)
        r = {"width": n, "history legal": legal, "bonds": nb, "legal triples": len(lt)}
        r["W's 15 pair minima (K histogram)"] = dict(sorted(Counter(int(K[x][y]) for x, y in itertools.combinations(W, 2)).items()))
        N4 = lambda e: {f for f in range(n) if f == e or K[e][f] <= 4}
        sup = {k: set(names[k]) for k in ("t", "p", "q", "w")}
        tp, tq, tc = sorted(sup["t"] & sup["p"])[0], sorted(sup["t"] & sup["q"])[0], sorted(sup["t"] & set(names["c"]))[0]
        pw, qw = sorted(sup["p"] & sup["w"])[0], sorted(sup["q"] & sup["w"])[0]
        pb, qb = sorted(sup["p"] & set(names["b"]))[0], sorted(sup["q"] & set(names["b"]))[0]
        r["forced: K(tp, tq) and common N4 = T"] = [int(K[tp][tq]), N4(tp) & N4(tq) == sup["t"]]
        r["forced: K(qw, qb) and common N4 = Q"] = [int(K[qw][qb]), N4(qw) & N4(qb) == sup["q"]]
        r["forced: K(pw, pb) and common N4 = P"] = [int(K[pw][pb]), N4(pw) & N4(pb) == sup["p"]]
        r["forced: K(pw, qw) and common N4 = A"] = [int(K[pw][qw]), N4(pw) & N4(qw) == sup["w"]]
        cert = set(W) ^ sup["t"] ^ sup["q"]
        r["W + T + Q"] = sorted(cert)
        r["largest K within W + T + Q (must exceed 4)"] = max(int(K[x][y]) for x, y in itertools.combinations(sorted(cert), 2))
        r["K(pb, wc)"] = int(K[pb][sorted(set(names["w"]) & set(names["c"]))[0]])
        rows = [sum(1 << x for x in S) for S in J]
        B = span(rows)
        r["W in the physical space"] = in_span(B, sum(1 << x for x in W))
        if n <= 26:
            K2 = table_rows(rows + [sum(1 << x for x in W)], n)
            r["space enlarged by W: physical and enlarged tables agree through K"] = agree_through(K, K2)
            r["space enlarged by W: full entries changed"] = int(sum(K[x][y] != K2[x][y] for x in range(n) for y in range(x + 1, n)))
        if case.get("marked_core_triple"):
            r["marked triple"] = case["marked_core_triple"]
        perms = {"mirrored": [((5, 8), (10, 13)), ((7, 8),)]}.get(case["case"].split()[0] if " " in case["case"] else case["case"], [])
        if "irror" in case["case"]:
            perms = [((5, 8), (10, 13)), ((7, 8),)]
        elif lt:
            perms = [((10, 11),)]
        for perm in perms:
            K2, p = permute(K, perm)
            imgs = {frozenset(p[x] for x in t) for t in lt}
            name = " ".join(f"({a} {b})" for a, b in perm)
            r[f"{name}: agrees through K"] = agree_through(K, K2)
            r[f"{name}: legal triples sent to forbidden ones"] = len(imgs - lt)
            if perm == ((5, 8), (10, 13)):
                Wi = sum(1 << p[x] for x in W)
                r[f"{name}: image of W in the physical space"] = in_span(B, Wi)
                r[f"{name}: image of W = P + A"] = {p[x] for x in W} == sup["p"] ^ sup["w"]
        out[case["case"]] = r
    # the 62 one-junction extensions of the base fixture
    base = [h["support"] for h in data["cases"][0]["physical"]["history"]]
    J, _, T, _ = RG.replay(base)
    nb = 1 + max(max(S) for S in J)
    ext = Counter()
    pos = 0
    owner = defaultdict(list)
    for k, S in enumerate(J):
        for x in S:
            owner[x].append(k)
    lc = T[2]
    named = Counter()
    for P in F.moves(T):
        ext[len(P)] += 1
        prod = 1
        for q in P:
            prod *= lc[q]
        named[len(P)] += 2 * prod
        T2 = F.add(T, P, 3)
        pos += bool(F.legal_triples(T2))
        T2 = F.add(T, P, 2)
        pos += bool(F.legal_triples(T2))
    out["base: legal one-junction parent sets by parent count"] = dict(ext)
    out["base: extensions (either fresh count) with a legal triple"] = pos
    out["base: legal one-junction extensions on named distinctions, by parent count (both fresh counts)"] = dict(named)
    return out


# ---------------------------------------------------------------- the 71-distinction witness


def exact_small_K(J, L):
    """Exact K through L (larger values pooled at L + 1) by the flow-pruned search over every shore."""
    stars = [frozenset(S) for S in J]
    masks = [sum(1 << b for b in S) for S in stars]
    n, adj, own = RRD.graph(stars)
    adjd = {u: dict(v) for u, v in adj.items()}
    nbits = len(own)
    with Pool(20) as pool:
        res = pool.map(RRD.search_root, [(adjd, n, r, L, 10 ** 9, L, masks) for r in range(n)])
    K = np.full((nbits, nbits), L + 1, dtype=np.int64)
    np.fill_diagonal(K, 0)
    bonds = 0
    for _, _, _, keep in res:
        for side, w in keep:
            bonds += 1
            bits = [b for b in range(w.bit_length()) if w >> b & 1]
            for x, y in itertools.combinations(bits, 2):
                if K[x][y] > len(bits):
                    K[x][y] = K[y][x] = len(bits)
    return K, bonds


def family_history(T, exceptions=1):
    """A birth order with a ternary seed, fresh 3 everywhere except at most `exceptions` two-parent two-fresh joins."""
    n, adj, loose = T
    deg = [bin(a).count("1") for a in adj]
    ar = [deg[i] + loose[i] for i in range(n)]

    def go(order, placed, npar, exc):
        if len(order) == n:
            return list(order)
        for i in range(n):
            if placed >> i & 1:
                continue
            P = [p for p in range(n) if placed >> p & 1 and adj[i] >> p & 1]
            if not 1 <= len(P) <= 3:
                continue
            f = ar[i] - len(P)
            e = 0
            if f != 3:
                if f == 2 and len(P) == 2 and exc < exceptions:
                    e = 1
                else:
                    continue
            if not all((bin(adj[p] & placed).count("1") - npar[p]) < ar[p] - npar[p] for p in P):
                continue
            A = [adj[p] & placed for p in P]
            if any(not (A[a] & A[b]) for a, b in itertools.combinations(range(len(P)), 2)):
                continue
            if len(P) == 3 and (A[0] & A[1] & A[2]):
                continue
            npar[i] = len(P)
            r = go(order + [i], placed | 1 << i, npar, exc + e)
            del npar[i]
            if r:
                return r
        return None
    for s in range(n):
        if ar[s] == 3:
            r = go([s], 1 << s, {s: 0}, 0)
            if r:
                return r
    return None


def part_w71():
    d = json.load(open(FAM / "families.json"))["sharp_one_binary"]
    J, legal, T, s = RG.replay(d["history"])
    n = 1 + max(max(S) for S in J)
    lt = F.legal_triples(T, J)
    K, bonds = exact_small_K(J, 7)
    a, b = d["swapped_bits"]
    K2, p = permute(K, ((a, b),))
    fresh = []
    for k, S in enumerate(J):
        fresh.append(sum(1 for x in S if all(x not in Q for Q in J[:k])))
    parents = [len(S) - f for S, f in zip(J, fresh)]
    exc = [(k, parents[k], fresh[k]) for k in range(1, len(J)) if fresh[k] != 3]
    mark = frozenset(d["legal_mark"])
    img = frozenset(p[x] for x in mark)
    pairs = n * (n - 1) // 2
    G = nx.Graph()
    for k in range(len(J)):
        G.add_node(k)
    for k1, k2 in itertools.combinations(range(len(J)), 2):
        if set(J[k1]) & set(J[k2]):
            G.add_edge(k1, k2)
    G2 = G.copy()
    G2.remove_edges_from(list(nx.bridges(G)))
    holders = {k for x in mark for k, S in enumerate(J) if x in S}
    cyc = [k for k in range(17, len(J)) if len(J[k]) == 4]
    comp = nx.node_connected_component(G2, next(iter(holders)))
    return {"width": n, "junctions": len(J), "history legal": legal, "arities": dict(sorted(Counter(map(len, J)).items())),
            "joins whose fresh count is not 3 (site, parents, fresh)": exc, "legal triples": len(lt), "mark legal": mark in lt,
            "image of the mark legal": img in lt, "image repeats a holder": len({k for x in img for k, S in enumerate(J) if x in S}) < 3,
            "pairs": pairs, "bonds through K = 7 (exact search)": bonds,
            "entries equal after the swap, clipped through K = 5": int(sum(F.clip(K, 5)[x][y] == F.clip(K2, 5)[x][y] for x in range(n) for y in range(x + 1, n))),
            "entries changed, clipped through K = 6": int(sum(F.clip(K, 6)[x][y] != F.clip(K2, 6)[x][y] for x in range(n) for y in range(x + 1, n))),
            "marked holders and the new four-place sites in one part after removing ordinary bridges": holders <= comp and set(cyc) <= comp,
            "new four-place sites": cyc}


# ---------------------------------------------------------------- exhaustive all-rival check of the one-exception theorem


def _prep(T):
    J, n = F.supports(T)
    K, _ = F.bond_table(J, n)
    jneed = {0: n // 3, 2: (n + 1) // 3}.get(n % 3)          # width = 3j - (number of two-fresh exceptions)
    mem = T[0] == jneed and family_history(T) is not None
    return T, mem, {L: F.invariant(F.clip(K, L)) for L in (5, 6)}


def _check(args):
    T, rivals, L = args
    J, n = F.supports(T)
    C = F.clip(F.bond_table(J, n)[0], L)
    gens, nq, capped, q = F.generators(C)
    stars = {frozenset(S) for S in J}
    lt = F.legal_triples(T, J)
    iso = flips = 0
    for R in rivals:
        JR, _ = F.supports(R)
        CR = F.clip(F.bond_table(JR, n)[0], L)
        pm = F.isometric(C, CR)
        if pm is None:
            continue
        iso += 1
        flips += {frozenset(pm[x] for x in t) for t in lt} != F.legal_triples(R, JR)
    return {"keeps stars": F.keeps(gens, stars), "keeps triples": F.keeps(gens, lt) if lt else True, "iso": iso, "flips": flips,
            "capped": capped, "legal": len(lt)}


def part_family(wmax=23, wmin=12):
    levels = F.census(wmax)
    out = {}
    with Pool(20) as pool:
        for w in range(wmin, wmax + 1):
            rows = pool.map(_prep, levels.get(w, []), chunksize=32)
            mem = [i for i, r in enumerate(rows) if r[1]]
            if not mem:
                continue
            res = {}
            for L in (6, 5):
                bucket = defaultdict(list)
                for i, r in enumerate(rows):
                    bucket[r[2][L]].append(i)
                jobs = [(rows[i][0], [rows[k][0] for k in bucket[rows[i][2][L]] if k != i], L) for i in mem]
                rs = pool.map(_check, jobs, chunksize=4)
                res[f"K through {L}"] = {"family sources": len(mem), "with a legal triple": sum(x["legal"] > 0 for x in rs),
                                         "a clipped symmetry moves a junction support": sum(not x["keeps stars"] for x in rs),
                                         "a clipped symmetry moves a legal triple to a forbidden one": sum(not x["keeps triples"] for x in rs),
                                         "rivals with an isometric clipped table": sum(x["iso"] for x in rs),
                                         "... changing a triple verdict": sum(x["flips"] for x in rs),
                                         "searches capped": sum(x["capped"] for x in rs)}
            out[f"width {w}"] = res
            print(w, json.dumps(res), file=sys.stderr, flush=True)
    return out


# ---------------------------------------------------------------- structural conditions on random one-exception sources


def random_source(rng, target, exc_at):
    """Random history: ternary seed, three fresh everywhere except one two-parent two-fresh join at step exc_at (if possible)."""
    T = F.seed()
    step = 0
    while F.width(T) < target:
        mv = F.moves(T)
        if step == exc_at:
            two = [P for P in mv if len(P) == 2]
            if two:
                T = F.add(T, rng.choice(two), 2)
                step += 1
                continue
        if not mv:
            return None
        w = [1 if len(P) == 1 else 4 for P in mv]
        P = rng.choices(mv, weights=w)[0]
        T = F.add(T, P, 3)
        step += 1
    return T


def _cond(args):
    seed, target = args
    rng = random.Random(seed)
    T = None
    while T is None:
        T = random_source(rng, target, rng.randrange(1, 12))
    J, n = F.supports(T)
    # condition 1: least cut around three or more sites
    m1 = min_cut_three(T)
    # condition 2: exact K through 6, an identifying pair for every star of size 5 or 6
    K, _ = exact_small_K_serial(J, 6)
    ok2 = True
    for S in J:
        d = len(S)
        if d not in (5, 6):
            continue
        good = False
        for x, y in itertools.combinations(sorted(S), 2):
            if K[x][y] != d:
                continue
            if not any(z not in S and K[x][z] <= d and K[y][z] <= d for z in range(n)):
                good = True
                break
        ok2 &= good
    # condition 3: the four-place graph is a cactus (every edge on at most one simple cycle)
    G4 = nx.Graph()
    four = [k for k, S in enumerate(J) if len(S) == 4]
    G4.add_nodes_from(four)
    for a, b in itertools.combinations(four, 2):
        if set(J[a]) & set(J[b]):
            G4.add_edge(a, b)
    cactus = all(len(c) <= 1 for c in [None]) if False else is_cactus(G4)
    return {"width": n, "junctions": len(J), "has the two-fresh join": n == 3 * len(J) - 1, "least cut around three or more sites": m1, "identifying pairs": ok2, "cactus": cactus,
            "largest junction": max(map(len, J)), "legal triples": len(F.legal_triples(T, J))}


def is_cactus(G):
    for comp in nx.biconnected_components(G):
        H = G.subgraph(comp)
        if H.number_of_edges() > 1 and H.number_of_edges() != H.number_of_nodes():
            return False
    return True


def min_cut_three(T):
    sys.path.insert(0, str(ROOT / "research/VARIABLE-OUTPUT-READER-20261118-001H/referee-R1"))
    import referee_h as RH
    return RH.min_cut_three(T)[0]


def exact_small_K_serial(J, L):
    stars = [frozenset(S) for S in J]
    masks = [sum(1 << b for b in S) for S in stars]
    n, adj, own = RRD.graph(stars)
    adjd = {u: dict(v) for u, v in adj.items()}
    nbits = len(own)
    K = np.full((nbits, nbits), L + 1, dtype=np.int64)
    np.fill_diagonal(K, 0)
    for r in range(n):
        _, _, _, keep = RRD.search_root((adjd, n, r, L, 10 ** 9, L, masks))
        for side, w in keep:
            bits = [b for b in range(w.bit_length()) if w >> b & 1]
            for x, y in itertools.combinations(bits, 2):
                if K[x][y] > len(bits):
                    K[x][y] = K[y][x] = len(bits)
    return K, None


def part_conditions(N=300):
    with Pool(20) as pool:
        rows = pool.map(_cond, [(s, 30 + (s % 31)) for s in range(N)])
    return {"sources": len(rows), "widths": [min(r["width"] for r in rows), max(r["width"] for r in rows)],
            "condition 1 (least cut around >= 3 sites >= 7)": sum(r["least cut around three or more sites"] >= 7 for r in rows),
            "condition 2 (an identifying pair for every 5- and 6-place star)": sum(r["identifying pairs"] for r in rows),
            "condition 3 (four-place graph a cactus)": sum(r["cactus"] for r in rows),
            "least cut histogram": dict(sorted(Counter(r["least cut around three or more sites"] for r in rows).items())),
            "largest junction histogram": dict(sorted(Counter(r["largest junction"] for r in rows).items())),
            "with a legal triple": sum(r["legal triples"] > 0 for r in rows),
            "with the two-fresh join": sum(r["has the two-fresh join"] for r in rows)}


def part_shrink():
    d = json.load(open(FAM / "families.json"))["single_ternary_shrinking_control"]
    J, legal, T, s = RG.replay(d["history"])
    last = J[-1]
    before = J[:-1]
    cut = lambda JJ: len(set().union(*map(set, JJ)) - {x for x in set().union(*map(set, JJ)) if sum(x in S for S in JJ) == 2})
    # boundary of the set of all sites = the distinctions held once
    return {"history legal": legal, "boundary before the last join": cut(before), "boundary after": cut(J),
            "last join (parents, fresh)": [len([x for x in last if any(x in S for S in before)]), len([x for x in last if not any(x in S for S in before)])]}


# ---------------------------------------------------------------- width 24: two named sources against every rival


def _inv24(T):
    J, n = F.supports(T)
    K, _ = F.bond_table(J, n)
    return {L: F.invariant(F.clip(K, L)) for L in (4, 5, 6)}


def part_w24():
    """The width-24 fixture `live_2_2` (claimed: K through 5 fixes every support against every rival; K through 4 has an
    opposing witness) and the width-24 intersecting-cycle source (two two-fresh joins; claimed settled against every rival at
    K through 6 by the block proof), each against every reachable type of width 24."""
    fx = json.load(open(FAM / "fixtures.json"))
    fam = json.load(open(FAM / "families.json"))
    named = {"fixture live_2_2": [h["support"] for h in next(c for c in fx["cases"] if c["case"] == "live_2_2")["physical"]["history"]],
             "intersecting cycles, one repetition": fam["nonshrinking_intersecting_cycles"][0]["history"]}
    levels = F.census(24)
    types = levels[24]
    with Pool(20) as pool:
        invs = pool.map(_inv24, types, chunksize=64)
    out = {"width-24 types": len(types)}
    for name, steps in named.items():
        J, legal, T, s = RG.replay(steps)
        n = 1 + max(max(S) for S in J)
        K, _ = F.bond_table(J, n)
        G0 = F.graph(T)
        lt = F.legal_triples(T, J)
        stars = {frozenset(S) for S in J}
        res = {"width": n, "history legal": legal, "legal triples": len(lt)}
        for L in (4, 5, 6):
            C = F.clip(K, L)
            iv = F.invariant(C)
            cands = [i for i, x in enumerate(invs) if x[L] == iv]
            iso = flips = same = 0
            for i in cands:
                R = types[i]
                if nx.is_isomorphic(G0, F.graph(R), node_match=F.nm):
                    same += 1
                    continue
                JR, _ = F.supports(R)
                pm = F.isometric(C, F.clip(F.bond_table(JR, n)[0], L))
                if pm is None:
                    continue
                iso += 1
                flips += {frozenset(pm[x] for x in t) for t in lt} != F.legal_triples(R, JR)
            gens, nq, capped, q = F.generators(C)
            res[f"K through {L}"] = {"types sharing the invariant": len(cands), "of which the source's own type": same,
                                     "other types with an isometric clipped table": iso, "... changing a triple verdict": flips,
                                     "every clipped symmetry keeps the supports": F.keeps(gens, stars),
                                     "every clipped symmetry keeps the legal triples": F.keeps(gens, lt) if lt else True}
        out[name] = res
    return out


if __name__ == "__main__":
    part = sys.argv[1]
    args = [int(a) for a in sys.argv[2:]]
    f = {"fixtures": part_fixtures, "w71": part_w71, "family": part_family, "conditions": part_conditions, "shrink": part_shrink,
         "w24": part_w24}[part]
    print(json.dumps(f(*args), indent=1, default=str))
