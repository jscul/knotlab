"""A bounded second attempt on undecided referee levels.

Complement symmetry is handled in the *certificate*, not assumed by its checker:
from a DRUP proof of F and v, append -v to each addition to derive -v from F;
complement that derivation to derive v, then derive the empty clause. F is the
original complement-invariant NAE formula, so the resulting proof is ordinary DRUP.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import resource
import tempfile
import time
from pathlib import Path

from pysat.solvers import Solver

from check_rup import RUPChecker
from fresh_patterns import cnf, fate, pattern, verify_assignment
from fast_certificates import check_fast

HERE = Path(__file__).resolve().parent
tempfile.tempdir = str(HERE)  # Includes anonymous temporary solver proof files.


def expanded_proof(lines, variable):
    additions = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith(('c', 'd')):
            continue
        numbers = list(map(int, line.split()))
        assert numbers[-1] == 0
        additions.append(numbers[:-1])
        if not numbers[:-1]:
            break
    assert additions and additions[-1] == []
    first = [' '.join(map(str, clause + [-variable])) + ' 0' for clause in additions]
    second = [' '.join(map(str, [-x for x in clause] + [variable])) + ' 0' for clause in additions]
    return first + second + ['0']


def control():
    triples = sorted({tuple(sorted((x, (x + 1) % 7, (x + 3) % 7))) for x in range(7)})
    clauses = cnf(triples)
    with Solver(name='g4', bootstrap_with=clauses + [[1]], with_proof=True) as solver:
        assert solver.solve() is False
        proof = expanded_proof(solver.get_proof(), 1)
    outcome = RUPChecker(clauses, 7).check(proof)
    assert outcome['valid']
    # A conditional empty clause alone would be false for this satisfiable F;
    # the expansion must not make such an invalid premise acceptable.
    rejected = RUPChecker([[1, 2, 3], [-1, -2, -3]], 3).check(expanded_proof(['0'], 1))
    assert not rejected['valid']
    return {'unconditional_fano_expansion': outcome, 'invalid_conditional_proof_rejected': rejected}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--start', type=int, default=0)
    parser.add_argument('--limit', type=int, default=4)
    parser.add_argument('--budget', type=int, default=500000)
    parser.add_argument('--solver', choices=['g4', 'cd19'], default='g4')
    parser.add_argument('--alive-only', action='store_true')
    parser.add_argument('--dead-only', action='store_true')
    parser.add_argument('--no-phases', action='store_true')
    parser.add_argument('--fast-checker', action='store_true')
    parser.add_argument('--defer-check', action='store_true')
    parser.add_argument('--family-phases', action='store_true')
    parser.add_argument('--model-only', action='store_true')
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (3 * 1024**3, 3 * 1024**3))
    (HERE / 'refinement_controls.json').write_text(json.dumps(control(), indent=2) + '\n')
    selection_path = HERE / 'refinement_selection.json'
    if args.prepare:
        selected = []
        for folder in ('returns', 'sample'):
            for path in (HERE / folder).glob('*.json'):
                rec = json.loads(path.read_text())
                for level in rec['levels']:
                    if level['verdict'] is None:
                        selected.append({'file': str(path.relative_to(HERE)), 'level': level['level'],
                                         'knots': level['knots'], 'recorded_verdict': level['recorded_verdict']})
        selected.sort(key=lambda x: (x['level'], x['knots'], x['file']))
        selection_path.write_text(json.dumps(selected, indent=2) + '\n')
        print(json.dumps({'unknown_levels': len(selected), 'selection': selected}), flush=True)
        return
    selected = json.loads(selection_path.read_text())
    if args.alive_only:
        selected = [target for target in selected if target['recorded_verdict'] == 1]
    if args.dead_only:
        selected = [target for target in selected if target['recorded_verdict'] == 0]
    selected = selected[args.start:args.start + args.limit]
    families = {r['key_id']: r for r in json.loads((HERE / 'cadical_families.json').read_text())} if args.family_phases else {}
    for selected_level in selected:
        path = HERE / selected_level['file']
        rec = json.loads(path.read_text())
        n = selected_level['level']
        old = rec['levels'][n - 1]
        if old['verdict'] is not None:
            continue
        triples = pattern(rec['key'], n)
        clauses = cnf(triples)
        symmetry = min(x for triple in triples for x in triple) + 1
        start = time.monotonic()
        with Solver(name=args.solver, bootstrap_with=clauses + [[symmetry]], with_proof=not args.model_only) as solver:
            family_previous = (families.get(rec['key_id'], {}).get('levels', [])[n - 2]
                               if args.family_phases and n > 1 and rec['key_id'] in families else None)
            use_family = family_previous is not None and family_previous['verdict'] == 1
            use_previous = not args.no_phases and n > 1 and (use_family or rec['levels'][n - 2]['verdict'] == 1)
            if use_previous:
                previous = family_previous['assignment'] if use_family else rec['levels'][n - 2]['assignment']
                solver.set_phases([(x + 1) * (1 if previous[x >> 1] == '1' else -1) for x in range(1 << n)])
            solver.conf_budget(args.budget)
            verdict = solver.solve_limited()
            attempt = {'solver': args.solver, 'symmetry_variable': symmetry, 'conflict_budget': args.budget,
                       'phases_from_previous': use_previous, 'phases_from_fresh_family': use_family,
                       'model_only': args.model_only,
                       'stats': solver.accum_stats(), 'solver_seconds': time.monotonic() - start,
                       'verdict': int(verdict) if verdict is not None else None}
            if verdict is True:
                values = [False] * (1 << n)
                for lit in solver.get_model():
                    values[abs(lit) - 1] = lit > 0
                assert verify_assignment(triples, values)
                old.update(verdict=1, certified=True, assignment=''.join('1' if v else '0' for v in values),
                           witness_checked_knots=len(triples), solver=f'{args.solver} symmetry refinement')
                old.pop('reason', None)
            elif verdict is False and not args.model_only:
                proof = expanded_proof(solver.get_proof(), symmetry)
                proof_text = '\n'.join(proof) + '\n'
                proof_path = HERE / 'certificates' / f"{rec['key_id']}-L{n:02d}-{args.solver}-b{args.budget}-expanded.drup.gz"
                with gzip.open(proof_path, 'wt') as stream:
                    stream.write(proof_text)
                checking = time.monotonic()
                checked = ({'valid': False, 'reason': 'exact check deferred'} if args.defer_check else
                           check_fast(clauses, 1 << n, proof_path) if args.fast_checker else
                           RUPChecker(clauses, 1 << n).check(proof))
                attempt['proof_check'] = checked
                attempt['checker'] = 'deferred' if args.defer_check else 'check_rup_fast.cpp' if args.fast_checker else 'check_rup.py'
                if checked['valid']:
                    old.update(verdict=0, certified=True, solver=f'{args.solver} with symmetry and unconditional DRUP expansion',
                               certificate=str(proof_path.relative_to(HERE)), proof_check=checked,
                               certificate_uncompressed_sha256=hashlib.sha256(proof_text.encode()).hexdigest(),
                               certificate_lines=len(proof), certificate_check_seconds=time.monotonic() - checking,
                               checker=attempt['checker'],
                               symmetry_unit=False)
                    old.pop('reason', None)
                else:
                    attempt['unaccepted_certificate'] = str(proof_path.relative_to(HERE))
                    attempt['reason'] = ('Exact check deferred; level remains uncertified' if args.defer_check else
                                         'Solver proof not accepted as RUP; level remains uncertified')
        attempt['total_seconds'] = time.monotonic() - start
        old.setdefault('refinements', []).append(attempt)
        old['agrees'] = old['verdict'] is None or old['recorded_verdict'] is None or old['verdict'] == old['recorded_verdict']
        assert old['agrees'], (path, n, old)
        verdicts = [level['verdict'] for level in rec['levels']]
        rec.update(fresh_fate=fate(verdicts, rec['counts']),
                   fresh_first_death=next((n for n, v in enumerate(verdicts, 1) if v == 0), None),
                   fresh_return=any(v == 0 and 1 in verdicts[i + 1:] for i, v in enumerate(verdicts)),
                   all_levels_certified=all(level['certified'] for level in rec['levels']))
        rec['fate_agrees'] = rec['fresh_fate'] == rec['recorded_fate']
        path.write_text(json.dumps(rec, sort_keys=True, indent=2) + '\n')
        print(json.dumps({'key': rec['key_id'][:12], 'n': n, 'verdict': old['verdict'],
                          'certified': old['certified'], 'attempt': attempt}), flush=True)


if __name__ == '__main__':
    main()
