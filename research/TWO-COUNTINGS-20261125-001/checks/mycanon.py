"""Run the canonical knotlab checker on chosen rules of chosen structures (checker's own CNF writer)."""
import itertools
import json
import resource
import subprocess
import sys
import time

REPO = 'REPO_ROOT'
PY = REPO + '/.venv/bin/python3'


def cap():
    resource.setrlimit(resource.RLIMIT_AS, (6 * 1024 ** 3, 6 * 1024 ** 3))


def clauses(rules):
    out = []
    for law, P in rules:
        if law == 'nae':
            out.append(' '.join(P))
            out.append(' '.join('~' + p for p in P))
            continue
        par = 0 if law == 'even' else 1
        for bits in itertools.product((0, 1), repeat=len(P)):
            if sum(bits) % 2 != par:
                # clause false exactly at this assignment
                out.append(' '.join(('~' + p) if b else p for p, b in zip(P, bits)))
    return ';'.join(out)


def run(rules, i):
    law, P = rules[i]
    allv = sorted({p for _, Q in rules for p in Q})
    wit = [v for v in allv if v not in P]
    cmd = [PY, '-B', '-m', 'knotlab', 'check', '--cnf', clauses(rules), '--loops', *P[:-1], '--contact', P[-1],
           '--json']
    if wit:
        cmd += ['--witnesses', *wit]
    t = time.time()
    r = subprocess.run(cmd, cwd=REPO, env={'PYTHONPATH': 'tools', 'PATH': '/usr/bin:/bin'}, capture_output=True,
                       text=True, preexec_fn=cap, timeout=1200)
    dt = time.time() - t
    if r.returncode:
        return {'error': r.stderr[-400:], 'sec': dt}
    d = json.loads(r.stdout)
    return {'K1': d['binding'], 'K2': d['loss_on_erasure'], 'K3': d['coexistence'], 'knot': d['is_knot'],
            'allowed': sorted(d['allowed']), 'vars': d.get('variables'), 'sec': round(dt, 2)}


if __name__ == '__main__':
    S = json.load(open(sys.argv[1]))
    jobs = json.load(open(sys.argv[2]))  # [[structure name, rule index], ...]
    res = []
    for name, i in jobs:
        rules = [(l, tuple(p)) for l, p in S[name]]
        r = run(rules, i)
        r['structure'] = name
        r['rule'] = '%s(%s)' % (rules[i][0], ','.join(rules[i][1]))
        res.append(r)
        print(json.dumps({k: r[k] for k in r if k not in ('allowed',)}), r.get('allowed'), flush=True)
    json.dump(res, open(sys.argv[3], 'w'), indent=1)
