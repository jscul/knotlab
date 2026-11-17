"""Exploratory (KEEP-REACH-20261117-001, after the read-out): the third-class descriptions (never forget on all assignments, alive at
every depth, no two-orbit bond at some s). For each: (1) trimmed forgetting: the least r such that every actual joint of an orbit and
a descendant orbit r levels below, at stable depth, from every level 1..12, is a product (values states actually take); (2) the exact
reach L_9(3, s), s = 1..4, by the census's search (LEVEL-REACH job.compute, 120 s per s)."""
import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'research/DIRECT-REACH-20261115-001/exploratory'))
sys.path.insert(0, str(ROOT / 'experiments/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/codex'))
from window_tree import WindowTree, level_states  # noqa: E402


def rect(J):
    A = {a for a, _ in J}
    B = {b for _, b in J}
    return len(J) == len(A) * len(B)


def trimmed_forget(tree, levels=12, rmax=10):
    F = tree.feasible(20)
    r0 = next(r for r in range(19) if F[r] == F[r + 1])
    Fc = F[r0]
    st = level_states(tree, levels, [Fc] * (levels + 2))
    for r in range(1, rmax + 1):
        ok = True
        for j in range(1, levels + 1):
            for t, up in st[j]:
                frontier = {(t, frozenset((x, x) for x in up))}
                for _ in range(r):
                    frontier = {(tree.children[t2][ci][0], tree.step(t2, Fc, ci, J)) for t2, J in frontier
                                for ci in range(len(tree.children[t2]))}
                for c, J in frontier:
                    Jf = frozenset((a, z) for a, z in J if z in Fc[c])
                    if Jf and not rect(Jf):
                        ok = False
        if ok:
            return r
    return None


def exact_reach(key):
    import job
    job.BUDGET = 120
    wd = tempfile.mkdtemp()
    try:
        r = job.compute(key, wd, N=9, k0=3, S=4, histograms=False)
        return [lv['L_N'] for lv in r['levels']]
    finally:
        shutil.rmtree(wd, ignore_errors=True)


if __name__ == '__main__':
    out = {}
    for f in ('sample_keep.jsonl', 'mutants_keep.jsonl'):
        p = HERE.parent / f
        if not p.exists():
            continue
        for line in open(p):
            r = json.loads(line)
            if r.get('small_orbits') and r.get('alive_every_depth') and r.get('r_all') is None and not r.get('timeout') \
                    and not r['two_orbit_every_s']:
                tree = WindowTree(r['key'])
                tf = trimmed_forget(tree)
                L = exact_reach(r['key'])
                out[str(r['index'])] = dict(key=r['key'], trimmed_r=tf, L9=L, two_orbit_first=r['two_orbit_first'], orbit_sizes=sorted(set(tree.m)),
                                            types=len(tree.types))
                print(r['index'], 'trimmed r', tf, 'L9(3, 1..4)', L, 'orbits', sorted(set(tree.m)), 'types', len(tree.types), flush=True)
    json.dump(out, open(HERE / 'third_class.json', 'w'), indent=1)
