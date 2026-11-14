"""Exact minimum forbidden-support search, followed by full bond tests.

The general engine enumerates cardinalities, with a SAT implicit hitting set
over signed unit selectors. A checked total state excludes every candidate
it satisfies. Failed bond tests exclude all supersets of a nonfull proper
support, locally to this query. Exhaustion is a SAT UNSAT result at k_max,
never a sample of supports. An incidence-forest reduction handles tree rulers.
"""
from collections import OrderedDict, deque
import itertools
from pathlib import Path
import threading
import time

import numpy as np
from pysat.card import CardEnc, EncType
from pysat.solvers import Minisat22

from certificates import (BudgetExpired, checked_refutation, model_from_literals,
                          pack_state, seconds_left)
from pattern import clauses, components, level

# Optional witness memoization, separate from the exact formula and each
# query's correction/exclusion clauses. Misses recompute through the SAT
# oracle; saturation may affect timing, never an exhaustion verdict.
MAX_RETAINED_MODELS = 512
MAX_SAT_CACHE = 20000
MAX_PROJECTION_CACHE = 1024


class SearchEngine:
    def __init__(self, K, nvars, workdir, certify=True, tree_optimization=True,
                 compiled_optimization=True):
        self.K = np.asarray(K, dtype=np.int64).reshape((-1, 3))
        self.nvars = int(nvars)
        self.workdir = Path(workdir)
        self.workdir.mkdir(parents=True, exist_ok=True)
        self.certify = certify
        self.tree_optimization = tree_optimization
        self.compiled_optimization = compiled_optimization
        self.compiled = None
        self.solver = Minisat22(bootstrap_with=clauses(self.K))
        self.alive = self.solver.solve()
        self.models = []
        self.model_set = set()
        self.sat_cache = OrderedDict()
        self.projection_cache = OrderedDict()
        self.proved_bounds = []
        self.nonfull_supports = {tuple(map(int, row)) for row in self.K}
        self.local_resolution_ready = False
        self._coverage_columns = [0] * self.nvars
        self._coverage_seen = 0
        self.labels = components(self.K, nvars)
        self.sat_calls = 1
        self._active = [self.solver]
        self._expired = False
        self._timer = None
        self.forest = self._is_forest()
        if self.alive:
            self._remember(self._checked_model(self.solver.get_model() or []))

    def close(self):
        if self._timer:
            self._timer.cancel()
            self._timer.join()
            self._timer = None
        # Timer.function and the compiler's deadline callback both refer
        # back to this engine. Detach them when its computation is over so
        # completed-engine caches do not survive into the next computation.
        self.compiled = None
        self.solver.delete()

    def _checked_model(self, literals, units=()):
        state = model_from_literals(literals, self.nvars)
        val = np.asarray(state, dtype=np.int8)
        if len(self.K):
            seen = val[self.K]
            assert np.all(seen.min(axis=1) != seen.max(axis=1)), 'search solver returned bad state'
        assert all(state[abs(l) - 1] == int(l > 0) for l in units)
        return state

    def _remember(self, state):
        bits = sum(b << v for v, b in enumerate(state))
        # Stable indices are required by coverage columns. Keep the pool
        # append-only and return every actual state even after saturation.
        if len(self.models) < MAX_RETAINED_MODELS and bits not in self.model_set:
            self.model_set.add(bits)
            self.models.append(bits)
        return bits

    def _covered(self, support):
        """Checked total states can prove fullness, never nonfullness."""
        while self._coverage_seen < len(self.models):
            bits = self.models[self._coverage_seen]
            flag = 1 << self._coverage_seen
            for v in range(self.nvars):
                if (bits >> v) & 1:
                    self._coverage_columns[v] |= flag
            self._coverage_seen += 1
        cells = [(1 << self._coverage_seen) - 1]
        first = self._coverage_columns[support[0]]
        mask = cells[0]
        for v in support[1:]:
            diff = first ^ self._coverage_columns[v]
            refined = []
            for cell in cells:
                zero, one = cell & (mask ^ diff), cell & diff
                if not zero or not one:
                    return False
                refined.extend((zero, one))
            cells = refined
        return True

    def _interrupt(self):
        self._expired = True
        for solver in self._active:
            try:
                solver.interrupt()
            except Exception:
                pass

    def _check_time(self, deadline):
        if self._expired:
            raise BudgetExpired('query deadline')
        seconds_left(deadline)

    def oracle(self, units, deadline):
        """Return a checked total state or None for a forbidden assignment."""
        self._check_time(deadline)
        units = tuple(sorted(map(int, units), key=abs))
        invert = bool(units and units[0] > 0)
        canonical = tuple(-l for l in units) if invert else units
        if canonical in self.sat_cache:
            bits = self.sat_cache[canonical]
            self.sat_cache.move_to_end(canonical)
        else:
            self.sat_calls += 1
            answer = self.solver.solve_limited(assumptions=list(canonical), expect_interrupt=True)
            if answer is None:
                raise BudgetExpired('interrupted pattern SAT query')
            if answer:
                state = self._checked_model(self.solver.get_model() or [], canonical)
                bits = self._remember(state)
            else:
                bits = None
            self.sat_cache[canonical] = bits
            if len(self.sat_cache) > MAX_SAT_CACHE:
                self.sat_cache.popitem(last=False)
        if bits is None:
            return None
        if invert:
            bits ^= (1 << self.nvars) - 1
        return [(bits >> v) & 1 for v in range(self.nvars)]

    def projection(self, support, deadline):
        support = tuple(sorted(support))
        if support in self.projection_cache:
            self.projection_cache.move_to_end(support)
            return self.projection_cache[support]
        states = []
        for assignment in range(1 << len(support)):
            units = [v + 1 if (assignment >> j) & 1 else -v - 1 for j, v in enumerate(support)]
            state = self.oracle(units, deadline)
            if state is None:
                answer = (False, units)
                self.projection_cache[support] = answer
                if len(self.projection_cache) > MAX_PROJECTION_CACHE:
                    self.projection_cache.popitem(last=False)
                return answer
            states.append(pack_state(state))
        answer = (True, states)
        self.projection_cache[support] = answer
        if len(self.projection_cache) > MAX_PROJECTION_CACHE:
            self.projection_cache.popitem(last=False)
        return answer

    def _bond_test(self, support, deadline):
        proper = []
        for i in range(len(support)):
            subset = support[:i] + support[i + 1:]
            full, evidence = self.projection(subset, deadline)
            if not full:
                # An unsatisfiable partial assignment on this proper support
                # suffices to block all of its supersets in THIS query.
                # Reduce a witnessed forbidden assignment before blocking.
                # This preserves a known nonfull support and removes many
                # equivalent failures caused by one small local constraint.
                units = list(evidence)
                for literal in tuple(units):
                    trial = [l for l in units if l != literal]
                    if self.oracle(trial, deadline) is None:
                        units = trial
                reduced = tuple(sorted(abs(l) - 1 for l in units))
                self.nonfull_supports.add(reduced)
                return False, list(reduced)
            proper.append((subset, evidence))
        return True, proper

    def _report_bond(self, support, units, proper, meta, deadline, corrupt_test=False):
        support = sorted(support)
        self.nonfull_supports.add(tuple(support))
        result = {'L': len(support), 'bond': support,
                  'forbidden_assignment': [int(l > 0) for l in sorted(units, key=abs)],
                  'optimality_proved': True, 'search': meta}
        if not self.certify:
            result['certificate'] = {'omitted': 'gate comparison only; no reported scientific bond'}
            return result
        refutation = checked_refutation(self.K, self.nvars, units, self.workdir, deadline, corrupt_test)
        pool, indices, maximal = [], {}, []
        count = 0
        for subset, states in proper:
            refs = []
            for packed in states:
                if packed not in indices:
                    indices[packed] = len(pool)
                    pool.append(packed)
                refs.append(indices[packed])
            maximal.append({'support': list(subset), 'state_indices': refs})
            count += len(states)
        result['certificate'] = {'refutation': refutation, 'state_encoding': 'little-endian bits, hex bytes; id v is bit v',
                                 'state_pool': pool, 'maximal_proper': maximal,
                                 'assignments_checked': count, 'all_maximal_projections_full': True}
        return result

    def _is_forest(self):
        """The exact reduction requires acyclic incidence AND variable degree<=2."""
        incident = [[] for _ in range(self.nvars)]
        for i, row in enumerate(self.K):
            for v in row:
                incident[int(v)].append(i)
        if any(len(xs) > 2 for xs in incident):
            return None
        parent = list(range(len(self.K)))

        def find(v):
            while parent[v] != v:
                parent[v] = parent[parent[v]]
                v = parent[v]
            return v

        for xs in incident:
            if len(xs) == 2:
                a, b = map(find, xs)
                if a == b:
                    return None
                parent[a] = b
        return incident

    def _forest_candidate(self, A, B, allowed):
        """Minimize factor count along A--B paths, an exact lower bound.

        In this incidence forest every minimal nonfull support is the
        boundary of a connected factor subtree H. If H has t factors, its
        boundary has t+2 variables. A shortest variable-to-variable path
        attains that bound when its boundary is in the candidate domain.
        See REPORT for the elimination argument; SAT verifies the candidate.
        """
        if self.forest is None:
            return None
        targets = set(B)
        queue = deque(sorted(A))
        previous = {v: None for v in queue}
        found = None
        while queue:
            node = queue.popleft()
            if node < self.nvars and node in targets:
                found = node
                break
            neighbors = ([self.nvars + f for f in self.forest[node]] if node < self.nvars
                         else map(int, self.K[node - self.nvars]))
            for target in neighbors:
                if target not in previous:
                    previous[target] = node
                    queue.append(target)
        if found is None:
            return None
        path = []
        while found is not None:
            if found >= self.nvars:
                path.append(found - self.nvars)
            found = previous[found]
        path.reverse()
        if not path:
            return None
        count, color = {}, {}
        for j, f in enumerate(path):
            for v in map(int, self.K[f]):
                count[v] = count.get(v, 0) + 1
                color[v] = j % 2
        support = sorted(v for v, degree in count.items() if degree == 1)
        if not set(support) <= allowed:
            return None  # The lower bound alone is insufficient; use IHS.
        assert len(support) == len(path) + 2
        units = [v + 1 if color[v] else -v - 1 for v in support]
        return support, units, len(path)

    def _seed_models(self, deadline, count=24):
        # Checked phase-varied states only speed up the hitting-set search.
        # Neither their absence nor their count establishes exhaustion.
        import random
        rng = random.Random('LEVEL-REACH-CEGAR-initial-models')
        for _ in range(count):
            self._check_time(deadline)
            self.solver.set_phases([v + 1 if rng.getrandbits(1) else -v - 1 for v in range(self.nvars)])
            self.sat_calls += 1
            answer = self.solver.solve_limited(expect_interrupt=True)
            if answer is None:
                raise BudgetExpired('model-seeding deadline')
            assert answer
            self._remember(self._checked_model(self.solver.get_model() or []))

    def _compiled_search(self, A, B, domain, kmax, deadline, corrupt_test):
        """Exact existential-elimination circuit when fill width is small.

        The circuit's root means that the original NAE formula has a state
        extending the selected units. Requiring its negation searches all
        forbidden candidates directly, in increasing cardinality. It is
        an alternative exact minimum-forbidden-assignment engine, retaining
        the same original-formula minimality tests and LRAT certificates.
        """
        from compiled_search import CompiledPattern
        if not self.local_resolution_ready:
            self._local_resolution_facts(deadline)
        if self.compiled is None:
            self.compiled = CompiledPattern(self.K, self.nvars, width_limit=7, gate_limit=500000,
                                            check=lambda: self._check_time(deadline))
        compiled = self.compiled
        self._check_time(deadline)
        if not compiled.available:
            return None
        root = compiled.root
        assert type(root) is not bool or root, 'alive union compiled to false'
        if root is True:
            return {'L': f'> {kmax}', 'optimality_proved': True,
                    'search': {'method': 'exact existential-elimination circuit',
                               'exhausted_through': kmax, 'constant_full_relation': True,
                               'compilation': compiled.stats}}
        domain_set = set(domain)
        hard = [[-root]]
        selected = []
        for v in range(self.nvars):
            zero, one = 2 * v + 1, 2 * v + 2
            hard.append([-zero, -one])
            if v not in domain_set:
                hard.extend(([-zero], [-one]))
            else:
                selected.extend((zero, one))
        hard.append([compiled.presence[v] for v in A])
        hard.append([compiled.presence[v] for v in B])
        # Facts may be shared across queries; their eligibility may not.
        # A nonfull support missing A or B can never be contained in a
        # desired bond. Never inclusively block an eligible known support.
        aset, bset = set(A), set(B)
        blocked = [[-compiled.presence[v] for v in support]
                   for support in sorted(self.nonfull_supports)
                   if set(support) <= domain_set
                   and not (set(support) & aset and set(support) & bset)]
        candidates = 0
        for size in range(2, kmax + 1):
            self._check_time(deadline)
            cardinality = CardEnc.atmost(selected, bound=size, top_id=compiled.top_id,
                                        encoding=EncType.seqcounter)
            with Minisat22(bootstrap_with=compiled.clauses + hard + blocked + cardinality.clauses) as candidate_solver:
                self._active = [self.solver, candidate_solver]
                while True:
                    self._check_time(deadline)
                    answer = candidate_solver.solve_limited(expect_interrupt=True)
                    if answer is None:
                        raise BudgetExpired('interrupted compiled candidate search')
                    if not answer:
                        break
                    candidates += 1
                    positive = {l for l in candidate_solver.get_model() if l > 0}
                    units = [v + 1 if 2 * v + 2 in positive else -v - 1
                             for v in domain if 2 * v + 1 in positive or 2 * v + 2 in positive]
                    support = sorted(abs(l) - 1 for l in units)
                    assert self.oracle(units, deadline) is None, 'compiled forbidden assignment is SAT'
                    valid, proper = self._bond_test(support, deadline)
                    if valid:
                        return self._report_bond(support, units, proper,
                                                 {'method': 'exact existential-elimination circuit',
                                                  'exhausted_smaller_sizes': list(range(2, len(support))),
                                                  'candidate_limit': size, 'candidates': candidates,
                                                  'query_local_blockers': len(blocked),
                                                  'compilation': compiled.stats}, deadline, corrupt_test)
                    blocker = [-compiled.presence[v] for v in proper]
                    blocked.append(blocker)
                    candidate_solver.add_clause(blocker)
            self._active = [self.solver]
        return {'L': f'> {kmax}', 'optimality_proved': True,
                'search': {'method': 'exact existential-elimination circuit', 'exhausted_through': kmax,
                           'exhaustion': 'exact state-existence circuit with root=false: candidate CNF UNSAT through k_max',
                           'candidates': candidates, 'query_local_blockers': len(blocked),
                           'compilation': compiled.stats}}

    def _local_resolution_facts(self, deadline):
        """Safe nonfull-support pruning from at most three NAE clauses.

        Ordinary resolution preserves implication. No completeness claim is
        made for these bounded rounds: they only pre-exclude known nonfull
        supports that are ineligible for the current query. The exact
        circuit/hitting-set search still establishes every lower bound.
        """
        incident = [[] for _ in range(self.nvars)]
        rows = [tuple(map(int, row)) for row in self.K]
        for i, row in enumerate(rows):
            for v in row:
                incident[v].append(i)
        derived = set()
        steps = 0
        for v, factors in enumerate(incident):
            for i, j in itertools.combinations(factors, 2):
                steps += 1
                if steps % 256 == 0:
                    self._check_time(deadline)
                first, second = set(rows[i]), set(rows[j])
                if first & second != {v}:
                    continue
                clause = frozenset([u + 1 for u in first - {v}] + [-u - 1 for u in second - {v}])
                derived.add(clause)
                derived.add(frozenset(-l for l in clause))
                self.nonfull_supports.add(tuple(sorted(abs(l) - 1 for l in clause)))
                if len(derived) >= 50000:
                    break
            if len(derived) >= 50000:
                break
        for clause in sorted(derived, key=lambda c: tuple(sorted(c))):
            for literal in sorted(clause):
                v = abs(literal) - 1
                for factor in incident[v]:
                    steps += 1
                    if steps % 256 == 0:
                        self._check_time(deadline)
                    # Pick the original NAE clause with the opposite pivot.
                    sign = -1 if literal > 0 else 1
                    other = {sign * (u + 1) for u in rows[factor]}
                    resolvent = (set(clause) - {literal}) | (other - {-literal})
                    if len(resolvent) > 5 or any(-l in resolvent for l in resolvent):
                        continue
                    self.nonfull_supports.add(tuple(sorted(abs(l) - 1 for l in resolvent)))
                    if len(self.nonfull_supports) >= 100000:
                        self.local_resolution_ready = True
                        return
        self.local_resolution_ready = True

    def search(self, A, B, allowed=None, kmax=10, deadline=None, corrupt_test=False):
        deadline = time.monotonic() + 300 if deadline is None else deadline
        start, calls = time.monotonic(), self.sat_calls
        self._expired = False
        self._timer = threading.Timer(max(0.001, deadline - start), self._interrupt)
        self._timer.daemon = True
        self._timer.start()
        result = None
        try:
            result = self._search(sorted(A), sorted(B), allowed, kmax, deadline, corrupt_test)
        except BudgetExpired as exc:
            result = {'L': 'undecided', 'optimality_proved': False, 'reason': str(exc)}
        finally:
            self._timer.cancel()
            self._timer.join()
            self.solver.clear_interrupt()
            self._active = [self.solver]
        result['seconds'] = time.monotonic() - start
        result['sat_calls'] = self.sat_calls - calls
        return result

    def _search(self, A, B, allowed, kmax, deadline, corrupt_test):
        if not self.alive:
            return {'L': None, 'optimality_proved': False, 'reason': 'dead union: L undefined'}
        common = {self.labels[v] for v in A} & {self.labels[v] for v in B}
        if not common:
            return {'L': 'none', 'optimality_proved': True, 'search': {'method': 'disconnected components'}}
        domain = set(range(self.nvars)) if allowed is None else set(allowed)
        domain = sorted(v for v in domain if self.labels[v] in common)
        A, B = sorted(set(A) & set(domain)), sorted(set(B) & set(domain))
        assert A and B and not (set(A) & set(B)), 'query sets must be disjoint and nonempty in domain'
        Aset, Bset, domain_set = set(A), set(B), set(domain)
        lower = 2
        for old_a, old_b, old_domain, bound in self.proved_bounds:
            if Aset <= old_a and Bset <= old_b and domain_set <= old_domain:
                lower = max(lower, bound)
        if self.tree_optimization:
            candidate = self._forest_candidate(A, B, set(domain))
            if candidate:
                support, units, factors = candidate
                meta = {'method': 'exact incidence-forest boundary minimization', 'minimum_factors': factors,
                        'exhausted_smaller_sizes': list(range(2, len(support))),
                        'reason': 'every minimal nonfull support is boundary(H), size=number_of_factors(H)+2'}
                if len(support) > kmax:
                    return {'L': f'> {kmax}', 'optimality_proved': True, 'search': meta}
                assert self.oracle(units, deadline) is None
                valid, proper = self._bond_test(support, deadline)
                assert valid, 'incidence-forest reduction failed bond test'
                return self._report_bond(support, units, proper, meta, deadline, corrupt_test)

        if self.compiled_optimization:
            compiled_result = self._compiled_search(A, B, domain, kmax, deadline, corrupt_test)
            if compiled_result is not None:
                return compiled_result

        # Alive complement-invariant NAE has both values at every variable.
        # Thus every cross pair tested below is automatically a bond if nonfull.
        for a in A if lower < 3 else ():
            for b in B:
                self._check_time(deadline)
                for value in (0, 1):
                    units = [-a - 1, b + 1 if value else -b - 1]
                    if self.oracle(units, deadline) is None:
                        support = sorted((a, b))
                        valid, proper = self._bond_test(support, deadline)
                        assert valid
                        return self._report_bond(support, units, proper,
                                                 {'method': 'exhaustive cross pairs', 'lower_bound': 2}, deadline, corrupt_test)
        if kmax < 3:
            return {'L': f'> {kmax}', 'optimality_proved': True,
                    'search': {'method': 'exhaustive cross pairs', 'exhausted_through': kmax}}

        # This is merely an ordering shortcut at size three, after all pairs.
        self.proved_bounds.append((Aset, Bset, domain_set, 3))
        blocked = []
        for row in self.K:
            support = sorted(map(int, row))
            if lower < 4 and set(support) <= domain_set and set(support) & Aset and set(support) & Bset:
                valid, proper = self._bond_test(support, deadline)
                if valid:
                    units = [-v - 1 for v in support]
                    return self._report_bond(support, units, proper,
                                             {'method': 'size-three knot after exhaustive cross pairs', 'lower_bound': 3},
                                             deadline, corrupt_test)
                blocked.append(tuple(proper))

        # Enumerating cross triples is practical here (O(|A||B||domain|)).
        # Checked total states prove most projections full via four bitset
        # intersections; any uncovered assignment still goes to the SAT
        # oracle. This is exact exhaustion, not statistical coverage.
        if lower < 4:
            if len(self.models) < 128:
                self._seed_models(deadline, count=128)
            columns = [0] * self.nvars
            seen = 0

            def update_columns():
                nonlocal seen
                while seen < len(self.models):
                    bits = self.models[seen]
                    flag = 1 << seen
                    for v in domain:
                        if (bits >> v) & 1:
                            columns[v] |= flag
                    seen += 1

            update_columns()
            exhausted = 0
            for a in A:
                for b in B:
                    for c in domain:
                        if c == a or c == b or (c in Aset and c < a) or (c in Bset and c < b):
                            continue
                        exhausted += 1
                        if exhausted % 2048 == 0:
                            self._check_time(deadline)
                        mask = (1 << seen) - 1
                        x, y = columns[a] ^ columns[b], columns[a] ^ columns[c]
                        if (x & y) and (x & (mask ^ y)) and ((mask ^ x) & y) and ((mask ^ x) & (mask ^ y)):
                            continue
                        support = sorted((a, b, c))
                        if any(set(p) <= set(support) for p in blocked):
                            continue
                        full, evidence = self.projection(support, deadline)
                        update_columns()
                        if full:
                            continue
                        valid, proper = self._bond_test(support, deadline)
                        if valid:
                            return self._report_bond(support, evidence, proper,
                                                     {'method': 'exhaustive cross triples with checked-state bitsets',
                                                      'lower_bound': 3, 'triples_visited': exhausted},
                                                     deadline, corrupt_test)
                        blocked.append(tuple(proper))
            self.proved_bounds.append((Aset, Bset, domain_set, 4))
            lower = 4
        if kmax < 4:
            return {'L': f'> {kmax}', 'optimality_proved': True,
                    'search': {'method': 'exhaustive cross pairs and triples', 'exhausted_through': kmax}}

        # At the already-proved size-four lower bound, try two top and two
        # target variables first. This ordering shortcut makes no exhaustion
        # claim; the IHS still handles all other size-four supports.
        heuristic_target_pairs = list(itertools.combinations(B, 2))
        if len(B) == 1:
            b = B[0]
            heuristic_target_pairs = [(b, c) for c in domain if c != b and level(c) == level(b)]
        for top_pair in itertools.combinations(A, 2):
            for target_pair in heuristic_target_pairs:
                self._check_time(deadline)
                support = sorted(top_pair + target_pair)
                if self._covered(support):
                    continue
                full, evidence = self.projection(support, deadline)
                if full:
                    continue
                valid, proper = self._bond_test(support, deadline)
                if valid:
                    return self._report_bond(support, evidence, proper,
                                             {'method': 'size-four candidate ordering after exhaustive cross triples',
                                              'lower_bound': 4}, deadline, corrupt_test)
                blocked.append(tuple(proper))

        # Every original knot is a nonfull support. If it is ineligible for
        # this query, no eligible bond can contain it. Eligible knots were
        # tested above; never globally block an eligible known bond.
        for row in self.K:
            support = tuple(map(int, row))
            if set(support) <= domain_set and not (set(support) & Aset and set(support) & Bset):
                blocked.append(support)

        if len(self.models) < 24:
            self._seed_models(deadline)
        positions = {v: i for i, v in enumerate(domain)}
        selectors = lambda v: (2 * positions[v] + 1, 2 * positions[v] + 2)
        count_vars = 2 * len(domain)
        presence = {v: count_vars + i + 1 for i, v in enumerate(domain)}
        base = [[-selectors(v)[0], -selectors(v)[1]] for v in domain]
        for v in domain:
            zero, one = selectors(v)
            present = presence[v]
            base.extend(([-zero, present], [-one, present], [-present, zero, one]))
        base.extend(([s for v in A for s in selectors(v)], [s for v in B for s in selectors(v)]))
        corrections, model_seen, iterations = [], set(), 0

        def add_model(bits):
            for complement in (False, True):
                signed_bits = bits ^ ((1 << self.nvars) - 1) if complement else bits
                signature = tuple((signed_bits >> v) & 1 for v in domain)
                if signature in model_seen:
                    continue
                model_seen.add(signature)
                correction = [selectors(v)[1 - signature[i]] for i, v in enumerate(domain)]
                corrections.append(correction)

        for bits in self.models:
            add_model(bits)
        for size in range(max(4, lower), kmax + 1):
            self._check_time(deadline)
            cardinality = CardEnc.atmost(list(range(1, count_vars + 1)), bound=size,
                                        top_id=3 * len(domain), encoding=EncType.seqcounter)
            hard = base + corrections + cardinality.clauses
            # Each support exclusion stays query-local. Presence is exactly
            # the disjunction of its two selectors, avoiding a 2**|p| clause
            # expansion without restricting any additional assignment.
            for p in blocked:
                hard.append([-presence[v] for v in p])
            with Minisat22(bootstrap_with=hard) as hitting:
                self._active = [self.solver, hitting]
                added = len(corrections)
                while True:
                    self._check_time(deadline)
                    answer = hitting.solve_limited(expect_interrupt=True)
                    if answer is None:
                        raise BudgetExpired('interrupted minimum hitting set')
                    if not answer:
                        break  # All forbidden candidates of size<=size exhausted.
                    iterations += 1
                    selected = {lit for lit in hitting.get_model() if 0 < lit <= count_vars}
                    units = [v + 1 if selectors(v)[1] in selected else -v - 1
                             for v in domain if any(x in selected for x in selectors(v))]
                    support = sorted(abs(l) - 1 for l in units)
                    state = self.oracle(units, deadline)
                    if state is not None:
                        before = len(corrections)
                        add_model(self._remember(state))
                        assert len(corrections) > before, 'correction failed to exclude SAT candidate'
                        for correction in corrections[added:]:
                            hitting.add_clause(correction)
                        added = len(corrections)
                        continue
                    valid, proper = self._bond_test(support, deadline)
                    if valid:
                        return self._report_bond(support, units, proper,
                                                 {'method': 'cardinality-first implicit hitting set',
                                                  'exhausted_smaller_sizes': list(range(2, len(support))),
                                                  'correction_sets': len(corrections), 'candidates': iterations,
                                                  'candidate_limit': size, 'query_local_blockers': len(blocked)},
                                                 deadline, corrupt_test)
                    p = tuple(proper)
                    blocked.append(p)
                    hitting.add_clause([-presence[v] for v in p])
            self._active = [self.solver]
        return {'L': f'> {kmax}', 'optimality_proved': True,
                'search': {'method': 'cardinality-first implicit hitting set', 'exhausted_through': kmax,
                           'exhaustion': 'candidate SAT formula UNSAT at every size through k_max',
                           'correction_sets': len(corrections), 'candidates': iterations,
                           'query_local_blockers': len(blocked)}}
