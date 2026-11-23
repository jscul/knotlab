"""Ordinary growth engine with explicit allocations, a recorder, and two injectable faults.

Written for REVIEW-LEADS-20261123-001E-E001.  The ordinary law implemented here is the one defined in
research/ORDINARY-DYNAMICS-20261120-001/end_operator.md ("The operator on the present end"):

  * live knots hold at least one loose distinction (held by that knot alone);
  * two live knots are one end step apart when some knot (a witness) is adjacent to both;
  * a group is an inclusion-maximal set of at least three pairwise adjacent live knots with no common
    witness, plus every adjacent pair contained in no such set;
  * each knot owes one loose distinction to each group containing it; if some knot owes more than it
    holds the whole round stalls; otherwise every group is one birth and every remaining loose
    distinction is one unary birth;
  * a birth takes one loose distinction from each parent and receives max(demand, 3 - p, 1) fresh
    distinctions, where demand counts the groups that contain it when all births are provisionally live;
    under parity a sole birth is implied and receives none.

Everything here is independent of values.  The compact reference operator
(experiments/ORDINARY-DYNAMICS-20261120-001A/.../end_operator.py) is imported read-only by path and is
used to cross-check every plan this module makes.
"""

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations
from pathlib import Path
import sys

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LAWS = ("parity", "nae")
REFERENCE_OPERATOR = ROOT / ("experiments/ORDINARY-DYNAMICS-20261120-001A/"
                             "ORDINARY-DYNAMICS-20261120-001A-E001_ordinary/end_operator.py")


def load_module(path, name):
    """Import a file by path without writing bytecode beside it."""
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


_reference = None


def reference_operator():
    global _reference
    if _reference is None:
        _reference = load_module(REFERENCE_OPERATOR, "reference_end_operator")
    return _reference


# ----------------------------------------------------------------------------------------------
# Holdings
# ----------------------------------------------------------------------------------------------

def holders_of(stars):
    owners = defaultdict(list)
    for knot, row in enumerate(stars):
        for d in row:
            owners[d].append(knot)
    for d, hs in owners.items():
        assert len(hs) in (1, 2) and len(set(hs)) == len(hs), (d, hs)
    return owners


def loose_of(stars, owners=None):
    owners = owners or holders_of(stars)
    return {k: sorted(d for d in row if len(owners[d]) == 1) for k, row in enumerate(stars)}


def neighbours_of(stars, owners=None):
    owners = owners or holders_of(stars)
    nbrs = [set() for _ in stars]
    for hs in owners.values():
        if len(hs) == 2:
            a, b = hs
            nbrs[a].add(b)
            nbrs[b].add(a)
    return nbrs


# ----------------------------------------------------------------------------------------------
# Groups: a function of the holdings alone (no values, no names)
# ----------------------------------------------------------------------------------------------

def groups_from_adjacency(nodes, edge_sets, witnesses_of):
    """Maximal cliques of >=3 with no common witness, then the adjacent pairs they leave uncovered.

    ``edge_sets`` yields iterables of nodes that are mutually adjacent (one witness block each);
    ``witnesses_of(node)`` is the set of witnesses a node has.  A clique is held when its members
    share a witness.
    """
    graph = nx.Graph()
    graph.add_nodes_from(nodes)
    for block in edge_sets:
        graph.add_edges_from(combinations(sorted(block), 2))
    big = []
    for clique in nx.find_cliques(graph):
        if len(clique) >= 3 and not set.intersection(*(set(witnesses_of(p)) for p in clique)):
            big.append(tuple(sorted(clique)))
    big.sort()
    covered = {pair for group in big for pair in combinations(group, 2)}
    pairs = sorted(tuple(sorted(e)) for e in graph.edges if tuple(sorted(e)) not in covered)
    return tuple(big) + tuple(pairs)


def proposed_groups(stars, owners=None, loose=None, nbrs=None):
    """The proposed parent groups of one round, from the holdings alone."""
    owners = owners or holders_of(stars)
    loose = loose or loose_of(stars, owners)
    nbrs = nbrs or neighbours_of(stars, owners)
    live = {k for k, row in loose.items() if row}
    blocks = (nbrs[k] & live for k in range(len(stars)))
    return groups_from_adjacency(live, blocks, lambda p: nbrs[p])


def lookahead_demand(parent_sets):
    """Number of next groups that contain each provisional birth (all births live, one opening each)."""
    siblings = defaultdict(set)
    for i, ps in enumerate(parent_sets):
        for p in ps:
            siblings[p].add(i)
    groups = groups_from_adjacency(range(len(parent_sets)), siblings.values(), lambda i: parent_sets[i])
    count = Counter(i for g in groups for i in g)
    return tuple(count[i] for i in range(len(parent_sets)))


# ----------------------------------------------------------------------------------------------
# One round
# ----------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Birth:
    knot: int
    parents: tuple
    inputs: tuple      # inputs[j] is the loose distinction taken from parents[j]
    fresh: tuple
    demand: int

    @property
    def support(self):
        return self.inputs + self.fresh


@dataclass
class Plan:
    status: str                 # "extend", "stall", "closed"
    parents: tuple = ()         # parent set of every birth, in birth order
    fresh_counts: tuple = ()
    demand: tuple = ()
    groups: tuple = ()          # proposed groups before payment
    shortages: tuple = ()
    implied: bool = False
    loose: dict = field(default_factory=dict)


def plan_round(stars, law, veto=None, max_births=None):
    """Plan one complete round.  ``veto`` is the injected fault: a predicate on a proposed group.

    With ``max_births`` the round is not planned in full when it would write more births than that
    (status "cap"); the expensive look-ahead that fixes the fresh counts is then skipped.
    """
    assert law in LAWS
    owners = holders_of(stars)
    loose = loose_of(stars, owners)
    nbrs = neighbours_of(stars, owners)
    live = [k for k, row in loose.items() if row]
    if not live:
        return Plan("closed", loose=loose)
    groups = proposed_groups(stars, owners, loose, nbrs)
    if veto is not None:
        groups = tuple(g for g in groups if not veto(g))
    used = Counter(p for g in groups for p in g)
    shortages = tuple((k, used[k] - len(loose[k])) for k in sorted(used) if used[k] > len(loose[k]))
    if shortages:
        return Plan("stall", groups=groups, shortages=shortages, loose=loose)
    parents = groups + tuple((k,) for k in live for _ in range(len(loose[k]) - used[k]))
    if max_births is not None and len(parents) > max_births:
        return Plan("cap", parents, groups=groups, loose=loose)
    demand = lookahead_demand(parents)
    implied = law == "parity" and len(parents) == 1
    fresh = tuple(0 if implied else max(demand[i], 3 - len(ps), 1) for i, ps in enumerate(parents))
    return Plan("extend", parents, fresh, demand, groups, (), implied, loose)


def canonical_allocation(plan):
    """Smallest names first: the i-th birth containing a knot receives its i-th loose distinction."""
    return {k: list(ds) for k, ds in plan.loose.items() if ds}


def births_of_knot(plan):
    """For each knot the birth indices that contain it, in birth order."""
    result = defaultdict(list)
    for i, ps in enumerate(plan.parents):
        for p in ps:
            result[p].append(i)
    return result


def apply_plan(stars, plan, allocation=None):
    """Write the round's births.  ``allocation[k]`` lists k's loose distinctions in birth order."""
    assert plan.status == "extend"
    allocation = allocation or canonical_allocation(plan)
    own = births_of_knot(plan)
    for k, ds in plan.loose.items():
        if ds:
            assert sorted(allocation[k]) == ds and len(allocation[k]) == len(own[k]), k
    cursor = {k: iter(allocation[k]) for k in own}
    top = max(d for row in stars for d in row) + 1
    births = []
    for i, (ps, count) in enumerate(zip(plan.parents, plan.fresh_counts, strict=True)):
        inputs = tuple(next(cursor[p]) for p in ps)
        fresh = tuple(range(top, top + count))
        top += count
        births.append(Birth(len(stars) + i, ps, inputs, fresh, plan.demand[i]))
    assert all(next(c, None) is None for c in cursor.values())
    return tuple(stars) + tuple(b.support for b in births), tuple(births)


def agrees_with_reference(stars, law, plan):
    """Cross-check a plan against the compact reference operator (needs a connected presentation)."""
    ref = reference_operator()
    try:
        end = ref.from_stars(stars)
    except ValueError as error:
        if "one connected presentation" in str(error):
            return None
        raise
    turn = ref.step(end, law)
    if turn.status != plan.status:
        return False
    if plan.status == "extend":
        return (turn.parents == plan.parents and turn.fresh == plan.fresh_counts
                and turn.demand == plan.demand and turn.implied == plan.implied)
    if plan.status == "stall":
        return {k: s for k, s in turn.shortages} == {k: s for k, s in plan.shortages}
    return True


# ----------------------------------------------------------------------------------------------
# Histories and the recorder
# ----------------------------------------------------------------------------------------------

@dataclass
class History:
    name: str
    law: str
    frames: list                       # frames[t] is the tuple of supports after t rounds
    births: list                       # births[t] are the births of round t+1 (may be empty)
    statuses: list                     # status of each attempted round
    cross_checks: list = field(default_factory=list)   # True/False/None per round vs the reference operator


def grow_history(stars, law, rounds, knot_cap=None, veto=None, cross_check=True, edit=None, name=""):
    """Grow up to ``rounds`` complete rounds from ``stars``, recording every frame.

    ``knot_cap`` stops before any round that would take the number of knots above it (rounds are
    atomic; status "cap" is recorded).  ``edit(t, frame)`` is the injected first fault: it may return a
    changed copy of the frame after round t (used to add a loose distinction to an existing knot).
    """
    frames = [tuple(tuple(r) for r in stars)]
    births, statuses, checks = [], [], []
    for t in range(1, rounds + 1):
        room = None if knot_cap is None else knot_cap - len(frames[-1])
        plan = plan_round(frames[-1], law, veto, max_births=room)
        if cross_check and veto is None and plan.status != "cap":
            # the reference operator costs as much as this engine; skip it for rounds of over 400 births
            checks.append(agrees_with_reference(frames[-1], law, plan) if len(plan.parents) <= 400 else None)
        statuses.append(plan.status)
        if plan.status != "extend":
            break
        frame, batch = apply_plan(frames[-1], plan)
        if edit is not None:
            frame = edit(t, frame)
        frames.append(frame)
        births.append(batch)
    return History(name, law, frames, births, statuses, checks)


def birth_signature(batch):
    """Parents and numbers of fresh distinctions of a round, nothing else."""
    return tuple((b.parents, len(b.fresh)) for b in batch)


def read_births(frames):
    """Recorder: recover each round's births from consecutive frames, with no reference to the engine.

    A new knot's parents are the old knots that hold the distinctions it re-uses; its fresh count is
    the number of distinctions it holds that no earlier knot held.
    """
    result = []
    for before, after in zip(frames, frames[1:]):
        seen = defaultdict(list)
        for k, row in enumerate(before):
            for d in row:
                seen[d].append(k)
        batch = []
        for k in range(len(before), len(after)):
            parents = tuple(sorted(seen[d][0] for d in after[k] if d in seen))
            fresh = sum(1 for d in after[k] if d not in seen)
            batch.append((parents, fresh))
        result.append(tuple(batch))
    return tuple(result)


# ----------------------------------------------------------------------------------------------
# Laws on values
# ----------------------------------------------------------------------------------------------

def lawful_word(law, word):
    ones = sum(word)
    return ones % 2 == 0 if law == "parity" else 0 < ones < len(word)


def lawful_completions(law, inputs, count):
    out = []
    for n in range(1 << count):
        fresh = tuple((n >> i) & 1 for i in range(count))
        if lawful_word(law, tuple(inputs) + fresh):
            out.append(fresh)
    return out


def sample_completion(law, inputs, count, rng):
    """A uniformly random lawful fresh word for the given paid inputs, without enumerating 2^count words."""
    assert count >= 1
    inputs = tuple(inputs)
    if law == "parity":
        fresh = [rng.getrandbits(1) for _ in range(count - 1)]
        fresh.append((sum(inputs) + sum(fresh)) % 2)
        return tuple(fresh)
    while True:
        fresh = tuple(rng.getrandbits(1) for _ in range(count))
        if lawful_word(law, inputs + fresh):
            return fresh


def check_values(stars, values, law):
    return all(lawful_word(law, tuple(values[d] for d in row)) for row in stars)


def completions_count(law, input_values, fresh_count):
    """Number of lawful fresh words given the old inputs (closed form, checked against enumeration)."""
    if fresh_count == 0:
        return int(lawful_word(law, tuple(input_values)))
    if law == "parity":
        return 2 ** (fresh_count - 1)
    return 2 ** fresh_count - int(len(set(input_values)) == 1)
