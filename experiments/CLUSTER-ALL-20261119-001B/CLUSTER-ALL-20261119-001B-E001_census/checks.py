"""Gate checks for CLUSTER-ALL-20261119-001B.  python3 -B checks.py > checks_output.json

G1  the pilot replays: every census arrangement of up to four knots, regrown 20 rounds, equals the rule where it is in scope
    (1,901), and 38 are out of scope.
G2  hand cases: a lone knot closes in its 2^a pattern; two touching knots of three places give 2(t + 1); of four places, the
    relay; the ring of five four-place knots, five a round; of five five-place knots, 5 F(t + 2).
G3  a mutant without the relay misses two touching four-place knots; a mutant whose open = 2 offshoots are leaves misses two
    touching three-place knots.
G4  on RING-PAIR-20261119-001's 17 fresh starts the rule equals that study's cover model for 12 rounds."""
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import clusters as Cl  # noqa: E402
import importlib.util  # noqa: E402
_spec = importlib.util.spec_from_file_location('cluster_all_job', HERE / 'job.py')   # not JOIN-GROWTH's job.py on the path
job = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(job)
J = Cl.J


def main():
    out = {}
    keys = sorted(k for k in job.arrlib.arrangements(4))
    tally = Counter(job.judge(*job.edges_of(k))['verdict'] for k in keys)
    out['G1'] = dict(tally)
    hand = {'lone3': (([3], []), [1, 3, 3, 1]), 'pair33': (([3, 3], [(0, 1)]), [2 * (t + 1) for t in range(12)]),
            'pair44': (([4, 4], [(0, 1)]), [2, 6, 6, 2, 2, 4, 6, 8, 10, 12, 14, 16]),
            'ring5x4': (([4] * 5, J.ring_edges(5)), [5] * 12)}
    fib = [1, 1]
    for _ in range(20):
        fib.append(fib[-1] + fib[-2])
    hand['ring5x5'] = (([5] * 5, J.ring_edges(5)), [5 * fib[t + 1] for t in range(12)])
    g2 = {}
    for k, ((sz, e), want) in hand.items():
        p = Cl.series(sz, e, 12)
        g2[k] = p[:len(want)] == want
    out['G2'] = g2
    orig = Cl._geom
    s0 = Cl.series([4, 4], [(0, 1)], 12)
    src = open(HERE / 'clusters.py').read()
    ns = {'__file__': str(HERE / 'clusters.py'), '__name__': 'mutant'}
    exec(compile(src.replace('if finite and len(comps) > 1:', 'if False:'), 'mutant1', 'exec'), ns)
    m1 = ns['series']([4, 4], [(0, 1)], 12) != s0
    ns = {'__file__': str(HERE / 'clusters.py'), '__name__': 'mutant'}
    exec(compile(src.replace("kind = 0 if opn[k] >= 3 else (1 if opn[k] == 2 else 2)", "kind = 0 if opn[k] >= 2 else 2"),
                 'mutant2', 'exec'), ns)
    m2 = ns['series']([3, 3], [(0, 1)], 12) != Cl.series([3, 3], [(0, 1)], 12)
    out['G3'] = {'no_relay_differs': m1, 'chain_as_leaf_differs': m2}
    sys.path.insert(0, str(Cl.ROOT / 'experiments/RING-PAIR-20261119-001B/RING-PAIR-20261119-001B-E001_cover'))
    import covermodel as M
    import fresh
    g4 = {}
    for cid, (n, e, sp) in fresh.starts().items():
        sizes = J.bare_sizes(n, e, sp)
        g4[cid] = Cl.series(sizes, e, 12) == M.model_counts(n, e, sp, 12)
    out['G4'] = {'equal': sum(g4.values()), 'of': len(g4)}
    out['pass'] = (tally.get('match') == 1901 and tally.get('out of scope') == 38 and not tally.get('miss') and all(g2.values())
                   and m1 and m2 and out['G4']['equal'] == out['G4']['of'])
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
