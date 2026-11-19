"""Shared-runner job for the referee's check of WALL-READ-20261119-001, with the referee's own code: its EXPLOSIVE-R1 grower (the
program's rule on actual distinctions, maximal-clique groups, structural implied test), its REDUCE-BLOCKS-R1 hub realization and
random starts, and its own partnered-set search.  rosterlib is read, not run.

Parts:
- PART: partnered starts of order n = 2 (ten rounds), 3 (rounds 1-3 built, round 4's groups counted), 4 and 5 (round 1 built,
  round 2's groups counted), each from the referee's own hub realization: per round the (parents, fresh) multiset, and at every
  built stage the form (F1)-(F3): the candidate graph among live junctions is every pair but a perfect matching of complements; the
  maximal blocks number N_(t-1), are transversals of that matching and closed under complement; each point lies in m_(t-1) of them.
  Also the largest place count of a live knot in the realization (8 at n = 3).
- CTRL: n = 3, 4 with open count 2^(n-1) - 1 (stall in round 1) and 2^(n-1) + 1 (2n offshoots in round 1).
- LEM-c: Lemmas 2 and 3 on every stage, rounds 0 to 6, of 1,125 own random starts of 6 to 14 knots within eight places (one past
  the study's seven) and on the 16 explosive starts' stages (rounds 0 to 7, stages of at most 4,000 live junctions), each grown
  in a child (4 GB, 300 s): with the stage's next-round groups listed by the rule, (a) every greedy partnered set of order k >= 2:
  2^k - |B| <= groups; (b) W = all live points and a random W of 12: mc(G[W]) - |B| - l <= groups; (c) every partnered set of
  order 2 to 10 with no outside common candidate: Q(T) the least group holding T meets W in T, complements are disjoint, other pairs
  meet, and the surviving Q(T) number at least 2^(k-1) - |B| pairs.
- B2: start-03's stage 7 grown by the referee's engine: its open sum, round 8's groups by the rule (count, largest), offshoots,
  junctions and parent sum (the study: 28,064 groups, largest 109, 28,065 junctions, 993,164 both ways).

  .venv/bin/python -B scripts/longrun.py launch research/WALL-READ-20261119-001/referee-R1/job_wr.py \\
      --out runs/referee-wr --unit referee-wr --workers 3 --case-timeout 14400 --case-mem 4G --mem-max 13G
"""
import itertools
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for p in ("research/EXPLOSIVE-20261119-001/referee-R1", "research/RING-IDENT-20261119-001/referee-R1",
          "research/FIRST-KNOT-20261118-001/referee-R1", "research/MERGE-BURST-20261119-001/referee-R1",
          "research/REDUCE-BLOCKS-20261119-001/referee-R1"):
    sys.path.insert(0, str(ROOT / p))
PARAMS = {}


def setup(params):
    PARAMS.update(params)


def partnered_start(n, opn=None):
    import job_rb as RB
    live = list(range(2 * n))
    o = 2 ** (n - 1) if opn is None else opn
    blocks = {frozenset((i, j)) for i, j in itertools.combinations(live, 2) if j != i + n}
    A = {"live": live, "open": [o] * (2 * n), "maximal": blocks}
    sizes, edges, lm = RB.realize(A)
    return sizes, edges


def stage_of(G):
    """Live junctions, candidate graph (pairs with a common neighbour), maximal blocks, lone points."""
    import networkx as nx
    live = [j for j in G.live if any(len(G.owner[b]) == 1 for b in G.bits[j])]
    lv = set(live)
    blocks = set()
    for w in range(len(G.bits)):
        B = frozenset(G.nbr[w] & lv)
        if len(B) >= 2:
            blocks.add(B)
    maximal = [B for B in blocks if not any(B < C for C in blocks)]
    C = nx.Graph()
    C.add_nodes_from(live)
    for B in maximal:
        C.add_edges_from(itertools.combinations(sorted(B), 2))
    lone = [v for v in live if C.degree(v) == 0]
    return live, C, maximal, lone


def form(G):
    live, C, maximal, lone = stage_of(G)
    import networkx as nx
    non = [(u, v) for u, v in itertools.combinations(live, 2) if not C.has_edge(u, v)]
    deg = Counter(x for e in non for x in e)
    matching = len(non) * 2 == len(live) and all(deg[v] == 1 for v in live)
    partner = {}
    for u, v in non:
        partner[u], partner[v] = v, u
    trans = matching and all(all(partner[x] not in B for x in B) and 2 * len(B) == len(live) for B in maximal)
    closed = trans and {frozenset(partner[x] for x in B) for B in maximal} == set(maximal)
    inb = Counter(x for B in maximal for x in B)
    return {"live": len(live), "complements are the only non-candidates": matching, "blocks are transversals": trans,
            "blocks closed under complement": closed, "maximal blocks": len(maximal),
            "blocks per point": sorted(set(inb.values()))}


def part_part():
    import job_expl as JX
    import job_ring as JR
    out = {}
    for n, built in ((2, 10), (3, 3), (4, 1), (5, 1)):
        sizes, edges = partnered_start(n)
        G = JX.grower(JR.stars_of(len(sizes), edges, list(sizes)))
        live0 = [j for j in range(len(sizes)) if sizes[j] > sum(1 for e in edges if j in e)]
        row = {"knots, largest live place count": [len(sizes), max(sizes[j] for j in live0)], "rounds": []}
        for t in range(1, built + 1):
            r = G.step(JX.floored, None, None)
            if r != "ok":
                row["rounds"].append(r)
                break
            born = [j for j in range(len(G.bits)) if G.round[j] == t]
            row["rounds"].append({"t": t, "count": len(born),
                                  "(parents, fresh)": sorted(Counter((len(G.parents[j]), G.fresh[j]) for j in born).items()),
                                  "form": form(G)})
        live, C, maximal, lone = stage_of(G)
        row["next round's groups by the rule"] = len(G.groups(live, None))
        out[f"n = {n}"] = row
    return json.loads(json.dumps(out, default=str))


def part_ctrl():
    import job_expl as JX
    import job_ring as JR
    out = {}
    for n in (3, 4):
        for d in (-1, 1):
            sizes, edges = partnered_start(n, 2 ** (n - 1) + d)
            G = JX.grower(JR.stars_of(len(sizes), edges, list(sizes)))
            r = G.step(JX.floored, None, None)
            born = [j for j in range(len(G.bits)) if G.round[j] == 1]
            out[f"n = {n}, open {2 ** (n - 1) + d}"] = {"round 1": r, "offshoots": sum(1 for j in born if len(G.parents[j]) == 1)}
    return out


def partnered_sets(C, live, seeds, rng):
    """Greedy partnered sets (induced cocktail-party subgraphs): from a seed non-candidate pair, repeatedly add a non-candidate
    pair inside the common candidates of all chosen points.  Returns a list of (pairs) found, largest first."""
    nbr = {v: set(C[v]) for v in live}
    lv = list(live)
    non = []
    tries = 0
    found = []
    while len(found) < seeds and tries < seeds * 20:
        tries += 1
        u = rng.choice(lv)
        others = [v for v in lv if v != u and v not in nbr[u]]
        if not others:
            continue
        v = rng.choice(others)
        pairs = [(u, v)]
        common = nbr[u] & nbr[v]
        while True:
            cand = sorted(common)
            rng.shuffle(cand)
            added = False
            for a in cand:
                rest = [b for b in common if b != a and b not in nbr[a]]
                if rest:
                    b = rest[0]
                    pairs.append((a, b))
                    common = common & nbr[a] & nbr[b]
                    added = True
                    break
            if not added:
                break
        found.append(pairs)
    found.sort(key=len, reverse=True)
    return found


def check_stage(G, rng):
    import networkx as nx
    live, C, maximal, lone = stage_of(G)
    if len(live) < 2 or len(live) > 4000:
        return None
    groups = G.groups(live, None)
    ng = len(groups)
    nB, l = len(maximal), len(lone)
    s = Counter()
    bad = []
    # (b) W = all live points, and a random W of 12
    mcall = sum(1 for _ in nx.find_cliques(C))
    s["lemma 2, W = all live: checked"] += 1
    s["lemma 2, W = all live: held"] += mcall - nB - l <= ng
    W = rng.sample(live, min(12, len(live)))
    mcw = sum(1 for _ in nx.find_cliques(C.subgraph(W)))
    s["lemma 2, random W of 12: checked"] += 1
    s["lemma 2, random W of 12: held"] += mcw - nB - l <= ng
    if mcw - nB - l > ng or mcall - nB - l > ng:
        bad.append(["lemma 2", len(live), mcall, mcw, nB, l, ng])
    # (a) and (c) partnered sets
    gs = [frozenset(g) for g in groups]
    nbr = {v: set(C[v]) for v in live}
    for pairs in partnered_sets(C, live, 30, rng):
        k = len(pairs)
        s[f"largest partnered order seen"] = max(s["largest partnered order seen"], k)
        if k < 2:
            continue
        s["lemma 2, partnered: checked"] += 1
        s["lemma 2, partnered: held"] += 2 ** k - nB <= ng
        if 2 ** k - nB > ng:
            bad.append(["lemma 2 partnered", k, nB, ng])
        Wset = {x for p in pairs for x in p}
        outside = [z for z in live if z not in Wset and Wset <= nbr[z]]
        if outside or k > 10:
            continue
        s["lemma 3: checked"] += 1
        ok = True
        Q = {}
        for choice in itertools.product((0, 1), repeat=k):
            T = frozenset(p[c] for p, c in zip(pairs, choice))
            if any(T <= B for B in maximal):
                continue
            hold = sorted((g for g in gs if T <= g), key=lambda g: sorted(g))
            if not hold:
                ok = False
                break
            Q[T] = hold[0]
            if Q[T] & Wset != T:
                ok = False
        alive = 0
        for choice in itertools.product((0, 1), repeat=k):
            if choice[0] == 1:
                continue
            T = frozenset(p[c] for p, c in zip(pairs, choice))
            Tc = frozenset(p[1 - c] for p, c in zip(pairs, choice))
            if T in Q and Tc in Q:
                alive += 1
                if Q[T] & Q[Tc]:
                    ok = False
        for T1, T2 in itertools.combinations(list(Q), 2):
            if T1 & T2 and not (Q[T1] & Q[T2]):
                ok = False
        ok = ok and alive >= 2 ** (k - 1) - nB
        s["lemma 3: held"] += ok
        if not ok:
            bad.append(["lemma 3", k, nB])
    return s, bad


def lem_child(conn, sizes, edges, rounds, seed):
    import resource
    import job_expl as JX
    import job_ring as JR
    resource.setrlimit(resource.RLIMIT_AS, (4_000_000_000, 4_000_000_000))
    rng = random.Random(seed)
    G = JX.grower(JR.stars_of(len(sizes), list(edges), list(sizes)))
    for t in range(rounds + 1):
        r = check_stage(G, rng)
        if r is not None:
            conn.send(("stage", t, dict(r[0]), r[1]))
        if t == rounds or G.step(JX.floored, None, None) != "ok":
            break
    conn.send(("done", None, None, None))


def follow(sizes, edges, rounds, seed, seconds=300):
    import multiprocessing as mp
    import time
    ctx = mp.get_context("fork")
    a, b = ctx.Pipe(duplex=False)
    pr = ctx.Process(target=lem_child, args=(b, sizes, edges, rounds, seed))
    pr.start()
    b.close()
    s, bad, stages, end = Counter(), [], 0, "memory"
    t0 = time.time()
    while time.time() - t0 < seconds:
        if a.poll(0.5):
            try:
                kind, t, c, bd = a.recv()
            except EOFError:
                break
            if kind == "done":
                end = "done"
                break
            stages += 1
            for k, v in c.items():
                if k == "largest partnered order seen":
                    s[k] = max(s[k], v)
                else:
                    s[k] += v
            bad += bd
            continue
        if not pr.is_alive() and not a.poll(0):
            break
    else:
        end = "time"
    pr.kill()
    pr.join(5)
    return s, bad, stages, end


def part_lem(c):
    import job_rb as RB
    import job_mb as MB
    tot, bad = Counter(), []
    ends = Counter()
    if c < 9:
        n = 6 + c
        rng = random.Random(f"referee-wr-{n}")
        for i in range(125):
            sizes, e = RB.sample(n, rng, P=8)
            s, b, st, end = follow(sizes, e, 6, f"{n}-{i}")
            for k, v in s.items():
                tot[k] = max(tot[k], v) if k == "largest partnered order seen" else tot[k] + v
            tot["stages"] += st
            ends[end] += 1
            bad += b
    else:
        for i, x in enumerate(MB.population()):
            s, b, st, end = follow(x["sizes"], x["edges"], 7, f"explosive-{i}", seconds=600)
            for k, v in s.items():
                tot[k] = max(tot[k], v) if k == "largest partnered order seen" else tot[k] + v
            tot["stages"] += st
            ends[end] += 1
            bad += b
    return {"counts": dict(tot), "ends": dict(ends), "failures": bad[:10]}


def part_b2():
    import resource
    import job_expl as JX
    import job_ring as JR
    import job_mb as MB
    resource.setrlimit(resource.RLIMIT_AS, (9_000_000_000, 9_000_000_000))
    x = MB.population()[3]
    G = JX.grower(JR.stars_of(len(x["sizes"]), x["edges"], list(x["sizes"])))
    for t in range(7):
        assert G.step(JX.floored, None, None) == "ok"
    live, C, maximal, lone = stage_of(G)
    born = [j for j in range(len(G.bits)) if G.round[j] == 7]
    groups = G.groups(live, None)
    use = Counter(v for g in groups for v in g)
    opn = {j: G.fresh[j] for j in born}
    off = sum(opn[j] - use[j] for j in live)
    return {"start": x["sizes"], "round 7 junctions, open sum": [len(born), sum(opn.values())],
            "round 8: groups by the rule, largest, three or more parents": [len(groups), max(len(g) for g in groups),
                                                                           sum(1 for g in groups if len(g) >= 3)],
            "round 8: offshoots, junctions, parent sum": [off, len(groups) + off, sum(len(g) for g in groups) + off],
            "a stall": any(use[j] > opn[j] for j in live)}


def cases():
    only = set(PARAMS["only"].split(",")) if PARAMS.get("only") else None
    allc = [("PART", {"part": "PART"}), ("CTRL", {"part": "CTRL"}), ("B2", {"part": "B2"})]
    allc += [(f"LEM-{c:02d}", {"part": "LEM", "c": c}) for c in range(10)]
    for cid, p in allc:
        if only is None or cid in only:
            yield cid, p


def run(case_id, p):
    k = p["part"]
    if k == "PART":
        r = part_part()
    elif k == "CTRL":
        r = part_ctrl()
    elif k == "B2":
        r = part_b2()
    else:
        r = part_lem(p["c"])
    return json.loads(json.dumps(r, default=lambda o: int(o) if hasattr(o, "__int__") else str(o)))
