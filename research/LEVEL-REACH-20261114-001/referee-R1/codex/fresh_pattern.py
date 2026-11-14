"""Fresh mixed-level construction; only the previous referee's actions are reused.

No study producer is imported. Term indices are word-major with none,0,1.
"""
from __future__ import annotations
import importlib.util
import itertools
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OLD = ROOT / 'research/ADDR-KNOTS-20261113-001/referee-R1/codex/fresh_patterns.py'
spec = importlib.util.spec_from_file_location('previous_referee_actions', OLD)
previous = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous)


def build(key, N):
    catalog = previous.words(key[0])
    terms = sorted({t for p in key[4] for t in p})
    knots = set()
    for n in range(N + 1):
        maps = previous.state_actions(key, n)
        images = {}
        for t in terms:
            wi, letter = divmod(t, 3)
            vals = list(range(1 << n))
            for q in reversed(catalog[wi]):
                vals = [maps[q][x] for x in vals]
            if letter:
                images[t] = [(1 << (n + 1)) - 1 + 2*x + letter - 1 for x in vals]
            else:
                images[t] = [(1 << n) - 1 + x for x in vals]
        for p in key[4]:
            if n == N and any(t % 3 for t in p):
                continue
            for row in zip(*(images[t] for t in p)):
                if len(set(row)) == 3:
                    knots.add(tuple(sorted(row)))
    return sorted(knots)


def direct_build(key, N):
    """Slow, separate bit-by-bit control, no state-action tables."""
    catalog = previous.words(key[0])
    out = set()
    for n in range(N + 1):
        for x in range(1 << n):
            for p in key[4]:
                row = []
                for t in p:
                    wi, letter = divmod(t, 3)
                    if letter and n == N:
                        break
                    y = x
                    for q in reversed(catalog[wi]):
                        y = previous.direct_state(key, q, y, n)
                    length = n + bool(letter)
                    if letter:
                        y = 2*y + letter - 1
                    row.append((1 << length) - 1 + y)
                if len(row) == 3 and len(set(row)) == 3:
                    out.add(tuple(sorted(row)))
    return sorted(out)


def cnf(knots):
    return previous.cnf(knots)


def level(v):
    return (v + 1).bit_length() - 1


def components(knots, nvars):
    parent = list(range(nvars))
    def find(v):
        while parent[v] != v:
            parent[v] = parent[parent[v]]
            v = parent[v]
        return v
    for row in knots:
        a = find(row[0])
        for v in row[1:]:
            parent[find(v)] = a
    return [find(v) for v in range(nvars)]
