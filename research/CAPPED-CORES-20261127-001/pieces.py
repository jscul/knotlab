"""pieces.py: for the certified starts of runs/KIND_KNOTS.jsonl, redraw them (same weighting, seed and order) and report
whether their capped piece is one late.py counts as a tree or as a cycle, and its cycle rank against blocks and cells."""
import sys, os, json, random, importlib.util, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'GRADED-ORDER-20261126-001'))
import graded
late = graded.late
spec = importlib.util.spec_from_file_location('wl', graded.ROOT + '/experiments/WEIGHTINGS-20261119-001B/WEIGHTINGS-20261119-001B-E001_weights/weightlib.py')
WL = importlib.util.module_from_spec(spec); spec.loader.exec_module(WL)
out = collections.Counter()
for fn in sys.argv[1:]:
    rows = [json.loads(l) for l in open(fn)]; meta = rows[-1]; want = {r['draw']: r for r in rows[:-1]}
    rng = random.Random(meta['seed'])
    for i in range(meta['draws']):
        sizes, edges = graded.sample_start(WL, meta['weighting'], meta['knots'], rng)
        if i in want:
            M = late.Map(graded.stars_of(sizes, edges))
            kinds = ['tree' if t else 'cycle' for _, t, _ in M.pieces]
            out[(meta['weighting'], meta['knots'], want[i]['class'], 'pieces: ' + '+'.join(sorted(kinds)))] += 1
for k, v in sorted(out.items(), key=str): print(v, k)
