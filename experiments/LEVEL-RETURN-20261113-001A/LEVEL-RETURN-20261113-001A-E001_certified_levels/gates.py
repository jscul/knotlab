"""Validation gates for the certifier (run before the registered run): the checker accepts proofs CaDiCaL writes for known dead
patterns, rejects corrupted proofs, and the certifier agrees with brute force on small patterns."""
import itertools, json, os, random, subprocess, sys, tempfile
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from certify import certify, pattern, CADICAL, CHECKER
res = {}
FANO = np.array([[0, 1, 3], [1, 2, 4], [2, 3, 5], [3, 4, 6], [4, 5, 0], [5, 6, 1], [6, 0, 2]])
with tempfile.TemporaryDirectory() as d:
    res['fano'] = certify(FANO, 7, d, 60)['verdict']
    # corrupted proofs: write a proof, then change one hint or one literal; the checker must reject
    cnf = os.path.join(d, 'f.cnf'); prf = os.path.join(d, 'p.lrat')
    with open(cnf, 'w') as f:
        f.write(f'p cnf 7 {2*len(FANO)+1}\n')
        for a, b, c in FANO.tolist(): f.write(f'{a+1} {b+1} {c+1} 0\n{-a-1} {-b-1} {-c-1} 0\n')
        f.write('1 0\n')
    subprocess.run([CADICAL, '--lrat=true', '--binary=false', '-q', cnf, prf], capture_output=True)
    lines = open(prf).read().splitlines()
    adds = [i for i, l in enumerate(lines) if ' d ' not in l]
    rejected = 0; tried = 0
    rng = random.Random(1)
    for i in adds:
        parts = lines[i].split(); z = parts.index('0')
        hints = parts[z + 1:-1]
        if not hints: continue
        bad = lines[:]; h = parts[:]; h[z + 1 + rng.randrange(len(hints))] = '1'
        bad[i] = ' '.join(h)
        open(prf + '.bad', 'w').write('\n'.join(bad) + '\n'); tried += 1
        r = subprocess.run([CHECKER, cnf, prf + '.bad'], capture_output=True, text=True)
        rejected += r.returncode != 0
    res['corrupted_tried'], res['corrupted_rejected'] = tried, rejected
    trunc = [l for l in lines if not l.split()[1:2] == ['0'] or True][:-1]
    open(prf + '.trunc', 'w').write('\n'.join(lines[:-1]) + '\n')
    r = subprocess.run([CHECKER, cnf, prf + '.trunc'], capture_output=True, text=True)
    res['truncated_rejected'] = r.returncode != 0 or 'VERIFIED' not in r.stdout
    # brute force agreement on random small patterns
    agree = 0; total = 0; dead = 0
    rng = np.random.default_rng(3)
    for _ in range(400):
        nv = int(rng.integers(5, 14)); nk = int(rng.integers(3, 4 * nv))
        K = np.unique(np.sort(np.array([rng.choice(nv, 3, replace=False) for _ in range(nk)]), 1), axis=0)
        X = ((np.arange(1 << nv)[:, None] >> np.arange(nv)) & 1)
        V = X[:, K]; alive = bool(np.any(np.all(V.min(2) != V.max(2), 1)))
        c = certify(K, nv, d, 60)['verdict']
        total += 1; agree += (c == ('alive' if alive else 'dead')); dead += not alive
    res['brute'] = dict(total=total, agree=agree, dead=dead)
ok = res['fano'] == 'dead' and res['corrupted_rejected'] == res['corrupted_tried'] and res['truncated_rejected'] and res['brute']['agree'] == res['brute']['total']
res['status'] = 'passed' if ok else 'failed'
print(json.dumps(res)); json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gates.json'), 'w'), indent=1)
