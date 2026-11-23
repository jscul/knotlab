"""Shared code for REVIEW-LEADS-20261123-001A-E001 (the operator test read on every stage of growth).

Frozen definitions: research/REVIEW-LEADS-20261123-001A/preregistration.md.  Nothing here changes a definition.

Recorded code that is reused (imported or copied, source named at each use):
  * the ordinary growth engine `end_operator.step` (ORDINARY-DYNAMICS-20261120-001A), both knot laws;
  * the recorded sources and the labelled-tree sampler (GENERATORS-20261120-001A, READS-HOLDERS-SOURCES-20261120-001C,
    CALIBRATIONS-CLOCKS-AND-WIDER-KNOTS-20261120-001B, FOUR-READINGS-20261120-001A, HEAVY-GROWTH-20261119-001 archive);
  * the shape benchmark constructors (GROWTH-STATISTICS-20261121-001A `sources.py`);
  * the independent signed-operator solver `pauli_solution` (FOUR-READINGS-20261120-001A `census.py`).
"""
import importlib.util
import json
import random
import sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TICKET = HERE.parent.name
OUT = ROOT / "artifacts" / TICKET / HERE.name
EXP = ROOT / "experiments"
ORDINARY = EXP / "ORDINARY-DYNAMICS-20261120-001A/ORDINARY-DYNAMICS-20261120-001A-E001_ordinary"
sys.path.insert(0, str(ORDINARY))
import end_operator as EO  # noqa: E402  (the recorded ordinary growth engine; both laws)

LAWS = ("parity", "nae")
P3_SEED = 2026112301
REWIRE_SEEDS = tuple(range(2026112310, 2026112318))
ARCHIVE_JSON = ROOT / "artifacts/HEAVY-GROWTH-20261119-001/HEAVY-GROWTH-20261119-001-E001_checks/sources_audit.json"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# --------------------------------------------------------------------------------------------------------------------------
# Sources.  A source is a tuple of stars; a star is the tuple of distinctions one knot holds.
# --------------------------------------------------------------------------------------------------------------------------
def source_from(meetings, opens):
    """GENERATORS-20261120-001A fixtures.source_from: meeting distinctions first, then each knot's loose ones."""
    stars = [[] for _ in opens]
    for d, (left, right) in enumerate(meetings):
        stars[left].append(d)
        stars[right].append(d)
    top = len(meetings)
    for row, count in zip(stars, opens, strict=True):
        row.extend(range(top, top + count))
        top += count
    return tuple(map(tuple, stars))


def seven_knot_source():
    """research/GENERATORS-20261120-001/source.md, 'The seven-knot construction'; links as in small_periodic.physical."""
    links = [(0, 1), (0, 4), (1, 4), (2, 4), (2, 6), (3, 4), (3, 5), (5, 6), (0, 1)]
    return source_from(links, (3, 0, 3, 3, 3, 2, 2))


def nine_knot_source():
    """research/READS-HOLDERS-SOURCES-20261120-001C/proof.md, 'Physical examples at the upper bound'."""
    pairs = [(0, 2), (0, 3), (0, 5), (1, 2), (2, 7), (3, 8), (4, 5), (4, 8), (5, 6), (6, 7)]
    return source_from(pairs, (5, 2, 4, 3, 3, 4, 3, 3, 2))


def twenty_one_knot_source():
    """GENERATORS-20261120-001A periodic.frame('meeting'): nine points and twelve exhausted witnesses (21 knots, 60 distinctions)."""
    a = ("v", "r1", "r2", "r3")
    arcs = list(zip(a, a[1:] + a[:1])) + [("v", "s"), ("t", "v"), ("s", "b0"), ("t", "b0"), ("s", "b1"), ("b1", "t"),
                                          ("t", "b2"), ("b2", "s")]
    links, opens = [], Counter()
    for i, (p, q) in enumerate(arcs):
        w = f"w{i}"
        links.extend([(p, w), (q, w), (q, w)])
        opens.update([p, q])
    names = sorted({s for edge in links for s in edge})
    idx = {p: i for i, p in enumerate(names)}
    return source_from([(idx[p], idx[q]) for p, q in links], [opens.get(p, 0) for p in names])


def five_founder_clock():
    """CALIBRATIONS-CLOCKS-AND-WIDER-KNOTS-20261120-001B phase_clocks.source_cases()['five_odd']."""
    five = [(0, 1, 2), (1, 2, 1), (2, 3, 1), (3, 4, 1), (4, 0, 3)]
    rows = [[] for _ in range(5)]
    distinction = 0
    for a, b, multiplicity in five:
        for _ in range(multiplicity):
            rows[a].append(distinction)
            rows[b].append(distinction)
            distinction += 1
    for knot in range(5):
        rows[knot].extend((distinction, distinction + 1))
        distinction += 2
    return tuple(map(tuple, rows))


def archived_start(name):
    """HEAVY-GROWTH-20261119-001 archive, as stars_from(sizes, meetings) in FOUR-READINGS-20261120-001A growth.ordinary()."""
    r = json.loads(ARCHIVE_JSON.read_text())["named_archive_starts"][name]
    sizes, meetings = r["sizes"], [tuple(m) for m in r["meetings"]]
    degree = Counter(k for pair in meetings for k in pair)
    stars = source_from(meetings, [s - degree[k] for k, s in enumerate(sizes)])
    return stars, r


def recorded_sources():
    out = {
        "seven_knot": seven_knot_source(),
        "nine_knot_drawn": nine_knot_source(),
        "knots21_two_clocks": twenty_one_knot_source(),
        "five_founder_clock": five_founder_clock(),
    }
    for name in ("start-00", "start-04", "start-13"):
        out["archive_" + name] = archived_start(name)[0]
    return out


def p3_draws(seed=P3_SEED, per_arm=256):
    """Fresh draws: sizes 4..8 with equal weight, a uniform labelled tree (Pruefer word), each knot filled to three places
    plus one more loose distinction with chance 1/4, and 0, 1, 2, 3 uniform extra meetings (distinct unused pairs).
    The sampler follows READS-HOLDERS-SOURCES-20261120-001C survey.draw_specs / GENERATORS sample.source_draws."""
    rng = random.Random(seed)
    for arm in (0, 1, 2, 3):
        for i in range(per_arm):
            n = rng.randint(4, 8)
            word = [rng.randrange(n) for _ in range(n - 2)]
            tree = nx.from_prufer_sequence(word)
            coins = [int(rng.randrange(4) == 0) for _ in range(n)]
            missing = [p for p in combinations(range(n), 2) if not tree.has_edge(*p)]
            extras = sorted(rng.sample(missing, arm))
            meetings = sorted([tuple(sorted(e)) for e in tree.edges] + extras)
            degree = Counter(k for pair in meetings for k in pair)
            sizes = [max(3, degree[v]) + coins[v] for v in range(n)]
            opens = [sizes[v] - degree[v] for v in range(n)]
            yield {"arm": arm, "draw": i, "n": n, "prufer": word, "coins": coins, "extra_meetings": extras,
                   "meetings": meetings, "sizes": sizes, "opens": opens, "stars": source_from(meetings, opens)}


# --------------------------------------------------------------------------------------------------------------------------
# Patterns and the operator test T (planarity of the knot-distinction incidence graph).
# --------------------------------------------------------------------------------------------------------------------------
def incidence_graph(stars, n=None):
    """One node per knot and one per distinction; a link when the knot holds the distinction.  `n` takes the first n knots."""
    g = nx.Graph()
    for k, star in enumerate(stars if n is None else stars[:n]):
        g.add_node(("k", k))
        for d in star:
            g.add_edge(("k", k), ("d", d))
    return g


def loop_rank(g):
    return g.number_of_edges() - g.number_of_nodes() + nx.number_connected_components(g)


def euler_fail(g):
    """The incidence graph is simple and bipartite, so a planar one has at most 2V-4 links (V >= 3).  More links: not planar."""
    v = g.number_of_nodes()
    return v >= 3 and g.number_of_edges() > 2 * v - 4


def passes(g, shortcut=True):
    """T: the stage passes when its pattern is planar (networkx.check_planarity).  With `shortcut`, a pattern with more links
    than 2V-4 is reported failing by Euler's bound without calling the routine (provably the same verdict; gate-tested)."""
    if shortcut and euler_fail(g):
        return False
    return nx.check_planarity(g)[0]


def pair_count_lower_bound(stars, n=None):
    """Lower removal bound: over connected parts with K >= 3 knots, max(0, P - (3K - 6)), P = distinct pairs of knots that share
    a distinction."""
    stars = stars if n is None else stars[:n]
    holders = defaultdict(list)
    for k, star in enumerate(stars):
        for d in star:
            holders[d].append(k)
    parent = list(range(len(stars)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    pairs = set()
    for hs in holders.values():
        for a, b in combinations(hs, 2):
            pairs.add((a, b))
        for a, b in zip(hs, hs[1:]):
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb
    knots, pcount = Counter(), Counter()
    for k in range(len(stars)):
        knots[find(k)] += 1
    for a, b in pairs:
        pcount[find(a)] += 1
    return sum(max(0, pcount[r] - (3 * K - 6)) for r, K in knots.items() if K >= 3)


def upper_removal_bound(stars, n=None, max_links=160, max_removals=80):
    """Upper removal bound: remove one shared distinction lying on the forbidden sub-pattern the routine returns (the one with
    the least name), repeat until the stage passes, count the removals.  Pendant nodes (loose distinctions, knots holding one
    distinction) cannot lie on the forbidden sub-pattern and are pruned first; sizes above `max_links` or more than
    `max_removals` removals are not computed (returns (None, reason))."""
    g = incidence_graph(stars, n)
    removed = 0
    while True:
        g = nx.Graph(nx.k_core(g, 2))
        if g.number_of_edges() > max_links:
            return None, f"more than {max_links} links in the 2-core"
        ok, cert = nx.check_planarity(g, counterexample=True)
        if ok:
            return removed, "ok"
        if removed >= max_removals:
            return None, f"more than {max_removals} removals"
        pick = min(x[1] for x in cert.nodes if x[0] == "d")
        g.remove_node(("d", pick))
        removed += 1


def stage_row(stars, n):
    """The census line of the stage made of the first n knots."""
    g = incidence_graph(stars, n)
    holders = Counter(d for k in range(n) for d in stars[k])
    loose = sum(1 for c in holders.values() if c == 1)
    ok = passes(g)
    return {"knots": n, "distinctions": len(holders), "loose": loose, "links": g.number_of_edges(),
            "parts": nx.number_connected_components(g), "loop_rank": loop_rank(g), "T": "pass" if ok else "fail",
            "lower_bound": pair_count_lower_bound(stars, n)}


# --------------------------------------------------------------------------------------------------------------------------
# The ordinary growth engine, driven from a source.
# --------------------------------------------------------------------------------------------------------------------------
class StepTimeout(Exception):
    pass


def _alarm(signum, frame):
    raise StepTimeout()


def grow(stars, law, horizon, cap, time_limit=None):
    """Ordinary growth by the recorded `end_operator.step`, one stage per parent step.

    Returns a dict: `stars` (all knots grown, in birth order), `n_at` (knots at each stage 0..steps), `births` (per step, the
    list of (number of parents, number of fresh distinctions) of each birth, in the engine's order), `outcome`:
    'horizon' (alive after the horizon), 'closed' (a closing birth, or no live knot), 'stall', 'cap' (the next step would
    exceed `cap` knots), 'time' (the wall-clock budget `time_limit` seconds ran out inside a step; the stages before it are
    kept).  A step that would take the structure above `cap` knots is not taken."""
    import signal
    import time
    started = time.time()
    stars = [tuple(s) for s in stars]
    end = EO.from_stars(stars)
    counts = Counter(d for s in stars for d in s)
    loose = {k: [d for d in s if counts[d] == 1] for k, s in enumerate(stars)}
    top = max(counts) + 1
    n_at, births, outcome = [len(stars)], [], "horizon"
    for _ in range(horizon):
        try:
            if time_limit is not None:
                left = time_limit - (time.time() - started)
                if left <= 0:
                    raise StepTimeout()
                signal.signal(signal.SIGALRM, _alarm)
                signal.setitimer(signal.ITIMER_REAL, left)
            try:
                turn = EO.step(end, law, max_births=max(0, cap - len(stars)))
            finally:
                signal.setitimer(signal.ITIMER_REAL, 0)
        except StepTimeout:
            outcome = "time"
            break
        if turn.status == "closed":
            outcome = "closed"
            break
        if turn.status == "stall":
            outcome = "stall"
            break
        if turn.status == "cap":
            outcome = "cap"
            break
        base = len(stars)
        record = []
        for parents, fresh in zip(turn.parents, turn.fresh, strict=True):
            inputs = tuple(loose[p].pop() for p in parents)
            made = tuple(range(top, top + fresh))
            top += fresh
            stars.append(inputs + made)
            loose[len(stars) - 1] = list(made)
            record.append((len(parents), fresh))
        births.append(record)
        n_at.append(len(stars))
        if turn.implied:
            outcome = "closed"
            break
        nxt = turn.end
        end = EO.End({base + i: c for i, c in nxt.opens.items()},
                     tuple(tuple(base + i for i in blk) for blk in nxt.blocks))
    return {"stars": stars, "n_at": n_at, "births": births, "outcome": outcome, "steps": len(births)}


def growth_kind(history):
    """stalled; bounded (births per step never above the largest of the first four steps); growing (otherwise).
    A history with no births at all (no live knot at the source) is read as stalled."""
    b = [len(step) for step in history["births"]]
    if history["outcome"] == "stall" or not b:
        return "stalled"
    return "bounded" if max(b) <= max(b[:4]) else "growing"


def one_parent_share(history):
    total = sum(len(s) for s in history["births"])
    one = sum(1 for s in history["births"] for p, _ in s if p == 1)
    return one, total


# --------------------------------------------------------------------------------------------------------------------------
# The rewired comparison.
# --------------------------------------------------------------------------------------------------------------------------
def rewire(source_stars, births, seed):
    """Replay a start's ordinary history keeping, at each parent step, the number of births and each birth's number of parents
    and of fresh distinctions; each birth draws its parents uniformly without replacement from the knots that still hold a
    loose distinction when the birth is made (knots born in the same step are not yet available).  Returns (stars, shortfall,
    short_births)."""
    rng = random.Random(seed)
    stars = [tuple(s) for s in source_stars]
    counts = Counter(d for s in stars for d in s)
    top = max(counts) + 1
    loose = {k: [d for d in s if counts[d] == 1] for k, s in enumerate(stars)}
    avail = [k for k in range(len(stars)) if loose[k]]
    where = {k: i for i, k in enumerate(avail)}

    def drop(k):
        i = where.pop(k)
        last = avail.pop()
        if i < len(avail):
            avail[i] = last
            where[last] = i

    shortfall = short_births = 0
    for step in births:
        pending = []
        for p, fresh in step:
            take = min(p, len(avail))
            if take < p:
                shortfall += p - take
                short_births += 1
            chosen = rng.sample(avail, take)
            inputs = tuple(loose[q].pop() for q in chosen)
            for q in chosen:
                if not loose[q]:
                    drop(q)
            made = tuple(range(top, top + fresh))
            top += fresh
            stars.append(inputs + made)
            if made:
                loose[len(stars) - 1] = list(made)
                pending.append(len(stars) - 1)
        for k in pending:
            where[k] = len(avail)
            avail.append(k)
    return stars, shortfall, short_births


def first_failing_stage(stars, n_at):
    """Least stage t (0 = the source) whose stage fails T, or None.  Failing is monotone in the parent step, so stages are
    visited in increasing order and the search stops at the first failure."""
    for t, n in enumerate(n_at):
        if not passes(incidence_graph(stars, n)):
            return t
    return None


# --------------------------------------------------------------------------------------------------------------------------
# Closed parity parts and the independent signed-operator test.
# --------------------------------------------------------------------------------------------------------------------------
_census = None


def census_module():
    global _census
    if _census is None:
        _census = load_module("fr_census", EXP / "FOUR-READINGS-20261120-001A/FOUR-READINGS-20261120-001A-E001_signed_rules/census.py")
    return _census


def closed_parts(stars, n):
    """Connected parts of the stage that hold no loose distinction (every distinction held by two knots)."""
    holders = defaultdict(list)
    for k in range(n):
        for d in stars[k]:
            holders[d].append(k)
    g = nx.Graph()
    g.add_nodes_from(range(n))
    loose_knots = set()
    for hs in holders.values():
        if len(hs) == 1:
            loose_knots.add(hs[0])
        else:
            g.add_edges_from(zip(hs, hs[1:]))
    parts = []
    for comp in nx.connected_components(g):
        if comp.isdisjoint(loose_knots):
            parts.append(sorted(comp))
    return parts, holders


def operator_reading(part, holders, max_rank=150, max_odd_tries=40):
    """'Admits': for some single odd knot, commuting two-valued operators satisfy every knot (no assignment does: with every
    distinction held by two knots the even sum of all knots cannot equal the odd right side).  Uses the recorded independent
    solver `pauli_solution` (FOUR-READINGS-20261120-001A census.py).  Returns (verdict or None, note)."""
    index = {k: i for i, k in enumerate(part)}
    ends = []
    for d in sorted(holders):
        hs = holders[d]
        if hs[0] in index:
            if len(hs) != 2:
                return None, "a distinction with other than two holders"
            ends.append((index[hs[0]], index[hs[1]]))
    if len(ends) - len(part) + 1 > max_rank:
        return None, f"loop rank above {max_rank}; independent solver not run"
    if len(part) < 2:
        return None, "single knot"
    census = census_module()
    for odd in range(min(len(part), max_odd_tries)):
        if census.pauli_solution(ends, {odd}) is not None:
            return True, f"odd knot {odd}"
    return False, f"no solution with any of {min(len(part), max_odd_tries)} odd knots tried"


# --------------------------------------------------------------------------------------------------------------------------
def dump(path, rows, mode="w"):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open(mode) as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True, separators=(",", ":")) + "\n")
