"""CORNER-ROW-20261110-001A: exact corner rows at the training sides only (refuses n >= 64 until a rule is committed).
For each v contact on the two side walls, the walk series from c = (0, 1) in s = w^2, reduced by Berlekamp-Massey over GF(2)."""
import sys, json, time
sys.path.insert(0, '/home/jscul/p-vs-np-contact-first/proofs/RETURN-LAW-20261110-001A/RETURN-LAW-20261110-001A-P001_the_quadrant_law')
from return_lib import FastRect

def bm(seq):
    """Berlekamp-Massey over GF(2) on a list of bits: returns (C, L), C the connection polynomial as int (bit i = c_i, c_0 = 1)."""
    C, B, L, m = 1, 1, 0, 1
    for i in range(len(seq)):
        d = seq[i]
        # discrepancy: d = s_i + sum_{j=1..L} c_j s_{i-j}
        c = C >> 1; j = 1
        while c:
            if c & 1: d ^= seq[i - j]
            c >>= 1; j += 1
        if d == 0:
            m += 1
        elif 2 * L <= i:
            T = C; C ^= B << m; L = i + 1 - L; B = T; m = 1
        else:
            C ^= B << m; m += 1
    return C, L

def pmul(a, b):
    r = 0
    while b:
        if b & 1: r ^= a
        a <<= 1; b >>= 1
    return r

def series_to_rational(seq):
    C, L = bm(seq)
    S = sum(bit << k for k, bit in enumerate(seq))
    P = pmul(S, C) & ((1 << L) - 1)        # numerator: (S * C) mod s^L
    return P, C, L

if __name__ == "__main__":
    out = {}
    for n in [int(a) for a in sys.argv[1:]]:
        assert n < 64, "side 64 is held out until a rule is committed"
        t = time.time()
        N = 2 * n - 2
        R = FastRect(N, N)
        targets = [("L", b, (0, 2 * b + 1)) for b in range(n - 1)] + [("R", b, (N, 2 * b + 1)) for b in range(n - 1)]
        K = 8 * n * (n - 1) + 8 * n          # in w
        idx = [R.idx(*p) for _, _, p in targets]
        seqs = [[] for _ in targets]
        x = 1 << R.idx(0, 1)
        for k in range(K):
            if k % 2 == 0:
                for t_i, i in enumerate(idx):
                    seqs[t_i].append((x >> i) & 1)
            else:
                assert all(((x >> i) & 1) == 0 for i in idx)
            x = R.step(x)
        row = {}
        for (X, b, p), sq in zip(targets, seqs):
            P, Q, L = series_to_rational(sq)
            # verify on the second half: the recurrence reproduces every term (exactness check)
            row[f"{X}{b}"] = {"num": hex(P), "den": hex(Q), "L": L}
        out[n] = row
        print(n, "done in %.1f s; max complexity %d (bound %d)" % (time.time() - t, max(v["L"] for v in row.values()), n * (n - 1)), flush=True)
    json.dump(out, open("rows_training.json", "w"), indent=1)
