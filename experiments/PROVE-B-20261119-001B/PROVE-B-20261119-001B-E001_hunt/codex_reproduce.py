"""PROVE-B-20261119-001B, after the read-out: Codex's two reached counterexamples (GROWN-END-SWAP-20261119-001's construct_6,
meeting twice; GROWN-END-MEET-ONCE-20261119-001's seven-junction start, meeting once) reproduced in this program's engine, each
through reached_job.test_stage, with the three-way readings the swap breaks.  Run: .venv/bin/python -B codex_reproduce.py ->
codex_reproduce.json beside the artifacts."""
import json
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import reached_job as J  # noqa: E402
EX, L = J.EX, J.L


def three(stars):
    p3 = {}
    for b in L.bonds(stars):
        for t in combinations(sorted(b), 3):
            if p3.get(t, 10 ** 9) > len(b) - 1:
                p3[t] = len(b) - 1
    return p3


def check(name, stage, swap):
    nxt = EX.grow1(stage)
    phi = {x: x for x in L.owners(stage)}
    phi.update(swap)
    t, lab = L.table(stage)
    R = EX.reading(stage)
    psi = EX.keeps_reading(phi, stage, stage, R, R)
    phi2 = EX.extension(phi, psi, stage, stage, nxt, nxt)
    t2, _ = EX.full_table(nxt)
    bad = [[x, y, t2[(x, y)], t2[tuple(sorted((phi2[x], phi2[y])))]] for (x, y) in t2 if t2[(x, y)] != t2[tuple(sorted((phi2[x], phi2[y])))]]
    p3 = three(stage)
    c, ex = Counter(), []
    J.test_stage(stage, nxt, c, ex, name)
    return {'junctions': len(stage), 'distinctions': len(lab), 'meet_once': L.max_shared(stage) < 2,
            'swap_is_table_isometry': all(t[(x, y)] == t[tuple(sorted((phi[x], phi[y])))] for (x, y) in t),
            'keeps_reading': psi is not None, 'extension_fails_on': bad,
            'three_way_readings_broken': sum(1 for tr, v in p3.items() if p3.get(tuple(sorted(phi[x] for x in tr)), 'none') != v),
            'all_symmetries_of_the_stage': dict(c)}


def main():
    d = json.loads((ROOT / 'artifacts/GROWN-END-SWAP-20261119-001/GROWN-END-SWAP-20261119-001-E001_reached/construct_6.json').read_text())
    twice = [frozenset(s) for s in d['a']['current']]
    once_start = [frozenset(s) for s in [[0, 2, 5, 6, 7], [1, 3, 8, 9], [0, 1, 4], [2, 3, 4], [5, 10, 11], [6, 12, 13], [7, 14, 15]]]
    out = {'GROWN-END-SWAP construct_6 (meeting twice)': check('twice', twice, {0: 2, 2: 0}),
           'GROWN-END-MEET-ONCE seven-junction start, round 1 (meeting once)': check('once', EX.grow1(once_start), {0: 1, 1: 0})}
    dest = ROOT / 'artifacts/PROVE-B-20261119-001B/PROVE-B-20261119-001B-E001_hunt'
    (dest / 'codex_reproduce.json').write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
