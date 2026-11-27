"""census_boxes.py OUT.jsonl --rounds R --holders M [--full-upto F] [--sample K --seed S --exclude-seed S2
--exclude-count K2] [--chunk I/N] [--box-limit B]: boxes (boxes.py) on census starts and their grown stages.
UPPER-GROWN-20261127-001.

For each chosen census start, at rounds 0..R (as far as ordinary not-all-equal growth is funded): the bonds of the full
search on stages of at most F distinctions, and otherwise those held by a connected set of at most M knots
(RING-BOND's local search, checked on the whole stage), the boxes they form (at most B
read per stage), and for each box read: its upper missing words, the laws they need, whether a birth is needed, and
whether it reads a born distinction."""
import sys, json, random, time, collections
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import boxes as BX
RB = BX.RB


def stage_record(sup, n_start, m, blim, full_upto):
    n = len({x for r in sup for x in r})
    if n <= full_upto:                                      # the full search (holders of any shape) where it fits
        good = RB.bonds(RB.Stage(sup, 'nae'), 'agree')['bonds']; how = 'full'
    else:
        L = RB.local_bonds(sup, 'nae', m); how = 'local'
        good = [b for b in L if b['same relation on the stage'] and not b['read at a knot of the stage']]
    bx = BX.find_boxes(good)
    recs = [BX.read_box(sup, x, n_start) for x in bx[:blim]]
    return {'distinctions': n, 'knots': len(sup), 'search': how, 'bonds': len(good), 'boxes': len(bx),
            'boxes read': len(recs),
            'upper missing exactly one': sum(1 for r in recs if len(r['upper missing']) == 1),
            'a birth needed': sum(1 for r in recs if r.get('a birth needed')),
            'reads a born distinction': sum(1 for r in recs if r['reads a born distinction']),
            'examples': [r for r in recs if r.get('a birth needed')][:2] or recs[:1]}


if __name__ == '__main__':
    out = sys.argv[1]; args = sys.argv[2:]
    get = lambda k, d: type(d)(args[args.index(k) + 1]) if k in args else d
    R, m, K, seed, blim = get('--rounds', 2), get('--holders', 4), get('--sample', 0), get('--seed', 20261128), get('--box-limit', 200)
    full_upto = get('--full-upto', 19)
    starts = RB.forbid.census(); order = list(range(len(starts)))
    if '--exclude-seed' in args:
        ex = set(random.Random(get('--exclude-seed', 1)).sample(order, get('--exclude-count', 10))); order = [i for i in order if i not in ex]
    if K: order = sorted(random.Random(seed).sample(order, K))
    if '--chunk' in args:
        ci, cn = map(int, args[args.index('--chunk') + 1].split('/')); order = order[ci::cn]
    with open(out, 'w') as f:
        for i in order:
            t0 = time.time(); S = RB.forbid.supports_of(starts[i]); rec = {'start': 'census %d' % i, 'rounds': []}
            for t, (sup, born) in enumerate(RB.stages(S, 'nae', R)):
                rec['rounds'].append(dict(round=t, **stage_record(sup, len(S), m, blim, full_upto)))
            rec['seconds'] = round(time.time() - t0, 2)
            f.write(json.dumps(rec) + '\n'); f.flush()
