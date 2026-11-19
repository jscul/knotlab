"""Score JOIN-GROWTH-20261118-001B-E001.  .venv/bin/python -B merge.py <runner out dir> <results.json> [<rerun out dir>] (numpy for roots)

Reads the runner's latest record per case and scores P1-P10 of research/JOIN-GROWTH-20261118-001/preregistration.md."""
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import job  # noqa: E402
import reclib as R  # noqa: E402

ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from longrun import load_results  # noqa: E402

# starts of family D grown in the pilot before the freeze (pilot/results.json)
SEEN = {'D-D-none-a0-b0', 'D-D-none-a1-b1', 'D-D-none-a2-b1', 'D-D-at-r1-a1-b1', 'D-D-at-r1-a2-b1', 'D-D-at-r-a2-b1',
        'D-D-at-r2-a2-b1', 'D-K-none-b0', 'D-K-none-b1', 'D-K-none-b2', 'D-K-at-r1-b2', 'D-K-at-r-b0', 'D-K-at-r2-b0',
        'D-P1-at-r1-a2-b1'}


def verdict(r, payload):
    p = payload['annihilator']
    if p is None:
        return None
    c = r['counts']
    t0 = r.get('annihilated_from')
    if t0 is not None and t0 <= 12:
        return 'holds'
    d = len(p) - 1
    if len(c) - (12 + d) < 3:          # fewer than three rounds past the order from round 12
        bad = [t for t in range(d, len(c)) if sum(p[k] * c[t - d + k] for k in range(d + 1)) != 0]
        return 'unsettled' if not bad or max(bad) - d > 12 else 'fails'
    return 'fails'


def rate(r, payload):
    v = verdict(r, payload)
    if v == 'holds':
        return r['predicted_rate'], 'predicted'
    m = r.get('minimal')
    if m:
        return max_modulus(m[2]), 'minimal'
    c = r['counts']
    if r['outcome'] in ('closed', 'stall') or len(c) < 7 or c[-1] == 0:
        return (0.0 if r['outcome'] == 'closed' else None), 'none'
    rs = [c[i] / c[i - 1] for i in range(len(c) - 5, len(c))]
    return math.exp(sum(math.log(x) for x in rs) / 5), 'ratios'


def dimension(m, c):
    """For a polynomial growth: the multiplicity of the root 1 of the minimal annihilator (junctions by round ~ t^dim)."""
    if not m:
        return None
    p = m[2]
    k = 0
    while True:
        if sum(p) != 0:
            break
        k += 1
        # divide by (x - 1): synthetic division
        q, acc = [], 0
        for a in reversed(p):
            acc = acc + a
            q.append(acc)
        p = list(reversed(q[:-1]))
        if len(p) <= 1:
            break
    return k


def main():
    out_dir, dest = sys.argv[1], sys.argv[2]
    recs = load_results(out_dir)
    for extra in sys.argv[3:]:          # the memory rerun (amendment of 23:56 UTC): its ok record replaces a main record not ok
        for cid, rec in load_results(extra).items():
            if rec.get('status') == 'ok' and (recs.get(cid) or {}).get('status') != 'ok':
                recs[cid] = rec
    cs = dict(job.cases())
    rows, per = {}, defaultdict(list)
    for cid, pay in cs.items():
        rec = recs.get(cid)
        if rec is None or rec.get('status') != 'ok':
            rows[cid] = {'status': None if rec is None else rec.get('status')}
            per[pay['family']].append((cid, None))
            continue
        r = rec['result']
        v = verdict(r, pay)
        lam, how = rate(r, pay)
        row = {'outcome': r['outcome'], 'rounds': r['rounds'], 'junctions': r['junctions'], 'sizes': r['sizes'],
               'counts': r['counts'], 'minimal': r['minimal'], 'verdict': v, 'rate': lam, 'rate_from': how,
               'annihilated_from': r.get('annihilated_from'), 'predicted_rate': r.get('predicted_rate'), 'seen': cid in SEEN}
        if pay['family'] == 'C' and r['outcome'] not in ('closed', 'stall'):
            lo = 8 if len(r['counts']) > 11 else 4
            row['fit'] = dict(zip(('lambda', 'alpha', 'max_residual'), R.fit_power_exponential(r['counts'], lo)))
        rows[cid] = row
        per[pay['family']].append((cid, row))
    S = {}
    for fam in ('A1', 'A2', 'A3', 'A4', 'A5', 'A6'):
        S[fam] = dict(Counter((row or {}).get('verdict') for _, row in per[fam]))
    dk = [(c, r) for c, r in per['D'] if c.startswith(('D-D-', 'D-K-'))]
    S['P7_all'] = dict(Counter((r or {}).get('verdict') for _, r in dk))
    S['P7_unseen'] = dict(Counter((r or {}).get('verdict') for c, r in dk if c not in SEEN))
    S['P7_fails'] = [c for c, r in dk if (r or {}).get('verdict') != 'holds']
    # P8: faster than the ring alone
    p8 = []
    for fam in ('A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'B', 'D'):
        for cid, r in per[fam]:
            if r is None:
                p8.append((cid, None, None, 'missing'))
                continue
            pay = cs[cid]
            j = sum(int(v) for k, v in pay['surplus'].items() if int(k) < ring_n(cid))
            base = 1.0 if j == 0 else R.dominant_root(R.polyadd([0] * (ring_n(cid) + j) + [1], R.polyneg(R.polypow([1, 1], j))))
            ok = r['rate'] is not None and r['rate'] > base + 0.01
            p8.append((cid, r['rate'], base, 'ok' if ok else 'FAIL'))
    S['P8_failures'] = [x for x in p8 if x[3] != 'ok']
    S['P8_count'] = len(p8)
    # P9: two rings
    C = {c: r for c, r in per['C']}
    lam = {c: (r or {}).get('fit', {}).get('lambda') for c, r in C.items()}
    S['P9'] = {
        'a_no_recurrence': {c: (r or {}).get('minimal') is None for c, r in C.items()},
        'b_lambda_above_1.5': {c: (lam[c] or 0) > 1.5 for c in C},
        'c_order': {'5-7 < 2.51': (lam.get('C-5-7-D') or 9) < 2.51,
                    '7-7 < 5-7': (lam.get('C-7-7-D') or 9) < (lam.get('C-5-7-D') or 0),
                    '5-9 < 5-7': (lam.get('C-5-9-D') or 9) < (lam.get('C-5-7-D') or 0)},
        'd_alpha_in_[-2,-1]': {c: -2 <= ((r or {}).get('fit', {}).get('alpha') or 0) <= -1 for c, r in C.items()},
        'fits': {c: (r or {}).get('fit') for c, r in C.items()}}
    # P10: no ring
    E = {}
    for cid, r in per['E']:
        if r is None:
            E[cid] = None
            continue
        expo = r['rate'] is not None and ((r['rate_from'] in ('minimal', 'predicted') and r['rate'] > 1.001) or
                                          (r['rate_from'] == 'ratios' and r['rate'] > 1.1))
        E[cid] = {'outcome': r['outcome'], 'rate': r['rate'], 'dimension': dimension(r['minimal'], r['counts']),
                  'exponential': expo}
    S['P10'] = E
    S['B'] = {c: {'rate': (r or {}).get('rate'), 'minimal': (r or {}).get('minimal'), 'outcome': (r or {}).get('outcome')}
              for c, r in per['B']}
    Path(dest).write_text(json.dumps({'summary': S, 'cases': rows}, indent=1, default=str))
    print(json.dumps(S, indent=1, default=str))


def max_modulus(p):
    """The largest modulus of a root of the polynomial p (constant term first)."""
    import numpy as np
    q = list(p)
    while len(q) > 1 and q[-1] == 0:
        q.pop()
    if len(q) <= 1:
        return 0.0
    return float(max(abs(z) for z in np.roots(list(reversed(q)))))


def ring_n(cid):
    """Ring length of a single-ring case, read from its id (n5, n7, n9; family D and B use the ring of five unless named)."""
    for tok in cid.split('-'):
        if tok.startswith('n') and tok[1:].isdigit():
            return int(tok[1:])
    return 5


if __name__ == '__main__':
    main()
