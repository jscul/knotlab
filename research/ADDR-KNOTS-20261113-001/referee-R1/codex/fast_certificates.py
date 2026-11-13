"""Adapter and controls for the fresh compiled DRUP verifier.

Compiler and all verifier scratch are confined to this directory. No SAT solver
is imported or used here. The Python verifier remains the reference comparator.
"""
import argparse
import gzip
import hashlib
import json
import random
import resource
import subprocess
import tempfile
import time
from pathlib import Path

from check_rup import RUPChecker
from fresh_patterns import cnf, fate, pattern

HERE = Path(__file__).resolve().parent
tempfile.tempdir = str(HERE)


def check_fast(clauses, nvars, proof_path):
    with tempfile.NamedTemporaryFile(mode='w', dir=HERE, prefix='.rup-input-', suffix='.cnf') as stream:
        stream.write(f'p cnf {nvars} {len(clauses)}\n')
        for clause in clauses:
            stream.write(' '.join(map(str, clause)) + ' 0\n')
        stream.flush()
        process = subprocess.run([str(HERE / 'check_rup_fast'), stream.name, str(proof_path)],
                                 capture_output=True, text=True)
    if process.returncode in (0, 1):
        result = json.loads(process.stdout)
        assert result['valid'] == (process.returncode == 0)
        return result
    return {'valid': False, 'reason': 'compiled verifier input error', 'stderr': process.stderr,
            'exit_code': process.returncode}


def plain_conflict(clauses, assumptions):
    assignment = {}
    for literal in assumptions:
        if abs(literal) in assignment and assignment[abs(literal)] != (literal > 0):
            return True
        assignment[abs(literal)] = literal > 0
    while True:
        additions = []
        for clause in clauses:
            if any(abs(lit) in assignment and assignment[abs(lit)] == (lit > 0) for lit in clause):
                continue
            unset = [lit for lit in clause if abs(lit) not in assignment]
            if not unset:
                return True
            if len(unset) == 1:
                additions.append(unset[0])
        if not additions:
            return False
        for literal in additions:
            if abs(literal) in assignment and assignment[abs(literal)] != (literal > 0):
                return True
            assignment[abs(literal)] = literal > 0


def controls():
    rng = random.Random(78196)
    tested = 0
    start = time.monotonic()
    for _ in range(100):
        n = rng.randrange(2, 9)
        clauses = []
        for _ in range(rng.randrange(1, 25)):
            variables = rng.sample(range(1, n + 1), rng.randrange(1, min(4, n) + 1))
            clauses.append([v * rng.choice([-1, 1]) for v in variables])
        for _ in range(3):
            candidate = [v * rng.choice([-1, 1]) for v in rng.sample(range(1, n + 1), rng.randrange(n + 1))]
            expected = plain_conflict(clauses, [-v for v in candidate])
            with tempfile.NamedTemporaryFile(dir=HERE, suffix='.drup.gz') as stream:
                with gzip.open(stream.name, 'wt') as zipped:
                    zipped.write(' '.join(map(str, candidate)) + ' 0\n')
                actual = check_fast(clauses, n, Path(stream.name))
            accepted_addition = actual['valid'] or actual.get('reason') == 'no derived empty clause'
            assert accepted_addition == expected, (clauses, candidate, expected, actual)
            tested += 1
    reference_cases = []
    for path in sorted((HERE / 'returns').glob('*.json')):
        rec = json.loads(path.read_text())
        for level in rec['levels']:
            if level['verdict'] == 0 and level['level'] <= 6:
                triples = pattern(rec['key'], level['level'])
                original = cnf(triples)
                proof_path = HERE / level['certificate']
                with gzip.open(proof_path, 'rt') as stream:
                    proof = stream.read().splitlines()
                python_result = RUPChecker(original, 1 << level['level']).check(proof)
                compiled_result = check_fast(original, 1 << level['level'], proof_path)
                assert python_result == compiled_result
                reference_cases.append({'key': rec['key_id'], 'level': level['level'], **compiled_result})
                break
        if len(reference_cases) == 20:
            break
    result = {'random_candidate_rup_against_plain_unit_propagation': tested,
              'saved_certificates_identical_to_python_checker': reference_cases,
              'seconds': time.monotonic() - start,
              'source_sha256': hashlib.sha256((HERE / 'check_rup_fast.cpp').read_bytes()).hexdigest(),
              'binary_sha256': hashlib.sha256((HERE / 'check_rup_fast').read_bytes()).hexdigest()}
    (HERE / 'fast_checker_controls.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'random_cases': tested, 'reference_certificates': len(reference_cases),
                      'seconds': result['seconds']}), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['controls', 'adopt'])
    parser.add_argument('--file')
    parser.add_argument('--level', type=int)
    parser.add_argument('--proof')
    parser.add_argument('--solver', default='Glucose4')
    parser.add_argument('--symmetry-reduced', action='store_true')
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (3 * 1024**3, 3 * 1024**3))
    if args.mode == 'controls':
        controls()
        return
    path = HERE / args.file
    proof_path = HERE / args.proof
    rec = json.loads(path.read_text())
    level = rec['levels'][args.level - 1]
    triples = pattern(rec['key'], args.level)
    clauses = cnf(triples)
    symmetry = None
    certificate_clauses = clauses
    if args.symmetry_reduced:
        # F is invariant under complementing every variable. Hence any model
        # can be complemented to satisfy v, and UNSAT(F & v) proves UNSAT(F).
        signatures = {tuple(sorted(clause)) for clause in clauses}
        assert signatures == {tuple(sorted(-lit for lit in clause)) for clause in clauses}
        symmetry = min(x for triple in triples for x in triple) + 1
        conditional = proof_path.with_name(proof_path.name.replace('.drup.gz', '.conditional.drup.gz'))
        reached_empty = False
        with gzip.open(proof_path, 'rt') as source, gzip.open(conditional, 'wt') as destination:
            for line in source:
                numbers = list(map(int, line.split()))
                assert numbers[-2:] == [-symmetry, 0], 'expected first-half conditional expansion'
                original = numbers[:-2]
                destination.write(' '.join(map(str, original)) + ' 0\n')
                if not original:
                    reached_empty = True
                    break
        assert reached_empty
        proof_path = conditional
        certificate_clauses = clauses + [[symmetry]]
    start = time.monotonic()
    checked = check_fast(certificate_clauses, 1 << args.level, proof_path)
    assert checked['valid'], checked
    with gzip.open(proof_path, 'rt') as stream:
        proof_text = stream.read()
    level.update(verdict=0, certified=True, proof_check=checked, checker='check_rup_fast.cpp',
                 certificate=str(proof_path.relative_to(HERE)),
                 certificate_uncompressed_sha256=hashlib.sha256(proof_text.encode()).hexdigest(),
                 certificate_lines=len(proof_text.splitlines()),
                 certificate_check_seconds=time.monotonic() - start,
                 solver=f'{args.solver} with unconditional complement-symmetry DRUP expansion')
    if symmetry is not None:
        level['symmetry_reduction'] = {'unit': symmetry, 'complement_invariance_checked': True,
                                       'rule': 'Any model of complement-invariant F can be complemented to satisfy this unit.'}
        level['symmetry_unit'] = symmetry
        level['solver'] = f'{args.solver}, complement-symmetry half with checked DRUP proof'
    level.pop('reason', None)
    level['agrees'] = level['recorded_verdict'] in (None, 0)
    assert level['agrees']
    verdicts = [entry['verdict'] for entry in rec['levels']]
    rec.update(fresh_fate=fate(verdicts, rec['counts']),
               all_levels_certified=all(entry['certified'] for entry in rec['levels']))
    rec['fate_agrees'] = rec['fresh_fate'] == rec['recorded_fate']
    path.write_text(json.dumps(rec, sort_keys=True, indent=2) + '\n')
    print(json.dumps({'key': rec['key_id'][:12], 'n': args.level, 'check': checked,
                      'seconds': level['certificate_check_seconds']}), flush=True)


if __name__ == '__main__':
    main()
