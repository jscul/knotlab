"""Replay the frozen enumeration order only for the three truncated census listings."""

import ast

from pysat.card import CardEnc, EncType
from pysat.solvers import Solver

from minimal_count import bits
from minimal_measure import cross_pair


def frozen_backend(path):
    # Read the declared back end without executing any of the study's code.
    tree = ast.parse(path.read_text())
    listing = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "listing")
    call = next(node for node in ast.walk(listing)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "Solver")
    return next(ast.literal_eval(param.value) for param in call.keywords if param.arg == "name")


def archive_prefix(source, code, size, sign, limit, backend):
    width = len(code.columns)
    clauses = []
    top = width

    def constrain_parity(row, sign):
        nonlocal top
        literals = [i + 1 for i in bits(row)]
        if not literals:
            if sign:
                clauses.append([])
            return
        existing, *rest = literals
        for incoming in rest:
            top += 1
            clauses.extend((
                [-top, existing, incoming], [-top, -existing, -incoming],
                [top, -existing, incoming], [top, existing, -incoming],
            ))
            existing = top
        clauses.append([existing] if sign else [-existing])

    # The frozen listing ordered its parity rows by first encounter in
    # value-pair order, holding one index fixed while varying the second.
    rows = {}
    for i, (a, c, b, d) in enumerate(code.cycles):
        for u, v in ((a, c), (a, d), (b, c), (b, d)):
            pair = cross_pair(u, v)
            rows[pair] = rows.get(pair, 0) | (1 << i)
    assert sorted(rows.values()) == sorted(row for row in code.checks if row)
    for row in rows.values():
        constrain_parity(row, 0)
    constrain_parity(code.cost, sign)
    for value in range(1 + max(d for support in source["supports"] for d in support)):
        literals = [i + 1 for i, pair in enumerate(source["pairs"]) if value in pair]
        if len(literals) >= 2:
            restriction = CardEnc.atmost(lits=literals, bound=1, top_id=top, encoding=EncType.seqcounter)
            top = max(top, restriction.nv)
            clauses.extend(restriction.clauses)
    restriction = CardEnc.equals(
        lits=list(range(1, width + 1)), bound=size, top_id=top, encoding=EncType.seqcounter,
    )
    clauses.extend(restriction.clauses)
    words = set()
    with Solver(name=backend, bootstrap_with=clauses) as solver:
        for _ in range(limit):
            solver.conf_budget(2_000_000)
            assert solver.solve_limited() is True
            chosen = [literal for literal in solver.get_model() if 0 < literal <= width]
            word = sum(1 << (literal - 1) for literal in chosen)
            assert word not in words and word.bit_count() == size
            words.add(word)
            solver.add_clause([-literal for literal in sorted(chosen)])
    return words
