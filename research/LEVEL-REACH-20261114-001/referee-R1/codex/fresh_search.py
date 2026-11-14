"""Exact least-bond search from finite relation semantics, independently written.

Bucket elimination compiles existence of an extension into a Boolean circuit
on dual-rail assumption selectors. The SAT master sets that circuit false.
Cardinality bounds prove absence of smaller forbidden partial assignments;
nonminimal supports are removed only after an explicit projection check.
There is no import of the study search, no assumed ruler formula, and no
incidence-forest shortcut. Width/time limits return undecided, never > cap.
"""
from __future__ import annotations
import heapq
import itertools
import time
from collections import defaultdict
from pysat.solvers import Solver
from pysat.card import ITotalizer
from fresh_pattern import cnf, components


class Limit(Exception):
    pass


def elimination_order(knots, nvars, width_limit):
    adj = [set() for _ in range(nvars)]
    for row in knots:
        for a in row:
            adj[a].update(v for v in row if v != a)
    heap = [(len(a), v) for v, a in enumerate(adj)]
    heapq.heapify(heap)
    alive = set(range(nvars))
    order = []
    width = 0
    while heap:
        degree, v = heapq.heappop(heap)
        if v not in alive or degree != len(adj[v]):
            continue
        ns = sorted(adj[v])
        width = max(width, len(ns))
        if width > width_limit:
            raise Limit(f'elimination width {width} exceeds {width_limit}')
        order.append(v)
        alive.remove(v)
        for a in ns:
            adj[a].remove(v)
            adj[a].update(x for x in ns if x != a)
            heapq.heappush(heap, (len(adj[a]), a))
        adj[v].clear()
    assert len(order) == nvars
    return order, width


class Circuit:
    def __init__(self, nvars, deadline, gate_limit):
        self.top = 2*nvars
        self.clauses = []
        self.memo = {}
        self.deadline = deadline
        self.gate_limit = gate_limit
        # Constants use Python booleans; native literals are nonzero ints.

    def gate(self, op, entries):
        unit, zero = (True, False) if op == 'and' else (False, True)
        vals = set()
        for x in entries:
            if x is zero:
                return zero
            if x is unit:
                continue
            if -x in vals:
                return zero
            vals.add(x)
        if not vals:
            return unit
        if len(vals) == 1:
            return next(iter(vals))
        args = tuple(sorted(vals))
        key = (op, args)
        if key in self.memo:
            return self.memo[key]
        if len(self.memo) >= self.gate_limit or time.monotonic() > self.deadline:
            raise Limit('circuit gate/time limit')
        self.top += 1
        g = self.top
        if op == 'and':
            self.clauses.extend([[-g, x] for x in args])
            self.clauses.append([g] + [-x for x in args])
        else:
            self.clauses.extend([[g, -x] for x in args])
            self.clauses.append([-g] + list(args))
        self.memo[key] = g
        return g


def compile_existence(knots, nvars, deadline, width_limit=8, gate_limit=500000):
    order, width = elimination_order(knots, nvars, width_limit)
    rank = {v: i for i, v in enumerate(order)}
    buckets = [[] for _ in order]
    circuit = Circuit(nvars, deadline, gate_limit)
    roots = []
    def store(scope, table):
        if not scope:
            roots.append(table[0])
        else:
            buckets[min(rank[v] for v in scope)].append((scope, table))
    for v in range(nvars):
        # selector 2v+1 chooses state0; 2v+2 chooses state1.
        store((v,), (-(2*v+2), -(2*v+1)))
    for row in knots:
        store(tuple(row), tuple(mask not in (0, 7) for mask in range(8)))
    entries = 0
    for oi, v in enumerate(order):
        if time.monotonic() > deadline:
            raise Limit('compilation deadline')
        factors = buckets[oi]
        joint = sorted({x for scope, _ in factors for x in scope})
        rest = tuple(x for x in joint if x != v)
        assert len(rest) <= width_limit
        projections = []
        for scope, table in factors:
            projections.append(([(rest.index(x) if x != v else -1) for x in scope], table))
        result = []
        for mask in range(1 << len(rest)):
            branches = []
            for bit in (0, 1):
                terms = []
                for positions, table in projections:
                    index = sum(((bit if p == -1 else (mask >> p) & 1) << j)
                                for j, p in enumerate(positions))
                    terms.append(table[index])
                branches.append(circuit.gate('and', terms))
            result.append(circuit.gate('or', branches))
        entries += len(result)
        store(rest, tuple(result))
        buckets[oi] = []
    root = circuit.gate('and', roots)
    return circuit, root, {'width': width, 'gates': len(circuit.memo), 'entries': entries,
                           'circuit_clauses': len(circuit.clauses), 'variables': nvars}


def projection_full(solver, support, deadline):
    """All assignments, modulo complement symmetry; valid for NAE formulas."""
    if not support:
        return solver.solve(), 1, None
    calls = 0
    for mask in range(1 << (len(support)-1)):
        if time.monotonic() > deadline:
            raise Limit('projection deadline')
        values = [0] + [(mask >> i) & 1 for i in range(len(support)-1)]
        ass = [(v+1) if b else -(v+1) for v, b in zip(support, values)]
        calls += 1
        if not solver.solve(assumptions=ass):
            return False, calls, values
    return True, calls, None


def search(knots, nvars, A, B, cap=10, seconds=90, width_limit=8,
           precompiled=None, model_name='cadical195', allowed=None):
    start = time.monotonic()
    deadline = start + seconds
    stats = {'method': 'fresh bucket-elimination existence circuit plus cardinality SAT',
             'cap': cap, 'candidates': 0, 'projection_calls': 0, 'blocked_supports': [],
             'exhausted_sizes': []}
    base = Solver(name=model_name, bootstrap_with=cnf(knots))
    master = None
    total = None
    try:
        if not base.solve():
            return {'L': 'dead', 'exact': True, 'stats': stats}
        comp = components(knots, nvars)
        common = {comp[v] for v in A} & {comp[v] for v in B}
        if not common:
            return {'L': 'none', 'exact': True, 'stats': stats}
        valid = [v for v in range(nvars) if comp[v] in common and
                 (allowed is None or v in allowed)]
        valid_set = set(valid)
        A = sorted(set(A) & valid_set)
        B = sorted(set(B) & valid_set)
        if precompiled is None:
            circuit, root, compilation = compile_existence(knots, nvars, deadline, width_limit)
        else:
            circuit, root, compilation = precompiled
        stats['compilation'] = compilation
        clauses = list(circuit.clauses)
        if root is True:
            return {'L': f'> {cap}', 'exact': True, 'stats': stats}
        if root is not False:
            clauses.append([-root])
        top = circuit.top
        presence = {}
        for v in range(nvars):
            a,b = 2*v+1, 2*v+2
            clauses.append([-a,-b])
            if v not in valid_set:
                clauses.extend([[-a],[-b]])
            else:
                top += 1
                p = presence[v] = top
                clauses.extend([[-a,p],[-b,p],[-p,a,b]])
        clauses.extend([[presence[v] for v in A], [presence[v] for v in B]])
        # A native NAE triple is always nonfull. If it does not itself meet
        # both designated levels, no cross bond may contain that triple.
        aset,bset = set(A),set(B)
        native_blocks = 0
        for row in knots:
            support = set(row)
            if support <= valid_set and not (support & aset and support & bset):
                clauses.append([-presence[v] for v in row])
                native_blocks += 1
        stats['native_nonfull_support_blocks'] = native_blocks
        # All selected members of a bond are in one constraint component.
        if len(common) > 1:
            groups = {}
            for c in sorted(common):
                top += 1
                groups[c] = top
            for v in valid:
                clauses.append([-presence[v],groups[comp[v]]])
            gs = list(groups.values())
            for i,g in enumerate(gs):
                clauses.extend([[-g,-h] for h in gs[i+1:]])
        total = ITotalizer(lits=list(presence.values()), ubound=min(cap,len(presence)), top_id=top)
        clauses.extend(total.cnf.clauses)
        master = Solver(name=model_name, bootstrap_with=clauses)
        for k in range(2, min(cap,len(presence)) + 1):
            bound = [-total.rhs[k]] if k < len(total.rhs) else []
            while True:
                if time.monotonic() > deadline:
                    raise Limit('master deadline')
                # Interrupt at bounded conflict slices to honor wall-clock envelope.
                master.conf_budget(20000)
                sat = master.solve_limited(assumptions=bound)
                if sat is None:
                    if time.monotonic() > deadline:
                        raise Limit('master SAT deadline')
                    continue
                if not sat:
                    stats['exhausted_sizes'].append(k)
                    break
                positive = {l for l in master.get_model() if l > 0}
                support = [v for v in valid if presence[v] in positive]
                values = [int(2*v+2 in positive) for v in support]
                assumptions = [(v+1) if b else -(v+1) for v,b in zip(support,values)]
                assert len(support) <= k and not base.solve(assumptions=assumptions), 'bad compiler'
                stats['candidates'] += 1
                bad = None
                for v in support:
                    subset = [x for x in support if x != v]
                    full, calls, _ = projection_full(base, subset, deadline)
                    stats['projection_calls'] += calls
                    if not full:
                        bad = subset
                        break
                if bad is None:
                    stats['seconds'] = time.monotonic()-start
                    return {'L': len(support), 'bond': support, 'forbidden_assignment': values,
                            'exact': True, 'stats': stats}
                # Every superset of this nonfull proper subset fails support-minimality.
                # Shrink it to avoid wasting time on other supersets.
                for v in list(bad):
                    trial = [x for x in bad if x != v]
                    full, calls, _ = projection_full(base, trial, deadline)
                    stats['projection_calls'] += calls
                    if not full:
                        bad = trial
                stats['blocked_supports'].append(bad)
                master.add_clause([-presence[v] for v in bad])
        stats['seconds'] = time.monotonic()-start
        return {'L': f'> {cap}', 'exact': True, 'stats': stats}
    except Limit as e:
        stats['seconds'] = time.monotonic()-start
        return {'L': 'undecided', 'exact': False, 'reason': str(e), 'stats': stats}
    finally:
        base.delete()
        if master is not None:
            master.delete()
        if total is not None:
            total.delete()


def levels(k0, s):
    return list(range((1<<k0)-1,(1<<(k0+1))-1)), list(range((1<<(k0+s))-1,(1<<(k0+s+1))-1))
