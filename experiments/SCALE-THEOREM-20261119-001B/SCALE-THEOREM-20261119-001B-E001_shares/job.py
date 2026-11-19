"""Shared-runner job for SCALE-THEOREM-20261119-001B-E001.

For n in (5, 6, 7, 8, 10, 12, 16, 20) and chains 0-7 (SCALE-SHARE's seeds; chains 4-7 from a dense ring), regenerate SCALE-SHARE's
1,000 samples, and record for each: SCALE-SHARE's recorded cluster-rule class (from runs/scale-share, for the integrity check), the
cluster-rule class recomputed here, the theorem class and predicted growth class (scalelib), the dimension-two mechanism, the
out-of-class reason, and the weight |Aut| / n!.  On chain 0, the first 60 samples in the class are regrown: the growth's per-round
multiset of (parents, fresh) to round 6 against the relayed extended cover's (DOUBLE-IDENT's model)."""
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import scalelib as L  # noqa: E402
sys.path.insert(0, str(L.ROOT / 'scripts'))
from longrun import load_results  # noqa: E402

SIZES = (5, 6, 7, 8, 10, 12, 16, 20)
REGROW = 60


def cases():
    for n in SIZES:
        for seed in range(8):
            yield f'S-n{n:02d}-c{seed}', {'n': n, 'seed': seed, 'samples': 1000}


def run(case_id, payload):
    n, seed = payload['n'], payload['seed']
    R = load_results(str(L.ROOT / 'runs/scale-share'))
    recorded = [s['class'] for s in R[case_id]['result']['samples']]
    samp = L.SC.chain(n, payload['samples'], seed, dense=seed >= 4)
    out, regrown = [], 0
    for i, (sizes, M) in enumerate(samp):
        sz, e = L.SC.edges_of(sizes, M)
        c, D = L.theorem_class(sizes, M)
        rec = {'recorded': recorded[i], 'cluster_rule': L.SC.classify(sizes, M), 'theorem': c,
               'weight': L.SC.automorphisms(sizes, M) / math.factorial(n)}
        if c == 'in':
            Dv, why = L.DM.predict(sz, e)
            rec['predicted'] = L.label(D)
            rec['why'] = why
            if seed == 0 and regrown < REGROW and D != 0:
                a, b = L.DC.growth(sz, e), L.DC.model(sz, e)
                rec['regrown_agree'] = all(a.get(t, {}) == b.get(t, {}) for t in range(L.DC.T + 1) if t in a or t in b)
                regrown += 1
        elif c == 'out':
            nn, nb, opn, live, groups, d = L.DC.data(sz, e)
            rec['why'] = 'S3' if any(len(g) > 2 for g in groups) else 'S4'
        out.append(rec)
    return {'samples': out}
