"""Replay the referee's saved SAT witnesses and DRUP certificates, with no solver.

Usage: .../.venv/bin/python -B path/to/replay_certificates.py [alternating|other|returns|sample|all]
The saved key defines each input; its reconstructed hash and CNF digest must agree.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import sys
import time
from pathlib import Path

from check_rup import RUPChecker
from fresh_patterns import cnf, fingerprint, pattern, verify_assignment
from fast_certificates import check_fast


def cnf_sha(clauses, nvars):
    digest = hashlib.sha256(f'p cnf {nvars} {len(clauses)}\n'.encode())
    for clause in clauses:
        digest.update((' '.join(map(str, clause)) + ' 0\n').encode())
    return digest.hexdigest()


def main():
    home = Path(__file__).resolve().parent
    mode = sys.argv[1] if len(sys.argv) > 1 else 'all'
    use_fast = '--fast' in sys.argv
    skip_checked = '--skip-checked' in sys.argv
    assert mode in ('alternating', 'other', 'returns', 'sample', 'all')
    if mode in ('alternating', 'other'):
        selected = {r['key_id'] for r in json.loads((home / f'{mode}_selection.json').read_text())}
        paths = sorted(p for p in (home / 'returns').glob('*.json') if p.stem in selected)
    elif mode != 'all':
        paths = sorted((home / mode).glob('*.json'))
    else:
        paths = sorted(list((home / 'returns').glob('*.json')) + list((home / 'sample').glob('*.json')))
    start = time.monotonic()
    rows = []
    for path in paths:
        saved = json.loads(path.read_text())
        patterns = [pattern(saved['key'], n) for n in range(1, 13)]
        assert fingerprint(patterns) == saved['recorded_pattern_hash']
        checked_levels = []
        for level in saved['levels']:
            n = level['level']
            triples = patterns[n - 1]
            clauses = cnf(triples)
            assert cnf_sha(clauses, 1 << n) == level['cnf_sha256']
            if level['verdict'] == 1:
                assignment = level['assignment']
                assert len(assignment) == 1 << n and set(assignment) <= {'0', '1'}
                assert verify_assignment(triples, [v == '1' for v in assignment])
                checked_levels.append({'level': n, 'verdict': 1, 'valid': True})
            elif level['verdict'] == 0:
                if level.get('symmetry_reduction'):
                    signatures = {tuple(sorted(clause)) for clause in clauses}
                    assert signatures == {tuple(sorted(-lit for lit in clause)) for clause in clauses}
                    unit = level['symmetry_reduction']['unit']
                    assert 1 <= unit <= 1 << n
                    clauses = clauses + [[unit]]
                with gzip.open(home / level['certificate'], 'rt') as stream:
                    proof_text = stream.read()
                assert hashlib.sha256(proof_text.encode()).hexdigest() == level['certificate_uncompressed_sha256']
                if skip_checked and level.get('checker') == 'check_rup_fast.cpp':
                    # This proof was already checked by the standalone verifier
                    # from this exact saved file during adoption. Recheck its
                    # digest/binding here, while avoiding a second large run.
                    check = {'valid': level['proof_check']['valid'],
                             'previous_standalone_disk_check_reused': True,
                             'repropagated_in_this_replay': False}
                else:
                    check = (check_fast(clauses, 1 << n, home / level['certificate']) if use_fast
                             else RUPChecker(clauses, 1 << n).check(proof_text.splitlines()))
                assert check['valid'], (path.name, n, check)
                checked_levels.append({'level': n, 'verdict': 0, **check})
            else:
                checked_levels.append({'level': n, 'verdict': None, 'valid': False})
        rows.append({'file': str(path.relative_to(home)), 'key_id': saved['key_id'],
                     'levels': checked_levels})
        print(json.dumps({'replayed': str(path.relative_to(home)), 'levels': len(checked_levels)}), flush=True)
    result = {'solver_used': False, 'checker': 'check_rup_fast.cpp' if use_fast else 'check_rup.py',
              'keys': rows, 'seconds': time.monotonic() - start}
    (home / f'certificate_replay_{mode}.json').write_text(json.dumps(result, indent=2) + '\n')


if __name__ == '__main__':
    main()
