"""posthoc.py OUT.json: after the frozen test failed, the revised reading (late.GeneralPiece: parents are all valid
subsets one smaller, fresh distinctions all valid supersets one larger) on every grown set, fitting and held-out.
Post hoc: found on the held-out misses, so it is exploration, not a test."""
import sys, os, json, gzip, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import late, score

SETS = [('fitting, 1 to 4 knots', 'nae', '../LOOK-ALIKE-20261126-001/phase1_grown.jsonl.gz'),
        ('fitting, 5 knots', 'nae', '../SETTLE-BOUND-20261126-001/grown_g5_nae.jsonl.gz'),
        ('fitting, 5 knots', 'parity', '../SETTLE-BOUND-20261126-001/grown_g5_par.jsonl.gz')] + \
       [(S, law, fn) for (S, law), fn in score.GROWN.items()]

if __name__ == '__main__':
    res = collections.Counter(); left = []
    for S, law, fn in SETS:
        for l in late.opener(os.path.join(HERE, fn)):
            x = json.loads(l); st = {}
            P, why = late.predict(x['stars'], 40 if S == 'horizon' else 24, law, static=st, general=True)
            if P is None: res[(S, law, 'not predicted: ' + why)] += 1; continue
            first = score.compare(P, x)
            res[(S, law, st['stratum'], 'agree' if first is None else 'differ')] += 1
            if first is not None: left.append([S, law, x['index'], st['stratum'], first, x['stars']])
    r = {'tally': {' / '.join(k): v for k, v in sorted(res.items())}, 'still differ': left}
    json.dump(r, open(sys.argv[1], 'w'), indent=1)
    print(json.dumps(r['tally'], indent=1)); print('still differ:', len(left)); [print(m) for m in left[:8]]
