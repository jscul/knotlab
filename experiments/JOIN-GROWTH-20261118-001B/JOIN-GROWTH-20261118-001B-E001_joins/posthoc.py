"""Post hoc (after the freeze, not a frozen test): the nested law on the census's paths and chains.
.venv/bin/python -B posthoc.py <runner out dir> <posthoc.json> [<rerun out dirs>]

The candidate relation of the joining rule links knots two apart along a chain hanging from a ring knot r (r, K1, K2, K3, ...): knots
at even removes nest under r, knots at odd removes under K1, which is a candidate of r's ring neighbours.  Nested law: a knot with s
surplus distinctions and candidate children c has F = 1 + y (1 + y)^s prod F(c); an end whose only surplus distinction is the
floor's renews, F = 1/(1 - y).  The ring's menu is the product over r's ring surplus and the top knots of each nest.  On the
two-fold piece (K1 = A, K2 = B) this is the frozen product law; the chains of three and four on rings of 5, 7 and 9
(posthoc/chain_*.json) were grown after the nested law for four was written down (posthoc/prediction_chain4.txt)."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import job  # noqa: E402
import reclib as R  # noqa: E402

ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from longrun import load_results  # noqa: E402

ONE = [1]


def F(s, children=()):
    """(numerator, denominator) of 1 + y (1 + y)^s prod children."""
    N, D = R.polypow([1, 1], s), [1]
    for n_, d_ in children:
        N, D = R.polymul(N, n_), R.polymul(D, d_)
    return R.polyadd(D, [0] + N), D


RENEW = ([1], [1, -1])


def F_one_demand(s, children=()):
    """Refinement found on the census (law 2): a knot with round-1 demand 1 and exactly one surplus distinction renews it
    (its offshoot's only candidate through it is the knot's one group, so the floor gives the offshoot a surplus distinction again):
    F = 1 + y/(1 - y) prod children.  Otherwise as F."""
    if s != 1:
        return F(s, children)
    Nc, Dc = [1], [1]
    for n_, d_ in children:
        Nc, Dc = R.polymul(Nc, n_), R.polymul(Dc, d_)
    D = R.polymul([1, -1], Dc)
    return R.polyadd(D, [0] + Nc), D


def end(b):
    """A chain's last knot: listed b, its floor distinction making s = b + 1; renewing when b = 0."""
    return RENEW if b == 0 else F(b + 1)


def predicted(cid, law=1):
    """Factors of the nested law (law 1, written before the census was read) or its refinement (law 2) for a census path."""
    G = F if law == 1 else F_one_demand
    t = cid.split('-')
    if t[0] == 'D' and t[1] in ('P1', 'P2'):
        ring = t[2] if t[2] == 'none' else t[2] + '-' + t[3]
        a = int(t[-2][1:])
        b = int(t[-1][1:])
        spare = [] if ring == 'none' else [([1, 1], [1])]
        if t[1] == 'P1':           # r - K - A - B: K at one remove nests B (three removes); A at two removes
            return spare + [F(0, [end(b)]), G(a)]
        return spare + [F(0, [G(a)]), F(0, [end(b)])]   # r - K1 - K2 - A - B: K1 nests A, K2 nests B
    if cid == 'B-chain3-bare':
        return [F(0, [RENEW]), F(0)]
    if cid == 'B-chain3-s111':     # K1 s 1, K2 s 1, K3 listed 1 (floor + 1 = 2)
        return [F(1, [end(1)]), G(1)]   # K2 has demand 1 (r through K1)
    return None


def score(p, c):
    """holds: annihilated from t0 <= 12 with at least three rounds tested past the order; unsettled: no failure after round 12 + order
    but fewer than three such rounds; fails otherwise."""
    d = len(p) - 1
    bad = [t for t in range(d, len(c)) if sum(p[k] * c[t - d + k] for k in range(d + 1)) != 0]
    t0 = (max(bad) - d + 1) if bad else 0
    tested = len(c) - (t0 + d)
    if t0 <= 12 and tested >= 3:
        return 'holds', t0, tested
    if t0 <= 12:
        return 'unsettled', t0, tested
    return 'fails', t0, tested


def main():
    recs = {}
    for d in sys.argv[3:] + [sys.argv[1]]:
        for cid, rec in load_results(d).items():
            if rec.get('status') == 'ok' or cid not in recs:
                recs[cid] = rec
    out = {}
    for cid, pay in job.cases():
        if predicted(cid) is None:
            continue
        rec = recs.get(cid)
        if rec is None or rec.get('status') != 'ok':
            out[cid] = {'status': None if rec is None else rec.get('status')}
            continue
        c = rec['result']['counts']
        row = {'rounds': len(c) - 1}
        for law in (1, 2):
            p = job.annihilator(5, predicted(cid, law))
            v, t0, tested = score(p, c)
            row[f'law{law}'] = {'verdict': v, 'from': t0, 'tested': tested, 'degree': len(p) - 1, 'rate': R.dominant_root(p)}
        out[cid] = row
    tally = {law: {} for law in ('law1', 'law2')}
    for v in out.values():
        for law in tally:
            if law in v:
                tally[law][v[law]['verdict']] = tally[law].get(v[law]['verdict'], 0) + 1
    Path(sys.argv[2]).write_text(json.dumps({'tally': tally, 'cases': out}, indent=1))
    print(json.dumps(tally))
    for k, v in out.items():
        if v.get('law2', {}).get('verdict') != 'holds':
            print(k, v)


if __name__ == '__main__':
    main()
