"""Post hoc readings of LOOP-CATALOGUE-20261119-001B-E001 (after the frozen read-out; labelled so in the note).

C2*: the starts where W's root and the rule's rate differed by more than 10^-5, recomputed with W to 120 terms (the frozen run
     truncated W at 30 terms, which cuts the infinite series of an endless chain).
I2*: I2 re-scored to the pre-registration's wording: loop knots are the knots on the loop's cycle (the scorer also took the side
     knots of its blocks), and a hanging path of two multiplies W by (1 + y)/(1 - y) (the scorer kept the advisor's (1 + y)^2).
R1*: the even rings with a spare, whose two loops the frozen W left uncomputed: W of the loop holding the spare.
python3 -B posthoc.py <runner out dir> <out.json>"""
import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import eddy as E  # noqa: E402
import loopweight as LW  # noqa: E402
sys.path.insert(0, str(E.ROOT / 'scripts'))
from longrun import load_results  # noqa: E402


def cycle_knots(sz, e):
    A = E.Cl.analyse(sz, e)
    out = set()
    for ks, bs, r, bare, meet in E.pieces(A):
        if r != 1:
            continue
        nb = defaultdict(set)
        for i in bs:
            for z in A['blocks'][i]:
                nb[('b', i)].add(('k', z))
                nb[('k', z)].add(('b', i))
        alive = set(nb)
        changed = True
        while changed:
            changed = False
            for v in list(alive):
                if len(nb[v] & alive) <= 1:
                    alive.discard(v)
                    changed = True
        out |= {v[1] for v in alive if v[0] == 'k'}
    return out


def div(a, b, n=10):
    ia = next(i for i, x in enumerate(a) if x)
    ib = next(i for i, x in enumerate(b) if x)
    a, b = a[ia:], b[ib:]
    r = list(a) + [0] * n
    q = []
    for k in range(n):
        c = r[k] / b[0]
        q.append(c)
        for j, x in enumerate(b):
            if k + j < len(r):
                r[k + j] -= c * x
    return ia - ib, q


def main():
    R = load_results(sys.argv[1])
    out = {'C2*': [], 'I2*': {'n': 0, 'agree': 0, 'differ': []}, 'R1*': []}
    want = {'spare': [1, 1] + [0] * 8, 'lone': [1, 1] + [0] * 8, 'lone+spare': [1, 1, 1] + [0] * 7, 'path2': [1] + [2] * 9}
    for c in sorted(R):
        if not c.startswith('I-') or R[c].get('status') != 'ok':
            continue
        x = R[c]['result']
        ent = x['entry']
        base = LW.round_weight(ent['sizes'], [tuple(v) for v in ent['edges']], 120)
        loop = cycle_knots(ent['sizes'], [tuple(v) for v in ent['edges']])
        for row in x['interfaces']:
            sz, e = row['sizes'], [tuple(v) for v in row['edges']]
            eq = row['equation']
            if row['exact'] and row['W'] and row['W'].get('rate') and eq.get('kind') == 'rational' and \
                    abs(row['W']['rate'] - eq['ratio']) > 1e-5:
                W = LW.round_weight(sz, e, 120)
                r = 1 / LW.root(W)
                out['C2*'].append({'case': c, 'knot': row['knot'], 'kind': row['kind'], 'rate_W120': round(r, 7),
                                   'rule_rate': eq['ratio'], 'agree': abs(r - eq['ratio']) <= 1e-5})
            if base is not None and row['knot'] in loop and row['kind'] in want and row['exact']:
                W = LW.round_weight(sz, e, 120)
                if W is None:
                    continue
                sh, q = div(W, base)
                ok = sh == 0 and all(abs(q[k] - want[row['kind']][k]) < 1e-9 for k in range(10))
                out['I2*']['n'] += 1
                out['I2*']['agree'] += ok
                if not ok:
                    out['I2*']['differ'].append([c, row['knot'], row['kind'], [round(v, 3) for v in q[:6]]])
    for c in sorted(R):
        if c.startswith('R-') and R[c].get('status') == 'ok' and R[c]['result']['spare'] and R[c]['result']['n'] % 2 == 0:
            x = R[c]['result']
            n = x['n']
            # the loop holding the spare: the even knots of the ring (knot 0 has the spare)
            out['R1*'].append({'n': n, 'rule_rate': x['equation'].get('ratio'),
                               'predicted': round(1 / LW.root([0] * (n // 2) + [1, 1]), 6)})
    Path(sys.argv[2]).write_text(json.dumps(out, indent=1))
    print(json.dumps({'C2*': [(d['kind'], d['agree']) for d in out['C2*']], 'I2*': {k: v for k, v in out['I2*'].items() if k != 'differ'},
                      'I2*differ': out['I2*']['differ'][:6], 'R1*': out['R1*']}))


if __name__ == '__main__':
    main()
