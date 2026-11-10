"""REACH-HALVES-20261110-001, stress test of ticket A's computed laws one size past the sides they were found at (4 to 32).

    python3 -B stress_test.py        writes stress_test.json and stress_test_log.txt beside this file

At every power of two n = 4 to 128, along the corner (0, 1)'s orbit over one period P of that orbit (checked: e A^P = e):
  S1 the corner return law: A^k[(0,1),(0,1)] = 1 exactly when 4 | k and k/4 + 1 is a power of two modulo 2n - 1
     (the series 1/(1 + L(w^4)), L(z) = z + z^2 + ... + z^n);
  S2 the contacts the corner never reads are exactly (X + 1, X), X = n + 2, n + 6, ..., 2n - 6 (none at n = 4);
  S3 the far corner: A^k[(0,1), (N, N - 1)] = A^(k - 4n + 2)[(0,1),(0,1)] for every k (the series w^(4n - 2)/(1 + L(w^4))).
At 8, 16 and 32 also S4: in the quadrant and in both half-strips the corner does read d* = (n + 3, n + 2) (a finite certificate);
and S5: below w^1200 the corner's return series in the quadrant is the Catalan series C(w^4) mod 2 (returns at 4(2^i - 1)) and in
both half-strips it equals the quadrant's (the regions are cut at 700, out of reach below 1200 steps).
Exact over GF(2); vectors are Python ints over the full grid [0, N]^2 (bit X(N + 1) + Y)."""
import json
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent


class Rect:
    def __init__(s, NX, NY):
        s.NX, s.NY = NX, NY
        W = s.W = NY + 1
        H = V = Y0 = YN = X0 = XN = 0
        for X in range(NX + 1):
            for Y in range(NY + 1):
                b = 1 << (X * W + Y)
                if (X + Y) % 2:
                    if X % 2:
                        H |= b
                    else:
                        V |= b
                if Y >= 1:
                    Y0 |= b
                if Y <= NY - 1:
                    YN |= b
                if X >= 1:
                    X0 |= b
                if X <= NX - 1:
                    XN |= b
        s.hm, s.hp = H & Y0 & X0, H & YN & XN       # h reads (X-1, Y-1) and (X+1, Y+1)
        s.vp, s.vm = V & XN & Y0, V & X0 & YN       # v reads (X+1, Y-1) and (X-1, Y+1)

    def idx(s, X, Y):
        return X * s.W + Y

    def step(s, x):
        W = s.W
        return ((x & s.hm) >> (W + 1)) ^ ((x & s.hp) << (W + 1)) ^ ((x & s.vp) << (W - 1)) ^ ((x & s.vm) >> (W - 1))


def powers_of_two_mod(n):
    q, out, p = 2 * n - 1, set(), 1
    for _ in range(64):
        out.add(p % q)
        p = (2 * p) % q
    return out


def side(n, E):
    N = 2 * n - 2
    B = Rect(N, N)
    e = 1 << B.idx(0, 1)
    P = E * (2 * n - 1)
    pw = powers_of_two_mod(n)
    i0, ifar = B.idx(0, 1), B.idx(N, N - 1)
    x, union, ret, far = e, 0, [], []
    for k in range(P):
        union |= x
        ret.append((x >> i0) & 1)
        far.append((x >> ifar) & 1)
        x = B.step(x)
    period_ok = x == e
    law = [1 if (k % 4 == 0 and (k // 4 + 1) % (2 * n - 1) in pw) else 0 for k in range(P)]
    s1 = ret == law
    contacts = [(X, Y) for X in range(N + 1) for Y in range(N + 1) if (X + Y) % 2]
    missed = sorted(c for c in contacts if not (union >> B.idx(*c)) & 1)
    want = sorted((X + 1, X) for X in range(n + 2, 2 * n - 5, 4))
    s3 = all(far[k] == ret[(k - 4 * n + 2) % P] for k in range(P))
    return {"P": P, "A^P fixes the corner orbit": period_ok, "S1 return law": s1,
            "S2 never read": missed == want, "never read": missed, "S3 far corner delayed by 4n - 2": s3}


def s4(n, K):
    N = 2 * n - 2
    big = K + 10
    d = (n + 3, n + 2)
    out = {}
    for name, NX, NY in [("quadrant", big, big), ("X bounded", N, big), ("Y bounded", big, N)]:
        R = Rect(NX, NY)
        x, first = 1 << R.idx(0, 1), None
        for k in range(K):
            if (x >> R.idx(*d)) & 1:
                first = k
                break
            x = R.step(x)
        out[name] = first
    return out


def s5(n, H=1200, big=700):
    N = 2 * n - 2
    want = [1 if (k % 4 == 0 and ((k // 4) + 1) & (k // 4) == 0) else 0 for k in range(H)]
    out = {}
    for name, NX, NY in [("quadrant", big, big), ("X bounded", N, big), ("Y bounded", big, N)]:
        R = Rect(NX, NY)
        i0 = R.idx(0, 1)
        x, seq = 1 << i0, []
        for k in range(H):
            seq.append((x >> i0) & 1)
            x = R.step(x)
        out[name] = seq == want
    return out


def main():
    t0 = time.time()
    log = open(HERE / "stress_test_log.txt", "w")
    E = {4: 4, 8: 8, 16: 16, 32: 16, 64: 32, 128: 32}
    res = {}
    for n in (4, 8, 16, 32, 64, 128):
        t1 = time.time()
        res[str(n)] = side(n, E[n])
        log.write("n %d %s (%.1f s)\n" % (n, json.dumps({k: v for k, v in res[str(n)].items() if k != "never read"}), time.time() - t1))
        log.flush()
    res["S4 (first time the corner reads d*)"] = {str(n): s4(n, 400) for n in (8, 16, 32)}
    res["S5 (return series below w^1200 is the Catalan series C(w^4))"] = {str(n): s5(n) for n in (8, 16, 32)}
    log.write("S5 %s\n" % json.dumps(res["S5 (return series below w^1200 is the Catalan series C(w^4))"]))
    log.write("S4 %s\n" % json.dumps(res["S4 (first time the corner reads d*)"]))
    ok = all(res[str(n)]["A^P fixes the corner orbit"] and res[str(n)]["S1 return law"] and res[str(n)]["S2 never read"]
             and res[str(n)]["S3 far corner delayed by 4n - 2"] for n in (4, 8, 16, 32, 64, 128))
    ok4 = all(v is not None for d in res["S4 (first time the corner reads d*)"].values() for v in d.values())
    ok5 = all(v for d in res["S5 (return series below w^1200 is the Catalan series C(w^4))"].values() for v in d.values())
    res["all pass"] = ok and ok4 and ok5
    res["seconds"] = round(time.time() - t0, 1)
    (HERE / "stress_test.json").write_text(json.dumps(res, indent=1) + "\n")
    log.write("all pass: %s, %.1f s\n" % (res["all pass"], res["seconds"]))
    log.close()


if __name__ == "__main__":
    main()
