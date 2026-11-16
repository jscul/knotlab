"""Diagnostic advice only. Primary search never imports this module."""
from itertools import combinations


def outside_patterns(n, scheme):
    full = (1 << n) - 1
    first = 0 if not scheme else sum(1 << i for i in range(n) if (i // scheme) % 2 == 0)
    return first, first ^ full


def local_offsets(group):
    return [sum(((b >> j) & 1) << i for j,i in enumerate(group)) for b in range(8)]


def witness_score(offsets, groupmask, raw, patterns):
    base = [v & ~groupmask for v in patterns]
    left, right, combined = set(), set(), set()
    readings = [None] * 8
    # Follow the discovery order of the fixed implementation. Count all
    # requested observations and verifier references, including cache hits.
    schedule = ([(0,j) for j in range(3)] + [(1,j) for j in range(3)] +
                [(s,j) for j in range(3,8) for s in (0,1)])
    for requests,(side,j) in enumerate(schedule, 1):
        value = raw[base[side] | offsets[j]]
        if side == 0:
            readings[j] = value
            left.add(value)
            if len(left) == 3:
                return requests + 3, requests, 1
        else:
            right.add(value)
            if len(right) == 3:
                return requests + 3, requests, 1
            combined.add((readings[j],value))
            if len(combined) == 3:
                return requests + 6, requests, 2
    return None


def available(task):
    n = task["n"]
    one, two = task["outputs"]
    raw = [((one >> x) & 1) | (((two >> x) & 1) << 1) for x in range(1 << n)]
    patterns = [outside_patterns(n, i) for i in range(4)]
    by_group = {}
    for g in combinations(range(n),3):
        mask = sum(1 << i for i in g)
        offsets = local_offsets(g)
        by_group[mask] = [witness_score(offsets,mask,raw,p) for p in patterns]
    return by_group


def advice(tasks):
    result = {k:[] for k in ["oracle-menu", *(f"skip-{i}" for i in range(4))]}
    for task in tasks:
        available_groups = available(task)
        menu = {}
        for mask,scores in available_groups.items():
            candidate = min(((s,i) for i,s in enumerate(scores) if s is not None), default=(None,-1))
            menu[mask] = candidate[1]
        result["oracle-menu"].append(menu)
        for i in range(4):
            result[f"skip-{i}"].append({m:(i if s[i] is not None else -1) for m,s in available_groups.items()})
    return result
