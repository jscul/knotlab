"""RETURN-LAW-20261110-001, stress test of the computed laws one size past the sides and horizons they were checked at.

    python3 -B stress_test.py        writes stress_test.json and stress_test_log.txt beside this file

S1  C1 exactly at n = 512: the box's corner series agrees with 1/(1 + L(w^4)) below 2n(n - 1) + 4n terms (both obey linear
    recurrences of orders <= 2n(n - 1) and 4n, so this is equality of the series);
S2  B1 at every even side 66 to 80 below w^3200, B2 (first difference at 4n) at every odd side 65 to 79;
S3  A1 below w^8000 (the quadrant's corner series is C(w^4));
S4  C3 at every side 65 to 128 (the box first differs from the quadrant at time 8n);
S5  the four-corner formula at 128 below w^2000;
S6  ticket C's Theorem 7 against the box walk at the sides 13 to 16 (to s^40).
Exact over GF(2), using the library of RETURN-LAW-20261110-001A."""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "proofs/RETURN-LAW-20261110-001A/RETURN-LAW-20261110-001A-P001_the_quadrant_law"))
from return_lib import FastRect as Rect, Ring, arch_two_sided, box_law_sequence, catalan2, corner_returns, spread  # noqa: E402

out, log = {}, []


def say(msg):
    log.append(msg)
    print(msg, flush=True)
    (HERE / "stress_test_log.txt").write_text("\n".join(log) + "\n")


t0 = time.time()
# S1
n = 512
K = 2 * n * (n - 1) + 4 * n
d = corner_returns(2 * n - 2, 2 * n - 2, K)
out["S1"] = {"n": n, "terms": K, "pass": d == box_law_sequence(n, K)}
say(f"S1 C1 exactly at 512 ({K} terms): {out['S1']['pass']}  [{time.time() - t0:.0f} s]")
# S2
H = 3200
q = spread(catalan2(H), 4, H)
s2 = {}
for n in range(65, 81):
    a = corner_returns(2 * n - 2, H // 2 + 4, H)
    if n % 2 == 0:
        s2[n] = a == q
    else:
        x = a ^ q
        s2[n] = ((x & -x).bit_length() - 1 if x else None) == 4 * n
out["S2"] = {"pass": all(s2.values()), "sides": s2}
say(f"S2 B1 at even sides 66..80 below w^3200, B2 at odd 65..79: {out['S2']['pass']}  [{time.time() - t0:.0f} s]")
# S3
H = 8000
d = corner_returns(H // 2 + 4, H // 2 + 4, H)
out["S3"] = {"pass": d == spread(catalan2(H), 4, H)}
say(f"S3 A1 below w^8000: {out['S3']['pass']}  [{time.time() - t0:.0f} s]")
# S4
s4 = {}
for n in range(65, 129):
    H = 8 * n + 8
    x = corner_returns(2 * n - 2, 2 * n - 2, H) ^ spread(catalan2(H), 4, H)
    s4[n] = ((x & -x).bit_length() - 1 if x else None) == 8 * n
out["S4"] = {"pass": all(s4.values())}
say(f"S4 C3 at 65..128: {out['S4']['pass']}  [{time.time() - t0:.0f} s]")
# S5
n, m, K = 128, 7, 2000
N = 2 * n - 2
B = Rect(N, N)
cs = [(0, 1)]
for _ in range(3):
    X, Y = cs[-1]
    cs.append((Y, N - X))
got = [B.series((0, 1), c, K) for c in cs]
Cm = sum(1 << (4 * (2 ** j - 1)) for j in range(m + 1))
pred, k = [0, 0, 0, 0], 0
while k * (2 * n - 1) < K:
    pred[k % 4] ^= (Cm << (k * (2 * n - 1))) & ((1 << K) - 1)
    k += 1
pred[3] ^= 1 << (2 * n - 3)
out["S5"] = {"pass": got == pred}
say(f"S5 four-corner formula at 128 below w^2000: {out['S5']['pass']}  [{time.time() - t0:.0f} s]")
# S6
T = 40
R = Ring(T)
s6 = {}
for n in range(13, 17):
    E, _ = arch_two_sided(R, n)
    dd = corner_returns(2 * n - 2, 2 * n - 2, 2 * T)
    s6[n] = E[0][0] == sum(((dd >> (2 * k)) & 1) << k for k in range(T))
out["S6"] = {"pass": all(s6.values()), "sides": s6}
say(f"S6 Theorem 7 at 13..16 to s^40: {out['S6']['pass']}  [{time.time() - t0:.0f} s]")
out["all_pass"] = all(v["pass"] for k, v in out.items() if k.startswith("S"))
out["seconds"] = round(time.time() - t0)
(HERE / "stress_test.json").write_text(json.dumps(out, indent=2, default=str) + "\n")
say(f"ALL PASS: {out['all_pass']}  [{out['seconds']} s]")
