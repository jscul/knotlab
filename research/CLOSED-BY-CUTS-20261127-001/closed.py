"""closed.py ARM OUT.jsonl [--chunk I/C] [--full-upto F]: stages closed by growth under a rival law, and their boxes.
CLOSED-BY-CUTS-20261127-001; README.md.

For every census start, grow under ARM ('one_fewer', A129, or 'arity_floor', A130) for at most 6 rounds.  A stage is
closed when it holds no loose distinction.  For each start whose growth closes after at least one round: the closed
stage's size, and (when it has at most F distinctions) the full bond search, its boxes (UPPER-GROWN's boxes.py), and
for each box the laws it needs and whether a birth is among them.  Starts already closed, stalled or still funded at
round 6 are counted only."""
import sys, json, time, collections
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'UPPER-GROWN-20261127-001'))
import boxes as BX
RB = BX.RB; F = RB.forbid

if __name__ == '__main__':
    arm, out = sys.argv[1], sys.argv[2]; args = sys.argv[3:]
    full_upto = int(args[args.index('--full-upto') + 1]) if '--full-upto' in args else 20
    starts = F.census(); order = list(range(len(starts)))
    if '--chunk' in args:
        ci, cn = map(int, args[args.index('--chunk') + 1].split('/')); order = order[ci::cn]
    tally = collections.Counter()
    with open(out, 'w') as f:
        for i in order:
            S = F.supports_of(starts[i]); st = S; end = None
            for r in range(1, 7):
                nxt, status, births = F.grown(st, 'nae', arm)
                if status != 'funded': end = (status, r - 1); break
                st = nxt
            if end is None: tally['funded through round 6'] += 1; continue
            loose = sum(1 for v in F.holders(st).values() if len(v) == 1)
            if end[1] == 0 or loose: tally['%s at round %d%s' % (end[0], end[1], '' if loose else ', no loose')] += 1; continue
            t0 = time.time(); n = len({x for k in st for x in k})
            rec = {'start': 'census %d' % i, 'closed after round': end[1], 'status': end[0], 'knots': len(st), 'start knots': len(S),
                   'distinctions': n, 'places': sorted(len(k) for k in st)}
            if n <= full_upto:
                b = RB.bonds(RB.Stage(st, 'nae'), 'agree')['bonds']; bx = BX.find_boxes(b)
                recs = [BX.read_box(st, x, len(S)) for x in bx[:50]]
                rec.update({'bonds': len(b), 'boxes': len(bx), 'a birth needed': sum(1 for x in recs if x.get('a birth needed')),
                            'example': recs[:1]})
            else: rec['not searched'] = 'more than %d distinctions' % full_upto
            rec['seconds'] = round(time.time() - t0, 1); tally['closed by growth'] += 1
            f.write(json.dumps(rec) + '\n'); f.flush()
        f.write(json.dumps({'tally': dict(tally)}) + '\n')
