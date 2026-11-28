"""decode.py: encoded readers (ENCODED-READERS-20261127-001; README.md, frozen predictions G, P1-P4).

A strict odd choice F on a closed pattern: disjoint failing pairs of unheld distinctions, every two knots' checks
commuting, closing odd. A merge takes two pairs (x', x), (y', y) with x' and y' held by the same two knots and x, y
sharing a knot w: if the other holders of x and y coincide, both pairs go (a doubled pair); otherwise they become
(x', z), with z a new distinction held by those two other holders. The merge is forced when w holds no other value of
F. F decodes when some sequence of merges leaves exactly one base game: the three-reader game (four mutually meeting
knots, one pair per way of splitting them into two pairs) or a ring game (a knot meeting every knot of an odd ring,
each pair (n-1)/2 steps on).
    decode.py [--limit N] [--enum 14] [--out DIR]
Writes results.jsonl, census_types.jsonl, fixtures.json, gates.json and summary.json next to this file.
"""
import argparse
import itertools
import json
import random
import resource
import sys
import threading
import time
from pathlib import Path

import networkx as nx
from pysat.card import CardEnc, EncType
from pysat.solvers import Solver

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RS = ROOT / "research" / "READER-SPLIT-20261127-001"
sys.path.insert(0, str(RS))
import readers as R  # noqa: E402  (Code, program, nullspace, is_strict, closed, from_ends, FIXTURES, Cnf; lc, forbid)

lc, forbid = R.lc, R.forbid
SEEDS = (1, 2, 3)
FEWEST_CAP = 1000
SIZE_CAP = 2000
MAX_PAIRS = 8
STATES = 20000
TIME = 60


class Unsettled(Exception):
    pass


def popcount(x):
    return bin(x).count("1")


# ---------------------------------------------------------------- checks on an abstract pattern

def interleave(holders, a, b, pos):
    x1, x2 = sorted(holders[a], key=pos.__getitem__)
    y1, y2 = sorted(holders[b], key=pos.__getitem__)
    p = lambda u: pos[u]
    return int(p(x1) < p(y1) < p(x2) < p(y2) or p(y1) < p(x1) < p(y2) < p(x2))


def check(holders, F, order2):
    """(commuting, disjoint and unheld; sign in index order; sign in the second order)"""
    seen = set()
    for a, b in F:
        if a in seen or b in seen or a == b or set(holders[a]) & set(holders[b]):
            return False, 0, 0
        seen.update((a, b))
    cover = {}
    for a, b in F:
        for u in holders[a]:
            for v in holders[b]:
                key = (min(u, v), max(u, v))
                cover[key] = cover.get(key, 0) ^ 1
    if any(cover.values()):
        return False, 0, 0
    knots = {u for a, b in F for d in (a, b) for u in holders[d]}
    pos1 = {u: u for u in knots}
    pos2 = {u: order2.get(u, u) for u in knots}
    s1 = sum(interleave(holders, a, b, pos1) for a, b in F) % 2
    s2 = sum(interleave(holders, a, b, pos2) for a, b in F) % 2
    return True, s1, s2


def values_at(holders, F):
    at = {}
    for a, b in F:
        for d in (a, b):
            for u in holders[d]:
                at.setdefault(u, []).append(d)
    return at


def minimal(holders, F):
    """no proper non-empty sub-collection commutes: rank of the pairs' met-pair patterns is len(F) - 1"""
    index = {}
    rows = []
    for a, b in F:
        v = 0
        for u in holders[a]:
            for w in holders[b]:
                key = (min(u, w), max(u, w))
                if key not in index:
                    index[key] = len(index)
                v ^= 1 << index[key]
        rows.append(v)
    piv = {}
    for r in rows:
        while r:
            h = r.bit_length() - 1
            if h in piv:
                r ^= piv[h]
            else:
                piv[h] = r
                break
    return len(piv) == len(F) - 1


def key_of(holders, F):
    return tuple(sorted(tuple(sorted((tuple(sorted(holders[a])), tuple(sorted(holders[b]))))) for a, b in F))


# ---------------------------------------------------------------- merges

def merges(holders, F):
    """every applicable merge: (w, x, y, forced)"""
    at = values_at(holders, F)
    partner = {}
    for a, b in F:
        partner[a], partner[b] = b, a
    out = []
    for w, ds in sorted(at.items()):
        for x, y in itertools.combinations(sorted(ds), 2):
            if sorted(holders[partner[x]]) == sorted(holders[partner[y]]):
                out.append((w, x, y, len(ds) == 2))
    return out


def apply(holders, F, move, nxt):
    """returns (holders, F, step) after the merge; holders is copied when a distinction is added"""
    w, x, y, forced = move
    partner = {}
    for a, b in F:
        partner[a], partner[b] = b, a
    xp = partner[x]
    r = [u for u in holders[x] if u != w][0]
    s = [u for u in holders[y] if u != w][0]
    F2 = [p for p in F if x not in p and y not in p]
    step = {"knot": w, "forced": forced}
    if r == s:
        step["kind"] = "doubled pair"
        return holders, F2, step
    h2 = dict(holders)
    h2[nxt] = (min(r, s), max(r, s))
    F2.append((min(xp, nxt), max(xp, nxt)))
    step["kind"] = "merge"
    return h2, F2, step


# ---------------------------------------------------------------- base games

def three_reader(holders, F):
    if len(F) != 3:
        return False
    knots = {u for a, b in F for d in (a, b) for u in holders[d]}
    if len(knots) != 4:
        return False
    splits = {frozenset((frozenset(holders[a]), frozenset(holders[b]))) for a, b in F}
    a, b, c, d = sorted(knots)
    return splits == {frozenset((frozenset((a, b)), frozenset((c, d)))), frozenset((frozenset((a, c)), frozenset((b, d)))),
                      frozenset((frozenset((a, d)), frozenset((b, c))))}


def ring_game(holders, F):
    n = len(F)
    if n < 5 or n % 2 == 0:
        return False
    at = values_at(holders, F)
    for h, ds in at.items():
        if len(ds) != n:
            continue
        spoke_of, ring = {}, []
        good = True
        for a, b in F:
            sa, sb = h in holders[a], h in holders[b]
            if sa == sb:
                good = False
                break
            s, e = (a, b) if sa else (b, a)
            spoke_of[[u for u in holders[s] if u != h][0]] = e
            ring.append(e)
        if not good or len(spoke_of) != n:
            continue
        G = nx.MultiGraph()
        G.add_nodes_from(spoke_of)
        for e in ring:
            G.add_edge(*holders[e])
        if set(G.nodes) != set(spoke_of) or any(G.degree(v) != 2 for v in G) or not nx.is_connected(G):
            continue
        order = [min(spoke_of)]
        while len(order) < n:
            order.append([v for v in G.neighbors(order[-1]) if v not in order][0] if len(order) == 1 else
                         [v for v in G.neighbors(order[-1]) if v != order[-2]][0])
        pos = {v: i for i, v in enumerate(order)}
        half = (n - 1) // 2
        if all(set(holders[e]) == {order[(pos[r] + half) % n], order[(pos[r] + half + 1) % n]}
               for r, e in spoke_of.items()):
            return True
    return False


def base_kind(holders, F):
    if three_reader(holders, F):
        return "three-reader game"
    if ring_game(holders, F):
        return f"ring game of {len(F)}"
    return None


# ---------------------------------------------------------------- decoding

def decode(holders, F, order2):
    """Search merges for exactly one base game. Returns a dict: decodes, kind, steps (of the path found), states,
    checks hold (every merge on the path rechecked afresh), and the forced-only remainder."""
    nxt = [max(holders) + 1]
    seen = set()
    states = [0]
    checks = [True]

    def dfs(h, G, path):
        states[0] += 1
        if states[0] > STATES:
            raise Unsettled("search state cap")
        kind = base_kind(h, G)
        if kind:
            return kind, path
        k = key_of(h, G)
        if k in seen:
            return None
        seen.add(k)
        for mv in merges(h, G):
            nxt[0] += 1
            h2, G2, step = apply(h, G, mv, nxt[0])
            ok, s1, s2 = check(h2, G2, order2) if G2 else (True, 0, 0)
            if not ok or s1 != 1 or s2 != 1:
                checks[0] = False          # a merge that breaks the choice (item 2 says this never happens)
                continue
            got = dfs(h2, G2, path + [step])
            if got:
                return got
        return None
    got = dfs(dict(holders), list(F), [])
    out = {"decodes": got is not None, "states": states[0], "checks hold": checks[0]}
    if got:
        out["kind"], steps = got
        out["merges"] = sum(1 for s in steps if s["kind"] == "merge")
        out["forced merges"] = sum(1 for s in steps if s["kind"] == "merge" and s["forced"])
        out["merges through knots holding other values"] = sum(1 for s in steps if s["kind"] == "merge" and not s["forced"])
        out["doubled pairs met"] = sum(1 for s in steps if s["kind"] == "doubled pair")
        out["knots merged through"] = [s["knot"] for s in steps]
    return out


def forced_remainders(holders, F, order2):
    """forced merges only, under three seeded orders: the sorted remainders, and whether every merge rechecked"""
    rems = []
    ok_all = True
    for seed in SEEDS:
        rng = random.Random(seed)
        h, G = dict(holders), list(F)
        nxt = max(holders) + 1
        while True:
            mv = [m for m in merges(h, G) if m[3]]
            if not mv:
                break
            nxt += 1
            h, G, _ = apply(h, G, mv[rng.randrange(len(mv))], nxt)
            ok, s1, s2 = check(h, G, order2) if G else (True, 0, 0)
            ok_all = ok_all and ok and s1 == 1 and s2 == 1
        rems.append(key_of(h, G))
    return len(set(rems)) == 1, ok_all


# ---------------------------------------------------------------- listing choices of a closure

def listing(code, k, cap):
    """every strict odd choice with exactly k failing pairs, up to cap; (words, complete)"""
    cnf = R.Cnf(code.n)
    R.parity_clauses(code, cnf)
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
        deadline = time.time() + TIME
        while len(out) < cap:
            timer = threading.Timer(max(1.0, deadline - time.time()), s.interrupt)
            timer.start()
            ok = s.solve_limited(expect_interrupt=True)
            timer.cancel()
            if ok is None:
                raise Unsettled(f"listing of {k} pairs interrupted")
            if not ok:
                return out, True
            m = set(v for v in s.get_model() if v > 0)
            word = sum(1 << j for j in range(code.n) if j + 1 in m)
            out.append(word)
            s.add_clause([-(j + 1) for j in range(code.n) if (word >> j) & 1])
    return out, False


def planar(st):
    G = nx.Graph()
    G.add_nodes_from(range(len(st.knots)))
    for d, h in st.holders.items():
        if len(h) == 2:
            G.add_edge(*h)
    return nx.check_planarity(G)[0]


def study(code, enum_limit):
    st = code.st
    holders = {d: tuple(h) for d, h in st.holders.items()}
    sizes = {u: len(k) for u, k in enumerate(st.knots)}
    order2 = list(range(len(st.knots)))
    random.Random(len(st.knots) * 7919 + code.n).shuffle(order2)
    order2 = {u: i for i, u in enumerate(order2)}
    row = {"planar": planar(st)}
    try:
        fs = R.program(code, strict=True)
    except R.Unsettled as e:
        row["unsettled"] = str(e)
        return row
    row["strict"] = fs is not None
    if fs is None:
        return row
    w0 = fs[0]
    row["fewest strict readers"] = w0
    try:
        words, complete = listing(code, w0, FEWEST_CAP)
        row["fewest splits listed"] = len(words)
        row["fewest listing complete"] = complete
        row["integer program's split among them"] = (fs[1] in words) if complete else None
        decs = []
        for w in words:
            F = code.failing(w)
            d = decode(holders, F, order2)
            ats = values_at(holders, F)
            d["c"] = len(ats) - len(F)
            d["same under three orders"], d["forced checks hold"] = forced_remainders(holders, F, order2)
            d["sizes merged through"] = [sizes[u] for u in d.get("knots merged through", []) if u in sizes]
            decs.append(d)
        row["fewest: every one decodes"] = all(d["decodes"] for d in decs)
        row["fewest: kinds"] = sorted({d.get("kind") for d in decs if d["decodes"]})
        row["fewest: checks hold"] = all(d["checks hold"] and d["forced checks hold"] for d in decs)
        row["fewest: forced merges same under three orders"] = all(d["same under three orders"] for d in decs)
        row["fewest: no doubled pair met"] = all(d.get("doubled pairs met", 0) == 0 for d in decs if d["decodes"])
        row["fewest: counting identity"] = all(d["merges through knots holding other values"] == 1 - d["c"]
                                               for d in decs if d["decodes"])
        row["fewest: merges"] = sorted({(d.get("forced merges"), d.get("merges through knots holding other values"))
                                        for d in decs if d["decodes"]})
        row["fewest: sizes merged through"] = sorted({s for d in decs for s in d["sizes merged through"]})
        row["fewest: c"] = sorted({d["c"] for d in decs})
        # P1: minimal strict odd choices with at most MAX_PAIRS pairs
        p1 = {}
        bad = []
        capped = []
        for k in range(w0, MAX_PAIRS + 1):
            ws, comp = listing(code, k, SIZE_CAP)
            if not comp:
                capped.append(k)
            n_min = n_dec = 0
            kinds = {}
            for w in ws:
                F = code.failing(w)
                if not minimal(holders, F):
                    continue
                n_min += 1
                d = decode(holders, F, order2)
                if d["decodes"]:
                    n_dec += 1
                    kinds[d["kind"]] = kinds.get(d["kind"], 0) + 1
                elif len(bad) < 5:
                    bad.append([list(map(list, (holders[a], holders[b]))) for a, b in F])
            p1[str(k)] = {"choices": len(ws), "minimal": n_min, "decode": n_dec, "kinds": kinds}
        row["P1 by pairs"] = p1
        row["P1 minimal choices"] = sum(v["minimal"] for v in p1.values())
        row["P1 decoding"] = sum(v["decode"] for v in p1.values())
        row["P1 sizes at the cap"] = capped
        row["P1 failures (holder pairs)"] = bad
    except Unsettled as e:
        row["unsettled"] = str(e)
        return row
    if enum_limit is not None:
        dim = len(R.nullspace(code))
        row["free choices"] = dim
        if dim <= enum_limit:
            n = n_min = n_dec = 0
            rest = {}
            bad = []
            try:
                for w in strict_odd_words(code):
                    n += 1
                    F = code.failing(w)
                    if minimal(holders, F):
                        n_min += 1
                        d = decode(holders, F, order2)
                        n_dec += d["decodes"]
                        if not d["decodes"] and len(bad) < 5:
                            bad.append([list(map(list, (holders[a], holders[b]))) for a, b in F])
                    else:
                        h, G = dict(holders), list(F)
                        nxt = max(holders) + 1
                        while True:            # forced merges only, then describe what remains
                            mv = [m for m in merges(h, G) if m[3]]
                            if not mv:
                                break
                            nxt += 1
                            h, G, _ = apply(h, G, mv[0], nxt)
                        kk = f"{len(G)} pairs"
                        rest[kk] = rest.get(kk, 0) + 1
            except Unsettled as e:
                row["small code unsettled"] = str(e)
            row["small code: strict odd choices"] = n
            row["small code: minimal"] = n_min
            row["small code: minimal decoding"] = n_dec
            row["small code: failures (holder pairs)"] = bad
            row["small code: not minimal, remainder after forced merges"] = rest
    return row


def strict_odd_words(code):
    basis = R.nullspace(code)
    w = 0
    for i in range(1, 1 << len(basis)):
        w ^= basis[(i & -i).bit_length() - 1]
        if code.sign(w) and R.is_strict(code, w):
            yield w


# ---------------------------------------------------------------- fixtures: the reviewer's constructions

def pattern_from_pairs(pairs):
    """holders and F from failing pairs written as pairs of holder pairs"""
    holders, F = {}, []
    for e, f in pairs:
        a, b = len(holders), len(holders) + 1
        holders[a], holders[b] = tuple(sorted(e)), tuple(sorted(f))
        F.append((a, b))
    return holders, F


NINE = [((0, 4), (1, 3)), ((1, 5), (2, 4)), ((2, 3), (0, 5)), ((3, 7), (4, 6)), ((4, 8), (5, 7)), ((5, 6), (3, 8)),
        ((2, 6), (0, 7)), ((1, 7), (2, 8)), ((0, 8), (1, 6))]


def three_games_example():
    """item 3: three-reader games on {p,q,a,b}, {p,q,c,d}, {p,q,e,f}; ab and cd passed through w (p=0, q=1, a..f=2..7,
    w=8)"""
    p, q, a, b, c, d, e, f, w = range(9)
    pairs = [((p, q), (w, a)), ((p, q), (w, b)), ((p, a), (q, b)), ((p, b), (q, a)),
             ((p, q), (w, c)), ((p, q), (w, d)), ((p, c), (q, d)), ((p, d), (q, c)),
             ((p, q), (e, f)), ((p, e), (q, f)), ((p, f), (q, e))]
    return pattern_from_pairs(pairs), w


def split_into_three_reader_games(holders, F):
    F = list(F)
    if not F:
        return True
    first = F[0]
    for q, r in itertools.combinations(F[1:], 2):
        if three_reader(holders, [first, q, r]):
            if split_into_three_reader_games(holders, [p for p in F[1:] if p not in (q, r)]):
                return True
    return False


def fixtures():
    out = {}
    h, F = pattern_from_pairs(NINE)
    ok, s1, s2 = check(h, F, {u: (u * 5) % 9 for u in range(9)})
    d = decode(h, F, {u: (u * 5) % 9 for u in range(9)})
    out["nine-knot choice: strict, commuting, odd, minimal, does not decode"] = (
        ok and s1 == 1 and s2 == 1 and minimal(h, F) and not d["decodes"])
    (h, F), w = three_games_example()
    ok, s1, s2 = check(h, F, {u: (u * 2) % 9 for u in range(9)})
    at = values_at(h, F)[w]
    partner = {}
    for a, b in F:
        partner[a], partner[b] = b, a
    by = {tuple(sorted(x for x in h[v] if x != w)): v for v in at}     # w's values by their other holder
    va, vb, vc, vd = by[(2,)], by[(3,)], by[(4,)], by[(5,)]
    o2 = {u: (u * 2) % 9 for u in range(9)}

    def two_merges(pair1, pair2):
        h2, G2, _ = apply(h, F, (w, *pair1, False), 100)
        h3, G3, _ = apply(h2, G2, (w, *pair2, len(values_at(h2, G2)[w]) == 2), 101)
        return h3, G3
    hg, Gg = two_merges((va, vb), (vc, vd))
    hb, Gb = two_merges((va, vc), (vb, vd))
    out["item 3 example: odd and commuting"] = ok and s1 == 1 and s2 == 1
    out["item 3 example: pairing ab and cd at w restores three three-reader games"] = split_into_three_reader_games(hg, Gg)
    out["item 3 example: pairing ac and bd at w leaves no merge and no three games"] = (
        not merges(hb, Gb) and not split_into_three_reader_games(hb, Gb))
    st5 = R.closed(R.FIXTURES["ring of five's closure"])
    c5 = R.Code(st5, st5.unheld)
    f5 = R.program(c5, strict=True)
    d5 = decode({x: tuple(y) for x, y in st5.holders.items()}, c5.failing(f5[1]), {u: u for u in range(6)})
    out["ring of five's closure: a ring game with no merge"] = d5["decodes"] and d5["kind"] == "ring game of 5" and \
        d5["merges"] == 0
    stages, births, end = lc.grow(lc.RING3, 4, 40)
    st3 = lc.Structure(stages, births)
    c3 = R.Code(st3, st3.local)
    f3 = R.program(c3, strict=True)
    d3 = decode({x: tuple(y) for x, y in st3.holders.items()}, c3.failing(f3[1]), {u: u for u in range(4)})
    out["ring of three's closure: a three-reader game with no merge"] = d3["decodes"] and \
        d3["kind"] == "three-reader game" and d3["merges"] == 0
    return out


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
            row = study(R.Code(st, st.local), args.enum) if p["strict"] else {"planar": planar(st), "strict": False}
            row.update({"start": r["start"], "closing round": r["closing round"], "readers study's kind": kind,
                        "readers study's fewest strict": p.get("fewest strict readers"),
                        "four mutually meeting knots": p["four mutually meeting knots"],
                        "shortest odd ring around a knot": p["shortest odd ring around a knot"]})
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
            row = study(R.Code(st, st.unheld), args.enum) if p.get("strict") else {"planar": planar(st), "strict": False}
            row.update({"type": i, "readers study's kind": kind})
            trows.append(row)
            fh.write(json.dumps(row) + "\n")
    fx = fixtures()
    (out / "fixtures.json").write_text(json.dumps(fx, indent=1) + "\n")
    g = gates(rows, trows, fx, args)
    (out / "gates.json").write_text(json.dumps(g, indent=1) + "\n")
    s = summarise(rows, trows)
    s["seconds"] = round(time.time() - t0, 1)
    s["peak KiB"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    (out / "summary.json").write_text(json.dumps(s, indent=1) + "\n")
    print(json.dumps({"gates": g, "summary": s}, indent=1))


def gates(rows, trows, fx, args):
    g = dict(fx)
    strict = [r for r in rows if r.get("strict")]
    allr = strict + [t for t in trows if t.get("strict")]
    g["unsettled rows"] = sum(1 for r in rows + trows if "unsettled" in r)
    hist = {}
    for r in strict:
        hist[str(r["fewest strict readers"])] = hist.get(str(r["fewest strict readers"]), 0) + 1
    g["fewest strict counts"] = hist
    if args.limit is None:
        g["fewest strict counts as in the readers study"] = hist == {"3": 423, "4": 198, "5": 66, "6": 5}
    g["fewest strict equals the readers study's at every closure"] = all(
        r["fewest strict readers"] == r["readers study's fewest strict"] for r in strict)
    shapes = json.loads((RS / "referee-R1" / "shapes.json").read_text())
    ref = {e["start"]: sum(e["all minimum strict words by shape"].values()) for e in shapes["by census start"]}
    mine = {r["start"]: r["fewest splits listed"] for r in strict if r["start"] in ref}
    g["fewest words at the 252 as in the referee's record (closures compared)"] = [
        all(mine[s] == ref[s] for s in mine), len(mine), sum(mine.values())]
    settled = [r for r in allr if "unsettled" not in r]
    g["fewest listing at the cap (closures)"] = sum(not r["fewest listing complete"] for r in settled)
    g["integer program's split among the listed where complete"] = all(
        r["integer program's split among them"] is not False for r in settled)
    g["every fewest split decodes to one base game"] = all(r["fewest: every one decodes"] for r in settled)
    g["every merge rechecked"] = all(r["fewest: checks hold"] for r in settled)
    g["forced merges same under three orders"] = all(r["fewest: forced merges same under three orders"] for r in settled)
    g["no doubled pair met by a fewest split"] = all(r["fewest: no doubled pair met"] for r in settled)
    g["counting identity at every fewest split"] = all(r["fewest: counting identity"] for r in settled)
    ex = [r for r in rows if r["start"] == 786]
    if ex:
        g["start 786: decodes by one forced merge"] = ex[0]["fewest: merges"] == [(1, 0)] or ex[0]["fewest: merges"] == [[1, 0]]
    return g


def summarise(rows, trows):
    s = {}
    strict = [r for r in rows if r.get("strict") and "unsettled" not in r]
    ts = [t for t in trows if t.get("strict") and "unsettled" not in t]
    s["closures with a strict split"] = len(strict)
    s["P1 minimal choices (closures)"] = sum(r["P1 minimal choices"] for r in strict)
    s["P1 decoding (closures)"] = sum(r["P1 decoding"] for r in strict)
    s["P1 minimal choices (types)"] = sum(t["P1 minimal choices"] for t in ts)
    s["P1 decoding (types)"] = sum(t["P1 decoding"] for t in ts)
    s["P1 holds"] = s["P1 minimal choices (closures)"] == s["P1 decoding (closures)"]
    s["P1 closures with a size at the cap"] = [(r["start"], r["P1 sizes at the cap"]) for r in strict if r["P1 sizes at the cap"]]
    s["P1 failures (first five closures)"] = [(r["start"], r["P1 failures (holder pairs)"][:1])
                                             for r in strict if r["P1 failures (holder pairs)"]][:5]
    byk = {}
    for r in strict:
        for k, v in r["P1 by pairs"].items():
            b = byk.setdefault(k, {"choices": 0, "minimal": 0, "decode": 0, "kinds": {}})
            for kk in ("choices", "minimal", "decode"):
                b[kk] += v[kk]
            for kind, n in v["kinds"].items():
                b["kinds"][kind] = b["kinds"].get(kind, 0) + n
    s["P3 minimal choices by pairs (one vote per choice)"] = byk
    small = [r for r in strict + ts if "small code: minimal" in r]
    s["P2 codes"] = len(small)
    s["P2 minimal choices"] = sum(r["small code: minimal"] for r in small)
    s["P2 decoding"] = sum(r["small code: minimal decoding"] for r in small)
    s["P2 holds"] = s["P2 minimal choices"] == s["P2 decoding"]
    s["P2 failures (first five)"] = [r["small code: failures (holder pairs)"][:1] for r in small
                                     if r["small code: failures (holder pairs)"]][:5]
    rest = {}
    for r in small:
        for k, v in r["small code: not minimal, remainder after forced merges"].items():
            rest[k] = rest.get(k, 0) + v
    s["P3 strict odd choices not minimal: remainder after forced merges"] = rest
    kinds = {}
    for r in strict:
        k = " + ".join(r["fewest: kinds"]) or "none"
        kinds[k] = kinds.get(k, 0) + 1
    s["P3 base games reached by the fewest splits (closures)"] = kinds
    mh = {}
    for r in strict:
        for m in r["fewest: merges"]:
            key = f"{m[0]} forced, {m[1]} through knots holding other values"
            mh[key] = mh.get(key, 0) + 1
    s["P3 merges of the fewest splits (closure counts per pattern)"] = mh
    sz = {}
    for r in strict:
        for x in r["fewest: sizes merged through"]:
            sz[str(x)] = sz.get(str(x), 0) + 1
    s["P3 sizes in the closure of knots merged through (closures)"] = sz
    tab = {}
    for r in rows:
        key = ("planar" if r["planar"] else "not planar") + " / " + r["readers study's kind"]
        tab[key] = tab.get(key, 0) + 1
    s["P4 grown closures: the literature's planarity against split kind"] = tab
    ttab = {}
    for t in trows:
        key = ("planar" if t["planar"] else "not planar") + " / " + t["readers study's kind"]
        ttab[key] = ttab.get(key, 0) + 1
    s["P4 census types: the literature's planarity against split kind"] = ttab
    s["census types: every fewest split decodes"] = sum(t["fewest: every one decodes"] for t in ts)
    return s


if __name__ == "__main__":
    main()
