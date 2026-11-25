"""Unit tests of the readings (KD 3) and the gate (KD 4) on sequences written by hand.
usage: python -B test_readings.py   (prints one line per test; writes nothing unless --out PATH)"""
import json
import sys
from math import comb

import readings as RD

RES = {}


def check(name, cond, detail=None):
    RES[name] = {'ok': bool(cond), 'detail': detail}
    print('%-72s %s' % (name, 'ok' if cond else 'FAIL'), '' if cond else detail)


def main():
    # a square: 2r^2 + 2r + 1 on 0..20
    sq = [2 * r * r + 2 * r + 1 for r in range(21)]
    v = RD.read(sq)
    check('square: POWER(2) on [0, 20]', v['verdict'] == 'POWER' and v['j'] == 2 and v['segment'] == [0, 20]
          and v['poly'] == '[1, 2, 2]', v)
    # a cubic: C(r + 3, 3) on 0..64 (control 4)
    cu = [comb(r + 3, 3) for r in range(65)]
    v = RD.read(cu)
    check('cubic: POWER(3) on [0, 64]', v['verdict'] == 'POWER' and v['j'] == 3 and v['segment'] == [0, 64], v)
    # a cubic with only 10 values is not POWER(3) (needs j + 8 = 11); it is not LINREC(<=3) either
    v = RD.read(cu[:10])
    check('cubic, 10 values: not POWER', v['verdict'] != 'POWER', v)
    # linear with a quadratic start (the bare ring from a made knot, n = 15): 2r^2+2r+1 to 14, then 15(2r+1)
    n = 15
    br = [2 * r * r + 2 * r + 1 if r <= n - 1 else n * (2 * r + 1) for r in range(40)]
    v = RD.read(br)
    check('ring count: POWER(1) final, POWER(2) earlier', v['verdict'] == 'POWER' and v['j'] == 1
          and v['segment'] == [15, 39] and v['earlier'] and v['earlier'][0]['j'] == 2
          and v['earlier'][0]['segment'] == [0, 14], v)
    # n = 9: the quadratic part has 9 values, fewer than j + 8 = 10, so no earlier POWER(2) is listed
    n = 9
    br = [2 * r * r + 2 * r + 1 if r <= n - 1 else n * (2 * r + 1) for r in range(40)]
    v = RD.read(br)
    check('ring count n = 9: no earlier POWER(2) (9 values)', v['verdict'] == 'POWER' and v['j'] == 1
          and v['segment'] == [9, 39] and not any(e.get('j') == 2 for e in v['earlier']), v)
    check('ring count: step n-1 to n is 3n - 1', br[n] - br[n - 1] == 3 * n - 1, (br[n - 1], br[n]))
    # a two-phase sequence: r even -> r^2, r odd -> 3r^2 (each phase of degree 2), 0..40
    tp = [r * r if r % 2 == 0 else 3 * r * r for r in range(41)]
    v = RD.read(tp)
    check('two-phase: POWER(2) 2-phase on [0, 40]', v['verdict'] == 'POWER' and v['m'] == 2 and v['j'] == 2
          and v['segment'] == [0, 40], v)
    # three-phase linear: F(3i + q) = (q + 1) i + q
    th = [((r % 3) + 1) * (r // 3) + (r % 3) for r in range(60)]
    v = RD.read(th)
    check('three-phase: POWER(1) 3-phase', v['verdict'] == 'POWER' and v['m'] == 3 and v['j'] == 1, v)
    # a recurrence: Fibonacci-like F(r) = F(r-1) + F(r-2), 1, 2, 3, 5, ... (LINREC(2), root golden ratio)
    fib = [1, 2]
    while len(fib) < 20:
        fib.append(fib[-1] + fib[-2])
    v = RD.read(fib)
    check('recurrence: LINREC(2) root 1.618', v['verdict'] == 'LINREC' and v['k'] == 2
          and abs(v['root'] - 1.6180339887) < 1e-9 and v['verified'] == 16, v)
    # LINREC(1) on 3 * 2^r with 2 fitted and 10 verified (control 2's S)
    geo = [3 * 2 ** (r - 1) for r in range(1, 13)]
    v = RD.read(geo, r0=1, kind='S')
    check('geometric S: LINREC(1) root 2, 2 fitted 10 verified', v['verdict'] == 'LINREC' and v['k'] == 1
          and v['root'] == 2.0 and v['fitted'] == 2 and v['verified'] == 10 and v['segment'] == [1, 12], v)
    # H = 3*2^r - 2 reads LINREC(2) (roots 2 and 1)
    h = [3 * 2 ** r - 2 for r in range(13)]
    v = RD.read(h)
    check('branching H: LINREC(2) root 2', v['verdict'] == 'LINREC' and v['k'] == 2 and abs(v['root'] - 2) < 1e-9, v)
    # a sequence too short for a recurrence's 8 verified terms: undecided
    v = RD.read([1, 4, 2, 8, 5, 7, 1, 3])
    check('short irregular: UNDECIDED', v['verdict'] == 'UNDECIDED', v)
    # a slowly rising, irregular count: increments rise by less than 1.25 a step, not a power, not a recurrence
    import random
    rng = random.Random(7)
    s = [10]
    for _ in range(40):
        s.append(s[-1] + rng.randint(1, 3))
    F = [0]
    for x in s:
        F.append(F[-1] + x)
    v = RD.read(F, with_bound=False)
    check('irregular rising increments: UNDECIDED rising (no BOUND)', v['verdict'] == 'UNDECIDED' and v.get('rising'),
          v)
    # the same with BOUND: 10r + r^2 has C/c near 2.8 for j = 2 on [4, 41]: no BOUND, UNDECIDED rising
    v = RD.read(F)
    check('10r + r^2-like: no BOUND(2), UNDECIDED rising', v['verdict'] == 'UNDECIDED', v)
    # r^2 plus noise below r: BOUND(2) on [4, 60]
    q = [r * r + rng.randint(0, r) for r in range(61)]
    v = RD.read(q)
    check('r^2 + noise: BOUND(2) on [4, 60]', v['verdict'] == 'BOUND' and v['j'] == 2 and v['segment'] == [4, 60], v)
    # BOUND: r^2 * (1 + 0.5*sin) style integers: floor(r^2 * (3 + (-1)^r) / 2): ratio 2 exactly
    b2 = [r * r * (2 if r % 2 == 0 else 1) for r in range(100)]
    v = RD.bound(b2, 0)
    check('BOUND(2) with C/c = 2 exactly', v is not None and v['j'] == 2 and v['segment'] == [4, 99]
          and v['C_over_c'] == 2.0, v)
    b3 = [r * r * (3 if r % 2 == 0 else 1) for r in range(100)]
    check('C/c = 3: no BOUND', RD.bound(b3, 0) is None, RD.bound(b3, 0))
    # RATIO: increments 1.3^r rounded up -> RATIO with x >= 1.25
    import math
    sr = [math.ceil(10 * 1.3 ** r) for r in range(20)]
    F = [0]
    for x in sr:
        F.append(F[-1] + x)
    v = RD.read(F)
    check('ratio 1.3: RATIO or LINREC', v['verdict'] in ('RATIO', 'LINREC'), v)
    vr = RD.ratio(*RD.increments(F, 0))
    check('ratio 1.3: RATIO(x) x >= 1.25', vr['verdict'] == 'RATIO' and vr['x'] >= 1.25, vr)
    # births b(t) under RATIO on b itself
    b = [math.ceil(5 * 1.4 ** t) for t in range(1, 16)]
    v = RD.read(b, r0=1, kind='b')
    check('births rising 1.4: RATIO on b', v['verdict'] in ('RATIO', 'LINREC'), v)
    # constant births: POWER(0)
    v = RD.read([7] * 30, r0=1, kind='b')
    check('constant births: POWER(0)', v['verdict'] == 'POWER' and v['j'] == 0, v)
    v = RD.read([0] * 30, r0=1, kind='b')
    check('zero births: not POWER', v['verdict'] != 'POWER', v)
    # ENDED first
    v = RD.read(sq, ended=True)
    check('ended: ENDED first', v['verdict'] == 'ENDED', v)
    # doubling reading on the ring count (n = 33): a run within 0.3 of 2 starting at 4
    n = 33
    br = [2 * r * r + 2 * r + 1 if r <= n - 1 else n * (2 * r + 1) for r in range(200)]
    runs = RD.doubling(br)
    check('doubling: [4, 38] at j = 2 on Ring(33,2) made knot', any(x['j'] == 2 and x['range'] == [4, 38]
                                                                     for x in runs), runs)
    cu = [comb(r + 3, 3) for r in range(200)]
    eps13 = math.log2(cu[26] / cu[13])
    eps12 = math.log2(cu[24] / cu[12])
    check('doubling: C(r+3,3) first within 0.3 of 3 at r = 13', abs(eps13 - 3) <= 0.3 < abs(eps12 - 3),
          (eps12, eps13))
    # the gate: R_400-like 2r+1 from 16 knots on [0, 64]: j = 1 on [4, 64], spread 1.12
    counts = {u: [2 * r + 1 for r in range(65)] for u in range(16)}
    g = RD.gate(counts)
    check('gate: 2r+1 gives j = 1 on [4, 64]', g['holds'] and g['j'] == 1 and g['range'] == [4, 64]
          and abs(g['spread']['all']['spread'] - 2.25 / 2.015625) < 1e-12, g)
    # the gate: a comb-like mix (quadratic and linear knots) -> no gate
    counts = {0: [comb(r + 2, 2) for r in range(64)], 1: [r + 1 for r in range(64)]}
    g = RD.gate(counts)
    check('gate: C(r+2,2) with r+1 gives no gate', not g['holds'], g)
    # the gate needs z >= 32
    counts = {0: [2 * r + 1 for r in range(31)]}
    g = RD.gate(counts)
    check('gate: least kept range below 32 -> no gate (range)', not g['holds'] and 'below' in g['reason'], g)
    # the gate on the bare ring: made and start knots of Ring(33,2) at 264 rounds: j = 1 on [16, 132]
    n = 33
    made = [2 * r * r + 2 * r + 1 if r <= n - 1 else n * (2 * r + 1) for r in range(133)]
    st = []
    for r in range(265):
        if r <= 16:
            st.append(2 * r * r + 2 * r + 1)
        elif r <= 32:
            st.append(545 + 34 * (r - 16))
        else:
            st.append(n * (r + 1))
    check('bare ring start count: (r+1)^2 at r = 32', st[32] == 33 * 33, st[32])
    counts = {0: st, 1: made}
    g = RD.gate(counts, labels={0: 'start', 1: 'made'})
    check('gate: Ring(33,2)-like counts give j = 1 on [16, 132]', g['holds'] and g['j'] == 1
          and g['range'] == [16, 132], g)
    ok = all(r['ok'] for r in RES.values())
    print('ALL PASSED' if ok else 'SOME FAILED', '%d tests' % len(RES))
    if '--out' in sys.argv:
        with open(sys.argv[sys.argv.index('--out') + 1], 'w') as f:
            json.dump(RES, f, indent=1, sort_keys=True, default=str)
    return ok


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
