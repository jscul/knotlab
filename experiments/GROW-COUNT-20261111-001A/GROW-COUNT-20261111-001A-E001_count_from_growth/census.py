"""The frozen census of GROW-COUNT-20261111-001A-E001 (contract.json beside this file): the count from growth.

A world of knots alone grows from one knot by adding knots {x, y, z} on a co-knotted pair {x, y}, the third distinction z existing
or new, a move accepted only if the not-all-equal law (NAE) still reads the world faithfully. Three rules, naming more and more of
the count of how knots meet (A64):
  free  names nothing: any co-knotted pair, any z.
  open  names "two knots per pair": only pairs in one knot, and every pair must stay in at most two.
  disc  names that too and "one link per distinction": every link must stay a single path or a single cycle.
None names a degree. Each run records the pairs in three or more knots, pinched links, and the degrees of closed distinctions.

Run from the repository root:
    .venv/bin/python -B experiments/GROW-COUNT-20261111-001A/GROW-COUNT-20261111-001A-E001_count_from_growth/census.py
Output: artifacts/GROW-COUNT-20261111-001A/GROW-COUNT-20261111-001A-E001_count_from_growth/census.json and census_log.txt.
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

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
LIB = os.path.join(ROOT, "experiments", "KNOTS-ALONE-20261111-001A", "KNOTS-ALONE-20261111-001A-E001_knots_alone_census")
LIB_SHA = "aee9a2eda0907064b89eae4fe4badddb22b80fecb62bd91d5a5fa448397010de"
sys.path.insert(0, LIB)
import knots_alone as ka  # noqa: E402

CONTROL = "--control" in sys.argv
OUT = os.path.join(ROOT, "artifacts", "GROW-COUNT-20261111-001A", "GROW-COUNT-20261111-001A-E001_count_from_growth")
if CONTROL:
    OUT = sys.argv[sys.argv.index("--control") + 1]

# Frozen parameters (contract.json, "definitions")
RULES = ("free", "open", "disc")
CLOSE_BIAS = (0.3, 0.6, 0.9)     # probability that a proposed move uses an existing third distinction
SEEDS = range(10)
N_KNOTS = 80                     # stop when the world has this many knots
MAX_TRIES = 400                  # or after this many rejected proposals in a row (a stall)
LAWS_RUN = ("NAE", "OR")         # NAE under test; OR (accepts every move, ka D4) as the frozen comparison
WORKERS = 12


def log(msg):
    print(msg, flush=True)
    with open(os.path.join(OUT, "census_log.txt"), "a") as f:
        f.write(msg + "\n")


class World:
    def __init__(self):
        self.V = 3
        self.knots = {(0, 1, 2)}
        self.mult = Counter({(0, 1): 1, (0, 2): 1, (1, 2): 1})

    def pairs(self, lam=None):
        return [p for p, m in self.mult.items() if lam is None or m == lam]

    def add(self, t):
        self.knots.add(t)
        for e in itertools.combinations(t, 2):
            self.mult[e] += 1
        self.V = max(self.V, max(t) + 1)

    def remove(self, t):
        self.knots.discard(t)
        for e in itertools.combinations(t, 2):
            self.mult[e] -= 1
            if self.mult[e] == 0:
                del self.mult[e]

    def link_components(self, v):
        """Components of v's link as (number of components, every link vertex of degree <= 2, is a single cycle)."""
        adj = defaultdict(set)
        for t in self.knots:
            if v in t:
                a, b = [x for x in t if x != v]
                adj[a].add(b)
                adj[b].add(a)
        if not adj:
            return 0, True, False
        seen, comps = set(), 0
        for s in adj:
            if s in seen:
                continue
            comps += 1
            stack = [s]
            while stack:
                u = stack.pop()
                if u in seen:
                    continue
                seen.add(u)
                stack.extend(adj[u] - seen)
        maxdeg = max(len(n) for n in adj.values())
        cycle = comps == 1 and all(len(n) == 2 for n in adj.values())
        return comps, maxdeg <= 2, cycle


def legal(world, t, rule):
    if t in world.knots or len(set(t)) < 3:
        return False
    if rule == "free":
        return True
    if any(world.mult.get(e, 0) >= 2 for e in itertools.combinations(t, 2)):
        return False
    if rule == "open":
        return True
    world.add(t)
    ok = all(world.link_components(v)[0] <= 1 and world.link_components(v)[1] for v in t)
    world.remove(t)
    return ok


def faithful(world, law):
    T = sorted(world.knots)
    return bool(ka.read_law_sat(world.V, T, ka.LAWS[law]).get("faithful"))


def closings(world, t):
    """Degrees of the links that adding t would close into a single cycle."""
    before = {v: world.link_components(v)[2] for v in t}
    world.add(t)
    out = [sum(1 for k in world.knots if v in k) for v in t if world.link_components(v)[2] and not before[v]]
    world.remove(t)
    return out


def grow(args):
    rule, bias, seed, law = args
    rng = random.Random(1000 * RULES.index(rule) + 100 * CLOSE_BIAS.index(bias) + seed + 20261115)
    closed_ok, closed_no = Counter(), Counter()
    w = World()
    tries, accepted, rejected_faithful, rejected_rule = 0, 0, 0, 0
    while len(w.knots) < N_KNOTS and tries < MAX_TRIES:
        tries += 1
        pool = w.pairs(1) if rule in ("open", "disc") else w.pairs()
        if not pool:
            break
        x, y = rng.choice(sorted(pool))
        if rng.random() < bias and w.V > 3:
            z = rng.randrange(w.V)
        else:
            z = w.V
        t = tuple(sorted((x, y, z)))
        if not legal(w, t, rule):
            rejected_rule += 1
            continue
        would_close = closings(w, t)
        w.add(t)
        if faithful(w, law):
            accepted += 1
            tries = 0
            closed_ok.update(would_close)
        else:
            w.remove(t)
            rejected_faithful += 1
            closed_no.update(would_close)
    T = sorted(w.knots)
    V = w.V
    mult = Counter(w.mult.values())
    closed, pinched, branching = [], 0, 0
    for v in range(V):
        comps, ok, cycle = w.link_components(v)
        if comps > 1:
            pinched += 1
        if not ok:
            branching += 1
        if cycle:
            closed.append(sum(1 for t in T if v in t))
    return {"rule": rule, "bias": bias, "seed": seed, "law": law, "V": V,
            "closings accepted by degree": dict(sorted(closed_ok.items())), "closings rejected by degree": dict(sorted(closed_no.items())), "knots": len(T), "stalled": len(T) < N_KNOTS,
            "pairs by count": dict(sorted(mult.items())), "pinched links": pinched, "branching links": branching,
            "closed degrees": dict(sorted(Counter(closed).items())), "accepted": accepted,
            "rejected by faithfulness": rejected_faithful, "rejected by rule": rejected_rule,
            "closed surface": ka.is_surface(V, T), "euler": ka.euler(V, T), "faithful at end": faithful(w, law), "T": [list(t) for t in T]}


def main():
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, "census_log.txt"), "w").close()
    t0 = time.time()
    have = hashlib.sha256(open(os.path.join(LIB, "knots_alone.py"), "rb").read()).hexdigest()
    log(f"library hash matches: {have == LIB_SHA}")
    if have != LIB_SHA:
        raise SystemExit("library changed")
    if CONTROL:
        # outside the family: two seeds past the registered ones, both laws
        jobs = [(r, 0.6, s, law) for r in RULES for s in (98, 99) for law in LAWS_RUN]
    else:
        jobs = [(r, b, s, law) for r in RULES for b in CLOSE_BIAS for s in SEEDS for law in LAWS_RUN]
    with Pool(WORKERS) as pool:
        runs = pool.map(grow, jobs, chunksize=1)
    registered = sorted((r, b, s, law) for r in RULES for b in CLOSE_BIAS for s in SEEDS for law in LAWS_RUN)
    coverage = sorted((r["rule"], r["bias"], r["seed"], r["law"]) for r in runs) == registered
    log(f"every registered run ran: {coverage}")
    summary = {"coverage": coverage}
    for rule, law in itertools.product(RULES, LAWS_RUN):
        rs = [r for r in runs if r["rule"] == rule and r["law"] == law]
        deg, cok, cno = Counter(), Counter(), Counter()
        for r in rs:
            deg.update({int(k): v for k, v in r["closed degrees"].items()})
            cok.update({int(k): v for k, v in r["closings accepted by degree"].items()})
            cno.update({int(k): v for k, v in r["closings rejected by degree"].items()})
        summary[f"{rule} {law}"] = {"closings accepted by degree": dict(sorted(cok.items())),
            "closings rejected by degree": dict(sorted(cno.items())),
            "runs": len(rs), "stalled": sum(r["stalled"] for r in rs),
            "runs with pairs in three or more knots": sum(1 for r in rs if any(int(k) >= 3 for k in r["pairs by count"])),
            "runs with pinched links": sum(1 for r in rs if r["pinched links"]),
            "closed degrees (all runs)": dict(sorted(deg.items())),
            "runs where degree 6 is at least 90% of closed distinctions": sum(
                1 for r in rs if r["closed degrees"] and r["closed degrees"].get(6, 0) >= 0.9 * sum(r["closed degrees"].values())),
            "closed surfaces": sum(r["closed surface"] for r in rs),
            "flat closed surfaces": sum(1 for r in rs if r["closed surface"] and r["euler"] == 0),
            "faithful at end": sum(r["faithful at end"] for r in rs),
            "rejected by faithfulness": sum(r["rejected by faithfulness"] for r in rs),
            "accepted": sum(r["accepted"] for r in rs)}
    s = summary
    s["P1"] = {"holds": s["free NAE"]["runs with pairs in three or more knots"] == s["free NAE"]["runs"] > 0}
    s["P2"] = {"holds": s["open NAE"]["runs with pinched links"] > 0}
    disc_deg = s["disc NAE"]["closed degrees (all runs)"]
    s["P3"] = {"holds": len([d for d, n in disc_deg.items() if n > 0]) >= 3
               and s["disc NAE"]["runs where degree 6 is at least 90% of closed distinctions"] == 0}
    s["P4"] = {"holds": s["disc NAE"]["flat closed surfaces"] == 0}
    s["seconds"] = round(time.time() - t0, 1)
    log(json.dumps(s, indent=1, default=str))
    with open(os.path.join(OUT, "census.json"), "w") as f:
        json.dump({"summary": s, "runs": runs}, f, default=str)


if __name__ == "__main__":
    main()
