"""Gate checks for RING-PAIR-20261119-001B.  python3 -B checks.py > checks_output.json

G1  the model's counts equal the grown counts of the bare 5-5 join (16 rounds, JOIN-GROWTH's pilot) and of every census start of
    JOIN-GROWTH-20261118-001B in the model's scope, every round grown (36 starts); every census start outside the scope differs.
G2  a brute-force count of connected sets on the cover (walk normal forms, pilot/animals.py) equals the block series on three
    starts, to size 9.
G3  a mutant model with every block cut into its pairs (no simplices) disagrees with the growth of the 5-5 join.
G4  (the advisor's identity) on starts without surplus points, the rooted series' coefficient of y^(t+1) is (t + 1) c(t): the
    dissymmetry count and the rooted count agree, to round 20."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / 'pilot'))
import covermodel as M  # noqa: E402
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'experiments/JOIN-GROWTH-20261118-001B/JOIN-GROWTH-20261118-001B-E001_joins'))
from longrun import load_results  # noqa: E402
import job as JG  # noqa: E402
J = M.J
PILOT55 = [10, 14, 24, 42, 78, 154, 310, 638, 1346, 2888, 6278, 13822, 30776, 69168, 156748, 357928]


def main():
    out = {}
    e55 = J.ring_edges(5) + J.ring_edges(5, 5) + [(0, 5)]
    recs = {}
    for d in ['runs/join-growth', 'runs/join-growth-mem', 'runs/join-growth-mem2']:
        for k, r in load_results(str(ROOT / d)).items():
            if r.get('status') == 'ok':
                recs[k] = r
    inside = outside_diff = outside = inside_eq = 0
    for cid, p in JG.cases():
        if cid not in recs:
            continue
        e = [tuple(x) for x in p['edges']]
        g = recs[cid]['result']['counts']
        ok, _ = M.in_scope(p['n'], e, p['surplus'])
        eq = M.model_counts(p['n'], e, p['surplus'], len(g))[:len(g)] == g
        if ok:
            inside += 1
            inside_eq += eq
        else:
            outside += 1
            outside_diff += not eq
    out['G1'] = {'pilot_5_5': M.model_counts(10, e55, {}, 16) == PILOT55, 'in_scope': inside, 'in_scope_equal': inside_eq,
                 'outside': outside, 'outside_differ': outside_diff}
    import animals
    import gamma
    agree = []
    for n, e in [(10, e55), (6, J.ring_edges(5) + [(0, 5)]), (11, J.ring_edges(5) + [(0, 5), (5, 6), (6, 7), (7, 8), (8, 9),
                                                                                       (9, 10), (10, 0)])]:
        sz, E, big, tri = gamma.complex_of(n, e)
        brute = [int(x) for x in animals.orbit_counts(n, E, tri, 9)]
        agree.append(brute == M.model_counts(n, e, {}, 9))
    out['G2'] = {'brute_force_agrees': agree}
    nv, B = M.blocks_of(10, e55)
    pairs = sorted({p for b in B for p in __import__('itertools').combinations(b, 2)})
    out['G3'] = {'mutant_differs': M.series(nv, pairs, 12, 10) != PILOT55[:12]}
    g4 = []
    for n, e in [(10, e55), (11, J.ring_edges(5) + [(0, 5), (5, 6), (6, 7), (7, 8), (8, 9), (9, 10), (10, 0)]),
                 (12, J.ring_edges(5) + J.ring_edges(5, 5) + [(0, 10), (10, 11), (11, 5)])]:
        nv, B = M.blocks_of(n, e)
        c, r = M.series(nv, B, 21, n, rooted=True)
        g4.append(all(r[t + 1] == (t + 1) * c[t] for t in range(20)))
    out['G4'] = {'rooted_identity': g4}
    out['pass'] = all(g4) and (out['G1']['pilot_5_5'] and inside_eq == inside == 36 and outside_diff == outside and all(agree)
                   and out['G3']['mutant_differs'])
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
