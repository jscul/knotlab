"""Referee R1 (MARK-RATE-20261116-001), item 2: my own families (referee_marks_lib.MyMarks) against marks.py's (marks.Marks on
window_tree.WindowTree, CALLED AS THE THING UNDER TEST), type by type (the two type systems are checked identical first), and my
Theorem M verdict against census_marks.json and against marks.py's no_skip.
Usage: referee_families.py OUT.json per_class max_seconds"""
import gzip
import json
import random
import signal
import sys
import time
from pathlib import Path

ROOT = Path('/home/jscul/p-vs-np-contact-first')
sys.path.insert(0, str(ROOT / 'research/DIRECT-REACH-20261115-001/referee-R1'))
sys.path.insert(0, str(ROOT / 'research/MARK-RATE-20261116-001/referee-R1'))
from referee_marks_lib import MyMarks, to_set  # noqa: E402  (mine)

sys.path.insert(0, str(ROOT / 'research/MARK-RATE-20261116-001'))
sys.path.insert(0, str(ROOT / 'research/DIRECT-REACH-20261115-001/exploratory'))
from marks import Marks  # noqa: E402  (under test)
from window_tree import WindowTree  # noqa: E402  (under test, input of Marks)

CENSUS = ROOT / 'artifacts/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/records_slim.jsonl.gz'


class Timeout(Exception):
    pass


def _alarm(signum, frame):
    raise Timeout()


signal.signal(signal.SIGALRM, _alarm)

if __name__ == '__main__':
    out_path, per, maxsec = sys.argv[1], int(sys.argv[2]), float(sys.argv[3])
    rows = json.load(open(ROOT / 'research/MARK-RATE-20261116-001/census_marks.json'))['rows']
    keys = {}
    for line in gzip.open(CENSUS, 'rt'):
        r = json.loads(line)
        if r['case'] in rows:
            keys[r['case']] = r['key']
    classes = {
        'cyclic r=2 pass (new)': lambda v: v['name'] == 'ruler' and v['cyclic'] and v['r'] == 2 and v['no_skip'] is True,
        'cyclic r=2 fail': lambda v: v['name'] == 'ruler' and v['cyclic'] and v['r'] == 2 and v['no_skip'] is False,
        'cyclic r=3 fail': lambda v: v['name'] == 'ruler' and v['cyclic'] and v['r'] == 3 and v['no_skip'] is False,
        'acyclic r=2 fail': lambda v: v['name'] == 'ruler' and not v['cyclic'] and v['r'] == 2 and v['no_skip'] is False,
        'half-rate fail': lambda v: v['name'] == 'half-rate' and v['no_skip'] is False,
        'ruler r=1 pass': lambda v: v['name'] == 'ruler' and v['r'] == 1 and v['no_skip'] is True,
    }
    rng = random.Random(515)
    pick = []
    for nm, f in classes.items():
        cs = sorted(c for c, v in rows.items() if f(v) and v['seconds'] <= maxsec)
        pick += [(nm, c) for c in rng.sample(cs, min(per, len(cs)))]
    res, diffs = {}, []
    t0 = time.time()
    for nm, cid in pick:
        t1 = time.time()
        signal.alarm(240)
        try:
            mine = MyMarks(keys[cid])
            ok_mine, wit = mine.no_skip()
            t_mine = time.time() - t1
            tree = WindowTree(keys[cid])
            theirs = Marks(tree)
            ok_theirs, _ = theirs.no_skip()
        except Timeout:
            res[cid] = dict(cls=nm, error='over 240 s')
            print(cid[:12], nm, 'over 240 s', flush=True)
            continue
        finally:
            signal.alarm(0)
        enc = lambda T: tuple(tuple((i, tuple(sec)) for i, sec in row) for row in T)
        same_types = [enc(T) for T in tree.types] == [enc(T) for T in mine.B.types] and \
            [[(c, list(pos)) for c, pos in ch] for ch in tree.children] == [[(c, list(pos)) for c, pos in ch] for ch in mine.B.kids]
        cmp = dict(types=len(tree.types), same_types=same_types)
        for fam in ('D', 'U'):
            eq = sub = 0
            for t in range(len(tree.types)):
                a = {to_set(v) for v in getattr(mine, fam)[t]}
                b = set(getattr(theirs, fam)[t])
                eq += a == b
                sub += b <= a
            cmp[fam] = dict(types_equal=eq, theirs_subset_of_mine=sub)
        eqb = sum({to_set(v) for v in mine.below(t)} == set(theirs.below(t)) for t in range(len(tree.types)))
        equf = sum(to_set(mine.Ufree[t]) == set(theirs.Ufree[t]) for t in range(len(tree.types)))
        cmp['below_types_equal'] = eqb
        cmp['Ufree_types_equal'] = equf
        cmp['no_skip'] = dict(mine=ok_mine, marks_py=ok_theirs, census=rows[cid]['no_skip'])
        n = len(tree.types)
        good = same_types and cmp['D']['types_equal'] == n and cmp['U']['types_equal'] == n and eqb == n and equf == n and \
            ok_mine == ok_theirs == rows[cid]['no_skip']
        if not good:
            diffs.append(dict(case=cid, cls=nm, **cmp))
        res[cid] = dict(cls=nm, D_sizes=sum(len(d) for d in mine.D), U_sizes=sum(len(u) for u in mine.U), witness=wit,
                        seconds_mine=round(t_mine, 2), seconds_total=round(time.time() - t1, 2), **cmp)
        print(cid[:12], nm, 'types', n, 'equal' if good else 'DIFF', cmp['no_skip'], '%.1fs' % (time.time() - t1), flush=True)
        json.dump(dict(differences=diffs, cases=res, seconds=time.time() - t0), open(out_path, 'w'), indent=0)
    print('done', len(res), 'differences', len(diffs))
