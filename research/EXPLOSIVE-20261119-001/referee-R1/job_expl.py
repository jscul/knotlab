"""Shared-runner job for the referee's check of EXPLOSIVE-20261119-001 (framed under A110: what a sample of this kind shows).

Own code: the referee's FIRST-KNOT-R1 engine with the program's rule, the implied test read structurally (a connected start: a
junction is implied exactly when it takes every loose distinction), and its round's groups found as the maximal cliques of the
candidate graph (Bron-Kerbosch with pivoting, networkx) that have no common neighbour, plus the candidate pairs in none of them.
That is the same rule as the clique search of the referee's earlier engine (a maximal clique containing a valid set is itself
valid), but it reaches groups of hundreds.  Each start grows in its own child process with an address-space limit and a time limit;
the rounds stream back, so a stopped child keeps them.  The study's starts and records are read from runs/explosive as data; none
of its code is run.

Parts:
- E (one case per explosive start of the run, cap7 and ref): grown to round 40, or 150,000 junctions, or the child's limits.
- F (one case per X1 failure of cap7): the same.
- R (the filled reading, chunks of the 3,200 starts): the referee's own round-1 groups, demand, blocks, filled map over GF(2) and
  reading, against the study's recorded reading.
- L (a sample of 400 decided starts, every eighth by crc32): grown to round 40 or 30,000 junctions; the study's class rule applied
  to the referee's counts at 20 rounds and at 40; whether the class changes with the horizon.

  .venv/bin/python -B scripts/longrun.py launch research/EXPLOSIVE-20261119-001/referee-R1/job_expl.py \\
      --out runs/referee-explosive --unit referee-explosive --workers 2 --case-timeout 3600 --case-mem 7G --mem-max 15G
"""
import itertools
import json
import sys
import zlib
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for p in ("research/RING-IDENT-20261119-001/referee-R1", "research/FIRST-KNOT-20261118-001/referee-R1",
          "research/DOUBLE-IDENT-20261119-001/referee-R1", "research/RELAY-IDENT-20261119-001/referee-R1",
          "research/CHAIN-IDENT-20261119-001/referee-R1", "research/TOUCH-CENSUS-20261118-001/referee-R1"):
    sys.path.insert(0, str(ROOT / p))
PARAMS = {}
CHILD_AS = 4_500_000_000
CHILD_SECONDS = 240


def setup(params):
    PARAMS.update(params)


def floored(G, info, rng):
    return [i["d"] if i["implied"] else max(i["d"], 3 - i["p"], 1) for i in info]


def grower(stars):
    import networkx as nx
    import referee_first as RFK

    class Fast(RFK.Start):
        def _add(self, j):
            pass

        def _reduce(self, x):
            return 0 if x == self._loose0 else x

        def groups(self, live, cap):
            lv = set(live)
            G = nx.Graph()
            G.add_nodes_from(lv)
            for w in range(len(self.bits)):
                ln = [u for u in self.nbr[w] if u in lv]
                G.add_edges_from(itertools.combinations(sorted(ln), 2))
            valid = []
            for C in nx.find_cliques(G):
                if len(C) < 3:
                    continue
                common = set.intersection(*(self.nbr[u] for u in C))
                if not common:
                    valid.append(frozenset(C))
            covered = set()
            for C in valid:
                for p in itertools.combinations(sorted(C), 2):
                    covered.add(p)
            pairs = [frozenset(e) for e in G.edges() if tuple(sorted(e)) not in covered]
            return valid + pairs

        def step(self, rule, cap=None, rng=None):
            self._loose0 = sum(1 << b for b, js in self.owner.items() if len(js) == 1)
            return super().step(rule, cap, rng)
    return Fast(stars)


def _child(conn, sizes, edges, rounds, maxj):
    import resource
    import job_ring as JR
    resource.setrlimit(resource.RLIMIT_AS, (CHILD_AS, CHILD_AS))
    G = grower(JR.stars_of(len(sizes), edges, list(sizes)))
    for t in range(1, rounds + 1):
        r = G.step(floored, None, None)
        if r != "ok":
            conn.send((r, None, None))
            return
        born = [j for j in range(len(G.bits)) if G.round[j] == t]
        conn.send(("round", len(born), max(len(G.parents[j]) for j in born)))
        if len(G.bits) > maxj:
            conn.send(("cap", None, None))
            return
    conn.send(("alive", None, None))


def grow(sizes, edges, rounds, maxj, seconds=CHILD_SECONDS):
    import multiprocessing as mp
    import time
    ctx = mp.get_context("fork")
    a, b = ctx.Pipe(duplex=False)
    pr = ctx.Process(target=_child, args=(b, sizes, edges, rounds, maxj))
    pr.start()
    b.close()
    counts, groups, outcome = [len(sizes)], [1], "resource"
    t0 = time.time()
    while True:
        if a.poll(1.0):
            try:
                kind, c, g = a.recv()
            except EOFError:
                break
            if kind == "round":
                counts.append(c)
                groups.append(g)
                continue
            outcome = kind
            if kind == "closed":
                counts.append(0)
                groups.append(0)
            break
        if not pr.is_alive() and not a.poll(0):
            break
        if time.time() - t0 > seconds:
            pr.kill()
            outcome = "resource (time)"
            break
    pr.join(5)
    if pr.is_alive():
        pr.kill()
    return {"outcome": outcome, "counts": counts, "groups": groups}


def measured(outcome, c):
    """The study's class rule as its pre-registration states it, applied to the referee's counts."""
    if outcome == "closed":
        return "closes"
    if outcome == "stall":
        return "stall"
    body = c[1:]
    for D in range(1, 9):
        for q in (1, 2, 3):
            dd = body
            for _ in range(D):
                dd = [dd[i + q] - dd[i] for i in range(len(dd) - q)]
            need = max(4, D + 3)
            if len(dd) >= need and all(v == 0 for v in dd[-need:]):
                return f"dimension {D}" + ("" if q == 1 else f" (period {q})")
    rat = [c[i + 1] / c[i] for i in range(len(c) - 1) if c[i]]
    if any(r >= 3 for r in rat[3:]):
        return "explosive"
    last = rat[-5:]
    if len(last) == 5:
        m = sum(last) / 5
        if m > 1.05 and all(abs(r - m) <= 0.15 * m for r in last):
            return "exponential-like"
    return "undecided"


def records():
    rows = []
    for line in open(ROOT / "runs/explosive/results.jsonl"):
        r = json.loads(line)
        for x in r["result"]["starts"]:
            x["case"] = r["case"]
            rows.append(x)
    return rows


def my_reading(sizes, edges):
    """The filled reading from the referee's own round-1 groups and filled map."""
    import job_ring as JR
    n = len(sizes)
    G = grower(JR.stars_of(n, edges, list(sizes)))
    sh = Counter()
    nb = defaultdict(set)
    for a, b in edges:
        sh[a] += 1
        sh[b] += 1
        nb[a].add(b)
        nb[b].add(a)
    opn = [sizes[k] - sh[k] for k in range(n)]
    live = [k for k in range(n) if opn[k] >= 1]
    groups = G.groups(live, None)
    d = Counter(x for g in groups for x in g)
    ls = set(live)
    blocks = {w: frozenset(nb[w] & ls) for w in range(n) if len(nb[w] & ls) >= 2}
    of = defaultdict(set)
    for w, B in blocks.items():
        for k in B:
            of[k].add(w)
    # cycles of three blocks
    cells = []
    for x, y, z in itertools.combinations(sorted(of), 3):
        a, b, c = of[x] & of[y], of[y] & of[z], of[z] & of[x]
        if a and b and c and not (of[x] & of[y] & of[z]):
            for wa, wb, wc in itertools.product(sorted(a), sorted(b), sorted(c)):
                if len({wa, wb, wc}) == 3:
                    cells.append(((x, wa), (y, wa), (y, wb), (z, wb), (z, wc), (x, wc)))
    # pieces of the incidence graph
    parent = {}

    def find(u):
        while parent.setdefault(u, u) != u:
            u = parent[u]
        return u
    edges_inc = [(("p", k), ("b", w)) for w, B in blocks.items() for k in B]
    for u, v in edges_inc:
        parent[find(u)] = find(v)
    comps = defaultdict(lambda: {"pts": set(), "edges": [], "nodes": set()})
    for k in live:
        comps[find(("p", k))]["pts"].add(k)
        comps[find(("p", k))]["nodes"].add(("p", k))
    for u, v in edges_inc:
        c = comps[find(u)]
        c["edges"].append((u, v))
        c["nodes"] |= {u, v}
    out = []
    for c in comps.values():
        idx = {frozenset(e): i for i, e in enumerate(c["edges"])}
        rank_graph = len(c["edges"]) - len(c["nodes"]) + 1
        basis = {}
        r = 0
        for cell in cells:
            if ("p", cell[0][0]) not in c["nodes"]:
                continue
            m = 0
            for (k, w) in cell:
                m ^= 1 << idx[frozenset((("p", k), ("b", w)))]
            while m:
                h = m.bit_length() - 1
                if h in basis:
                    m ^= basis[h]
                else:
                    basis[h] = m
                    r += 1
                    break
        rays = sum((opn[k] - d[k]) * {1: 2, 2: 1}.get(opn[k], 0) for k in c["pts"])
        out.append((rank_graph - r, rays))
    if any(b1 > 0 for b1, _ in out):
        return "cycle left"
    many = len(out) >= 2
    D = max((r if r else (2 if many else 0)) for _, r in out) if out else 0
    return "closes" if D == 0 else f"dimension {D}"


def cases():
    only = set(PARAMS["only"].split(",")) if PARAMS.get("only") else None
    rows = records()
    allc = []
    ex = [x for x in rows if x["measured"] == "explosive"]
    for i, x in enumerate(ex):
        allc.append((f"E-{i:02d}", {"part": "E", "start": x}))
    fails = [x for x in rows if x["tag"] == "cap7" and all(b == 0 for b in x["b1"]) and x["measured"] != "undecided" and
             x["reading"] != x["measured"]]
    for i, x in enumerate(fails):
        if x["measured"] != "explosive":          # the explosive ones are the E cases
            allc.append((f"F-{i:02d}", {"part": "F", "start": x}))
    for a in range(0, len(rows), 400):
        allc.append((f"R-{a // 400:02d}", {"part": "R", "lo": a, "hi": a + 400}))
    dec = [x for x in rows if x["measured"] not in ("undecided", "explosive") and zlib.crc32(repr(x["edges"]).encode()) % 8 == 0]
    for a in range(0, min(len(dec), 400), 50):
        allc.append((f"L-{a // 50:02d}", {"part": "L", "starts": dec[a:a + 50]}))
    for cid, p in allc:
        if only is None or cid in only:
            yield cid, p


def run(case_id, p):
    if p["part"] in ("E", "F"):
        x = p["start"]
        g = grow(x["sizes"], [tuple(e) for e in x["edges"]], 40, 150000)
        return {"study": {k: x[k] for k in ("case", "tag", "sizes", "edges", "reading", "measured", "outcome", "counts", "groups",
                                            "overlap_point", "overlap_block", "b1")},
                "referee": g, "referee's class at the study's 20 rounds": measured("alive", g["counts"][:21]) if len(g["counts"]) > 21 else None,
                "referee's class": measured(g["outcome"], g["counts"]),
                "counts agree with the study's on common rounds": g["counts"][:len(x["counts"])] == x["counts"][:len(g["counts"])]}
    if p["part"] == "R":
        rows = records()[p["lo"]:p["hi"]]
        s = Counter()
        bad = []
        for x in rows:
            r = my_reading(x["sizes"], [tuple(e) for e in x["edges"]])
            s["starts"] += 1
            s["reading equals the study's"] += r == x["reading"]
            if r != x["reading"]:
                bad.append([x["sizes"], x["edges"], r, x["reading"]])
        return {"counts": dict(s), "differ": bad[:10]}
    out = []
    for x in p["starts"]:
        g = grow(x["sizes"], [tuple(e) for e in x["edges"]], 40, 30000, seconds=300)
        c20 = measured("closed" if g["outcome"] == "closed" and len(g["counts"]) <= 22 else "alive", g["counts"][:21])
        out.append({"tag": x["tag"], "study": x["measured"], "referee at 20": c20, "referee at 40": measured(g["outcome"], g["counts"]),
                    "outcome": g["outcome"], "rounds": len(g["counts"]) - 1,
                    "agree on common rounds": g["counts"][:len(x["counts"])] == x["counts"][:len(g["counts"])]})
    return {"rows": out}
