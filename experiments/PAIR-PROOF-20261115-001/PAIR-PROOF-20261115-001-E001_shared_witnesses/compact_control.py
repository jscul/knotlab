"""Ordinary cofactor search with cached triple layouts and a two-class early exit."""
from functools import cache
from itertools import combinations
from time import process_time_ns

from controls import _location
from parent_engine import _measure, _partition, _select, _shared


@cache
def _layouts(m, axes):
    rows = 1 << m
    full = (1 << rows) - 1
    zero = [full // ((1 << (1 << i)) + 1) for i in range(m)]
    groups = []
    for triple in combinations(axes, 3):
        a, b, c = triple
        mask = zero[a] & zero[b] & zero[c]
        x, y, z = 1 << a, 1 << b, 1 << c
        groups.append((triple, mask | (mask << rows), (x, y, x+y, z, x+z, y+z, x+y+z)))
    return tuple(groups)


def third_residual(joint, mask, remaining):
    """Return true exactly when the triple needs at least three messages."""
    first, second = joint & mask, -1
    for shift in remaining:
        value = (joint >> shift) & mask
        if value == first or value == second:
            continue
        if second >= 0:
            return True
        second = value
    return False


def _minimum(state, work):
    candidate = _location(state, work)
    incumbent = _partition(state, work, candidate) if candidate is not None else None
    if incumbent is None or not incumbent["eligible"] or incumbent["width"] > 2:
        return _select(state, work, candidate, incumbent if incumbent and incumbent["eligible"] else None)
    if incumbent["width"] == 1:
        state._global_width = 1
        return incumbent
    joint = state.tables[0] | (state.tables[1] << (1 << state.m))
    tests = 0
    axes = _shared(state, work)
    for triple, mask, remaining in _layouts(state.m, axes):
        if triple == candidate:
            continue
        tests += 1
        if not third_residual(joint, mask, remaining):
            work["compact_exact_alternatives"] += tests
            state._global_width = 1
            return _partition(state, work, triple)
    work["compact_exact_alternatives"] += tests
    state._global_width = 2
    return incumbent


def compact(state):
    from pair_solver import finish_selected
    def complete(s, work):
        started = process_time_ns()
        selected = _minimum(s, work)
        work["minimum_selection_cpu_ns"] += process_time_ns() - started
        return finish_selected(s, work, selected)
    return _measure(state, complete)
