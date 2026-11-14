"""Fresh Lemma W audit; standard library plus installed PySAT only.

No producer Python is read or imported. Semantics are reconstructed from the
frozen notes and the earlier permitted referee's finite-description semantics.
Window enumeration and selected-path/all-copy CNF are separate computations.
"""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
import os
import resource
import time
from pathlib import Path

for variable in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[variable] = '1'
resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, 2 * 1024**3))
from pysat.solvers import Solver

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
INPUT = HERE / 'window_inputs.json'


def project(state, positions):
    return sum(((state >> p) & 1) << j for j, p in enumerate(positions))


def usual(raw):
    return [(k, own, [(callee, tuple(args)) for callee, args in calls] +
             ([('K', (0, 1, 2))] if any(c == 'SELF' and sorted(a) == [0, 1, 2]
                                      for c, a in calls) else []))
            for k, own, calls in raw]


def limit(defs):
    types = {i for i, (_, _, calls) in enumerate(defs)
             if any(c == 'SELF' for c, _ in calls)}
    old = {i: (1 << (1 << defs[i][0])) - 1 for i in types}
    history = []
    while True:
        all_relations = []
        for i, (k, own, calls) in enumerate(defs):
            good = 0
            for state in range(1 << (k + own)):
                valid = True
                for callee, args in calls:
                    value = project(state, args)
                    rel = 0x7e if callee == 'K' else old[i] if callee == 'SELF' else all_relations[callee]
                    if not ((rel >> value) & 1):
                        valid = False
                        break
                if valid:
                    good |= 1 << (state & ((1 << k) - 1))
            all_relations.append(good)
        new = {i: all_relations[i] for i in types}
        assert all((new[i] & old[i]) == new[i] for i in types)
        history.append({str(i): hex(new[i]) for i in sorted(types)})
        if old == new:
            return all_relations, types, history
        old = new


def flatten(defs, types, which):
    n = defs[which][0]
    calls = []
    def visit(i, actual):
        nonlocal n
        k, own, body = defs[i]
        assert len(actual) == k
        local = tuple(range(n, n + own))
        n += own
        env = tuple(actual) + local
        for c, a in body:
            mapped = tuple(env[v] for v in a)
            if c == 'K':
                calls.append((c, mapped))
            elif c == 'SELF':
                calls.append((i, mapped))
            elif c in types:
                calls.append((c, mapped))
            else:
                visit(c, mapped)
    visit(which, tuple(range(defs[which][0])))
    return n, calls


def block_states(size, calls, G, skip=None):
    return [state for state in range(1 << size)
            if all(j == skip or ((0x7e if c == 'K' else G[c]) >> project(state, a)) & 1
                   for j, (c, a) in enumerate(calls))]


def call_relation(size, calls, G, chosen, arity):
    result = 0
    for state in block_states(size, calls, G, chosen):
        a = state & ((1 << arity) - 1)
        b = project(state, calls[chosen][1])
        result |= 1 << (8 * a + b)
    return result


def compose(left, right, nrows):
    result = 0
    for a in range(nrows):
        middle = (left >> (8 * a)) & 255
        row = 0
        while middle:
            bit = middle & -middle
            middle ^= bit
            row |= (right >> (8 * (bit.bit_length() - 1))) & 255
        result |= row << (8 * a)
    return result


def canonical(items):
    seen = {}
    return tuple(seen.setdefault(x, len(seen)) for x in items)


class Window:
    def __init__(self, raw, S):
        self.defs = usual(raw)
        self.G, self.types, self.limit_history = limit(self.defs)
        self.S = S
        self.main = len(raw) - 1
        self.km = self.defs[-1][0]
        self.wrapper = self.main != S
        self.flat = {i: flatten(self.defs, self.types, i) for i in set((S, self.main))}
        self.size, self.calls = self.flat[S]
        assert self.defs[S][0] == 3
        self.own = self.size - 3
        self.child_indices = [j for j, (c, _) in enumerate(self.calls) if c == S]
        self.generators = [call_relation(self.size, self.calls, self.G, j, 3)
                           for j in self.child_indices]
        self.good = block_states(self.size, self.calls, self.G)
        assert self.G[S] and self.G[self.main] and self.good
        self.starts = {}
        if not self.wrapper:
            diagonal = sum(1 << (8 * a + a) for a in range(8))
            part = tuple(range(self.km)) + tuple(range(3))
            self.starts[(diagonal, part)] = (None, ())
        else:
            size, calls = self.flat[self.main]
            for entry, (c, args) in enumerate(calls):
                if c != S:
                    continue
                J = call_relation(size, calls, self.G, entry, self.km)
                part = canonical(tuple(range(self.km)) + args)
                self.starts[(J, part)] = (entry, ())
        assert self.starts
        self.g_cache = {}
        self.literal_cache = {}
        self.relation_cache = {}

    def step(self, q, label):
        J, part = q
        args = self.calls[self.child_indices[label]][1]
        roots = [('old', i) for i in range(self.km)]
        child = [('old', part[self.km + a]) if a < 3 else ('new', a) for a in args]
        return compose(J, self.generators[label], 1 << self.km), canonical(roots + child)

    def relation(self, q):
        if q in self.relation_cache:
            return self.relation_cache[q]
        J, part = q
        own_labels = tuple(range(self.km + 3, self.km + self.size))
        labels = tuple(sorted(set(part) | set(own_labels)))
        positions = {label: j for j, label in enumerate(labels)}
        allowed = 0
        for b in self.good:
            u = b & 7
            for t in range(1 << self.km):
                if not ((J >> (8 * t + u)) & 1):
                    continue
                values = {j: (t >> j) & 1 for j in range(self.km)}
                valid = True
                for j in range(3):
                    label, value = part[self.km + j], (u >> j) & 1
                    if label in values and values[label] != value:
                        valid = False
                        break
                    values[label] = value
                if not valid:
                    continue
                values.update({label: (b >> (3 + j)) & 1 for j, label in enumerate(own_labels)})
                state = sum(values[label] << positions[label] for label in labels)
                allowed |= 1 << state
        assert allowed, 'living window was empty'
        result = labels, allowed
        self.relation_cache[q] = result
        return result

    def least_bond(self, q):
        labels, allowed = self.relation(q)
        key = labels, allowed
        if key in self.g_cache:
            return self.g_cache[key]
        n = len(labels)
        if n not in self.literal_cache:
            universe = (1 << (1 << n)) - 1
            positives = [sum(1 << state for state in range(1 << n) if (state >> j) & 1)
                         for j in range(n)]
            self.literal_cache[n] = positives, universe
        positives, universe = self.literal_cache[n]
        cache = {}
        def shattered(support):
            if support in cache:
                return cache[support]
            portions = [allowed]
            for j in support:
                pos = positives[j]
                neg = universe ^ pos
                updated = []
                for row in portions:
                    a, b = row & pos, row & neg
                    if not a or not b:
                        cache[support] = False
                        return False
                    updated.extend((a, b))
                portions = updated
            cache[support] = bool(allowed)
            return cache[support]
        roots = {j for j, label in enumerate(labels) if label < self.km}
        own = {j for j, label in enumerate(labels) if label >= self.km + 3}
        for size in range(2, min(6, n) + 1):
            for support in itertools.combinations(range(n), size):
                if not roots.intersection(support) or not own.intersection(support):
                    continue
                if shattered(support):
                    continue
                if all(shattered(support[:j] + support[j + 1:]) for j in range(size)):
                    result = (size, tuple(labels[j] for j in support))
                    self.g_cache[key] = result
                    return result
        result = (None, ())
        self.g_cache[key] = result
        return result

    def orbit(self):
        current = dict(self.starts)
        seen = {}
        levels = []
        states = set()
        stored = 0
        while True:
            frozen = frozenset(current)
            if frozen in seen:
                preperiod = seen[frozen]
                return {'preperiod': preperiod, 'period': len(levels) - preperiod,
                        'repeat_at': len(levels), 'levels': levels, 'states': states,
                        'stored_states': stored}
            assert len(levels) < 2000 and stored + len(current) <= 200000
            seen[frozen] = len(levels)
            states.update(current)
            stored += len(current)
            winner = None
            for q, path in current.items():
                g, support = self.least_bond(q)
                if g is not None and (winner is None or g < winner['U']):
                    winner = {'U': g, 'state': q, 'path': path, 'support': support}
            levels.append({'s': len(levels), 'states': len(current), 'winner': winner})
            following = {}
            for q, (entry, word) in current.items():
                for label in range(len(self.generators)):
                    nxt = self.step(q, label)
                    if nxt not in following:
                        following[nxt] = entry, word + (label,)
            current = following


def clauses_for_relation(actual, allowed):
    return [[-(v + 1) if (state >> j) & 1 else v + 1 for j, v in enumerate(actual)]
            for state in range(1 << len(actual)) if not ((allowed >> state) & 1)]


class DirectCNF:
    def __init__(self, window):
        self.w = window
        self.n = window.km
        self.clauses = []
        self.block_count = 0

    def block(self, which, actual, skip=None):
        size, calls = self.w.flat[which]
        arity = self.w.defs[which][0]
        local = tuple(range(self.n, self.n + size - arity))
        self.n += len(local)
        env = tuple(actual) + local
        self.block_count += 1
        for j, (callee, args) in enumerate(calls):
            if j == skip:
                continue
            actual_call = tuple(env[a] for a in args)
            allowed = 0x7e if callee == 'K' else self.w.G[callee]
            self.clauses.extend(clauses_for_relation(actual_call, allowed))
        return env

    def selected_path(self, entry, word):
        actual = tuple(range(self.w.km))
        if self.w.wrapper:
            env = self.block(self.w.main, actual, entry)
            actual = tuple(env[a] for a in self.w.flat[self.w.main][1][entry][1])
        for label in word:
            chosen = self.w.child_indices[label]
            env = self.block(self.w.S, actual, chosen)
            actual = tuple(env[a] for a in self.w.calls[chosen][1])
        return self.block(self.w.S, actual)

    def all_copies(self, entry, word, cutoff):
        target = None
        def visit(actual, depth, address, start):
            nonlocal target
            size, calls = self.w.flat[self.w.S]
            local = tuple(range(self.n, self.n + size - 3))
            self.n += len(local)
            env = tuple(actual) + local
            self.block_count += 1
            if start == entry and address == word:
                target = env
            for j, (c, args) in enumerate(calls):
                a = tuple(env[x] for x in args)
                if c == self.w.S and depth < cutoff:
                    label = self.w.child_indices.index(j)
                    visit(a, depth + 1, address + (label,), start)
                else:
                    self.clauses.extend(clauses_for_relation(a, 0x7e if c == 'K' else self.w.G[c]))
        roots = tuple(range(self.w.km))
        if self.w.wrapper:
            size, calls = self.w.flat[self.w.main]
            local = tuple(range(self.n, self.n + size - self.w.km))
            self.n += len(local)
            env = roots + local
            self.block_count += 1
            for j, (c, args) in enumerate(calls):
                a = tuple(env[x] for x in args)
                if c == self.w.S:
                    visit(a, 0, (), j)
                else:
                    self.clauses.extend(clauses_for_relation(a, 0x7e if c == 'K' else self.w.G[c]))
        else:
            visit(roots, 0, (), None)
        assert target is not None
        return target


def label_actuals(w, q, target):
    _, part = q
    mapping = {i: i for i in range(w.km)}
    for j in range(3):
        label, actual = part[w.km + j], target[j]
        if label in mapping:
            assert mapping[label] == actual
        mapping[label] = actual
    mapping.update({w.km + j: target[j] for j in range(3, w.size)})
    assert len(set(mapping.values())) == len(mapping)
    return mapping


def sat_projection(solver, actual):
    mask = 0
    for state in range(1 << len(actual)):
        if solver.solve(assumptions=[v + 1 if (state >> j) & 1 else -(v + 1)
                                     for j, v in enumerate(actual)]):
            mask |= 1 << state
    return mask


def verify_bond(solver, actual):
    if len(actual) != len(set(actual)):
        raise ValueError('A bond support cannot repeat one distinction identity')
    allowed = sat_projection(solver, actual)
    full = (1 << (1 << len(actual))) - 1
    deletions = []
    for j in range(len(actual)):
        smaller = actual[:j] + actual[j + 1:]
        p = sat_projection(solver, smaller)
        deletions.append(p.bit_count())
        assert p == (1 << (1 << len(smaller))) - 1
    assert allowed != full and allowed
    return {'size': len(actual), 'actual_distinctions': list(actual),
            'allowed_states': allowed.bit_count(),
            'forbidden_states': [s for s in range(1 << len(actual)) if not ((allowed >> s) & 1)],
            'one_deleted_projection_counts': deletions,
            'minimal_nonshattered': True,
            'proper_deletion_bond_claim_rejected': True}


def direct_check(w, level, explicit=False):
    winner = level['winner']
    assert winner
    q, (entry, word), support = winner['state'], winner['path'], winner['support']
    cnf = DirectCNF(w)
    target = cnf.all_copies(entry, word, len(word) + 1) if explicit else cnf.selected_path(entry, word)
    mapping = label_actuals(w, q, target)
    labels, expected = w.relation(q)
    with Solver(name='cadical195', bootstrap_with=cnf.clauses) as solver:
        assert solver.solve(), 'empty direct instance'
        actual = tuple(mapping[label] for label in labels)
        projected = sat_projection(solver, actual)
        assert projected == expected, 'window projection differs from direct SAT'
        checked = verify_bond(solver, tuple(mapping[label] for label in support))
    return {'word_length': len(word), 'absolute_depth': len(word) + int(w.wrapper),
            'entry_flat_call': entry, 'self_call_labels': list(word),
            'support_labels': list(support), 'state': {'J': hex(q[0]), 'partition': list(q[1])},
            'window_labels': list(labels), 'window_states': expected.bit_count(),
            'full_window_assignments_checked': 1 << len(labels),
            'projection_equal': True, 'bond': checked,
            'method': 'all-S-copies-with-exact-frontier' if explicit else 'selected-path-with-exact-off-path-subtrees',
            'variables': cnf.n, 'clauses': len(cnf.clauses), 'blocks': cnf.block_count}


def repeated_port_control():
    # One ancestor's own distinction is handed to two positions of its child.
    w = Window([[3, 1, [['K', [0, 1, 3]], ['SELF', [0, 3, 3]]]]], 0)
    start = next(iter(w.starts))
    q = w.step(start, 0)
    assert q[1] == (0, 1, 2, 0, 3, 3)
    cnf = DirectCNF(w)
    target = cnf.selected_path(None, (0,))
    assert target[1] == target[2]
    labels, expected = w.relation(q)
    mapping = label_actuals(w, q, target)
    with Solver(name='cadical195', bootstrap_with=cnf.clauses) as solver:
        assert sat_projection(solver, tuple(mapping[label] for label in labels)) == expected
        duplicate_positions = sat_projection(solver, (target[1], target[2]))
        merged_identity = sat_projection(solver, (target[1],))
        rejected = False
        try:
            verify_bond(solver, (target[1], target[2]))
        except ValueError:
            rejected = True
        assert rejected
    assert duplicate_positions == 0b1001 and merged_identity == 0b11
    # A second, fully elementary brute check uses the four actual variables.
    brute = 0
    for state in range(1 << cnf.n):
        if all(any(bool((state >> (abs(lit) - 1)) & 1) == (lit > 0) for lit in clause)
               for clause in cnf.clauses):
            brute |= 1 << ((state >> target[1]) & 1)
    assert brute == merged_identity
    return {'partition': list(q[1]), 'child_ports_actual': list(target[:3]),
            'unmerged_two_position_relation': [0, 3],
            'merged_one_identity_relation': [0, 1],
            'spurious_size_two_bond_rejected': rejected,
            'whole_window_projection_equal': True,
            'tiny_all_assignments': 1 << cnf.n, 'brute_sat_agree': True}


def serial_level(level):
    winner = level['winner']
    return {'s': level['s'], 'states': level['states'], 'U': winner['U'] if winner else '> 6'}


def audit(record):
    started = time.monotonic()
    digest, census, cert = record['digest'], record['census'], record['certificate']
    w = Window(json.loads(digest['key']), census['S'])
    assert w.generators == [int(r, 16) for r in cert['R_i']]
    orbit = w.orbit()
    pre, period = orbit['preperiod'], orbit['period']
    assert (pre, period, orbit['repeat_at']) == (cert['window']['preperiod'], cert['window']['period'], cert['window']['repeat_at'])
    ours = [serial_level(x) for x in orbit['levels']]
    theirs = [{k: x[k] for k in ('s', 'states', 'U')} for x in cert['window']['levels']]
    assert ours == theirs, 'U(s) or level cardinality mismatch'
    certified_states = {(int(x['J'], 16), canonical(x['partition'])): x['g'] for x in cert['window']['state_bonds']}
    assert set(certified_states) == orbit['states']
    for q, their_g in certified_states.items():
        g, _ = w.least_bond(q)
        assert (g if g is not None else '> 6') == their_g
    maximum = max(level['winner']['U'] for level in orbit['levels'][pre:])
    assert maximum == cert['window']['maximum']
    # The first complete repeating interval proves every subsequent residue.
    depths = sorted(set((1, 2, 3, 6)) | set(range(pre, pre + period)))
    checks = []
    for depth in depths:
        index = depth if depth < len(orbit['levels']) else pre + (depth - pre) % period
        level = orbit['levels'][index]
        if depth != index:
            # Reconstruct an actual representative at this exact length.
            current = dict(w.starts)
            for _ in range(depth):
                following = {}
                for q, (entry, word) in current.items():
                    for label in range(len(w.generators)):
                        following.setdefault(w.step(q, label), (entry, word + (label,)))
                current = following
            target_q = level['winner']['state']
            level = {'s': depth, 'winner': dict(level['winner'], path=current[target_q])}
        checks.append(direct_check(w, level))
    explicit = [direct_check(w, orbit['levels'][depth], explicit=True)
                for depth in (1, 2, 3) if depth < len(orbit['levels'])]
    # Minimal start at which the claimed eventual maximum holds, distinct from
    # the first-repeat preperiod, which certifies the full Q_s state set.
    earlier_violations = [level['s'] for level in orbit['levels'][:pre]
                          if not level['winner'] or level['winner']['U'] > maximum]
    onset = max(earlier_violations, default=-1) + 1
    return {'key_sha256': digest['key_sha256'], 'key': digest['key'], 'stratum': digest['stratum'],
            'final_verdict': cert['verdict'], 'final_caps': cert['caps'],
            'wrapper': w.wrapper, 'main_ports': w.km, 'S': w.S,
            'per_call_relations_match': True, 'living': True,
            'limit_history': w.limit_history, 'limit_relations': [hex(g) for g in w.G],
            'preperiod': pre, 'period': period, 'repeat_at': orbit['repeat_at'],
            'absolute_periodic_threshold': pre + int(w.wrapper),
            'eventual_window_maximum': maximum,
            'earliest_window_bound_onset': onset,
            'earliest_absolute_window_bound_onset': onset + int(w.wrapper),
            'state_values_checked': len(orbit['states']), 'stored_level_states': orbit['stored_states'],
            'window_distinction_counts': sorted({len(w.relation(q)[0]) for q in orbit['states']}),
            'censored_state_values': sum(w.least_bond(q)[0] is None for q in orbit['states']),
            'fresh_Q_and_U_equal_certificate': True, 'levels': ours,
            'target_port_internal_merge_states': sum(len(set(q[1][w.km:])) < 3 for q in orbit['states']),
            'direct_checks': checks, 'explicit_checks': explicit,
            'seconds': round(time.monotonic() - started, 3),
            'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int)
    parser.add_argument('--prefix', default='window_results')
    args = parser.parse_args()
    started = time.monotonic()
    data = json.loads(INPUT.read_text())
    records = data['records'][:args.limit]
    results = []
    raw = HERE / (args.prefix + '.jsonl')
    with raw.open('w') as output:
        for record in records:
            result = audit(record)
            output.write(json.dumps(result, separators=(',', ':')) + '\n')
            output.flush()
            results.append(result)
            print(json.dumps({'key': result['key_sha256'][:12], 'bound': result['eventual_window_maximum'],
                              'preperiod': result['preperiod'], 'period': result['period'],
                              'states': result['state_values_checked'], 'seconds': result['seconds']}), flush=True)
    control = repeated_port_control()
    summary = {'families': len(results), 'all_passed': True, 'repeated_port_control': control,
               'final_bounded_families': sum(r['final_verdict'] == 'bounded' for r in results),
               'by_rule_undecided_families': sum(r['final_verdict'] == 'undecided' for r in results),
               'state_values_checked': sum(r['state_values_checked'] for r in results),
               'direct_bonds_checked': sum(len(r['direct_checks']) for r in results),
               'explicit_bonds_checked': sum(len(r['explicit_checks']) for r in results),
               'projection_assignments_checked': sum(c['full_window_assignments_checked']
                   for r in results for c in r['direct_checks'] + r['explicit_checks']),
               'sources': data['sources'], 'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'input_sha256': hashlib.sha256(INPUT.read_bytes()).hexdigest(),
               'seconds': round(time.monotonic() - started, 3),
               'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
               'validation': 'V2 separate same-task implementation; AI referee, no external replication',
               'forbidden_python_opened_or_imported': False,
               'nonclaim': 'Finite audit does not prove a new uniform theorem or a global least-bond value.'}
    (HERE / (args.prefix + '.json')).write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary), flush=True)


if __name__ == '__main__':
    main()
