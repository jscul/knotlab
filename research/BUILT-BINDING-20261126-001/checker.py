"""checker.py OUT.json: the canonical knot checker on the relation of the three ring facts.  BUILT-BINDING-20261126-001.

No value is defined as a sum of the others: each z_i is the parity of its own ring's four shared distinctions.  The
relation is the set of their joint values once every distinction of the start is quantified away (built.tuples_linear,
checked by a solver call per tuple); written as clauses that exclude each tuple that does not occur, it goes to
`knotlab check` with each choice of contact.  The variant with two loose distinctions at J is the control."""
import sys, os, json, itertools, subprocess
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import built as BU


def check(occ, contact):
    names = ['z1', 'z2', 'z3']
    clauses = []
    for v in itertools.product((0, 1), repeat=3):
        if v not in occ: clauses.append(' '.join(('~' if b else '') + n for n, b in zip(names, v)))
    cnf = '; '.join(clauses) if clauses else 'z1 ~z1'
    loops = [n for n in names if n != contact]
    out = subprocess.run([sys.executable, '-B', '-m', 'knotlab', 'check', '--cnf', cnf, '--loops', *loops, '--contact', contact,
                          '--json'], capture_output=True, text=True, cwd=ROOT, env=dict(os.environ, PYTHONPATH=str(ROOT / 'tools')))
    return {'contact': contact, 'clauses': cnf, 'checker': json.loads(out.stdout) if out.stdout.strip() else out.stderr[-400:]}


if __name__ == '__main__':
    res = []
    for var in ('base', 'J two loose'):
        S, rings = BU.build(var)
        occ = {tuple(x) for x in BU.tuples_linear(S, rings)}
        assert occ == {tuple(x) for x in BU.tuples_solver(S, rings)}
        res.append({'variant': var, 'tuples': sorted(occ), 'checks': [check(occ, c) for c in ('z3', 'z1', 'z2')]})
    json.dump(res, open(sys.argv[1], 'w'), indent=1)
    for r in res:
        print(r['variant'], len(r['tuples']), [(c['contact'], {k: v for k, v in c['checker'].items() if k in ('knot', 'K1', 'K2', 'K3', 'is_knot')}
                                                if isinstance(c['checker'], dict) else c['checker']) for c in r['checks']])
