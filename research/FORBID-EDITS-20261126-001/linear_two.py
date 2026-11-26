# Abstract check: uniform worlds on W ∩ (S_x × T_y), W a linear subspace of F2^(nA+nB), S_x, T_y linear subspaces of
# each side's space (homogeneous parity forbidding), outcomes nonzero linear functionals. Max CHSH under full-record
# no-signalling (each side's projected distribution independent of the far setting).
import itertools
from fractions import Fraction
nA = nB = 2
N = nA + nB
vecs = list(range(1 << N))
def span(gens):
    s = {0}
    for g in gens: s |= {v ^ g for v in s}
    return frozenset(s)
subs = set()
for k in range(0, N + 1):
    for gens in itertools.combinations(range(1, 1 << N), k): subs.add(span(gens))
subs = list(subs)
sideA = list({span(g) for k in range(0, nA + 1) for g in itertools.combinations(range(1, 1 << nA), k)})
A = lambda v: v & ((1 << nA) - 1); B = lambda v: v >> nA
funA = range(1, 1 << nA); funB = range(1, 1 << nB)
dot = lambda f, u: bin(f & u).count('1') & 1
best = (0, None)
for W in subs:
    for S0, S1, T0, T1 in itertools.product(sideA, repeat=4):
        V = {(x, y): [v for v in W if A(v) in (S0, S1)[x] and B(v) in (T0, T1)[y]] for x in (0, 1) for y in (0, 1)}
        ok = True
        for x in (0, 1):
            pa = [sorted({A(v) for v in V[(x, y)]}) for y in (0, 1)]
            if pa[0] != pa[1]: ok = False
        for y in (0, 1):
            pb = [sorted({B(v) for v in V[(x, y)]}) for x in (0, 1)]
            if pb[0] != pb[1]: ok = False
        if not ok: continue
        for a0, a1, b0, b1 in itertools.product(funA, funA, funB, funB):
            E = {}
            for (x, y), vs in V.items():
                f, g = (a0, a1)[x], (b0, b1)[y]
                E[(x, y)] = Fraction(sum(1 - 2 * (dot(f, A(v)) ^ dot(g, B(v))) for v in vs), len(vs))
            for signs in itertools.product((1, -1), repeat=4):
                if signs.count(-1) % 2 == 1:
                    S = signs[0] * E[(0, 0)] + signs[1] * E[(0, 1)] + signs[2] * E[(1, 0)] + signs[3] * E[(1, 1)]
                    if S > best[0]: best = (S, (sorted(W), S0, S1, T0, T1, (a0, a1, b0, b1), dict(E)))
print('best CHSH with full-record no-signalling (linear forbidding, uniform worlds):', best[0]); print(best[1])
