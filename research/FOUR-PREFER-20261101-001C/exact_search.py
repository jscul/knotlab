"""Exact search for a failing signing on a fixed 4-regular system (exists a choice of one class member per line such that no colouring
satisfies every line), by counterexample-guided refinement with two SAT solvers."""
import json, random, sys, time
from pysat.solvers import Minisat22
from pysat.card import CardEnc
sys.path.insert(0, "/home/jscul/p-vs-np-contact-first/proofs/FOUR-PLACE-20261031-001A/FOUR-PLACE-20261031-001A-P001_the_value_free_four_place_knots")
import four_lib as F
H4 = F.H4
knots = []
for m in range(1, 1 << 16):
    R = frozenset(s for i, s in enumerate(H4) if m >> i & 1)
    if F.is_knot(R): knots.append(R)
cls = {}
for R in knots: cls.setdefault(F.canonical(R), []).append(R)
CL = sorted(cls.items(), key=lambda kv: (len(kv[0]), sorted(kv[0])))

def failing_signing(lines, mem, limit=4000):
    n = 1 + max(max(L) for L in lines)
    m, K = len(lines), len(mem)
    var = lambda l, r: l * K + r + 1
    top = m * K
    S = Minisat22()
    for l in range(m):                                         # exactly one relation per line
        enc = CardEnc.equals(lits=[var(l, r) for r in range(K)], bound=1, top_id=top)
        top = max(top, enc.nv)
        for cl in enc.clauses: S.add_clause(cl)
    excl = {pat: [r for r, R in enumerate(mem) if pat not in R] for pat in H4}
    cex = 0
    while cex < limit:
        if not S.solve():
            S.delete(); return None, cex                       # no failing signing exists on this system
        model = set(v for v in S.get_model() if v > 0)
        choice = [next(r for r in range(K) if var(l, r) in model) for l in range(m)]
        rels = [mem[r] for r in choice]
        with Minisat22(bootstrap_with=F.cnf(lines, rels, n)) as T:
            if not T.solve():
                S.delete(); return choice, cex                 # failing signing found
            col = [1 if v > 0 else 0 for v in T.get_model()[:n]]
        # this colouring must be excluded by some line's relation
        S.add_clause([var(l, r) for l, L in enumerate(lines) for r in excl[tuple(col[p] for p in L)]])
        cex += 1
    S.delete(); return "limit", cex

if __name__ == "__main__":
    census = json.load(open("/home/jscul/p-vs-np-contact-first/research/MUTUAL-SELECTION-20261031-001C/census.json"))
    rng = random.Random(5)
    def rand_simple(n):
        while True:
            stubs = [p for p in range(n) for _ in range(4)]
            rng.shuffle(stubs)
            lines = [tuple(stubs[4 * i:4 * i + 4]) for i in range(n)]
            if all(len(set(L)) == 4 for L in lines) and len({frozenset(L) for L in lines}) == n:
                return lines
    systems = [(f"n{n}#{i}", L) for n in (5, 6, 7) for i, L in enumerate(F.systems(n, census)) if len({frozenset(x) for x in L}) == len(L)]
    systems += [(f"rand{n}#{t}", rand_simple(n)) for n in (8, 10, 12) for t in range(3)]
    todo = [int(x) for x in sys.argv[1].split(",")]
    t0 = time.time()
    for ci in todo:
        c, mem = CL[ci]
        for name, L in systems:
            t1 = time.time()
            out, cex = failing_signing(L, mem, limit=1500)
            print(f"class {ci:2d} {name}: {'FAIL ' + str(out) if isinstance(out, list) else ('none' if out is None else 'limit')} ({cex} counterexamples, {round(time.time() - t1, 1)} s)", flush=True)
