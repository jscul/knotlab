"""Pilot (fitting): the rule against every census arrangement of up to four knots, regrown 20 rounds or 20,000 junctions."""
import sys, json, time
from multiprocessing import Pool
sys.path.insert(0, '.')
sys.path.insert(0, "..")
import clusters as Cl
J = Cl.J
sys.path.insert(0, str(Cl.ROOT / 'experiments/TOUCH-CENSUS-20261118-001B/TOUCH-CENSUS-20261118-001B-E001_arrangements'))
import arrlib
def edges_of(key):
    sizes, flat = key
    n = len(sizes)
    e = []
    for (i, j), m in zip(__import__('itertools').combinations(range(n), 2), flat):
        e += [(i, j)] * m
    return list(sizes), e
def one(key):
    sizes, e = edges_of(key)
    pred = Cl.series(sizes, e, 21)
    try:
        g = J.grow(sizes, e, rounds=20, maxj=20000, tmax=120)
    except ValueError as ex:
        return {'key': key, 'error': str(ex)}
    c, out = g['counts'], g['outcome']
    if pred is None:
        v = 'out of scope'
    elif pred == 'stall':
        v = 'match' if out == 'stall' else 'MISS'
    else:
        if out == 'stall':
            v = 'MISS'
        else:
            v = 'match' if pred[:len(c)] == c and (out != 'closed' or all(x == 0 for x in pred[len(c):len(c) + 3])) else 'MISS'
    return {'key': key, 'verdict': v, 'outcome': out, 'counts': c[:8], 'pred': pred[:8] if isinstance(pred, list) else pred}
if __name__ == '__main__':
    nmax = int(sys.argv[1]); out = sys.argv[2]
    keys = sorted(k for k in arrlib.arrangements(nmax) if len(k[0]) <= nmax)
    t = time.time()
    with Pool(6) as p:
        res = p.map(one, keys, chunksize=8)
    from collections import Counter
    print(len(res), Counter(r.get('verdict', 'error') for r in res), round(time.time() - t))
    json.dump(res, open(out, 'w'))
    for r in res:
        if r.get('verdict') in ('MISS', None): print(r)
