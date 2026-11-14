"""Fresh CNF unfolding for CARRY-BOUND R1; no per-call relation code.

The only reused search implementation is the explicitly permitted older
FREE-TARGET referee's DirectSearch class, extracted without its imports or
its producer-language loader. Boundary port masks are greatest fixed points
of the definition equations, computed here by local assignment enumeration.
"""
from __future__ import annotations
import ast
import gzip
import hashlib
import itertools
import json
import math
import random
import resource
import threading
import time
from pathlib import Path
from pysat.solvers import Solver
from pysat.card import CardEnc, EncType

ROOT = Path('/home/jscul/p-vs-np-contact-first')
HERE = ROOT / 'research/CARRY-BOUND-20261114-001/referee-R1/codex'
OLD = ROOT / 'research/FREE-TARGET-20261114-001/referee-R1/codex/direct_bonds.py'
READS = {}


def read(path):
    path = Path(path)
    relative = str(path.relative_to(ROOT))
    assert not (path.suffix == '.py' and relative.startswith((
        'experiments/CARRY-BOUND-20261114-001A/',
        'proofs/CARRY-BOUND-20261114-001Z/')))
    data = path.read_bytes()
    READS[relative] = hashlib.sha256(data).hexdigest()
    return data


def rows(path):
    raw = read(path)
    if str(path).endswith('.gz'):
        raw = gzip.decompress(raw)
    return [json.loads(line) for line in raw.splitlines() if line.strip()]


# Reuse the old exact cube-enumeration/CEGAR search, not its input pipeline.
_tree = ast.parse(read(OLD), filename=str(OLD))
_tree.body = [x for x in _tree.body if isinstance(x, (ast.ClassDef, ast.FunctionDef))
              and x.name in {'SearchTimeout', 'DirectSearch', 'controls'}]
exec(compile(_tree, str(OLD), 'exec'), globals())


def usual(raw):
    result = []
    for arity, own, calls in raw:
        calls = [(c, tuple(a)) for c, a in calls]
        if any(c == 'SELF' and sorted(a) == [0, 1, 2] for c, a in calls):
            calls.append(('K', (0, 1, 2)))
        result.append((arity, own, calls))
    return result


def bits(state, args):
    return sum(((state >> v) & 1) << j for j, v in enumerate(args))


def limits(defs):
    """Only local port masks, never a relation between copies."""
    types = {i for i, d in enumerate(defs) if any(c == 'SELF' for c, _ in d[2])}
    previous = {i: set(range(1 << defs[i][0])) for i in types}
    history = []
    while True:
        allowed = []
        for i, (arity, own, calls) in enumerate(defs):
            good = set()
            for state in range(1 << (arity + own)):
                if all(bits(state, a) not in (0, 7) if c == 'K' else
                       bits(state, a) in (previous[i] if c == 'SELF' else allowed[c])
                       for c, a in calls):
                    good.add(state & ((1 << arity) - 1))
            allowed.append(good)
        current = {i: allowed[i] for i in types}
        history.append({str(i): sorted(v) for i, v in current.items()})
        assert all(current[i] <= previous[i] for i in types)
        if current == previous:
            return allowed, history
        previous = current


def flatten(defs, definition):
    types = {i for i, d in enumerate(defs) if any(c == 'SELF' for c, _ in d[2])}
    next_id = defs[definition][0]
    calls = []

    def expand(i, ports):
        nonlocal next_id
        arity, own, body = defs[i]
        env = list(ports) + list(range(next_id, next_id + own))
        next_id += own
        for c, args in body:
            a = tuple(env[j] for j in args)
            if c == 'K':
                calls.append(('K', a))
            elif c == 'SELF':
                calls.append((i, a))
            elif c in types:
                calls.append((c, a))
            else:
                expand(c, a)
    expand(definition, range(defs[definition][0]))
    return next_id, calls


def forbid(ports, allowed):
    return [[-(v + 1) if (state >> j) & 1 else v + 1
             for j, v in enumerate(ports)]
            for state in range(1 << len(ports)) if state not in allowed]


def unfold(defs, allowed, S, cutoff, target_depth):
    """All covered copies in the prefix; targets are precisely S own members.

    Other recursive definitions have no own members in the in-scope sample;
    their exact port mask eliminates their subtrees without losing members.
    Main=S is at depth 0; a wrapper enters S at absolute depth 1.
    """
    main = len(defs) - 1
    blocks = {i: flatten(defs, i) for i in range(len(defs))}
    n = defs[main][0]
    clauses, copies, origin = [], [], {}
    roots, targets = set(range(n)), set()
    active_boundary = []

    def visit(i, ports, depth, address):
        nonlocal n
        size, body = blocks[i]
        arity = defs[i][0]
        own = list(range(n, n + size - arity))
        n += len(own)
        env = list(ports) + own
        copy = {'definition': i, 'depth': depth, 'address': list(address),
                'ports': list(ports), 'own': own}
        copies.append(copy)
        for v in own:
            origin[v] = {'definition': i, 'depth': depth, 'address': list(address)}
        if i == S and depth == target_depth:
            targets.update(own)
        for j, (c, arguments) in enumerate(body):
            a = [env[v] for v in arguments]
            if c == 'K':
                clauses.extend(([v + 1 for v in a], [-(v + 1) for v in a]))
            elif c == S:
                child_depth = depth + 1 if i == S else 1
                if child_depth <= cutoff:
                    visit(c, a, child_depth, address + (j,))
                else:
                    clauses.extend(forbid(a, allowed[c]))
                    active_boundary.append({'ports': a, 'depth': child_depth})
            else:
                assert blocks[c][0] == defs[c][0], 'noncovered own members in scope'
                clauses.extend(forbid(a, allowed[c]))
    visit(main, list(roots), 0, ())
    return clauses, n, roots, targets, copies, origin, active_boundary


def preferred_pools(copies, roots, S, target_depth):
    pools = []
    for c in copies:
        if c['definition'] != S or c['depth'] != target_depth:
            continue
        address = c['address']
        pool = set(roots)
        for a in copies:
            prefix = a['address']
            if len(prefix) <= len(address) and address[:len(prefix)] == prefix:
                pool.update(a['ports']); pool.update(a['own'])
        pools.append(pool)
    return pools
