"""Physical ordinary and spent-witness policies. No status mutates the supplied holdings."""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
import sys

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ORDINARY = ROOT / 'experiments/ORDINARY-DYNAMICS-20261120-001A/ORDINARY-DYNAMICS-20261120-001A-E001_ordinary'
sys.path.insert(0, str(ORDINARY))
import end_operator

Group = tuple[int, ...]
Groups = tuple[Group, ...]
Stars = tuple[tuple[int, ...], ...]
Witness = tuple[int, int, int, Group, Group]


@dataclass(frozen=True)
class Step:
    status: str
    stars: Stars
    funded: bool | None = None
    groups: Groups = ()
    added: Groups = ()
    bridges: tuple[Witness, ...] = ()
    shortages: tuple[tuple[int, int], ...] = ()
    parents: Groups = ()
    inputs: Groups = ()
    fresh: Groups = ()
    demand: tuple[int, ...] = ()
    next_added: Groups = ()
    planned_births_lower: int | None = None


@dataclass(frozen=True)
class Physical:
    graph: nx.Graph
    loose: dict[int, tuple[int, ...]]
    shared: dict[tuple[int, int], list[int]]
    end: end_operator.End


def read(stars: Stars) -> Physical:
    """Count individual physical names, retaining parallel holdings in shared."""
    holders = defaultdict(list)
    for k, row in enumerate(stars):
        for bit in row:
            holders[bit].append(k)
    graph = nx.Graph()
    graph.add_nodes_from(range(len(stars)))
    loose = defaultdict(list)
    shared = defaultdict(list)
    for bit, owners in holders.items():
        if len(owners) == 1:
            loose[owners[0]].append(bit)
        elif len(owners) == 2 and owners[0] != owners[1]:
            a, b = owners
            shared[a, b].append(bit)
            graph.add_edge(a, b)
        else:
            raise ValueError('each bit must have one or two distinct physical holders')
    if not graph or not nx.is_connected(graph):
        raise ValueError('the status of a solitary parity birth requires a connected presentation')
    private = {k: tuple(sorted(bits)) for k, bits in sorted(loose.items())}
    witness_blocks = tuple(tuple(v for v in graph[k] if v in private) for k in graph)
    return Physical(graph, private, shared, end_operator.End({k:len(row) for k,row in private.items()}, witness_blocks))


def separating_witnesses(physical: Physical) -> tuple[Witness, ...]:
    live = physical.loose.keys()
    donors = {w: tuple(sorted(set(physical.graph[w]) & live)) for w in physical.graph if w not in live}
    candidates = {pair: bits[0] for pair,bits in physical.shared.items()
                  if len(bits) == 1 and donors.get(pair[0]) and donors.get(pair[1])}
    if not candidates:
        return ()
    separating = {tuple(sorted(pair)) for pair in nx.bridges(physical.graph)}
    return tuple((candidates[a,b], a, b, donors[a], donors[b])
                 for a,b in sorted(separating & candidates.keys()))


def propose(physical: Physical, rule: str, cap: int, suppress_name: int | None = None) -> tuple[Groups | None, Groups, tuple[Witness, ...]]:
    witnesses = separating_witnesses(physical) if rule == 'spent' else ()
    sets = {tuple(sorted(set(left) | set(right))) for bit,_,_,left,right in witnesses if bit != suppress_name}
    # Across a separating name the two donor sets are disjoint. No ordinary group
    # can contain a donor on each side. Keep full-set dedup explicit in code.
    try:
        old = end_operator._proposals(physical.end, cap)
    except end_operator._Cap:
        return None, tuple(sorted(sets)), witnesses
    added = tuple(sorted(sets - set(old)))
    groups = old + added
    return (groups if len(groups) <= cap else None), added, witnesses


def step(stars: Stars, law: str, rule: str, cap: int = 256, forecast_cap: int = 8192, *, suppress_name: int | None = None) -> Step:
    if law not in ('nae', 'parity') or rule not in ('ordinary', 'spent'):
        raise ValueError('unknown law or proposal rule')
    if cap < 1 or forecast_cap < 1:
        raise ValueError('caps must be positive')
    stars = tuple(tuple(row) for row in stars)
    old = read(stars)
    if not old.loose:
        return Step('closed', stars)
    groups, added, witnesses = propose(old, rule, cap, suppress_name)
    hints = dict(added=added, bridges=witnesses)
    if groups is None:
        return Step('cap', stars, planned_births_lower=cap+1, **hints)
    hints['groups'] = groups
    charge = Counter(p for group in groups for p in group)
    shortage = tuple((k,charge[k]-len(bits)) for k,bits in old.loose.items() if charge[k] > len(bits))
    if shortage:
        return Step('stall', stars, funded=False, shortages=shortage, **hints)
    n = len(groups) + sum(len(bits)-charge[k] for k,bits in old.loose.items())
    if n > cap:
        return Step('cap', stars, funded=True, planned_births_lower=n, **hints)
    parents = groups + tuple((k,) for k,bits in old.loose.items() for _ in range(len(bits)-charge[k]))
    used = Counter()
    inputs = []
    for family in parents:
        inputs.append(tuple(old.loose[k][used[k]] for k in family))
        used.update(family)
    assert all(used[p] == len(bits) for p,bits in old.loose.items())
    inputs = tuple(inputs)
    start = max(max(row) for row in stars)+1
    future = stars + tuple(row + (start+i,) for i,row in enumerate(inputs))
    next_groups, next_added, _ = propose(read(future), rule, forecast_cap)
    hints.update(parents=parents, inputs=inputs, next_added=next_added)
    if next_groups is None:
        return Step('forecast_cap', stars, funded=True, **hints)
    need = Counter(p for group in next_groups for p in group)
    demand = tuple(need[len(stars)+i] for i in range(len(parents)))
    if law == 'parity' and len(parents) == 1:
        assert demand == (0,)
        fresh_counts = (0,)
    else:
        fresh_counts = tuple(max(1,3-len(ps),d) for ps,d in zip(parents,demand,strict=True))
    fresh = []
    for amount in fresh_counts:
        fresh.append(tuple(range(start,start+amount)))
        start += amount
    grown = stars + tuple(ps+fs for ps,fs in zip(inputs,fresh,strict=True))
    return Step('extend', grown, funded=True, fresh=tuple(fresh), demand=demand, **hints)
