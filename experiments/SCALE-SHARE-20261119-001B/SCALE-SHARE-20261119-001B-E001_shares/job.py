"""Shared-runner job for SCALE-SHARE-20261119-001B-E001.

Part S: for n in (5, 6, 7, 8, 10, 12, 16, 20), eight Metropolis chains of 1,000 samples each (scale.chain, seeds 0-7), every
sample classified by the cluster rule (scale.classify) with its weight |Aut| / n! (scale.automorphisms).
Chains 0-3 start from a path, chains 4-7 from a dense ring (the advisor's dispersed starts).  Each sample also records rule-free
features (shared distinctions, cycle rank, open places per knot, over-demanded knots).
Part G: for n in (6, 7, 8, 10, 12), the first 200 samples of chain 8 that do not stall, grown under the fewest counts to 15 rounds
(or 20,000 junctions) and compared with the rule's counts, round by round."""
import importlib.util
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import scale as S  # noqa: E402
J = S.J
SIZES = (5, 6, 7, 8, 10, 12, 16, 20)


def cases():
    for n in SIZES:
        for seed in range(8):
            yield f'S-n{n:02d}-c{seed}', {'part': 'S', 'n': n, 'seed': seed, 'samples': 1000}
    for n in (6, 7, 8, 10, 12):
        yield f'G-n{n:02d}', {'part': 'G', 'n': n, 'seed': 8, 'samples': 200}


def run(case_id, payload):
    n = payload['n']
    if payload['part'] == 'S':
        samp = S.chain(n, payload['samples'], payload['seed'], dense=payload['seed'] >= 4)
    else:
        samp, k = [], 0
        while len(samp) < payload['samples']:
            batch = S.chain(n, 200, payload['seed'] * 1000 + k)
            k += 1
            samp += [x for x in batch if S.classify(*x) != 'stall']
        samp = samp[:payload['samples']]
    out = []
    for sizes, M in samp:
        rec = {'class': S.classify(sizes, M), 'weight': S.automorphisms(sizes, M) / math.factorial(n), **S.features(sizes, M)}
        if payload['part'] == 'G':
            sz, e = S.edges_of(sizes, M)
            pred = S.Cl.series(sz, e, 16)
            g = J.grow(sz, e, rounds=15, maxj=20000, tmax=120)
            c = g['counts']
            if pred is None:
                rec['grown'] = 'out of scope'
            elif pred == 'stall':
                rec['grown'] = 'equal' if g['outcome'] == 'stall' else 'differs'
            else:
                rec['grown'] = 'equal' if (g['outcome'] != 'stall' and pred[:len(c)] == c and
                                           (g['outcome'] != 'closed' or not any(pred[len(c):]))) else 'differs'
            rec['outcome'] = g['outcome']
        out.append(rec)
    return {'samples': out}
