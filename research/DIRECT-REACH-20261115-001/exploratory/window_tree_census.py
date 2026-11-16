"""Every-depth reach for the population-D descriptions whose orbits stay bounded (window_tree.py), tops k = 2 and 3.
DIRECT-REACH-20261115-001, exploratory, the thread's own code. Writes window_tree_census.json."""
import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from window_tree import WindowTree, every_depth_pairs  # noqa: E402
from window_types import population_D  # noqa: E402


def verdict(seqs):
    """'tie at every s', 'no tie, two-orbit 3-bond at every s', or the pattern of values."""
    vals = [v for P in seqs.values() for v in P]
    ties = {a for a, b in vals}
    b3 = {b for a, b in vals}
    if ties == {1}:
        return 'tie at every s'
    if ties == {0} and b3 == {1}:
        return 'no tie; two-orbit 3-bond at every s'
    if ties == {0}:
        first = [P for P in seqs.values()]
        return 'no tie; two-orbit 3-bond at s = ' + ','.join(str(i + 1) for i, (a, b) in enumerate(first[-1]) if b and i < 8) + ' (of the first 8)'
    return 'mixed'


if __name__ == '__main__':
    rows, tally = {}, collections.Counter()
    for cid, key, prof, cls in population_D():
        try:
            tree = WindowTree(key)
        except ValueError as e:
            rows[cid] = dict(profile=prof, relative_class=cls, window_tree=str(e))
            tally[(str(prof), 'unbounded orbits')] += 1
            continue
        res = {}
        for k in (2, 3):
            r = every_depth_pairs(tree, k)
            res['k%d' % k] = dict(r, verdict=verdict(r['sequences']))
        rows[cid] = dict(profile=prof, relative_class=cls, types=len(tree.types), orbit_sizes=sorted(set(tree.m)), **res)
        tally[(str(prof), res['k3']['verdict'], res['k2']['verdict'] == res['k3']['verdict'], res['k3']['alive_every_depth'])] += 1
        print(cid[:12], prof, cls, len(tree.types), res['k3']['verdict'], '| k=2:', res['k2']['verdict'], flush=True)
    json.dump(dict(cases=rows, tally={str(k): v for k, v in tally.items()}), open(HERE / 'window_tree_census.json', 'w'), indent=1)
    for k, v in sorted(tally.items(), key=str):
        print(k, v)
