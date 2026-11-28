"""cellsign.py: cross pairs and the closing sign (CELL-SIGN-20261127-001; README.md, frozen predictions G, P1-P3).

A commuting choice is a set of failing pairs (x, y) of unheld values, every two knots' checks commuting. A cross pair of
(x, y) is a pair of knots, one holding x and one holding y; the four make its cycle a, c, b, d (x held by a, b; y by c,
d). Item 1 of the README: with any cyclic order of each cycle and any reference order of each pair of knots, the closing
sign is the number L of (failing pair, cross pair) listings in the reference order, mod 2. This script checks it on every
choice of the populations and measures the structure: coverage exactly two, the cycles at each knot and the separated
Euler count, orientability, the weaker GF(2) condition of 2(a), two-colourable cross pairs, and the Euler count.
    cellsign.py [--limit N] [--enum 14] [--out DIR]
Writes results.jsonl, census_types.jsonl, fixtures.json, gates.json and summary.json next to this file.
"""
import argparse
import collections
import json
import random
import resource
import sys
import time
from pathlib import Path

import networkx as nx
from pysat.card import CardEnc, EncType
from pysat.solvers import Solver

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ER = ROOT / "research" / "ENCODED-READERS-20261127-001"
RS = ROOT / "research" / "READER-SPLIT-20261127-001"
sys.path.insert(0, str(ER))
sys.path.insert(0, str(RS))
import decode as D  # noqa: E402  (minimal, pattern_from_pairs, NINE)
import readers as R  # noqa: E402  (Code, program, nullspace, is_strict, closed, from_ends, population, Cnf, Unsettled)

lc, forbid = R.lc, R.forbid
SIZE_CAP = 2000
FEWEST_CAP = 1000
MAX_PAIRS = 8
CONFLICTS = 2_000_000          # per satisfiability call; exhausted counts as unsettled
SEARCH_NODES = 2_000_000       # per exact orientability search


class Unsettled(Exception):
    pass


# ---------------------------------------------------------------- the cycles of a choice

def cycles_of(holders, F):
    """for each failing pair (x, y): its cycle (a, c, b, d), x held by a, b and y by c, d"""
    out = []
    for x, y in F:
        a, b = holders[x]
        c, d = holders[y]
        out.append((a, c, b, d))
    return out


def steps(cyc):
    return [(cyc[i], cyc[(i + 1) % 4]) for i in range(4)]


def reverse(cyc):
    return (cyc[0], cyc[3], cyc[2], cyc[1])


def commute_and_sign(holders, F):
    """every pair of knots a cross pair of an even number of failing pairs; the interleaving cost in index order"""
    cover = collections.Counter()
    sign = 0
    for x, y in F:
        assert not set(holders[x]) & set(holders[y]), "a failing pair of held values"
        for u in holders[x]:
            for v in holders[y]:
                cover[frozenset((u, v))] ^= 1
        x1, x2 = sorted(holders[x])
        y1, y2 = sorted(holders[y])
        sign ^= int(x1 < y1 < x2 < y2 or y1 < x1 < y2 < x2)
    return not any(cover.values()), sign


def order_count(cycles, rng):
    """random cyclic orders and reference orders; sum of L(s) mod 2"""
    ref = {}
    total = 0
    for cyc in cycles:
        c = cyc if rng.random() < 0.5 else reverse(cyc)
        for u, v in steps(c):
            key = frozenset((u, v))
            if key not in ref:
                ref[key] = (u, v) if rng.random() < 0.5 else (v, u)
            total += ref[key] == (u, v)
    return total % 2


def orientable(cycles, m):
    """cyclic orders listing every pair of knots equally often each way: propagation where every cross pair is in two
    failing pairs, otherwise an exact search with a node budget"""
    n = len(cycles)
    at = collections.defaultdict(list)
    for i, c in enumerate(cycles):
        for u, v in steps(c):
            at[frozenset((u, v))].append((i, (u, v)))
    if all(k == 2 for k in m.values()):
        flip = [None] * n
        for s0 in range(n):
            if flip[s0] is not None:
                continue
            flip[s0] = 0
            stack = [s0]
            while stack:
                i = stack.pop()
                for u, v in steps(cycles[i]):
                    for j, (p, q) in at[frozenset((u, v))]:
                        if j == i:
                            continue
                        # listed (u, v) by i (as flipped by flip[i]); j lists (p, q) as flipped by flip[j]; need opposite
                        same_base = (p, q) == (u, v)
                        want = flip[i] ^ (0 if not same_base else 1)
                        if flip[j] is None:
                            flip[j] = want
                            stack.append(j)
                        elif flip[j] != want:
                            return False
        return True
    need = {e: k // 2 for e, k in m.items()}
    fwd = collections.Counter()
    left = collections.Counter(m)
    order = sorted(range(n), key=lambda i: -sum(m[frozenset(p)] for p in steps(cycles[i])))
    nodes = [0]

    def place(t):
        nodes[0] += 1
        if nodes[0] > SEARCH_NODES:
            raise Unsettled("orientability search budget")
        if t == n:
            return all(fwd[e] == need[e] for e in m)
        i = order[t]
        for c in (cycles[i], reverse(cycles[i])):
            changed = []
            good = True
            for u, v in steps(c):
                e = frozenset((u, v))
                left[e] -= 1
                f = u < v
                if f:
                    fwd[e] += 1
                changed.append((e, f))
                if fwd[e] > need[e] or fwd[e] + left[e] < need[e]:
                    good = False
            if good and place(t + 1):
                return True
            for e, f in changed:
                left[e] += 1
                if f:
                    fwd[e] -= 1
        return False
    return place(0)


def weak_even(cycles, m):
    """2(a)'s weaker condition: flips o_i with sum over i at s of (base listing ^ o_i) = m(s)/2 mod 2, over GF(2)"""
    rows = []
    for e, k in m.items():
        row, rhs = 0, (k // 2) % 2
        for i, c in enumerate(cycles):
            for u, v in steps(c):
                if frozenset((u, v)) == e:
                    row ^= 1 << i
                    rhs ^= int(u < v)
        rows.append((row, rhs))
    piv = {}
    for r, b in rows:
        while r:
            h = r.bit_length() - 1
            if h in piv:
                r ^= piv[h][0]
                b ^= piv[h][1]
            else:
                piv[h] = (r, b)
                break
        else:
            if b:
                return False
    return True


def separate(cycles):
    """split every knot whose failing pairs form several cycles into one knot per cycle; returns new cycles"""
    knots = {u for c in cycles for u in c}
    new = [list(c) for c in cycles]
    nxt = max(knots) + 1
    for v in sorted(knots):
        L = nx.MultiGraph()
        idx = []
        for i, c in enumerate(cycles):
            if v in c:
                j = c.index(v)
                L.add_edge(c[(j - 1) % 4], c[(j + 1) % 4], key=i)
                idx.append(i)
        comps = list(nx.connected_components(L))
        if len(comps) <= 1:
            continue
        for comp in comps[1:]:
            label = nxt
            nxt += 1
            for a, b, i in L.edges(keys=True):
                if a in comp:
                    j = cycles[i].index(v)
                    new[i][j] = label
    return [tuple(c) for c in new]


def structure(cycles):
    m = collections.Counter(frozenset(p) for c in cycles for p in steps(c))
    knots = {u for c in cycles for u in c}
    one = True
    for v in knots:
        L = nx.MultiGraph()
        for c in cycles:
            if v in c:
                j = c.index(v)
                L.add_edge(c[(j - 1) % 4], c[(j + 1) % 4])
        one = one and nx.is_connected(L) and all(dg == 2 for _, dg in L.degree())
    G = nx.Graph()
    G.add_edges_from(tuple(e) for e in m)
    return m, len(knots) - len(m) + len(cycles), one, nx.is_bipartite(G)


def features(holders, F, rng1, rng2):
    cyc = cycles_of(holders, F)
    ok, sign = commute_and_sign(holders, F)
    if not ok:
        raise AssertionError("not a commuting choice")
    m, euler, one, twocol = structure(cyc)
    out = {"pairs": len(F), "sign": sign, "order count": order_count(cyc, rng1), "order count again": order_count(cyc, rng2),
           "exactly two": all(v == 2 for v in m.values()), "most at a cross pair": max(m.values()),
           "Euler count": euler, "one cycle at every knot": one, "two-colourable": twocol,
           "orientable": orientable(cyc, m), "weak even condition": weak_even(cyc, m)}
    if out["exactly two"]:
        at = collections.defaultdict(list)
        for c in cyc:
            for u, v in steps(c):
                at[frozenset((u, v))].append((u, v))
        out["same-order parity"] = sum(1 for e, ls in at.items() if ls[0] == ls[1]) % 2
        sep = separate(cyc)
        m2, e2, one2, twocol2 = structure(sep)
        out["separated Euler count"] = e2
        out["separated two-colourable"] = twocol2
        out["pinched knots"] = len({u for c in sep for u in c}) - len({u for c in cyc for u in c})
    return out


def theorem_ok(f):
    ok = f["order count"] == f["sign"] == f["order count again"]
    if f.get("same-order parity") is not None:
        ok = ok and f["same-order parity"] == f["sign"]
    return ok


def corollary_failure(f):
    """an orientable, weakly even or two-colourable choice that closes odd (would refute 2(a), 2(d))"""
    return f["sign"] == 1 and (f["orientable"] or f["weak even condition"] or f["two-colourable"])


# ---------------------------------------------------------------- listing with a sign

def listing(code, k, cap, parity):
    """every strict choice with exactly k failing pairs and the given closing sign, up to cap; (words, complete)"""
    cnf = R.Cnf(code.n)
    for r in code.H:
        cnf.xor([j + 1 for j in range(code.n) if (r >> j) & 1], 0)
    cnf.xor([j + 1 for j in range(code.n) if (code.cost >> j) & 1], parity)
    for d in range(code.D):
        lits = [j + 1 for j in code.at[d]]
        if len(lits) >= 2:
            enc = CardEnc.atmost(lits=lits, bound=1, top_id=cnf.top, encoding=EncType.seqcounter)
            cnf.top = max(cnf.top, enc.nv)
            cnf.clauses += enc.clauses
    if k > code.n:
        return [], True
    enc = CardEnc.equals(lits=list(range(1, code.n + 1)), bound=k, top_id=cnf.top, encoding=EncType.seqcounter)
    cnf.top = max(cnf.top, enc.nv)
    cnf.clauses += enc.clauses
    out = []
    with Solver(name="cadical153", bootstrap_with=cnf.clauses) as s:
        while len(out) < cap:
            s.conf_budget(CONFLICTS)
            ok = s.solve_limited()
            if ok is None:
                raise Unsettled(f"listing of {k} pairs, sign {parity}: conflict budget")
            if not ok:
                return out, True
            mm = set(v for v in s.get_model() if v > 0)
            word = sum(1 << j for j in range(code.n) if j + 1 in mm)
            out.append(word)
            s.add_clause([-(j + 1) for j in range(code.n) if (word >> j) & 1])
    return out, False


# ---------------------------------------------------------------- tallies

def new_tally():
    return {"choices": 0, "theorem holds": 0, "exactly two": 0, "one cycle at every knot": 0, "orientable": 0,
            "two-colourable": 0, "weak even condition": 0, "Euler counts": {}, "separated Euler counts": {},
            "most at a cross pair": {}}


def add(t, f):
    t["choices"] += 1
    t["theorem holds"] += theorem_ok(f)
    for k in ("exactly two", "one cycle at every knot", "orientable", "two-colourable", "weak even condition"):
        t[k] += bool(f[k])
    for k, src in (("Euler counts", "Euler count"), ("separated Euler counts", "separated Euler count"),
                   ("most at a cross pair", "most at a cross pair")):
        if src in f:
            t[k][str(f[src])] = t[k].get(str(f[src]), 0) + 1


def merge(a, b):
    for k, v in b.items():
        if isinstance(v, dict):
            for kk, vv in v.items():
                a[k][kk] = a[k].get(kk, 0) + vv
        else:
            a[k] += v


# ---------------------------------------------------------------- one closure or type

def study(code, enum_limit, seed, lists=True):
    st = code.st
    holders = {d: tuple(h) for d, h in st.holders.items()}
    rng1, rng2 = random.Random(seed), random.Random(seed + 1)
    row = {"tallies": {}, "corollary failures": 0, "theorem failures": 0, "P1 failures": [],
           "coverage four": {"fewest words": 0, "minimal non-fewest words": 0}}
    T = row["tallies"]

    def take(name, F):
        f = features(holders, F, rng1, rng2)
        add(T.setdefault(name, new_tally()), f)
        row["corollary failures"] += corollary_failure(f)
        row["theorem failures"] += not theorem_ok(f)
        return f
    try:
        fs = R.program(code, strict=True)
        row["strict"] = fs is not None
        if fs is not None and lists:
            row["fewest strict readers"] = fs[0]
            words, comp = listing(code, fs[0], FEWEST_CAP, 1)
            row["fewest listing complete"] = comp
            for w in words:
                f = take("fewest strict", code.failing(w))
                row["coverage four"]["fewest words"] += f["most at a cross pair"] >= 4
            capped = []
            for parity in (0, 1):
                name = "minimal strict odd" if parity else "minimal strict even"
                for k in range(2, MAX_PAIRS + 1):
                    ws, comp = listing(code, k, SIZE_CAP, parity)
                    if not comp:
                        capped.append((parity, k))
                    for w in ws:
                        F = code.failing(w)
                        if not D.minimal(holders, F):
                            continue
                        f = take(name, F)
                        if parity and k > fs[0]:
                            row["coverage four"]["minimal non-fewest words"] += f["most at a cross pair"] >= 4
                        if (parity and f["exactly two"] and f["separated Euler count"] not in (0, 1)
                                and len(row["P1 failures"]) < 3):
                            row["P1 failures"].append([list(map(list, (holders[a], holders[b]))) for a, b in F])
            row["sizes at the cap"] = capped
        if enum_limit is not None:
            dim = len(R.nullspace(code))
            row["free choices"] = dim
            if dim <= enum_limit:
                basis = R.nullspace(code)
                w = 0
                for i in range(1, 1 << len(basis)):
                    w ^= basis[(i & -i).bit_length() - 1]
                    F = code.failing(w)
                    strict = R.is_strict(code, w)
                    ok, sgn = commute_and_sign(holders, F)
                    name = "small code, " + ("strict" if strict else "not strict") + ", " + ("odd" if sgn else "even")
                    f = take(name, F)
                    if (f["sign"] and strict and f["exactly two"] and f["separated Euler count"] not in (0, 1)
                            and D.minimal(holders, F) and len(row["P1 failures"]) < 3):
                        row["P1 failures"].append([list(map(list, (holders[a], holders[b]))) for a, b in F])
    except (Unsettled, R.Unsettled) as e:
        row["unsettled"] = str(e)
    return row


# ---------------------------------------------------------------- constructed choices

def from_cycles(cells):
    holders, F = {}, []
    for a, c, b, d in cells:
        i = len(holders)
        holders[i], holders[i + 1] = tuple(sorted((a, b))), tuple(sorted((c, d)))
        F.append((i, i + 1))
    return holders, F


def torus(n, m):
    v = lambda i, j: (i % n) * m + (j % m)
    return [(v(i, j), v(i + 1, j), v(i + 1, j + 1), v(i, j + 1)) for i in range(n) for j in range(m)]


def klein(n, m):
    def v(i, j):
        if j == m:
            i, j = -i, 0
        return (i % n) * m + j
    return [(v(i, j), v(i + 1, j), v(i + 1, j + 1), v(i, j + 1)) for i in range(n) for j in range(m)]


def projective(N):
    parent = {}

    def find(p):
        while parent.setdefault(p, p) != p:
            p = parent[p]
        return p
    for i in range(N + 1):
        for p, q in (((i, 0), (N - i, N)), ((0, i), (N, N - i))):
            parent[find(p)] = find(q)
    ids = {}
    vid = lambda p: ids.setdefault(find(p), len(ids))
    return [(vid((i, j)), vid((i + 1, j)), vid((i + 1, j + 1)), vid((i, j + 1))) for i in range(N) for j in range(N)]


def cube_mod_antipodal(k):
    """the cube subdivided k x k on each face, modulo the antipodal map: the squares of three faces"""
    ids = {}

    def vid(p):
        q = tuple(k - c for c in p)
        return ids.setdefault(min(p, q), len(ids))
    cells = []
    for a in range(k):
        for b in range(k):
            cells.append((vid((0, a, b)), vid((0, a + 1, b)), vid((0, a + 1, b + 1)), vid((0, a, b + 1))))
            cells.append((vid((a, 0, b)), vid((a + 1, 0, b)), vid((a + 1, 0, b + 1)), vid((a, 0, b + 1))))
            cells.append((vid((a, b, 0)), vid((a + 1, b, 0)), vid((a + 1, b + 1, 0)), vid((a, b + 1, 0))))
    return cells


def ring_game(n):
    half = (n - 1) // 2
    return [((0, j), (((j + half - 1) % n) + 1, ((j + half) % n) + 1)) for j in range(1, n + 1)]


CUBE = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
GAMES = {
    "three-reader game": [((0, 1), (2, 3)), ((0, 2), (1, 3)), ((0, 3), (1, 2))],
    "ring game of five": ring_game(5),
    "grown six-pair game": [((0, 1), (4, 5)), ((0, 2), (1, 3)), ((0, 3), (2, 4)), ((0, 4), (3, 5)), ((1, 2), (0, 5)),
                            ((2, 4), (1, 5))],
    "census six-pair game": [((0, 1), (2, 3)), ((0, 4), (2, 6)), ((0, 5), (3, 6)), ((1, 4), (2, 5)), ((1, 6), (3, 5)),
                             ((3, 4), (5, 6))],
    "census eight-pair game": [((0, 1), (3, 4)), ((0, 2), (5, 6)), ((0, 3), (1, 5)), ((0, 4), (1, 6)), ((0, 5), (2, 4)),
                               ((0, 6), (2, 3)), ((3, 5), (4, 6)), ((3, 6), (4, 5))],
    "census ten-pair game": [((0, 1), (2, 6)), ((0, 2), (3, 6)), ((0, 3), (1, 5)), ((0, 5), (1, 2)), ((0, 6), (3, 5)),
                             ((1, 3), (4, 6)), ((1, 4), (2, 3)), ((1, 6), (4, 5)), ((2, 4), (5, 6)), ((2, 5), (3, 4))],
}
OTHER = {
    "start 4786 fourfold witness": [((0, 1), (2, 4)), ((0, 2), (1, 4)), ((0, 3), (1, 4)), ((0, 3), (2, 4)),
                                    ((1, 5), (3, 4)), ((2, 5), (3, 4))],
    "five-pair fourfold witness": [((0, 1), (2, 4)), ((0, 1), (3, 4)), ((0, 2), (1, 4)), ((0, 2), (3, 4)),
                                   ((0, 3), (1, 2))],
    "even seven-knot control": [((0, 1), (3, 4)), ((0, 1), (5, 6)), ((0, 2), (3, 5)), ((0, 2), (4, 6)),
                                ((1, 2), (3, 6)), ((1, 2), (4, 5))],
    "nine-knot choice": D.NINE,
    "ring game of seven": ring_game(7),
    "ring game of nine": ring_game(9),
}


def fixtures():
    out = {}
    rng1, rng2 = random.Random(5), random.Random(6)
    built = {"cube": CUBE}
    for n in (3, 4, 5):
        for m in (3, 4, 5):
            built[f"torus grid {n}x{m}"] = torus(n, m)
            built[f"Klein bottle grid {n}x{m}"] = klein(n, m)
    for N in (3, 4):
        built[f"projective grid {N}x{N}"] = projective(N)
    for k in (1, 2, 3):
        built[f"cube {k}x{k} mod antipodal"] = cube_mod_antipodal(k)
    for name, cells in built.items():
        h, F = from_cycles(cells)
        f = features(h, F, rng1, rng2)
        f["four distinct knots in every cell"] = all(len(set(c)) == 4 for c in cells)
        out[name] = f
    for name, pairs in {**GAMES, **OTHER}.items():
        h, F = D.pattern_from_pairs(pairs)
        f = features(h, F, rng1, rng2)
        f["minimal"] = D.minimal(h, F)
        out[name] = f
    return out


def random_patterns(count=150, seed=4040):
    """random closed patterns with all their commuting choices (theorem gate only)"""
    rng = random.Random(seed)
    t = new_tally()
    corr = 0
    for trial in range(count * 3):
        if t["choices"] and trial >= count * 3:
            break
        K = rng.randint(4, 7)
        ends = [(rng.randrange(v), v) for v in range(1, K)]
        for _ in range(rng.randint(K, 2 * K)):
            a, b = rng.sample(range(K), 2)
            ends.append((min(a, b), max(a, b)))
        knots = R.from_ends(ends)
        if min(len(k) for k in knots) < 2:
            continue
        st = R.closed(knots)
        code = R.Code(st, st.unheld)
        basis = R.nullspace(code)
        if len(basis) > 12:
            continue
        holders = {d: tuple(h) for d, h in st.holders.items()}
        w = 0
        for i in range(1, 1 << len(basis)):
            w ^= basis[(i & -i).bit_length() - 1]
            f = features(holders, code.failing(w), rng, rng)
            add(t, f)
            corr += corollary_failure(f)
    return t, corr


# ---------------------------------------------------------------- the run

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--enum", type=int, default=14)
    ap.add_argument("--out", default=str(HERE))
    args = ap.parse_args()
    out = Path(args.out)
    t0 = time.time()
    prior = {r["start"]: r for r in map(json.loads, (RS / "results.jsonl").open())}
    starts = forbid.starts()
    elig, _ = R.population(args.limit)
    rows = []
    with (out / "results.jsonl").open("w") as fh:
        for r in elig:
            stages, births, end = lc.grow(forbid.supports_of(starts[r["start"]]), 4, 40)
            st = lc.Structure(stages, births)
            p = prior[r["start"]]
            kind = "strict" if p["strict"] else ("other only" if p["general"] else "none")
            row = study(R.Code(st, st.local), args.enum, r["start"], lists=p["strict"])
            row.update({"start": r["start"], "readers study's kind": kind, "closing round": r["closing round"]})
            rows.append(row)
            fh.write(json.dumps(row) + "\n")
    census = json.loads(lc.CENSUS.read_text())
    prior_t = {t["type"]: t for t in map(json.loads, (RS / "census_types.jsonl").open())}
    trows = []
    with (out / "census_types.jsonl").open("w") as fh:
        for i, t in enumerate(census):
            st = R.closed(R.from_ends([tuple(x) for x in t["sharing"]]))
            p = prior_t[i]
            kind = "strict" if p.get("strict") else ("other only" if p.get("general") else "none")
            row = study(R.Code(st, st.unheld), args.enum, 100000 + i, lists=bool(p.get("strict")))
            row.update({"type": i, "readers study's kind": kind})
            trows.append(row)
            fh.write(json.dumps(row) + "\n")
    fx = fixtures()
    (out / "fixtures.json").write_text(json.dumps(fx, indent=1) + "\n")
    rp, rp_corr = random_patterns()
    g = gates(rows, trows, fx, rp, rp_corr, args)
    (out / "gates.json").write_text(json.dumps(g, indent=1) + "\n")
    s = summarise(rows, trows)
    s["random patterns (theorem gate)"] = rp
    s["seconds"] = round(time.time() - t0, 1)
    s["peak KiB"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    (out / "summary.json").write_text(json.dumps(s, indent=1) + "\n")
    print(json.dumps({"gates": g, "summary": s}, indent=1))


def totals(rows):
    T = {}
    for r in rows:
        for name, t in r.get("tallies", {}).items():
            merge(T.setdefault(name, new_tally()), t)
    return T


def gates(rows, trows, fx, rp, rp_corr, args):
    g = {}
    allr = rows + trows
    g["unsettled rows"] = sum(1 for r in allr if "unsettled" in r)
    g["theorem holds on every choice of the populations (failures, choices)"] = [
        sum(r["theorem failures"] for r in allr), sum(t["choices"] for t in totals(allr).values())]
    g["no orientable, weakly even or two-colourable choice closes odd (populations)"] = sum(
        r["corollary failures"] for r in allr) == 0
    g["theorem and corollaries on random patterns (failures, choices)"] = [rp["choices"] - rp["theorem holds"] + rp_corr,
                                                                          rp["choices"]]
    g["theorem and corollaries on every fixture"] = all(theorem_ok(f) and not corollary_failure(f) for f in fx.values())

    def ok(name, **want):
        f = fx[name]
        return all(f.get(k) == v for k, v in want.items())
    g["hemi-cube and ring games: odd, not orientable, Euler count 1, not two-colourable"] = all(
        ok(nm, sign=1, orientable=False, **{"Euler count": 1, "two-colourable": False})
        for nm in ("three-reader game", "ring game of five", "ring game of seven", "ring game of nine"))
    g["cube: orientable, Euler count 2, even"] = ok("cube", sign=0, orientable=True, **{"Euler count": 2})
    g["torus grids: orientable, Euler count 0, even"] = all(
        ok(f"torus grid {n}x{m}", sign=0, orientable=True, **{"Euler count": 0}) for n in (3, 4, 5) for m in (3, 4, 5))
    g["Klein grids: not orientable, Euler count 0, odd exactly when n is odd"] = all(
        ok(f"Klein bottle grid {n}x{m}", sign=n % 2, orientable=False, **{"Euler count": 0})
        for n in (3, 4, 5) for m in (3, 4, 5))
    g["projective grids: not orientable, Euler count 1, two-colourable, even"] = all(
        ok(f"projective grid {N}x{N}", sign=0, orientable=False, **{"Euler count": 1, "two-colourable": True})
        for N in (3, 4))
    g["cube mod antipodal: not orientable, Euler count 1, odd exactly when k is odd"] = all(
        ok(f"cube {k}x{k} mod antipodal", sign=k % 2, orientable=False, **{"Euler count": 1}) for k in (1, 2, 3))
    g["constructed grids: every cross pair in two, one cycle at every knot, four knots per cell"] = all(
        fx[nm]["exactly two"] and fx[nm]["one cycle at every knot"] and fx[nm]["four distinct knots in every cell"]
        for nm in fx if "grid" in nm or "mod antipodal" in nm or nm == "cube")
    want = {"three-reader game": 1, "ring game of five": 1, "grown six-pair game": 0, "census six-pair game": 1,
            "census eight-pair game": -1, "census ten-pair game": -3}
    g["six games: odd, minimal, Euler counts 1, 1, 0, 1, -1, -3"] = all(
        fx[k]["sign"] == 1 and fx[k]["minimal"] and fx[k]["Euler count"] == v for k, v in want.items())
    g["fourfold witnesses: odd, minimal, a pair of knots covered four times"] = all(
        fx[k]["sign"] == 1 and fx[k]["minimal"] and fx[k]["most at a cross pair"] == 4
        for k in ("start 4786 fourfold witness", "five-pair fourfold witness"))
    g["seven-knot control: even, two-colourable, Euler count 1"] = ok("even seven-knot control", sign=0,
                                                                       **{"two-colourable": True, "Euler count": 1})
    g["nine-knot choice: odd, Euler count 0"] = ok("nine-knot choice", sign=1, **{"Euler count": 0})
    if args.limit is None:
        cov_fewest = sum(r["coverage four"]["fewest words"] for r in rows)
        cov_fewest_closures = sum(1 for r in rows if r["coverage four"]["fewest words"])
        cov_more = sum(r["coverage four"]["minimal non-fewest words"] for r in rows)
        cov_more_closures = sum(1 for r in rows if r["coverage four"]["minimal non-fewest words"])
        cov_types = sum(r["coverage four"]["fewest words"] + r["coverage four"]["minimal non-fewest words"] for r in trows)
        g["referee's coverage table: fewest words covered four times (words, closures), further minimal (words, closures), types"] = [
            cov_fewest, cov_fewest_closures, cov_more, cov_more_closures, cov_types]
        g["referee's coverage table reproduced"] = [cov_fewest, cov_fewest_closures, cov_more, cov_more_closures,
                                                    cov_types] == [240, 20, 136, 13, 0]
    g["listings at the cap (rows)"] = sum(1 for r in allr if r.get("sizes at the cap"))
    return g


def summarise(rows, trows):
    s = {}
    for label, rs in (("grown closures", rows), ("census types", trows),
                      ("grown closures with no split", [r for r in rows if r["readers study's kind"] == "none"])):
        s[label] = totals(rs)
    fails = [(r.get("start", r.get("type")), r["P1 failures"][:1]) for r in rows + trows if r.get("P1 failures")]
    s["P1 failures (first five rows)"] = fails[:5]
    s["P1 rows failing"] = len(fails)
    s["P1 holds"] = not fails
    return s


if __name__ == "__main__":
    main()
