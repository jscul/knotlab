"""CORNER-ROW-20261110-001A: the held-out side 64, computed after commit 128b2e30d recorded the training verdict and the predictions
P1 to P5. Exact rows by the frozen method (Berlekamp-Massey over GF(2), here with a bit-parallel discrepancy), then the tests."""
import json, random, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "proofs/RETURN-LAW-20261110-001A/RETURN-LAW-20261110-001A-P001_the_quadrant_law"))
from return_lib import FastRect  # noqa: E402

def bm_fast(bits):
    """Berlekamp-Massey over GF(2); bits is a list. Returns (C, L) with C the connection polynomial as an int."""
    C, B, L, m, R = 1, 1, 0, 1, 0
    for i, b in enumerate(bits):
        R = (R << 1) | b                    # bit j of R is s_(i - j)
        if bin(C & R).count("1") & 1:
            if 2 * L <= i:
                C, B, L, m = C ^ (B << m), C, i + 1 - L, 1
            else:
                C ^= B << m; m += 1
        else:
            m += 1
    return C, L

def pmul(a, b):
    r = 0
    while b:
        if b & 1: r ^= a
        a <<= 1; b >>= 1
    return r

def exact_row(n):
    N = 2 * n - 2
    R = FastRect(N, N)
    targets = [("L", b, (0, 2 * b + 1)) for b in range(n - 1)] + [("R", b, (N, 2 * b + 1)) for b in range(n - 1)]
    K = 8 * n * (n - 1) + 8 * n
    idx = [R.idx(*p) for _, _, p in targets]
    seqs = [[] for _ in targets]
    x = 1 << R.idx(0, 1)
    for k in range(K):
        if k % 2 == 0:
            for t, i in enumerate(idx):
                seqs[t].append((x >> i) & 1)
        x = R.step(x)
    row = {}
    for (X, b, _), sq in zip(targets, seqs):
        C, L = bm_fast(sq)
        S = sum(bit << k for k, bit in enumerate(sq))
        row[f"{X}{b}"] = {"num": hex(pmul(S, C) & ((1 << L) - 1)), "den": hex(C), "L": L}
    return row

if __name__ == "__main__":
    t = time.time()
    # the fast Berlekamp-Massey agrees with the frozen one on the training rows
    train = json.load(open(HERE / "rows_training.json"))
    for n in ("4", "8", "16", "32"):
        assert exact_row(int(n)) == train[n], n
    print("fast Berlekamp-Massey reproduces the training rows exactly", flush=True)
    row = exact_row(64)
    json.dump({"64": row}, open(HERE / "rows_heldout64.json", "w"), indent=1)
    print("side 64: largest complexity %d (bound %d), %.0f s" % (max(v["L"] for v in row.values()), 64 * 63, time.time() - t))
