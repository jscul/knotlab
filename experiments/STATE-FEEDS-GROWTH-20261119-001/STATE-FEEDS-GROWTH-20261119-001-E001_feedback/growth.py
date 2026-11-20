"""Complete parity growth with one activity reading per proposed birth."""

from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import cache, lru_cache
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import SimpleNamespace


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EDDY = ROOT / "experiments/EDDY-WORLD-20261119-001/EDDY-WORLD-20261119-001-E001_world/world_growth.py"
ACTIONS = ("P", "V", "+", "-")
ORDINARY = ("P", "P")
ACTION_NAMES = dict(zip(("pass", "veto", "plus", "minus"), ACTIONS, strict=True))


@cache
def predecessor():
    spec = spec_from_file_location("feedback_predecessor", EDDY)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _groups(neighbors, live):
    _, fast = predecessor().production()
    return tuple(tuple(sorted(g)) for g in fast.groups_among(SimpleNamespace(nbr=neighbors), live))


@dataclass(frozen=True)
class Stage:
    stars: tuple
    names: frozenset
    loose: dict
    neighbors: tuple


@lru_cache(maxsize=64)
def _index(stars):
    holders = defaultdict(list)
    for v, support in enumerate(stars):
        if len(support) < 3 or len(set(support)) != len(support):
            raise ValueError(f"invalid support at knot {v}")
        for d in support:
            if not isinstance(d, int) or d < 0:
                raise ValueError(f"invalid distinction name {d!r}")
            holders[d].append(v)
    if not stars or len(set(stars)) != len(stars):
        raise ValueError("one nonempty connected presentation with distinct supports is required")
    loose = defaultdict(list)
    neighbors = tuple(set() for _ in stars)
    for d, row in holders.items():
        if len(row) == 1:
            loose[row[0]].append(d)
        elif len(row) == 2:
            v, w = row
            neighbors[v].add(w)
            neighbors[w].add(v)
        else:
            raise ValueError(f"distinction {d} has more than two holders")
    if len(predecessor().reached(neighbors, 0)) != len(stars):
        raise ValueError("the ordinary knot presentation must be connected")
    return Stage(stars, frozenset(holders), {v: tuple(sorted(ds)) for v, ds in sorted(loose.items())}, neighbors)


def _state(stars, occupied):
    index = _index(tuple(tuple(sorted(row)) for row in stars))
    state = frozenset(occupied)
    if not state <= index.names or any(sum(d in state for d in s) % 2 for s in index.stars):
        raise ValueError("occupied distinctions must form an allowed relative assignment")
    return index, state


@lru_cache(maxsize=64)
def _candidate_groups(stars):
    stage = _index(stars)
    return _groups(stage.neighbors, stage.loose)


@lru_cache(maxsize=128)
def _lookahead(old_count, parents):
    neighbors = defaultdict(set)
    born = tuple(range(old_count, old_count + len(parents)))
    for j, family in zip(born, parents, strict=True):
        for v in family:
            neighbors[j].add(v)
            neighbors[v].add(j)
    groups = _groups(neighbors, born)
    demand = Counter(v for group in groups for v in group)
    return groups, tuple(demand[j] for j in born)


@dataclass(frozen=True)
class Birth:
    parents: tuple
    active: bool
    action: str
    demand: int
    baseline: int
    fresh: int
    clipped: bool


@dataclass(frozen=True)
class Plan:
    stage: Stage
    occupied: frozenset
    status: str
    details: dict
    births: tuple = ()


def plan_round(stars, occupied=(), table=ORDINARY, *, caps=None, recorded_actions=None):
    """Decide the unordered roster before allocating any concrete old distinction."""
    stage, occupied = _state(stars, occupied)
    table = tuple(ACTION_NAMES.get(a, a) for a in table)
    if len(table) != 2 or any(a not in ACTIONS for a in table):
        raise ValueError("a table has two entries from P, V, + and -")
    if not stage.loose:
        return Plan(stage, occupied, "closed", {})
    hot = {v for v in stage.loose if not occupied.isdisjoint(stage.stars[v])}

    def choose(parents):
        active = any(v in hot for v in parents)
        action = table[active] if recorded_actions is None else recorded_actions[parents]
        return active, action

    groups = _candidate_groups(stage.stars)
    decisions = [(group, *choose(group)) for group in groups]
    kept = [(group, active, action) for group, active, action in decisions if action != "V"]
    used = Counter(v for group, _, _ in kept for v in group)
    shortages = {v: used[v] - len(bits) for v, bits in stage.loose.items() if used[v] > len(bits)}
    details = {
        "hot_live_parents": sorted(hot),
        "candidate_groups": [{"parents": list(g), "active": a, "action": action} for g, a, action in decisions],
        "retained_multi": len(kept), "vetoed_multi": len(decisions) - len(kept),
    }
    if shortages:
        return Plan(stage, occupied, "stall", {**details, "shortages": shortages})

    roster = kept + [((v,), *choose((v,)))
                     for v, bits in stage.loose.items() for _ in range(len(bits) - used[v])]
    n_knots = len(stage.stars) + len(roster)
    closes = len(roster) == 1
    if closes and len(roster[0][0]) < 3:
        # The old whole-loose parity is implied, so attaching fresh choices cannot free its proper projection.
        return Plan(stage, occupied, "arity_stop", {**details, "implied_arity": len(roster[0][0])})
    n_old = len(stage.names)
    extra_floor = sum(max(1, 3 - len(g)) + (action == "+") for g, _, action in roster) if not closes else 0
    projection = {"planned_new_knots": len(roster), "planned_total_knots": n_knots}
    if caps is not None and n_knots > caps["junctions"]:
        return Plan(stage, occupied, "junction_cap", {**details, **projection,
                    "planned_total_distinctions_lower": n_old + extra_floor})
    if caps is not None and n_old + extra_floor > caps["distinctions"]:
        return Plan(stage, occupied, "distinction_cap", {**details, **projection,
                    "planned_total_distinctions_lower": n_old + extra_floor})

    following, need = _lookahead(len(stage.stars), tuple(g for g, _, _ in roster))
    births = []
    for (parents, active, action), demand in zip(roster, need, strict=True):
        floor = max(1, 3 - len(parents))
        base = 0 if closes else max(floor, demand)
        count = 0 if closes else max(floor, base + (action == "+") - (action == "-"))
        births.append(Birth(parents, active, action, demand, base, count,
                            action == "-" and count != base - 1))
    width = n_old + sum(b.fresh for b in births)
    if caps is not None and width > caps["distinctions"]:
        return Plan(stage, occupied, "distinction_cap", {**details, **projection,
                    "planned_total_distinctions": width})
    details["lookahead_groups"] = following
    details["implied_closure"] = closes
    return Plan(stage, occupied, "extend", details, tuple(births))


def literal_allocation(plan):
    """A display representative; all allocations in realize_round are admissible."""
    available = {v: iter(row) for v, row in plan.stage.loose.items()}
    return tuple(tuple(next(available[v]) for v in b.parents) for b in plan.births)


def _snapshot(stars, occupied):
    stage, occupied = _state(stars, occupied)
    rank = len(stage.stars) - (not stage.loose)
    return {"stars": stage.stars, "occupied": sorted(occupied), "live": list(stage.loose),
            "loose": stage.loose, "junction_count": len(stage.stars),
            "distinction_count": len(stage.names), "equation_rank": rank,
            "state_dimension": len(stage.names) - rank, "parity_allowed": True}


def realize_round(plan, *, allocation=None, birth_order=None, choose_fresh=None):
    """Realize any funded port allocation and any minimum-parity lift of the current values."""
    if plan.status != "extend":
        return {"status": plan.status, **plan.details}
    old = plan.stage
    if allocation is None:
        allocation = literal_allocation(plan)
    if birth_order is None:
        birth_order = range(len(plan.births))
    birth_order = tuple(birth_order)
    if set(birth_order) != set(range(len(plan.births))) or len(birth_order) != len(plan.births):
        raise ValueError("birth_order must enumerate each planned birth once")
    allocation = tuple(tuple(ds) for ds in allocation)
    used = set()
    for b, row in zip(plan.births, allocation, strict=True):
        for v, d in zip(b.parents, row, strict=True):
            if d in used or d not in old.loose[v]:
                raise ValueError("each parent must supply a different current loose distinction")
            used.add(d)
    assert len(used) == sum(map(len, old.loose.values()))

    stars = list(old.stars)
    occupied = set(plan.occupied)
    next_name = max(old.names) + 1
    births = []
    ids = {}
    for i in birth_order:
        b, spent = plan.births[i], allocation[i]
        j = len(stars)
        ids[len(old.stars) + i] = j
        fresh = tuple(range(next_name, next_name + b.fresh))
        next_name += b.fresh
        if sum(d in occupied for d in spent) % 2:
            if not fresh:
                raise AssertionError("the whole-loose inherited parity must already hold")
            choice = fresh[0] if choose_fresh is None else choose_fresh(fresh)
            if choice not in fresh:
                raise ValueError("a parity lift must choose a fresh distinction of its own child")
            occupied.add(choice)
        stars.append((*spent, *fresh))
        births.append({"knot": j, "parents": b.parents, "active": b.active, "action": b.action,
                       "demand": b.demand, "baseline_fresh": b.baseline, "fresh": fresh,
                       "spent": tuple(zip(b.parents, spent, strict=True)), "minus_clipped": b.clipped})

    frame = _snapshot(stars, occupied)
    frame.update(plan.details)
    frame.update({"status": "extend", "born": [b["knot"] for b in births], "births": births,
                  "parent_sets": {b["knot"]: b["parents"] for b in births},
                  "consumed": {b["knot"]: b["spent"] for b in births},
                  "fresh": {b["knot"]: b["fresh"] for b in births},
                  "demand_at_birth": {b["knot"]: b["demand"] for b in births},
                  "lookahead_groups": [sorted(ids[j] for j in g) for g in plan.details["lookahead_groups"]],
                  "new_occupied": sorted(occupied - plan.occupied),
                  "spent_occupied": sorted(used & plan.occupied), "old_states_preserved": True})
    assert frame["equation_rank"] == len(old.stars) + sum(b.fresh > 0 for b in plan.births)
    return frame


def step(stars, occupied=(), table=ORDINARY, *, caps=None):
    """Return one complete stage or the exact reason the complete round stopped."""
    return realize_round(plan_round(stars, occupied, table, caps=caps))


def grow(stars, occupied=(), table=ORDINARY, rounds=1, *, caps=None, start_age=0):
    """Return the complete prefix from the given physical stage, including termination."""
    if rounds < 0:
        raise ValueError("rounds must be nonnegative")
    frame = _snapshot(stars, occupied)
    if caps is not None and (frame["junction_count"] > caps["junctions"] or
                             frame["distinction_count"] > caps["distinctions"]):
        raise ValueError("the initial stage already exceeds the physical caps")
    source_knots = list(range(frame["junction_count"])) if start_age == 0 else []
    frame.update({"age": start_age, "born": source_knots, "births": [], "parent_sets": {},
                  "consumed": {}, "fresh": {}, "candidate_groups": []})
    stages = {str(start_age): frame}
    last = start_age
    termination = {"status": "age_limit", "last_age": start_age + rounds}
    for age in range(start_age + 1, start_age + rounds + 1):
        frame = step(frame["stars"], frame["occupied"], table, caps=caps)
        if frame["status"] != "extend":
            termination = {"last_age": last, "next_age": age, **frame}
            break
        stages[str(age)] = {"age": age, **frame}
        last = age
    if not stages[str(last)]["live"]:
        termination = {"status": "closed", "last_age": last}
    return {"stages": stages, "termination": termination}
