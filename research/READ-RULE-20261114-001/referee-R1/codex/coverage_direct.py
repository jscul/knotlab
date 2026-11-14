"""Fresh READ relation-free CNF/SAT audit for nine exceptions and 20 controls.

Q reconstruction chooses concrete words only. Decisive projections and search
are from independently unfolded clauses with exact off-word subtree limits;
neither per-call relations nor composition is used in that search.
"""
from __future__ import annotations

import collections
import importlib.util
import itertools
import json
import resource
import sys
import time
from pathlib import Path

import coverage_run as audit

ROOT, HERE, OLD = audit.ROOT, audit.HERE, audit.OLD
spec = importlib.util.spec_from_file_location('earlier_carry_referee_direct', OLD / 'grow_core.py')
core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)


def word_cnf(raw, S, entry, word):
    """Unfold just the actual word; exact limits replace off-word subtrees."""
    defs = core.usual(raw)
    limits, history = core.limits(defs)
    flat = {i: core.flatten(defs, i) for i in range(len(defs))}
    main = len(defs) - 1
    roots = set(range(defs[main][0]))
    n = len(roots)
    clauses, copies, origin = [], [], {}

    def block(which, ports, skip, depth):
        nonlocal n
        size, body = flat[which]
        arity = defs[which][0]
        own = tuple(range(n, n + size - arity))
        n += len(own)
        env = tuple(ports) + own
        copies.append({'definition': which, 'depth': depth, 'ports': list(ports), 'own': list(own)})
        for v in own:
            origin[v] = {'definition': which, 'depth': depth}
        for call_index, (callee, args) in enumerate(body):
            if call_index == skip:
                continue
            actual = tuple(env[j] for j in args)
            if callee == 'K':
                clauses.extend(([v + 1 for v in actual], [-(v + 1) for v in actual]))
            else:
                clauses.extend(core.forbid(actual, limits[callee]))
        return env

    actual = tuple(sorted(roots))
    offset = int(main != S)
    if main != S:
        env = block(main, actual, entry, 0)
        callee, args = flat[main][1][entry]
        assert callee == S
        actual = tuple(env[j] for j in args)
    child_indices = [j for j, (callee, _) in enumerate(flat[S][1]) if callee == S]
    for depth, label in enumerate(word):
        selected = child_indices[label]
        env = block(S, actual, selected, depth + offset)
        actual = tuple(env[j] for j in flat[S][1][selected][1])
    target = block(S, actual, None, len(word) + offset)
    targets = set(target[3:])
    return {'clauses': clauses, 'n': n, 'roots': roots, 'targets': targets,
            'target': target, 'copies': copies, 'origin': origin,
            'port_limits': [sorted(s) for s in limits], 'limit_history': history}


def sat_rows(solver, actual):
    return [state for state in range(1 << len(actual))
            if solver.solve(assumptions=[v + 1 if state >> j & 1 else -(v + 1)
                                         for j, v in enumerate(actual)])]


def all_bonds_inside(solver, actual, required):
    universe = tuple(sorted(set(actual)))
    found = []
    for size in range(2, len(universe) + 1):
        for support in itertools.combinations(universe, size):
            if not set(required) <= set(support):
                continue
            rows = sat_rows(solver, support)
            if len(rows) == 1 << size:
                continue
            deletions = [len(sat_rows(solver, support[:j] + support[j + 1:])) for j in range(size)]
            if all(n == 1 << (size - 1) for n in deletions):
                found.append({'support': list(support), 'allowed': rows, 'deletion_counts': deletions})
    return found


def verify_candidate(cnf, q, candidate, expected_exception=None):
    actual = tuple(cnf['target'][v] for v in candidate)
    p = q[1][len(cnf['roots']) + candidate[0]]
    assert actual[0] == p and p in cnf['roots'], 'syntactic identity must match the actual CNF word'
    with core.Solver(name='cadical195', bootstrap_with=cnf['clauses']) as solver:
        assert solver.solve(), 'dead instance excluded'
        rows = sat_rows(solver, actual)
        info = audit.triple_info(rows)
        bonds = all_bonds_inside(solver, actual, actual[:2])
        assert bool(bonds) == (not info['exception'])
        if expected_exception is not None:
            assert info['exception'] == expected_exception
    return {'candidate': list(candidate), 'actual': list(actual), 'triple_rows': rows,
            'bonds_inside_W_through_p_x': bonds, **info}


def least_other_bond(cnf, seconds=20):
    # Exhaust all root-target pairs before seeking triples. The members of
    # a triple can be anywhere in this explicit word, rather than in W.
    pool = set(cnf['roots']) | set(cnf['target'])
    search = core.DirectSearch(cnf['clauses'], cnf['n'], cnf['roots'], cnf['targets'], seconds, [pool])
    try:
        result = search.run(max_size=3, seeds=12)
        result.update(queries=search.queries, iterations=search.iterations)
        if result['minimum'] is None:
            return result
        assert result['minimum'] in (2, 3)
        support = tuple(result['witness'])
        with core.Solver(name='glucose42', bootstrap_with=cnf['clauses']) as solver:
            allowed = sat_rows(solver, support)
            deleted = [len(sat_rows(solver, support[:j] + support[j + 1:])) for j in range(len(support))]
            assert allowed and len(allowed) < 1 << len(support)
            assert all(n == 1 << (len(support) - 1) for n in deleted)
        result['independent_solver_witness_check'] = {'allowed': allowed, 'one_deleted_counts': deleted}
        result['origins'] = [cnf['origin'].get(v, {'root': v}) for v in support]
        return result
    finally:
        search.close()


def distance(a, b):
    sa, sb = a['syntax'], b['syntax']
    return (100 * (a['wrapper'] != b['wrapper']) +
            20 * abs(sa['size'] - sb['size']) +
            5 * abs(len(sa['knots']) - len(sb['knots'])) +
            abs(len(sa['calls']) - len(sb['calls'])), b['key_sha256'])


def choose_controls(records, exceptions):
    good = [r for r in records if r['in_scope'] and r['R'] and r['R']['exists_good_each_Q_residue']]
    chosen, roles = [], {}
    for exception in exceptions:
        pick = min((r for r in good if r not in chosen), key=lambda r: distance(exception, r))
        chosen.append(pick)
        roles[pick['key']] = {'role': 'matched_exception_control', 'matched_exception': exception['key_sha256'],
                              'syntax_distance': distance(exception, pick)[0]}
    # The newly covered cases directly discriminate the quantifier question.
    priorities = [r for r in good if not r['R']['strict_each_R_residue']]
    priorities += sorted(good, key=lambda r: (-r['R']['Q_period'], -r['R']['Q_mu'], r['key_sha256']))[:10]
    priorities += sorted((r for r in good if r['syntax']['R1_all']), key=lambda r: r['key_sha256'])
    priorities += sorted(good, key=lambda r: r['key_sha256'])
    for r in priorities:
        if r not in chosen:
            chosen.append(r)
            roles[r['key']] = {'role': 'quantifier_or_period_or_pendant_control'}
        if len(chosen) == 20:
            break
    assert len(chosen) == 20
    return chosen, roles


def main():
    start = time.monotonic()
    controls = core.controls()
    records = [json.loads(line) for line in (HERE / 'coverage_results.jsonl').open()]
    digest = {r['key']: r for r in audit.gzrows(audit.DIGEST)}
    old_exc = {r['key'] for r in audit.read_json(audit.DATA / 'summary.json')['Q1']['exception_only_families']}
    exceptions = [r for r in records if r['key'] in old_exc]
    nonexceptions, roles = choose_controls(records, exceptions)
    details = HERE / 'coverage_direct_states.jsonl'
    details.write_text('')
    result_rows = []
    count_states = count_readings = 0
    for index, rec in enumerate(exceptions + nonexceptions):
        key, S = rec['key'], rec['S']
        is_exception = key in old_exc
        w = audit.window.Window(json.loads(key), S)
        levels, mu, period = audit.q_orbit(w, digest[key]['preperiod'], digest[key]['period'])
        if is_exception:
            # Check every eligible Q/candidate pair in every exception-only
            # eventual Q phase, deduplicating actual Q states across phases.
            interesting = [r for r in rec['R']['residues'] if r['exception_only']]
            roster = {}
            for phase in interesting:
                s = phase['s']
                at = s if s < len(levels) else mu + (s - mu) % period
                for q, path in levels[at].items():
                    if any(q[1][w.km + c[0]] < w.km for c in rec['syntax']['candidates']):
                        roster.setdefault(q, path)
            assert roster
        else:
            witness = rec['R']['witnesses'][0]
            q = (int(witness['Q']['J'], 16), tuple(witness['Q']['partition']))
            roster = {q: (witness['entry'], tuple(witness['word']))}
        readings, state_count, other = 0, 0, None
        for q, (entry, word) in roster.items():
            cnf = word_cnf(json.loads(key), S, entry, word)
            checks = []
            for candidate in rec['syntax']['candidates']:
                if q[1][w.km + candidate[0]] >= w.km:
                    continue
                expected_rows = audit.projected_local_rows(w, q, candidate)
                expected = audit.triple_info(expected_rows)['exception']
                if not is_exception and expected:
                    continue
                check = verify_candidate(cnf, q, candidate, is_exception)
                assert check['triple_rows'] == list(expected_rows)
                checks.append(check)
            assert checks
            if other is None:
                searched = least_other_bond(cnf)
                if searched['minimum'] is not None:
                    other = searched
                    other.update(entry=entry, word=list(word), variables=cnf['n'], clauses=len(cnf['clauses']),
                                 member_universe='all distinctions in this explicitly unfolded root-to-target word')
            detail = {'key_sha256': rec['key_sha256'], 'exception_family': is_exception,
                      'entry': entry, 'word': list(word), 'Q': {'J': hex(q[0]), 'partition': list(q[1])},
                      'variables': cnf['n'], 'clauses': len(cnf['clauses']), 'checks': checks}
            with details.open('a') as stream:
                stream.write(json.dumps(detail, sort_keys=True) + '\n')
            readings += len(checks)
            state_count += 1
        if other is None:
            # Other bounded witnesses need not themselves identity-carry a
            # reading position. Search all states of this same exact phase.
            phase = rec['R']['residues'][0]['s']
            at = phase if phase < len(levels) else mu + (phase - mu) % period
            for q, (entry, word) in levels[at].items():
                cnf = word_cnf(json.loads(key), S, entry, word)
                searched = least_other_bond(cnf)
                if searched['minimum'] is not None:
                    other = searched
                    other.update(entry=entry, word=list(word), variables=cnf['n'], clauses=len(cnf['clauses']),
                                 member_universe='all distinctions in this explicitly unfolded root-to-target word')
                    break
        assert other is not None, 'no independently verified size-three bound found'
        count_states += state_count
        count_readings += readings
        row = {'key_sha256': rec['key_sha256'], 'key': key, 'exception_family': is_exception,
               'scope': rec['in_scope'], 'verdict': rec['verdict'], 'wrapper': rec['wrapper'],
               'R1_every': rec['syntax']['R1_all'], 'strict_R_every': rec['R']['strict_each_R_residue'],
               'existential_R_every': rec['R']['exists_good_each_Q_residue'],
               'exact_Q_states_directly_checked': state_count, 'exact_candidate_readings_checked': readings,
               'other_bond': other, 'role': {'role': 'official_exception'} if is_exception else roles[key]}
        result_rows.append(row)
        (HERE / 'coverage_direct_progress.json').write_text(json.dumps({'completed': index + 1, 'rows': result_rows}, indent=2) + '\n')
        print(json.dumps({'completed': index + 1, 'sha': rec['key_sha256'][:16], 'exception': is_exception,
                          'Q_states': state_count, 'readings': readings, 'minimum_in_explicit_word': other['minimum'],
                          'seconds': round(time.monotonic() - start, 3)}), flush=True)
    out = {'exception_families': len(exceptions), 'nonexception_families': len(nonexceptions),
           'exact_Q_states_checked': count_states, 'candidate_readings_checked': count_readings,
           'all_projected_rows_agree': True, 'all_exception_W_no_bond_through_p_x': True,
           'all_nine_have_other_bonds_at_most_three': True,
           'controls': controls, 'rows': result_rows, 'seconds': time.monotonic() - start,
           'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
           'limits': ['Each finite explicit word with exact off-word limits has the exact infinite-system projection on that word.',
                      'A witnessed bond is a global upper bound. The reported least sizes are exact over the explicit member universe.',
                      'No finite sample establishes a uniform theorem or rules out a smaller bond using members outside that universe.'],
           'inputs_sha256': {str(p.relative_to(ROOT)): audit.sha(p) for p in (HERE / 'coverage_run.py',
                                                                          HERE / 'coverage_results.jsonl',
                                                                          OLD / 'grow_core.py', core.OLD)}}
    (HERE / 'coverage_direct.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({k: v for k, v in out.items() if k not in ('rows', 'controls', 'inputs_sha256')}, indent=2))


if __name__ == '__main__':
    main()
