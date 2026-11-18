"""Referee R1 for VARIABLE-OUTPUT-READER-20261118-001E (own code; none of the study's checkers or libraries are imported; the
width-32 supports and the five-frontier history are copied from the study's certificates as data).

  ../../../.venv/bin/python -B referee_e.py <part> > referee_e_<part>.json      (from this directory)

Built on the referee's 001D-R1 code (`referee_reader`: the serial law, GF(2) bonds and bond distances, legal triples, table
automorphisms).

Parts:
  w32    the width-32 table: the reader "all three pair distances six" against the legal triples on all 4,960 triples; the candidate
         spaces L + <S> (L = the equations both realizations share, S every word of three to six distinctions whose pairs fit
         the table's bound) that reproduce all 496 entries; the ternary minima d3({4, 11, 13}), d3({4, 11, 14}) and how many of the
         4,960 change under (13 14).
  five   the five-distinction frontier: the history replayed, its five loose distinctions, whether they form a bond, their ten
         distances, the legal triples among them; and after the next three-parent join.
  small  every reachable presentation of widths 15, 16 and 17 up to isomorphism (BFS on junctions, isomorphism of the incidence
         graphs, the seed unmarked, as the study counts them); `small 19` takes the census to width 19: the counts per width and junction number; whether any two distinct presentations of one width have isometric
         tables; whether every table automorphism keeps the legal triples.
"""
import itertools
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import networkx as nx
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/VARIABLE-OUTPUT-READER-20261118-001D/referee-R1"))
import referee_reader as RR  # noqa: E402


def bonds_list(P):
    """All bonds (inclusion-minimal nonzero dual words) as integer masks."""
    n = P.width()
    rows = np.array([sum(1 << b for b in S) for S in P.J], dtype=np.uint64)
    words = np.zeros(1, dtype=np.uint64)
    for r in rows:
        words = np.concatenate([words, words ^ r])
    words = np.unique(words[words != 0])
    size = np.bitwise_count(words)
    order = np.argsort(size, kind="stable")
    words, size = words[order], size[order]
    minimal = np.zeros(0, dtype=np.uint64)
    for s in np.unique(size):
        W = words[size == s]
        if len(minimal):
            W = W[~((W[:, None] & minimal[None, :]) == minimal[None, :]).any(axis=1)]
        minimal = np.concatenate([minimal, W])
    return [int(x) for x in minimal]


def table_from_rows(rows, n):
    P = RR.Pres([[b for b in range(n) if (r >> b) & 1] for r in rows])
    P.nb = n
    return RR.table(P)[0]


def span_basis(rows):
    basis = {}
    for r in rows:
        while r:
            p = r.bit_length() - 1
            if p not in basis:
                basis[p] = r
                break
            r ^= basis[p]
    return basis


def reduce(basis, w):
    while w:
        p = w.bit_length() - 1
        if p not in basis:
            return w
        w ^= basis[p]
    return 0


def canonical_space(rows):
    """A canonical reduced basis of the span (as a sorted tuple)."""
    basis = span_basis(rows)
    piv = sorted(basis, reverse=True)
    red = {}
    for p in piv:
        v = basis[p]
        for q in piv:
            if q != p and (v >> q) & 1 and q in red:
                v ^= red[q]
        red[p] = v
    # full reduction
    changed = True
    while changed:
        changed = False
        for p in piv:
            for q in piv:
                if q != p and (red[p] >> q) & 1:
                    red[p] ^= red[q]
                    changed = True
    return tuple(sorted(red.values()))


W32 = RR.W32


def part_w32():
    P = RR.Pres(W32)
    n = P.width()
    D, rows = RR.table(P)
    legal = P.legal_triples()
    reader = {frozenset(T) for T in itertools.combinations(range(n), 3) if all(D[x][y] == 6 for x, y in itertools.combinations(T, 2))}
    out = {"triples": len(list(itertools.combinations(range(n), 3))), "legal": len(legal),
           "reader 'all three distances six'": len(reader), "reader = legal": reader == legal}
    # the two realizations and their common part
    sw = lambda b: 14 if b == 13 else 13 if b == 14 else b
    rows0 = [sum(1 << b for b in S) for S in W32]
    rows1 = [sum(1 << sw(b) for b in S) for S in W32]
    B0, B1 = span_basis(rows0), span_basis(rows1)
    common = [r for r in rows0 if reduce(B1, r) == 0]
    L = span_basis(common)
    out["rank of the true space"] = len(B0)
    out["junction equations shared by both realizations"] = len(common)
    out["rank of L"] = len(L)
    DL = table_from_rows(common, n)
    out["L alone reproduces the table"] = bool((DL == D).all())
    # candidate one-more generators S: three to six distinctions, every internal pair with D <= |S| - 1, not in L
    Dl = D.tolist()
    cands = set()
    for k in range(3, 7):
        def ext(S):
            if len(S) == k:
                w = sum(1 << b for b in S)
                if reduce(L, w):
                    cands.add(canonical_space(common + [w]))
                return
            start = S[-1] + 1 if S else 0
            for b in range(start, n):
                if all(Dl[b][x] <= k - 1 for x in S):
                    ext(S + [b])
        ext([])
    out["distinct candidate spaces L + <S>"] = len(cands)
    matches = []
    for sp in cands:
        Dc = table_from_rows(list(sp), n)
        if (Dc == D).all():
            matches.append(sp)
    out["candidate spaces reproducing all 496 entries"] = len(matches)
    out["... the true space among them"] = canonical_space(rows0) in matches
    out["... the swapped space among them"] = canonical_space(rows1) in matches
    # ternary minima
    bl = bonds_list(P)
    def d3(T):
        m = sum(1 << b for b in T)
        sizes = [bin(w).count("1") for w in bl if w & m == m]
        return min(sizes) if sizes else None
    out["d3({4, 11, 13})"] = d3((4, 11, 13))
    out["d3({4, 11, 14})"] = d3((4, 11, 14))
    vals = {T: d3(T) for T in itertools.combinations(range(n), 3)}
    changed = sum(1 for T, v in vals.items() if vals[tuple(sorted(sw(b) for b in T))] != v)
    out["ternary entries changed by (13 14)"] = changed
    return out


FIVE_HISTORY = (((0,), 3), ((1,), 3), ((0, 2), 3), ((1, 3), 2), ((2, 4), 2), ((3, 5), 2), ((0, 6), 2), ((5, 7), 2), ((2, 8), 2),
                ((1, 7, 9), 2), ((4, 8, 10), 2), ((3, 9, 11), 2))


def part_five():
    P = RR.Pres()
    legal_steps = True
    for parents, fresh in FIVE_HISTORY:
        legal_steps &= P.legal_parents(parents)
        P.add(parents, fresh)
    n = P.width()
    D, rows = RR.table(P)
    loose = sorted(b for b, js in P.owner.items() if len(js) == 1)
    bl = set(bonds_list(P))
    mask = sum(1 << b for b in loose)
    legal = P.legal_triples()
    within = [T for T in legal if T <= set(loose)]
    out = {"history legal": legal_steps, "width": n, "junctions": len(P.J), "loose distinctions": loose,
           "they form a bond": mask in bl, "their ten distances": sorted(int(D[x][y]) for x, y in itertools.combinations(loose, 2)),
           "legal triples among them": sorted(sorted(T) for T in within), "triples among them": 10, "all legal triples": len(legal)}
    aut, capped = RR.automorphisms(D)
    out["table automorphisms"] = len(aut)
    out["automorphisms moving a legal triple to a forbidden one"] = sum(1 for g in aut if {frozenset(g[x] for x in T) for T in legal} != legal)
    P.add((6, 10, 12), 2) if P.legal_parents((6, 10, 12)) else None
    out["next join (6, 10, 12) legal"] = len(P.J) == 14
    loose2 = sorted(b for b, js in P.owner.items() if len(js) == 1)
    out["after it: loose distinctions"] = len(loose2)
    out["after it: legal triples"] = len(P.legal_triples())
    return out


# ---------------- small widths ----------------

def incidence_graph(P):
    G = nx.Graph()
    for k, S in enumerate(P.J):
        G.add_node(("j", k), kind=0)
        for b in S:
            G.add_node(("b", b), kind=2)
            G.add_edge(("j", k), ("b", b))
    return G


def iso_key(P):
    G = incidence_graph(P)
    return nx.weisfeiler_lehman_graph_hash(G, node_attr="kind", iterations=4), G


def enumerate_presentations(wmax):
    """Every reachable presentation with width <= wmax, up to isomorphism of the incidence (junction-bit) graph. The seed is
    not marked: two histories giving isomorphic incidences are one presentation."""
    level = [RR.Pres()]
    allp = list(level)
    while level:
        nxt = {}
        for P in level:
            for par in P.moves():
                for f in (2, 3):
                    if P.width() + f > wmax:
                        continue
                    Q = RR.Pres(P.J)
                    Q.nb = P.nb
                    Q.add(par, f)
                    h, G = iso_key(Q)
                    bucket = nxt.setdefault(h, [])
                    if not any(nx.is_isomorphic(G, G2, node_match=lambda a, b: a["kind"] == b["kind"]) for _, G2 in bucket):
                        bucket.append((Q, G))
        level = [Q for b in nxt.values() for Q, _ in b]
        allp.extend(level)
    return allp


def table_invariant(D):
    n = len(D)
    Dl = D.tolist()
    sig = [tuple(sorted(Dl[i])) for i in range(n)]
    for _ in range(3):
        sig = [tuple(sorted((Dl[i][j], sig[j]) for j in range(n))) for i in range(n)]
    return tuple(sorted(sig))


def part_small(wmax=17):
    import time
    t0 = time.time()
    pres = enumerate_presentations(wmax)
    out = {"seconds to enumerate": None}
    counts = Counter()
    groups = defaultdict(list)
    stats = Counter()
    for P in pres:
        w = P.width()
        if w < 15:
            continue
        legal = P.legal_triples()
        counts[(w, len(P.J), "presentations")] += 1
        counts[(w, len(P.J), "with a legal triple")] += bool(legal)
        counts[(w, len(P.J), "legal triples")] += len(legal)
        D, rows = RR.table(P)
        aut, capped = RR.automorphisms(D, 100000)
        stats["automorphism searches capped"] += capped
        stats["automorphisms checked"] += len(aut)
        stats["automorphisms moving a legal triple to a forbidden one"] += sum(
            1 for g in aut if {frozenset(g[x] for x in T) for T in legal} != legal)
        groups[(w, table_invariant(D))].append(len(P.J))
    out["seconds to enumerate"] = round(time.time() - t0, 1)
    out["counts (width, junctions, what)"] = {f"{w} / {j} / {what}": v for (w, j, what), v in sorted(counts.items())}
    out["presentations per width"] = dict(Counter(w for (w, j, what) in counts.elements() if what == "presentations"))
    out["table classes per width (refinement invariant)"] = dict(Counter(w for (w, _) in groups))
    out["invariant classes holding two or more presentations"] = sum(1 for v in groups.values() if len(v) > 1)
    out["... i.e. pairs of distinct presentations that could have isometric tables"] = sum(len(v) * (len(v) - 1) // 2 for v in groups.values())
    out["checks"] = dict(stats)
    return out


def shore(rows, w):
    """The set U of junctions whose equations sum to w (unique: the equations are independent), or None."""
    basis = {}
    for k, r in enumerate(rows):
        c = 1 << k
        while r:
            p = r.bit_length() - 1
            if p not in basis:
                basis[p] = (r, c)
                break
            r ^= basis[p][0]
            c ^= basis[p][1]
    c = 0
    while w:
        p = w.bit_length() - 1
        if p not in basis:
            return None
        w ^= basis[p][0]
        c ^= basis[p][1]
    return [k for k in range(len(rows)) if (c >> k) & 1]


def frontier_one(seed):
    import random as _r
    rng = _r.Random(f"referee-e-frontier-{seed}")
    # grow towards few loose distinctions (joins preferred, two fresh), stopping when exactly four remain or at width 30
    P = RR.Pres()
    while True:
        loose_now = sum(1 for b, js in P.owner.items() if len(js) == 1)
        if (loose_now == 4 and len(P.J) >= 4) or P.width() >= 30:
            break
        mv = P.moves()
        if not mv:
            break
        by = {k: [m for m in mv if len(m) == k] for k in (1, 2, 3)}
        ks = [k for k in (1, 2, 3) if by[k]]
        k = rng.choices(ks, weights=[(1, 4, 12)[k - 1] for k in ks])[0]
        P.add(rng.choice(by[k]), 2 if rng.random() < 0.85 else 3)
    if len(P.J) > 14:
        return {"skipped": 1}
    rows = [sum(1 << b for b in S) for S in P.J]
    r = Counter(presentations=1)
    big = []
    for w in bonds_list(P):
        if bin(w).count("1") == 4:
            U = shore(rows, w)
            r["four-bit bonds"] += 1
            if U is not None and len(U) >= 3:
                r["... with a shore of three or more junctions"] += 1
                big.append({b for b in range(P.width()) if (w >> b) & 1})
    if not big:
        return dict(r)
    F = set().union(*big)
    for T in P.legal_triples():
        r["legal triples using a distinction of such a bond (now)"] += bool(T & F)
    # continuations: up to six random joins, then the same test on the distinctions of F still loose
    for c in range(4):
        Q = RR.Pres(P.J)
        Q.nb = P.nb
        for _ in range(rng.randint(1, 6)):
            mv = Q.moves()
            if not mv:
                break
            by = {k: [m for m in mv if len(m) == k] for k in (1, 2, 3)}
            ks = [k for k in (1, 2, 3) if by[k]]
            k = rng.choices(ks, weights=[(1, 3, 6)[k - 1] for k in ks])[0]
            Q.add(rng.choice(by[k]), rng.choice((2, 3)))
        r["continuations"] += 1
        for T in Q.legal_triples():
            r["legal triples using a distinction of such a bond (continuation)"] += bool(T & F)
    return dict(r)


def frontier14_one(seed):
    """A random continuation (one to eight joins, biased to joins) of the study's fourteen-junction presentation with the
    four-distinction frontier {27, 29, 30, 31} (the five-frontier history and the join (6, 10, 12))."""
    import random as _r
    rng = _r.Random(f"referee-e-frontier14-{seed}")
    P = RR.Pres()
    for parents, fresh in FIVE_HISTORY + (((6, 10, 12), 2),):
        P.add(parents, fresh)
    F = {b for b, js in P.owner.items() if len(js) == 1}
    steps = 1 + seed % 8
    for _ in range(steps):
        mv = P.moves()
        if not mv:
            break
        by = {k: [m for m in mv if len(m) == k] for k in (1, 2, 3)}
        ks = [k for k in (1, 2, 3) if by[k]]
        k = rng.choices(ks, weights=[(2, 3, 5)[k - 1] for k in ks])[0]
        P.add(rng.choice(by[k]), rng.choice((2, 3)))
    legal = P.legal_triples()
    return {"continuations": 1, f"continuations of {steps} joins": 1, "legal triples": len(legal),
            "legal triples using a frontier distinction": sum(1 for T in legal if T & F),
            "continuations of at most four joins with a legal triple": int(steps <= 4 and bool(legal)),
            "continuations with a legal triple": int(bool(legal))}


def part_frontier14(n=4000, workers=16):
    from multiprocessing import Pool
    acc = Counter()
    with Pool(workers) as Pl:
        for r in Pl.imap_unordered(frontier14_one, range(n), chunksize=16):
            acc.update(r)
    P = RR.Pres()
    for parents, fresh in FIVE_HISTORY + (((6, 10, 12), 2),):
        P.add(parents, fresh)
    rows = [sum(1 << b for b in S) for S in P.J]
    F = sorted(b for b, js in P.owner.items() if len(js) == 1)
    w = sum(1 << b for b in F)
    out = {"frontier": F, "frontier is a bond": w in set(bonds_list(P)), "its shore (junctions)": len(shore(rows, w) or [])}
    out.update(dict(sorted(acc.items())))
    return out


def part_frontier(n=4000, workers=16):
    from multiprocessing import Pool
    acc = Counter()
    with Pool(workers) as Pl:
        for r in Pl.imap_unordered(frontier_one, range(n), chunksize=8):
            acc.update(r)
    return dict(sorted(acc.items()))


if __name__ == "__main__":
    part = sys.argv[1]
    if part == "small" and len(sys.argv) > 2:
        print(json.dumps(part_small(int(sys.argv[2])), indent=1, default=str))
    else:
        print(json.dumps({"w32": part_w32, "five": part_five, "small": part_small, "frontier": part_frontier, "frontier14": part_frontier14}[part](), indent=1,
                         default=str))
