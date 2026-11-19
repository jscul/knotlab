"""PARENT-RULE-20261119-001B, exploratory (after S1a and S1b failed; not a frozen prediction).  An arrangement is self-grown when
one complete round of the census's law (cheapest counts, elimination over GF(2)) applied to its peel gives it back, up to
isomorphism.  Every open reached stage of round >= 1 is self-grown (the round depends only on the arrangement before it).  For
every other-states pair of part S, are both sides self-grown?  Run: .venv/bin/python -B self_grown.py -> self_grown.json."""
import json
import sys
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import census_job as C  # noqa: E402  (the census's law: S, F)
import plib as L  # noqa: E402
import static_pairs as SP  # noqa: E402
DEST = ROOT / 'artifacts/PARENT-RULE-20261119-001B/PARENT-RULE-20261119-001B-E001_parent'


def self_grown(stars):
    if not L.live_set(stars):
        return False
    base = L.peel(stars)
    if not base:
        return False
    P = C.S.from_junctions([sorted(s) for s in base])
    res = P.step(C.S.gf2(C.F.fewest), None)
    if res is None or res.get('new', 0) == 0:
        return False
    grown = [frozenset(b) for b in P.bits_of]
    return len(grown) == len(stars) and L.arrangement_iso(grown, stars)


def group_check(g):
    # rebuild the whole table group from the rows of its key, so that no member is lost to the listing's cap
    ms = g['members']
    flags = [(m['state_group'], self_grown([frozenset(s) for s in m['stars']]), m['row']['depth']) for m in ms]
    c = Counter()
    for i in range(len(flags)):
        for j in range(i + 1, len(flags)):
            if flags[i][0] != flags[j][0]:
                c['pairs_listed'] += 1
                c['both_self_grown'] += flags[i][1] and flags[j][1]
                c['one_self_grown'] += flags[i][1] != flags[j][1]
    c['members_listed'] += len(ms)
    c['members_self_grown'] += sum(f[1] for f in flags)
    c['groups_truncated'] += g['size'] > len(ms)
    return dict(c)


def main():
    d = json.loads((DEST / 'static_pairs.json').read_text())
    with Pool(8) as pool:
        rs = pool.map(group_check, d['other_states_groups'], chunksize=4)
    tot = Counter()
    for r in rs:
        tot.update(r)
    out = {'summary': dict(tot)}
    (DEST / 'self_grown.json').write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
