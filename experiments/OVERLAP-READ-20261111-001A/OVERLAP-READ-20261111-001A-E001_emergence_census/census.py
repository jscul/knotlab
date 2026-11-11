"""The frozen census of OVERLAP-READ-20261111-001A-E001 (contract.json beside this file): what not-all-equal makes of overlapping bases.

A base is a set of knots (three-element sets of distinctions) with no limit on how many knots a pair lies in. Under the not-all-equal
law (NAE) its allowed states may bind sets that no knot names. For a set S of at most three distinctions:
  frozen        S = {v} takes one value in every state;
  tie           S = {u, v}, both free, takes two of its four patterns;
  emergent knot S = {u, v, w}, not a knot, every pair free, takes fewer than eight patterns.
A base with states is read faithfully exactly when it has none of these (KNOTS-ALONE's definition) and every knot's pairs are free.
A configuration K forces S when S lies in K's distinctions and the states of K alone leave S's pattern count below full; it forces S
minimally when no knot of K can be removed with S still forced.

Parts (frozen):
  C1  the catalogue: every connected configuration of at most 6 knots, up to isomorphism, in which every distinction outside S lies in
      at least two knots; each minimal forcing (configuration, S) with S's relation.
  C2  small bases: every labeled base on 4 to 6 distinctions (by its set of states), and 20,000 random bases on each of 7 to 10.
  C3  NAE-SURFACE-20261111-001's 822 swap-made bases (regenerated from its frozen recipe) and GROW-COUNT-20261111-001's grown bases.
  C4  three-fold weaves: bases on 7 to 14 distinctions in which every co-knotted pair lies in exactly three knots, by SAT.
  C5  bond distance from distinction 0 at graph distance 2 and 3 on faithful bases with a pair in three or more knots.

Run from the repository root:
    .venv/bin/python -B experiments/OVERLAP-READ-20261111-001A/OVERLAP-READ-20261111-001A-E001_emergence_census/census.py
Output: artifacts/OVERLAP-READ-20261111-001A/OVERLAP-READ-20261111-001A-E001_emergence_census/census.json and census_log.txt.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import os
import random
import sys
import time
from collections import Counter, defaultdict
from multiprocessing import Pool

import networkx as nx
import numpy as np
from pysat.card import CardEnc, EncType
from pysat.solvers import Minisat22

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
LIB = os.path.join(ROOT, "experiments", "KNOTS-ALONE-20261111-001A", "KNOTS-ALONE-20261111-001A-E001_knots_alone_census")
LIB_SHA = "aee9a2eda0907064b89eae4fe4badddb22b80fecb62bd91d5a5fa448397010de"
LL = os.path.join(ROOT, "experiments", "LONG-LOOP-20261111-001A", "LONG-LOOP-20261111-001A-E001_long_loops")
sys.path.insert(0, LIB)
import knots_alone as ka  # noqa: E402

CONTROL = "--control" in sys.argv
OUT = os.path.join(ROOT, "artifacts", "OVERLAP-READ-20261111-001A", "OVERLAP-READ-20261111-001A-E001_emergence_census")
if CONTROL:
    OUT = sys.argv[sys.argv.index("--control") + 1]

# Frozen parameters (contract.json, "definitions")
CAT_K = 6                                   # C1: configurations of at most 6 knots
SMALL_EXHAUSTIVE = (4, 5, 6)                # C2: every labeled base
SMALL_RANDOM = (7, 8, 9, 10)                # C2: random bases
SMALL_N, SMALL_SEED = 20000, 20261118       # per size; seed SMALL_SEED + n
FORCE_SAMPLE, FORCE_ORDERS, FORCE_TRIES = 2000, 3, 5   # C2 forcing sets: first 2,000 unfaithful bases per size
NS_V = range(24, 49)                        # C3: NAE-SURFACE's recipe (its F2)
NS_K, NS_REPS, NS_SEED = (1, 2, 4), 2, 20261113
RADIUS_MAX = 4                              # C3: locality radius, emergent sets tried until one has radius <= 2
WEAVE3_V, WEAVE3_N, WEAVE3_SEED = range(7, 15), 30, 20261119   # C4
RULER_MIN_V = 7                             # C5


def log(*a):
    msg = " ".join(str(x) for x in a)
    print(msg, flush=True)
    with open(os.path.join(OUT, "census_log.txt"), "a") as f:
        f.write(msg + "\n")


# ----------------------------------------------------------------------------------------------------------------------
# Readings
# ----------------------------------------------------------------------------------------------------------------------

def states_brute(V, T):
    return ka.all_states(V, T, ka.LAWS["NAE"])


def pcount(st, vs):
    return ka.pattern_count(st, vs)


def relation(st, S):
    """The forbidden patterns of S (as bit strings), and their kind: for a triple 'plain' (000/111) or 'signed <a>'; for a pair
    'equal' or 'unequal'; for one distinction its value."""
    code = np.zeros(len(st), dtype=np.int64)
    for i, v in enumerate(S):
        code |= ((st >> v) & 1) << i
    present = set(np.unique(code).tolist())
    forbidden = sorted("".join(str((p >> i) & 1) for i in range(len(S))) for p in range(1 << len(S)) if p not in present)
    if len(S) == 3:
        pairs = {frozenset((f, "".join("1" if c == "0" else "0" for c in f))) for f in forbidden}
        if len(forbidden) == 2 and len(pairs) == 1:
            a = min(forbidden)
            kind = "plain" if a == "000" else "signed " + a
        else:
            kind = "other " + ",".join(forbidden)
    elif len(S) == 2:
        kind = {("01", "10"): "equal", ("00", "11"): "unequal"}.get(tuple(forbidden), "other " + ",".join(forbidden))
    else:
        kind = "frozen at " + ("1" if forbidden == ["0"] else "0")
    return forbidden, kind


def emergent_brute(V, T, st):
    """Frozen distinctions, ties and emergent knots of a base read by brute force (st its states)."""
    frozen = [(v,) for v in range(V) if pcount(st, (v,)) < 2]
    fz = {v for (v,) in frozen}
    free = {p for p in itertools.combinations(range(V), 2) if pcount(st, p) == 4}
    ties = [p for p in itertools.combinations(range(V), 2) if p not in free and p[0] not in fz and p[1] not in fz]
    kn = set(ka.norm(T))
    extra = [t for t in itertools.combinations(range(V), 3)
             if t not in kn and all(q in free for q in itertools.combinations(t, 2)) and pcount(st, t) < 8]
    native = all(all(q in free for q in itertools.combinations(t, 2)) for t in kn)
    return frozen, ties, extra, native


class SatBase:
    """NAE on a larger base, by SAT under assumptions."""

    def __init__(self, V, T):
        self.V, self.T = V, [tuple(t) for t in T]
        self.s = Minisat22(bootstrap_with=ka.law_clauses(self.T, ka.LAWS["NAE"]))
        self.ok = self.s.solve()
        self.cache = {}
        self.rows = None
        if self.ok:
            rng = random.Random(20261118 + V)
            rows = []
            for _ in range(64):
                self.s.set_phases([v + 1 if rng.random() < 0.5 else -(v + 1) for v in range(V)])
                self.s.solve()
                m = self.s.get_model()
                rows.append([1 if m[v] > 0 else 0 for v in range(V)])
            self.rows = np.array(rows, dtype=np.int64)

    def ext(self, S, p):
        key = (S, p)
        if key not in self.cache:
            if self.rows is not None and np.any(np.all(self.rows[:, list(S)] == np.array(p), axis=1)):
                self.cache[key] = True     # a sampled state shows it
            else:
                self.cache[key] = self.s.solve(assumptions=[v + 1 if b else -(v + 1) for v, b in zip(S, p)])
        return self.cache[key]

    def count(self, S):
        return sum(1 for p in itertools.product((0, 1), repeat=len(S)) if self.ext(S, p))

    def forbidden(self, S):
        return ["".join(str(b) for b in p) for p in itertools.product((0, 1), repeat=len(S)) if not self.ext(S, p)]

    def emergent(self):
        V = self.V
        frozen = [(v,) for v in range(V) if self.count((v,)) < 2]
        fz = {v for (v,) in frozen}
        free = {p for p in itertools.combinations(range(V), 2) if self.count(p) == 4}
        ties = [p for p in itertools.combinations(range(V), 2) if p not in free and p[0] not in fz and p[1] not in fz]
        kn = set(ka.norm(self.T))
        extra = []
        for t in itertools.combinations(range(V), 3):     # every triple is tested, near or far

            if t not in kn and all(q in free for q in itertools.combinations(t, 2)) and self.count(t) < 8:
                extra.append(t)
        native = all(all(q in free for q in itertools.combinations(t, 2)) for t in kn)
        return frozen, ties, extra, native

    def close(self):
        self.s.delete()


def forced(V, T, S):
    """Does NAE on the knots T alone force S (pattern count of S below full)? S must lie in T's distinctions."""
    if not T:
        return False
    pts = sorted({v for t in T for v in t})
    if not set(S) <= set(pts):
        return False
    idx = {v: i for i, v in enumerate(pts)}
    T2 = [tuple(idx[v] for v in t) for t in T]
    S2 = tuple(idx[v] for v in S)
    if len(pts) <= 20:
        st = ka.all_states(len(pts), T2, ka.LAWS["NAE"])
        if len(st) == 0:
            return True
        return pcount(st, S2) < (1 << len(S2))
    with Minisat22(bootstrap_with=ka.law_clauses(T2, ka.LAWS["NAE"])) as s:
        if not s.solve():
            return True
        return any(not s.solve(assumptions=[v + 1 if b else -(v + 1) for v, b in zip(S2, p)])
                   for p in itertools.product((0, 1), repeat=len(S2)))


def greedy_forcing_set(V, T, S, rng):
    """An inclusion-minimal set of knots of T forcing S, by deleting knots in a random order."""
    cur = list(T)
    order = list(range(len(cur)))
    rng.shuffle(order)
    keep = set(range(len(cur)))
    for i in order:
        trial = [cur[j] for j in keep if j != i]
        if forced(V, trial, S):
            keep.discard(i)
    return [cur[j] for j in sorted(keep)]


def ball_knots(T, S, r):
    """Knots all of whose distinctions are within graph distance r of S."""
    adj = defaultdict(set)
    for t in T:
        for a, b in itertools.combinations(t, 2):
            adj[a].add(b)
            adj[b].add(a)
    dist = {v: 0 for v in S}
    frontier = list(S)
    for d in range(1, r + 1):
        nxt = []
        for u in frontier:
            for w in adj[u]:
                if w not in dist:
                    dist[w] = d
                    nxt.append(w)
        frontier = nxt
    return [t for t in T if all(v in dist for v in t)]


def locality_radius(V, T, S, rmax):
    for r in range(1, rmax + 1):
        if forced(V, ball_knots(T, S, r), S):
            return r
    return None


def compact(T):
    """Renumber the distinctions a list of knots uses as 0..V-1, in increasing order."""
    used = sorted({v for t in T for v in t})
    idx = {v: i for i, v in enumerate(used)}
    return len(used), [tuple(sorted(idx[v] for v in t)) for t in T]


def profile(T):
    c = Counter(q for t in T for q in itertools.combinations(sorted(t), 2))
    return {"max knots per pair": max(c.values()) if c else 0, "pairs by count": dict(sorted(Counter(c.values()).items()))}


# ----------------------------------------------------------------------------------------------------------------------
# C1: the catalogue
# ----------------------------------------------------------------------------------------------------------------------

def inc_graph(cfg, S=()):
    G = nx.Graph()
    for i, t in enumerate(cfg):
        G.add_node(("k", i), b="k")
        for v in t:
            G.add_node(("p", v), b="s" if v in S else "p")
            G.add_edge(("k", i), ("p", v))
    return G


def iso(G, H):
    return nx.is_isomorphic(G, H, node_match=lambda x, y: x["b"] == y["b"])


def wl(G):
    return nx.weisfeiler_lehman_graph_hash(G, node_attr="b", iterations=4)


def deg1(cfg):
    c = Counter(v for t in cfg for v in t)
    return sum(1 for v in c.values() if v == 1)


def configurations(K):
    """Connected configurations of at most K knots up to isomorphism, pruned to those that can end with at most three distinctions
    in only one knot."""
    levels = {1: [((0, 1, 2),)]}
    for k in range(2, K + 1):
        buckets = defaultdict(list)
        out = []
        for cfg in levels[k - 1]:
            m = 1 + max(v for t in cfg for v in t)
            ex = set(cfg)
            for new in (0, 1, 2):
                for olds in itertools.combinations(range(m), 3 - new):
                    t = tuple(sorted(olds + tuple(range(m, m + new))))
                    if t in ex:
                        continue
                    c2 = tuple(sorted(cfg + (t,)))
                    if deg1(c2) - 3 * (K - k) > 3:
                        continue
                    G = inc_graph(c2)
                    h = wl(G)
                    if any(iso(G, o) for o in buckets[h]):
                        continue
                    buckets[h].append(G)
                    out.append(c2)
        levels[k] = out
        log(f"C1 configurations with {k} knots: {len(out)}")
    return levels


def catalogue_entries(cfg):
    m = 1 + max(v for t in cfg for v in t)
    st = states_brute(m, list(cfg))
    if len(st) == 0:
        return []
    frozen, ties, extra, _ = emergent_brute(m, list(cfg), st)
    c = Counter(v for t in cfg for v in t)
    out = []
    for S in frozen + ties + extra:
        if any(c[v] == 1 and v not in S for v in c):
            continue
        minimal = True
        for i in range(len(cfg)):
            sub = cfg[:i] + cfg[i + 1:]
            if forced(m, list(sub), S):
                minimal = False
                break
        if minimal:
            _, kind = relation(st, S)
            out.append({"knots": [list(t) for t in cfg], "S": list(S), "size": len(S), "kind": kind})
    return out


def run_catalogue():
    levels = configurations(CAT_K)
    allcfg = [cfg for k in sorted(levels) for cfg in levels[k]]
    with Pool(12) as pool:
        parts = pool.map(catalogue_entries, allcfg, chunksize=20)
    entries, buckets = [], defaultdict(list)
    for part in parts:
        for e in part:
            G = inc_graph([tuple(t) for t in e["knots"]], tuple(e["S"]))
            h = wl(G)
            if any(iso(G, o) for o in buckets[h]):
                continue
            buckets[h].append(G)
            entries.append(e)
    by = Counter((len(e["knots"]), {1: "frozen", 2: "tie", 3: "emergent knot"}[e["size"]]) for e in entries)
    kinds = Counter(e["kind"].split(" ")[0] for e in entries)
    log("C1 minimal forcing entries by (knots, kind):", sorted(by.items()), "relation kinds:", dict(kinds))
    return {"configurations by knots": {k: len(v) for k, v in levels.items()}, "entries": entries,
            "entries by knots and kind": {f"{k} {kind}": n for (k, kind), n in sorted(by.items())}, "relation kinds": dict(kinds)}


# ----------------------------------------------------------------------------------------------------------------------
# C2: small bases
# ----------------------------------------------------------------------------------------------------------------------

def adjacent_apices(T):
    by_pair = defaultdict(list)
    ks = [frozenset(t) for t in T]
    for t in ks:
        for q in itertools.combinations(sorted(t), 2):
            by_pair[frozenset(q)].append(t)
    for q, lst in by_pair.items():
        for t1, t2 in itertools.combinations(lst, 2):
            a, c = (t1 | t2) - q
            for t in by_pair.get(frozenset((a, c)), []):
                if not (t - {a, c}) <= q:
                    return True
    return False


def incomplete_pasch(T):
    """A Pasch configuration {a,b,c}, {a,y,z}, {x,b,z}, {x,y,c} whose complementary four {x,y,z}, {x,b,c}, {a,y,c}, {a,b,z} are not
    all knots."""
    ks = set(frozenset(t) for t in T)
    pts = sorted({v for t in T for v in t})
    for six in itertools.combinations(pts, 6):
        sub = [t for t in ks if t <= set(six)]
        if len(sub) < 4:
            continue
        for P in itertools.combinations(sub, 4):
            c = Counter(v for t in P for v in t)
            if len(c) != 6 or any(x != 2 for x in c.values()):
                continue
            if any(len(s & t) != 1 for s, t in itertools.combinations(P, 2)):
                continue
            # the complement: the four triples on the six meeting each knot of P in exactly one distinction, pairwise in one
            comp = [frozenset(t) for t in itertools.combinations(six, 3)
                    if all(len(set(t) & s) == 1 for s in P)]
            if any(t not in ks for t in comp):
                return True
    return False


def exhaustive_small(n):
    trip = list(itertools.combinations(range(n), 3))
    pairs = list(itertools.combinations(range(n), 2))
    X = np.arange(1 << n)
    bits = [(X >> v) & 1 for v in range(n)]
    mono = np.zeros(1 << n, dtype=np.int64)
    for k, t in enumerate(trip):
        s = bits[t[0]] + bits[t[1]] + bits[t[2]]
        mono |= ((s == 0) | (s == 3)).astype(np.int64) << k
    NT = 1 << len(trip)
    Ts = np.arange(NT, dtype=np.int64)
    S = np.zeros(NT, dtype=np.uint64)
    for x in range(1 << n):
        S |= (((mono[x] & Ts) == 0).astype(np.uint64) << np.uint64(x))
    uniq, inv = np.unique(S, return_inverse=True)

    def props(s):
        s = int(s)
        st = [x for x in range(1 << n) if (s >> x) & 1]
        if not st:
            return None

        def cnt(vs):
            return len({tuple((x >> v) & 1 for v in vs) for x in st})
        frozen = sum(1 for v in range(n) if cnt((v,)) < 2)
        fp = 0
        for k, p in enumerate(pairs):
            if cnt(p) == 4:
                fp |= 1 << k
        ties = sum(1 for k, p in enumerate(pairs) if not (fp >> k) & 1 and cnt((p[0],)) == 2 and cnt((p[1],)) == 2)
        b3 = 0
        for k, t in enumerate(trip):
            if all((fp >> pairs.index(q)) & 1 for q in itertools.combinations(t, 2)) and cnt(t) < 8:
                b3 |= 1 << k
        return frozen, ties, fp, b3
    P = [props(s) for s in uniq]
    pot = [[pairs.index(q) for q in itertools.combinations(t, 2)] for t in trip]
    tab = Counter()
    maxpair = Counter()
    for T in range(1, NT):
        ks = [trip[k] for k in range(len(trip)) if (T >> k) & 1]
        if len({v for t in ks for v in t}) < n or not ka.connected(n, ks):
            continue
        p = P[inv[T]]
        if p is None:
            tab["no state"] += 1
            continue
        frozen, ties, fp, b3 = p
        native = all(all((fp >> q) & 1 for q in pot[k]) for k in range(len(trip)) if (T >> k) & 1)
        f = native and frozen == 0 and ties == 0 and (b3 & ~T) == 0
        aa = adjacent_apices(ks)
        ip = incomplete_pasch(ks) if not aa else None
        tab[f"faithful={f} adjacent_apices={aa} incomplete_pasch={ip}"] += 1
        if f:
            maxpair[profile(ks)["max knots per pair"]] += 1
    log(f"C2 every labeled connected base on {n}:", dict(tab))
    return {"n": n, "table": dict(tab), "faithful by max knots per pair": dict(sorted(maxpair.items()))}


def random_bases(n):
    rng = random.Random(SMALL_SEED + n)
    trip = list(itertools.combinations(range(n), 3))
    out = []
    while len(out) < SMALL_N:
        m = rng.randint(2, len(trip) // 3)
        T = sorted(rng.sample(trip, m))
        if len({v for t in T for v in t}) == n and ka.connected(n, T):
            out.append(T)
    return out


def read_small(args):
    n, T, do_force, seed = args
    st = states_brute(n, T)
    rec = {"knots": len(T), **profile(T)}
    if len(st) == 0:
        rec["states"] = 0
        return rec
    frozen, ties, extra, native = emergent_brute(n, T, st)
    f = native and not frozen and not ties and not extra
    rec.update({"states": int(len(st)), "faithful": f, "frozen": len(frozen), "ties": len(ties), "emergent knots": len(extra),
                "native": native, "kinds": dict(Counter(relation(st, S)[1].split(" ")[0] for S in frozen + ties + extra))})
    if f and rec["max knots per pair"] >= 3 and n >= RULER_MIN_V:
        rows = []
        delta = ka.graph_distance(n, T, 0)
        bd = ka.bond_distances_from(n, T, st, 0, 5)
        for v in range(1, n):
            if delta[v] in (2, 3):
                rows.append({"v": v, "delta": delta[v], "bond distance": bd[v]})
        rec["ruler"] = rows
    if not f and do_force:
        rng = random.Random(seed)
        best = None
        for S in (frozen + ties + extra)[:FORCE_TRIES]:
            for _ in range(FORCE_ORDERS):
                fs = greedy_forcing_set(n, T, S, rng)
                if best is None or len(fs) < len(best[1]):
                    best = (S, fs)
            if best and len(best[1]) <= CAT_K:
                break
        rec["forcing set"] = {"S": list(best[0]), "knots": [list(t) for t in best[1]]} if best else None
        rec["base"] = [list(t) for t in T]
        if best is None or len(best[1]) > CAT_K:
            rec["emergent sets"] = [list(S) for S in frozen + ties + extra]
    return rec


# ----------------------------------------------------------------------------------------------------------------------
# C3: NAE-SURFACE's swap-made bases (its recipe, copied verbatim; importing its census.py would rewrite its log) and GROW-COUNT's
# ----------------------------------------------------------------------------------------------------------------------

def hexn(x, y):
    return max(abs(x), abs(y)) if x * y >= 0 else abs(x) + abs(y)


def ns_faithful_tori(Vs):
    """NAE-SURFACE-20261111-001A-E001's faithful_tori, verbatim."""
    seen, out = set(), []
    for V in Vs:
        for a in range(1, V + 1):
            if V % a:
                continue
            c = V // a
            for b in range(c):
                r = ka.lattice_torus_with_coords(a, b, c)
                if r is None:
                    continue
                _, T = r
                code = min(ka.canon_codes_surface(T))
                if code in seen:
                    continue
                seen.add(code)
                L = [(i * a, i * b + j * c) for i in range(-8, 9) for j in range(-8, 9) if (i, j) != (0, 0)]
                ew = min(hexn(*u) for u in L)
                if ew < 5:
                    continue
                if ka.read_law_sat(V, T, ka.LAWS["NAE"]).get("faithful"):
                    out.append({"V": V, "lattice": [a, b, c], "edge_width": ew, "T": [list(t) for t in T]})
    return out


def ns_swap_worlds(V, T, k, seed):
    """NAE-SURFACE-20261111-001A-E001's swap_worlds, verbatim."""
    rng = random.Random(seed)
    knots = [tuple(sorted(t)) for t in T]
    present = set(knots)
    done, tries = 0, 0
    while done < k and tries < 10000:
        tries += 1
        i, j = rng.sample(range(len(knots)), 2)
        t1, t2 = knots[i], knots[j]
        if set(t1) & set(t2):
            continue
        c, z = rng.choice(t1), rng.choice(t2)
        n1 = tuple(sorted([v for v in t1 if v != c] + [z]))
        n2 = tuple(sorted([v for v in t2 if v != z] + [c]))
        if n1 in present or n2 in present or n1 == n2:
            continue
        present -= {t1, t2}
        present |= {n1, n2}
        knots[i], knots[j] = n1, n2
        done += 1
    if done < k:
        return None
    return sorted(knots)


def long_loop():
    """LONG-LOOP's frozen census module (its ruler: bond distance from distinction 0 at graph distance 2 and 3), loaded by path since
    this file is also named census.py."""
    import importlib.util
    if "long_loop_census" not in sys.modules:
        spec = importlib.util.spec_from_file_location("long_loop_census", os.path.join(LL, "census.py"))
        mod = importlib.util.module_from_spec(spec)
        sys.modules["long_loop_census"] = mod
        spec.loader.exec_module(mod)
    return sys.modules["long_loop_census"]


def read_large(item):
    V, T = item["V"], [tuple(t) for t in item["T"]]
    b = SatBase(V, T)
    rec = {k: v for k, v in item.items() if k != "T"}
    rec.update(profile(T))
    if not b.ok:
        rec["states"] = False
        b.close()
        return rec
    frozen, ties, extra, native = b.emergent()
    f = native and not frozen and not ties and not extra
    kinds = Counter()
    for S in frozen + ties + extra:
        fb = b.forbidden(S)
        if len(S) == 3:
            kinds["plain" if fb == ["000", "111"] else ("signed" if len(fb) == 2 else "other")] += 1
        elif len(S) == 2:
            kinds["equal" if fb == ["01", "10"] else ("unequal" if fb == ["00", "11"] else "other")] += 1
        else:
            kinds["frozen"] += 1
    rec.update({"states": True, "faithful": f, "frozen": len(frozen), "ties": len(ties), "emergent knots": len(extra),
                "native": native, "kinds": dict(kinds)})
    b.close()
    if not f:
        radii = []
        for S in frozen + ties + extra:
            r = locality_radius(V, T, S, RADIUS_MAX)
            radii.append(r)
            if r is not None and r <= 2:
                break
        rec["locality radii"] = radii
    elif rec["max knots per pair"] >= 3 and item.get("ruler", True):
        rec["ruler"] = long_loop().ruler(V, T, 20261118 + V)
    return rec


# ----------------------------------------------------------------------------------------------------------------------
# C4: three-fold weaves
# ----------------------------------------------------------------------------------------------------------------------

def three_fold(n, count, seed):
    """Bases on n distinctions, every distinction used, connected, every co-knotted pair in exactly three knots."""
    trip = list(itertools.combinations(range(n), 3))
    x = {t: i + 1 for i, t in enumerate(trip)}
    top = len(trip)
    clauses = []
    pairs = list(itertools.combinations(range(n), 2))
    y = {}
    for p in pairs:
        top += 1
        y[p] = top
        lits = [x[t] for t in trip if set(p) <= set(t)]
        for l in lits:
            clauses.append([y[p], -l])          # not co-knotted: no knot on it
        for make in (CardEnc.atleast, CardEnc.atmost):     # built one after the other, so their auxiliaries do not overlap
            enc = make(lits, bound=3, top_id=top, encoding=EncType.seqcounter)
            top = max(top, enc.nv)
            for cl in enc.clauses:
                clauses.append(cl + [-y[p]])
    for v in range(n):
        clauses.append([x[t] for t in trip if v in t])
    rng = random.Random(seed)
    out, seen = [], set()
    with Minisat22(bootstrap_with=clauses) as s:
        tries = 0
        while len(out) < count and tries < 20 * count:
            tries += 1
            s.set_phases([(i if rng.random() < 0.2 else -i) for i in range(1, len(trip) + 1)])
            if not s.solve(assumptions=[x[t] for t in rng.sample(trip, 2)]):
                continue
            m = set(s.get_model())
            T = [t for t in trip if x[t] in m]
            key = tuple(T)
            if key in seen or not ka.connected(n, T):
                continue
            seen.add(key)
            out.append(T)
            s.add_clause([-x[t] for t in T])
    return out


def read_three_fold(args):
    n, T = args
    st = states_brute(n, T)
    rec = {"n": n, "knots": len(T), **profile(T)}
    if len(st) == 0:
        rec["states"] = 0
        return rec
    frozen, ties, extra, native = emergent_brute(n, T, st)
    rec.update({"states": int(len(st)), "faithful": native and not frozen and not ties and not extra, "frozen": len(frozen),
                "ties": len(ties), "emergent knots": len(extra), "adjacent apices": adjacent_apices(T)})
    return rec


# ----------------------------------------------------------------------------------------------------------------------
# The registered predictions (contract.json, "predictions") and consistency checks
# ----------------------------------------------------------------------------------------------------------------------

def embeds(entry_graph, T, S):
    """Does the catalogue entry (incidence graph, its S marked) map into the base T with its S onto S (knots to knots, distinctions
    one-to-one)?"""
    B = inc_graph([tuple(t) for t in T], tuple(S))
    gm = nx.algorithms.isomorphism.GraphMatcher(B, entry_graph, node_match=lambda x, y: x["b"] == y["b"])
    return gm.subgraph_is_monomorphic()


def summarize(out, items):
    sm = {}
    ents = out["C1"]["entries"]
    small = sorted((len(e["knots"]), e["kind"]) for e in ents if len(e["knots"]) <= 4)
    sm["P1"] = {"entries with at most 4 knots": small,
                "holds": small == sorted([(3, "signed 001"), (4, "unequal"), (4, "plain"), (4, "plain"), (4, "signed 011")])}
    kinds = Counter(e["kind"].split(" ")[0] for e in ents)
    for n in SMALL_RANDOM:
        for r in out["C2 random"][n]:
            for k, v in r.get("kinds", {}).items():
                kinds[k] += v
    for r in out["C3"]:
        for k, v in r.get("kinds", {}).items():
            kinds[k] += v
    sm["P2"] = {"relation kinds": dict(kinds), "holds": "other" not in kinds}
    fails, sizes, fallback = [], Counter(), Counter()
    cat = defaultdict(list)
    cat_list = []
    for e in ents:
        G = inc_graph([tuple(t) for t in e["knots"]], tuple(e["S"]))
        cat[wl(G)].append(G)
        cat_list.append((e, G))
    x2_total = x2_miss = 0
    for n in SMALL_RANDOM:
        for r in out["C2 random"][n]:
            if "forcing set" not in r:
                continue
            fs = r["forcing set"]
            size = len(fs["knots"]) if fs else None
            sizes[size] += 1
            if size is None or size > CAT_K:
                # exact fallback: does any catalogue entry map onto any emergent set of the base?
                ok = any(embeds(G, r["base"], S) for S in r.get("emergent sets", [])
                         for e, G in cat_list if len(e["S"]) == len(S))
                fallback["explained"] += ok
                fallback["tried"] += 1
                if not ok:
                    fails.append({"n": n, "base": r.get("base"), "forcing set": fs})
            else:
                used = sorted({v for t in fs["knots"] for v in t} | set(fs["S"]))
                idx = {v: i for i, v in enumerate(used)}
                G = inc_graph([tuple(sorted(idx[v] for v in t)) for t in fs["knots"]], tuple(idx[v] for v in fs["S"]))
                x2_total += 1
                if not any(iso(G, o) for o in cat[wl(G)]):
                    x2_miss += 1
    sm["P3"] = {"forcing-set sizes": {str(k): v for k, v in sorted(sizes.items(), key=lambda kv: (kv[0] is None, kv[0] or 0))},
                "greedy above 6, then the exact catalogue check": dict(fallback), "failures": fails[:5],
                "holds": not fails}
    sm["X2"] = {"forcing sets of at most 6 knots": x2_total, "not in the catalogue": x2_miss, "holds": x2_miss == 0}
    ns = [r for r in out["C3"] if r["family"] == "NAE-SURFACE"]
    p4f = [r for r in ns if r.get("states") and not r["faithful"]
           and not any(x is not None and x <= 3 for x in r.get("locality radii", []))]
    sm["P4"] = {"unfaithful": sum(1 for r in ns if r.get("states") and not r["faithful"]),
                "radii": dict(Counter(str(min([x for x in r.get("locality radii", []) if x is not None], default=None))
                                      for r in ns if r.get("states") and not r["faithful"])),
                "failures": [{k: r[k] for k in ("V", "torus", "swaps", "rep")} for r in p4f[:5]], "holds": not p4f}
    rec = json.load(open(os.path.join(ROOT, "artifacts", "NAE-SURFACE-20261111-001A",
                                      "NAE-SURFACE-20261111-001A-E001_faithful_non_surface", "census.json")))["records"]
    want = {}
    for r in rec:
        if r["family"] == "F2":
            nae = r["NAE"] if isinstance(r["NAE"], dict) else json.loads(r["NAE"].replace("'", '"').replace("True", "true")
                                                                          .replace("False", "false"))
            key = (int(r["V"]), str(r["torus"]).replace(" ", ""), int(r["swaps"]), int(r["rep"]))
            want[key] = bool(nae.get("faithful"))
    have = {(r["V"], str(r["torus"]).replace(" ", ""), r["swaps"], r["rep"]): bool(r.get("faithful")) for r in ns}
    sm["X1"] = {"regenerated": len(have), "recorded": len(want), "faithful": sum(have.values()),
                "mismatches": sum(1 for k in want if have.get(k) != want[k]), "holds": have == want}
    c4 = out["C4"]
    sm["P5"] = {"weaves": len(c4), "with states": sum(1 for r in c4 if r.get("states")),
                "faithful": sum(1 for r in c4 if r.get("faithful")), "holds": not any(r.get("faithful") for r in c4)}
    ex6 = next((r for r in out["C2 exhaustive"] if r["n"] == 6), {}).get("table")
    sm["X3"] = {"n=6 table": ex6}
    # measured: faithful overlapping bases and their rulers
    meas = {}
    for n in SMALL_RANDOM:
        rs = out["C2 random"][n]
        meas[f"small {n}"] = {"with states": sum(1 for r in rs if r.get("states")), "faithful": sum(1 for r in rs if r.get("faithful")),
                              "faithful with a pair in 3+ knots": sum(1 for r in rs if r.get("faithful") and r["max knots per pair"] >= 3),
                              "ruler rows (graph distance: bond distance)": dict(Counter(f"{x['delta']}: {x['bond distance']}"
                                                                                           for r in rs for x in r.get("ruler", [])))}
    gc = [r for r in out["C3"] if r["family"] == "GROW-COUNT"]
    meas["grown"] = {"bases": len(gc), "faithful": sum(1 for r in gc if r.get("faithful")),
                     "with a pair in 3+ knots": sum(1 for r in gc if r["max knots per pair"] >= 3),
                     "ruler rows (graph distance, bond of 4, bond of 5)": dict(Counter(
                         f"{x['delta']}, {x.get('bond4_local', x.get('bond4_global'))}, {x.get('bond5_local')}"
                         for r in gc for x in r.get("ruler", [])))}
    meas["swap-made"] = {"bases": len(ns), "faithful": sum(1 for r in ns if r.get("faithful"))}
    sm["measured"] = meas
    sm["failures"] = [k for k in ("P1", "P2", "P3", "P4", "P5", "X1", "X2") if not sm[k]["holds"]]
    return sm


# ----------------------------------------------------------------------------------------------------------------------

def main():
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, "census_log.txt"), "w").close()
    t0 = time.time()
    have = hashlib.sha256(open(os.path.join(LIB, "knots_alone.py"), "rb").read()).hexdigest()
    log("library hash matches:", have == LIB_SHA)
    if have != LIB_SHA:
        raise SystemExit("library changed")
    out = {}
    if CONTROL:
        # outside the families: the octahedron (faithful), a Pasch alone (four emergent knots), a 3-page book (faithful)
        Ps = [(0, 2, 4), (0, 3, 5), (1, 2, 5), (1, 3, 4)]
        Oc = Ps + [(1, 3, 5), (1, 2, 4), (0, 3, 4), (0, 2, 5)]
        for name, V, T in (("Pasch", 6, Ps), ("octahedron", 6, Oc), ("book3", 5, [(0, 1, 2), (0, 1, 3), (0, 1, 4)])):
            st = states_brute(V, T)
            fr, ti, ex, na = emergent_brute(V, T, st)
            out[name] = {"emergent knots": [list(t) for t in ex], "kinds": [relation(st, S)[1] for S in ex], "ties": len(ti)}
            log("control", name, out[name])
        out["catalogue"] = run_catalogue() if "--catalogue" in sys.argv else None
        json.dump(out, open(os.path.join(OUT, "census.json"), "w"), indent=1)
        return
    out["C1"] = run_catalogue()
    log("C1 done", round(time.time() - t0, 1), "s")
    out["C2 exhaustive"] = [exhaustive_small(n) for n in SMALL_EXHAUSTIVE]
    log("C2 exhaustive done", round(time.time() - t0, 1), "s")
    out["C2 random"] = {}
    for n in SMALL_RANDOM:
        bases = random_bases(n)
        jobs = [(n, T, False, 0) for T in bases]
        with Pool(12) as pool:
            recs = pool.map(read_small, jobs, chunksize=50)
        unf = [i for i, r in enumerate(recs) if r.get("states") and not r["faithful"]][:FORCE_SAMPLE]
        with Pool(12) as pool:
            frecs = pool.map(read_small, [(n, bases[i], True, SMALL_SEED + 7 * i) for i in unf], chunksize=5)
        for i, fr in zip(unf, frecs):
            recs[i] = fr
        out["C2 random"][n] = recs
        log(f"C2 random {n}: {len(recs)} bases, states {sum(1 for r in recs if r.get('states'))},"
            f" faithful {sum(1 for r in recs if r.get('faithful'))}, forcing sets {len(unf)}", round(time.time() - t0, 1), "s")
    # C3
    tori = ns_faithful_tori(NS_V)
    log("C3 NAE-SURFACE's faithful tori:", len(tori), round(time.time() - t0, 1), "s")
    items = []
    for nn, tor in enumerate(tori):
        for k in NS_K:
            for rep in range(NS_REPS):
                W = ns_swap_worlds(tor["V"], [tuple(t) for t in tor["T"]], k, seed=NS_SEED + 1000 * nn + 10 * k + rep)
                if W is not None:
                    items.append({"family": "NAE-SURFACE", "V": tor["V"], "torus": tor["lattice"], "swaps": k, "rep": rep, "T": W})
    gc = json.load(open(os.path.join(ROOT, "artifacts", "GROW-COUNT-20261111-001A",
                                     "GROW-COUNT-20261111-001A-E001_count_from_growth", "census.json")))["runs"]
    for r in gc:
        if r["law"] == "NAE":
            T = json.loads(r["T"]) if isinstance(r["T"], str) else r["T"]
            V, T = compact(T)            # its runs left unused numbers behind (GROW-COUNT's phantom distinctions)
            items.append({"family": "GROW-COUNT", "V": V, "rule": r["rule"], "bias": r["bias"], "seed": r["seed"], "T": T})
    log("C3 bases:", Counter(i["family"] for i in items))
    with Pool(12) as pool:
        out["C3"] = pool.map(read_large, items, chunksize=1)
    log("C3 done", round(time.time() - t0, 1), "s")
    # C4
    jobs = []
    for n in WEAVE3_V:
        for T in three_fold(n, WEAVE3_N, WEAVE3_SEED + n):
            jobs.append((n, T))
    with Pool(12) as pool:
        out["C4"] = pool.map(read_three_fold, jobs, chunksize=1)
    log("C4 three-fold weaves:", Counter(r["n"] for r in out["C4"]), "with states", sum(1 for r in out["C4"] if r.get("states")),
        "faithful", sum(1 for r in out["C4"] if r.get("faithful")), round(time.time() - t0, 1), "s")
    # coverage
    out["coverage"] = {"C1 knots": sorted(out["C1"]["configurations by knots"]) == list(range(1, CAT_K + 1)),
                       "C2 exhaustive": [r["n"] for r in out["C2 exhaustive"]] == list(SMALL_EXHAUSTIVE),
                       "C2 random": all(len(out["C2 random"][n]) == SMALL_N for n in SMALL_RANDOM),
                       "C3 NAE-SURFACE": sum(1 for i in items if i["family"] == "NAE-SURFACE"),
                       "C4 sizes": sorted({r["n"] for r in out["C4"]})}
    log("coverage:", out["coverage"])
    out["summary"] = summarize(out, items)
    log("summary:", json.dumps(out["summary"], default=str)[:4000])
    json.dump(out, open(os.path.join(OUT, "census.json"), "w"), indent=1, default=str)
    log("done", round(time.time() - t0, 1), "s")


if __name__ == "__main__":
    main()
