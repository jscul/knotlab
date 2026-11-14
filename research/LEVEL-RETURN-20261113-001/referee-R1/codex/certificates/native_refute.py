"""Bounded fresh CaDiCaL 2.1.2 LRAT production; hints never trusted.

The LRAT additions are stripped to DRUP, then checked by the old independent
RUP engine. The solver and checker run sequentially, one compute process.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path
import resource
import subprocess
import time

import fresh_certify as audit

HERE = Path(__file__).resolve().parent
BINARY = Path('/home/jscul/.elan/toolchains/leanprover--lean4---v4.35.0/bin/cadical')


def convert(source, destination):
    """Read LRAT ids/clauses, discard all hints and deletions, emit additions."""
    raw_sha = hashlib.sha256()
    drup_sha = hashlib.sha256()
    additions = deletions = empty = lines = 0
    largest_id = 0
    with source.open('rb') as src, gzip.open(destination, 'wb', compresslevel=6) as dst:
        for raw in src:
            lines += 1
            raw_sha.update(raw)
            values = raw.split()
            if not values or values[0] == b'c':
                continue
            clause_id = int(values[0])
            if clause_id < 0:
                raise ValueError('negative LRAT id')
            if len(values) > 1 and values[1] == b'd':
                if values[-1] != b'0':
                    raise ValueError('unterminated deletion')
                deletions += 1
                continue
            if clause_id <= largest_id:
                raise ValueError('non-increasing LRAT addition id')
            largest_id = clause_id
            numbers = [int(v) for v in values[1:]]
            zero = numbers.index(0)
            if not numbers[zero+1:] or numbers[-1] != 0:
                raise ValueError('missing LRAT hint terminator')
            clause = numbers[:zero]
            out = (' '.join(map(str,clause)) + (' ' if clause else '') + '0\n').encode()
            dst.write(out)
            drup_sha.update(out)
            additions += 1
            empty += not clause
    return {'lrat_lines': lines, 'additions': additions, 'deletions_discarded': deletions,
            'empty_additions': empty, 'lrat_sha256': raw_sha.hexdigest(),
            'drup_uncompressed_sha256': drup_sha.hexdigest(),
            'hints_consumed_by_checker': False}


def refute(prefix, clauses, nvars, budget, seconds):
    cnf = HERE/(prefix+'.cnf')
    lrat = HERE/(prefix+'.lrat')
    proof = HERE/(prefix+'.drup.gz')
    cnf.write_bytes(audit.dimacs(clauses,nvars))
    command = [str(BINARY), '-q', '--no-witness', '--no-binary', '--lrat',
               '-c', str(budget), '-t', str(seconds), str(cnf), str(lrat)]
    start = time.monotonic()
    process = subprocess.run(command,capture_output=True,text=True,timeout=seconds+30)
    result = {'command': command, 'solver_binary_sha256': audit.sha(BINARY.read_bytes()),
              'solver_version': '2.1.2', 'solver_exit_code': process.returncode,
              'solver_stdout': process.stdout, 'solver_stderr': process.stderr,
              'solve_seconds': time.monotonic()-start,
              'certificate_cnf_sha256': audit.sha(cnf.read_bytes()),
              'conflict_budget': budget, 'solver_seconds_limit': seconds}
    result['conversion'] = convert(lrat,proof)
    result['proof_check'] = audit.checker(cnf,proof)
    for path in (cnf,lrat):
        with path.open('rb') as source, gzip.open(str(path)+'.gz','wb',compresslevel=6) as destination:
            while chunk := source.read(1024*1024):
                destination.write(chunk)
        path.unlink()  # Only our uncompressed scratch; both compressed artifacts retained.
    result.update(cnf_path=cnf.name+'.gz',lrat_path=lrat.name+'.gz',proof_path=proof.name)
    result['certified'] = process.returncode == 20 and result['proof_check']['valid']
    result['seconds'] = time.monotonic()-start
    return result


def main():
    resource.setrlimit(resource.RLIMIT_AS,(3*1024**3,3*1024**3))
    parser = argparse.ArgumentParser()
    parser.add_argument('case')
    parser.add_argument('--budget',type=int,default=3000000)
    parser.add_argument('--seconds',type=int,default=300)
    args = parser.parse_args()
    if args.case == 'control':
        fano = [(0,1,2),(0,3,4),(0,5,6),(1,3,5),(1,4,6),(2,3,6),(2,4,5)]
        result = refute('native_fano',audit.fresh.cnf(fano),7,10000,10)
        assert result['certified']
        audit.dump(HERE/'native_control.json',result)
    else:
        _,triples,clauses,meta = audit.input_for(args.case)
        assert meta['registered_pattern_hash_matches'] and meta['registered_count_matches']
        signatures = {tuple(c) for c in clauses}
        assert all(tuple(-v for v in c) in signatures for c in clauses)
        unit = min(v for t in triples for v in t)+1
        clauses.append([unit])
        prefix = args.case+'.cadical212.b'+str(args.budget)
        result = {**meta, **refute(prefix,clauses,1<<meta['n'],args.budget,args.seconds),
                  'solver': 'cadical212', 'complement_invariance_checked': True,
                  'complement_symmetry_unit': unit}
        result['verdict'] = 'dead' if result['certified'] else 'undecided'
        result['agrees_with_registered_decided'] = result['verdict'] in ('undecided',meta['registered']['verdict'])
        audit.dump(HERE/(prefix+'.result.json'),result)
    print(json.dumps({k:result[k] for k in ('certified','seconds','proof_check')}),flush=True)


if __name__ == '__main__':
    main()
