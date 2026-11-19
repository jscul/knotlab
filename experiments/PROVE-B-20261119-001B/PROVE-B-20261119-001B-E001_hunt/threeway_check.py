"""PROVE-B-20261119-001B, after the read-out (exploratory): do reading-keeping, equation-breaking table symmetries ever keep the
three-way readings too?  Both known counterexamples (Proposition X, Codex's construct_6) break them.  On a sample of part B's
starts (every 25th start of every case), every such symmetry of every open stage of round >= 1 is tested for keeping all
three-way readings (smallest bond holding three distinctions, less one, or none; from every bond).
Run: .venv/bin/python -B threeway_check.py -> threeway_check.json beside the artifacts."""
import json
import sys
from collections import Counter
from itertools import combinations
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import reached_job as RJ  # noqa: E402
EX, L = RJ.EX, RJ.L
EVERY = 25


def three(stars):
    p3 = {}
    for b in L.bonds(stars):
        k = len(b) - 1
        for t in combinations(sorted(b), 3):
            if p3.get(t, 10 ** 9) > k:
                p3[t] = k
    return p3


def stage_check(a, c):
    ta, la = L.table(a)
    idx = {x: i for i, x in enumerate(la)}
    wa = [sum(1 << idx[x] for x in s) for s in a]
    ra = L.rank(wa)
    R = EX.reading(a)
    t3 = None
    for phi in RJ.coset_reps(a, ta, la):
        if phi == 'cap':
            c['capped'] += 1
            break
        mapped = [sum(1 << idx[phi[x]] for x in s) for s in a]
        if L.rank(wa + mapped) == ra:
            continue
        if EX.keeps_reading(phi, a, a, R, R) is None:
            continue
        if t3 is None:
            t3 = three(a)
        keeps3 = all(t3.get(tuple(sorted(phi[x] for x in t)), 'none') == v for t, v in t3.items()) and \
            len({tuple(sorted(phi[x] for x in t)) for t in t3}) == len(t3)
        c['reading_keeping_not_equations'] += 1
        c['of_which_keep_three_way'] += keeps3


def one(cp):
    cid, p = cp
    g = RJ.graphs()[p['graph']]
    c = Counter()
    for j, (stars, mult, ell) in enumerate(RJ.starts(g, p['first'])):
        if j % RJ.SPLIT != p['part'] or (j // RJ.SPLIT) % EVERY:
            continue
        c['starts'] += 1
        P = EX.C.S.from_junctions([sorted(s) for s in stars])
        for r in range(1, RJ.ROUNDS + 1):
            res = P.step(EX.C.S.gf2(EX.C.F.fewest), None)
            if res is None or res['new'] == 0:
                break
            cur = [frozenset(b) for b in P.bits_of]
            if len(cur) > RJ.FULL or not L.live_set(cur):
                break
            c['stages'] += 1
            stage_check(cur, c)
    return dict(c)


def main():
    with Pool(4) as pool:
        rs = pool.map(one, list(RJ.cases()), chunksize=4)
    s = Counter()
    for r in rs:
        s.update(r)
    dest = ROOT / 'artifacts/PROVE-B-20261119-001B/PROVE-B-20261119-001B-E001_hunt'
    (dest / 'threeway_check.json').write_text(json.dumps(dict(sorted(s.items())), indent=1))
    print(json.dumps(dict(sorted(s.items())), indent=1))


if __name__ == '__main__':
    main()
