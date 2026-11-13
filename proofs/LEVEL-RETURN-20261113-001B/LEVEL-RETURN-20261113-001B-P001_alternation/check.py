"""Runs the all-level product checks of prover.py for descriptions #2 and #3 and writes result.json.
Run from the repository root: .venv/bin/python -B proofs/LEVEL-RETURN-20261113-001B/LEVEL-RETURN-20261113-001B-P001_alternation/check.py"""
import json, os, sys, hashlib
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from prover import check, words_of, PARITY, FIRST_LAST
TWO = (([1, 0, 1], [0, 2, 2], [2, 1, 1]), [[0, 8, 10], [1, 8, 12], [1, 9, 10]])
THREE = (([1, 0, 1], [0, 2, 1], [0, 1, 1]), [[0, 1, 11], [0, 2, 3], [0, 2, 12], [0, 7, 9], [1, 7, 11], [1, 9, 10], [4, 7, 10], [5, 6, 7], [7, 9, 12]])
W = words_of(3)
res = {
    'two_parity_odd_from_3': check(TWO[0], W, TWO[1], PARITY, 1, 3),
    'two_parity_even_from_4': check(TWO[0], W, TWO[1], PARITY, 0, 4),
    'three_first_last_even_from_2': check(THREE[0], W, THREE[1], FIRST_LAST, 0, 2),
    'three_first_last_odd_from_3': check(THREE[0], W, THREE[1], FIRST_LAST, 1, 3),
}
ok = res['two_parity_odd_from_3'][0] and res['three_first_last_even_from_2'][0] and not res['two_parity_even_from_4'][0]
out = dict(status='passed' if ok else 'failed', checks={k: list(v) for k, v in res.items()},
           prover_sha256=hashlib.sha256(open(os.path.join(HERE, 'prover.py'), 'rb').read()).hexdigest())
json.dump(out, open(os.path.join(HERE, 'result.json'), 'w'), indent=1); print(out['status'], {k: v[0] for k, v in res.items()})
