"""RETURN-LAW-20261110-001, exploration (not a claim of the proofs): search for an algebraic relation over GF(2) for the boundary
series of the quadrant on the h contacts (the conveyor grid of REACH-HALVES-20261110-001A in the quadrant: E, N always, S if j >= 1,
W if i >= 1 and j >= 1, walks from (0, 0)): A(x) (endpoints on the bottom row) or B(y) (on the left column). The series are cut at s^T
and x^I; the unknowns are polynomials c_d(s, x) of degree <= ds in s and <= dx in x, d = 0..D, with sum_d c_d A^d = 0 on the safe
region. Usage: python3 -B guess_algebraic.py T I D ds dx A|B. Recorded runs (2026-11-10): (60, 20, 2, 6, 4) and (90, 24, 4, 8, 4)
for A and for B all gave kernel dimension 0: no relation in those degrees."""
import sys
T, I, D, ds, dx, which = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
# compute A or B mod 2: series as dict (k, i) -> bit
cur = {(0, 0)}
ser = set()
for k in range(T):
    for (i, j) in cur:
        if which == 'A' and j == 0 and i < I: ser.add((k, i))
        if which == 'B' and i == 0 and j < I: ser.add((k, j))
    nxt = {}
    for (i, j) in cur:
        mv = [(i+1, j), (i, j+1)]
        if j >= 1: mv.append((i, j-1))
        if i >= 1 and j >= 1: mv.append((i-1, j))
        for q in mv: nxt[q] = nxt.get(q, 0) ^ 1
    cur = {q for q, c in nxt.items() if c}
def mul(a, b):
    out = {}
    for (k1, i1) in a:
        for (k2, i2) in b:
            k, i = k1 + k2, i1 + i2
            if k < T and i < I: out[(k, i)] = out.get((k, i), 0) ^ 1
    return {p for p, c in out.items() if c}
powers = [{(0, 0)}, ser]
for d in range(2, D+1): powers.append(mul(powers[-1], ser))
# columns: (d, a, b) monomial s^a x^b * A^d ; rows: truncated coefficients (k, i) with k < T - ds, i < I - dx (safe region)
cols = [(d, a, b) for d in range(D+1) for a in range(ds+1) for b in range(dx+1)]
rows = [(k, i) for k in range(T - ds) for i in range(I - dx)]
ridx = {r: n for n, r in enumerate(rows)}
vecs = []
for (d, a, b) in cols:
    v = 0
    for (k, i) in powers[d]:
        kk, ii = k + a, i + b
        if (kk, ii) in ridx: v |= 1 << ridx[(kk, ii)]
    vecs.append(v)
# find kernel: gaussian elimination tracking combinations
basis = []  # (vec, combo)
kernel = []
for n, v in enumerate(vecs):
    combo = 1 << n
    for bv, bc in basis:
        if v ^ bv < v: v ^= bv; combo ^= bc
    if v == 0: kernel.append(combo)
    else:
        basis.append((v, combo)); basis.sort(key=lambda t: -t[0])
print("columns", len(cols), "rows", len(rows), "kernel dim", len(kernel))
for kc in kernel[:3]:
    terms = [cols[n] for n in range(len(cols)) if (kc >> n) & 1]
    print("relation:", " + ".join("s^%d x^%d A^%d" % (a, b, d) for d, a, b in terms))
