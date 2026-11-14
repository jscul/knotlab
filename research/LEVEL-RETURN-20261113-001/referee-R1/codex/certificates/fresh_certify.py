"""Fresh certificate audit, with no imports from the LEVEL-RETURN producer.

Run with .venv/bin/python -B. All writes stay beside this file. The earlier
independently authored ADDR reconstruction is explicitly reused and hash-bound.
The registered certificates were deleted; none of these is an original replay.
"""
from __future__ import annotations

import argparse
import ctypes
import gzip
import hashlib
import importlib.util
import itertools
import json
import os
from pathlib import Path
import random
import resource
import struct
import subprocess
import tempfile
import time

HERE = Path(__file__).resolve().parent
tempfile.tempdir = str(HERE)
os.environ['TMPDIR'] = str(HERE)
ROOT = HERE.parents[4]
EARLIER = ROOT / 'research/ADDR-KNOTS-20261113-001/referee-R1/codex'
SOURCE = EARLIER / 'fresh_patterns.py'
REGDIR = ROOT / 'experiments/LEVEL-RETURN-20261113-001A/LEVEL-RETURN-20261113-001A-E001_certified_levels'
SUMMARY = ROOT / 'research/LEVEL-RETURN-20261113-001/summary.json'
spec = importlib.util.spec_from_file_location('earlier_independent_patterns', SOURCE)
fresh = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fresh)


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def registered():
    return {x['result']['case']: x['result'] for x in
            (json.loads(line) for line in (REGDIR / 'run3/results.jsonl').read_text().splitlines())}


def keys():
    return {r['key_id'][:16]: r for r in
            (json.loads(p.read_text()) for p in (EARLIER / 'returns').glob('*.json'))}


def dimacs(clauses, nvars):
    return ('p cnf %d %d\n' % (nvars, len(clauses)) +
            ''.join(' '.join(map(str, c)) + ' 0\n' for c in clauses)).encode()


def pattern_hash(triples):
    return sha(struct.pack('<%dq' % (3 * len(triples)), *(v for t in triples for v in t)))


def checker(cnf, proof):
    start = time.monotonic()
    try:
        p = subprocess.run([str(HERE / 'check_rup_fast'), str(cnf), str(proof)],
                           text=True, capture_output=True, timeout=180)
    except subprocess.TimeoutExpired:
        return {'valid': False, 'reason': 'checker timeout', 'timeout_seconds': 180,
                'seconds': time.monotonic()-start}
    try:
        result = json.loads(p.stdout)
    except json.JSONDecodeError:
        result = {'valid': False, 'reason': p.stderr.strip()}
    return {**result, 'exit_code': p.returncode, 'seconds': time.monotonic() - start}


def input_for(case):
    key, level = case.rsplit('-L', 1)
    level = int(level)
    rec = keys()[key]
    triples = fresh.pattern(rec['key'], level)
    r = registered().get(case)
    clauses = fresh.cnf(triples)
    meta = {
        'case': case, 'key_id': rec['key_id'], 'n': level,
        'knots': len(triples), 'pattern_sha256': pattern_hash(triples),
        'original_cnf_available': False, 'original_model_available': False,
        'original_refutation_available': False, 'evidence_kind': 'fresh recertification',
        'generator_source_sha256': sha(SOURCE.read_bytes()),
        'unconditional_cnf_sha256': sha(dimacs(clauses, 1 << level)),
        'registered': r,
        'registered_pattern_hash_matches': r is not None and pattern_hash(triples) == r['pattern_sha256'],
        'registered_count_matches': r is not None and len(triples) == r['knots'],
    }
    return rec, triples, clauses, meta


def direct_action(key, state, address, level):
    _, sw, d0, d1, _ = key
    out = 0
    for letter in [(address >> i) & 1 for i in reversed(range(level))]:
        out = (out << 1) | (letter ^ sw[state])
        state = (d0 if letter == 0 else d1)[state]
    return out


def direct_pattern(key, level, wrong_order=False):
    words = [()] + [(q,) for q in range(key[0])] + list(itertools.product(range(key[0]), repeat=2))
    result = set()
    for p in key[4]:
        for x in range(1 << level):
            values = []
            for i in p:
                value = x
                for q in words[i] if wrong_order else reversed(words[i]):
                    value = direct_action(key, q, value, level)
                values.append(value)
            if len(set(values)) == 3:
                result.add(tuple(sorted(values)))
    return sorted(result)


def verify_model(triples, text, nvars):
    if len(text) != nvars or any(c not in '01' for c in text):
        return {'valid': False, 'reason': 'malformed or incomplete assignment'}
    violations = [t for t in triples if len({text[v] for v in t}) != 2]
    return {'valid': not violations, 'checked_knots': len(triples),
            'violated_knots': len(violations), 'first_violation': violations[:1]}


def controls():
    from pysat.solvers import Glucose4
    key_records = keys()
    seven = [r['key'] for r in json.loads(SUMMARY.read_text())['R1']['rows']]
    direct = []
    wrong_order_detected = []
    for key_id in seven:
        key = key_records[key_id]['key']
        for n in range(1, 7):
            expected = direct_pattern(key, n)
            actual = fresh.pattern(key, n)
            assert actual == expected
            direct.append({'key': key_id, 'level': n, 'knots': len(actual)})
            if direct_pattern(key, n, True) != actual:
                wrong_order_detected.append({'key': key_id, 'level': n})
    fano = [(0,1,2), (0,3,4), (0,5,6), (1,3,5), (1,4,6), (2,3,6), (2,4,5)]
    clauses = fresh.cnf(fano)
    positive_cnf = HERE / 'control_fano.cnf'
    positive_cnf.write_bytes(dimacs(clauses, 7))
    with Glucose4(bootstrap_with=clauses, with_proof=True) as solver:
        assert solver.solve() is False
        proof = solver.get_proof()
    results = {}
    for name, lines in [('positive', proof), ('truncated', proof[:-1]),
                        ('malformed', ['bogus 0']), ('non_rup', ['0']),
                        ('out_of_bounds', ['8 0'])]:
        path = HERE / ('control_' + name + '.drup.gz')
        with gzip.open(path, 'wt') as stream:
            stream.write('\n'.join(lines) + '\n')
        results[name] = checker(positive_cnf, path)
        assert results[name]['valid'] == (name == 'positive')
    model_controls = {
        'positive': verify_model([(0,1,2)], '001', 3),
        'wrong': verify_model([(0,1,2)], '000', 3),
        'truncated': verify_model([(0,1,2)], '00', 3),
        'malformed': verify_model([(0,1,2)], '01x', 3),
    }
    assert model_controls['positive']['valid']
    assert all(not value['valid'] for k, value in model_controls.items() if k != 'positive')
    result = {'direct_letter_by_letter_pattern_agreements': direct,
              'wrong_word_order_detected': wrong_order_detected,
              'proof_controls': results, 'model_controls': model_controls,
              'checker_source_sha256': sha((HERE/'check_rup_fast.cpp').read_bytes()),
              'checker_binary_sha256': sha((HERE/'check_rup_fast').read_bytes()),
              'generator_source_sha256': sha(SOURCE.read_bytes())}
    dump(HERE / 'controls.json', result)
    print(json.dumps({'controls': 'passed', 'direct_patterns': len(direct),
                      'wrong_order_differences': len(wrong_order_detected)}), flush=True)


def inventory():
    fields = {}
    for name in ('run3', 'run_rigid3'):
        rows = [json.loads(line) for line in (REGDIR/name/'results.jsonl').read_text().splitlines()]
        dead = [r for r in rows if (r.get('result') or {}).get('verdict') == 'dead']
        def hash_fields(value, prefix=''):
            found = []
            if isinstance(value, dict):
                for key, item in value.items():
                    path = prefix+'.'+key if prefix else key
                    if 'sha' in key.lower() or 'hash' in key.lower():
                        found.append(path)
                    found.extend(hash_fields(item,path))
            elif isinstance(value, list):
                for index, item in enumerate(value):
                    found.extend(hash_fields(item,prefix+'['+str(index)+']'))
            return found
        all_hash_fields = sorted({f for r in rows for f in hash_fields(r)})
        fields[name] = {'rows': len(rows), 'dead_verdict_rows': len(dead),
                        'retained_hash_field_names': all_hash_fields,
                        'proof_or_certificate_hash_field_names': [f for f in all_hash_fields if
                                                               'proof' in f.lower() or 'certificate' in f.lower()],
                        'dead_certificate_examples': [r['result'].get('certificate') for r in dead[:3]]}
    out = {'evidence_gap': 'Original CNF, models and LRAT proofs are not retained in the registered run directories.',
           'directories': {name: sorted(str(p.relative_to(ROOT)) for p in (REGDIR/name).iterdir())
                           for name in ('run3', 'run_rigid3')},
           'registered_input_sha256': sha((REGDIR/'run3/results.jsonl').read_bytes()),
           'record_field_inventory': fields,
           'restriction': 'No producer Python/C was read or imported; no LRAT hints were consumed.'}
    dump(HERE/'inventory.json', out)
    contract = {'question': 'Do fresh spec-derived patterns independently support sampled registered alive/dead verdicts?',
                'branch': 'code_analysis', 'evidence_stage': 'independent finite audit',
                'inputs': ['frozen ADDR codex_spec.md', str(SOURCE.relative_to(ROOT)),
                           'earlier independent returns/*.json keys', 'run3/results.jsonl', 'summary.json'],
                'forbidden_inputs': ['LEVEL-RETURN producer Python/C', 'LEVEL-RETURN summarize.py'],
                'outputs': 'Hash-bound reconstructed CNFs; checked fresh models or RUP refutations; undecided explicit.',
                'controls': 'Direct letter actions, wrong word order, Fano proof, malformed/truncated/non-RUP proofs, wrong models.',
                'resource_budget': 'One compute process at once; RLIMIT_AS 3 GiB; bounded conflicts; per-checker timeout 180 s.',
                'stop_rule': 'One first pass over seven patterns levels 13..16, prioritized dead; bounded other samples and follow-up.',
                'nonclaims': ['Original deleted-certificate replay', 'uniform all-level proof', 'resolution of every undecided level']}
    dump(HERE/'interface.json', contract)
    print(json.dumps({'inventory': 'no original certificates'}))


def reconstruct(cases):
    for case in cases:
        _, _, _, meta = input_for(case)
        assert meta['registered_pattern_hash_matches'] and meta['registered_count_matches']
        dump(HERE/(case+'.input.json'), meta)
        print(json.dumps({'case': case, 'knots': meta['knots'], 'pattern_matches': True}), flush=True)


def solve(case, solver_name, budget):
    from pysat.solvers import Cadical195, Glucose4
    start = time.monotonic()
    rec, triples, clauses, meta = input_for(case)
    assert meta['registered_pattern_hash_matches'] and meta['registered_count_matches']
    n = meta['n']; nvars = 1 << n
    prefix = case+'.'+solver_name+'.b'+str(budget)
    record = {**meta, 'solver': solver_name, 'conflict_budget': budget}
    # These are explicit states from the registered claim, checked directly.
    model = None
    if case.startswith('91c75673c09d9046') and n % 2:
        model = ''.join(str(x.bit_count() % 2) for x in range(nvars))
        record['model_source'] = 'explicit address parity'
    elif case.startswith('f4fd01e9afa56314') and not n % 2:
        model = ''.join(str((x >> (n-1)) ^ (x & 1)) for x in range(nvars))
        record['model_source'] = 'explicit first letter XOR last'
    if model is not None:
        record['model_check'] = verify_model(triples, model, nvars)
        assert record['model_check']['valid']
        result = True
    else:
        # Complementing all values preserves every NAE constraint. A contradiction
        # after fixing the least address therefore certifies the unrestricted CNF.
        unit = min((v for t in triples for v in t), default=-1) + 1
        if unit:
            signs = {tuple(c) for c in clauses}
            assert all(tuple(-v for v in c) in signs for c in clauses)
            clauses.append([unit])
        record['complement_symmetry_unit'] = unit or None
        record['complement_invariance_checked'] = True
        record['certificate_cnf_sha256'] = sha(dimacs(clauses, nvars))
        solver_class = {'cadical195': Cadical195, 'glucose4': Glucose4}[solver_name]
        with solver_class(bootstrap_with=clauses, with_proof=True) as solver:
            # Lift the previous same-parity earlier independent model as a phase
            # preference only. It is never treated as a certificate at this level.
            earlier = [x for x in rec['levels'] if x.get('assignment') and x['level'] < n and x['level'] % 2 == n % 2]
            if case.startswith('91c75673c09d9046'):
                solver.set_phases([x+1 if x.bit_count() % 2 else -x-1 for x in range(nvars)])
                record['phase_source'] = 'address parity, used only as a solver preference'
            elif earlier:
                prev = earlier[-1]
                assignment = prev['assignment']; shift = n-prev['level']
                solver.set_phases([x+1 if assignment[x >> shift] == '1' else -x-1 for x in range(nvars)])
                record['phase_level'] = prev['level']
            solver.conf_budget(budget)
            solving = time.monotonic()
            result = solver.solve_limited()
            record['solve_seconds'] = time.monotonic()-solving
            record['solver_stats'] = solver.accum_stats()
            if result is True:
                values = {abs(lit)-1: int(lit > 0) for lit in solver.get_model()}
                model = ''.join(str(values.get(x, 0)) for x in range(nvars))
                record['model_source'] = 'fresh SAT solve'
            if result is False and solver_name == 'cadical195':
                # PySAT's C trace owns a FILE* buffer separate from prfile.
                # fflush(NULL) affects only C streams in this process.
                assert ctypes.CDLL(None).fflush(None) == 0
                record['proof_buffer_flush'] = 'process-local libc fflush(NULL) before get_proof()'
            proof = solver.get_proof() if result is False else None
        if result is False:
            cnf_path = HERE/(prefix+'.cnf')
            cnf_path.write_bytes(dimacs(clauses, nvars))
            proof_path = HERE/(prefix+'.drup.gz')
            with gzip.open(proof_path, 'wt', compresslevel=6) as stream:
                stream.write('\n'.join(proof)+'\n')
            record['proof_path'] = proof_path.name
            record['proof_uncompressed_sha256'] = sha(('\n'.join(proof)+'\n').encode())
            record['proof_lines'] = len(proof)
            del proof
            record['proof_check'] = checker(cnf_path, proof_path)
            record['cnf_path'] = cnf_path.name + '.gz'
            with gzip.open(str(cnf_path)+'.gz', 'wb', compresslevel=6) as stream:
                stream.write(cnf_path.read_bytes())
            cnf_path.unlink()  # Only this task's regenerable uncompressed scratch.
    record['verdict'] = {True:'alive', False:'dead', None:'undecided'}[result]
    if result is True:
        record['model_check'] = verify_model(triples, model, nvars)
        assert record['model_check']['valid']
        record['assignment_sha256'] = sha(model.encode())
        model_path = HERE/(prefix+'.model.gz')
        with gzip.open(model_path, 'wt') as stream:
            stream.write(model+'\n')
        record['model_path'] = model_path.name
    record['certified'] = (result is True and record['model_check']['valid']) or (result is False and record['proof_check']['valid'])
    record['agrees_with_registered_decided'] = (record['registered']['verdict'] == 'undecided' or result is None or
                                                record['verdict'] == record['registered']['verdict'])
    record['seconds'] = time.monotonic()-start
    result_path = HERE/(prefix+'.result.json')
    if result_path.exists():
        raise FileExistsError(result_path)
    dump(result_path, record)
    print(json.dumps({k: record[k] for k in ('case','verdict','certified','seconds','agrees_with_registered_decided')}, sort_keys=True), flush=True)


def main():
    resource.setrlimit(resource.RLIMIT_AS, (3*1024**3, 3*1024**3))
    parser = argparse.ArgumentParser()
    parser.add_argument('operation', choices=['controls','inventory','reconstruct','solve'])
    parser.add_argument('cases', nargs='*')
    parser.add_argument('--solver', choices=['glucose4','cadical195'], default='glucose4')
    parser.add_argument('--budget', type=int, default=50000)
    args = parser.parse_args()
    if args.operation == 'controls': controls()
    elif args.operation == 'inventory': inventory()
    elif args.operation == 'reconstruct': reconstruct(args.cases)
    elif args.operation == 'solve':
        for case in args.cases: solve(case,args.solver,args.budget)


if __name__ == '__main__':
    main()
