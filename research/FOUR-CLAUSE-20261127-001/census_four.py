"""census_four.py OUT.jsonl [--sample K --seed S] [--chunk I/C] [--full-upto F] [--pattern-limit P]: the four-clause
step on census starts and their grown stages.  FOUR-CLAUSE-20261127-001; README.md.

The sample is drawn with a seeded generator from the census starts outside UPPER-GROWN-20261127-001's sample (seed
20261128, 1,000 starts) and its ten pilot starts, and outside census start 420.  For each start, at rounds 0 to 2 (as far as
ordinary growth is funded) and on stages of at most F distinctions: the full bond search, the four-clause patterns (at most
P read per stage), and for each pattern's three upper relations their words, freeness, reading by one lower bond, and
the laws needed.  Larger stages are recorded as not read."""
import sys, json, random, time, collections
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / 'UPPER-GROWN-20261127-001'))
import fourclause as FC, boxes as BX
RB = BX.RB

if __name__ == '__main__':
    out = sys.argv[1]; args = sys.argv[2:]
    get = lambda k, d: type(d)(args[args.index(k) + 1]) if k in args else d
    K, seed, full_upto, plim = get('--sample', 400), get('--seed', 20261130), get('--full-upto', 19), get('--pattern-limit', 60)
    starts = RB.forbid.census(); allidx = list(range(len(starts)))
    used = set(random.Random(20261128).sample([i for i in allidx if i not in set(random.Random(1).sample(allidx, 10))], 1000))
    used |= set(random.Random(1).sample(allidx, 10)) | {420}
    pool = [i for i in allidx if i not in used]
    order = sorted(random.Random(seed).sample(pool, K))
    if '--chunk' in args:
        ci, cn = map(int, args[args.index('--chunk') + 1].split('/')); order = order[ci::cn]
    with open(out, 'w') as f:
        for i in order:
            t0 = time.time(); S = RB.forbid.supports_of(starts[i]); rec = {'start': 'census %d' % i, 'rounds': []}
            for t, (sup, born) in enumerate(RB.stages(S, 'nae', 2)):
                n = len({x for k in sup for x in k}); row = {'round': t, 'distinctions': n, 'knots': len(sup)}
                if n > full_upto: row['not read'] = True; rec['rounds'].append(row); continue
                st = RB.Stage(sup, 'nae'); b = RB.bonds(st, 'agree', born=born)['bonds']; P = FC.find_patterns(b)
                rel = [r for p in P[:plim] for r in FC.read_pattern(st, p, len(S))]
                row.update({'bonds': len(b), 'patterns': len(P), 'relations read': len(rel),
                            'seven upper words': sum(1 for r in rel if len(r['upper words']) == 7),
                            'proper and pairs free and not read at one lower bond': sum(1 for r in rel if len(r['upper words']) < 8 and r['pairs free'] and not r['an upper reading read at one lower bond']),
                            'a birth needed': sum(1 for r in rel if r.get('a birth needed')),
                            'a birth needed, proper, free, not read at one lower bond': sum(1 for r in rel if r.get('a birth needed') and len(r['upper words']) < 8 and r['pairs free'] and not r['an upper reading read at one lower bond'])})
                rec['rounds'].append(row)
            rec['seconds'] = round(time.time() - t0, 1); f.write(json.dumps(rec) + '\n'); f.flush()
