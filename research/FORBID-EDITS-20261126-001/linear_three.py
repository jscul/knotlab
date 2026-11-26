# Abstract check, three readers: uniform worlds on W ∩ (S_x × T_y × U_z), all linear (homogeneous parity forbidding);
# full no-signalling: every one- and two-party record support independent of the other settings; readings: a
# nonzero linear functional of the record, relabelled freely. Best Mermin-game win (settings 000, 011, 101, 110;
# even parity at 000, odd elsewhere).
import itertools, sys
from fractions import Fraction
dims = tuple(int(c) for c in sys.argv[1])
N = sum(dims); off = [0, dims[0], dims[0] + dims[1]]
def span(gens):
    s = {0}
    for g in gens: s |= {v ^ g for v in s}
    return frozenset(s)
def subspaces(n):
    out = set()
    for k in range(n + 1):
        for g in itertools.combinations(range(1, 1 << n), k): out.add(span(g))
    return list(out)
part = lambda v, i: (v >> off[i]) & ((1 << dims[i]) - 1)
side = [subspaces(d) for d in dims]
dot = lambda f, u: bin(f & u).count('1') & 1
settings = list(itertools.product((0, 1), repeat=3))
scored = {(0, 0, 0): 0, (0, 1, 1): 1, (1, 0, 1): 1, (1, 1, 0): 1}
best = (Fraction(0), None); n_ns = 0
for W in subspaces(N):
    for choice in itertools.product(*[itertools.product(s, repeat=2) for s in side]):
        V = {st: [v for v in W if all(part(v, i) in choice[i][st[i]] for i in range(3))] for st in settings}
        ok = True
        for keep in ((0,), (1,), (2,), (0, 1), (0, 2), (1, 2)):
            seen = {}
            for st in settings:
                key = tuple(st[i] for i in keep)
                proj = frozenset(tuple(part(v, i) for i in keep) for v in V[st])
                if seen.setdefault(key, proj) != proj: ok = False; break
            if not ok: break
        if not ok: continue
        n_ns += 1
        for fa in itertools.product(*[itertools.product(range(1, 1 << dims[i]), repeat=2) for i in range(3)]):
            # per scored setting: is a+b+c constant (then the parity is 0, a homogeneous functional) or balanced?
            const = {}
            for st in scored:
                vals = {sum(dot(fa[i][st[i]], part(v, i)) for i in range(3)) & 1 for v in V[st]}
                const[st] = vals.pop() if len(vals) == 1 else None
            # best relabelling r_i(setting): win where const + relabel = target; balanced settings win 1/2
            for r in itertools.product((0, 1), repeat=6):
                w = Fraction(0)
                for st, t in scored.items():
                    if const[st] is None: w += Fraction(1, 2)
                    else: w += int((const[st] + r[st[0]] + r[2 + st[1]] + r[4 + st[2]]) % 2 == t)
                if w / 4 > best[0]: best = (w / 4, (sorted(W), choice, fa, r, const))
print(dims, 'no-signalling choices', n_ns, 'best Mermin win', best[0]); print(best[1])
