"""Referee R1 for VARIABLE-OUTPUT-READER-20261118-001F (own code; none of the study's C++ or Python is run or imported; the 311
hard cases are read from residual_cases.jsonl as data). Also the shared machinery for the referee's 001G and 001H checks.

  ../../../.venv/bin/python -B referee_f.py <part> [args] > referee_f_<part>.json      (from this directory)

The serial law (as 001D to 001H state it): a seed junction on three distinctions; each later junction takes one loose distinction
from each of one, two or three distinct junctions and makes two or three fresh ones; two parents need a common ordinary neighbour,
three parents pairwise so and no ordinary neighbour common to all three.  Sharing is simple (two junctions share at most one
distinction), so a presentation is its site graph with a loose count per site.

Bonds: a cut of the wired graph (sites plus one exterior vertex joined to every loose distinction) is a bond exactly when both of
its sides are connected; K(x, y) is the least bond size through x and y (D = K - 1).  The referee enumerates every set of sites as a
shore, which is independent of the GF(2) word filter used in its 001D/001E code.

Table symmetries: distinctions x, y are twins when D(x, z) = D(y, z) for every other z.  Twins form classes; every symmetry of a
table is a lift of a symmetry of the quotient (classes with sizes, internal entry and the entries between classes) composed with
permutations inside classes, so the adjacent transpositions inside classes and one lift of every quotient symmetry generate the
whole group.  This is an exact method, not a sample.

Parts:
  census W      every reachable presentation to width W (site graphs up to isomorphism, Weisfeiler-Lehman hash plus VF2), and at
                widths 20..W: counts by junction number, legal triples, whether two distinct presentations have isometric full
                tables, and whether every table symmetry keeps the legal triples (exact, by the twin quotient).
  hard          the 311 hard cases: a legal history found by search, the full table, the exact symmetry group's action on the
                legal triples (every symmetry keeps the menu?) and the number of orbits of legal triples.
  w18           001A's width-18 witness: both histories, their allowed states, tables and menus.
"""
import itertools
import json
import sys
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

import networkx as nx
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
INF = 99

# ---------------------------------------------------------------- site graphs


def seed():
    return (1, (0,), (3,))


def nbr(T, i):
    return T[1][i]


def legal_sites(T, P):
    n, adj, loose = T
    if len(set(P)) != len(P) or any(loose[i] == 0 for i in P):
        return False
    if len(P) == 1:
        return True
    if any(not (adj[a] & adj[b]) for a, b in itertools.combinations(P, 2)):
        return False
    return len(P) == 2 or not (adj[P[0]] & adj[P[1]] & adj[P[2]])


def moves(T):
    live = [i for i in range(T[0]) if T[2][i]]
    return [P for r in (1, 2, 3) for P in itertools.combinations(live, r) if legal_sites(T, P)]


def add(T, P, fresh):
    n, adj, loose = T
    adj = list(adj) + [sum(1 << p for p in P)]
    loose = list(loose) + [fresh]
    for p in P:
        adj[p] |= 1 << n
        loose[p] -= 1
    return (n + 1, tuple(adj), tuple(loose))


def width(T):
    n, adj, loose = T
    return sum(bin(a).count("1") for a in adj) // 2 + sum(loose)


def graph(T):
    G = nx.Graph()
    for i in range(T[0]):
        G.add_node(i, L=T[2][i])
    for i in range(T[0]):
        for j in range(i + 1, T[0]):
            if T[1][i] >> j & 1:
                G.add_edge(i, j)
    return G


def wl(T):
    return nx.weisfeiler_lehman_graph_hash(graph(T), node_attr="L", iterations=4)


def nm(a, b):
    return a["L"] == b["L"]


def supports(T):
    """Junction supports on distinction names: shared distinctions first (by site pair), then loose ones by site."""
    n, adj, loose = T
    S = [[] for _ in range(n)]
    b = 0
    for i in range(n):
        for j in range(i + 1, n):
            if adj[i] >> j & 1:
                S[i].append(b)
                S[j].append(b)
                b += 1
    for i in range(n):
        for _ in range(loose[i]):
            S[i].append(b)
            b += 1
    return S, b


def from_supports(J):
    """Site graph from junction supports (the bits must be shared by at most two)."""
    n = len(J)
    owner = defaultdict(list)
    for k, S in enumerate(J):
        for x in S:
            owner[x].append(k)
    adj = [0] * n
    loose = [0] * n
    for x, ks in owner.items():
        if len(ks) == 2:
            adj[ks[0]] |= 1 << ks[1]
            adj[ks[1]] |= 1 << ks[0]
        else:
            loose[ks[0]] += 1
    return (n, tuple(adj), tuple(loose))


# ---------------------------------------------------------------- bonds and the table


def bond_table(J, nbits):
    """K matrix (least bond size through each pair; INF where none) from junction supports J, by enumerating shores."""
    n = len(J)
    owner = defaultdict(list)
    for k, S in enumerate(J):
        for x in S:
            owner[x].append(k)
    star = [sum(1 << x for x in S) for S in J]
    adj = [0] * n
    haslo = 0
    for x, ks in owner.items():
        if len(ks) == 2:
            adj[ks[0]] |= 1 << ks[1]
            adj[ks[1]] |= 1 << ks[0]
        else:
            haslo |= 1 << ks[0]
    full = (1 << n) - 1

    def connected(U):
        if not U:
            return True
        comp = U & -U
        while True:
            new = comp
            m = comp
            while m:
                low = m & -m
                new |= adj[low.bit_length() - 1] & U
                m ^= low
            if new == comp:
                return comp == U
            comp = new

    def outside_ok(U):
        O = full & ~U
        # every component of the outside sites must reach the exterior: grow from the sites holding loose bits
        comp = O & haslo
        while True:
            new = comp
            m = comp
            while m:
                low = m & -m
                new |= adj[low.bit_length() - 1] & O
                m ^= low
            if new == comp:
                return comp == O
            comp = new
    K = np.full((nbits, nbits), INF, dtype=np.int64)
    np.fill_diagonal(K, 0)
    bonds = 0
    word = [0] * (1 << n)
    for U in range(1, 1 << n):
        low = U & -U
        word[U] = word[U ^ low] ^ star[low.bit_length() - 1]
        if not connected(U) or not outside_ok(U):
            continue
        bonds += 1
        w = word[U]
        idx = [x for x in range(nbits) if w >> x & 1]
        s = len(idx)
        sub = K[np.ix_(idx, idx)]
        np.minimum(sub, s, out=sub)
        K[np.ix_(idx, idx)] = sub
    np.fill_diagonal(K, 0)
    return K, bonds


def clip(K, L):
    """Exact K through L, and L + 1 for every larger value."""
    C = K.copy()
    C[C > L] = L + 1
    return C


# ---------------------------------------------------------------- symmetries by the twin quotient


def refine(K, rounds=3):
    n = len(K)
    Kl = K.tolist()
    col = [hash(tuple(sorted(Kl[i]))) for i in range(n)]
    for _ in range(rounds):
        col = [hash((col[i], tuple(sorted((Kl[i][j], col[j]) for j in range(n) if j != i)))) for i in range(n)]
    return col


def invariant(K):
    return hash(tuple(sorted(refine(K))))


def invariant_marked(K, marked):
    return hash(tuple(sorted(refine_marked(K, marked))))


def twin_classes(K):
    n = len(K)
    Kl = K.tolist()
    rows = defaultdict(list)
    for i in range(n):
        rows[tuple(sorted(Kl[i]))].append(i)
    cls = []
    seen = set()
    for grp in rows.values():
        for i in grp:
            if i in seen:
                continue
            c = [i]
            seen.add(i)
            for j in grp:
                if j not in seen and all(Kl[i][z] == Kl[j][z] for z in range(n) if z != i and z != j):
                    c.append(j)
                    seen.add(j)
            cls.append(sorted(c))
    return sorted(cls)


def quotient(K, marked=frozenset()):
    """Twin classes (split by membership of `marked`, so that a marked isometry maps marked to marked), the quotient table and
    each class's attributes."""
    cls = [sorted(g) for c in twin_classes(K) for g in (set(c) & marked, set(c) - marked) if g]
    cls.sort()
    col = refine(K) if not marked else refine_marked(K, marked)
    Kl = K.tolist()
    m = len(cls)
    Q = [[Kl[cls[a][0]][cls[b][0]] for b in range(m)] for a in range(m)]
    attr = [(len(c), Kl[c[0]][c[1]] if len(c) > 1 else -1, col[c[0]], c[0] in marked) for c in cls]
    return cls, Q, attr


def refine_marked(K, marked, rounds=3):
    n = len(K)
    Kl = K.tolist()
    col = [hash((tuple(sorted(Kl[i])), i in marked)) for i in range(n)]
    for _ in range(rounds):
        col = [hash((col[i], tuple(sorted((Kl[i][j], col[j]) for j in range(n) if j != i)))) for i in range(n)]
    return col


def quotient_maps(q1, q2, first_only=False, cap=200000):
    """Isometries between the two quotients (lists of class images)."""
    cls1, Q1, a1 = q1
    cls2, Q2, a2 = q2
    m = len(cls1)
    if m != len(cls2) or sorted(a1) != sorted(a2):
        return []
    by = defaultdict(list)
    for k in range(m):
        by[a2[k]].append(k)
    order = sorted(range(m), key=lambda i: (len(by[a1[i]]), i))
    out = []

    def go(img, used):
        if len(out) >= cap or (first_only and out):
            return
        k = len(img)
        if k == m:
            g = [0] * m
            for a, b in zip(order, img):
                g[a] = b
            out.append(g)
            return
        a = order[k]
        for t in by[a1[a]]:
            if t in used:
                continue
            if all(Q1[a][order[j]] == Q2[t][img[j]] for j in range(k)):
                used.add(t)
                go(img + [t], used)
                used.discard(t)
    go([], set())
    return out


def lift(q1, q2, g):
    cls1, cls2 = q1[0], q2[0]
    n = sum(len(c) for c in cls1)
    p = [0] * n
    for a, b in enumerate(g):
        for x, y in zip(cls1[a], cls2[b]):
            p[x] = y
    return p


def generators(K, cap=200000):
    """Generators of the table's symmetry group: adjacent transpositions inside twin classes and every quotient symmetry's lift."""
    q = quotient(K)
    n = len(K)
    gens = []
    for c in q[0]:
        for x, y in zip(c, c[1:]):
            p = list(range(n))
            p[x], p[y] = y, x
            gens.append(p)
    qs = quotient_maps(q, q, cap=cap)
    for g in qs:
        if g != list(range(len(g))):
            gens.append(lift(q, q, g))
    return gens, len(qs), len(qs) >= cap, q


def isometric(K1, K2, marked=frozenset()):
    """One isometry K1 -> K2 if any (exact); with `marked`, one carrying the marked set onto itself."""
    q1, q2 = quotient(K1, marked), quotient(K2, marked)
    g = quotient_maps(q1, q2, first_only=True)
    return lift(q1, q2, g[0]) if g else None


# ---------------------------------------------------------------- menus


def legal_triples(T, J=None):
    """Unordered triples of loose distinctions at three distinct junctions that could be the parents of a join."""
    if J is None:
        J, _ = supports(T)
    owner = defaultdict(list)
    for k, S in enumerate(J):
        for x in S:
            owner[x].append(k)
    loose = defaultdict(list)
    for x, ks in owner.items():
        if len(ks) == 1:
            loose[ks[0]].append(x)
    out = set()
    for P in itertools.combinations(sorted(loose), 3):
        if legal_sites(T, P):
            for t in itertools.product(*(loose[p] for p in P)):
                out.add(frozenset(t))
    return out


def legal_menu(T, J, r):
    owner = defaultdict(list)
    for k, S in enumerate(J):
        for x in S:
            owner[x].append(k)
    loose = defaultdict(list)
    for x, ks in owner.items():
        if len(ks) == 1:
            loose[ks[0]].append(x)
    out = set()
    for P in itertools.combinations(sorted(loose), r):
        if legal_sites(T, P):
            for t in itertools.product(*(loose[p] for p in P)):
                out.add(frozenset(t))
    return out


def keeps(gens, family):
    return all({frozenset(p[x] for x in s) for s in family} == family for p in gens)


def orbits(gens, family):
    fam = list(family)
    idx = {s: i for i, s in enumerate(fam)}
    parent = list(range(len(fam)))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for p in gens:
        for s in fam:
            t = frozenset(p[x] for x in s)
            if t in idx:
                parent[find(idx[s])] = find(idx[t])
    return len({find(i) for i in range(len(fam))})


# ---------------------------------------------------------------- the census


def _children(args):
    T, w, shard, shards = args
    out = []
    for P in moves(T):
        f = w - width(T)
        if f in (2, 3):
            C = add(T, P, f)
            h = wl(C)
            if int(h[:8], 16) % shards == shard:
                out.append((h, C))
    return out


def _dedup(bucket):
    reps = []
    for C in bucket:
        G = graph(C)
        if not any(nx.is_isomorphic(G, H, node_match=nm) for H, _ in reps):
            reps.append((G, C))
    return [C for _, C in reps]


def census(wmax, workers=20):
    levels = {3: [seed()]}
    with Pool(workers) as pool:
        for w in range(4, wmax + 1):
            parents = levels.get(w - 2, []) + levels.get(w - 3, [])
            shards = 1 + len(parents) // 150000      # bound the memory held by one pass
            reps = []
            for shard in range(shards):
                buckets = defaultdict(list)
                for res in pool.imap_unordered(_children, [(T, w, shard, shards) for T in parents], chunksize=64):
                    for h, C in res:
                        buckets[h].append(C)
                for r in pool.imap_unordered(_dedup, list(buckets.values()), chunksize=16):
                    reps.extend(r)
                del buckets
            levels[w] = reps
            print(f"width {w}: {len(reps)}", file=sys.stderr, flush=True)
    return levels


def _examine(T):
    J, nb = supports(T)
    K, _ = bond_table(J, nb)
    legal = legal_triples(T, J)
    gens, nq, capped, q = generators(K)
    return {"T": T, "j": T[0], "legal": len(legal), "keeps": keeps(gens, legal) if legal else True, "capped": capped,
            "quotient symmetries": nq, "inv": invariant(K)}


def _cross(group):
    """Exact isometry test between distinct presentations sharing an invariant."""
    tabs = []
    for T in group:
        J, nb = supports(T)
        tabs.append(bond_table(J, nb)[0])
    hits = 0
    for a, b in itertools.combinations(range(len(tabs)), 2):
        if isometric(tabs[a], tabs[b]) is not None:
            hits += 1
    return hits


def part_census(wmax=21, from_w=20):
    import time
    t0 = time.time()
    levels = census(wmax)
    out = {"presentations per width": {w: len(v) for w, v in sorted(levels.items())}, "seconds to enumerate": round(time.time() - t0)}
    with Pool(20) as pool:
        for w in range(from_w, wmax + 1):
            rows = pool.map(_examine, levels[w], chunksize=32)
            byj = Counter()
            for r in rows:
                byj[(r["j"], "types")] += 1
                byj[(r["j"], "with a legal triple")] += r["legal"] > 0
            inv = defaultdict(list)
            for r in rows:
                inv[r["inv"]].append(r["T"])
            coll = [g for g in inv.values() if len(g) > 1]
            cross = sum(pool.map(_cross, coll)) if coll else 0
            out[f"width {w}"] = {
                "presentations": len(rows),
                "by junction count": {f"{j} junctions: {what}": v for (j, what), v in sorted(byj.items())},
                "with a legal triple": sum(r["legal"] > 0 for r in rows),
                "legal triple occurrences": sum(r["legal"] for r in rows),
                "invariant classes holding two or more presentations": len(coll),
                "pairs of distinct presentations with isometric full tables (exact)": cross,
                "presentations with a legal triple whose table has a symmetry moving it to a forbidden one": sum(1 for r in rows if not r["keeps"]),
                "symmetry searches capped": sum(r["capped"] for r in rows),
                "presentations with a nontrivial quotient symmetry": sum(r["quotient symmetries"] > 1 for r in rows),
                "seconds so far": round(time.time() - t0)}
            print(json.dumps(out[f"width {w}"]), file=sys.stderr, flush=True)
    return out


# ---------------------------------------------------------------- the hard cases


def parse_source(line):
    v = list(map(int, line.split()))
    j = v[0]
    return (j, tuple(v[1:1 + j]), tuple(v[1 + j:1 + 2 * j]))


def find_history(T):
    """A legal birth order (seed, then each site's earlier neighbours its parents) with fresh counts 2 or 3, or None."""
    n, adj, loose = T
    deg = [bin(a).count("1") for a in adj]
    arity = [deg[i] + loose[i] for i in range(n)]
    failed = set()

    def go(order, placed, nparents):
        if len(order) == n:
            return list(order)
        key = (placed, tuple(sorted(nparents.items())))
        if key in failed:
            return None
        for i in range(n):
            if placed >> i & 1:
                continue
            P = [p for p in range(n) if placed >> p & 1 and adj[i] >> p & 1]
            if not 1 <= len(P) <= 3:
                continue
            f = arity[i] - len(P)
            if f not in (2, 3):
                continue
            # each parent still has an unused output
            ok = all((bin(adj[p] & placed).count("1") - nparents[p]) < arity[p] - nparents[p] for p in P)
            if not ok:
                continue
            A = [adj[p] & placed for p in P]
            if any(not (A[a] & A[b]) for a, b in itertools.combinations(range(len(P)), 2)):
                continue
            if len(P) == 3 and (A[0] & A[1] & A[2]):
                continue
            nparents[i] = len(P)
            r = go(order + [i], placed | 1 << i, nparents)
            del nparents[i]
            if r:
                return r
        failed.add(key)
        return None
    for s in range(n):
        if arity[s] == 3:
            r = go([s], 1 << s, {s: 0})
            if r:
                return r
    return None


def part_hard():
    path = ROOT / "proofs/VARIABLE-OUTPUT-READER-20261118-001F/VARIABLE-OUTPUT-READER-20261118-001F-P001_finite_interval/residual_cases.jsonl"
    rows = [json.loads(l) for l in open(path)]
    with Pool(20) as pool:
        res = pool.map(_hard_one, rows)
    by_w = Counter(r["width"] for r in res)
    return {"cases": len(res), "by width": dict(sorted(by_w.items())),
            "legal history found": sum(r["history"] for r in res),
            "width as stated": sum(r["width ok"] for r in res),
            "legal-triple counts as stated": sum(r["legal ok"] for r in res),
            "every table symmetry keeps the legal triples": sum(r["keeps"] for r in res),
            "symmetry searches capped": sum(r["capped"] for r in res),
            "orbits of legal triples (sum over cases)": sum(r["orbits"] for r in res),
            "legal triples (sum)": sum(r["legal"] for r in res),
            "nonidentity quotient symmetries (sum)": sum(r["quotient symmetries"] - 1 for r in res),
            "per case": res}


def _hard_one(row):
    T = parse_source(row["source"])
    J, nb = supports(T)
    hist = find_history(T)
    K, nbonds = bond_table(J, nb)
    legal = legal_triples(T, J)
    gens, nq, capped, q = generators(K)
    return {"line": row["line"], "width": nb, "width ok": nb == row["width"], "history": hist is not None,
            "legal": len(legal), "legal ok": len(legal) == row["legal_triples"], "keeps": keeps(gens, legal),
            "capped": capped, "orbits": orbits(gens, legal), "quotient symmetries": nq,
            "twin classes of size > 1": sum(1 for c in q[0] if len(c) > 1)}


# ---------------------------------------------------------------- 001A's width-18 witness


def part_w18():
    path = ROOT / "proofs/VARIABLE-OUTPUT-READER-20261118-001A/VARIABLE-OUTPUT-READER-20261118-001A-P001_width_eighteen/witness.json"
    w = json.load(open(path))
    prefix = [h for h in w["history"] if h["junction"] < 7]
    first = w["relation_preserving_witness"]["first_eighth_junction"]
    alt = w["relation_preserving_witness"]["alternate_eighth_junction"]
    out = {}
    sides = {}
    for name, last in (("first", first), ("alternate", alt)):
        J = [sorted(prefix[0]["fresh"])]
        legal_steps = True
        for h in prefix[1:] + [last]:
            T = from_supports(J)
            owner = defaultdict(list)
            for k, S in enumerate(J):
                for x in S:
                    owner[x].append(k)
            P = tuple(sorted(owner[x][0] for x in h["consumed"]))
            legal_steps &= all(len(owner[x]) == 1 for x in h["consumed"]) and legal_sites(T, P) and len(h["fresh"]) in (2, 3)
            J = J + [sorted(h["consumed"] + h["fresh"])]
        T = from_supports(J)
        K, nbonds = bond_table(J, 18)
        rows = [sum(1 << x for x in S) for S in J]
        sides[name] = (T, J, K, rows)
        out[name] = {"history legal": legal_steps, "eighth junction": sorted(last["consumed"] + last["fresh"]), "bonds": nbonds,
                     "one-parent choices (loose distinctions)": sorted(sorted(s) for s in legal_menu(T, J, 1)),
                     "two-parent choices": sorted(sorted(s) for s in legal_menu(T, J, 2)),
                     "three-parent choices": sorted(sorted(s) for s in legal_menu(T, J, 3))}

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

    def same_span(r1, r2):
        b1 = span(r1)
        for r in r2:
            x = r
            while x:
                p = x.bit_length() - 1
                if p not in b1:
                    return False
                x ^= b1[p]
        return len(span(r2)) == len(b1)
    out["allowed states identical on the same names (same parity-check space)"] = same_span(sides["first"][3], sides["alternate"][3])
    out["rank"] = len(span(sides["first"][3]))
    out["allowed rows"] = 2 ** (18 - out["rank"])
    out["full tables identical on the same names"] = bool((sides["first"][2] == sides["alternate"][2]).all())
    out["one-parent choices differ"] = out["first"]["one-parent choices (loose distinctions)"] != out["alternate"]["one-parent choices (loose distinctions)"]
    out["two-parent choices differ"] = out["first"]["two-parent choices"] != out["alternate"]["two-parent choices"]
    out["presentations isomorphic as incidence types"] = nx.is_isomorphic(graph(sides["first"][0]), graph(sides["alternate"][0]), node_match=nm)
    return out


if __name__ == "__main__":
    part = sys.argv[1]
    args = [int(a) for a in sys.argv[2:]]
    f = {"census": part_census, "hard": part_hard, "w18": part_w18}[part]
    print(json.dumps(f(*args), indent=1, default=str))
