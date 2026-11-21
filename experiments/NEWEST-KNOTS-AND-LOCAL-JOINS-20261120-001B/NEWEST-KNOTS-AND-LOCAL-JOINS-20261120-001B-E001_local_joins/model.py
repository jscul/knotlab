"""One radius-two added-group policy, with both unchanged comparators."""
from __future__ import annotations

from collections import Counter
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PRIOR_LEAF = 'LOOSE-NAMES-AND-SPENT-JOINS-20261120-001B'
PRIOR = ROOT / 'experiments' / PRIOR_LEAF / f'{PRIOR_LEAF}-E001_spent_joins'
spec = spec_from_file_location('previous_spent_model', PRIOR / 'model.py')
previous = module_from_spec(spec)
sys.modules[spec.name] = previous
spec.loader.exec_module(previous)
Step, Physical, read = previous.Step, previous.Physical, previous.read
separating_witnesses = previous.separating_witnesses


def ball(graph, w, z, radius=2):
    present = {w, z}
    front = present.copy()
    for _ in range(radius):
        front = {n for p in front for n in graph[p]} - present
        present.update(front)
    return present


def rooted_record(physical, name, radius=2):
    """The addressed version of the local record. Labels transport under isomorphism."""
    w, z = next(pair for pair, bits in physical.shared.items() if name in bits)
    members = ball(physical.graph, w, z, radius)
    shared_count = Counter()
    internal = []
    for (a, b), names in sorted(physical.shared.items()):
        shared_count[a] += len(names)
        shared_count[b] += len(names)
        if a in members and b in members:
            internal.append((a, b, tuple(sorted(names))))
    rows = [(a, len(physical.loose.get(a, ())), shared_count[a]) for a in sorted(members)]
    return {'root': (w, z, name), 'holders': rows, 'shared': internal}


def local_witnesses(physical):
    """Discontinue a named participation if its two ends still meet inside radius two."""
    live = physical.loose.keys()
    donors = {w: tuple(sorted(live & physical.graph[w].keys()))
              for w in physical.graph if w not in live}
    witnesses = []
    for (w, z), names in sorted(physical.shared.items()):
        if len(names) != 1 or not donors.get(w) or not donors.get(z):
            continue
        left, right = donors[w], donors[z]
        if not set(left).isdisjoint(right):
            continue
        members = ball(physical.graph, w, z)
        display = physical.graph.subgraph(members).copy()
        display.remove_edge(w, z)
        if not nx.has_path(display, w, z):
            witnesses.append((names[0], w, z, left, right))
    return tuple(witnesses)


def propose(physical, rule, cap, suppress_name=None):
    if rule in ('ordinary', 'spent'):
        return previous.propose(physical, rule, cap, suppress_name)
    if rule != 'local':
        raise ValueError(f'unknown participation rule {rule}')
    witnesses = local_witnesses(physical)
    unions = {tuple(sorted((*left, *right)))
              for name, _, _, left, right in witnesses if name != suppress_name}
    ordinary, _, _ = previous.propose(physical, 'ordinary', cap)
    if ordinary is None:
        return None, tuple(sorted(unions)), witnesses
    added = tuple(sorted(unions - set(ordinary)))
    groups = ordinary + added
    return (groups if len(groups) <= cap else None), added, witnesses


def step(stars, law, rule, cap=256, forecast_cap=8192, *, suppress_name=None):
    if rule != 'local':
        return previous.step(stars, law, rule, cap, forecast_cap, suppress_name=suppress_name)
    if law not in ('nae', 'parity') or min(cap, forecast_cap) < 1:
        raise ValueError('unknown law or invalid cap')
    stars = tuple(tuple(row) for row in stars)
    old = read(stars)
    if not old.loose:
        return Step('closed', stars)
    groups, added, witnesses = propose(old, rule, cap, suppress_name)
    info = dict(added=added, bridges=witnesses)
    if groups is None:
        return Step('cap', stars, planned_births_lower=cap + 1, **info)

    info['groups'] = groups
    charges = Counter(p for group in groups for p in group)
    shortages = tuple((p, charges[p] - len(bits)) for p, bits in old.loose.items()
                      if charges[p] > len(bits))
    if shortages:
        return Step('stall', stars, funded=False, shortages=shortages, **info)
    count = len(groups) + sum(len(bits) - charges[p] for p, bits in old.loose.items())
    if count > cap:
        return Step('cap', stars, funded=True, planned_births_lower=count, **info)
    unary = tuple((p,) for p, bits in old.loose.items() for _ in range(len(bits) - charges[p]))
    parents = groups + unary
    ports = {p: iter(bits) for p, bits in old.loose.items()}
    inputs = tuple(tuple(next(ports[p]) for p in group) for group in parents)
    assert all(next(bits, None) is None for bits in ports.values())

    first = 1 + max(max(row) for row in stars)
    provisional = stars + tuple(bits + (first + i,) for i, bits in enumerate(inputs))
    future, next_added, _ = propose(read(provisional), rule, forecast_cap)
    info.update(parents=parents, inputs=inputs, next_added=next_added)
    if future is None:
        return Step('forecast_cap', stars, funded=True, **info)
    costs = Counter(p for group in future for p in group)
    demand = tuple(costs[len(stars) + i] for i in range(len(parents)))
    if law == 'parity' and len(parents) == 1:
        assert demand == (0,)
        prices = (0,)
    else:
        prices = tuple(max(1, 3 - len(ps), k) for ps, k in zip(parents, demand, strict=True))
    fresh = []
    for price in prices:
        fresh.append(tuple(range(first, first + price)))
        first += price
    grown = stars + tuple(bits + new for bits, new in zip(inputs, fresh, strict=True))
    return Step('extend', grown, funded=True, fresh=tuple(fresh), demand=demand, **info)
