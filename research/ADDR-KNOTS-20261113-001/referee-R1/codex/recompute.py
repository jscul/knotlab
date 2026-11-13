"""Bounded independent referee checks. Run from the repository root with -B.

All paths written are children of this script's directory. No study-code imports.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import itertools
import json
import random
import resource
import tempfile
import time
from pathlib import Path

from pysat.solvers import Solver

from check_rup import RUPChecker
from fresh_patterns import (cnf, direct_state, fate, fingerprint, joining, pattern,
                            pattern_bytes, state_actions, verify_assignment, words)

HERE = Path(__file__).resolve().parent
tempfile.tempdir = str(HERE)  # PySAT's proof logger must also stay in the write root.
ROOT = HERE.parents[3]
RECORDS = ROOT / 'artifacts/ADDR-KNOTS-20261113-001A/ADDR-KNOTS-20261113-001A-E001_addressed_census/keys.jsonl.gz'
RETURNS = ROOT / 'research/ADDR-KNOTS-20261113-001/returns_recheck.json'


def read_records():
    with gzip.open(RECORDS, 'rt') as stream:
        return [json.loads(line) for line in stream]


def alternating(record):
    v = record['verdict_n']
    return record['return'] and all(v[i] is not None and v[i - 1] is not None and
                                    v[i] != v[i - 1] for i in range(7, 12))


def write_json(path, data):
    path.write_text(json.dumps(data, sort_keys=True, indent=2) + '\n')


def input_sha(clauses, nvars):
    digest = hashlib.sha256(f'p cnf {nvars} {len(clauses)}\n'.encode())
    for clause in clauses:
        digest.update((' '.join(map(str, clause)) + ' 0\n').encode())
    return digest.hexdigest()


def solve_level(triples, n, budget, stem, phases=None):
    start = time.monotonic()
    clauses = cnf(triples)
    result = {'level': n, 'knots': len(triples), 'join': joining(triples),
              'cnf_sha256': input_sha(clauses, 1 << n), 'conflict_budget': budget,
              'symmetry_unit': False}
    if not clauses:
        values = [False] * (1 << n)
        result.update(verdict=1, certified=True, assignment='0' * (1 << n),
                      witness_checked_knots=0, solver='empty pattern')
        return result
    if phases is not None:
        lifted = [phases[x >> 1] for x in range(1 << n)]
        if verify_assignment(triples, lifted):
            result.update(verdict=1, certified=True,
                          assignment=''.join('1' if v else '0' for v in lifted),
                          witness_checked_knots=len(triples), solver='directly checked lifted assignment',
                          total_seconds=time.monotonic() - start)
            return result
    with Solver(name='g4', bootstrap_with=clauses, with_proof=True) as solver:
        if phases is not None:
            solver.set_phases([(x + 1) if phases[x >> 1] else -(x + 1)
                               for x in range(1 << n)])
        solver.conf_budget(budget)
        verdict = solver.solve_limited()
        result.update(solver='Glucose4', stats=solver.accum_stats(),
                      solve_seconds=time.monotonic() - start)
        if verdict is True:
            model = solver.get_model()
            values = [False] * (1 << n)
            for literal in model:
                if abs(literal) <= len(values):
                    values[abs(literal) - 1] = literal > 0
            assert verify_assignment(triples, values), 'invalid SAT witness'
            result.update(verdict=1, certified=True,
                          assignment=''.join('1' if v else '0' for v in values),
                          witness_checked_knots=len(triples))
        elif verdict is False:
            proof = solver.get_proof()
            proof_path = HERE / 'certificates' / f'{stem}-L{n:02d}.drup.gz'
            proof_path.parent.mkdir(exist_ok=True)
            proof_text = '\n'.join(proof) + '\n'
            with gzip.open(proof_path, 'wt') as stream:
                stream.write(proof_text)
            checking_start = time.monotonic()
            checked = RUPChecker(clauses, 1 << n).check(proof)
            result.update(verdict=0, certified=checked['valid'], proof_check=checked,
                          certificate=str(proof_path.relative_to(HERE)),
                          certificate_uncompressed_sha256=hashlib.sha256(proof_text.encode()).hexdigest(),
                          certificate_lines=len(proof),
                          certificate_check_seconds=time.monotonic() - checking_start)
            assert checked['valid'], ('proof rejected', checked)
        else:
            result.update(verdict=None, certified=False, reason='Glucose4 conflict budget exhausted')
    result['total_seconds'] = time.monotonic() - start
    return result


def check_key(record, budget, output_directory):
    stem = record['key_id']
    patterns = [pattern(record['key'], n) for n in range(1, 13)]
    counts = list(map(len, patterns))
    joins = [joining(p) for p in patterns]
    digest = fingerprint(patterns)
    result = {'key_id': stem, 'key': record['key'], 'recorded_fate': record['fate'],
              'recorded_verdicts': record['verdict_n'], 'recorded_first_death': record['first_death'],
              'recorded_pattern_hash': record['pattern_hash'], 'fresh_pattern_hash': digest,
              'hash_matches': digest == record['pattern_hash'], 'counts_match': counts == record['knots_n'],
              'joins_match': joins == record['join_n'], 'counts': counts, 'joins': joins,
              'alternating': alternating(record), 'levels': []}
    assert result['hash_matches'] and result['counts_match'] and result['joins_match'], result
    previous = None
    output_directory.mkdir(exist_ok=True)
    target = output_directory / f'{stem}.json'
    for n, triples in enumerate(patterns, 1):
        level = solve_level(triples, n, budget, stem, previous)
        level['recorded_verdict'] = record['verdict_n'][n - 1]
        level['agrees'] = level['verdict'] is None or level['recorded_verdict'] is None or level['verdict'] == level['recorded_verdict']
        assert level['agrees'], ('VERDICT MISMATCH', stem, n, level)
        result['levels'].append(level)
        previous = [x == '1' for x in level['assignment']] if level['verdict'] == 1 else None
        write_json(target, result)
        print(json.dumps({'key': stem[:12], 'n': n, 'v': level['verdict'],
                          'certified': level['certified'], 'seconds': level.get('total_seconds', 0),
                          'proof_lines': level.get('certificate_lines')}), flush=True)
    verdicts = [x['verdict'] for x in result['levels']]
    result['fresh_fate'] = fate(verdicts, counts)
    result['fresh_first_death'] = next((n for n, v in enumerate(verdicts, 1) if v == 0), None)
    result['fresh_return'] = any(v == 0 and 1 in verdicts[i + 1:] for i, v in enumerate(verdicts))
    result['all_levels_certified'] = all(x['certified'] for x in result['levels'])
    result['fate_agrees'] = result['fresh_fate'] == record['fate']
    write_json(target, result)
    return result


def sample_records(records, number=30):
    # Deterministic stratification by actual size, placement count and class;
    # hashed order is fixed before any fresh outcome is computed.
    buckets = {}
    for r in sorted(records, key=lambda r: r['key_id']):
        label = (r['key'][0], len(r['key'][4]), r['rel_class'])
        buckets.setdefault(label, []).append(r)
    groups = sorted(buckets)
    random.Random(20261113).shuffle(groups)
    selected = [buckets[g][0] for g in groups[:number]]
    # Require at least one record of each available automaton size and class.
    for field, categories in [('s', range(1, 6)), ('class', ['finitary', 'bounded', 'polynomial', 'exponential'])]:
        for category in categories:
            matches = [r for r in records if (r['key'][0] if field == 's' else r['rel_class']) == category]
            if matches and not any((r['key'][0] if field == 's' else r['rel_class']) == category for r in selected):
                selected.append(min(matches, key=lambda r: r['key_id']))
    return selected


def controls():
    rng = random.Random(8291)
    compared = 0
    for s in range(1, 6):
        for _ in range(4):
            key = [s, [rng.randrange(2) for _ in range(s)],
                   [rng.randrange(s) for _ in range(s)], [rng.randrange(s) for _ in range(s)], []]
            for n in range(1, 7):
                arrays = state_actions(key, n)
                for q in range(s):
                    assert arrays[q] == [direct_state(key, q, x, n) for x in range(1 << n)]
                    assert sorted(arrays[q]) == list(range(1 << n))
                    compared += 1
    fano = sorted({tuple(sorted((x, (x + 1) % 7, (x + 3) % 7))) for x in range(7)})
    formula = cnf(fano)
    assert not any(verify_assignment(fano, bits) for bits in itertools.product([False, True], repeat=7))
    with Solver(name='g4', bootstrap_with=formula, with_proof=True) as solver:
        assert solver.solve() is False
        proof = solver.get_proof()
    accepted = RUPChecker(formula, 7).check(proof)
    rejected = RUPChecker([[1, 2, 3], [-1, -2, -3]], 3).check(['0'])
    missing = RUPChecker(formula, 7).check(proof[:-1])
    assert accepted['valid'] and not rejected['valid'] and not missing['valid']
    # Exhaustively compare each candidate RUP test with a separate scan-based
    # implementation. This exercises units, tautologies and watch movement.
    def plain_conflict(clauses, assumptions):
        known = {}
        def force(lit):
            variable, value = abs(lit), lit > 0
            if variable in known:
                return known[variable] == value
            known[variable] = value
            return True
        if not all(force(x) for x in assumptions):
            return True
        while True:
            changed = False
            for clause in clauses:
                if any(abs(x) in known and known[abs(x)] == (x > 0) for x in clause):
                    continue
                unset = [x for x in clause if abs(x) not in known]
                if not unset:
                    return True
                if len(unset) == 1:
                    if not force(unset[0]):
                        return True
                    changed = True
            if not changed:
                return False
    propagation_cases = 0
    for _ in range(200):
        n = rng.randrange(2, 9)
        clauses = []
        for _ in range(rng.randrange(1, 25)):
            variables = rng.sample(range(1, n + 1), rng.randrange(1, min(4, n) + 1))
            clauses.append([v * rng.choice([-1, 1]) for v in variables])
        checker = RUPChecker(clauses, n)
        for _ in range(20):
            assumptions = [rng.choice([-1, 1]) * rng.randrange(1, n + 1) for _ in range(rng.randrange(n + 2))]
            assert checker.contradiction(assumptions) == plain_conflict(clauses, assumptions)
            propagation_cases += 1
    return {'action_array_vs_letter_controls': compared, 'fano_exhaustive_unsat': True,
            'fano_proof': accepted, 'false_empty_clause_rejected': rejected,
            'proof_without_empty_rejected': missing,
            'watched_vs_independent_plain_unit_propagation': propagation_cases}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['controls', 'alternating', 'other', 'sample'])
    parser.add_argument('--offset', type=int, default=0)
    parser.add_argument('--limit', type=int, default=1000)
    parser.add_argument('--budget', type=int, default=100000)
    args = parser.parse_args()
    # One process, bounded address space; no child processes or BLAS work.
    resource.setrlimit(resource.RLIMIT_AS, (3 * 1024**3, 3 * 1024**3))
    if args.mode == 'controls':
        result = controls()
        write_json(HERE / 'controls.json', result)
        print(json.dumps(result), flush=True)
        return
    records = read_records()
    if args.mode in ('alternating', 'other'):
        ids = {r['key_id'] for r in json.loads(RETURNS.read_text())}
        selected = [r for r in records if r['key_id'] in ids and alternating(r) == (args.mode == 'alternating')]
        selected.sort(key=lambda r: (sum(r['knots_n']), r['key_id']))
    else:
        selected = sample_records(records)
    selection = [{'key_id': r['key_id'], 's': r['key'][0], 'placements': len(r['key'][4]),
                  'class': r['rel_class'], 'recorded_fate': r['fate']} for r in selected]
    write_json(HERE / f'{args.mode}_selection.json', selection)
    selected = selected[args.offset:args.offset + args.limit]
    output = HERE / ('sample' if args.mode == 'sample' else 'returns')
    for rec in selected:
        check_key(rec, args.budget, output)


if __name__ == '__main__':
    main()
