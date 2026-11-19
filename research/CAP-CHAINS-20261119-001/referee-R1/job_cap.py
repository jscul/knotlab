"""Shared-runner job for the referee's check of CAP-CHAINS-20261119-001 (own constructions, own graph enumeration, own classification,
X+ reading, growth and relayed model; the touch census's arrangements read from runs/touch-census as data; no study code imported
or run).

Parts:
- F: the families, built by the referee from the proof's text: S_3 to S_6 at bare sizes (the referee's own bare sizes), T_1 and T_2
  (dead three-place hubs, members of five places, connectors and ends of three), the ring of seven with one knot hung on it and
  the bare rings of 5, 7 and 8 at bare sizes.  For each: class, reading, rays per piece, growth against the relayed model per round
  to round 8, the referee's growth to many rounds and its exact minimal recurrence (Berlekamp-Massey over Q).
- G: every connected graph with no cycle of 3, 4 or 6 knots and deg_k + sum over neighbours (deg_w - 1) <= 5, to 14 knots (the
  study: 12), by the referee's own augmentation (a new knot joined to any set of old ones; both conditions pass to connected
  subgraphs, and every connected graph has a knot whose removal keeps it connected); cross-checked against the networkx atlas to
  7 knots.  The core shape of each.
- A (one case per graph): every assignment open_k in [max(1, d_k), 5 - deg_k] (to 13 knots), each read by the referee's own
  classification: in the class, the most rays in one piece, a relay included (Theorem 1); and, to 10 knots (the study: 9), every
  simple start with sizes in [max(3, deg_k + 1), 5]: in the class, read three or more dimensions (C3).
- C: every connected graph of 6 or 7 knots in the atlas with girth at least 5 and a 6-cycle, every all-live size assignment within
  five places, no cap filter: none in the class (Lemma 1's 6-cycle step, C4).
- X: the touch census's in-class arrangements with no dead knot: the most rays in one piece (C5).

  .venv/bin/python -B scripts/longrun.py launch research/CAP-CHAINS-20261119-001/referee-R1/job_cap.py \\
      --out runs/referee-cap --unit referee-cap --workers 4 --case-timeout 7200 --case-mem 3G --mem-max 16G
"""
import itertools
import json
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for p in ("research/WEIGHTINGS-20261119-001/referee-R1", "research/DOUBLE-IDENT-20261119-001/referee-R1",
          "research/RELAY-IDENT-20261119-001/referee-R1", "research/CHAIN-IDENT-20261119-001/referee-R1",
          "research/RING-IDENT-20261119-001/referee-R1", "research/FIRST-KNOT-20261118-001/referee-R1",
          "research/TOUCH-CENSUS-20261118-001/referee-R1", "research/BREAK-EDDIES-20261119-001/referee-R1"):
    sys.path.insert(0, str(ROOT / p))
NMAX = 14
NA = 13
NREAD = 10
PARAMS = {}


def setup(params):
    PARAMS.update(params)


def flat_of(n, edges):
    c = Counter(tuple(sorted(e)) for e in edges)
    return [c[(a, b)] for a, b in itertools.combinations(range(n), 2)]


def most_rays(sizes, flat):
    """The most rays in one piece of X+, a relay (two rays on each finite piece when there are two or more) included."""
    import job_double as JD
    X = JD.build(sizes, flat, 2)
    pieces = [c for c in X["comps"].values() if c["knots"]]
    best = 0
    for c in pieces:
        pts = c["points"] | c["knots"]
        cyc = c["inc"] - (len(pts) + c["blocks"]) + 1
        r = c["rays"]
        if r == 0 and cyc == 0 and len(pieces) >= 2:
            r = 2
        best = max(best, r)
    return best, sorted((c["rays"] for c in pieces), reverse=True)


def in_class(c):
    return c in ("in", "one loose", "none")


# ---- families ----

def family_S(R):
    edges, n = [], 0

    def new():
        nonlocal n
        n += 1
        return n - 1
    branches = [new() for _ in range(R - 2)]
    for a, b in zip(branches, branches[1:]):
        x = new()
        edges += [(a, x), (x, b)]
    for i, b in enumerate(branches):
        arms = 3 if R == 3 else (2 if i in (0, len(branches) - 1) else 1)
        for _ in range(arms):
            a = new()
            leaf = new()
            edges += [(b, a), (a, leaf)]
    return n, edges


def family_T(h):
    sizes, edges = [], []

    def new(p):
        sizes.append(p)
        return len(sizes) - 1

    def hub(depth, entry=None):
        H = new(3)
        members = ([entry] if entry is not None else []) + [new(5) for _ in range(3 - (entry is not None))]
        for m in members:
            edges.append((H, m))
        for m in members:
            if m == entry:
                continue
            X = new(3)
            edges.append((m, X))
            if depth == h:
                edges.append((X, new(3)))
            else:
                m2 = new(5)
                edges.append((X, m2))
                hub(depth + 1, m2)
    hub(1)
    return sizes, edges


def light_counts(sizes, edges, rounds, maxj=600000):
    """Per-round counts by the referee's engine with the implied test read structurally (a connected start: a junction is implied
    exactly when it takes every loose distinction of the stage, PARENT-RULE Lemma 2) instead of by GF(2) elimination, which is what
    costs memory on long runs.  The two agree wherever both run (checked here on the first rounds)."""
    import job_ring as JR
    import referee_first as RFK

    class Light(RFK.Start):
        def _add(self, j):
            pass

        def _reduce(self, x):
            return 0 if x == self._loose0 else x

        def step(self, rule, cap=None, rng=None):
            self._loose0 = sum(1 << b for b, js in self.owner.items() if len(js) == 1)
            return super().step(rule, cap, rng)
    n = len(sizes)
    G = Light(JR.stars_of(n, edges, list(sizes)))
    counts = [n]
    for _ in range(rounds):
        r = G.step(floored, None, None)
        if r != "ok":
            counts.append(r)
            break
        counts.append(sum(1 for x in G.round if x == G.rounds))
        if len(G.bits) > maxj:
            break
    return counts


def floored(G, info, rng):
    return [i["d"] if i["implied"] else max(i["d"], 3 - i["p"], 1) for i in info]


def grow_family(sizes, edges, rounds):
    import job_double as JD
    import job_relay as RL
    import job_weight as JW
    import break_readout as BR
    n = len(sizes)
    flat = flat_of(n, edges)
    c = JD.classify(sizes, flat)
    out = {"knots": n, "largest knot": max(sizes), "dead knots": 0, "class": c}
    sh = Counter()
    for a, b in edges:
        sh[a] += 1
        sh[b] += 1
    out["dead knots"] = sum(1 for k in range(n) if sizes[k] - sh[k] == 0)
    if not in_class(c):
        return out
    X = JD.build(sizes, flat, 2)
    out["reading"] = str(JD.predict(X))
    out["most rays in a piece"], out["rays per piece"] = most_rays(sizes, flat)
    X8 = JD.build(sizes, flat, 11)
    a, _ = RL.grow_keys(n, X8["edges"], list(sizes), 8)
    b = RL.relayed_keys(n, X8, 9)
    out["agrees with the relayed model to round 8"] = all(
        {k: Fraction(v) for k, v in a.get(t, {}).items()} == {k: v for k, v in b.get(t, {}).items() if v} for t in range(9))
    _, exact = RL.grow_keys(n, JD.data(sizes, flat)[1], list(sizes), 6)
    counts = light_counts(sizes, JD.data(sizes, flat)[1], rounds)
    out["light engine equals the GF(2) engine to round 6"] = counts[:len(exact)] == exact
    num = [x for x in counts if isinstance(x, int)]
    out["counts"] = counts
    rd = BR.read(num)
    out["recurrence"] = {k: v for k, v in rd.items() if not k.startswith("family")} if rd else None
    if num and len(num) > 3:
        out["last ratios"] = [round(num[t] / num[t - 1], 4) for t in range(max(1, len(num) - 5), len(num))]
    return out


def part_f():
    import job_weight as JW
    out = {}
    for R in (3, 4, 5, 6):
        n, e = family_S(R)
        sizes = JW.my_bare(n, flat_of(n, e))
        out[f"S_{R}"] = grow_family(sizes, e, 24 if R <= 5 else 20)
    for h in (1, 2):
        sizes, e = family_T(h)
        out[f"T_{h}"] = grow_family(sizes, e, 24 if h == 1 else 18)
    for L, leaf in ((5, False), (7, False), (8, False), (7, True)):
        e = [tuple(sorted((i, (i + 1) % L))) for i in range(L)] + ([(0, L)] if leaf else [])
        n = L + leaf
        sizes = JW.my_bare(n, flat_of(n, e))
        out[f"ring of {L}" + (" with a leaf" if leaf else "")] = grow_family(sizes, e, 60 if leaf else 30)
    return out


# ---- graphs ----

def ok_graph(G):
    import networkx as nx
    if any(G.degree(k) + sum(G.degree(w) - 1 for w in G[k]) > 5 for k in G):
        return False
    try:
        g = nx.girth(G)
    except Exception:
        g = float("inf")
    if g < 5:
        return False
    return not any(len(c) == 6 for c in nx.simple_cycles(G, length_bound=6))


def graphs(nmax):
    import networkx as nx
    levels = {1: [nx.empty_graph(1)]}
    for n in range(1, nmax):
        found = defaultdict(list)
        for G in levels[n]:
            for r in range(1, n + 1):
                for S in itertools.combinations(range(n), r):
                    H = G.copy()
                    H.add_edges_from((n, s) for s in S)
                    if not ok_graph(H):
                        continue
                    key = tuple(sorted(Counter(dict(H.degree()).values()).items())), nx.weisfeiler_lehman_graph_hash(H, iterations=5)
                    if any(nx.is_isomorphic(H, K) for K in found[key]):
                        continue
                    found[key].append(H)
        levels[n + 1] = [K for v in found.values() for K in v]
    return levels


def core_shape(G):
    import networkx as nx
    core = [k for k in G if G.degree(k) >= 2]
    if len(core) <= 1:
        return "star or less"
    C = G.subgraph(core)
    if not nx.is_connected(C) or max(dict(C.degree()).values()) > 2:
        return "other"
    return "cycle" if all(d == 2 for _, d in C.degree()) else "path"


def part_g():
    import networkx as nx
    lv = graphs(NMAX)
    out = {"graphs by size": {n: len(v) for n, v in lv.items()}, "core shapes": dict(Counter(core_shape(G) for v in lv.values() for G in v))}
    atlas = Counter()
    for G in nx.graph_atlas_g():
        if 1 <= G.number_of_nodes() <= 7 and nx.is_connected(G) and ok_graph(G):
            atlas[G.number_of_nodes()] += 1
    out["atlas, to 7 knots"] = dict(atlas)
    out["augmentation agrees with the atlas to 7"] = all(atlas[n] == len(lv[n]) for n in range(1, 8))
    out["edge lists"] = {n: [sorted(tuple(sorted(e)) for e in G.edges()) for G in v] for n, v in lv.items()}
    return out


def part_a(n, edges):
    import job_double as JD
    edges = [tuple(x) for x in edges]
    eset = set(edges)
    deg = Counter()
    for a, b in edges:
        deg[a] += 1
        deg[b] += 1
    dform = [sum(deg[w] - 1 for w in range(n) if (min(k, w), max(k, w)) in eset) for k in range(n)]
    flat = flat_of(n, edges)
    s = Counter()
    if n <= NA:
        for opn in itertools.product(*[range(max(1, dform[k]), 5 - deg[k] + 1) for k in range(n)]):
            sizes = [deg[k] + opn[k] for k in range(n)]
            c = JD.classify(sizes, flat)
            s["assignments"] += 1
            if in_class(c):
                s["in the class"] += 1
                best, _ = most_rays(sizes, flat)
                s[f"most rays in a piece {best}"] += 1
    if n <= NREAD:
        for sizes in itertools.product(*[range(max(3, deg[k] + 1), 6) for k in range(n)]):
            sizes = list(sizes)
            c = JD.classify(sizes, flat)
            s["simple starts"] += 1
            if in_class(c):
                D = str(JD.predict(JD.build(sizes, flat, 2)))
                s[f"simple starts in the class read {D}"] += 1
            else:
                s[f"simple starts {c}"] += 1
    return dict(s)


def part_c():
    import job_double as JD
    import networkx as nx
    s = Counter()
    for G in nx.graph_atlas_g():
        n = G.number_of_nodes()
        if n not in (6, 7) or not nx.is_connected(G):
            continue
        try:
            if nx.girth(G) < 5:
                continue
        except Exception:
            continue
        if not any(len(c) == 6 for c in nx.simple_cycles(G, length_bound=6)):
            continue
        e = sorted(tuple(sorted(x)) for x in G.edges())
        flat = flat_of(n, e)
        s["graphs"] += 1
        for sizes in itertools.product(*[range(max(3, G.degree(k) + 1), 6) for k in range(n)]):
            c = JD.classify(list(sizes), flat)
            s["starts"] += 1
            s[c] += 1
    return dict(s)


def part_x():
    import job_double as JD
    rows = []
    for line in open(ROOT / "runs/touch-census/results.jsonl"):
        r = json.loads(line)
        if r.get("status") == "ok":
            rows += [a["key"] for a in r["result"]["arrangements"]]
    s = Counter()
    for sizes, flat in rows:
        c = JD.classify(sizes, flat)
        if not in_class(c):
            continue
        s["in the class"] += 1
        n = len(sizes)
        sh = Counter()
        for (a, b), m in zip(itertools.combinations(range(n), 2), flat):
            sh[a] += m
            sh[b] += m
        if any(sizes[k] - sh[k] == 0 for k in range(n)):
            s["with a dead knot"] += 1
            best, _ = most_rays(sizes, flat)
            s[f"with a dead knot, most rays in a piece {best}"] += 1
            continue
        s["no dead knot"] += 1
        best, _ = most_rays(sizes, flat)
        s[f"no dead knot, most rays in a piece {best}"] += 1
    return dict(s)


def cases():
    only = set(PARAMS["only"].split(",")) if PARAMS.get("only") else None
    allc = [("F", {"part": "F"}), ("F6", {"part": "F6"}), ("G", {"part": "G"}), ("C", {"part": "C"}), ("X", {"part": "X"})]
    if PARAMS.get("graphs"):
        for n, gs in json.load(open(PARAMS["graphs"]))["result"]["edge lists"].items():
            for i, e in enumerate(gs):
                allc.append((f"A-{int(n):02d}-{i:03d}", {"part": "A", "n": int(n), "edges": [tuple(x) for x in e]}))
    for cid, p in allc:
        if only is None or cid in only:
            yield cid, p


def run(case_id, p):
    part = p["part"]
    if part == "F":
        return part_f()
    if part == "F6":
        import job_weight as JW
        n, e = family_S(6)
        return {"S_6": grow_family(JW.my_bare(n, flat_of(n, e)), e, 28)}
    if part == "G":
        return part_g()
    if part == "C":
        return part_c()
    if part == "X":
        return part_x()
    return part_a(p["n"], p["edges"])
