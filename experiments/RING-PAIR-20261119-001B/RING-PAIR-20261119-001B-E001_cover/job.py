"""Shared-runner job for RING-PAIR-20261119-001B-E001: the cover model against the growth of fresh joins.

Cases: fresh.starts() (in the model's scope; P1) and fresh.outside() (outside it; grown for the record, no prediction).  Each is
grown under the fewest counts (joinlib.grow) to 80 rounds, 250,000 junctions or 900 seconds, and the model's counts are computed
for the same rounds."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import covermodel as M  # noqa: E402
import fresh  # noqa: E402

J = M.J
ROUNDS, MAXJ, TMAX = 80, 250000, 900.0


def cases():
    for cid, (n, e, sp) in list(fresh.starts().items()) + list(fresh.outside().items()):
        yield cid, {'n': n, 'edges': [list(x) for x in e], 'surplus': sp, 'predicted': cid.startswith('F')}


def run(case_id, payload):
    n, e, sp = payload['n'], [tuple(x) for x in payload['edges']], payload['surplus']
    ok, why = M.in_scope(n, e, sp)
    sizes = J.bare_sizes(n, e, sp)
    g = J.grow(sizes, e, rounds=ROUNDS, maxj=MAXJ, tmax=TMAX)
    res = dict(g, sizes=sizes, in_scope=ok, why=why)
    if ok:
        c = M.model_counts(n, e, sp, len(g['counts']))
        res['model'] = c
        res['equal'] = c[:len(g['counts'])] == g['counts']
        res['first_difference'] = next((t for t, (a, b) in enumerate(zip(c, g['counts'])) if a != b), None)
    return res
