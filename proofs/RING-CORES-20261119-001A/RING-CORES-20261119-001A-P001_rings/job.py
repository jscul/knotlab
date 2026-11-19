"""Shared-runner job for RING-CORES-20261119-001A-P001's machine check.

Cases:
- ring-L-c: chunk c of the decorated rings of L knots (L = 5, 7..14). Each word gets:
  - K1: the start's class, its largest knot, and whether every knot is live with the forced open counts;
  - K2: dims.predict's reading;
  - K3: the engine's per-round counts (joinlib.grow, to round 40 or 4,000 junctions), compared with the formula;
  - K4: the closed form compared with the direct interval sum to round 40.
- classify-n: K6, every simple start of n knots (2..9) on the cap study's graphs. Exponential in the class iff the core is a ring
  with a leaf or a spare."""
import importlib.util
import itertools
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import ringlib as R  # noqa: E402

_s = importlib.util.spec_from_file_location('cc_mc', ROOT / 'proofs/CAP-CHAINS-20261119-001A/CAP-CHAINS-20261119-001A-P001_caps/machine_check.py')
CC = importlib.util.module_from_spec(_s)
sys.modules['cc_mc'] = CC
_s.loader.exec_module(CC)
DC, DM, SL, J = CC.DC, CC.DM, CC.SL, CC.J
CHUNK = 600


def cases():
    for L in (5, 7, 8, 9, 10, 11, 12, 13, 14):
        m = sum(1 for _ in R.words(L))
        for c in range((m + CHUNK - 1) // CHUNK):
            yield f'ring-{L:02d}-{c:03d}', {'kind': 'ring', 'L': L, 'chunk': c}
    for n in range(2, 10):
        yield f'classify-{n:02d}', {'kind': 'classify', 'n': n}


def forced_ok(word, sizes, e):
    nn, nb, opn, live, groups, d = DC.data(sizes, e)
    L = len(word)
    if len(live) != nn:
        return False
    want = {}
    j = L
    for c in range(L):
        t = word[c][0]
        want[c] = 2 if t == 'L' else (3 if t == 'N' else 2 + word[c][1])
        if t == 'L':
            want[j] = 2 + word[c][1]
            j += 1
    return all(opn[k] == want[k] for k in range(nn)) and all(d[k] == (3 if word[k][0] == 'N' else 2) for k in range(L))


def run_ring(L, chunk):
    ws = list(R.words(L))[chunk * CHUNK:(chunk + 1) * CHUNK]
    out = []
    for w in ws:
        sizes, e = R.start_of(w, J.bare_sizes)
        c = DC.classify(sizes, e)
        D, why = DM.predict(sizes, e)
        f, Ws = R.formula(w)
        dr = R.direct(w, 40)
        g = J.grow(sizes, e, rounds=40, maxj=4000)
        cs = g['counts']
        out.append({'word': [list(x) for x in w], 'class': c, 'max_places': max(sizes), 'forced': forced_ok(w, sizes, e),
                    'bare': R.bare(w), 'reading': SL.label(D), 'rounds': len(cs) - 1, 'engine_equals_formula': cs == f[:len(cs)],
                    'closed_equals_direct': f[:41] == dr, 'rate': max(R.rate(W) for W in Ws),
                    'W': [{i: x for i, x in enumerate(W) if x} for W in Ws], 'counts_head': cs[:12]})
    return out


def run_classify(n):
    levels = CC.enumerate_graphs(5, n)
    tally = Counter()
    bad = []
    for G in levels[n]:
        e = sorted(tuple(sorted(x)) for x in G.edges())
        deg = {k: G.degree(k) for k in G}
        shape = CC.core_shape(G)
        for sizes in itertools.product(*[range(max(3, deg[k] + 1), 6) for k in range(n)]):
            sizes = list(sizes)
            c = DC.classify(sizes, e)
            if c in ('stall', 'out'):
                tally[c] += 1
                continue
            D, why = DM.predict(sizes, e)
            lab = SL.label(D)
            nn, nb, opn, live, groups, d = DC.data(sizes, e)
            decorated = shape == 'cycle' and (n > len([k for k in G if deg[k] >= 2]) or any(opn[k] > d[k] for k in G))
            tally[(c, shape, 'decorated' if decorated else 'bare', lab)] += 1
            if c == 'in' and ((lab == 'exponential') != decorated):
                bad.append([sizes, e, lab])
    return {'tally': {' | '.join(map(str, k)) if isinstance(k, tuple) else k: v for k, v in sorted(tally.items(), key=str)}, 'bad': bad[:20]}


def run(case_id, payload):
    if payload['kind'] == 'ring':
        return {'words': run_ring(payload['L'], payload['chunk'])}
    return run_classify(payload['n'])
