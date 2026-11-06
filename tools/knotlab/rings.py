"""Which knots remember a loop (epic KNOT-LOOPS-20261019-001).

A link is a relation with one witness distinction passed in, one passed out,
and some middle distinctions. For each value of its middle distinctions it
allows some (witness in, witness out) pairs: its transfer. A ring joins copies
so that each passes its witness out to the next copy's witness in; forgetting
the witnesses leaves a relation on the copies' middle distinctions. A network
puts one copy on every edge of a graph, with the witnesses at the vertices.

Under the forgetting reading of K1-K3 (KNOT-LOOPS-20261019-001B-P001, Lean):

- a ring excludes a pattern exactly when every transfer along it is a
  permutation and an odd number of them swap, so it composes into a knot or
  into nothing;
- only parity has all-permutation transfers, and it keeps one full bit at
  every length; other knots' memory fades with the length of the loop.

A parity network keeps one bit per independent loop of the graph
(KNOT-LOOPS-20261019-001C-E001).
"""

from __future__ import annotations

import math
from itertools import product
from typing import Sequence

from .relations import Relation

Pairs = frozenset[tuple[bool, bool]]
IDENTITY: Pairs = frozenset({(False, False), (True, True)})
SWAP: Pairs = frozenset({(False, True), (True, False)})
DIAGONAL: Pairs = IDENTITY


def _middle(relation: Relation, win: str, wout: str) -> list[str]:
    if win == wout or win not in relation.variables or wout not in relation.variables:
        raise ValueError("win and wout must be two distinct variables of the relation")
    return [name for name in relation.variables if name not in (win, wout)]


def transfers(relation: Relation, win: str, wout: str) -> dict[tuple[bool, ...], Pairs]:
    """For each value of the middle distinctions, the allowed (witness in, witness out) pairs."""
    middle = _middle(relation, win, wout)
    order = relation.variables
    table: dict[tuple[bool, ...], set[tuple[bool, bool]]] = {m: set() for m in product((False, True), repeat=len(middle))}
    for row in relation.rows:
        value = dict(zip(order, row))
        table[tuple(value[name] for name in middle)].add((value[win], value[wout]))
    return {m: frozenset(pairs) for m, pairs in table.items()}


def _compose(first: Pairs, second: Pairs) -> Pairs:
    return frozenset((a, c) for a, b in first for b2, c in second if b == b2)


def ring(relation: Relation, win: str, wout: str, k: int) -> Relation:
    """The relation on the middle distinctions of k copies joined in a ring, witnesses forgotten."""
    if k < 1:
        raise ValueError("a ring has at least one copy")
    middle = _middle(relation, win, wout)
    table = transfers(relation, win, wout)
    names = tuple(f"{name}{i}" for i in range(k) for name in middle)
    rows = set()
    for pattern in product(list(table), repeat=k):
        composed = DIAGONAL
        for m in pattern:
            composed = _compose(composed, table[m])
        if composed & DIAGONAL:
            rows.add(tuple(bit for m in pattern for bit in m))
    return Relation(names, frozenset(rows))


def network(relation: Relation, win: str, wout: str, edges: Sequence[tuple[int, int]]) -> Relation:
    """One copy per edge (witness in at the first vertex, out at the second), witnesses forgotten."""
    middle = _middle(relation, win, wout)
    table = transfers(relation, win, wout)
    vertices = sorted({v for edge in edges for v in edge})
    names = tuple(f"{name}_{u}{v}" for u, v in edges for name in middle)
    rows = set()
    for pattern in product(list(table), repeat=len(edges)):
        for witnesses in product((False, True), repeat=len(vertices)):
            at = dict(zip(vertices, witnesses))
            if all((at[u], at[v]) in table[m] for (u, v), m in zip(edges, pattern)):
                rows.add(tuple(bit for m in pattern for bit in m))
                break
    return Relation(names, frozenset(rows))


def memory(relation: Relation, win: str, wout: str) -> str:
    """Which ring lengths keep a constraint: 'every length', 'odd lengths' or 'never' (the ring theorem)."""
    table = transfers(relation, win, wout).values()
    has_swap, has_identity = SWAP in table, IDENTITY in table
    if has_swap and has_identity:
        return "every length"
    return "odd lengths" if has_swap else "never"


def bits(relation: Relation) -> float:
    """How much the relation remembers: log2 of all states over allowed states."""
    if not relation.rows:
        return math.inf
    return math.log2(2 ** len(relation.variables) / len(relation.rows))


def predicted_excluded(relation: Relation, win: str, wout: str, k: int) -> frozenset[tuple[bool, ...]]:
    """The ring theorem's excluded patterns: all transfers permutations, an odd number of swaps."""
    table = transfers(relation, win, wout)
    out = set()
    for pattern in product(list(table), repeat=k):
        pairs = [table[m] for m in pattern]
        if all(p in (IDENTITY, SWAP) for p in pairs) and sum(p == SWAP for p in pairs) % 2 == 1:
            out.add(tuple(bit for m in pattern for bit in m))
    return frozenset(out)
