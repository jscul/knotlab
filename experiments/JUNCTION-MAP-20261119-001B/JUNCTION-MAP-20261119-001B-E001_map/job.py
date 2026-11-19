"""Shared-runner job for JUNCTION-MAP-20261119-001B-E001: the junction map against growth.

Population: BREAK-EDDIES' rational starts other than the 36 with W = y^2 (1 + y) used in the pilot (their counts from
runs/break-eddies), the referee's two six-knot eddies (runs/break-eddies-ref), the five catalogue entries, rings of 9 to 13 knots
with one spare, and two controls (two touching three-place knots, a chain of three); the last three groups grown here to 12 rounds.
For s = 1, 2, 3: G (gate) the stage presentation grown 8 rounds equals the continued growth; the stage's status (inside the rule's
scope and free of known breaks, or holding the overlap); J1/J2 the junction map (maplib.lifted_series) against the growth from
round s + 1; and once per start J3 the knot-level cut-lifted map against the growth."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import maplib as M  # noqa: E402
SL = M.SL
E = SL.E
J = E.J
sys.path.insert(0, str(M.ROOT / 'scripts'))
from longrun import load_results  # noqa: E402


def first_diff(p, c):
    if not isinstance(p, list):
        return str(p)
    n = min(len(p), len(c))
    return next((k for k in range(n) if p[k] != c[k]), None), n


def study(sz, e, counts):
    out = {'sizes': sz, 'edges': [list(x) for x in e], 'counts': counts[:20]}
    out['J3'] = first_diff(M.lifted(sz, e, min(len(counts), 12)), counts)
    rows = []
    for s in (1, 2, 3):
        st, _ = SL.stage(sz, e, s)
        if st is None or len(counts) < s + 3:
            break
        g = J.grow(st[0], st[1], rounds=8, maxj=60000)['counts']
        n = min(len(g) - 1, len(counts) - s - 1, 8)
        gate = g[1:1 + n] == counts[s + 1:s + 1 + n]
        A = E.analyse_all(st[0], st[1])
        status = 'stall' if A.get('stall') else ('clean' if A['scope'] and E.exact(A) else 'overlap' if not A['scope'] else 'break')
        p = M.lifted_series(sz, e, s, min(8, len(counts) - s - 1))
        rows.append({'s': s, 'gate': gate, 'gate_rounds': n, 'status': status, 'map': first_diff(p, counts[s + 1:])})
    out['stages'] = rows
    return out


def cases():
    R = load_results(str(M.ROOT / 'runs/break-eddies'))
    k = 0
    for c, r in sorted(R.items()):
        if r.get('status') != 'ok':
            continue
        x = r['result']
        rec = x['recurrence']
        if not rec or 'W' not in rec or tuple(rec['W']) == (0, 0, 1, 1):
            continue
        yield f'B-{k:03d}', {'start': x['start'], 'counts': x['counts']}
        k += 1
    F = load_results(str(M.ROOT / 'runs/break-eddies-ref'))
    for c, r in sorted(F.items()):
        x = r['result']
        if x.get('recurrence') and x['recurrence'].get('W'):
            yield f'F-{c[2:]}', {'start': x['start'], 'counts': x['counts']}
    cat = json.loads((M.ROOT / 'experiments/LOOP-CATALOGUE-20261119-001B/LOOP-CATALOGUE-20261119-001B-E001_catalogue/catalogue.json').read_text())
    for i, ent in enumerate(cat):
        yield f'C-{i}', {'start': {'sizes': ent['sizes'], 'edges': ent['edges']}, 'grow': True}
    for n in range(9, 14):
        edges = [sorted((i, (i + 1) % n)) for i in range(n)]
        sz = J.bare_sizes(n, [tuple(x) for x in edges])
        sz[0] += 1
        yield f'R-{n}', {'start': {'sizes': sz, 'edges': edges}, 'grow': True}
    yield 'K-pair', {'start': {'sizes': [3, 3], 'edges': [[0, 1]]}, 'grow': True}
    yield 'K-chain', {'start': {'sizes': [3, 3, 3], 'edges': [[0, 1], [1, 2]]}, 'grow': True}


def run(case_id, payload):
    st = payload['start']
    sz, e = st['sizes'], [tuple(x) for x in st['edges']]
    counts = payload.get('counts') or J.grow(sz, e, rounds=12, maxj=60000)['counts']
    return study(sz, e, counts)
