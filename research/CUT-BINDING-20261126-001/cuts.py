"""cuts.py SET ARM OUT.jsonl: the binding test of BINDING-20261126-001 under a forbidding cut.  CUT-BINDING-20261126-001
(a check by the thread, not registered); README.md.

ARM is one of the two recorded forbidding cuts of the fresh count (FORBIDDING-JOIN-20261120-001B's rival_growth.cut):
one_fewer (a birth gets one fresh distinction fewer, never below the arity floor) or arity_floor (it gets only what
three places need).  Growth is otherwise the ordinary growth under parity.  On every stage of SET (census: every census
start of three to five knots; heldout: the 900 fresh starts of six to eight knots; witnesses: the layers referee's
starts), rounds 0 to 2 (witnesses 3): B (sums of laws that are allowed changes and empty on the loose distinctions), and
every nonzero element of B split into distinction-disjoint cycles; a binding is a split into three or more cycles each
a class label (even on every shortest change) not read by one knot.  Also read, per stage, whether the old distinctions'
allowed changes are kept (the cut can remove old states)."""
import sys, os, json
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'research' / 'BINDING-20261126-001'))
import judge as JD, binding as BD, split as SP
forbid = BD.forbid
sys.path.insert(0, str(ROOT / 'research' / 'LAYERS-20261126-001'))
import layers as LY


def items(which):
    if which == 'census':
        for i, s in enumerate(forbid.census()): yield 'census %d' % i, forbid.supports_of(s)
    elif which == 'heldout':
        for n in (6, 7, 8):
            for j, s in enumerate(forbid.sampled(n, 300, 20261206 + n)): yield 'held out %d-%d' % (n, j), forbid.supports_of(s)
    else:
        yield from BD.witnesses()


if __name__ == '__main__':
    which, arm, out = sys.argv[1], sys.argv[2], sys.argv[3]
    rounds = 3 if which == 'witnesses' else 2
    with open(out, 'w') as f:
        for name, S in items(which):
            st = S; rec = {'start': name, 'arm': arm, 'rounds': []}
            for t in range(0, rounds + 1):
                if t:
                    nxt, status, births = forbid.grown(st, 'parity', arm)
                    if status != 'funded': rec['rounds'].append({'round': t, 'end': status}); break
                    st = nxt
                if len({x for r in st for x in r}) > 600: rec['rounds'].append({'round': t, 'end': 'not read'}); break
                try:
                    r = JD.judge_all(st) or {'dim B': 0}
                except AssertionError as e:
                    rec['rounds'].append({'round': t, 'end': str(e)}); break
                r['round'] = t
                if t: r['old allowed changes kept'] = LY.projection_kept(S, st)['same']
                rec['rounds'].append(r)
            f.write(json.dumps(rec) + '\n'); f.flush()
