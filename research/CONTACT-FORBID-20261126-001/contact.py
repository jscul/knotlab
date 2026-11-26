"""contact.py: the contact cases left open by the forbidding study's referee (README.md). The placements of the forbidding study where
forbidding answers every reader's own setting through a birth of two readers (the contact addendum, `--shared`), and the
two sampled starts where one reader's edit changes the inputs of the other's own birth (the referee's seven-knot start
1007, readers (3,6) and (2,0), and six-knot start 699, readers (5,0) and (3,2), addressed edits). For each, under U and S:
how far each reader's complete record moves with the far setting (largest total variation over its own setting), whether
the move is in the shape of its births (which births it has, their parents, inputs and fresh counts: a change it can read
off its structure) or only in values, and the largest CHSH (Mermin win) over the readings of the forbidding study.

    contact.py      a JSON line per placement and weighting"""
import sys, json, gzip, glob, itertools
from fractions import Fraction
from pathlib import Path
HERE = Path(__file__).resolve().parent
FE = HERE.parent / 'FORBID-EDITS-20261126-001'
sys.path.insert(0, str(FE))
sys.argv.append('--shared')                       # forbid.SHARED: read placements with a birth of two readers
import forbid


def placements():
    out = []
    for f in sorted(glob.glob(str(FE / 'shared_*.jsonl.gz'))):
        for l in gzip.open(f, 'rt'):
            r = json.loads(l)
            if r['kind'] == 'shared birth, read' and 'U' in r and all(r['forbidding changes with own setting']):
                out.append(('census', r['start'], r['kind of edit'], r['law'], r['arm'], [tuple(x) for x in r['readers']]))
    ext = forbid.extension()
    for idx, readers in ((1007, [(3, 6), (2, 0)]), (699, [(5, 0), (3, 2)])):
        for law in forbid.LAWS:
            for arm in forbid.ARMS:
                out.append(('extension', idx, 'E2', law, arm, readers))
    return out


def tv(p, q):
    keys = set(p) | set(q)
    return sum(abs(p.get(k, 0) - q.get(k, 0)) for k in keys) / 2


if __name__ == '__main__':
    S5, SX = forbid.census(), None
    for src, idx, kind, law, arm, readers in placements():
        if src == 'census': base = forbid.supports_of(S5[idx])
        else:
            SX = SX or forbid.extension(); base = forbid.supports_of(SX[idx])
        p = forbid.placement(base, tuple(readers), kind, law, arm, True)
        T = p['tables']; k = len(readers); width = next(iter(T.values()))['width']
        row = {'source': src, 'start': idx, 'kind of edit': kind, 'law': law, 'arm': arm, 'readers': readers, 'kind': p['kind'],
               'status': {''.join(map(str, s)): t['status'] for s, t in T.items()}}
        for w in ('U', 'S'):
            moves = []
            for i in range(k):
                best, shape = Fraction(0), False
                for own in (0, 1):
                    sts = [s for s in T if s[i] == own]
                    for a, b in itertools.combinations(sts, 2):
                        (sa, da), (sb, db) = T[a]['records'][w][i], T[b]['records'][w][i]
                        if sa != sb: shape = True; best = max(best, Fraction(1))
                        else: best = max(best, tv(da, db))
                moves.append({'largest total variation': str(best), 'in the shape of its births': shape})
            if k == 2:
                score = forbid.chsh(T, w, 0, 1, width)[0]                   # the fixed old value
                if kind == 'E2': score = max(score, forbid.chsh(T, w, 2, 3, width)[0])      # and the added value
            else:
                score = forbid.mermin(T, w, width, (0, 1, 2))
            row[w] = {'record moves': moves, 'score': str(score), 'single unchanged': forbid.checks(T, k, w, width)[0]}
        print(json.dumps(row), flush=True)
